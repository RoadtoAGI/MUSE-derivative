---
name: character-rehearsal
description: MUSE 角色表演素材模块 — 以角色身份为 Phase 6 多角色场产出结构化 performance 素材(台词/行为/交互/外显心理/禁区),并为审稿阶段提供角色校验。
---

# 角色表演素材模块

## 核心原则

> 「人物性格真相在人处于压力之下做出选择时得到揭示。」
> —— 《故事》第五章

素材 ≠ 设计,素材 ≠ 剧本。本模块只服务已经存在的角色资产和具体场景:让角色在情境压力下预演,产出**候选素材**供 writer 取舍——writer 保持作者身份,可选用、可改写、可丢弃;唯一硬约束是 `forbidden`(禁用语气 / 绝不说的话)。

## 与 character-actor agent 的关系

使用预定义 agent `character-actor`(通过 Agent tool 按名称 dispatch,不要自建临时 agent)。performance 素材与角色校验共用同一个 agent,区别在于 orchestrator 给的指令不同。

Agent 的三层上下文:

| 层 | Phase 6 performance 素材 | 审稿:角色校验 |
|----|-----------------|-----------------|
| 核心层 | character-actor.md | character-actor.md |
| 人设层 | skill `{slug}` + state.md + role_briefs 合集 + scene_card(静态自读,见 situational-method §3);adapter 仅 fallback | `pipeline/characters/{角色名}.md`(adapter-only,见 validation-method §顶部 scope note) |
| 经历层 | dispatch 二元组 `{scene_id, role_slug}`(情境由 actor 自读 scene_card,orchestrator 不转述) | 成品文本(审稿 subagent 指令) |

## 两类运行时任务

| 阶段 | 时机 | 方法引用 | 输出 |
|------|------|---------|------|
| performance 素材 | Phase 6 writer 调用前 | `references/situational-method.md`(含落盘前 self-check) | `staging/scene_{scene_id}/{slug}_performance.md` |
| 角色校验 | 审稿阶段(Phase 6 → 7 过渡) | `references/validation-method.md` | `staging/scene_{scene_id}/{slug}_validation.md` |

→ 产物 schema 权威源:`references/output-schema.md`

## 适用条件

多角色场(在场角色 ≥ 2)默认必跑,per-role 并行 fan-out 全部在场角色;触发判据与豁免契约(`audit/skip_performance.yaml` 逐场声明)由 phase6 执行协议承载。角色校验按审稿需要触发。
