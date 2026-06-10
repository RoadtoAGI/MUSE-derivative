# Scene Review Output Schema

本文件记录 scene-reviewer 输出 schema 的机器热路径字段。R 轮 `post_revision_updates` 仍保持 append-only list，不在其下挂 semantic migration 状态。

## cluster_alerts 字段

aggregation 层输出，不归 FAMILY_REGISTRY。详 design doc §4.2 schema 草案。

```yaml
cluster_alerts:
  - alert_id: <str>
    scope: scene | paragraph | span
    family: <family_id>
    cluster: <cluster_name>
    group: semantic_heuristic | hard
    rule_counts: {<rule_name>: <count>}
    total_count: <int>
    density_per_1k: <float>
    hit_ids: [<lint_hit_id>, ...]
    distribution:
      mode: single_span | single_sentence | distributed | catastrophic | paragraph_pattern
      paragraph_count: <int>
      contiguous: <bool>
    severity: low | medium | high
    governance:
      individual_exemption_allowed: <bool>
      required_triage: cluster_finding
      required_patch_mode: rewrite_patch_set
      required_patch_kind_options: [rewrite_sentence, rewrite_span]
      forbidden_patch_kind: [delete_token, replace_phrase]
```

## reader_yield_check[] 字段

scene-reviewer 输出必填数组，每条对应一个候选短句。详 design doc §7.3.2。

```yaml
reader_yield_check:
  - text: <str>
    candidate_type: <enum>                       # <=10_micro_clause / state_confirm / counted_speech / ordinal_marker / cluster_alert_low_info / ledger_observed_in_high_cluster
    yields:
      plot_change: <bool>
      danger_change: <bool>
      tactical_change: <bool>
      character_choice: <bool>
      relationship_shift: <bool>
      world_rule: <bool>
      sensory_irreplaceable: <bool>
      formal_function: <bool>
    yield_evidences:
      - yield_type: <enum>
        reason: <str>                            # >=10 字 <=30 字 可验证理由
    verdict: zero_yield | low_yield_label | low_yield_mergeable | harmful_pattern | effective
    recommended_action: keep | merge | convert_to_consequence | delete | rewrite
    reason: <str>                                # verdict 总理由 <=30 字
```

### 举证倒置硬约束

- 所有 yields 默认 false
- 升 true 必须 yield_evidences 中显式列出该 yield_type + >=10 字 <=30 字 可验证理由
- **`yields.* == true` 且无对应 yield_evidences 项 -> schema error 硬阻断**（validator 不静默改 false）
- 字段缺省或显式 false -> 当 false 处理
- 全部 yields false -> verdict 自动判 zero_yield

## scene_level_issues.low_information_cadence 字段

aggregation 层信号，与 cluster_alert 同层。详 design doc §7.4。

```yaml
scene_level_issues:
  - issue_type: low_information_cadence
    severity: major
    trigger:
      scene_zero_yield_micro_clause_gte: <int>
      same_function_micro_clause_gte: <int>
      zero_yield_density_per_1k_chars: <float>
      cluster_alert_high: <bool>
    distribution:
      mode: single_span | single_sentence | distributed | catastrophic | paragraph_pattern   # 沿用 F1.C enum
      paragraph_count: <int>
      contiguous: <bool>
```

## pattern_migration_gate.semantic_function_migration 字段

```yaml
pattern_migration_gate:
  evaluated: true
  gate_pass: <bool>
  cross_cluster_migration: <bool>
  same_cluster_migration: <bool>
  semantic_function_migration:
    detected: <bool>
    migrations:
      - old_function: contrastive_explanation
        forbidden_new_patterns: [actually_assertion, true_actual_template, ...]
        detected_in_v2:
          - anchor_line: <int>
            matched_text: <str>
            matched_pattern: <pattern_name>
            verdict: failed
```

## ledger 字段扩展

```yaml
lint_resolution_ledger:
  v1_triage: [...]
  post_revision_updates:
    - review_round: post_revision_round1
      source_lint_run_id: ai_filler.v2
      updates: [...]
  semantic_migration_state:
    attempt_count: <int>
    last_failed_patch_ids: [<patch_id>, ...]
```
