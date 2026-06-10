---
name: phase5-scene-arrangement
description: MUSE Phase 5 — 场景编排。将 Phase 4 的序列设计展开为具体场景清单，规划每个场景的实质性叙事增量（按 spine_mode 解释：价值变化 / 信息揭示 / 关系重估 / 感知重构）、冲突和张力曲线，并为关键场景标注节拍方向。orchestrator 跑到 Phase 5 时显式触发；属 pipeline 内部阶段件，不直接承接用户自然语言入口（写作意图由 story-writing / novel-outline / plot-design 等入口 skill 路由）。
---

# Phase 5: 展开序列为场景 + 预留节拍入口

## 核心原则

每个场景都是一个缩微故事——必须带来**实质性的叙事增量**：可表现为**价值变化**（麦基默认 / `spine_mode=desire`）、**信息揭示**（侦探 / 调查 / 真相显形）、**关系重估**（人物间认知 / 力量对比改变）或**感知重构**（POV / 读者对世界 / 处境的理解变化）。原文见 `references/mckee-scenes.md §场景定义 / §转折点`——麦基的"价值转折"是该原则在 desire 范式下的具体形态。

**所有 `spine_mode` 通用判据**：如果一个场景的**关键叙事状态**在结尾与开头实质相同——没有任何叙事增量发生——这个场景不应该存在。

## 输入契约

从 Phase 4 接收（核心依赖）：
- `arc_expansions[]` — 按 Arc 组织的序列设计（逐序列展开为场景）
- `causal_chain` — 序列级因果链（场景间因果应与之对齐）

从 Phase 3 接收（参考依赖）：
- `spine_statement` — 场景取舍测试：是否与脊椎相关？
- `story_climax_design` — 危机/高潮场景的设计依据
- `arcs[]` — Arc 的价值方向（场景的 arc_id 派生字段来源）

从 Phase 2 接收（核心依赖）：
- `protagonist`, `deuteragonist`（若存在）, `antagonist`, `supporting_cast` — 场景人物分配
- `voice_traits` — 涉及对白的场景需要声音特征参考

从 Phase 1 接收（核心依赖）：
- `generative_driver` — 题材的冲突生成机制；场景的具体威胁、可用资源、不可信/可信细节应从 driver 推导，禁止临场发明与之矛盾的世界事实
- `world_rules` — 物理 / 社会 / 心理规则；约束场景内人物行动可能性

从 Phase 0 接收（参考依赖）：
- `core_value` — 场景的实质性叙事增量围绕核心价值的正负极（desire 下=价值变化 / information 下=围绕真相显形的认知正负极 / motif 下=母题展开的语义正负极）
- `requirements`（可选） — 用户的结构性约束（如章节数、段落格式）
- `style_directives`（可选） — 作品风格要求

## Canon/design reference（设计前置必跑）

**本段必跑**：进入本阶段先调用 `Skill design-doc-reference`——**不要**基于"当前可见 skill 列表里没看到"或"猜测 MUSE-canon-distill 未装"做预判跳过。**先调，再由 skill 自身返回值决定是否降级**：

```
phase=5
genre=<Phase 0 genre.primary>
signals=<JSON: 至少含 scene_count_target, key_scene_types, pov_pattern, risk_families 中能填的>
```

调用成功 → Read `pipeline/references/phase5_design_ref.md`，只学习：

- **场景编排节奏**（同 genre 内场景数量 / 类型分布 / 张力曲线的取舍）
- **POV 切分模式**（单 POV / 多 POV / POV 内外双场景对位）
- **key_scene 类型分布**（开篇 / 收束 / 高潮 / 高压对峙 / 群戏的典型配比）

**合法降级条件**：仅当 skill **实际返回** 扩展包未装 / KB 不可达 / 无匹配 三类信号时，才跳过本段按下方步骤自主设计。"看不到 skill 名"、"未确认是否安装"**不是**合法降级理由——这两类情况必须先调一次再判。

## inspiration_refs[] 字段

scene_card 新增 `inspiration_refs` 字段——本场承载哪些 `pipeline/inspiration_ledger.yaml` 中 `type=pattern` 的 INS-* 灵感卡：

```yaml
scenes:
  - scene_id: S07
    reader_track: ...
    scene_tasks: [...]
    craft_carrier: ...
    inspiration_refs:               # 新增字段（全 optional）
      - INS-001                     # 引用 ledger 中 type=pattern 的卡
      - INS-007
```

**Budget 约束**：

| 场景类型 | 推荐数量 |
|---|---|
| 普通场景 | 0-1 张 |
| key_scene（开篇 / 收束 / 高潮 / 主要转折 / 高压对峙 / 群戏 / 情感转折）| 0-2 张（上限 2）|

**Why 不规定硬数字门槛**：描述性范围 + reviewer 现场判定，避免凑数式应用规则。

**字段引用闭环 hard gate**（脚本见 `validate_phase5_r10.py`）：

对每个 `scene.inspiration_refs[]` 中的 INS-*：

- ledger 内必须存在该 INS-*
- 引用的卡必须 `type=pattern` 且 `status ∈ {accepted, bound}`
- 该 INS-* 的 `project_encoding[]` 至少存在一项满足：
  - `phase == 5`
  - `scene_id == 本 scene_id`
  - `adoption_kind ∈ {scene_carrier, reveal_carrier, structure_carrier, craft_carrier}`

字段不存在 → 不报错（向后兼容）；存在则必须闭环自洽。

## 衍生前置：已有 `phase5_scenes.yaml` 则在其上完善（MUSE-derivative）

本 skill 在 **MUSE-derivative**（衍生写作）运行——与 MUSE-writing 的唯一区别在此段。执行 §执行步骤 前先看 work_dir 是否已有 `pipeline/phase5_scenes.yaml`（derivative 入口经 `init_derivative_run.py` 从 canon 蒸馏物 / 用户已有 pipeline 预置的继承基线；canon `scenes/scene_*.md` 蒸馏可作风格 few-shot）：

- **已有（继承基线）** → 不从零重生成，把它当起点在其上**完善**：
  - **续写（sequel）**：原作场景索引另记到 `inherited_scene_index`（不进 `scenes:`、不重写），`scenes:`（= phase6 遍历展开的字段）只列**待写的续写新增场景**（新 scene_id 从原索引末号+1）——这样 phase6 正常遍历 `scenes:` 即只写续写段，与 MUSE-writing 一致。续写首场须锚定 canon 末场状态（地点/时间/主角状态/情绪不矛盾）。
  - **跨风格**：保留场景清单作 phase6 重写蓝本（`scenes:` 沿用 canon scene_id）。
  - 其余（fan_fiction/spin_off 若入口未预置 phase5）按"没有"分支重建。
  - 元数据标 `source: derived_from=<canon-slug | existing_pipeline>`。此时 §执行步骤 作**完善检查表**（缺则补），非从零产出指令。
- **没有** → 按 §执行步骤 从零生成（与 MUSE-writing 完全一致）。

两种情形产物 schema 与下游消费都与 MUSE-writing 一致——这是 derivative ≈ MUSE-writing 的根本。

## 执行步骤

### 1. 逐序列展开场景

**结构约束优先**：如果 Phase 0 的 `requirements` 中包含结构性约束（如"分为 5 章"、"4-5 个自然段"），以用户要求为主框架。

对 Phase 4 每个序列，设计其内部场景。每个场景需要：

- **scene_id**：编号，**必须匹配 `^S\d{2}$` pattern**（S01 / S02 / ... / S99）。下游所有路径模板形如 `pipeline/scene_{scene_id}/`、`pipeline/scenes/scene_{scene_id}.md`——`scene_id` 自身**不得含 `scene_` 前缀**，否则路径会撞双前缀（如 `pipeline/scene_scene_1/`）

| ❌ 错误 | ✅ 正确 |
|---|---|
| `scene_id: scene_1` | `scene_id: S01` |
| `scene_id: 1` / `scene_id: "1"` | `scene_id: S01` |
| `scene_id: s01` / `scene_id: S1` | `scene_id: S01`（大写 S + 两位零填充数字） |
| `scene_id: 第一场` | `scene_id: S01`（中文标题放 `title` 字段） |
- **arc_id**：派生字段，从所属序列的 arc_id 获得
- **title**：场景标题（供 Phase 6 场景标识 + 检索）
- **location_time**：时空坐标，何时何地发生（引用 Phase 1 世界观切片，如"破宅 / 黄昏"）
- **participants**：在场人物
- **pov**：从谁的眼睛看这个场景
- **conflict**：这个场景中对抗什么
- **value_start / value_end**：进入和离开时的**关键叙事状态**（平铺两字段，**必须实质不同**——按 `spine_mode` 解释：desire 下=价值翻转 / information 下=信息或认知状态跃升 / observe-motif 下=关系或感知重构）
- **reader_track**（必填）：本场读者跟随的**单一阅读问题 / 行动线**。所有 scene_tasks 必须能解释如何服务这条线；服务不了的不能当 main 展开。例："小龙女判断陌生人证据是否可信，并决定是否纳入寻找杨过的行动"。
- **scene_tasks**：本场景必须完成的**叙事工作 + 创意灵感** list。每条必须是 scene_task object，见下方"scene_task 物理化判据"。
- **handoff**：如何衔接到下一个场景
- **narration_style**：叙事腔调锚。取值 `close-third`（紧贴 pov 角色内心）/ `third-omniscient`（全知叙述者）/ `first`（第一人称）。

场景数量由序列的冲突复杂度决定，不预设。

## scene_task 物理化判据

每条 scene_task 必含四字段（schema error 阻断缺一）：

```yaml
scene_task:
  abstract_function: <str>          # 允许保留戏剧意图概括
  physical_carrier:                 # list of object，≥1 项
    - text: <str>                   # 载体描述
      function_link: <str>          # 对应 abstract_function 子节点；非空非 placeholder
  reader_yield: [<str>, ...]
  rendering:
    default: summary | expand
    expand_only_if: <str>
```

### 物理化的是"戏剧承载物"，不是"动作步骤"（反向警告）

正确的 dramatic carrier（推荐）：

```yaml
abstract_function: "自我说服在公开场域的运转"
physical_carrier:
  - text: "杯沿停在唇边却没喝"
    function_link: "杯沿→自我说服可观察化"
  - text: "折扇开合的节拍跟话术对位"
    function_link: "折扇→话术节拍同步"
reader_yield: ["自欺装置首次被外人观察"]
rendering:
  default: summary
  expand_only_if: "动作改变关系 / 危险 / 欲望"
```

错误的反向 action_log 流水账（anti-pattern，schema error）：

```yaml
# 5 行扁平动作 + function_link 空
physical_carrier:
  - text: "裴怀璧端起酒杯"
    function_link: ""               # 触发 schema error
  - text: "他喝一口"
    function_link: ""
  - text: "放下酒杯"
    function_link: ""
  - text: "看了一眼窗外"
    function_link: ""
  - text: "敲桌"
    function_link: ""
```

历史双 marker 字符串（如 `[核心][main] ...`）仅保留为下游渲染兼容；Phase 5 新产物不再以字符串任务作为主结构。详细 4 类校验见 [references/output-schema.md](references/output-schema.md)。

### 1bis. 序列级场景排布模式（按需启用）

线性 "一事件一场景" 之外，phase5 在排布场景时**可考虑**以下两个序列级模式。两者都是与对位序列（phase4 `sequence_counterpoint`）互补的场景级工具，不强制使用——只在场景设计天然适配时启用。

#### 模式：双场景共写一事件（`dual_scene_one_event`）

核心灾难 / 重大事件 / 关键决断可分配两个空间分离的 POV，同一事件被读者经历两次（一次目击、一次推断）。

- **触发条件**：事件本身有"内 / 外"自然分隔（婚礼内 vs 婚礼外、决战内 vs 后勤侧、政变内 vs 平民街区）
- **设计要点**：
  - 内 POV 走 intimate distance，亲历的绝望
  - 外 POV 走 reporter distance，远距离信号推断（火光颜色 / 歌声 / 帐篷数变化 / 远处鼓声变奏）
  - 两个场景共用一个事件时间锚但**不互相补足信息**——外 POV 只拿到信号，不拿到现场真相
- **反 AI 化禁令**：禁止外 POV 突然"听清楚"或"看明白"；禁止用 narrator 旁白把外 POV 升级成全知。外 POV 的信息天花板=远距离可感知信号

名著锚点：《冰与火之歌Ⅲ》scene_S13（凯特琳内）+ scene_S14（艾莉亚外）——红色婚礼的内 / 外双场景。

#### 模式：赌注放大（`stakes_amplification`）

高赌注场景**之前**，加入一个"远超当前事件的远景对话"作为赌注放大器，让小目标突然背上大命题。

- **触发条件**：大型决战 / 关键谈判 / 临终告别等高赌注场景
- **设计要点**：
  - 远景对话内容必须远超当前事件（决战前谈百年大计 / 谈判前谈整个行业未来 / 告别前谈一生选择）
  - 远景对话长度不能太长（5-10 句即可，否则成为说教）
  - 远景对话与当前事件用一个共同物件 / 共同 POV 连接
- **反 AI 化禁令**：赌注放大**不允许通过 narrator 旁白直接说出**（"他不知道，这一战的结果将改变整个文明"）；必须通过角色之间的远景对话完成

名著锚点：《绍宋》scene_19——获鹿决战前夕，赵官家与吕颐浩在城头讨论战后"迁都燕京"，把战争赌注从"能否打赢"升级到"打赢后整个文明秩序"。

### 2. 标注关键场景的节拍方向

对以下关键场景，标注 `beat_direction`——节拍的大致方向和鸿沟位置：
- 激励事件场景
- 每个序列的高潮场景
- 每个 Arc 的高潮场景
- 故事危机/高潮场景

`beat_direction` 是给 Phase 6 的提示，不是逐节拍设计。示例：
- "从信任走到背叛，鸿沟在老板拿出审计数据时裂开"
- "从安全感走到不可逆的被困感，罗辑发现面壁者身份不可撤销"

**承载约束**：beat_direction 不只写"情绪走向"，必须写：鸿沟在哪里裂开 + 由什么承载。承载选择见 scene_card 同级新增字段 `craft_carrier`。

非关键场景不标注 beat_direction——节拍在 Phase 6 创作中自然生长。

### 3. 设计张力曲线

重复同一强度的情感体验会钝化读者（原文见 `references/mckee-scenes.md §张力设计`）。张力曲线的设计原则：
- **高低交替**：高张力场景后接低张力场景，形成呼吸节奏
- **整体递进**：张力的总体趋势向上，每次"低谷"都比前一次更高
- **高潮前加速**：临近故事高潮时，张力间隔缩短，节奏加快

标出全局张力曲线的高峰场景和低谷场景。

### 4. 验证因果连接

验证相邻场景之间的因果关系：前一个场景的结果是否导致了后一个场景的发生？如果只是时间顺序（"然后"），需要补强因果逻辑。

### 5. 非事件测试（所有 `spine_mode` 通用）

最终检查：每个场景是否带来**实质性叙事增量**（按 `spine_mode` 解释——desire=价值转折 / information=信息或认知状态跃升 / motif 或观察驱动=关系或感知重构）？如果某个场景的 `value_start` 和 `value_end` 实质相同（按当前故事的 mode 语义判定），删除它或与相邻场景合并。

### 6. AI pattern 风险标注（必填显式声明）

每个 scene **必须**显式声明 `scene_card.prose_risk_contract.used`——写作层 AI pattern 预防的场景级触发开关。无风险场景也要写 `used: false`，**禁止字段 absent**（PostToolUse hook 会扫 phase5_scenes.yaml 每个 scene，缺 `used` → WARN）。

判断本场是否激活 contract：命中以下触发画像时设 `used: true`，否则 `used: false`：

- 高密度动作 / 搜寻 / 移动 / 调度场景
- 展厅 / 宴会 / 办公室 / 饭局等社交调度场景
- 高强情绪但角色克制不说破的场景
- 依赖物件 / 沉默 / 停顿 / 视线传递关系变化的场景
- 大量环境描写 / 氛围描写场景
- 上轮 review 已诊断出某 family 命中的同类场景

不写数字阈值（动作 N 次 / 对白 N 句之类——feedback_no_rigid_rules + D1）；按场景判断是否命中即可。

`risk_families` 填 `prose-craft/references/ai-cliche-patterns.md` 现有 family 名（F 类 snake_case 或 A-G/观察层中文短语都行）。字段语义 / 渲染契约 / 冲突兜底详见 [`references/output-schema.md`](references/output-schema.md) `## prose_risk_contract` 段。

## 输出

→ YAML 输出结构见 `references/output-schema.md`

Phase 5 交付物：`pipeline/phase5_scenes.yaml`（聚合 yaml），其 `scenes[]` 每元素是一个 **scene_card**（L2 逻辑单位），供 Phase 6 writer / orchestrator 调度消费。
**不产 role_brief**——role_brief 在 Phase 6 runtime 由 role-brief-deriver subagent 派生。

聚合 yaml 同时包含：sequence_expansions[]（按序列分组的场景）、tension_curve、scene_causal_chain。

## 常见错误

| 错误 | 后果 | 修正 |
|------|------|------|
| 视角频繁切换 | 读者无法代入 | 中短篇建议固定 1-2 个视角 |
| 所有场景都标注 beat_direction | 过度设计，挤压 Phase 6 创作空间 | 仅关键场景标注 |
| 场景无实质性叙事增量（按 `spine_mode` 解释——desire 下无价值转折 / information 下无信息跃升 / motif 或观察驱动下无关系或感知重构） | 非事件 | 删除或与相邻场景合并 |
| 用 `must_include` / `characters` / `setting` / `core_conflict` / `value_shift` 等禁用字段名 | 下游 schema 对齐失败 | 统一用权威字段名：scene_tasks / participants / location_time / conflict / value_start+value_end |

> scene_tasks 的完整语义（禁写抽象读者反应 / 氛围目标 / 道具清单等）单一权威见 `references/output-schema.md §scene_tasks 语义`——Step 1 的 ✅/❌ 示例与之一致。

→ 理论深度参考见 `references/mckee-scenes.md`
→ **承载模式参考**：[`prose-craft/references/novel-craft-patterns.md`](../prose-craft/references/novel-craft-patterns.md)（按需加载——A 类承载点 / B 类视角 / C 类高潮 / D 类人物 / E 类形态；设计 scene_card 的 `craft_carrier` / `beat_direction` 时可参考）
