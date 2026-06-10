---
name: character-rehearsal
description: MUSE 角色排练模块 — 通过"成为角色"的对话模拟，为 Phase 6 写作前情境排练和审稿阶段角色校验提供场景级素材。
---

# 角色排练模块

## 核心原则

> 「人物性格真相在人处于压力之下做出选择时得到揭示。」
> —— 《故事》第五章

排练 ≠ 设计。排练只服务已经存在的角色资产和具体场景：让角色在情境中自然反应，给 writer 或 reviewer 提供可取舍的素材。

## 与 character-actor agent 的关系

排练使用预定义 agent `character-actor`（通过 Agent tool 按名称 dispatch，不要自建临时 agent）。情境排练和角色校验共用同一个 agent，区别在于 orchestrator 给的指令不同。

Agent 的三层上下文在排练中的体现：

| 层 | Phase 6 情境排练 | 审稿：角色校验 |
|----|-----------------|-----------------|
| 核心层 | character-actor.md | character-actor.md |
| 人设层 | skill `{slug}` + state.md + role_brief（见 situational-method §1）；adapter 仅 fallback | `pipeline/characters/{角色名}.md`（adapter-only，见 validation-method §顶部 scope note） |
| 经历层 | 当前场景情境（orchestrator 指令） | 成品文本（审稿 subagent 指令） |

## 两类运行时排练

| 阶段 | 时机 | 方法引用 | 输出 |
|------|------|---------|------|
| 情境排练 | Phase 6 writer 调用前 | `references/situational-method.md` | `staging/scene_{scene_id}/{slug}_rehearsal.md`（四项固定：想说但不会直说 / 台词候选 2-4 条 / 禁用语气 / 动作或停顿）|
| 角色校验 | 审稿阶段（Phase 6 → 7 过渡） | `references/validation-method.md` | `staging/scene_{scene_id}/{slug}_validation.md` |

→ 排练输出格式见 `references/output-schema.md`

## 适用条件

排练是可选步骤，在以下情况特别推荐：
- 角色的职业/身份标签容易导致修辞过载（程序员、医生、军人等）
- 多角色故事需要声音差异化验证
- 情感密度高的场景（危机、高潮、转折）
- 审稿阶段需要用角色视角验证对白真实性
