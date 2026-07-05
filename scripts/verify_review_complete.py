#!/usr/bin/env python3
"""Phase 7 入口 gate：验证 §1.5 场景审阅链路已跑完。

由 hook verify-review-complete.sh 在 PreToolUse Bash matcher 拦截 assemble_story.py
调用时触发。

判据：
- pipeline/phase6_development.yaml 存在（前置 phase6 跑完才进 phase 7）
- pipeline/review/scene_{scene_id}.yaml 对每个场景都存在
- verdict ∈ {PASS, PATCH, ROLLBACK, REWRITE}
- ESCALATED / review_incomplete / orchestrator_input_gate → 未闭合，阻断
- PATCH verdict → patch_directive.applied.yaml 存在（reviser 已消费）且
  pipeline/review/scene_{scene_id}.post_revision.yaml verdict=PASS
- ROLLBACK / REWRITE verdict → pipeline/review/scene_{scene_id}.post_revision.yaml verdict=PASS

Escape hatch：
- pipeline/audit/skip_review.yaml 存在且含 {reason: "<具体>", risk_acknowledged: true}
- reason 不允许空洞值（skip / manual_choice / none 等）→ 视为无效

退出码：
- 0: §1.5 完整 OR escape hatch 生效 OR 前置 phase6 未跑完（不该 phase 7 该管）
- 2: §1.5 未跑完且无有效 escape hatch（阻断 Phase 7）

边界 case：
- 路径解析失败 / yaml 损坏 → exit 0 + stderr warn（不误伤）
- yaml 模块缺失 → exit 0 + stderr warn（运行环境不完整）
"""
from __future__ import annotations
import sys
from pathlib import Path

VALID_VERDICTS = {"PASS", "PATCH", "ROLLBACK", "REWRITE"}
EMPTY_REASONS = {"", "skip", "manual_choice", "none", "n/a", "todo", "tbd"}


def _warn(msg: str) -> None:
    print(f"[verify_review_complete WARN] {msg}", file=sys.stderr)


def _fail(msg: str, detail: list[str] | None = None) -> int:
    print(f"[verify_review_complete] ❌ {msg}", file=sys.stderr)
    if detail:
        for line in detail:
            print(f"  {line}", file=sys.stderr)
    print(
        "  ↳ 必须先 dispatch story-reviewer + scene-reviewer 走完 §1.5，或在",
        file=sys.stderr,
    )
    print(
        "    pipeline/audit/skip_review.yaml 声明 escape hatch "
        "（reason: \"<具体可审计>\" + risk_acknowledged: true）",
        file=sys.stderr,
    )
    print(
        "  ↳ 详见 phase7-integration/SKILL.md Step 0 / "
        "phase6-scene-development/references/execution-protocol.md §1.5",
        file=sys.stderr,
    )
    return 2


def _ai_pattern_gate_closed(post_revision: dict) -> tuple[bool, str | None]:
    gate = post_revision.get("ai_pattern_gate")
    if not isinstance(gate, dict):
        return True, None
    machine_gate = str(gate.get("machine_gate") or "").lower()
    if machine_gate != "fail":
        return True, None
    override = gate.get("override") or {}
    if not isinstance(override, dict):
        return False, "machine_fail_no_override"
    if bool(override.get("applied")) and (override.get("override_reason") or "").strip():
        return True, None
    return False, "machine_fail_no_override"


def _scene_has_clusters_or_high_hits(review_dir: Path, scene_id: str, yaml_module) -> bool:
    """扫 ai_filler.v2.yaml（fallback 到 .yaml），看是否有 cluster_alerts 非空或 high hit。"""
    lint_dir = review_dir / "lint"
    for fname in (f"{scene_id}.ai_filler.v2.yaml", f"{scene_id}.ai_filler.yaml"):
        lint_path = lint_dir / fname
        if not lint_path.exists():
            continue
        try:
            data = yaml_module.safe_load(lint_path.read_text(encoding="utf-8")) or {}
        except yaml_module.YAMLError:
            continue
        if data.get("cluster_alerts"):
            return True
        hits = data.get("lint_hits") or data.get("hits") or []
        if any(h.get("severity") == "high" for h in hits):
            return True
        return False
    return False


def _check_lint_ledger(review_dir: Path, scene_id: str, verdict: str, yaml_module) -> tuple[bool, str]:
    """Rn+2 O3: ledger hard gate + malformed YAML 处理。
    Returns: (is_hard_fail, reason)。is_hard_fail=False 且 reason 非空 -> WARN advisory。
    """
    machine_ledger_path = review_dir / f"{scene_id}.machine_ledger.yaml"
    if machine_ledger_path.exists():
        try:
            machine_ledger = yaml_module.safe_load(
                machine_ledger_path.read_text(encoding="utf-8")
            ) or {}
        except yaml_module.YAMLError as exc:
            return True, f"{scene_id}: machine_ledger malformed YAML — hard fail: {exc}"
        if isinstance(machine_ledger.get("entries"), list):
            return False, ""

    ledger_path = review_dir / f"scene_{scene_id}.lint_resolution_ledger.yaml"
    requires_hard = (
        verdict in {"PATCH", "ROLLBACK", "REWRITE"}
        or _scene_has_clusters_or_high_hits(review_dir, scene_id, yaml_module)
    )

    if not ledger_path.exists():
        msg = f"scene_{scene_id}: lint_resolution_ledger.yaml 缺失"
        if requires_hard:
            return True, f"{msg}（verdict={verdict} 或含 cluster/high hit）— hard fail"
        _warn(f"{msg}（advisory only）")
        return False, ""

    try:
        ledger = yaml_module.safe_load(ledger_path.read_text(encoding="utf-8")) or {}
    except yaml_module.YAMLError as exc:
        return True, f"scene_{scene_id}: ledger malformed YAML — hard fail: {exc}"

    if not isinstance(ledger.get("v1_triage"), (dict, list)):
        msg = f"scene_{scene_id}: ledger 缺 v1_triage"
        if requires_hard:
            return True, f"{msg} — hard fail"
        _warn(f"{msg}（advisory only）")
        return False, ""

    updates = ledger.get("post_revision_updates")
    if updates is not None and not isinstance(updates, (dict, list)):
        return True, f"scene_{scene_id}: post_revision_updates 格式异常 — hard fail"

    return False, ""


def _check_machine_channel(review_dir: Path, scene_id: str, yaml_module) -> tuple[bool, str]:
    directive_path = review_dir / f"{scene_id}.machine_directive.yaml"
    if not directive_path.exists():
        return False, ""

    try:
        directive = yaml_module.safe_load(directive_path.read_text(encoding="utf-8")) or {}
    except yaml_module.YAMLError as exc:
        return True, f"{scene_id}: machine_directive malformed YAML — hard fail: {exc}"

    pending_ids = [
        entry.get("id")
        for entry in directive.get("entries", []) or []
        if isinstance(entry, dict) and entry.get("status") == "pending" and entry.get("id")
    ]
    if not pending_ids:
        return False, ""

    gate_path = review_dir / f"{scene_id}.distribution_gate.yaml"
    if gate_path.exists():
        try:
            gate = yaml_module.safe_load(gate_path.read_text(encoding="utf-8")) or {}
        except yaml_module.YAMLError as exc:
            return True, f"{scene_id}: distribution_gate malformed YAML — hard fail: {exc}"
        if gate.get("verdict") == "PASS":
            return False, ""

    ledger_path = review_dir / f"{scene_id}.machine_ledger.yaml"
    ledger_status_by_id = {}
    if ledger_path.exists():
        try:
            ledger = yaml_module.safe_load(ledger_path.read_text(encoding="utf-8")) or {}
        except yaml_module.YAMLError as exc:
            return True, f"{scene_id}: machine_ledger malformed YAML — hard fail: {exc}"
        ledger_status_by_id = {
            entry.get("id"): entry.get("status")
            for entry in ledger.get("entries", []) or []
            if isinstance(entry, dict) and entry.get("id")
        }

    blocking = [entry_id for entry_id in pending_ids if ledger_status_by_id.get(entry_id) != "escalated"]
    if blocking:
        return True, f"{scene_id}: machine directive pending 未消费: {blocking}"
    return False, ""


def check(work_dir: Path) -> int:
    try:
        import yaml
    except ImportError:
        _warn("PyYAML 缺失，跳过 §1.5 完整性检查（不阻断）")
        return 0

    if not work_dir.is_dir():
        _warn(f"work_dir 不存在或不是目录: {work_dir}（不阻断）")
        return 0

    dev_yaml = work_dir / "pipeline" / "phase6_development.yaml"
    if not dev_yaml.exists():
        # phase6 都没产物 → 不该 phase 7 该管
        return 0

    try:
        dev_data = yaml.safe_load(dev_yaml.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError) as e:
        _warn(f"phase6_development.yaml 读取失败: {e}（不阻断）")
        return 0

    scenes = (dev_data or {}).get("scenes", [])
    if not scenes:
        _warn("phase6_development.yaml 无 scenes 字段（不阻断）")
        return 0

    scene_ids = [s.get("id") or s.get("scene_id") for s in scenes if s.get("id") or s.get("scene_id")]
    if not scene_ids:
        _warn("scenes 列表中未提取出 scene id（不阻断）")
        return 0

    # 1. 收集缺失 / verdict 异常的场景
    review_dir = work_dir / "pipeline" / "review"
    missing: list[str] = []
    invalid_verdict: list[tuple[str, str]] = []
    escalated_unclosed: list[tuple[str, str]] = []
    patch_not_applied: list[str] = []
    patch_no_post_revision: list[str] = []
    rollback_no_post_revision: list[tuple[str, str]] = []
    ai_gate_unclosed: list[tuple[str, str]] = []
    ledger_hard_fail: list[tuple[str, str]] = []
    machine_channel_unclosed: list[tuple[str, str]] = []
    post_revision_pass_unclosed: list[tuple[str, str]] = []

    for sid in scene_ids:
        review_yaml = review_dir / f"scene_{sid}.yaml"
        if not review_yaml.exists():
            missing.append(sid)
            continue
        try:
            r = yaml.safe_load(review_yaml.read_text(encoding="utf-8")) or {}
        except (yaml.YAMLError, OSError) as e:
            _warn(f"scene_{sid}.yaml 读取失败: {e}（视为缺失）")
            missing.append(sid)
            continue

        verdict = (r.get("verdict") or "").upper()
        written_by = r.get("written_by", "")
        review_incomplete = bool(r.get("review_incomplete"))

        if verdict == "ESCALATED":
            if written_by == "orchestrator_input_gate" or review_incomplete:
                escalated_unclosed.append((sid, written_by or "review_incomplete"))
                continue
            escalated_unclosed.append((sid, "escalated_misuse"))
            continue

        if verdict not in VALID_VERDICTS:
            invalid_verdict.append((sid, verdict or "<空>"))
            continue

        # Rn+2 O3 + R1 F2: ledger hard gate（所有 valid verdict 通用）
        hard_fail, reason = _check_lint_ledger(review_dir, sid, verdict, yaml)
        if hard_fail:
            ledger_hard_fail.append((sid, reason))
            continue

        hard_fail, reason = _check_machine_channel(review_dir, sid, yaml)
        if hard_fail:
            machine_channel_unclosed.append((sid, reason))
            continue

        if verdict == "PATCH":
            applied = work_dir / "pipeline" / f"scene_{sid}" / "patch_directive.applied.yaml"
            if not applied.exists():
                patch_not_applied.append(sid)
                continue
            post_rev = review_dir / f"scene_{sid}.post_revision.yaml"
            if not post_rev.exists():
                patch_no_post_revision.append(sid)
                continue
            try:
                pr = yaml.safe_load(post_rev.read_text(encoding="utf-8")) or {}
            except (yaml.YAMLError, OSError):
                patch_no_post_revision.append(sid)
                continue
            if (pr.get("verdict") or "").upper() != "PASS":
                patch_no_post_revision.append(sid)
                continue
            gate_closed, gate_reason = _ai_pattern_gate_closed(pr)
            if not gate_closed:
                ai_gate_unclosed.append((sid, gate_reason or "ai_pattern_gate"))
                continue
            from scene_review_schema_validator import validate_post_revision_pass
            ledger_path = review_dir / f"scene_{sid}.lint_resolution_ledger.yaml"
            lint_v2_path = review_dir / "lint" / f"{sid}.ai_filler.v2.yaml"
            phase5_path = work_dir / "pipeline" / "phase5_scenes.yaml"
            try:
                ledger_data = yaml.safe_load(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else {}
                lint_v2_data = yaml.safe_load(lint_v2_path.read_text(encoding="utf-8")) if lint_v2_path.exists() else {}
                phase5_data = yaml.safe_load(phase5_path.read_text(encoding="utf-8")) if phase5_path.exists() else {}
            except yaml.YAMLError:
                # ledger malformed 已被 _check_lint_ledger 拦截；此处忽略
                pass
            else:
                scene_card_equiv = next(
                    (s for s in (phase5_data.get("scenes") or [])
                     if (s.get("id") or s.get("scene_id")) == sid),
                    {},
                )
                pr_check = validate_post_revision_pass(pr, ledger_data, lint_v2_data, scene_card=scene_card_equiv)
                if not pr_check.valid:
                    post_revision_pass_unclosed.append((sid, pr_check.reason))
                    continue

        if verdict in ("ROLLBACK", "REWRITE"):
            post_rev = review_dir / f"scene_{sid}.post_revision.yaml"
            if not post_rev.exists():
                rollback_no_post_revision.append((sid, verdict))
                continue
            try:
                pr = yaml.safe_load(post_rev.read_text(encoding="utf-8")) or {}
            except (yaml.YAMLError, OSError):
                rollback_no_post_revision.append((sid, verdict))
                continue
            if (pr.get("verdict") or "").upper() != "PASS":
                rollback_no_post_revision.append((sid, verdict))
                continue
            gate_closed, gate_reason = _ai_pattern_gate_closed(pr)
            if not gate_closed:
                ai_gate_unclosed.append((sid, gate_reason or "ai_pattern_gate"))
                continue
            from scene_review_schema_validator import validate_post_revision_pass
            ledger_path = review_dir / f"scene_{sid}.lint_resolution_ledger.yaml"
            lint_v2_path = review_dir / "lint" / f"{sid}.ai_filler.v2.yaml"
            phase5_path = work_dir / "pipeline" / "phase5_scenes.yaml"
            try:
                ledger_data = yaml.safe_load(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else {}
                lint_v2_data = yaml.safe_load(lint_v2_path.read_text(encoding="utf-8")) if lint_v2_path.exists() else {}
                phase5_data = yaml.safe_load(phase5_path.read_text(encoding="utf-8")) if phase5_path.exists() else {}
            except yaml.YAMLError:
                # ledger malformed 已被 _check_lint_ledger 拦截；此处忽略
                pass
            else:
                scene_card_equiv = next(
                    (s for s in (phase5_data.get("scenes") or [])
                     if (s.get("id") or s.get("scene_id")) == sid),
                    {},
                )
                pr_check = validate_post_revision_pass(pr, ledger_data, lint_v2_data, scene_card=scene_card_equiv)
                if not pr_check.valid:
                    post_revision_pass_unclosed.append((sid, pr_check.reason))
                    continue

    if (
        not missing
        and not invalid_verdict
        and not escalated_unclosed
        and not patch_not_applied
        and not patch_no_post_revision
        and not rollback_no_post_revision
        and not ai_gate_unclosed
        and not ledger_hard_fail
        and not machine_channel_unclosed
        and not post_revision_pass_unclosed
    ):
        return 0  # §1.5 完整，放行

    # 2. 检查 escape hatch
    skip_yaml = work_dir / "pipeline" / "audit" / "skip_review.yaml"
    if skip_yaml.exists():
        try:
            skip_data = yaml.safe_load(skip_yaml.read_text(encoding="utf-8")) or {}
        except (yaml.YAMLError, OSError) as e:
            _warn(f"skip_review.yaml 读取失败: {e}（视为无效 escape hatch）")
            skip_data = {}

        reason = (skip_data.get("reason") or "").strip().lower()
        ack = bool(skip_data.get("risk_acknowledged"))

        if reason and reason not in EMPTY_REASONS and ack:
            print(
                f"[verify_review_complete] §1.5 escape hatch 生效 "
                f"(reason={skip_data['reason']!r})",
                file=sys.stderr,
            )
            return 0
        else:
            _warn(
                f"skip_review.yaml 存在但无效（reason={skip_data.get('reason')!r}, "
                f"risk_acknowledged={skip_data.get('risk_acknowledged')!r}）— 仍阻断"
            )

    # 3. 阻断 + 输出诊断
    detail = []
    if missing:
        detail.append(f"缺少 review/scene_*.yaml：{missing}")
    if invalid_verdict:
        detail.append(
            "verdict 不在 {PASS,PATCH,ROLLBACK,REWRITE}: "
            + ", ".join(f"scene_{s}={v}" for s, v in invalid_verdict)
        )
    if escalated_unclosed:
        detail.append(
            f"ESCALATED 未闭合（input_gate 失败 / review_incomplete）: "
            + ", ".join(f"scene_{s}({reason})" for s, reason in escalated_unclosed)
        )
    if patch_not_applied:
        detail.append(f"PATCH verdict 但 patch_directive.applied.yaml 缺失: {patch_not_applied}")
    if patch_no_post_revision:
        detail.append(f"PATCH 未闭合（缺 post_revision PASS）: {patch_no_post_revision}")
    if rollback_no_post_revision:
        detail.append(
            "ROLLBACK/REWRITE 未闭合（缺 post_revision PASS）: "
            + ", ".join(f"scene_{s}({v})" for s, v in rollback_no_post_revision)
        )
    if ai_gate_unclosed:
        detail.append(
            "ai_pattern_gate 未闭合（machine_gate=fail 且无有效 override.applied）: "
            + ", ".join(f"scene_{s}({reason})" for s, reason in ai_gate_unclosed)
        )
    if ledger_hard_fail:
        detail.append(f"ledger hard fail: {ledger_hard_fail}")
    if machine_channel_unclosed:
        detail.append(f"machine channel 未闭合: {machine_channel_unclosed}")
    if post_revision_pass_unclosed:
        detail.append(f"post-revision PASS 准入未闭合: {post_revision_pass_unclosed}")

    return _fail(
        "§1.5 场景审阅链路未跑完，Phase 7 拼接被阻断",
        detail,
    )


def main() -> int:
    if len(sys.argv) < 2:
        _warn("用法: verify_review_complete.py <work_dir>（不阻断）")
        return 0
    return check(Path(sys.argv[1]).resolve())


if __name__ == "__main__":
    sys.exit(main())
