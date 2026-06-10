"""Schema checks for scene-reviewer output."""

from dataclasses import dataclass


YIELD_TYPES = [
    "plot_change",
    "danger_change",
    "tactical_change",
    "character_choice",
    "relationship_shift",
    "world_rule",
    "sensory_irreplaceable",
    "formal_function",
]


@dataclass
class PassValidationResult:
    valid: bool
    reason: str = ""


# Rn+2 P1-4 + N1 + R1 F4/F7 fix: post-revision PASS 准入硬协议
ALLOWED_RESOLVED_STATUSES = frozenset({"patched", "merged_into_higher", "migration_verified"})
FORMAL_FUNCTION_EXEMPTED_MAX_PER_SCENE = 3
MEDIUM_TRIAGE_REASON_MIN = 10
MEDIUM_TRIAGE_REASON_MAX = 30


def _collect_carrier_function_links(scene_card: dict | None) -> set[str]:
    """Rn+2 R1 F4 fix: physical_carrier 真实字段 = {text, function_link}（无 id）。
    367 实证 physical_carrier 嵌在 scene_tasks 内层；兼容顶层 + 嵌套两种位置。
    """
    result: set[str] = set()
    if not scene_card:
        return result
    for pc in scene_card.get("physical_carrier") or []:
        if isinstance(pc, dict) and pc.get("function_link"):
            result.add(pc["function_link"])
    for task in scene_card.get("scene_tasks") or []:
        if not isinstance(task, dict):
            continue
        for pc in task.get("physical_carrier") or []:
            if isinstance(pc, dict) and pc.get("function_link"):
                result.add(pc["function_link"])
    return result


def validate_post_revision_pass(
    review: dict,
    ledger: dict,
    lint_v2: dict,
    scene_card: dict | None = None,
) -> PassValidationResult:
    """Rn+2 post-revision verdict=PASS 准入检查。

    high cluster hit_ids 准入：ledger.post_revision_updates[hid].status 必须:
    - ∈ ALLOWED_RESOLVED_STATUSES; OR
    - == "formal_function_exempted" + carrier_function_link ∈ scene_card.physical_carrier[*].function_link;
      且 scene 总 formal_function_exempted 数 ≤ FORMAL_FUNCTION_EXEMPTED_MAX_PER_SCENE

    medium cluster hit_ids 准入（R1 F7 fix）：ledger.v1_triage[hid] 必须有 status + reason
    (10-30 字)；status 允许 observed，不强制 patch。

    禁用 status：observed_not_patched（Rn+2 起弃用）。
    """
    if review.get("verdict") != "PASS" or review.get("review_stage") != "post_revision":
        return PassValidationResult(valid=True)

    high_hit_ids: set[str] = set()
    medium_hit_ids: set[str] = set()
    for alert in (lint_v2 or {}).get("cluster_alerts", []) or []:
        sev = alert.get("severity")
        for hid in alert.get("hit_ids", []) or []:
            if sev == "high":
                high_hit_ids.add(hid)
            elif sev == "medium":
                medium_hit_ids.add(hid)

    if not high_hit_ids and not medium_hit_ids:
        return PassValidationResult(valid=True)

    updates = (ledger or {}).get("post_revision_updates") or {}
    if isinstance(updates, list):
        updates = {e.get("lint_id"): e for e in updates if isinstance(e, dict) and e.get("lint_id")}

    triage = (ledger or {}).get("v1_triage") or []
    if isinstance(triage, dict):
        triage_by_id = triage
    else:
        triage_by_id = {e.get("lint_id"): e for e in triage if isinstance(e, dict) and e.get("lint_id")}

    valid_function_links = _collect_carrier_function_links(scene_card)
    exempted_count = 0

    # high cluster 准入
    for hid in high_hit_ids:
        entry = updates.get(hid)
        if not entry:
            return PassValidationResult(
                False,
                f"high cluster hit {hid} 在 ledger.post_revision_updates 中无记录",
            )
        status = entry.get("status")
        if status in ALLOWED_RESOLVED_STATUSES:
            continue
        if status == "formal_function_exempted":
            fl = entry.get("carrier_function_link")
            if not fl or fl not in valid_function_links:
                return PassValidationResult(
                    False,
                    f"hit {hid} status=formal_function_exempted 缺有效 carrier_function_link "
                    f"（'{fl}' 不在 scene_card.physical_carrier[*].function_link 中）",
                )
            exempted_count += 1
            if exempted_count > FORMAL_FUNCTION_EXEMPTED_MAX_PER_SCENE:
                return PassValidationResult(
                    False,
                    f"scene formal_function_exempted 数={exempted_count} "
                    f"超上限 {FORMAL_FUNCTION_EXEMPTED_MAX_PER_SCENE}",
                )
            continue
        return PassValidationResult(
            False,
            f"hit {hid} status='{status}' 不在允许集合"
            f"（{sorted(ALLOWED_RESOLVED_STATUSES)} ∪ formal_function_exempted+carrier）",
        )

    # medium cluster triage 检查（R1 F7 fix）
    for hid in medium_hit_ids:
        entry = triage_by_id.get(hid)
        if not entry:
            return PassValidationResult(
                False,
                f"medium cluster hit {hid} 在 ledger.v1_triage 中无 triage 项",
            )
        if not entry.get("status"):
            return PassValidationResult(False, f"medium cluster hit {hid} triage 缺 status")
        reason = entry.get("reason", "")
        if not (MEDIUM_TRIAGE_REASON_MIN <= len(reason) <= MEDIUM_TRIAGE_REASON_MAX):
            return PassValidationResult(
                False,
                f"medium cluster hit {hid} triage.reason 长度={len(reason)} "
                f"不在 {MEDIUM_TRIAGE_REASON_MIN}-{MEDIUM_TRIAGE_REASON_MAX} 字范围",
            )

    return PassValidationResult(valid=True)


def validate_scene_review(review: dict) -> dict:
    for index, reader_yield in enumerate(review.get("reader_yield_check", [])):
        yields = reader_yield.get("yields", {})
        evidences = reader_yield.get("yield_evidences", [])
        evidence_types = {
            evidence.get("yield_type")
            for evidence in evidences
            if isinstance(evidence, dict)
        }

        for yield_type in YIELD_TYPES:
            if yields.get(yield_type) is True and yield_type not in evidence_types:
                return {
                    "valid": False,
                    "error": (
                        f"reader_yield_check[{index}].yields.{yield_type}=true "
                        "但 yield_evidences 无对应项"
                    ),
                }

        for evidence_index, evidence in enumerate(evidences):
            reason = evidence.get("reason", "") if isinstance(evidence, dict) else ""
            if not (10 <= len(reason) <= 30):
                return {
                    "valid": False,
                    "error": (
                        f"reader_yield_check[{index}].yield_evidences"
                        f"[{evidence_index}].reason 长度需 >=10 <=30 字"
                    ),
                }

        if all(not yields.get(yield_type, False) for yield_type in YIELD_TYPES):
            if reader_yield.get("verdict") != "zero_yield":
                return {
                    "valid": False,
                    "error": (
                        f"reader_yield_check[{index}] yields 全 false，"
                        "verdict 必须 auto-zero_yield"
                    ),
                }

    return {"valid": True}
