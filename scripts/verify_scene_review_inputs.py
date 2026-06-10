#!/usr/bin/env python3
"""verify_scene_review_inputs.py — Phase 6 Step 5 input gate

scene-reviewer subagent 启动前由 orchestrator 调用。检查 required 输入完整性，
缺任一 → 退出码 1 + stdout 输出 missing_inputs YAML（供 orchestrator 写降级 yaml）。

接口：
    python3 verify_scene_review_inputs.py --scene-id S01 --pipeline-root <path>

输出（YAML 到 stdout）：
    status: ok | failed
    scene_id: S01
    missing_inputs: [path1, path2, ...]
    optional_present: [path1, ...]    # B/C 文件实际在场时列出

退出码：
    0 — 全部 required 输入在场（含 conditional role_briefs 满足）
    1 — 任一 required 输入缺失

required = 正文 + scene_card + A + 3 lint；
B/C 是 optional——文件存在即列入 optional_present，缺失不 fail；
scene-reviewer 应在 SKILL 中按"存在即读、scene_id 命中本场景的 finding 才用"消费。
"""
import argparse
import sys
from pathlib import Path

import yaml


def _base_required_paths(scene_id):
    """required input：正文 + scene_card + A + 3 lint。"""
    return [
        f"pipeline/scenes/scene_{scene_id}.md",
        f"pipeline/scene_{scene_id}/scene_card.md",
        "pipeline/review/A_aesthetic.yaml",
        f"pipeline/review/lint/{scene_id}.ai_filler.yaml",
        f"pipeline/review/lint/{scene_id}.lexical_stats.yaml",
        f"pipeline/review/lint/{scene_id}.dialogue.yaml",
    ]


def _optional_paths():
    """optional inputs：B/C 文件存在则列入 optional_present。"""
    return [
        "pipeline/review/B_narrative_consistency.yaml",
        "pipeline/review/C_structural_consistency.yaml",
    ]


def _voice_consistency_in_scene(a_aesthetic_path, scene_id):
    """A_aesthetic.yaml 是否含 voice_consistency finding 且 scene_id 命中本场景。"""
    try:
        data = yaml.safe_load(a_aesthetic_path.read_text()) or {}
    except (OSError, yaml.YAMLError):
        return False
    findings = data.get("review_findings")
    if findings is None:
        findings = data.get("findings", []) or []
    for f in findings:
        if not isinstance(f, dict):
            continue
        if f.get("dimension") == "voice_consistency" and f.get("scene_id") == scene_id:
            return True
    return False


def verify(pipeline_root, scene_id):
    """返回 (missing_inputs: list[str], optional_present: list[str])。"""
    root = Path(pipeline_root)
    missing = []
    optional_present = []

    for rel in _optional_paths():
        if (root / rel).exists():
            optional_present.append(rel)

    for rel in _base_required_paths(scene_id):
        if not (root / rel).exists():
            missing.append(rel)

    a_path = root / "pipeline/review/A_aesthetic.yaml"
    if a_path.exists() and _voice_consistency_in_scene(a_path, scene_id):
        rb = f"pipeline/scene_{scene_id}/role_briefs.md"
        if not (root / rb).exists():
            missing.append(rb)

    return missing, optional_present


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--scene-id", required=True)
    parser.add_argument("--pipeline-root", required=True)
    args = parser.parse_args()

    missing, optional_present = verify(args.pipeline_root, args.scene_id)
    payload = {
        "status": "ok" if not missing else "failed",
        "scene_id": args.scene_id,
        "missing_inputs": missing,
    }
    if optional_present:
        payload["optional_present"] = optional_present
    yaml.safe_dump(payload, sys.stdout, allow_unicode=True, sort_keys=False)
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
