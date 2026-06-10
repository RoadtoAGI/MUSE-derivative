#!/usr/bin/env python3
"""
assemble_story.py — 按 phase6_development.yaml 中的场景顺序将场景文件拼接为 story.md

用法：
    python ${CLAUDE_PLUGIN_ROOT}/scripts/assemble_story.py <work_dir>

输入：
    <work_dir>/pipeline/phase6_development.yaml  — 场景索引（含 file_path 字段）
    <work_dir>/pipeline/scenes/scene_*.md        — 各场景正文

输出：
    <work_dir>/story.md  — 拼接后的完整正文
"""

import re
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("用法：python assemble_story.py <work_dir>", file=sys.stderr)
        sys.exit(1)

    work_dir = Path(sys.argv[1]).resolve()
    yaml_path = work_dir / "pipeline" / "phase6_development.yaml"
    output_path = work_dir / "story.md"

    if not yaml_path.exists():
        print(f"错误：找不到 {yaml_path}", file=sys.stderr)
        sys.exit(1)

    # 用正则提取 file_path 字段，绕开 beats 等字段中的 YAML 语法问题
    text = yaml_path.read_text(encoding="utf-8")
    file_paths = [
        p.strip().strip('"').strip("'")
        for p in re.findall(r'^\s+file_path:\s+(.+)$', text, re.MULTILINE)
    ]
    if not file_paths:
        print("错误：phase6_development.yaml 中没有找到 file_path", file=sys.stderr)
        sys.exit(1)

    parts = []
    for rel in file_paths:
        scene_path = work_dir / rel
        if not scene_path.exists():
            print(f"警告：场景文件不存在，已跳过：{scene_path}", file=sys.stderr)
            continue
        parts.append(scene_path.read_text(encoding="utf-8").rstrip("\n"))

    story = "\n\n".join(parts) + "\n"
    output_path.write_text(story, encoding="utf-8")
    print(f"✓ story.md 已生成：{len(parts)} 个场景，{len(story)} 字符 → {output_path}")


if __name__ == "__main__":
    main()
