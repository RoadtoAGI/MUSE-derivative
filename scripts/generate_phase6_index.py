#!/usr/bin/env python3
"""
generate_phase6_index.py - 生成 phase6_development.yaml 骨架

从 phase5_scenes.yaml 提取设计字段（scene_id, arc_id, sequence_id, title），
从 scenes/*.md 统计实际字数，合并输出骨架 YAML。
orchestrator 只需补 summary 和 beats。

用法：
    python ${CLAUDE_PLUGIN_ROOT}/scripts/generate_phase6_index.py <work_dir>

输出：
    <work_dir>/pipeline/phase6_development.yaml
"""

import re
import sys
from pathlib import Path

import yaml

from yaml_resilient import load_yaml_resilient


def count_words(text: str) -> int:
    """中英文混合字数统计：中文按字，英文按词。"""
    # 英文单词
    english = re.findall(r"[a-zA-Z]+(?:\'[a-zA-Z]+)?", text)
    # 中文字符
    chinese = re.findall(r"[一-鿿]", text)
    return len(english) + len(chinese)


def parse_phase5_scenes(yaml_path: Path) -> list[dict]:
    """从 phase5_scenes.yaml 的 sequence_expansions[].scenes[] 提取每个场景的设计字段。

    用 PyYAML 正确解析嵌套结构（旧版正则会被 arc_progression 等其他顶级段
    污染——遇到 ``- scene_id: S01`` 时无法判别属于哪个 sequence；复盘
    query 184 第一/二轮均触发 "sequence_id 全为 Q3" 的漂移 bug）。
    """
    data, report = load_yaml_resilient(yaml_path.read_text(encoding="utf-8"))
    data = data or {}
    if report.recovered_lines:
        sys.stderr.write(
            f"[WARN] {yaml_path}: auto-recovered broken double-quoted scalars "
            f"at line(s) {report.recovered_lines} (promoted to block scalar).\n"
        )

    scenes = []
    for seq in data.get("sequence_expansions") or []:
        seq_id = seq.get("sequence_id")
        seq_arc_id = seq.get("arc_id")
        for scene in seq.get("scenes") or []:
            sid = scene.get("scene_id")
            if not sid:
                continue
            scenes.append({
                "scene_id": str(sid),
                # scene 自带 sequence_id 优先，否则继承自所属 sequence_expansions 项
                "sequence_id": str(scene.get("sequence_id") or seq_id or ""),
                "arc_id": str(scene.get("arc_id") or seq_arc_id or ""),
                "title": str(scene.get("title") or ""),
            })

    return scenes


def main():
    if len(sys.argv) != 2:
        print("用法：python generate_phase6_index.py <work_dir>", file=sys.stderr)
        sys.exit(1)

    work_dir = Path(sys.argv[1]).resolve()
    from extract_scene_card import _verify_prose_risk_contract_used
    _verify_prose_risk_contract_used(work_dir)
    phase5_path = work_dir / "pipeline" / "phase5_scenes.yaml"
    scenes_dir = work_dir / "pipeline" / "scenes"
    output_path = work_dir / "pipeline" / "phase6_development.yaml"

    # 从 Phase 5 提取设计字段
    design = {}
    if phase5_path.exists():
        for s in parse_phase5_scenes(phase5_path):
            design[s["scene_id"]] = s

    # 扫描实际场景文件
    scene_files = sorted(scenes_dir.glob("scene_*.md")) if scenes_dir.exists() else []

    # phase5-only skeleton 模式（2026-05-18 plan T19a）：
    # 当 pipeline/scenes/ 无文件时（如 phase5 刚写完、writer 尚未跑），
    # 仅按 phase5_scenes.yaml 的设计字段产骨架 + file_path 填 writer 待产出位置 placeholder。
    # 让 auto-phase6-index hook 在 phase5_scenes.yaml 写入时也能产物。
    skeleton_mode = not scene_files

    entries = []
    total_words = 0
    if skeleton_mode:
        if not design:
            print(f"错误：{scenes_dir} 下无场景文件，且 {phase5_path} 也无设计字段——无法产 phase6 骨架",
                  file=sys.stderr)
            sys.exit(1)
        for sid, info in design.items():
            entries.append({
                "scene_id": sid,
                "file_path": f"pipeline/scenes/scene_{sid}.md",  # writer 待产出位置 placeholder
                "arc_id": info.get("arc_id", ""),
                "sequence_id": info.get("sequence_id", ""),
                "title": info.get("title", ""),
                "approximate_words": 0,  # 无文件可统计
            })
    else:
        for f in scene_files:
            # 从文件名提取 scene_id：scene_SC01.md → SC01, scene_S01.md → S01
            sid = f.stem.replace("scene_", "")
            content = f.read_text(encoding="utf-8")
            wc = count_words(content)
            total_words += wc

            info = design.get(sid, {})
            entries.append({
                "scene_id": sid,
                "file_path": f"pipeline/scenes/{f.name}",
                "arc_id": info.get("arc_id", ""),
                "sequence_id": info.get("sequence_id", ""),
                "title": info.get("title", ""),
                "approximate_words": wc,
            })

    # 写 YAML（手动拼接，避免 PyYAML 输出风格分歧；解析输入用 PyYAML 已足够正确）
    lines = ["scenes:"]
    for e in entries:
        lines.append(f'  - scene_id: {e["scene_id"]}')
        lines.append(f'    file_path: {e["file_path"]}')
        if e["arc_id"]:
            lines.append(f'    arc_id: {e["arc_id"]}')
        if e["sequence_id"]:
            lines.append(f'    sequence_id: {e["sequence_id"]}')
        if e["title"]:
            lines.append(f'    title: "{e["title"]}"')
        lines.append(f'    summary: ""  # orchestrator 按需补充')
        lines.append(f'    approximate_words: {e["approximate_words"]}')
        lines.append("")

    lines.append(f"total_word_count: {total_words}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✓ phase6_development.yaml 骨架已生成：{len(entries)} 个场景，{total_words} 词")
    print(f"  待 orchestrator 按需补充：summary")
    print(f"  路径：{output_path}")


if __name__ == "__main__":
    main()
