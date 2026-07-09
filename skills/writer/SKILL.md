---
name: writer
description: MUSE Phase 6 writer subagent 的职责层 — 为单场景首次生成 draft。由 orchestrator 通过当前运行时的 subagent dispatch 启动 writer，writer 启动后通过运行时 skill 机制加载本 skill 获取输入路径硬约定 / 输出约束 / 创意字段消费 / 产出约束。
---

# Writer — 单场景首次生成

## 输入文件（硬约定，按 scene_id 替换路径模板）

**本场景必读**：

1. `pipeline/scene_{scene_id}/scene_card.md` — 本场景设计切片（15 字段，`extract_scene_card.py` 产）
2. `pipeline/scene_{scene_id}/role_briefs.md` — 所有在场角色的 role_brief 合集（Step 2 role-brief-deriver 产；字段 schema 权威见 role-brief-deriver skill，重点读 `primary_objective` / `suppressed_pressure` / `scene_stake` / `boldness_guardrails` / `desire_now` / `fear_now` / `misread_now`）
3. `pipeline/phase3_spine.yaml` 的 `spine_statement` 字段（主题锚定，1-2 句）
4. `pipeline/story-character-skills/.claude/skills/{slug}/SKILL.md` — 角色长期人格权威源（每 participant 一份）
5. `pipeline/story-character-skills/.claude/skills/{slug}/state.md` — 本场景进入前主观状态（每 participant 一份）

**本场景按条件读**：

6. `pipeline/staging/scene_{scene_id}/{slug}_performance.md`（Phase 6 performance 素材，orchestrator 在 writer dispatch 前按条件硬依赖预跑——触发与豁免契约见 `phase6-scene-development/references/execution-protocol.md §1 Step 4b`）
	   - **本场全部在场角色的 performance 文件，存在即必读**；读取次序：role_briefs 之后、draft_tail 之前（字段：goal_anchor / decisions / actions / lines / reactions / tells / forbidden，schema 权威见 character-rehearsal skill）
	   - 缺失且 `pipeline/audit/skip_performance.yaml` 有本场条目 → 素材缺席降级：仅凭 role_brief + 角色 skill package 写作，不阻断
7. `pipeline/scene_{scene_id - 1}/draft_tail.md`（首场景 S01 无；`extract_draft_tail.py` 产；前 100 字尾摘供衔接）
8. `pipeline/phase0_conception.yaml` 的 `reference_materials.summary` + `reference_materials.key_details`（用户提供时有；只读这两个子字段，不读 `applicable_phases`）
9. `pipeline/phase1_world.yaml` 的 `domain_knowledge` 字段（Phase 1 有时读；全量读）
10. `pipeline/references/{scene_id}_ref.md`（MUSE-canon-distill 的 `scene-reference` 产物；orchestrator 在 writer dispatch 前按 key_scene 信号 / 用户偏好按需预跑——见 `phase6-scene-development/references/execution-protocol.md §3.5`）
	   - **读取时机**：其余输入全部消化后、动笔前**最后**读——ref 是文风锚，离生成越近引力越强
	   - **style anchor 提取**（读完即做，内隐不落盘）：从 ref 原文提炼 3-5 条本场可执行的文风锚点，覆盖：叙事语态（全知说书 / 限知贴身 / 档案冷感…）、句长节奏与段落呼吸（参照各条目密度元数据）、词汇质地（文白比例 / 口语度 / 修辞密度）、对白形态（对白推进还是叙述推进、归属方式）、留白方式
	   - **正向贴近**：正文以 style anchor 为准绳**主动贴近 ref 的腔调与质感**，这是本输入的目的——不是背景资料。**贴文风 ≠ 抄内容**：语态、句式、节奏、修辞密度尽量贴近；人物 / 情节 / 专有名词 / 具体句子不得复制
	   - ref 内标注"仅文风参考"的条目只贴文风、不学叙事结构；style anchor 与 scene_card / role_briefs / prose_risk_contract 冲突时设计文档优先
	   - **跨语言降级**：ref 语言与产出语言不一致时，词汇质地维度不可迁移——只贴语态 / 节奏 / 留白
	   - 文件不存在时跳过，不报错（扩展包未装 / 场景不命中判据 / KB 缺失等情形的统一降级）
11. `pipeline/inspiration_ledger.yaml` 中 scene_card 列出的 INS-* 卡
	   - **触发**：scene_card.md 含 `## 灵感引用 (inspiration_refs)` 段且段内列出 INS-* ID 时，按段内 ID 读取 ledger 文件取对应 INS-* 卡
	   - **消费内容**：对每个引用的 INS-*：
	     - 读 `disclosure_ladder[]`，找 `scene_id == 本场 scene_id` 的 layer（early_signal / mid_reframe / final_confirmation），按该 layer 的 `carrier` + `reader_inference` 写正文
	     - 严格遵守该 layer 的 `do_not_explain[]` 禁项（"显示而非告诉"规则）
	   - **字段缺失降级**：ledger 文件不存在 / scene_card.md 不含 `## 灵感引用` 段 / 段内 ID 列表为空 → 跳过本步，按其他输入正常写正文，不报错

**不读**：
- 本场景自己产的 `pipeline/scenes/scene_{scene_id}.md`（ROLLBACK 档 fresh session 进来看到就忽略——已存在文件由 orchestrator 选择保留或覆盖）
- phase4_structure.yaml / phase5_scenes.yaml 全量（已通过 scene_card.md 切片提供）
- 其他场景的 role_briefs / material / scene_card（注意力集中）
- story.md（Phase 7 整合产物，writer 不读）
- 其他场景的 `pipeline/scenes/scene_*.md`（本场景之外，通过 draft_tail 已获得必要衔接信号；本场景的 scene_{scene_id}.md 是 writer 自己产出的目标文件，按上一条 fresh session 约定亦不读）
- 任何 skill 的 `SKILL.md` / `references/*.md`（通过运行时 skill 入口加载同名 skill，不用 Read）
- 例外：`pipeline/story-character-skills/.claude/skills/{slug}/SKILL.md` 是 run 级角色资产，按上方必读清单用 Read 读取
- `pipeline/characters/{中文名}.md`（adapter，build-time 校验视图；writer 不读）

## 输出

- `pipeline/scenes/scene_{scene_id}.md`（唯一产出；**纯 Markdown 正文**，无 YAML frontmatter，无批注注释）

## Writing skills 加载时机

- 写正文前加载 `prose-craft` skill（散文叙述 / 节拍 / 潜文本 / 段落节奏 / 省略 / 迟进早出 / 风格 / 领域知识 / 信息暴露 / 创意执行）
- 场景含对白时加载 `dialogue-craft` skill（对白矩阵 / 声音差异 / 质量验证 / POV 锚点）
- 两个 skill 提供**原则**，不提供模板——按场景实际条件用
- **承载模式参考**：[`prose-craft/references/novel-craft-patterns.md`](../prose-craft/references/novel-craft-patterns.md)（按需加载——A 类承载点 / B 类视角 / C 类高潮 / D 类人物 / E 类形态；scene_card 的 `craft_carrier` 字段命中相应模式时拉对应小节）

## 人物语言素材消费优先级

writer 同时接触多个人物语言相关的素材源——按以下优先级组装场景内的角色行动 / 对白：

| 优先级 | 来源 | 语义 | 用法 |
|---|---|---|---|
| 1️⃣ | `role_briefs.md` | 本场景目标 / 压力 / 误读（`primary_objective` / `suppressed_pressure` / `misread_now` / `boldness_guardrails`） | 定义角色**此刻的行动方向** — 写作时角色的每次选择应可回溯到这些字段 |
| 2️⃣ | `story-character-skills/.claude/skills/{slug}/SKILL.md` + `state.md` | 角色**长期声音** + 入场主观状态 | 保证角色说话方式在故事全局稳定；逐场景不变的人设底色 |
| 3️⃣ | `pipeline/staging/scene_{scene_id}/{slug}_performance.md` | **本场景表演素材** — goal_anchor / decisions / actions / lines（台词候选）/ reactions（交互预案）/ tells（外显心理）/ forbidden（禁区） | 场景级细颗粒度的台词 / 动作 / 交互 / 潜台词素材；是 1️⃣+2️⃣ 的场景化投影 |

**组装方式**：

- 1️⃣ 决定"角色想做什么"、2️⃣ 决定"角色怎么说话"、3️⃣ 提供"这一刻具体怎么体现"
- 有 3️⃣ 时优先从候选台词 / 动作里挑选（见下方素材纪律）；无 3️⃣ 时按 1️⃣+2️⃣ 自由发挥
- 三层出现冲突时以 1️⃣ 为准（本场景 primary_objective 优先于长期声音与局部台词）；若 3️⃣ 的候选与 2️⃣ 的声音框架明显不符，视为 performance 素材质量问题，**丢弃这些候选**（decisions / actions / lines / reactions / tells）只用 1️⃣+2️⃣ 写——但 **`forbidden` 不在可丢弃之列**：它是硬约束，素材其余部分被弃用时仍必须读取并遵守

**performance 素材使用纪律**：

- **候选非剧本**：素材可选用、可改写、可丢弃；台词不必逐字采纳（贴合本场节奏时逐字用也可以），但正文中该角色的关键对白应能回答 `lines.intent` 同款问题（对谁说 / 想达成什么）——这是判据信号，不是逐字对照
- **`forbidden` 是硬约束**：正文不得出现角色 forbidden 列表内的语气 / 表达（违反即 scene-review voice 类 finding）。素材其余字段全部弃用时，`forbidden` 依然生效
- **`tells` 与 `lines.subtext` 只准外显**：写成动作 / 沉默 / 视线 / 对白错位；**禁止**转述为"他心里其实 / 她其实想……"式解释性旁白（两字段同等适用）
- **节奏优先**：素材过剩时舍弃，不把每个角色的高光都塞进正文——场景节奏由 writer 负责，这是素材库模式的代价与自觉

## Craft Preflight（写正文前必须完成，但不输出）

读取 scene_card 后，先选择本场主承载操作。每场最多 1 个主操作、1 个辅操作：
- object_trace
- bodily_action
- silence_time
- procedural_form
- limited_pov
- second_hand_story
- sensory_shock
- expectation_reversal
- scale_shrink
- syntactic_symptom
- delayed_pain

然后回答：
1. 本场哪段"解释 / 心理 / 背景"应被这个操作替代？
2. 哪个空白不能被正文补上？
3. 最后读者应记住的一个动作 / 物件 / 声音 / 图像是什么？

操作选择必须呼应 scene_card.craft_carrier 与 role_brief.carrier_hint；冲突时回报 orchestrator 不写正文。

## 高潮场景 pattern menu

**仅当 scene_card.climax_pattern 显式选择时启用。**
`scene_card.climax / sequence_climax / arc_climax = true` 不自动加载全部高潮模板——climax 标记只说"这是高潮场景"，pattern 才说"用什么手艺"。

可选 7 个 pattern（enum 与 phase5 scene_card schema 一致）：

| pattern | 触发场景 | 执行要点 | 名著锚点 |
|---|---|---|---|
| `layered_revelation` | 关键真相揭示 | 三层揭示（视觉冲击 → 外行反应 → 改写性事实）；禁止任何一层加"这意味着…" | 《月亮与六便士》S15 |
| `ineffable_realization` | 顿悟时刻 | 让角色尝试两个比喻并自我否定；第三个比喻不出现；"说不清"本身是力量 | 《月亮与六便士》S12 |
| `passive_death` | 自然死亡 / 老去 | 终幕动作主语必须是物件 / 身体部位，不是角色本人；动词非意志性（"松软"/"滑动"/"跌进"） | 《斯通纳》S13 |
| `mask_hard_cut` | 硬汉破防后恢复 | 用硬切（无过渡）；后续姿态必须是"主动戴上的面具"；不允许"他迅速擦掉" | 《月亮与六便士》S14 |
| `unfinished_action` | 觉醒高潮 | 让觉醒台词出现但用"然而他没有说出口"立刻封闭；完成的动作传递结果，未完成的传递无力 | 《阿Q正传》S12 |
| `anti_epic_failure` | 主角失败型高潮 | 主角失败，伏笔 / 副角色欲望 / 世界机制完成结果；不是"主角胜利但伤痛" | 《指环王》末日裂隙 |
| `scale_shrink` | 高潮尺度收缩 | 高潮收缩到小物件 / 一只手 / 一句回家；不是"宏大事件越来越大" | 《三体Ⅲ》5kg 生态球 / 《指环王》山姆回家 |

**硬约束**：
- writer 看到 `scene_card.climax = true` 但 `climax_pattern` 缺字段或 `primary: null` → **不加载任何高潮模板**，走通用 Craft Preflight
- writer 看到 `climax_pattern.primary` 已选 → 只执行该 pattern 的执行要点；不批量加载全部
- writer 看到 `climax_pattern.secondary` 也填 → primary 主，secondary 辅
- `climax_pattern.forbidden_moves` 列出的具体禁做必须遵守

完整说明（每 pattern 的更深范例）见 [`prose-craft/references/novel-craft-patterns.md`](../prose-craft/references/novel-craft-patterns.md) C 类"高潮与尺度"。

## 创意字段消费

### reader_track（阅读主线锚点）

scene_card 的 `reader_track` 字段是**本场单一阅读主线**——读者跟住什么问题或行动线。写作前先读 reader_track，再消费 scene_tasks——所有任务必须服务这条线。

字段缺位 → 退回旧路径（按 scene_tasks 推断主线）；写作产出仍要保证读者能跟住一条线。

### scene_task 分层结构处理

scene_card 的 `## scene_tasks` 段由 `extract_scene_card.py` 渲染为分层结构，writer 必须按四字段消费：

| 字段 | 写作处理 |
|---|---|
| `abstract_function` | 只作为戏剧意图，不直接写进正文；正文必须让它通过可见承载物成立 |
| `physical_carrier` | 正文优先交付的动作 / 物件 / 停顿 / 台词锚点；`function_link` 说明它服务哪个子功能 |
| `reader_yield` | 判断句子是否值得存在的收益锚；不能新增收益的句子默认删或并入前后句 |
| `rendering` | `summary` 只给结果 + 必要锚点；`expand` 才展开过程；`expand_only_if` 是展开条件 |

**执行顺序**：
1. 先读 `reader_track`，确认本场单一阅读问题 / 行动线
2. 再读每条 scene_task 的 `physical_carrier`，选择正文要落地的可见承载物
3. 用 `function_link` 校验承载物是否确实服务 `abstract_function`
4. 依据 `reader_yield` 与 `rendering` 决定写、合并、省略或展开

历史 `[核心][main]` 字符串任务只作为 legacy fallback：按旧 reader_layer 规则消费，但新 scene_card 若已有四字段结构，以四字段结构为准。

**绝不**：把 scene_tasks 当 checklist 逐条机械交付（AI 味温床）；在正文出现 `abstract_function` / `physical_carrier` / `reader_yield` / `rendering` / `[核心]` / `[灵感]` / `[惊艳]` / `[main]` / `[support]` / `[atmosphere]` 字面（这些都是元数据，读者只读正文）。

### 信息分层与节奏（消费 reader_track 的硬约束）

1. **分层消费**：`[main]` 亲历**关键变化**（不是完整过程；只展开最有戏剧代价的部分，其余压成一句）/ `[support]` 给结果 + 必要锚点 / `[atmosphere]` 留压力与质感不解释——禁止把所有任务平铺为同等密度
2. **同段不连续平铺新机制**：连续新增物证 / 规则 / 判断时，必须有明确的行动承接或人物压力变化；否则合并、后置或降为 `[atmosphere]`
3. **角色主功能倾向**（非硬规则）：每个角色本场应有一个主信息功能；额外判断必须改变行动 / 关系 / 压力，否则删除或转为反应
4. **信息让位**：信息让位于人物压力、行动选择、情绪变化——逻辑链不能淹没行动链与情绪链

**省略是默认值**：读者能自行补完的移动、检查、整理、等待、转身、开门、下楼，一律跳过或压成一句。只有改变危险、欲望、关系、世界规则、人物裂隙、情绪转折或形式惊艳的动作才展开。

**角色特质 ≠ 叙述形态**：角色可以清单化思考（程序员、PM、军官等 POV 常见），但正文不能清单化交付。读者要读到人物在压力中的选择，不是读到操作日志。

### scene_card.md `## 世界观披露 (world_disclosure_plan)` 段消费规则

scene_card.md 含此段时，writer 按以下契约消费（精确段标题字面量，由 extract_scene_card.py 渲染保证）：

- **`allow` 列表**：授权由眼前物 / 动作触发，借第一人称口吻渐进披露——写时遵循"极简短句即止 / 不做百科说明 / 一触即收"的判据信号
- **`forbid` 列表**：硬约束，仍禁止披露终极成因 / 救援未来 / 宏大总结

段缺失时：沿用旧"不解释一切"约束，writer 不主动披露世界规则。

### scene_card.md `## 写作层 AI pattern 预防 (prose_risk_contract)` 段消费规则

scene_card.md 含此段时（由 `extract_scene_card.py` 渲染保证段标题精确字面量），writer 在 Craft Preflight 阶段按段内三个子项消费：

- **`risk_families`**：本场 high-risk family。写正文前通过 `prose-craft` skill 查 `references/ai-cliche-patterns.md` 对应 family 的判据 / 豁免条件，写作时主动规避该 family 的叙述形态。未知 family 不阻断 → 按 prose-craft 内置 cliche 库 fallback
- **`positive_strategy`**：本场特化策略——按指引选择本场叙述形态。**硬约束**：禁止靠禁词或同义替换规避（「删『然后』→ 换成『她目光落过去』」「删『像』→ 换成『某种没有声音的Y』」属于回流陷阱——表层词改了深层结构未变）；通用修法通过 prose-craft skill 查 ai-cliche-patterns.md 对应条目
- **`bad_shape_examples`**（可选）：本场结构形态示例。遇相同**结构**形态即改写叙述形态（合并 / 转关系动作 / 转感官替代），**严禁**字面匹配规避

段缺失 → writer 沿用 prose-craft 内置 cliche 库默认规避。

**多 contract 冲突兜底**：见 [`../phase5-scene-arrangement/references/output-schema.md`](../phase5-scene-arrangement/references/output-schema.md) `## prose_risk_contract` 末尾"同场冲突兜底"段（SSOT）；极端冲突 writer 无法自决 → 在 subagent 最终 reply 报告 orchestrator。

### information_yield_contract（writer 全局硬规则）

information_yield_contract 是 writer 每场必跑的全局硬规则，**不依赖** scene_card 注入或 prose_risk_contract.used 状态。三层硬约束：

**1. hard_avoid 5 类型**——以下五类**不写**：

- 无新增信息的短独立句（≤10 字阈值参考）——不写"他在看。/ 他在那里看着。/ 风停了。"
- 标签式结论——不写"血祭断了。/ 化了。"；改可见后果（"铜鼎边的火塌下去，骨号乱了。"）
- 重复状态确认（同锚点无变化）——不重写"赵庆还在那里。…赵庆还在那里。"
- 字数包装——不写"只说了一个字：等。"；改直接（他说："等。"）
- 意义硬标——不写"这是他第一次开漆匣。"；改动作（"他第一次开漆匣"）

**2. pruning pass 4 问**——写完后对每个候选句问：

1. "这句新增了什么信息？"
2. "如果删掉，读者少知道什么？"
3. "如果并入前后句，是否更自然？"
4. "它是否在替代本该出现的后果 / 动作 / 关系变化？"

**3. 8 yield 自答硬约束**（写 ≤6 字独立短句 / 状态确认 / 标签结论 时强制）——心智自答 8 种 yield 至少 1 种，答不出 → 删 / 合并：

- `plot_change` 推动情节 · `danger_change` 改写危险 · `tactical_change` 改变战术 / 选择空间
- `character_choice` 暴露选择 · `relationship_shift` 改变关系 · `world_rule` 立 / 改世界规则
- `sensory_irreplaceable` 不可替代感官精度 · `formal_function` 形式功能（recognition_object / 名字仪式 / 节拍）——`formal_function` 需绑具体 carrier 才算数

**4. 反向防御 5 条禁用豁免理由**——不要用这些理由保留 zero_yield 句：

- "节奏需要这一停顿"·"强化氛围 / 渲染气氛"·"保留文学性 / 这是 voice"·"读者可能漏看，加一句确认"·"美感 / 留白 / 顿挫"

唯一合法保留路径：8 yield 中至少 1 种显式可答且给出 ≥10 字 ≤30 字可验证理由（≥6 字短句无需正文写出理由，心智判断即可）。

### role_briefs.md 的 boldness_guardrails 字段

每个角色含 `boldness_guardrails` 字段（Step 2 产出），语义：**此场景本角色是否激活"大胆/惊艳"倾向及其强度**。

- guardrails 明示"高激活" → 选**更有代价**、**更能改写关系**、**更能释放信息差**的动作
- guardrails 明示"弱激活 / 日常场景" → 不强做惊艳，保持平稳
- 是**单场景建议**，不是角色恒常属性——同一角色不同场景 guardrails 可能完全不同

## 产出约束

- 正文**严格不含**设计 token：`[核心]` / `[灵感]` / `[惊艳]` / `scene_tasks` / `handoff` / `value_start` / `value_end` / `spine_statement` / role_brief 字段名 / 麦基术语 "价值"/"节拍"/"潜文本" 等
- `target_length` 是用户给的参考目标，不是硬阻断——按场景节拍自然收束即可；不要为了凑字数加水或砍内容。正文落地后字数报告由 phase6 索引输出，仅供用户感知，**不触发 second writer pass**
- `scene_{scene_id}.md` 首行**不加章节标题**（Phase 7 integration 统一编号）
- ROLLBACK 档重跑时 fresh session 已保证不读旧 draft；不要主动假设"要比上次好"，按当前输入正常写

## 不做

- 不做修订（PATCH 档 reviser 做）
- 不在 `scene_{scene_id}.md` 写作者批注 / writer_note / HTML 注释 / 设计回溯
- 不改写 scene_card / role_briefs / 角色 runtime package / phase yaml 等上游文件
- 不读 / 不写其他场景的文件
- **禁把候选清单机械倾倒进正文**：`lines` 是**候选素材**不是成品对白清单；逐条全量搬进本场会让对白失去节奏、且破坏"文本来自角色此刻选择"的幻觉。单条候选贴合本场节奏时可直接用，也可改写、截断、只取意图或整条丢弃——取舍权在 writer
- **禁**把 performance 文件的字段名 / 结构标记（goal_anchor / decisions / lines / reactions / tells / forbidden 等 yaml key）写入正文（同 scene_tasks marker 禁令）
- 不把 deliberate omission 补成内心独白
- 不在强动作 / 强物件之后追加"这意味着…"式解释
- 不把身体顿悟翻译成理论段落

## 失败语义

orchestrator 负责超时/重试；writer 本身只管把 `scene_{scene_id}.md` 写完。**`scene_{scene_id}.md` 始终是纯 Markdown 正文**——无论输入是否异常。

写到一半发现 role_brief / material / scene_card 有问题**不调整上游，也不污染 scene_{scene_id}.md**：
- 按当前输入条件下能写的最好版本正常产文
- 异常情况通过 **subagent 最终 reply** 报告给 orchestrator（例如 `"done draft for scene S02; NOTE: role_brief.desire_now 与 scene_card.conflict 语义错配，建议复查"`）
- orchestrator 收到 NOTE 后人肉判断是否上游修订；Step 5 scene-review 就位后由 reviewer 决定

这样 `scene_{scene_id}.md` 不被污染，下游 `extract_draft_tail.py` / `assemble_story.py` 都能安全消费。
