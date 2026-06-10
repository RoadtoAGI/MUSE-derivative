---
name: phase6-scene-development
description: MUSE Phase 6 — 场景展开。pipeline 中唯一产出正文的阶段：orchestrator 逐场景派生 role_brief 并调度 writer subagent 把 phase5 的 scene_card 展开为正文。由 orchestrator 跑到 Phase 6 时经 Skill 工具路由进入。不直接承接用户自然语言写作请求——那由 story-writing / novel-outline 等入口 skill 路由。
---

# Phase 6: 场景展开

## ⚠️ orchestrator 严禁直接产正文（硬约束）

**进入 Phase 6 后，orchestrator 永远不允许自己用 Write / Edit 工具产 `pipeline/scenes/scene_*.md`。** 所有场景正文产出必须通过 `Task(subagent_type="writer", ...)` dispatch writer subagent；所有 PATCH 档修订必须通过 dispatch reviser subagent。

| ❌ 错误 | ✅ 正确 |
|---|---|
| orchestrator 直接 `Write(pipeline/scenes/scene_S01.md, "...")` 写场景 | `Task(subagent_type="writer", prompt="为场景 S01 派 writer")`，writer 自产 |
| orchestrator 看到 "Phase 6 / 写场景" 任务，直接加载 `prose-craft` + `dialogue-craft` 自己写 | dispatch writer subagent；writer 自己按需加载 writing skills |
| orchestrator 用 Edit 直接改 `pipeline/scenes/scene_*.md`（除 §1.5 PATCH 档外） | dispatch reviser subagent 走 patch_directive 链路 |
| "MUSE 主对话直接执行 = 自己写正文" | "MUSE 主对话作 orchestrator 调度 subagent" — orchestrator 永不自己产 prose |

**例外（仅一个）**：用户**显式**说"不要 dispatch / 单场景小任务 / 我自己看看怎么写"时，orchestrator 跳过 dispatcher 直接写。其他场景（含全 pipeline / 用户没明示偏好 / Phase 6 标记任务），**默认走 dispatch**。

理由：per-role subagent 隔离是声音独立性与质量控制的前提；orchestrator 上下文混杂 design / audit / 多场景信息，自己写会让 prose 沾染这些噪声，密度下降、AI 味升高。

## 弹性入口

本 skill 同时服务完整 pipeline（0→7）和单场景任务（重写一场戏、修改对白等）。完整 pipeline 按 `references/execution-protocol.md` 的 scene-level dispatcher 执行；单场景/小任务在用户明示"自己写"时按下方核心原则走，无需跑 dispatcher。

## 核心原则

> 「节拍是人物行为中动作/反应的一种交流。」

> 「任何文本都有其潜文本。」
> —— 《故事》第十一章

节拍是叙事的最小单位——一个行动和一个反应的交换。场景由节拍链构成，节拍链驱动价值从开始状态转变到结束状态。对白不是交谈，而是行动——每句话背后都有一个意图，字面意思下藏着潜台词。

## 输入契约

从 Phase 2 接收（核心依赖）：
- `pipeline/story-character-skills/.claude/skills/{slug}/SKILL.md` — 角色长期人格权威源（身份/欲望/声音/边界）
- `phase2_character.yaml` — 结构化角色系统（desire / hidden_fear / voice_traits / relations）

从 Phase 5 接收（核心依赖）：
- `phase5_scenes.yaml` 的 `sequence_expansions[].scenes[]` — 每 scene_card 含 `scene_id / pov / participants / location_time / conflict / value_start / value_end / scene_tasks / handoff / beat_direction`

从 Phase 0 / 1 / 3 / 4 接收（参考依赖）：
- `target_length` / `genre` / `style_directives` / `reference_materials` / `setting` / `generative_driver` / `world_rules` / `domain_knowledge` / `spine_statement` / `crisis` / `climax`
- `generative_driver` 是世界事实的根：写作时引用的具体威胁 / 资源 / 道具细节须能追溯到 driver；driver 没覆盖的世界事实如需临场发明，必须与 driver 派生的 `world_rules` 不矛盾

从 runtime artifact 接收（可选 fallback）：
- `pipeline/story-character-skills/.claude/skills/{slug}/state.md` — 角色 runtime 主观状态
- `pipeline/scene_{scene_id - 1}/draft_tail.md` — 上一场景 draft 尾段（writer 完成后由 `extract_draft_tail.py` 产；首场景取空）

## Dispatcher：scene-level dispatch

进入每场景第一步**必做**：

> **orchestrator 通过当前运行时的 subagent dispatch 启动 `role-brief-deriver`**（仅传 `scene_id` 动态标识），派生 `pipeline/scene_{scene_id}/role_briefs.md`（合集版）。失败则 `mark_scene_pending_human(scene_id)` 跳过本场景。

**装有 MUSE-canon-distill 扩展包时**：role_briefs 派生成功后、dispatch writer 之前，按 key_scene 信号 / 用户全开偏好按需 `Skill scene-reference` 产 `pipeline/references/{scene_id}_ref.md`（writer 自动消费）；扩展包未装 / 不命中判据 → 整步跳过，不阻断主干。**触发时点、判据、降级语义、per-scene 流程图见 `references/execution-protocol.md` §3.5**。

权威流程与伪代码见 `references/execution-protocol.md` §1 dispatcher。

### 反先验场景 fast-path（`counter_prior_scene.used=true` 时）

scene_card 含 `counter_prior_scene` 结构化对象（schema 见 phase5 `output-schema.md`）且 `used=true` 时，orchestrator 在 dispatch writer 前**读子字段**，在 writer dispatch prompt 中**附加一段额外约束**：

> "本场景标记 counter_prior_scene。
>  - 类型：{kind}
>  - 嵌入的日常动作：{mundane_action}
>  - 高情感语境：{emotional_context}
>  - 禁止：{forbidden_moves 逐条列出}
>  保留嵌入的日常行为；不允许把日常行为升华成象征；不允许在日常行为后追加心理解释。"

writer **不 fork 新分支**——dispatch prompt 多一段结构化约束即可。参考实例：《挪威的森林》scene 10（医院 + 黄瓜 + 欧里庇得斯）。

`used=false` 或字段缺失 → 不注入，writer 走通用 Craft Preflight。完整伪代码见 `references/execution-protocol.md` §1。

### 写作层 AI pattern 预防 fast-path（`prose_risk_contract.used=true` 时）

scene_card 含 `prose_risk_contract.used=true` 时，`extract_scene_card.py` 已渲染 `## 写作层 AI pattern 预防 (prose_risk_contract)` 段到 scene_card.md——writer 通过 Read scene_card.md 即获得 contract 全文。orchestrator 在 writer dispatch prompt 仅附一句激活提醒：

> "本场 scene_card 含 `## 写作层 AI pattern 预防 (prose_risk_contract)` 段，writer 必须在 Craft Preflight 阶段按该段执行。"

不重复展开内容（避免 prompt 膨胀）。`used=false` 或字段缺失 → 不渲染、不附提醒。schema 见 phase5 `output-schema.md`。

## orchestrator 不产 prose

**orchestrator 不在 Phase 6 里改写或整合正文**——正文产出交 writer subagent。

orchestrator 在 Phase 6 **只做**：派 subagent、触发脚本、按 scene-review 四档路由。

## 执行步骤

**完整 pipeline** → 读取 `references/execution-protocol.md`，按 scene-level dispatcher 走。orchestrator 只调度——派 role-brief-deriver / writer / reviser subagent，触发机械脚本（`extract_scene_card.py` / `extract_draft_tail.py` 等），不产 prose。

**单场景/小任务** → 跳过 dispatcher，orchestrator 自己加载 `prose-craft` + `dialogue-craft` skill 获取写作工坊后直接写。写作核心原则（节拍驱动 / 潜文本 / 省略决策 / 段落节奏 / 创意执行 / 写后自检）统一由 `prose-craft` skill 承载；对白深度由 `dialogue-craft` skill 承载——本 SKILL 不再重复。

## 输出

→ YAML schema 见 `references/output-schema.md`

- 正文：`pipeline/scenes/scene_{id}.md`（每个场景一个文件）（接口约束）
- 每场景 runtime 产出（dispatcher 工作目录）：
  - `pipeline/scene_{scene_id}/role_briefs.md`（合集版，writer 消费）
  - `pipeline/scenes/scene_{scene_id}.md`（writer 产出，单路径协议）
- 索引：`pipeline/phase6_development.yaml`

**索引生成**：由 `auto-phase6-index` hook 在 `phase5_scenes.yaml` 写入后自动产 `pipeline/phase6_development.yaml` 骨架（含 phase5-only skeleton 模式，无 scene 文件时也产）；scenes/scene_*.md 落地后再次写入 phase5 / 手动重跑会刷新 `approximate_words` 与 `total_word_count`。orchestrator 按需补充 `summary`。

## 相关 skill

- **写作工坊**（writer 加载 / orchestrator 单场景任务加载）：
  - 加载 `prose-craft` skill（散文原则 / 节拍 / 潜文本 / 段落节奏 / 创意执行 / 写后自检 / 终审验证）
  - 加载 `dialogue-craft` skill（对白矩阵 / 声音差异 / POV 锚点）
- **本 SKILL references/**：
  - `execution-protocol.md`（dispatcher 伪代码 + role_brief 派生协议）
  - `output-schema.md`（phase6_development.yaml 索引结构）

（原 "写作核心 L1 / 写作指导 L2 / 写后自检 L3 / 终审验证 L4" 段落 Step 4 Task 5 迁到 `prose-craft` skill——写作细节由 writer / orchestrator 加载 prose-craft 获得，本 SKILL 专责 orchestrator 调度 + Phase 6 职责声明。）
