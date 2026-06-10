---
name: phase2-character
description: MUSE Phase 2 人物系统 pipeline 阶段 skill。设计主角欲望系统与弧光（character_arc.mode）、对手、配角群像、8D 声音特征，产出 phase2_character.yaml + 角色 Skill 包（hard gate）。由 orchestrator 跑到 Phase 2 时以 Skill 工具显式触发。pipeline 内部件，不直接承接用户"设计角色"的自然语言入口（那走 character-design / story-writing 等入口 skill 编排）。
---

# Phase 2: 人物系统

## 核心原则

人物塑造（外在可观察的素质）和人物性格（压力下的选择）是两回事——压力下的选择才揭示真相。对照/反衬人物塑造与性格真相是戏剧张力的核心机制（原文与案例见 `references/mckee-character.md`）。

## 输入契约

从 Phase 0 接收：
- `core_value` — 人物冲突应体现核心价值的正负对立
- `premise` — 人物处境围绕前提设定

从 Phase 1 接收：
- `setting(4D)` — 人物背景受世界设定约束
- `world_rules` — 世界规则决定人物的可能性边界
- `daily_life` — 仪式、价值观、权力结构为人物的日常和幕后故事提供素材

## Canon/design reference（设计前置必跑）

**本段必跑**：进入本阶段先调用 `Skill design-doc-reference`——**不要**基于"当前可见 skill 列表里没看到"或"猜测 MUSE-canon-distill 未装"做预判跳过。**先调，再由 skill 自身返回值决定是否降级**：

```
phase=2
genre=<Phase 0 genre.primary>
signals=<JSON: 至少含 protagonist_register, antagonist_register, relationship_mode, primary_drive 中能填的>
```

调用成功 → Read `pipeline/references/phase2_design_ref.md`，只学习：

- 同 register 名著人物的**维度组合**（外在塑造 vs 内在性格真相的反差结构）
- **声音特征写法**（HOW 描述而非标签）
- **弧光模式**（transformative / revelatory / static / degenerative 各自的组织线）

**合法降级条件**：仅当 skill **实际返回** 扩展包未装 / KB 不可达 / 无匹配 三类信号时，才走下方降级 fallback 表。"看不到 skill 名"、"未确认是否安装"**不是**合法降级理由——这两类情况必须先调一次再判。

## 名著人物档案参考（扩展包不可触发时的降级 fallback 表）

> **优先级**：上方 `Skill design-doc-reference` 是默认前置；本表仅作为 skill 实际返回扩展包未装 / KB 不可达 / 无匹配时的启发降级参考，不是"看不到 skill 就直接用本表"的入口。

MUSE-canon-distill 扩展包提供按"塑造 vs 真相 / 维度=矛盾 / 声音特征 / 关键对白 / 弧光"五段式蒸馏的名著人物档案（`knowledge-base/novels/{book}/characters/{角色}.md`，由 canon-distill 的 `character-kb-distill` skill 离线生成）——直接对照 phase2 字段填写。每次为新故事设计人物时，先选 2-3 个最接近 register 的名著人物档案做参考，**不是仿写**。主干 plugin 单独运行时此参考不可达，按下方表的"角色类型 / 学什么"两列即可启发设计。

### 推荐档案集（按 register 分类）

| 角色类型 / register | 名著档案（canon-distill 内位置） | 学什么 |
|---|---|---|
| 表达力弱但感受力强的主角 | `斯通纳/characters/威廉·斯通纳.md` | "极简对白 + 内心独白缺失"如何用外部行为推断内心；"知道自己曾经是谁"式弧光 |
| 沉默是主声形态的配角 | `白鹿原/characters/吴仙草.md` | "全书对白不超过 10 句"如何用 4-5 个关键短句承载全部角色重量 |
| 压力下程序前置 / 悲伤后置的女性 | `白鹿原/characters/朱白氏.md` | "把悲伤推后 + 把程序提前"如何让强韧不靠自我陈述 |
| 精神胜利法失效的反英雄 | `阿Q正传/characters/阿Q.md` | 标志性"心理机制"如何在压力下失效（不是单一负空间，是结构性崩塌）|
| 关怀语调推进暴力的施害者 | `现实一种/characters/山岗.md` | "亲切语言 + 精密道具"承载暴力的非传统反派写法 |
| 身体反应承载心理的脆弱者 | `月亮与六便士/characters/勃朗什·施特洛夫.md` | 完整的身体反应递进链如何替代任何内心独白 |

### 使用规则

1. **不是仿写**：参考档案的"结构"和"层次"，不复制"内容"。新角色的 inner_capacity / loss_signal / 关键对白都必须从故事设定派生。
2. **每个新角色至少参考 1 个档案**：减少 builder 凭空想象的概率。
3. **档案的"声音特征"和"关键对白"两节是 voice_traits / voice_boundaries 字段的最佳填写范例**——比抽象的"4D + 压力下确定性"更直观。
4. **`<!-- 来源 -->` 注解中引用档案路径**：从 phase2_character.yaml → 字段 → ref: 档案路径，让审稿能反查。

## canon_archetype 字段

当 `Skill design-doc-reference` 产出 archetype candidate 卡，且 orchestrator promote 到 `pipeline/inspiration_ledger.yaml`（status=accepted/bound）后，phase2 角色字段挂 INS-A* 引用：

```yaml
protagonist:
  display_name: ...
  desire_system: ...
  canon_archetype:                # 新增字段（全 optional）
    - id: INS-A01
      weight: dominant
    - id: INS-A02                 # 可选第二张
      weight: secondary
      merge_boundary: "只学习 X，不学习 Y"  # weight=secondary 时必填

deuteragonist:                    # 双主角同样可选
  canon_archetype:
    - id: INS-A03
      weight: dominant

antagonist:                       # 对手按需
  canon_archetype:
    - id: INS-A04
      weight: dominant
```

**原型数量约束**（一个不少，两个也行，三个就多了）：

| 数组长度 | 处理 |
|---|---|
| 0（字段不存在 / 空数组） | 不报错，phase2 走原创路径不挂原型 |
| 1 | **默认推荐**；weight 必须为 dominant |
| 2 | **例外路径**；必须 1 dominant + 1 secondary（不能两张都 dominant）；secondary 必须有 `merge_boundary` |
| ≥3 | **hard gate 报错**——原型过多会让角色变拼贴，违反 archetype "识别 + 保留 + 不复制" 强承诺 |

**字段引用闭环**：

- 引用的 INS-* ID 必须在 `pipeline/inspiration_ledger.yaml` 内
- 引用的卡必须 `type=archetype` 且 `status ∈ {accepted, bound}`
- 引用 INS-* 的 `archetype_target_slug` 必须对应本 phase2 中真实存在的角色 slot

字段不存在 → 不报错；存在则必须闭环自洽。

## 衍生前置：已有 `phase2_character.yaml` 则在其上完善（MUSE-derivative）

本 skill 在 **MUSE-derivative**（衍生写作）运行——与 MUSE-writing 的唯一区别在此段。执行 §执行步骤 前先看 work_dir 是否已有 `pipeline/phase2_character.yaml`（derivative 入口经 `init_derivative_run.py` 从 canon 蒸馏物 / 用户已有 pipeline 预置的继承基线；canon `characters/*.md` 亦在 work_dir 内）：

- **已有（继承基线）** → 不从零重生成，把它当起点在其上**完善**：保留继承角色（原作主角 / 配角谱系 / 关系网 / canonical 声音不推翻 = 衍生连贯性硬约束）；按本次衍生需求调整——续写/同人补新配角或深化既有角色弧光、外传把某配角升格为主角并把原主角降格、跨风格保留档案不动；元数据标 `source: derived_from=<canon-slug | existing_pipeline>`。此时 §执行步骤 作**完善检查表**（缺则补），非从零产出指令。
- **没有** → 按 §执行步骤 从零生成（与 MUSE-writing 完全一致）。

两种情形产物 schema 与下游消费都与 MUSE-writing 一致——这是 derivative ≈ MUSE-writing 的根本。

## 执行步骤

### 1. 设计主角

**人物塑造**（外在）：年龄、性别、职业、外貌、社会背景等可观察素质。

**欲望系统**（内在驱动力）：

- **自觉欲望**：主角知道自己想要什么（具体的、可追求的目标）
- **不自觉欲望**：主角真正需要但不自知的东西（通常与自觉欲望矛盾）
- **核心缺陷**：阻碍主角获得真正所需的性格弱点

**人物轨迹**（`character_arc`）：角色在压力下的存在方式——**不必然是"转变"**，由 `character_arc.mode` 字段声明轨迹类型：

| `mode` | 轨迹描述模式 | 典型 |
|---|---|---|
| `transformative` | 从初始状态到最终状态的可识别转变：`初始状态 → 触发 → 认知失调 → 蜕变节点 → 最终状态` | 经典弧光、成长、觉醒 |
| `revelatory` | 稳定核**原本就在那里**，故事做"显形"不是"改造"——start/end 是读者/人物**认知**的变化，角色本身的核没动 | 侦探型主角 / 见证者 / 讽刺小说扁平主角 / 压力下被看清的人 |
| `static` | 不以转变为组织力，也不以"逐步显形"为主要组织力——固定透镜 / 讽刺常量 / 见证者 / 反结构稳定存在 | 卡夫卡式被结构碾压者 / 观察视角承担者 |
| `degenerative` | 退化 / 堕落 / 不可逆衰败轨迹 | 悲剧主角 / 道德滑坡叙事 |

**边界钉（`revelatory` vs `static`）**：有没有"揭示稳定核"这条**组织线**。有，就是 `revelatory`（故事在做显形动作）；没有，角色只是固定存在，就是 `static`。

**load-bearing 约束**：当前 schema **`protagonist.character_arc.mode` 必填；`deuteragonist` 若存在，其 `character_arc.mode` 也必填**。设计上 load-bearing 角色（主角 / 双主角 / 守护者 + 承担弧光或显形功能的 antagonist / 关键配角）都应声明 mode，但 antagonist / supporting_cast 的 `character_arc.mode` 字段尚未开放——设计时不要把 antagonist 判成 load-bearing 却写不进 schema，契约矛盾会漏评。

**与 Phase 0 `primary_drive` 的关系**：`character_arc.mode` 是 phase-local operational enum——**Phase 2 不回读 `primary_drive` 做条件分支**。Phase 2 根据角色性质独立判定 mode。两层对齐由 Phase 5 → 6 过渡点的 `mode_alignment` companion report 非阻断校验，不在 Phase 2 内部分支。

**人物塑造与性格真相的反差**：显式设计主角的外在面具与内在性格的裂隙——戏剧张力的核心来源（所有 mode 通用；`static` 角色的"反差"可以是"外部世界对他的误读"而非他自己的内在裂隙）。

**幕后故事**：设计 3-5 个主角过去的关键事件。不是传记，而是可被 Phase 4-6 "采收"的种子（闪回、对话中提及、动机的具体化）。幕后故事应与 Phase 1 的世界设定一致。

> 欲望系统 / 弧光 / 反差 / 幕后故事的原文依据与理论展开见 `references/mckee-character.md`。

**日常生活**：

基于 Phase 1 的 `daily_life`，具体化主角在这个世界里的日常：怎么吃饭、怎么工作、怎么消遣、怎么与人打交道。这些细节为 Phase 6 提供叙事素材，避免模型临场泛化。

**移情机制**：确保读者能认同主角——至少一个引发好感的特质、值得同情的处境、值得追求的目标。

**内在生存能力**（`inner_capacity`）：主角的"内在生存能力"是 ta 之所以能在世界中存在的根基——失去它，ta 不再是 ta。设计该能力 + 何时失灵 + 失灵的具体可观察表现，让 Phase 6 在写"失去"的场景时有具体的反应缺席可落。

```yaml
inner_capacity:
  primary: "幻想 | 写作 | 共情 | 信任 | 修复 | 信仰 | 自我说服 | <自定>"
  why_load_bearing: "为什么这个能力是 ta 的存在基础（1 句）"
  loss_trigger: "什么场景 / 事件会触发这个能力失灵"
  loss_signal: "失灵时如何在正文中显示——必须是可执行的具体动作 / 反应缺席"
```

**辨认机制**（可选 enrichment 字段）：以下 3 个字段强制设计主角**怎么被读者/其他角色"认出"**——AI 默认会写"性格刻画"（形容词、心理描写），这些字段把焦点拉回到**辨认机制**（通过行动、物证、转述、误读、沉默、身体反应被读懂）。可选，但缺省时 Phase 6 容易把主角写成"被解释的人"而不是"被读出来的人"。

```yaml
recognition_path:
  primary_method: "direct_action | object_evidence | second_hand_story | misread_evidence | procedural_record | silence | bodily_reaction"
  first_false_reading: "读者或其他角色最初可能误读什么"
  correction_method: "后续如何修正"

backstory_harvest:
  method: "embedded_storyteller | object_trace | witness_chain | contradictory_testimony | sensory_trigger | official_record"
  carrier: "具体承载物 / 讲述者 / 证据"
  withheld_part: "故意不交代的部分"

misread_matrix:
  - observer: "谁"
    target: "误读谁"
    evidence_seen: "看见 / 听见 / 拿到的证据"
    wrong_conclusion: "错误结论"
    narrative_value: "制造反讽 / 冲突 / 迟滞 / 悬念"
```

### 2. 设计对手

结构的功能是把人物逼向越来越艰难的两难之境，对抗越强、真实本性揭示越深（原文见 `references/mckee-character.md §对抗力量`）。

- 对手必须足够强大，能真正威胁主角
- 从对手视角写对手——对手认为自己是正确的，有自己的欲望和逻辑
- 避免"纯粹的恶"，那是扁平化
- 考虑内在对手（主角自身）作为最强大的对抗力量

### 3. 设计配角

每个配角必须有存在的功能理由（人物经济原则），不做工具人：
- 与主角形成对照（反衬人物塑造 vs 性格真相）
- 各自有独特的说话方式和行为模式

**主体性物件**（`subjectivity_object`，仅 supporting_cast / antagonist / victim 类角色）：当配角在故事中会经历退场（死亡 / 失踪 / 沉默化），ta 留下的"物件"承载 ta 的主体性继续存在。设计该物件——主角或其他角色可拿到它、面对它、回应它，让退场不只是"消失"。

```yaml
subjectivity_object:  # 仅 supporting_cast / antagonist / victim 类角色
  what: "<具体物件描述>"
  created_when: "什么时候该角色创造的"
  where_it_lives: "在故事中以什么形式存在（藏在脑海 / 写在纸上 / 留给他人 / 物理实体）"
  potential_use: "如果该角色面临退场场景，此物件如何成为退场承载"
```

### 4. 设计声音特征

为每个重要角色设计 8D 声音框架（"演员级极简"原则见 `references/mckee-character.md §声音设计`）：


**避免过度设计**：

- **定义倾向，不定义映射**：写"偶尔用技术隐喻"，不要写"心跳加速=CPU负载红线，眼眶发热=未知进程占用资源"。给了映射表，Phase 6 会逐条执行，导致全文被同一类修辞淹没。
- **身份标签是背景，不是修辞引擎**：角色的职业/身份影响他的思维方式，但他首先是一个人。不要把身份标签定义为角色的默认修辞模式。一个程序员在恐惧时不会每次都用代码隐喻——他会像任何人一样恐惧。
- **为 Phase 6 留有余地**：声音特征是倾向性指南。Phase 6 在执行时应根据场景的情感需要自然调整，包括在高潮段落完全放弃角色的标志性修辞，让角色用最朴素的语言表达。

**维度 5-8 的 YAML 示例**（覆盖压力确定性 / 非语言声纹 / 负空间声音 / 误读模式——详细维度定义见 `references/voice-design.md`）：

```yaml
negative_space_voice:
  never_says_directly:
    - "我害怕失去你"
  converts_into:
    - "检查门窗 / 重新确认路线 / 嘲讽对方迟到"
pressure_certainty:
  when_accused: "不急于辩解，先指出对方证据链的一个漏洞"
nonverbal_voice:
  - "做决定时先处理手边物件，而非看人"
misread_pattern:
  often_misread_as: "{别人最容易给 ta 的标签}"
  by_whom: "{最常误读 ta 的人}"
  ta_corrects: false
```

→ 声音框架详细指南见 `references/voice-design.md`

### 5. 设计角色极化对比

当故事中有两个以上重要角色时，明确描述他们之间的极化关系。极化是产生戏剧张力的来源——同一情境下，两个极化的角色会做出截然不同的反应。

好的极化案例：
> 陈默=过度分析/言多/情感封装/数字思维；老谭=直觉行动/言少/情感外显/身体技能。对比产生张力，每个情境下两人反应截然不同。

极化不是对立——而是互相映照。每个角色都是另一个角色的"镜子"，照出对方缺少的东西。

### 6. 构建关系网络

绘制人物之间的关系图，标注：
- 权力动态（谁对谁有权力？）
- 亲密距离（关系的远近）
- 潜在变化（关系可能如何转变？）

### 7. 生成角色 Skill 包（hard gate — 不完成阻断 Phase 5/6）

Phase 2 **决定**要为哪些角色生成资产（主角、对手、值得构建 Skill 的配角），然后**调用** `character-persona` 构建器落盘。产物目录结构、adapter 派生规则、字段 / 章节白名单等详见 [`character-persona/SKILL.md`](../character-persona/SKILL.md)，**字段权威以 character-persona 为准，本节不复述**。

**4 产物（每角色齐全才放行）**：

| # | 产物 | 路径 |
|---|---|---|
| 1 | runtime Skill | `pipeline/story-character-skills/.claude/skills/{slug}/SKILL.md` |
| 2 | 初始主观状态 | `pipeline/story-character-skills/.claude/skills/{slug}/state.md` |
| 3 | 构建元数据 | `pipeline/story-character-skills/.claude/skills/{slug}/build-meta.yaml` |
| 4 | 兼容 adapter | `pipeline/characters/{中文角色名}.md`（sha256 与 build-meta.yaml `adapter_sha256` 一致） |

**核验**：Phase 2 step 7 收束前 + Phase 5→6 过渡前各跑一次：

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_phase2_assets.py <pipeline_dir>
```

退出码：
- **0** → 通过；在回复中明示 "phase2 hard gate PASS"
- **非 0** → abort：不进入下一阶段；在回复中粘贴脚本 stdout 失败原因；修复后重跑；**严禁**"继续往下，回头补"

**详细字段断言与错误码以脚本为权威**：
[`MUSE-writing/scripts/verify_phase2_assets.py`](../../scripts/verify_phase2_assets.py)。
本 SKILL.md 不复述脚本在防什么；执行者只需关心脚本调用 + 退出码处理。

**未构建例外**：仅"只在他人叙述中出现 / 纯背景人物 / 无对白无关键行动"的配角可跳过 Phase 2 构建，需在 build-report.md "未构建"表填非空 `skip_reason`（builder 自检；脚本兜底校验）。

**绝对硬线**：凡在 `phase5_scenes.yaml` `participants` 中登场的角色不得作为 Phase 2 例外——Phase 5→6 过渡时补建 gate 会拉回。

**硬约束**：`pipeline/characters/{角色名}.md` 不再手写；凡由 Phase 2 直接写入该目录的内容视为绕过构建器。

## 输出

→ YAML 输出结构见 `references/output-schema.md`

**step 4-6 交付物（设计层）**：
- `pipeline/phase2_character.yaml`：结构化数据（protagonist, antagonist, **deuteragonist**（可选）, supporting_cast, relationships, contrast_axes, voice_boundaries）；其中 `protagonist.character_arc.mode` 必填，`deuteragonist.character_arc.mode` 若存在也必填（enum：transformative / revelatory / static / degenerative，边界见 Step 1 "人物轨迹"段）；`deuteragonist` 是麦基双主角 / 守护者形态的可选字段（结构同 protagonist），下游 character-persona / story-writing 按 optional 处理

**step 7 hard gate 交付物（角色资产层）——缺任一项阻断 Phase 3 以后**：
- `pipeline/story-character-skills/.claude/skills/{slug}/SKILL.md` / `state.md` / `build-meta.yaml`：每角色运行时 Skill 包
- `pipeline/characters/{中文角色名}.md`：兼容 adapter（由 character-persona 从 SKILL.md 派生，下游 writer / design-validation / 审稿消费）
- `pipeline/story-character-skills/build-report.md`：构建决策记录 + 已构建 / 未构建角色清单

**硬约束**：`pipeline/characters/{角色名}.md` 不再手写；凡由 Phase 2 直接写入该目录的内容一律视为**绕过构建器**，违反 hard gate。

**既有产物 fallback**：`phase2_character.yaml` 的 `character_arc` 缺 `mode` 字段时兼容层按 `transformative` 解释，下游读取既有产物不视为缺必需字段。新生成路径必须显式依据角色性质选择最贴近的一类，不允许以"不确定"为由跳过判定。

## 常见错误

| 错误 | 后果 | 修正 |
|------|------|------|
| 人物轨迹与核心价值脱节（按 mode 各有表现：transformative 下是成长方向偏离主题 / revelatory 下是稳定核与主题无关联 / static 下是稳定核所抵抗的压力和主题无关联 / degenerative 下是退化轨迹与主题无关联）| 人物轨迹不承担价值表达，故事主题失重 | 轨迹的终点（或 static 的维持对象 / revelatory 的显形核）应体现核心价值的某种立场 |
| voice_traits 给出"情感→隐喻"映射表 | Phase 6 逐条执行，全文被同一类修辞淹没 | 只定义倾向和上限，不给具体映射 |

→ 理论深度参考见 `references/mckee-character.md`
