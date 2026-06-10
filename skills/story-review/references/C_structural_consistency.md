# 结构一致性审查（C 组）

> 审查目标：检测全文的时间线逻辑、世界观设定一致性，以及 pipeline 设计文档之间的交叉矛盾。
>
> 时间线和世界观问题在长篇叙事中特别容易累积——场景越多、设定越复杂，出错概率越高。pipeline 交叉校验则是 MUSE 特有的维度：8 阶段流程中，前序阶段的设计决策可能在后续阶段被无意覆盖或遗忘。

## 输入

**主场景（Phase 6 → Phase 7 过渡）：**
- `pipeline/scenes/scene_{id}.md` — 全部场景正文，按顺序通读（核心依赖）
- `pipeline/phase0_conception.yaml` — 构想（参考依赖）

**副场景（Phase 7 之后二次审查，story.md 已存在）：**
- `story.md` — 替代场景文件作为正文来源（核心依赖）
- `pipeline/phase0_conception.yaml` — 同下
- `pipeline/phase1_world.yaml` — 世界设定（核心依赖）
- `pipeline/phase2_character.yaml` — 角色设计（核心依赖）
- `pipeline/phase3_spine.yaml` — 故事脊椎（参考依赖）
- `pipeline/phase4_structure.yaml` — 结构设计（参考依赖）
- `pipeline/phase5_scenes.yaml` — 场景编排（核心依赖）

## 审查维度

### 1. 时间线与情节逻辑（timeline_plot）

检查故事中的时间关系和因果逻辑是否自洽。

**扫描要点：**

**A. 绝对时间矛盾**
- 明确提到的日期、年份、季节之间的矛盾
- "三年前"之类的相对时间锚点与其他时间线索冲突
- 角色年龄与时间线不匹配

**B. 时长/时序矛盾**
- 事件发生的顺序与叙述不一致
- 时间跨度不合理（如"一小时内"完成了需要数天的事情）
- 白天/黑夜、用餐时间等日常时间标记混乱
- 倒计时、截止期限、操作窗口等"状态推进"逻辑——前文建立的时间约束（如"你有 12 小时"）在后文中是否被遵守，到期时间点是否与叙事时间吻合

**C. 同时性矛盾**
- 同一角色在同一时间出现在两个不同地点
- 平行发生的事件之间的时间对不上

**D. 因果逻辑**
- 无因之果——事件结果出现了，但原因缺失或不充分
- 因果违反——结果与已建立的原因逻辑矛盾
- 被遗弃的情节线——前文埋下的线索或冲突后文完全消失，既未解决也未回收
- 具身前提——如果一个动作的物理前提在前文被否定（如门已锁、手已伤、路已断），后文直接执行该动作却不交代前提如何改变

**排除项：**
- 有意的非线性叙事（闪回、闪前）中的时间跳跃
- 魔幻现实主义中对时间的诗意处理
- 角色主观感受中的时间扭曲（"那一刻仿佛过了一个世纪"）

### 2. 世界观与设定（world_building）

检查故事世界的规则和设定在全文中是否被一致遵守。对照 `phase1_world.yaml` 中建立的世界规则。

**扫描要点：**

**A. 核心规则与后果链**
- 魔法/科技体系的规则在某些场景中被无声打破
- 已建立的物理法则或社会运行机制被违反
- Phase 1 设定的世界公理在正文中被矛盾
- 规则不仅要"存在"，还要"生效"——如果世界设定了某项限制（如技术的使用条件、能力的副作用、资源的稀缺性），正文中使用该规则时，其约束条件和后果是否也同时出现

**B. 社会规范矛盾**
- 文化习俗、礼仪、社会等级在不同场景中表现不一致
- 组织/机构的运作方式前后矛盾
- 经济体系、货币、交易规则的不一致

**C. 地理/空间矛盾**
- 地点之间的距离或方位前后不一致
- 建筑/空间的内部布局描述矛盾（如门的位置、房间的相对方位）
- 自然环境特征（气候、地形）与设定不符
- 空间拓扑——两地间的通行方式、可达性、旅行时间在不同场景中是否一致；一个封闭空间内的可见性、声音传播是否符合已建立的布局

**排除项：**
- 不同角色对世界规则的不同理解（认知差异，非矛盾）
- 世界规则本身有例外或灰色地带（已在设定中说明的）
- 随故事进展发生的世界变化（战争破坏、季节变换等）

### 3. 正文-设计偏离（pipeline_crosscheck）

检查正文是否无意偏离了设计文档。

> **职责分工**：设计文档之间的内部矛盾（YAML vs YAML）由 `design-validation` skill 在 Phase 5 → Phase 6 分段点处理。C 组只负责**正文相对设计的偏离**。

**扫描要点：**

**A. 事实偏离**
- 正文中的事实与 pipeline 设计明确不同（如 Phase 1 设定城市在山区，正文写成了海滨）
- 角色在正文中的年龄、职业、外貌等硬事实与 Phase 2 设计不一致

**B. 行为偏离**
- 角色在正文中的行为偏离 Phase 2 设计的核心特征（非成长弧线内的偏离）
- Phase 3 resolution 中的关键具象细节在正文中被替换或丢失

**C. 结构偏离**
- Phase 4/5 设计的关键转折点在正文中被跳过或大幅改变
- 场景的价值变化方向与 Phase 5 设计相反

**D. 承载点在正文真正生效（carrier_effective_in_prose）**

若 Phase 5 `scene_card` 含 `craft_carrier` 字段，C 组核对每场景：

- `craft_carrier.concrete_anchor` 是否在 `scenes/scene_{id}.md` 中以可识别形式出现（物件名 / 动作 / 文体切换）
- `craft_carrier.replaces` 中标注"应被替代的解释段"是否真的被替代（如果正文中仍有解释段，carrier 与解释段并存 = 设计偏离）
- 多场景共用同一类 carrier（如多场景共用"物件承载"）时，物件具体性是否保持（一种物件持续出现 vs 每场都临时换物件）
- 排除项：carrier 在正文中以隐性变体出现（同义物件、动作变体、文体微调）且仍承担同一表意功能，不算失守；`craft_carrier` 字段缺省（Phase 5 未声明）时本项不触发

参考：《冰与火之歌Ⅰ》瑟曦撕遗嘱（scene 14）— 物件承载持续到后续场景仍以"撕遗嘱"为权力锚点。

**E. narrator_distance 跨场景对齐（narrator_distance_cross_scene）**

若 Phase 5 `scene_card` 含 `narrator_distance` 字段，C 组核对：

- 同一 POV 角色在不同场景的 narrator_distance 切换是否有结构理由（如回忆场景从 intimate 切到 reminiscing 是合理的）
- 同一场景内 narrator_distance 是否被 writer 悄然切换（writer 把 archival_zero 写成 intimate = 失守）
- narrator_distance 漂移会被 B 组 § 3.A 捕到，但 C 组的视角是"是否与设计一致"——若 Phase 5 已明示 distance 选择，writer 偏离即是 pipeline_crosscheck 类问题
- 排除项：切换有 Phase 5 明示的结构理由（回忆 / 视角转移 / 章节切口）且与设计一致；`narrator_distance` 字段缺省时本项不触发

参考：《2666》场景 S11 — 全章 archival_zero；正文若混入叙述者反应即偏离。

**F. INS-* carrier 闭环**

读取 `pipeline/inspiration_ledger.yaml`（如存在），对每个 `status ∈ {accepted, bound}` 的 INS-* 做闭环检测。检测逻辑与 5 类 subkind 见 story-review/SKILL.md 的 `## INS-* carrier 可见性 / inference path 检测` 段；本子段产出的 finding 全部归入本维度（`dimension=pipeline_crosscheck`），subkind 取 5 类 INS-* code 之一。

**扫描要点**：

- `project_encoding[].field_path` 是否在对应 phase YAML 真实引用
- `disclosure_ladder[].carrier` 是否在对应 `scene_{sid}.md` 正文出现
- carrier 是否承担了 `reader_inference` 描述的信息变化
- `do_not_explain` 禁项是否被触发
- `archetype_target_slug` 对应角色的 phase2 `voice_traits` / `recognition_path` 是否体现 archetype 学习面

**字段缺席降级**：ledger 文件不存在 / 所有 INS-* status=candidate → 整段跳过，不报错。

**注意**：正文-设计偏离检查的目的不是要求正文机械遵循设计——创作过程中的有机偏离是正常的。只标记**无意的矛盾**，而非**有意的演化**。判断标准：如果偏离使故事更好，那它是演化；如果偏离导致逻辑漏洞，那它是矛盾。

## 输出

按 [`output-schema.md`](output-schema.md) 格式返回。

- 时间线和世界观维度的 `source` 为 `"story"`
- 正文-设计偏离的 `source` 为 `"pipeline"`，`location` 引用正文中的偏离段落，`contradiction_pair` 引用对应的设计文档字段
- `scene_id` 在全文级问题中为 `null`；如果能定位到具体场景则填写
