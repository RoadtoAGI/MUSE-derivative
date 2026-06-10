# 情境排练方法

## 用途

Phase 6 步骤 0 的排练协议。在写作前为 POV 角色做声音校准，产出场景级锚点。覆盖对白场景和叙述/内心戏场景。

---

## 时机

Phase 6 写作每个场景前按 `../SKILL.md §适用条件` 判断是否触发（排练是可选步骤，非每场必做）。Phase 2 已完成，前置产物可用：
- `pipeline/story-character-skills/.claude/skills/{slug}/SKILL.md` + `state.md`（character-persona 构建）
- `pipeline/scene_{scene_id}/role_briefs.md`（role-brief-deriver 生成的合集，全部在场角色各一段 YAML）
- `pipeline/characters/{角色名}.md`（adapter，兼容视图）

---

## 执行步骤

### 1. dispatch 预定义 agent `character-actor`

orchestrator 向 agent 传递路径、情境和落盘指令。prompt 模板：

```
你是角色 {角色名}（role_slug: {slug}）。

角色 runtime package 文件读取顺序（优先级从高到低，与 writer 侧对齐）：
1. Read pipeline/story-character-skills/.claude/skills/{slug}/SKILL.md——长期人格权威源（skill-shaped role package，**不是** registry 级 skill invocation——见下方 NB）
2. Read pipeline/story-character-skills/.claude/skills/{slug}/state.md——本场景进入前的主观状态
3. Read pipeline/scene_{scene_id}/role_briefs.md——本场景 role_brief 合集，定位 character: {slug} 的 YAML 段读取你的目标 / 压力 / 误读 / stake / boldness_guardrails
fallback（仅在 1/2 文件读取失败时）：Read pipeline/characters/{角色名}.md（adapter，长期声线的兼容视图）

NB：角色包是 run 级动态产物（每个 query 独立生成），项目级 skill registry（Codex `.codex/skills` / Claude Code `.claude/skills`）都不会自动发现 `pipeline/story-character-skills/` 下的动态包，因此**两个运行时统一走 file Read，不是 skill 机制加载**。

当前场景 {scene_id} 情境：{场景情境简述，1-2 句}

在此情境下以角色身份回应，并在回应末尾按以下四项固定结构产出——**产出必须承接本场景 role_brief 的目标/压力/误读，不得只泛化长期声线**：

## 想说但不会直说
...

## 台词候选（2-4 条）
- ...

## 禁用语气
...

## 动作或停顿
...

产出完整后 Write 到 pipeline/staging/scene_{scene_id}/{slug}_rehearsal.md。
```

### 2. 按场景类型设计排练 prompt

用麦基三层模型（已说 / 未说 / 不能说）指导 prompt 设计——排练问题越具体、越贴近实际场景，Actor 产出素材越有用；避免"你怎么看"式泛问。按场景类型选结构：

**对白场景**（多角色对话、争论、谈判）——产出已说 + 未说：
```
{对方角色}说了"{具体台词}"，转身要走。你怎么回应？
```
可继续追问：内心在想什么？如果这时有人走过来，你会说什么？做什么？

**叙述/内心戏场景**（战斗、独处、观察、逃亡）——产出感官过滤 + 思维模式 + 情感泄露：
```
你站在{场景地点}，{具体情境}。你注意到什么？你脑子里在想什么？有什么感觉你不愿意承认？
```
拆分维度：感官（先看到什么再听到什么）/ 思维（怎样组织信息）/ 泄露（身体反应）。

**压力场景**——产出压力下的认知变化 + 身体信号 + 思维退化：
```
{紧迫情境描述}。你必须在{时间限制}内做决定。你的身体有什么反应？你在想什么？
```

**压力表达排练**（排练角色"不能说出口时怎样行动"，产出动作 / 沉默 / 错位台词，不让最重的信息直译成内心独白）：

```
1. 当你被误解 / 逼问 / 羞辱时，你第一反应是解释、反问、沉默、转行动，还是攻击证据？
2. 你最想说但不能说的那句话，会变成哪个动作、物件处理、停顿或离开？
3. 如果只允许你说一句最普通的话，它要承担什么不可说的重量？
4. 你此刻故意不看、不承认、不追问什么？为什么？
```

self-check（与 §4.1 联动）：

```
若输出多次出现 "我感到 / 我其实 / 我害怕 / 我爱你 / 我恨你" 这类直译内心句，必须重跑，改为角色可执行的动作 / 沉默 / 错位台词。
```

理由 / 名著锚点：
- 《射雕英雄传》李萍的普通母亲句子后接自刎，最大重量不是台词而是行动（novels/射雕英雄传/craft_notes/scene_13_beats.md L3-L4，L8-L12）
- 《神雕侠侣》小龙女拒认杨过，真正信息从身体动作泄出（novels/神雕侠侣/craft_notes/scene_S11_beats.md L17-L20）
- 《三体Ⅰ》叶文洁审讯中的冷感来自程序化问答和省略心理（novels/三体Ⅰ-地球往事/craft_notes/scene_S22_beats.md L3-L4，L17-L29）

### 2bis. 反 AI 化情境模板（在压力 prompt 之外的二阶练习）

这组模板专门让 Actor 提前演练"AI 默认会反向写"的高压情境——AI 倾向把临终写得深刻、把死亡写得激烈、把目睹恶行写成谴责、把绝望写成提高声调、把退场写成牺牲。本节模板要求 Actor 在这些情境下做出反 AI 默认的反应。

```
1. 不合适物件嵌入临终：你在 ta 的病床边。你只有一根黄瓜 / 一本欧里庇得斯。说说你这一小时会做什么。**不允许说深刻的话**。
2. 延迟揭示型死亡：妈妈半年前在车祸中去世，你已经"知道"了但还没完全意识到。今天你坐公交回家，提前一站醒过来。**不允许直接回忆车祸场景**。
3. 不可靠叙述：你目睹了一件你应该反对的事，但你内心觉得"快感"。**不允许任何自我谴责或自我惊讶**。
4. 诊断式冷判定：你的伴侣刚提出一个让你绝望的事实。**不允许提高声调**。用一句平静的事实陈述回应。
5. 配角主体性退场：你即将退场。你想到的最后一件事不是你爱的人。**不允许把退场说成牺牲**。用一个你自己创造过的东西（一首诗 / 一道菜 / 一段秘密）作为退场承载。
```

适用条件：仅在 scene_card 标记 `counter_prior_scene.used=true`（反先验场景）或 role_brief 显式给出"反 AI 默认"指令时触发；否则用 §2 主流程即可，不强制每场都跑反 AI 模板。

名著锚点：挪威森林 scene 10（医院 + 黄瓜 + 欧里庇得斯）/ 你好旧时光 S14（延迟揭示型死亡）/ 流浪地球 S14（不可靠叙述）/ 斯通纳 S06（诊断式冷判定）/ 大唐李白 S20（配角主体性退场）。

→ 三层模型理论深度见 `dialogue-craft` skill 的 `references/subtext-theory.md`

### 3. 收敛到四项固定内容

orchestrator 在 prompt 末尾要求 Actor 直接产出四项固定内容（见 §4 契约），不做二次提取。Actor 产出后 orchestrator 原样落盘——不改写、不摘要。

rationale：原自由文本 + 事后抽锚点的模式在多场景批量排练中会让 orchestrator 注意力失焦；固定四项让 Actor 自己收敛，writer 直接消费，减少中间环节。

### 4.1 四项产出 self-check（落盘前必走）

Actor 收敛到四项后**先自检再 Write**——任一项过不了就改写，不要绕过。所有判断用 LLM 自评，不上硬数字阈值：

- **想说但不会直说**：必须承接本场景 `role_brief.suppressed_pressure` / `misread_now`，是"绕开 voice_boundaries 才不直说"，不是泛化的内心独白。脱离本场具体压力源 → 改写。
- **台词候选 2-4 条**：每条必须可指认行动目的（说服 / 威胁 / 试探 / 隐瞒 / 转移 / 求证…）；候选之间必须在情绪强度或潜台词上有差异，不是同一句话换措辞。引用 `dialogue-craft` 的"对白即行动 / 潜文本"小节做自检——任一条若读起来像"角色把心理活动直接说出口"，删除并重写。若候选反复出现"我感到 / 我其实 / 我害怕 / 我爱你 / 我恨你"等直译内心句，整组必须重跑，改为可执行的动作 / 沉默 / 错位台词（与 §2 压力表达排练 self-check 同源）。
- **禁用语气**：必须给出本场景该角色不会用的具体语气类型 + 1-2 词理由（如"哀求语气：杨过当面对洛朝弦不会示弱"）；不要只写"温柔"" 凶狠"等空标签。
- **动作或停顿**：必须服务本场景节奏 / 角色声音；引用 `prose-craft` 的"段落节奏 / 节拍"小节做自检——动作不能是套话（"皱了皱眉"），要带本场具体语境（看向 / 触摸 / 沉默时长 / 视线落点）。

四项任一项缺失或过不了自检 → Actor reply "排练未完成 + 缺项名 + 已尝试改写次数"，不落盘。orchestrator 视作 rehearsal 失败按既有兜底。

### 4. 落盘（Phase 6 scene-level rehearsal 契约）

Actor 产出**四项固定内容**，orchestrator 落盘 `pipeline/staging/scene_{scene_id}/{slug}_rehearsal.md`：

```markdown
# {display_name}（{slug}）— scene {scene_id} rehearsal

## 想说但不会直说
{角色此刻在场景情境下想表达但基于 voice_boundaries / 人设压抑会绕开的心理内容，1-3 句}

## 台词候选（2-4 条）
- {候选 1 — 角色可能说的台词，带语气标注}
- {候选 2 — 另一种情绪强度下的版本}
- ...

## 禁用语气
{在本场景情境下该角色不会使用的语气 / 修辞 / 表达方式，1-2 条}

## 动作或停顿
{非台词的身体反应 / 节奏细节，供 writer 穿插到叙述中，1-2 条}
```

- **slug** = 角色的 `role_slug`（与 `pipeline/story-character-skills/.claude/skills/{slug}/` 和 `role_briefs.md` 内 `character: {slug}` 字段对齐；中文名 → slug 的映射由 character-persona build-meta.yaml 落定）
- **子目录分层**：
  - Phase 6 情境排练 → `pipeline/staging/scene_{scene_id}/{slug}_rehearsal.md`
  - 审稿校验 → `pipeline/staging/scene_{scene_id}/{slug}_validation.md`（保持场景维度聚合）
- **产出强制**：缺任一项 Actor 返回"排练未完成" + 缺项名；orchestrator 视作 rehearsal 失败，writer 侧按"rehearsal 不可用"占位分支处理（见 writer SKILL 的按条件读约定）
- **Actor 的原始 QA 对话**不单独持久化（Phase 6 场景多、原文会挤占空间）；四项固定内容已是精炼后的 writer 消费素材
