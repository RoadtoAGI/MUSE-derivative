#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

import yaml

from ai_filler_lint import (
    DEVICE_BUDGET_CLASSES,
    FAMILY_REGISTRY,
    FAMILY_SOVEREIGNTY,
    RULE_TO_FAMILY,
    _devices_for_scene,
)


CLUSTER_MIGRATION_DENYLIST = {
    "micro_punchline_cadence": ["silence_pause_cliche", "rhythm_fragmentation"],
    "rhythm_fragmentation": ["micro_punchline_cadence"],
    "silence_pause_cliche": ["micro_punchline_cadence"],
    "lexical_cliche": ["abstract_phrase_debt"],
}

M_OBJECTION_CLUSTERS = {"explanatory_detour", "silence_pause_cliche", "action_log"}
OBSERVE_ONLY_FAMILIES = {"meta_language_leak"}
HIGH_SEVERITIES = {"high", "catastrophic", "major"}
GENERIC_FUNCTION_CLAIMS = (
    "节奏需要停顿",
    "强化氛围",
    "渲染气氛",
    "保留文学性",
    "这是 voice",
    "这是voice",
    "读者可能漏看",
    "美感",
    "留白",
    "顿挫",
)


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def _atomic_write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    os.replace(tmp_path, path)


def _entry_id(scene_id: str, family: str, idx: int, raw: dict) -> str:
    raw_id = raw.get("alert_id") or raw.get("lint_id")
    if isinstance(raw_id, str) and raw_id:
        return raw_id
    return f"{scene_id}-{family}-{idx}"


def _classify_level(family: str, severity: str, cluster: str) -> str:
    if severity in HIGH_SEVERITIES:
        return "S"
    if severity == "medium":
        if family in M_OBJECTION_CLUSTERS or cluster in M_OBJECTION_CLUSTERS:
            return "M"
        return FAMILY_SOVEREIGNTY.get(family, "S")
    return "L"


def _repair_hint(family: str) -> str:
    deny = CLUSTER_MIGRATION_DENYLIST.get(family, [])
    suffix = f"；禁止迁移到 {' / '.join(deny)}" if deny else ""
    return f"{family} 密度收敛到预算内{suffix}"


def _lint_path(work_dir: Path, scene_id: str, lint_suffix: str | None = None) -> Path:
    stem = f"{scene_id}.ai_filler"
    if lint_suffix:
        stem = f"{stem}.{lint_suffix}"
    return work_dir / "pipeline" / "review" / "lint" / f"{stem}.yaml"


def build_directive(
    work_dir: Path, scene_id: str, lint_suffix: str | None = None
) -> tuple[dict, dict]:
    lint_path = _lint_path(work_dir, scene_id, lint_suffix)
    lint = _load_yaml(lint_path)

    directive_entries = []
    ledger_entries = []
    seen_ids = set()
    idx = 1

    # en 检测处于观测模式：规则/基线成熟度不足（negation 类误报率高、金标样本少），
    # cluster alert 全部降为 L 级 observed，不产 directive entry、不触发 distribution lane。
    # zh 不受影响。恢复立案的前提：en 词表条目级误杀清洗 + 金标扩样重校准。
    observe_only = lint.get("language") == "en"

    for alert in lint.get("cluster_alerts", []) or []:
        if not isinstance(alert, dict):
            continue
        family = alert.get("family") or alert.get("cluster") or "unknown"
        cluster = alert.get("cluster") or FAMILY_REGISTRY.get(family, {}).get("cluster", "")
        severity = str(alert.get("severity") or "low")
        level = (
            "L"
            if observe_only or family in OBSERVE_ONLY_FAMILIES
            else _classify_level(family, severity, cluster)
        )
        entry_id = _entry_id(scene_id, family, idx, alert)
        seen_ids.add(entry_id)
        idx += 1
        ledger_entries.append({
            "id": entry_id,
            "family": family,
            "level": level,
            "status": "issued" if level in {"S", "M"} else "observed",
        })
        if level not in {"S", "M"}:
            continue
        directive_entries.append({
            "id": entry_id,
            "family": family,
            "level": level,
            "severity": severity,
            "hits": alert.get("hits", alert.get("total_count", 0)),
            "repair_hint": _repair_hint(family),
            "status": "pending",
        })

    for hit in lint.get("hits", []) or []:
        if not isinstance(hit, dict):
            continue
        family = hit.get("family") or RULE_TO_FAMILY.get(hit.get("rule"))
        if not family:
            continue
        entry_id = _entry_id(scene_id, family, idx, hit)
        if entry_id in seen_ids:
            continue
        seen_ids.add(entry_id)
        idx += 1
        ledger_entries.append({
            "id": entry_id,
            "family": family,
            "level": "L",
            "status": "observed",
        })

    directive = {
        "scene_id": scene_id,
        "stage": "post_lint",
        "dispatch_ready": False,
        "entries": directive_entries,
        "protected_regions": [],
    }
    ledger = {
        "scene_id": scene_id,
        "entries": ledger_entries,
    }
    return directive, ledger


def _merge_ledger_entries(existing: dict, generated: dict) -> dict:
    merged_entries = []
    seen = set()
    for entry in existing.get("entries", []) or []:
        if not isinstance(entry, dict):
            continue
        entry_id = entry.get("id")
        if entry_id:
            seen.add(entry_id)
        merged_entries.append(entry)

    for entry in generated.get("entries", []) or []:
        if not isinstance(entry, dict):
            continue
        entry_id = entry.get("id")
        if entry_id in seen:
            continue
        seen.add(entry_id)
        merged_entries.append(entry)

    merged = dict(existing)
    merged["scene_id"] = generated.get("scene_id", existing.get("scene_id"))
    merged["entries"] = merged_entries
    return merged


def generate_initial(work_dir: Path, scene_id: str, lint_suffix: str | None = None) -> int:
    directive_path = work_dir / "pipeline" / "review" / f"{scene_id}.machine_directive.yaml"
    ledger_path = work_dir / "pipeline" / "review" / f"{scene_id}.machine_ledger.yaml"
    if directive_path.exists() and lint_suffix is None:
        existing = _load_yaml(directive_path)
        if existing.get("stage") == "refreshed":
            print(
                f"[machine_directive] ERROR: refuse to overwrite refreshed directive: {directive_path}",
                file=sys.stderr,
            )
            return 2
    try:
        directive, ledger = build_directive(work_dir, scene_id, lint_suffix)
        if ledger_path.exists():
            ledger = _merge_ledger_entries(_load_yaml(ledger_path), ledger)
    except (FileNotFoundError, ValueError, yaml.YAMLError) as exc:
        print(f"[machine_directive] ERROR: {exc}", file=sys.stderr)
        return 2
    _atomic_write_yaml(directive_path, directive)
    _atomic_write_yaml(ledger_path, ledger)
    print(f"✅ {directive_path} · {len(directive['entries'])} entries")
    return 0


def _parse_protected_regions(summary_path: Path) -> list[dict]:
    if not summary_path.exists():
        return []
    regions = []
    current: dict | None = None
    patch_re = re.compile(
        r"\[(?P<patch_id>patch \d+)\s+·\s+issue_id\s+(?P<issue_id>[^ ]+)\s+·\s+applied\]\**\s*(?P<location>.*)"
    )
    for line in summary_path.read_text(encoding="utf-8").splitlines():
        match = patch_re.search(line)
        if match:
            current = {
                "patch_id": match.group("patch_id"),
                "issue_id": match.group("issue_id"),
                "location": match.group("location").strip(),
                "preserve": "",
            }
            regions.append(current)
            continue
        if current is None:
            continue
        preserve_match = re.search(r"preserve:\s*(?P<preserve>.+)$", line)
        if preserve_match:
            current["preserve"] = preserve_match.group("preserve").strip()
    return regions


def _budgeted_objections(objections: list[dict]) -> list[dict]:
    selected = []
    seen_families = set()
    for raw in objections[:2]:
        if not isinstance(raw, dict):
            continue
        family = raw.get("family")
        if family in seen_families:
            target = raw.get("target_entry_id", "<missing target_entry_id>")
            print(
                f"[machine_directive] WARN: ignored over-budget objection: {target}",
                file=sys.stderr,
            )
            continue
        seen_families.add(family)
        selected.append(raw)
    for raw in objections[2:]:
        if not isinstance(raw, dict):
            continue
        target = raw.get("target_entry_id", "<missing target_entry_id>")
        print(f"[machine_directive] WARN: ignored over-budget objection: {target}", file=sys.stderr)
    return selected


def _objection_denial_reason(
    objection: dict,
    entry_by_id: dict[str, dict],
    declared_devices: set[str],
    scene_text: str,
) -> str | None:
    target_id = objection.get("target_entry_id")
    entry = entry_by_id.get(target_id)
    if entry is None:
        return "target_entry_id_not_found"
    if entry.get("level") != "M":
        return "target_entry_not_m"

    family = objection.get("family")
    if family != entry.get("family"):
        return "family_mismatch"
    if family not in M_OBJECTION_CLUSTERS:
        return "family_not_objection_allowed"

    device = objection.get("device_claim")
    if device not in declared_devices:
        return "device_not_declared"
    if family not in DEVICE_BUDGET_CLASSES.get(device, {}):
        return "device_budget_not_cover_family"

    evidence = str(objection.get("evidence_quote") or "")
    if len(evidence) < 10:
        return "evidence_quote_too_short"
    if evidence not in scene_text:
        return "evidence_quote_not_found"

    function_claim = str(objection.get("function_claim") or "")
    if not function_claim:
        return "function_claim_empty"
    if len(function_claim) > 50:
        return "function_claim_too_long"
    if any(claim in function_claim for claim in GENERIC_FUNCTION_CLAIMS):
        return "function_claim_too_generic"

    return None


def _apply_machine_objections(work_dir: Path, scene_id: str, directive: dict) -> None:
    objection_path = work_dir / "pipeline" / "review" / f"{scene_id}.machine_objection.yaml"
    if not objection_path.exists():
        return

    ledger_path = work_dir / "pipeline" / "review" / f"{scene_id}.machine_ledger.yaml"
    scene_path = work_dir / "pipeline" / "scenes" / f"scene_{scene_id}.md"
    try:
        objection_data = _load_yaml(objection_path)
        ledger = _load_yaml(ledger_path)
        scene_text = scene_path.read_text(encoding="utf-8")
    except (FileNotFoundError, ValueError, yaml.YAMLError) as exc:
        print(f"[machine_directive] WARN: objection skipped: {exc}", file=sys.stderr)
        return

    objections = objection_data.get("objections", []) or []
    if not isinstance(objections, list):
        print(
            f"[machine_directive] WARN: objection skipped: {objection_path} objections must be a list",
            file=sys.stderr,
        )
        return

    entries = [entry for entry in directive.get("entries", []) or [] if isinstance(entry, dict)]
    entry_by_id = {entry.get("id"): entry for entry in entries if entry.get("id")}
    ledger_entries = ledger.get("entries", []) or []
    ledger_by_id = {
        entry.get("id"): entry
        for entry in ledger_entries
        if isinstance(entry, dict) and entry.get("id")
    }
    declared_devices = set(_devices_for_scene(work_dir, scene_id))

    granted_ids = set()
    for objection in _budgeted_objections(objections):
        target_id = objection.get("target_entry_id")
        reason = _objection_denial_reason(objection, entry_by_id, declared_devices, scene_text)
        ledger_entry = ledger_by_id.get(target_id)
        if reason is None:
            granted_ids.add(target_id)
            if ledger_entry is not None:
                ledger_entry["status"] = "objection_granted"
                ledger_entry.pop("objection_denied_reason", None)
            continue
        if ledger_entry is not None:
            ledger_entry["objection_denied_reason"] = reason

    if granted_ids:
        directive["entries"] = [entry for entry in entries if entry.get("id") not in granted_ids]
    _atomic_write_yaml(ledger_path, ledger)


def _snapshot_pre_dist_once(work_dir: Path, scene_id: str) -> None:
    pre_dist_path = _lint_path(work_dir, scene_id, "pre_dist")
    if pre_dist_path.exists():
        return
    lint_v2_path = _lint_path(work_dir, scene_id, "v2")
    source_path = lint_v2_path if lint_v2_path.exists() else _lint_path(work_dir, scene_id)
    shutil.copyfile(source_path, pre_dist_path)


def refresh_directive(work_dir: Path, scene_id: str) -> int:
    directive_path = work_dir / "pipeline" / "review" / f"{scene_id}.machine_directive.yaml"
    if not directive_path.exists():
        print(f"[machine_directive] ERROR: directive not found: {directive_path}", file=sys.stderr)
        return 2
    try:
        directive = _load_yaml(directive_path)
        _snapshot_pre_dist_once(work_dir, scene_id)
    except (FileNotFoundError, ValueError, yaml.YAMLError) as exc:
        print(f"[machine_directive] ERROR: {exc}", file=sys.stderr)
        return 2

    summary_path = work_dir / "pipeline" / f"scene_{scene_id}" / "revision_summary.md"
    _apply_machine_objections(work_dir, scene_id, directive)
    directive["stage"] = "refreshed"
    directive["dispatch_ready"] = True
    directive["protected_regions"] = _parse_protected_regions(summary_path)
    _atomic_write_yaml(directive_path, directive)
    print(f"✅ {directive_path} refreshed · {len(directive['protected_regions'])} protected_regions")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate machine directive from ai_filler lint output")
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--scene-id", required=True)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--lint-suffix", default=None)
    args = parser.parse_args()

    if args.refresh and args.lint_suffix:
        print("[machine_directive] ERROR: --lint-suffix cannot be used with --refresh", file=sys.stderr)
        return 2

    if args.refresh:
        return refresh_directive(args.work_dir.resolve(), args.scene_id)
    return generate_initial(args.work_dir.resolve(), args.scene_id, args.lint_suffix)


if __name__ == "__main__":
    sys.exit(main())
