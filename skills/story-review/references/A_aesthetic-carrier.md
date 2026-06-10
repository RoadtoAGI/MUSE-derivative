# A 组审查：豁免前置 + 承载完整性

> 本子文件承载 A 组审查的**协议层规则**：豁免前置判断（与 prose-craft cliche 表 + scene-review 协议同源）+ 承载完整性核验（与 `craft_carrier` 字段联动）。主表逐项检查见 [`A_aesthetic.md`](A_aesthetic.md)。

## §0 豁免前置

> 与 prose-craft/references/ai-cliche-patterns.md §"名著式合法手法豁免" 配套。

A 组扫到 AI 病灶 / 审美问题位置时，先核 4 类豁免（与 [`scene-review/SKILL.md`](../../scene-review/SKILL.md) "豁免后处理" 同源）：

1. `scene_card.pov_constraint.intentional_blind_spot` — 信息缺失类病灶（如 omniscient_overexposure 反向触发 / 反应过淡 / 信息不足）
2. `scene_card.omission_plan` — 解释缺席类病灶（如 psychological_overfill 反向 / 顿悟无内容 / 临终极简）
3. `scene_card.narrator_distance`（`archival_zero` / `unreliable_first` 等）— 文体冷感 / 不可靠叙述类病灶。**两个例外不适用本条单字段豁免**：① `subtext_translated_by_narrator`（旁白翻译潜台词）必须走完整豁免表的**误读型**判据——解码与后文证据矛盾（解码错误本身是性格）才豁免，`unreliable_first` 字段命中不自动豁免；② 同一句式模板全篇高频命中时不得按叙述者声线**整批**豁免——保留少数承担真实功能的代表用例，其余按对应 family 的 repair_strategy 修
4. 长独白满足 reframing 三项以上（见 [`A_aesthetic-micro_language.md`](A_aesthetic-micro_language.md) §reframing 独白判读）— 配角长独白被报"AI 注水"

**任一豁免命中 = 不写 finding。**

豁免要求 scene_card 字段**显式声明**；scene_card 漏标却出现合法名著手法时仍报，由 scene-reviewer 决定补字段（ROLLBACK 回 Phase 5）还是 PATCH 修正。完整 12 项豁免表（4 类）+ 执行硬约定见 [`prose-craft/references/ai-cliche-patterns.md`](../../prose-craft/references/ai-cliche-patterns.md) §"名著式合法手法豁免"。

## §11 承载完整性检查

> 与 `craft_carrier` 字段联动。

读 `pipeline/scene_{id}/scene_card.md` 中的 `craft_carrier.type` 与 `craft_carrier.concrete_anchor`。逐场景核：

| 检测项 | 判据 | 报告落点（`dimension: ai_pattern` + subkind） |
|---|---|---|
| **carrier 缺席** | scene_card 声明 carrier，正文中找不到 anchor 对应的物件 / 动作 / 文体 / POV 限制 | `subkind: carrier_missing` |
| **carrier 已完成意义后被解释** | carrier 出现并完成意义后，正文又用心理 / 主题语言重复同一意义 | `subkind: carrier_then_explain`（与 `psychological_overfill` 联动，但 `psychological_overfill` 是任何场景的通病，`carrier_then_explain` 是"已设计 carrier 仍解释"的强失守） |
| **carrier 反向解释** | scene_card 声明 `omission_plan`（故意不解释什么），正文偏要解释 | `subkind: omission_violated` |

craft_carrier 字段缺位时跳过本节，不强制。
