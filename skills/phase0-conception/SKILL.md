---
name: phase0-conception
description: MUSE Phase 0 阶段技能（故事构想）——pipeline 起点。从已确定的创作需求中提炼前提、核心价值对、主控思想、类型、主驱动 primary_drive，输出 phase0_conception.yaml。由 orchestrator 进入 Phase 0 时通过 Skill 工具触发；不直接承接用户自然语言入口。
---

# Phase 0: 故事构想

## 核心原则

前提不是稀世珍宝——偏转时应舍（原文见 `references/mckee-premise.md §前提`）。Phase 0 的任务是从用户的模糊灵感中提炼出可以驱动完整故事的结构化起点——前提、核心价值、主控思想和类型选择。

## 输入契约

| 输入 | 来源 | 必需性 |
|------|------|--------|
| 用户创作需求 | 用户消息 | 必需 |
| 题材偏好/灵感素材 | 用户提供 | 可选 |

这是 Pipeline 的第一个阶段，没有前序交付物依赖。

## 执行步骤

### 1. 提炼前提

从用户意图中提炼故事的核心灵感。前提采用"如果……将会发生什么？"的开放式问题形式（案例与原文见 `references/mckee-premise.md §前提`）。前提需要回答三个问题：
- 这个故事的独特之处是什么？
- 什么让这个故事值得讲述？
- 核心冲突可以用一句话概括吗？

### 2. 确定核心价值对

识别故事要探索的核心价值——故事进展由正负价值的动态移动构建（价值原文见 `references/mckee-premise.md §主控思想`）。设计四层价值光谱（麦基的"否定之否定"模型）：

```
正面 → 矛盾 → 相反 → 否定之否定
例：爱 → 冷漠 → 恨 → 自恨（以爱之名行恨之实）
例：正义 → 不作为 → 不公正 → 以正义之名行不公正
```

"否定之否定"是最深层的价值状态——它伪装成正面，实则是最极端的负面。能够触及这一层的故事往往最具力量。

### 3. 构建主控思想

主控思想 = 价值判断 + 原因。它是故事在高潮时刻通过行动（而非说教）表达的终极意义。

> 「主控思想可以用一个句子来表达，描述出生活如何以及为何会从故事开始时的一种存在状况转化为故事结局时的另一种状况。主控思想具有两个组成部分：价值加原因。」
> —— 《故事》第六章

格式：`[正面/负面价值] 因为/当 [原因/条件]`

经典案例：
- 「人类的勇气和智慧必定战胜大自然的肆虐」——《大白鲨》
- 「邪恶横行，因为这是人性的一部分」——《唐人街》
- 「爱情充满了我们的生活，只要我们征服理性幻想并听从我们的本能」——《汉娜姐妹》

注意：主控思想在此阶段是暂定的，后续创作中可能被深化或修正。

> 「是故事告诉了你它的意义，而不是你将意义叙述到了故事之中。你并不是从思想中汲取出了行动，而是从行动中汲取出了思想。」
> —— 《故事》第六章

### 4. 选择类型

类型决定了故事的常规——观众的期待框架和创作的限制空间。

> 「类型常规是讲故事的人的『诗歌』韵律系统。它并没有抑制创造力，而是对其进行激发。挑战来自既要恪守常规又要避免陈词滥调。」
> —— 《故事》第四章

选择类型时需考虑：
- 这个前提最适合哪种类型的表达？
- 所选类型的常规（设定、角色、事件、价值）是什么？
- 如何在遵守常规的同时注入原创性？

### 5. 确定目标篇幅

根据故事复杂度和类型，确定目标字数范围。这会影响后续所有阶段的展开深度。

### 6. 提取硬约束

如果用户需求中包含显式枚举或硬约束（如"至少要有一段对话"、"必须包含 X 场景"），将它们提取为紧凑的 `requirements[]` 列表。这样后续阶段（特别是 Phase 5 场景分配和 Phase 7 终验）可以追踪每条约束是否被满足。

仅在用户有明确硬约束时生成此字段。模糊的偏好（如"希望感人一点"）不算硬约束。

### 7. 提取参考资料与风格指令（按需）

用户 query 中可能附带大段背景素材（历史资料、领域知识、技法要点）或作品风格要求。这些信息不属于"故事构想"，但必须持久化到 pipeline 中，否则后续阶段无法看到。

**`reference_materials`**（条件字段）：当用户提供了背景素材时生成。提取为**结构化摘要**——保留对创作有价值的具体细节，去掉冗余的百科性内容。不要原文复制。

**`style_directives`**（条件字段）：当用户有作品层面的风格要求时生成。这是作品整体风格（如"金庸武侠风格"、"现实主义细节描摹"），区别于 Phase 2 中角色层面的 voice_traits。

没有额外信息的 query 不生成这两个字段。

**`craft_targets`**（条件字段，与 reference_materials 同期生成）：从参考作品提取**手艺操作**，禁止只用形容词。

```yaml
craft_targets:
  dominant_carriers:
    - "该参考作品常用什么承载情绪 / 主题：动作、物件、程序文体、POV 遮蔽、日常闲聊等"
  omission_style:
    - "哪些内容常被省略：心理、过程、解释、关键画面、历史背景"
  scale_strategy: "高潮倾向：放大 | 收缩 | 反高潮 | 对位 | 混合"
  characterization_method:
    - "人物主要通过自述 / 行动 / 他人证词 / 误读 / 物件痕迹 / 压力选择中的哪一种被认识"
```

禁止只输出："冷峻、克制、诗意、史诗感、电影感"；必须输出："用技术数据替代恐惧渲染；关键心理用动作压缩；宏大结尾收束到日常物件。"

新增子项 `narrator_position`（同样 optional）：

```yaml
narrator_position:
  primary: "intimate_first | reminiscing_first | reporter_third_close | reporter_third_distant | archival_zero | omniscient_satirist | bilingual_drifter | unreliable_first"
  permission: "narrator 在场景中允许做什么 / 禁止做什么"
  examples_in_reference_work:
    - "《阿Q正传》narrator 在意识流段沉默，让蜡烛燃烧速度自己评论"
    - "《月亮与六便士》narrator 是回忆者，可补充'后来发生的事'但不能进入角色心理"
```

**硬约束**：`narrator_position` 必须在选定 `reference_materials` 后确定。混合多本 reference 风格时必须明示主导者。

### 8. 判主驱动（`primary_drive`）

综合前 7 步的前提 / 核心价值 / 主控思想 / 类型 / 参考素材，判定本故事**主要靠什么前进**——即叙事驱动的主导方向。这是**全局默认**字段，下游 Phase 2/3/5 据此翻译为各自的 phase-local mode（不做跨 Phase 条件分支，只作近端默认建议）。

| 取值 | 语义 | 典型触发 |
|---|---|---|
| `shift` | 变化驱动——冲突 / 转折 / 弧光为主线（麦基默认）| 冲突驱动戏剧、单主角追求目标、成长/堕落叙事 |
| `reveal` | 揭示驱动——真相逐步显形 / 碎片逐步聚拢 | 侦探 / 档案拼图 / 观念显影 / 文献小说 |
| `observe` | 观察驱动——感知 / 关系 / 视角的累积变化 | 氛围累积 / 旅行观察 / 群像切片 / 风物志 |
| `mix` | 混合驱动——多个驱动**共同主导** | 侦探+成长并重 / 群像+单线调查并重 |

**`mix` 硬钉子**：`mix` **仅表示多个驱动共同主导，不表示未定**。一旦填 `mix`，Phase 2/3/5 仍必须各自落到明确的 phase-local mode（`character_arc_mode` / `spine_mode` / 叙事增量语义），不允许含糊其辞。**必须依据前 7 步选择最贴近的一类**——不允许以"不确定"为由跳过判定；只有多个驱动**共同主导**时才填 `mix`。既有产物缺字段时兼容层按 `shift` 解释，**不要**作为"拿不准时的安全回落"使用。

**`mix` 组成关系说明义务**：填 `mix` 时**必须**在 `phase0_conception.yaml` 的 `originality_statement.unique_angle` 字段写清**由哪些驱动共同主导、各自承担什么、关系如何**（如"信息揭示主导结构脊椎，成长副线服务证据拼合"）——不要求声明主次，但要求组合**可被复盘**。**承载位置硬约定**：组成关系说明**必须落在持久化 YAML 字段** `originality_statement.unique_angle`，不允许只写在主对话或非持久化的"构想说明"段落里——design-validation 只能读 YAML 文件，未持久化等于未说明。下游 mode_alignment 凭这段说明 + Phase 2/3/5 phase-local mode 的实际组合判 `aligned` / `explainable_divergence`；`originality_statement.unique_angle` 未写组成关系且 Phase 2/3/5 无法自洽组合时才 `suspicious_divergence`。**不为此新增 schema 字段**——复用已有 `originality_statement.unique_angle`。

**判据启发**：
- 前提问"什么发生了"——答"某人追求某事" → `shift` 默认
- 前提问"真相是什么"——答"事件的本质 / 某个隐藏事实" → `reveal`
- 前提问"这是一个什么样的世界 / 状态 / 人群"——答"某种氛围 / 观察角度" → `observe`
- 核心价值对的 positive/negative 极反映的是"状态变化"还是"真相显形"还是"感知重构"——强化主驱动判断

**不回读 / 不统治**：`primary_drive` 是**全局默认**，不是全局统治。writer / scene-reviewer / Phase 6 等下游 subagent **不回读** Phase 0 做 `if primary_drive == X then ...` 条件分支——它们只消费离自己最近的 phase-local 契约。Phase 0 的职责是**声明方向**，Phase 2/3/5 的职责是**把方向翻译为可执行契约**。

## 输出

→ YAML 输出结构见 `references/output-schema.md`

交付物写入 `pipeline/phase0_conception.yaml`，包含：premise, core_value, controlling_idea, genre, primary_drive, target_length, originality_statement。可选字段：requirements, reference_materials, style_directives, canon_reference_profile。

**既有产物 fallback**：`phase0_conception.yaml` 缺 `primary_drive` 时兼容层按 `shift` 解释，下游读取既有产物不视为缺必需字段。新生成路径必须显式填 primary_drive，不允许以"不确定"为由省略。

## canon_reference_profile 字段（方向 hint，可选）

Phase 0 本身不做结构化 canon research（输入未结构化 / signals 弱），但**保留 profile 字段**给 Phase 1+ 的 `Skill design-doc-reference` 提供方向 hint：

```yaml
canon_reference_profile:          # 全可选；缺席时由 design-doc-reference 自行从 genre/primary_drive 推方向
  desired_domains:                # 用户希望从 canon 学什么（提示 design-doc-reference refine 方向）
    - world_rule
    - reveal_structure
    - protagonist_archetype
    - scene_carrier
  avoid_domains:                  # 用户明示不要从 canon 学什么（模型据此自主收敛，不需开关字段）
    - prose_style_imitation
  user_reference_materials:       # 用户主动指定的参考 / 禁用作品
    - work: "斯通纳"
      stance: prefer              # prefer | avoid
      reason: "register 接近主角"
```

**用途**：Phase 1+ 调用 `Skill design-doc-reference` 时读 Phase 0 此字段作为 query refine 的初始方向，避免从 `genre / primary_drive` 单点猜测导致结果泛化。`avoid_domains` / `user_reference_materials.stance: avoid` 是用户"少引用某方向"意图的承载——下游 design-doc-reference 据此收敛，**不是**关闭 canon reference 的开关。

**字段缺席 → 不报错**；缺席时 design-doc-reference 退到 `genre / primary_drive` 推方向。Phase 1-5 一律先调用一次 `Skill design-doc-reference`（衍生写作默认 honor canon），由 skill 自身返回值决定是否降级——不存在"整层跳过"的关闭档。

## 常见错误

| 错误 | 后果 | 修正 |
|------|------|------|
| 前提落入陈词滥调 | 故事缺乏吸引力，泯然众人 | 追问用户的独特切入点，检索同题材经典作品做差异化 |
| 前提过于宏大 | 中短篇无法承载，最终空洞 | 聚焦单一核心冲突，缩小前提的时空范围 |

→ 理论深度参考见 `references/mckee-premise.md`
→ 交付前自检见 `references/mckee-premise.md §验证清单`
