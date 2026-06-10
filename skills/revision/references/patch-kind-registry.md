# patch-kind registry (single source of truth)

> 本文件是 patch_kind enum 的**单一来源**。scene-review 与 revision 都引本文件，不各自维护。新增 / 改名 / 调整 action 一律改本文件。

## PATCH 类（定点减法，reviser 执行）

```yaml
patch_kinds:
  carrier_then_explain:
    action: patch
    direction: "删除 carrier 完成意义后的'这意味着…'解释段；保留 carrier 独立完成意义"
  omission_violated:
    action: patch
    direction: "删除违反 omission_plan 的解释段；让空白回归空白"
  narrator_self_corrects:
    action: patch
    direction: "删除叙述者'但我隐约觉得不对'式自我谴责；保留叙述者不可靠"
  emotion_naming_under_face_loss:
    action: patch
    direction: "删除'她哭了'/'他感到悲伤'等情感命名词；改为第三方感官通道（触觉 / 嗅觉 / 视觉）"
  care_tone_violence_dropped:
    action: patch
    direction: "删除施害方'阴冷'/'冷笑'/'残忍'等语气标签；保留关怀台词；只在动作 / 物件层显化暴力"
  omission_filled_in:
    action: patch
    direction: "writer 把名著式留白填实了。reviser 删除补全的解释，恢复留白"
  rewrite_sentence:
    action: patch
    mode: semantic_rewriter
    direction: "单句重写：句内重写句法结构 / 合并连续动作 / 删低收益短语 / 把解释转为可见动作；保持 plot fact 不变"
  rewrite_span:
    action: patch
    mode: semantic_rewriter
    direction: "多句到一段重写：anchor 段内重组承载方式；patches 未列段落不动；超出 anchor 边界必须升 ROLLBACK"
```

### `rewrite_sentence`

**含义**：单句重写。

**适用**：同句多 family 信号 / 同句多 cluster 共现。

**修订方向**：anchor 句内重写句法结构 / 合并连续动作 / 删低收益短语 / 把解释转为可见动作；保持 plot fact 不变；低强度 carrier 压缩 / 合并默认允许（不与 preserve 冲突时）；plot-adjacent carrier 替换必须由 `rewrite_directive.allowed_carrier_changes` 显式授权。

**reviser mode**：semantic_rewriter mode。

### `rewrite_span`

**含义**：多句到一段重写。

**适用**：跨句聚合 / dominant_cluster 属于语义层病灶且证据门槛满足。

**修订方向**：anchor 段内（≤ max_sentences）重组承载方式；遵守 plot fact 红线；patches 未列段落不动；超出 anchor 边界必须升 ROLLBACK。

**reviser mode**：semantic_rewriter mode。

**Schema 要求**：必填 `anchor_quote_start` + `anchor_quote_end` + `old_span` + `location.line_range`。

## ROLLBACK 类（不进 PATCH — 改事件因果 / 镜像结构 / 全场基调；scene-reviewer 见此类直接定 ROLLBACK，不写 patch_directive）

```yaml
requires_rollback_reason:
  epic_death_facing:
    direction: "正面对决 / 临终顿悟 → 改为'背后击杀 + 单字临终'。此类改事件事实，超出 reviser PATCH 权限"
  mirror_loosened:
    direction: "镜像场景缺点对点对应。reviser 无法定点重建镜像结构"
  carrier_missing:
    direction: "scene_card 声明 carrier，正文找不到 anchor。属于'设计与正文偏离'"
  narrator_distance_global_drift:
    direction: "narrator_distance 跨场景漂移。属于场景整体节奏问题，非局部修订"
```

## 维护纪律

- 新增 patch_kind 必填 `action`（patch | rollback）
- enum 名一律 ASCII snake_case（不允许中文如 `omission_补全`）
- 改动后 scene-review/SKILL.md + revision/SKILL.md 不需要同步——它们引本文件
