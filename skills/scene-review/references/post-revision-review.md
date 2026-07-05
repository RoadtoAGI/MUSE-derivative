# post-revision review 协议（三层 gate + PASS 准入）

> 适用：dispatch prompt 含 "post-revision" / "post-rewrite" 的评审模式。首次评审模式不读本文件。

## Post-revision review schema（三层 gate）

post-revision 模式必须输出以下结构；三层 gate 都要写 `evaluated: true`，即使 Gate 1 已失败也不短路 Gate 2/3。机器失败但 reviewer 合法放行时只通过 `ai_pattern_gate.override.applied` 表达。

```yaml
review_round: post_revision_round1
verdict: PASS | PATCH | ROLLBACK | REWRITE

ai_pattern_gate:
  machine_gate: pass | fail
  reviewer_gate: pass | fail | override
  override:
    applied: false
    override_reason: null

targeted_span_gate:
  evaluated: true
  gate_pass: true
  per_patch:
    - patch_id: patch_01
      patch_kind: rewrite_sentence | rewrite_span | delete_token | replace_phrase
      local_lint_v1_family_set: []
      local_lint_v2_family_set: []
      same_family_remaining: false
      new_family_introduced: false
      semantic_function_preserved: true
      contract_conflict_observed: false

scene_residual_gate:
  evaluated: true
  gate_pass: true
  unresolved_high_spans: 0
  unresolved_medium_spans: 0
  unresolved_low_spans: 0
  needs_patch_hits: 0

pattern_migration_gate:
  evaluated: true
  gate_pass: true
  old_family_set: []
  new_family_set: []
  old_subtype_set: []
  new_subtype_set: []
  cross_cluster_migration: false
  same_cluster_migration: false
```

**post-revision review 不进入降级 yaml 路径**：post-revision 模式下，required input gate 仍由 orchestrator 在 dispatch 前跑 verify_scene_review_inputs.py（review/ 此时已有最新 A/B/C/lint）；input gate 失败 → orchestrator 写降级 yaml 到 `scene_{id}.yaml`（首次锚点位置），post-revision dispatch 不发生。

## Post-revision 三层 gate 判定语义

post-revision 模式必须三层全 evaluated：Gate 1 fail 不短路 Gate 2/3；第二轮 PATCH 需要同时知道 targeted span、全场残留、pattern migration 三类根因。

Gate 1 targeted span 是主判据；Gate 2/3 只作 residual / migration 诊断。

**Gate 1 targeted_span_gate** 是主判据。每个 patch 必须同时满足：
- `same_family_remaining=false`
- `new_family_introduced=false`
- `semantic_function_preserved=true`

任一 patch 不满足，Gate 1 fail；targeted span 失败不计作 Gate 2 的 unresolved span。

**Gate 2 scene_residual_gate** 判全场 residual：`unresolved_high_spans=0`、`unresolved_medium_spans=0`、`unresolved_low_spans=0`、`needs_patch_hits=0` 才 pass。剩余 ai_filler hit 的状态权威 = pipeline/review/{scene_id}.machine_ledger.yaml（脚本写入）；本 review 不裁决 ai_filler 残余，只核对定点 patch 自身的语义保持。

**Gate 3 pattern_migration_gate** 比较 family / subtype set：
- `old_cluster != new_cluster` → `cross_cluster_migration=true`
- `old_cluster == new_cluster` 且 family set 无交集、new family 仍属高风险 cluster → `same_cluster_migration=true`
- family 相同但 subtype 迁到更高风险模板 → 记 migration candidate，由 reviewer 判读

**混合判定**：
- `machine_gate = targeted_span_gate.gate_pass AND scene_residual_gate.gate_pass AND pattern_migration_gate.gate_pass`
- `reviewer_gate=fail` 时，即使 machine_gate pass 也升 PATCH
- machine_gate fail 时，只有 `reviewer_gate=override` 且 `override.applied=true` 并给出明确 reason，才能 PASS
- machine_gate fail 且无合法 override → PATCH；连续二轮仍 fail 时升 ROLLBACK

## superficial_patch_failed 检测

在 Gate 1 + Gate 3 内嵌检测：

- `patch_kind=delete_token`，但 new_span local lint 仍命中 same family heuristic → `superficial_patch_failed=true`
- `patch_kind=rewrite_sentence` / `rewrite_span`，但 new_span local lint 仍命中 same family 主模式 → `superficial_patch_failed=true`

命中即强制 `verdict=PATCH` 二轮，并升级 patch_kind：

- `delete_token` → `rewrite_sentence`
- `rewrite_sentence` → `rewrite_span`
- `rewrite_span` → `ROLLBACK`

## Gate 3 pattern_migration 判定纪律

machine 检出 migration 是**候选**，不是判罪——scene-reviewer 逐条确认：

- reviewer 判定为合理修订（同主题 cluster 内收缩、写实化、或 scene function 明确需要）→ 写 override，`gate_pass=true`
- 否则确认 hard fail，`verdict=PATCH` 二轮

不要把 migration 一律当作机器硬失败——机器检出的误报由 reviewer 确认环节吸收。

## post-revision PASS 准入硬协议

post-revision review verdict=PASS 准入条件——任一不满足 → verdict 强制改 PATCH 进二轮：

- **v2 出现 high cluster_alert 不由本 review 判读**——它属于机器通道（指令由脚本按残余重新生成并派发分布修复）；本 review 对其不给 PASS 也不给豁免，在 rationale 记录残余即可。
- **禁用 status**：`observed_not_patched` **弃用**——reviewer 不能用"功能性 / 节奏 / 留白"等理由放走 high cluster 残留；medium cluster 可用 observed 但 high 不可
- **formal_function_exempted 例外**：每条必须 `carrier_function_link: <scene_card.physical_carrier[*].function_link>` 绑定具体 carrier 的 function_link（真实 schema 字段，非 id）；scene 总 formal_function_exempted 数 **≤3**（兼顾 recognition_object / 名字仪式 / 节拍韵律 3 类高 impact functional 节拍）
- **medium cluster**：不强制记录——机器台账已记 observed；仅当它与某个定点 patch 的语义保持判定直接相关时在 rationale 提及。

准入失败 → `scene_review_schema_validator.py` 输出 hard fail，verdict 强制改 PATCH。
