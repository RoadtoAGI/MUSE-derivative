# A 组审查：微观语言 + 反 AI 化 + reframing 独白判读

> 本子文件承载 A 组审查中"句级 / 段级语言细节"的诊断规则：反 AI 化失守检查、微观语言错配（含 hot zone 判读、reader-visible damage 原则、修订方向）、以及 reframing 独白判读（盲读 reader-review 报症状时的二次诊断）。主表逐项检查见 [`A_aesthetic.md`](A_aesthetic.md)。

## §1bis 反 AI 化失守检查（与 ai-cliche-patterns.md 新 5 条联动）

针对 [`prose-craft/references/ai-cliche-patterns.md`](../../prose-craft/references/ai-cliche-patterns.md) 中新增的 narrator_self_corrects / emotion_naming_under_face_loss / music_doesnt_stop / care_tone_masking_violence / decline_without_numbers 五条，A 组逐场景扫描：

| 检测项 | 触发场景 | 报告落点（`dimension: ai_pattern` + subkind） |
|---|---|---|
| 叙述者过度自省 | 第一人称叙述场景，叙述者在道德灰区 | `subkind: narrator_self_corrects` |
| 情感命名破防场景 | 高自尊 / 反派 / 硬汉首次脆弱 | `subkind: emotion_naming_under_face_loss` |
| 暴力前声景中断 | 暴力 / 灾难高潮场景 | `subkind: music_doesnt_stop` |
| 施害方语气标签化 | 长期欺骗 / 酷刑场景 | `subkind: care_tone_masking_violence` |
| 衰落形容词化 | 现实主义场景含可量化衰落 | `subkind: decline_without_numbers` |

每条 finding 同样需要 `evidence_quote` 原句 + 一句失败原因；reviser 接 PATCH 时按对应模式的"反 AI 默认"做减法。

## §7 微观语言错配

扫描单句级"看似有文气但不成立"的问题。命中时 `dimension: micro_language`，并填 `subkind`：

| subkind | 判据 | 例 |
|---|---|---|
| `false_literary_diction` | 修饰语与被修饰动作不搭，句子只剩假文气 | "人群退得极轻" |
| `sensory_mismatch` | 感官通道错接，触/听/视觉强度混用且无转换 | "那一退极轻，却刺眼" |
| `abstract_judgment_without_action` | 用抽象判断替代可见动作或具体反应 | "他显得复杂而沉重" |
| `stock_speech_tag` | 用库存语气标签（"淡淡道 / 声音不高 / 低声道 / 平静道 / 沉声道 / 悠悠道"等）替代角色实际语气、动作压力或对白本身——**删去后信息不损失**即触发 | "他淡淡道：「刀断了，人还在。」" / "杨过声音不高，「这条路给他退……」" |
| `weak_character_expression` | 人物声音 / 神情 / 动作 / 心理描写附近用弱否定、虚词、副词或状态标签替代具体动作、压力或对白效果——**删去或改成正向可感细节后信息不损失**才触发 | "声音仍平" / "表情没有变化" / "脚步不慢" / "她只是看着" / "不是问句" |

**只报影响阅读的句子**：单个生僻搭配若语义清楚、符合角色感知，不报。每条 finding 必须给 `evidence_quote` 原句和一句失败原因，方便 scene-reviewer 直接转 patch。

**`stock_speech_tag` 与 dialogue_lint S3 信号联动**：dialogue_lint S3 已加 `STOCK_SPEECH_TAG` 正则信号（同名 enum，confidence=medium）；A 组消费 lint hits 时按"删去后信息不损失"原则人工核实——某角色一贯的"低声道"刻画 / 用于场景气氛而非语气替代时**不报**；典型替代型才报为 `dimension: micro_language, subkind: stock_speech_tag`。

**`weak_character_expression` 与 dialogue_lint S3 信号联动**：dialogue_lint S3 的 `weak_character_expression_candidate` 只是候选提示，不是定罪。candidate 分两档：

- **confidence=medium**——有锚点（声音/神情/动作/心中等身体部位或感官名词），如"声音仍平 / 表情没有变化 / 脚步不慢 / 心中仍想"
- **confidence=low**——仅代词锚点（"他/她 + 弱副词 + 弱动词"），宽召回兜底

每条 candidate 还附 `near_dialogue: bool`——命中行 ± 2 行内是否有对白引号。

**Hot zone 加权（near_dialogue=true）**：人物对白前后 1-2 行是 weak_character_expression 高发区——典型场景：

- 对白前后引导句："她声音平" / "他低声道" / "声音短硬"
- 同一人物连续两句对白之间的垫句："她没有动" / "神色不变" / "只是看着"
- 对白后补态度："不是问句" / "语气淡淡" / "话里没有怒气"

根因：模型用"状态标签"充当节奏刹车，避免写具体动作 / 物件反应 / 空间压力 / 对方反应。Hot zone 是 A 组判读优先级信号，不是定罪信号——`near_dialogue=true` 默认提高怀疑级别，但仍走下方判读流程。

### 判读流程（reader-visible damage）

**总原则**：报的是"已经在伤害读者体验的弱标签"，不是"看起来可疑的句子"。判据是：**这句话在做 attribution 之外的事吗？** 在做——不报；不在做——报。把"模糊可疑"留给 reviser 自由裁量会让 reviser 机械替换、把一个坏标签换成另一个坏标签；让 A 组只报真伤害读者的，reviser 才能集中处理实质问题。

**Step 1 — 范畴判定**：原句是否属于"人物声音 / 神情 / 动作 / 心理描写"？

不属于范畴的 candidate 视为 **lint 误报**，A 组**不报**：

- **主语不是人物**：景物 / 环境 / 物件——"水鸟掠翅的声音" / "册页翻动的声音" / "门没开" / "地上没有血迹"
- **否定承担信息纠错**：时间地点对比、事实辨析——"公审是今夜，不是明晨"
- **否定承担逻辑反驳**：对辩驳类对白——"这柄刀不是我塞到你们手里" / "他喝的不是我的方"

→ 进入 Step 2 才看是否伤害读者。

**Step 2 — 功能判定**：句子在做 attribution 之外的事吗？

**不报**（句子在承载具体叙事功能）：

- **承担转折，紧跟正向具体动作链**："接过茶，**却没饮**，**望着**远去的背影" / "**没有看他**，一直**盯着**船绳"
- **气氛由具体动作 / 物件 / 对手反应承载**（不混入状态标签）："她说完，屋里没人接话，灯芯爆了一下" / "他听完，把杯子推到桌中央，没再开口"
- **角色一贯刻画在长程场景中已建立**：第一次出现可保留，后续重复同一标签则报
- **删除后会让句意残缺或节奏断裂**：句子是上下文衔接的必要部件

**报**（句子是空状态标签、删去后信息不损失）：

- **纯库存语气标签**："淡淡道 / 沉声道 / 悠悠道 / 声音不高 / 语气平静" — 后续无具体动作 / 物件 / 反应承接
- **抽象状态替代具体反应**："声音仍平 / 表情没有变化 / 不是问句 / 没有起伏" — 删去后信息无损
- **同义堆叠**："她声音很轻，几乎听不见，又像是在自语" — 三句都说"轻"，无新信息

判定时问：**reviser 删去这句，读者会损失什么？** 答得出具体内容（节拍、气氛锚点、关系信号）→ 不报；答不出 → 报。

> 注：库存声音标签（"声音平 / 沉声道 / 淡淡道"）后接气氛句不构成"承担节奏锚点"——气氛若是后半句具体化承载的，前半句的状态标签仍是空标签，**报**。前半句应直接删，由后半句独立承担。

### 修订方向（写进 finding 的 `suggestion`）

保持**减法**——优先建议删除而非替换。明确告诉 reviser 不要把一个状态标签换成另一个状态标签（"声音更轻"、"语气更冷" 同质替换 = 没修）。承载节奏的合法手段：具体动作、物件反应、对方反应、停顿、视线落点；具体替换由 reviser 按上下文决定，A 组只标方向。

## §reframing 独白判读

> 消费 reader-review "长独白可能在 reframing" 症状时。

reader-review 报"长独白可能在 reframing"症状时（盲读契约约束：reader-review 只给症状不下判罪），A 组接症状后做技术判读：消费 `scene_card.craft_carrier` / `scene_card.pov_constraint` / `scene_card.omission_plan` / `scene_card.narrator_distance` 等设计字段，按下表 4 项判据判读，三项以上为"是" → 标 reframing 独白（保留，不报 AI 注水；并触发 [`A_aesthetic-carrier.md`](A_aesthetic-carrier.md) §0 豁免第 4 类）：

| 判据 | reframing 独白（保留）| 注水独白（出戏）|
|---|---|---|
| 是否改变读者对前文的理解 | 是 — 重新编码已读情节 | 否 — 只是重复 |
| 是否引入新的范畴 / 维度 | 是（从匿名"他们"到具体"我"等）| 否 |
| 结尾是否落到沉默 / 物理动作 / 反应缺失 | 是 — 沉默是最佳反应 | 否 — 接对白或下一场 |
| 是否在让读者认知一次性转变 | 是 — 独白即场景 | 否 — 独白是动作的填料 |

**判读原料**：
- 第 1/2/4 项主要看 scene 上下文 + scene_card 设计意图（独白前后读者对前文的理解差异、是否引入新范畴、独白后是否带读者完成一次认知转变）
- 第 3 项可直接核 scene_card 字段：若 `craft_carrier.type` 标明 reframing 类承载、`omission_plan` 声明独白后不接解释、`narrator_distance.mode` 为 `archival_zero` / `unreliable_first` 等冷感模式，独白结尾落沉默 / 物理动作 / 反应缺失就更易判"是"

**输出处理**：
- 三项以上"是" → 不写 finding；若 reader-review 已报症状，A 组在 lint 元数据中标记"reframing 豁免命中（参 [`A_aesthetic-carrier.md`](A_aesthetic-carrier.md) §0 第 4 类）"，reviser 不动该独白
- 三项以下"是" → 写 finding（`dimension: ai_pattern`，`subkind: monologue_padding`），reviser 走"砍独白 / 改场景"PATCH

参考：《冰与火之歌Ⅳ》场景 S06 — 梅里巴德修士独白满足 4 项中 3 项以上 = reframing；reader-review 报"长独白可能在 reframing"症状，A 组判保留不报。
