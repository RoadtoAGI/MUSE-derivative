#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from ai_filler_lint import (
    RULE_TO_FAMILY,
    _coefficient_of_variation,
    _sentence_lengths,
    analyze,
    detect_lang,
)


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(float(ordered[0]), 4)
    rank = (len(ordered) - 1) * percentile
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    value = ordered[lower] * (1 - weight) + ordered[upper] * weight
    return round(float(value), 4)


def _denominator(text: str, lang: str) -> float:
    # 与 aggregate_cluster_alerts 的 char_k 同口径（en 同 zh 按字符），
    # 否则基线与运行时 density 分母错位，抑制 gate 失真。
    return max(len(text) / 1000, 0.001)


def collect_family_densities(kb_root: Path) -> dict[str, dict[str, list[float]]]:
    densities: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    scene_paths = sorted(
        p for p in (kb_root / "novels").glob("*/scenes/*.md")
        if not p.stem.endswith("_craft")
    )
    for scene_path in scene_paths:
        text = scene_path.read_text(encoding="utf-8")
        lang = detect_lang(text)
        result = analyze(text, scene_id=scene_path.stem, lang=lang)
        counts: Counter[str] = Counter()
        for hit in result.get("hits", []):
            family = hit.get("family") or RULE_TO_FAMILY.get(hit.get("rule"))
            if family:
                counts[str(family)] += 1
        denom = _denominator(text, lang)
        for family, count in counts.items():
            densities[lang][family].append(round(count / denom, 4))
    return densities


def collect_sentence_cvs(kb_root: Path) -> dict[str, list[float]]:
    cvs: dict[str, list[float]] = defaultdict(list)
    scene_paths = sorted(
        p for p in (kb_root / "novels").glob("*/scenes/*.md")
        if not p.stem.endswith("_craft")
    )
    for scene_path in scene_paths:
        text = scene_path.read_text(encoding="utf-8")
        lang = detect_lang(text)
        lengths = _sentence_lengths(text, lang)
        if len(lengths) < 12:
            continue
        cvs[lang].append(round(_coefficient_of_variation(lengths), 4))
    return cvs


def build_calibration(kb_root: Path) -> dict:
    densities = collect_family_densities(kb_root)
    sentence_cvs = collect_sentence_cvs(kb_root)
    output = {}
    for lang in sorted(set(densities) | set(sentence_cvs)):
        output[lang] = {}
        if lang in sentence_cvs:
            values = sentence_cvs[lang]
            output[lang]["sentence_cv"] = {
                "p10": _percentile(values, 0.10),
                "p50": _percentile(values, 0.50),
                "p90": _percentile(values, 0.90),
                "samples": len(values),
            }
        family_values = densities.get(lang, {})
        for family, values in sorted(family_values.items()):
            output[lang][family] = {
                "p80": _percentile(values, 0.80),
                "p90": _percentile(values, 0.90),
                "samples": len(values),
            }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Shadow calibrate AI-pattern baselines over KB scenes")
    parser.add_argument("--kb-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if not args.kb_root.exists():
        print(f"[calibrate_baselines] ERROR: kb root not found: {args.kb_root}", file=sys.stderr)
        return 2

    try:
        calibration = build_calibration(args.kb_root)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(yaml.safe_dump(calibration, allow_unicode=True, sort_keys=False), encoding="utf-8")
    except Exception as exc:
        print(f"[calibrate_baselines] ERROR: {exc}", file=sys.stderr)
        return 2

    scene_count = len([
        p for p in (args.kb_root / "novels").glob("*/scenes/*.md")
        if not p.stem.endswith("_craft")
    ])
    print(f"✅ {args.out} · {scene_count} scenes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
