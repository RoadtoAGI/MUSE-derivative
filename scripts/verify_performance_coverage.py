#!/usr/bin/env python3
"""verify_performance_coverage.py — Phase 6 writer dispatch 硬前置(Step 4d)

writer dispatch 前由 orchestrator 协议步骤 / PreToolUse hook 调用。逐场校验
performance 素材覆盖;不通过 → 退出码 1 + stderr 给缺口清单,阻断 writer dispatch。

接口:
    python3 verify_performance_coverage.py --work-dir <run根> [--scene S01]

退出码:
    0 — 全部受检场景通过(slug 集合等价 或 该场有合法 skip 条目)
    1 — 覆盖缺口 / skip 契约违规 / performance 文件缺最小结构

判据(全部机器可数,所有场景受检):
- 期望集 = pipeline/scene_{sid}/role_briefs.md 内 `^character:\\s*(\\S+)` 捕获去重;
  role_briefs.md 缺失或无 character: 段 = 上游漏步,**skip 声明不豁免**
- 实际集 = pipeline/staging/scene_{sid}/*_performance.md 文件名前缀
- 集合等价(不是数量相等)——防"文件数对但张冠李戴/漏人"
- skip 契约:pipeline/audit/skip_performance.yaml 须为条目列表,每条 scene_id
  匹配 ^S\\d+$ 且 reason 非空;批量声明(all/通配/default/scenes/range 键)
  → 全局报错 exit 1,不只跳过该条
- 最小结构:performance 文件的 lines / forbidden 两个顶层 key 须各带至少一个列表项
  (光有 key 没条目 = 实质缺字段);HTML 注释内的 key 不计,fenced code block 内的
  计——actor 把 schema 包在 ```yaml fence 里是合法产物形态
- 全扫描(省略 --scene)发现零场景 → exit 1(work-dir 传错时不得静默放行)
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

CHARACTER_RE = re.compile(r"^character:\s*(\S+)", re.MULTILINE)
SCENE_ID_RE = re.compile(r"^S\d+$")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
MIN_KEYS = ("lines", "forbidden")
BANNED_SKIP_KEYS = {"scenes", "range"}
PERF_SUFFIX = "_performance.md"


def fail(msg):
    print(msg, file=sys.stderr)


def _key_has_item(text, key):
    """顶层 key 存在且其下第一条实质行是列表项。HTML 注释已剔除;fence 保留。"""
    lines = text.splitlines()
    pat = re.compile(rf"^{key}\s*:\s*$")
    for i, line in enumerate(lines):
        if not pat.match(line):
            continue
        for nxt in lines[i + 1:]:
            stripped = nxt.strip()
            if not stripped or stripped.startswith("#"):
                continue
            return stripped.startswith("-")
    return False


def missing_min_keys(text):
    body = HTML_COMMENT_RE.sub("", text)
    return [k for k in MIN_KEYS if not _key_has_item(body, k)]


def load_skip_entries(work_dir):
    """读取并全量校验 skip_performance.yaml;违约 → (None, 错误列表)。"""
    path = work_dir / "pipeline" / "audit" / "skip_performance.yaml"
    if not path.exists():
        return {}, []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, [f"skip_performance.yaml 解析失败: {exc}"]
    if not isinstance(data, list):
        return None, ["skip_performance.yaml 须为条目列表(- scene_id: … / reason: …)"]
    errors = []
    valid = {}
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            errors.append(f"skip 条目 {i}: 非 mapping")
            continue
        banned = BANNED_SKIP_KEYS & set(entry)
        if banned:
            errors.append(f"skip 条目 {i}: 含批量声明键 {sorted(banned)}(一条记录 = 一个精确 scene_id)")
            continue
        sid = str(entry.get("scene_id", "")).strip()
        reason = str(entry.get("reason", "") or "").strip()
        if not SCENE_ID_RE.match(sid):
            errors.append(f"skip 条目 {i}: scene_id '{sid}' 非精确单场(禁 all/通配/列表/区间)")
            continue
        if not reason:
            errors.append(f"skip 条目 {i}: reason 为空")
            continue
        valid[sid] = reason
    if errors:
        return None, errors
    return valid, []


def discover_scenes(work_dir):
    return sorted(
        p.name[len("scene_"):]
        for p in (work_dir / "pipeline").glob("scene_*")
        if p.is_dir()
    )


def check_scene(work_dir, sid, skip_map):
    problems = []
    briefs = work_dir / "pipeline" / f"scene_{sid}" / "role_briefs.md"

    # 期望集不可为空:role_briefs 缺失/无 character: 段是上游 role-brief-deriver 漏步,
    # skip 声明只豁免"本场不产素材",不豁免"不知道本场有谁"——先于 skip 短路硬失败
    if not briefs.exists():
        problems.append(
            f"scene {sid}: role_briefs.md 缺失(上游 role-brief-deriver 漏步);"
            f"skip 声明不豁免此项"
        )
        return problems
    expected = set(CHARACTER_RE.findall(briefs.read_text(encoding="utf-8")))
    if not expected:
        problems.append(
            f"scene {sid}: role_briefs.md 无 character: 段(期望集为空);"
            f"skip 声明不豁免此项"
        )
        return problems

    staging = work_dir / "pipeline" / "staging" / f"scene_{sid}"
    perf_files = sorted(staging.glob(f"*{PERF_SUFFIX}")) if staging.exists() else []
    actual = {p.name[: -len(PERF_SUFFIX)] for p in perf_files}

    # 最小结构:与覆盖判定独立,文件在场就查
    for p in perf_files:
        missing_keys = missing_min_keys(p.read_text(encoding="utf-8"))
        if missing_keys:
            problems.append(f"scene {sid}: {p.name} 缺最小结构字段 {missing_keys}(视为排练失败)")

    if actual == expected:
        return problems
    if sid in skip_map:
        return problems
    detail = []
    missing_slugs = sorted(expected - actual)
    extra_slugs = sorted(actual - expected)
    if missing_slugs:
        detail.append(f"缺失 slug: {missing_slugs}")
    if extra_slugs:
        detail.append(f"多余 slug: {extra_slugs}")
    problems.append(
        f"scene {sid}: performance 覆盖不通过({'; '.join(detail)});"
        f"需补 fan-out 或在 audit/skip_performance.yaml 写该场合法条目"
    )
    return problems


def main():
    ap = argparse.ArgumentParser(description="performance 素材覆盖检查(writer dispatch 硬前置)")
    ap.add_argument("--work-dir", required=True, help="run 根目录(含 pipeline/)")
    ap.add_argument("--scene", default=None, help="精确场景号(如 S01);省略时扫全部 pipeline/scene_*")
    args = ap.parse_args()
    work_dir = Path(args.work_dir)

    skip_map, skip_errors = load_skip_entries(work_dir)
    if skip_errors:
        for e in skip_errors:
            fail(e)
        return 1

    scenes = [args.scene] if args.scene else discover_scenes(work_dir)
    if not scenes:
        fail(f"{work_dir} 下未发现任何 pipeline/scene_* 目录——work-dir 路径可疑,不放行 writer")
        return 1
    problems = []
    for sid in scenes:
        problems.extend(check_scene(work_dir, sid, skip_map))
    for p in problems:
        fail(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
