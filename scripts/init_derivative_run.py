#!/usr/bin/env python3
"""init_derivative_run.py — 衍生写作（同人 / 续写 / 外传 / 跨风格改编）工作目录初始化

自含脚本（不依赖 muse-writing 的 init_run.py）：
  1. 自建 work_dir + 子目录骨架（内联 init_run 的 skeleton + 时间戳策略）
  2. 从 muse-canon-distill 模糊匹配小说 + 复制蒸馏物到 pipeline/references/canon/<slug>/
  3. 长篇正文（> 阈值 KB）跳过复制，生成 LONG_NOVEL_NOTICE.md（禁读硬约束）

Usage:
    python3 init_derivative_run.py --novel "射雕" --query "<衍生创作需求>"
    python3 init_derivative_run.py --novel "三体" --query "续写..." --timestamp 2026-05-30T1500
    python3 init_derivative_run.py --novel "海的女儿" --results-dir results/  # 短篇正文会复制
    python3 init_derivative_run.py --novel "三体" --run-dir /abs/path/to/run  # 显式 run 目录
    python3 init_derivative_run.py --existing-pipeline /abs/path  # 用户已有 phaseN 文档，跳过 canon

stdout 输出 work_dir 绝对路径，供 orchestrator 作为后续 phase work_dir。

Author: MUSE-derivative
"""

from __future__ import annotations

import argparse
import os
import re
import secrets
import shutil
import sys
from datetime import datetime
from pathlib import Path

# 默认长篇阈值：full_text 文件 > 此 KB 数则不复制
DEFAULT_LONG_NOVEL_KB = 200

# work_dir 子目录骨架（含 derivative/ 承载执行计划 + manifest + review）
SUBDIRS = [
    "pipeline/scenes",
    "pipeline/characters",
    "pipeline/staging",
    "pipeline/references",
    "pipeline/references/canon",
    "pipeline/derivative",
    "pipeline/review/lint",
    "pipeline/audit",
    "pipeline/story-character-skills/.claude/skills",
]

# 译名 / 通称 → canon 目录名 的别名映射。
# 加 entry 的判据：原作有多个流通译名/通称，且其中至少一个无法通过子串匹配落到 canon 目录上。
NOVEL_ALIASES = {
    "美人鱼": "海的女儿",
    "小美人鱼": "海的女儿",
}


# ----------------------------------------------------------------------------
# work_dir 骨架 + 时间戳策略（内联自 muse-writing/scripts/init_run.py，使本脚本自含）
# ----------------------------------------------------------------------------

def _slugify(query: str, max_len: int = 32) -> str:
    """从 query 提取文件系统友好的 slug（中英文保留）。"""
    if not query:
        return "run"
    s = re.sub(r"[^\w一-鿿-]+", "-", query.strip())
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:max_len] or "run"


def _validate_user_timestamp(ts: str) -> str:
    """校验 timestamp 格式。允许 YYYY-MM-DDTHHMM 或 YYYY-MM-DDTHHMMSS。"""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{4}(\d{2})?", ts):
        raise ValueError(
            f"--timestamp 格式应为 YYYY-MM-DDTHHMM 或 YYYY-MM-DDTHHMMSS（如 2026-05-30T1500），实为：{ts}"
        )
    return ts


def _make_skeleton(run_path: Path) -> Path:
    """在 run_path 下幂等建 pipeline/ + 子目录骨架。"""
    run_path.mkdir(parents=True, exist_ok=True)
    for sub in SUBDIRS:
        (run_path / sub).mkdir(parents=True, exist_ok=True)
    return run_path


def resolve_work_dir(results_dir: str, run_dir: str | None, query: str | None,
                     slug: str | None, user_timestamp: str | None) -> tuple[Path, str]:
    """选定并创建 work_dir。返回 (work_dir, strategy_note)。

    显式模式（--run-dir）：在给定绝对路径下幂等建骨架。
    派生模式（--results-dir）：派生 slug + 时间戳（整点优先，冲突 fallback 精确）。
    """
    if run_dir:
        run_path = Path(run_dir).resolve()
        _make_skeleton(run_path)
        return run_path, f"使用显式 run-dir={run_path}"

    results_root = Path(results_dir).resolve()
    results_root.mkdir(parents=True, exist_ok=True)
    actual_slug = slug if slug else _slugify(query or "")
    now = datetime.now()

    if user_timestamp:
        ts = _validate_user_timestamp(user_timestamp)
        run_path = results_root / f"{ts}_{actual_slug}"
        if run_path.exists():
            raise FileExistsError(
                f"用户指定的 timestamp 已存在：{run_path}（用户指定模式下不自动 fallback，请改名或换 timestamp）"
            )
        note = f"使用用户指定 timestamp={ts}"
    else:
        hour_ts = now.strftime("%Y-%m-%dT%H00")
        hour_path = results_root / f"{hour_ts}_{actual_slug}"
        if not hour_path.exists():
            run_path = hour_path
            note = f"使用整点 timestamp={hour_ts}"
        else:
            precise_ts = now.strftime("%Y-%m-%dT%H%M%S")
            run_path = results_root / f"{precise_ts}_{actual_slug}"
            if run_path.exists():
                run_path = results_root / f"{precise_ts}_{actual_slug}-{secrets.token_hex(2)}"
            note = f"整点 {hour_ts} 已占用，fallback 到精确 timestamp={precise_ts}"

    _make_skeleton(run_path)
    return run_path, note


# ----------------------------------------------------------------------------
# canon 物料定位 + 复制（自 muse-canon-distill 蒸馏物）
# ----------------------------------------------------------------------------

def find_canon_root() -> Path:
    """定位 muse-canon-distill/knowledge-base/novels/ 根目录。

    优先级：
      1. 环境变量 MUSE_CANON_ROOT
      2. ${CLAUDE_PLUGIN_ROOT}/../MUSE-canon-distill/knowledge-base/novels（兄弟 plugin 假设）
      3. 脚本相对路径回溯（开发态 monorepo 路径）
    """
    if env := os.environ.get("MUSE_CANON_ROOT"):
        p = Path(env)
        if p.is_dir():
            return p

    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        candidate = Path(plugin_root).parent / "MUSE-canon-distill" / "knowledge-base" / "novels"
        if candidate.is_dir():
            return candidate

    here = Path(__file__).resolve().parent
    candidate = here.parent.parent / "MUSE-canon-distill" / "knowledge-base" / "novels"
    if candidate.is_dir():
        return candidate

    print("[init_derivative] 无法定位 MUSE-canon-distill 物料目录", file=sys.stderr)
    print("  尝试过: env MUSE_CANON_ROOT / ${CLAUDE_PLUGIN_ROOT}/../MUSE-canon-distill / 脚本相对路径", file=sys.stderr)
    print("  请确认 MUSE-canon-distill 姊妹 plugin 已安装，或通过 MUSE_CANON_ROOT 显式指定；", file=sys.stderr)
    print("  无 canon 蒸馏物时改用 --existing-pipeline 挂载已有 phase 文档", file=sys.stderr)
    sys.exit(2)


def fuzzy_match_novel(canon_root: Path, query: str):
    """模糊匹配小说名。多匹配报错让用户消歧；零匹配列前 20 候选。"""
    novels = sorted([p.name for p in canon_root.iterdir() if p.is_dir()])

    if query in NOVEL_ALIASES:
        aliased = NOVEL_ALIASES[query]
        print(f"[init_derivative] alias: '{query}' → '{aliased}'", file=sys.stderr)
        query = aliased

    if query in novels:
        return canon_root / query, query

    matches = [n for n in novels if query in n or n in query]
    if len(matches) == 1:
        return canon_root / matches[0], matches[0]
    if len(matches) > 1:
        print(f"[init_derivative] 模糊匹配 '{query}' 命中多本，请精确指定：", file=sys.stderr)
        for m in matches:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(2)

    print(f"[init_derivative] 未找到匹配 '{query}' 的小说", file=sys.stderr)
    print("  可选小说（前 20 本，按字母序）：", file=sys.stderr)
    for n in novels[:20]:
        print(f"  - {n}", file=sys.stderr)
    if len(novels) > 20:
        print(f"  ...另 {len(novels) - 20} 本", file=sys.stderr)
    sys.exit(2)


def slugify_novel(s: str) -> str:
    """canon 子目录 slug（中文保留）。"""
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"[^\w一-鿿\-]", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:48] or "novel"


def is_full_text_file(name: str, novel_name: str) -> bool:
    """判断是否为正文文件（长篇时跳过复制）。"""
    patterns = {
        "full_text.md", "full_text.txt",
        "正文.md", "正文.txt",
        f"{novel_name}.md", f"{novel_name}.txt",
    }
    return name in patterns


def detect_long_novel(src: Path, novel_name: str, long_novel_kb: int):
    """检测原作是否长篇。返回 (is_long, max_full_text_kb)。"""
    max_kb = 0
    for p in src.iterdir():
        if p.is_file() and is_full_text_file(p.name, novel_name):
            kb = p.stat().st_size // 1024
            if kb > max_kb:
                max_kb = kb
    return max_kb > long_novel_kb, max_kb


def copy_canon_material(src: Path, dst: Path, novel_name: str, long_novel_kb: int):
    """复制 canon 物料；长篇正文跳过；生成 NOTICE。"""
    dst.mkdir(parents=True, exist_ok=True)

    is_long, full_text_kb = detect_long_novel(src, novel_name, long_novel_kb)
    stats = {
        "copied": 0,
        "skipped_full_text": [],
        "total_size_kb": 0,
        "is_long": is_long,
        "full_text_size_kb": full_text_kb,
    }

    for src_path in src.rglob("*"):
        if src_path.is_dir():
            continue
        rel = src_path.relative_to(src)
        if is_long and is_full_text_file(src_path.name, novel_name):
            stats["skipped_full_text"].append(str(rel))
            continue
        dst_path = dst / rel
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        stats["copied"] += 1
        stats["total_size_kb"] += src_path.stat().st_size // 1024

    if is_long:
        notice = dst / "LONG_NOVEL_NOTICE.md"
        lines = [
            "# 长篇小说提示",
            "",
            f"原作 `{novel_name}` 正文体量 ~{full_text_kb} KB（估算 ~{full_text_kb * 1000 // 3} 字），"
            f"超过 `long_novel_kb` 阈值 {long_novel_kb} KB；**正文文件未复制**到本工作目录。",
            "",
            "## 衍生创作约束（硬约束）",
            "",
            "- **禁止 Read 原作正文**（即使你能在 MUSE-canon-distill 仓库内找到 `full_text.md` / `正文.md` / `<书名>.txt`）",
            "- 衍生创作所依赖的原作设计层信息已蒸馏并复制到本目录：",
            "  - `characters/` — 角色档案蒸馏（人物 voice / 弧光 / 关系）",
            "  - `scenes/scene_*.md` — 场景级蒸馏（场景功能 / 节拍）",
            "  - `scene_index.json` — 场景索引",
            "  - `craft_notes/` — 节拍设计蒸馏（如有）",
            "  - `pipeline/phase*.yaml` — phase 设计 yaml 蒸馏（如有）",
            "  - `navigation.md` — 章节导航",
            "  - `segments/` — 段落级蒸馏（如有）",
            "- 续写 / 同人 / 外传所需的原作连贯性从上述蒸馏物提取，不需要回查原文",
            "- 风格 few-shot 通过 `craft_notes/` + `scenes/scene_*.md`（已蒸馏过的场景）即可",
            "- 极短引用（≤ 15 字 / 句）允许从 `scenes/scene_*.md` 蒸馏物中借用 signature_phrases；不可借大段",
            "",
            "## 已跳过的正文文件",
            "",
        ]
        for skipped in stats["skipped_full_text"]:
            lines.append(f"- `{skipped}`")
        notice.write_text("\n".join(lines) + "\n")

    return stats


# reuse_mode → 预置（pre-seed）哪些 phase 设计 yaml 到 work_dir/pipeline/（继承基线）。
# phase1-5 有 honor-yaml 逻辑（在预置 yaml 上完善，不重生成）；未预置的 phase 从零生成。
# phase0 仅 cross_style_rewrite 预置（构想 locked；入口不重调 phase0-conception）。
REUSE_SEED_PHASES = {
    "fan_fiction": [1, 2],
    "sequel": [1, 2, 3, 4, 5],
    "spin_off": [1, 2],
    "cross_style_rewrite": [0, 1, 2, 3, 4, 5],
}


def pre_seed_phase_docs(src_pipeline: Path, work_dir: Path, phases) -> list:
    """把 src_pipeline 下的 phase{N}_*.yaml 预置到 work_dir/pipeline/（继承基线）。

    phase1-5 的 honor-yaml 逻辑会在预置 yaml 上完善；缺该 phase 蒸馏（glob 空）则不预置、该 phase 从零生成。
    返回已预置文件名列表。
    """
    seeded = []
    if not src_pipeline.is_dir():
        return seeded
    dst_pipeline = work_dir / "pipeline"
    dst_pipeline.mkdir(parents=True, exist_ok=True)
    for n in phases:
        for src_yaml in sorted(src_pipeline.glob(f"phase{n}_*.yaml")):
            shutil.copy2(src_yaml, dst_pipeline / src_yaml.name)
            seeded.append(src_yaml.name)
    return seeded


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--novel",
                    help="小说名（模糊匹配 MUSE-canon-distill/knowledge-base/novels/ 下子目录）；"
                         "canon_distill source 必填")
    ap.add_argument("--existing-pipeline",
                    help="existing_pipeline source：用户已有 phaseN 文档的目录（绝对路径）；"
                         "提供时跳过 canon 匹配，仅建 skeleton + 软链/复制已有 phase 文档语义由 orchestrator 处理")
    ap.add_argument("--query", help="用户写作需求一句话（用于派生 slug）")
    ap.add_argument("--slug", help="显式 work_dir slug（覆盖从 query 派生）")
    ap.add_argument("--timestamp", help="显式 timestamp（YYYY-MM-DDTHHMM；冲突直接报错）")
    ap.add_argument("--results-dir", default="results/",
                    help="results 根目录（默认 results/）")
    ap.add_argument("--run-dir",
                    help="显式 run 目录（绝对路径；与 --query / --slug / --timestamp 宽容互斥）")
    ap.add_argument("--long-novel-kb", type=int, default=DEFAULT_LONG_NOVEL_KB,
                    help=f"长篇阈值（KB），超过则不复制正文文件（默认 {DEFAULT_LONG_NOVEL_KB}）")
    ap.add_argument("--canon-subdir",
                    help="canon 物料在 work_dir 内的子目录（默认 pipeline/references/canon/<novel-slug>）")
    ap.add_argument("--reuse-mode", choices=list(REUSE_SEED_PHASES),
                    help="衍生复用档（fan_fiction/sequel/spin_off/cross_style_rewrite）；"
                         "决定预置哪些 phase 设计 yaml 到 work_dir/pipeline/ 作继承基线（phase1-5 在其上完善）")

    args = ap.parse_args()

    if not args.novel and not args.existing_pipeline:
        ap.error("需提供 --novel（canon_distill source）或 --existing-pipeline（existing_pipeline source）其一")

    # --run-dir 模式下派生参数宽容忽略 + stderr WARN（与原行为对齐）
    if args.run_dir:
        ignored = [n for n, v in (("--query", args.query), ("--slug", args.slug),
                                  ("--timestamp", args.timestamp),
                                  ("--results-dir", args.results_dir if args.results_dir != "results/" else None))
                   if v]
        if ignored:
            print(f"[init_derivative WARN] --run-dir 模式下忽略派生参数：{', '.join(ignored)}", file=sys.stderr)

    # 建 work_dir 骨架（自含，不调外部脚本）
    try:
        work_dir, note = resolve_work_dir(
            results_dir=args.results_dir, run_dir=args.run_dir,
            query=args.query or (f"derivative-{args.novel}" if args.novel else "derivative-existing"),
            slug=args.slug, user_timestamp=args.timestamp,
        )
    except (ValueError, FileExistsError) as e:
        print(f"[init_derivative ERROR] {e}", file=sys.stderr)
        sys.exit(2)
    print(f"[init_derivative] {note}", file=sys.stderr)
    print(f"[init_derivative] work_dir: {work_dir}", file=sys.stderr)

    # existing_pipeline source：不匹配 canon，仅建骨架 + 提示 orchestrator 挂载已有 phase 文档
    if args.existing_pipeline and not args.novel:
        ep = Path(args.existing_pipeline).resolve()
        if not ep.is_dir():
            print(f"[init_derivative ERROR] --existing-pipeline 路径不存在或非目录：{ep}", file=sys.stderr)
            sys.exit(2)
        print(f"[init_derivative] source=existing_pipeline，已有 phase 文档目录：{ep}", file=sys.stderr)
        if args.reuse_mode:
            seeded = pre_seed_phase_docs(ep / "pipeline", work_dir, REUSE_SEED_PHASES[args.reuse_mode])
            print(f"  - reuse_mode={args.reuse_mode}：预置 phase 文档 {seeded or '（无匹配，全 phase 从零生成）'}", file=sys.stderr)
        else:
            print(f"  - 未传 --reuse-mode：未预置 phase 文档（orchestrator 自行决定挂载 {ep}/pipeline/phase*.yaml）", file=sys.stderr)
        print(work_dir)
        return

    # canon_distill source
    canon_root = find_canon_root()
    novel_path, novel_name = fuzzy_match_novel(canon_root, args.novel)
    print(f"[init_derivative] 匹配小说: {novel_name}", file=sys.stderr)

    canon_slug = slugify_novel(novel_name)
    if args.canon_subdir:
        canon_dst = work_dir / args.canon_subdir
    else:
        canon_dst = work_dir / "pipeline" / "references" / "canon" / canon_slug

    stats = copy_canon_material(novel_path, canon_dst, novel_name, args.long_novel_kb)

    print(f"[init_derivative] canon 物料已复制到 {canon_dst.relative_to(work_dir)}", file=sys.stderr)
    print(f"  - 文件数：{stats['copied']}", file=sys.stderr)
    print(f"  - 总大小：{stats['total_size_kb']} KB", file=sys.stderr)
    if stats["is_long"]:
        print(f"  - 长篇标识：正文 ~{stats['full_text_size_kb']} KB > 阈值 {args.long_novel_kb} KB", file=sys.stderr)
        print(f"  - 跳过正文文件 {len(stats['skipped_full_text'])} 个", file=sys.stderr)
        print(f"  - LONG_NOVEL_NOTICE.md 已生成（含禁读硬约束）", file=sys.stderr)
    else:
        print(f"  - 短篇：正文 ~{stats['full_text_size_kb']} KB ≤ 阈值；正文已复制", file=sys.stderr)

    # 预置 phase 设计 yaml（继承基线）——phase1-5 在其上完善
    if args.reuse_mode:
        seeded = pre_seed_phase_docs(novel_path / "pipeline", work_dir, REUSE_SEED_PHASES[args.reuse_mode])
        print(f"[init_derivative] reuse_mode={args.reuse_mode}：预置 phase 文档 {seeded or '（canon 无 phase 蒸馏，全 phase 从零生成）'}", file=sys.stderr)
    else:
        print(f"[init_derivative] 未传 --reuse-mode：未预置 phase 文档（全 phase 从零生成）", file=sys.stderr)

    print(work_dir)


if __name__ == "__main__":
    main()
