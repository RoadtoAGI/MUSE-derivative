---
name: scene-review
description: MUSE Phase 6 scene-reviewer subagent 的职责层 — 场景级四档分流决策（PASS / PATCH / ROLLBACK / REWRITE）。吃 pipeline/scenes/scene_{id}.md + scene_card.md + A findings（必读）+ L1 lint report（语境信号；ai_filler 病灶修复由机器通道接管，lint hit 不进 patch_directive）；B/C findings 按 adaptive dispatch（文件存在则筛 scene_id 读取，缺席不阻断）。产 scene_{id}.yaml（verdict 字段 = 单一权威源）；PATCH 档额外产 patch_directive.yaml（source=scene_review）喂 Step 4.5 reviser。required input 缺失由 orchestrator input_gate 写 ESCALATED，见 phase6-scene-development execution-protocol §1.5。
---

# Scene Review — 场景级四档分流决策

## 输入文件（硬约定）

> 本 subagent **被 dispatch 时假定 required input 全部在场**。缺失输入由 orchestrator input_gate 写 `ESCALATED` 降级 yaml；schema 与清理协议见 `phase6-scene-development/references/execution-protocol.md §1.5`。

**必读**：

1. `pipeline/scenes/scene_{scene_id}.md` — 待评审的 scene 正文（由 writer 或上一轮 reviser 产）
2. `pipeline/scene_{scene_id}/scene_card.md` — Phase 5 设计意图（value_start / value_end / scene_tasks / handoff）
3. `pipeline/review/A_aesthetic.yaml` — A 审美组 findings（筛 `scene_id == 本场景` 的条目）
4. L1 脚本 lint 报告（三份显式路径；**不要**用 glob，按 scene_id 精确读，避免误匹配其他场景或 future 新增 lint）：
   - `pipeline/review/lint/{scene_id}.ai_filler.yaml`（S1：口癖 / Markdown / 排比 / 关联词）
   - `pipeline/review/lint/{scene_id}.lexical_stats.yaml`（S2：副词 / TTR / 感官平衡 / 高频词——读 `density.*.imbalanced/overuse/too_low`）
   - `pipeline/review/lint/{scene_id}.dialogue.yaml`（S3：纯台词 / 指代 / 模板说话动词 / 孤立说话动作）
   - `pipeline/review/lint/{scene_id}.density_vs_ref.yaml`（**条件读**：仅 ref 场景且 orchestrator 跑了对齐校验时存在，缺失不阻断。读 `verdict` 字段——`SIGNIFICANT_DEVIATION` 且场景结构无正当理由时（题材性短切 / 纯对白段按 prose-craft ai-cliche E 类豁免先行核对）作为 PATCH 档的密度偏离信号并入 findings 翻译，不单独成档）
   > ai_filler 报告在本 skill 内只作两用：判叙事档位时的语境信号 + M 级 objection 素材（见下方"机器通道分工与 M 级 objection 窄门"）。ai_filler 病灶的修复指令由机器通道脚本直接生成，不经你翻译；dialogue / lexical_stats 仍按下方各段语义判读。

**按需读**（adaptive：B/C 在本轮 dispatch 了才存在；存在则读，scene_id 命中本场景的 finding 才考虑；缺失不阻断）：

5. `pipeline/review/B_narrative_consistency.yaml` — B 叙事一致性组 findings（筛 `scene_id == 本场景`；**`scene_id: null` 的条目跳过**）
6. `pipeline/review/C_structural_consistency.yaml` — C 结构一致性组 findings（同 B 组规则）

**按条件读**：
- `pipeline/scene_{scene_id}/role_briefs.md` — 仅在 A 组 voice_consistency finding 涉及本场景角色时读
- `pipeline/staging/scene_{scene_id}/{slug}_performance.md` — 存在才读，缺失不阻断。两个用途：① 核对正文是否出现某角色 `forbidden` 列表内的语气 / 表达——命中即 voice 类 finding；② 声音区分度判读以 performance 素材（lines / tells / forbidden）为证据源

**不读**：
- 其他场景的 findings（除非 B/C 给的条目明确引用本场景）
- phase0-5 yaml 全量（scene_card + findings 应自含足够上下文）
- 本场景之前的 `scene_{id}.yaml`（fresh session 约定；且若存在则走幂等前置 ESCALATED，不进入评审）
- 任何 skill 的 SKILL.md / references（通过运行时 skill 入口加载同名 skill，不用 Read）

## 评审模式（首次 vs post-revision）

scene-reviewer 有**两种 dispatch 模式**，由 orchestrator dispatch prompt 关键字决定：

| 模式 | 触发关键字 | 目标产物 | 幂等锚点 | 触发场景 |
|---|---|---|---|---|
| 首次评审 | 默认（无 post-revision/post-rewrite 关键字） | `pipeline/review/scene_{id}.yaml` | 同上 | per-scene loop 后 Step 5 第一次 dispatch |
| post-revision review | dispatch prompt 含 "post-revision" 或 "post-rewrite" | `pipeline/review/scene_{id}.post_revision.yaml` | 同上（**不**检查 `scene_{id}.yaml`——首次产物保留） | PATCH 档 reviser publish 后 / ROLLBACK 档 writer 重写 publish 后（与 PATCH 分支对称）|

**post-revision 模式必读**：review schema（三层 gate）/ gate 判定语义 / superficial_patch_failed 检测 / pattern_migration 判定纪律 / PASS 准入硬协议全部在 [references/post-revision-review.md](references/post-revision-review.md)，post-revision dispatch 启动时先 Read 该文件再开始评审；首次评审模式不读。

## 幂等前置检查（启动第一步·硬约定）

```
# 首次评审模式
verdict_path = pipeline/review/scene_{scene_id}.yaml

# post-revision review 模式（dispatch prompt 含 "post-revision" / "post-rewrite"）
verdict_path = pipeline/review/scene_{scene_id}.post_revision.yaml

if verdict_path.exists():
    Task reply: "ESCALATED(already_reviewed); {scene_id} 已评审"
    不再产任何文件，不覆盖 verdict 或 patch_directive
    return
```

锚点选择理由：目标 verdict yaml 是所有 scene-reviewer 档（PASS / PATCH / ROLLBACK / REWRITE）的统一产出，能覆盖所有档的"已评审"状态——不像 `patch_directive.yaml` 只在 PATCH 档产，作锚点无法覆盖其余档。

`verdict_source_conflict` / `verdict_missing` 触发重派时，**orchestrator 先主动删** `verdict_path` 再 dispatch fresh session——scene-reviewer 本身不感知"是否重派"，只看锚点存在性。

**降级 yaml 让位**：当现存 `verdict_path` 是 `written_by: orchestrator_input_gate` + `verdict: ESCALATED` 的 input gate 降级 yaml 时，**orchestrator 在 dispatch 前**已**原子移动**该 yaml 到 `pipeline/review/scene_{id}.input_gate.yaml`（保留 audit），所以 scene-reviewer 启动时 `verdict_path` **不存在**，幂等前置正常通过。scene-reviewer 自身**不感知**降级 yaml 让位逻辑——这是 orchestrator 的责任（详见 `phase6-scene-development/references/execution-protocol.md §1.5` Step 2.5）。

## scene_id=null 全文级 finding 路由规则

B/C 组的 `scene_id: null` finding（全文级问题，如 `narrative_style` 跨场景漂移 / `pipeline_crosscheck` 设计矛盾 / `timeline_plot` 跨场景时序）**不进入本 scene-review 的输入**。

全局路由由 **orchestrator** 处理：
- orchestrator 聚合 `scene_id=null` finding 到 `pipeline/review/global_findings.yaml`
- 若全局有 CRITICAL 级 finding → orchestrator 按优先级决定全局动作（升级人工 / 回退 Phase 5 以上）
- **两层并行**：全局问题不阻止单场景 scene-review 继续产局部 verdict——局部信息自带价值（后续 orchestrator 汇总决策用）

你只管能定位到本场景 scene_id 的 finding，不尝试归属全文级问题。

## 四档分流判据（原则性）

| 档 | 判据 | 后续 | 来源 |
|---|---|---|---|
| **PASS** | 无 CRITICAL 级，minor 占多数；scene value_change 与 scene_card 设计一致（读 scene_card 的 value_start/value_end） | orchestrator 跳过修订；进 Step 7 整合 | scene-reviewer |
| **PATCH** | 有 major，**但位置可定位、方向明确、减法可解**；**不涉及**设计事实偏离 / 人物 OOC / 价值变化方向错反 / 场景整体节奏崩塌；**且无 C/B blocker** | 产 `patch_directive.yaml` → reviser 接线 | scene-reviewer |
| **ROLLBACK** | scene_card 设计事实偏离 / 人物 OOC / 价值变化方向错反 / 场景整体节奏崩塌；**或** PATCH 定点修无法覆盖；**或** 存在 C `pipeline_crosscheck` / B `characterization` blocker | orchestrator 派 writer fresh session **重写本场景**（不回上游） | scene-reviewer |
| **REWRITE** | 问题涉及 Phase 3-5 设计层缺陷（脊椎 / 结构 / 场景编排本身错） | orchestrator 升级人工，回退 Phase 5 以上 | scene-reviewer |
input 缺失不属于本 subagent 分流档；orchestrator input_gate 写 `ESCALATED`，本 subagent 永不在主体 yaml 中写 `verdict=ESCALATED`。

**硬约定**：
- **C 组 `pipeline_crosscheck` / `timeline_plot` / `world_building` 出现 blocker** → **不得定 PATCH**，至少 ROLLBACK
- **B 组 `characterization` 出现 blocker**（人物 OOC / 记忆断裂 / 知识矛盾） → **不得定 PATCH**，至少 ROLLBACK
- 不硬编码阈值——判读"blocker / major / minor"由你对 finding `issue` 字段语义+严重度综合判
- finding 自带 `severity` 字段时（story-review output-schema 枚举 `CRITICAL` / `IMPORTANT` / `INFO`）作判读**起点**：CRITICAL 从 blocker 起判、INFO 从 minor 起判、字段缺省按 IMPORTANT 从 major 起判；语义判读可升降——字段是输入不是结论

## 判档算法决策树（含证据门槛）

前提：lint 命中只是定位风险，修订目标是消除该 span 的 AI 叙述形态。

## 机器通道分工与 M 级 objection 窄门

ai_filler 病灶按家族分级主权处理，你没有豁免权：

| 级 | 覆盖 | 你的动作 |
|---|---|---|
| S | high / catastrophic cluster、hard cliche 命中 | 无——机器指令直接派发修复，不需要你确认，也不接受豁免 |
| M | medium 级语义 heuristic cluster | 默认也走机器修复；你**可以**对个别 cluster 提交 objection（下方窄门） |
| L | 孤立 low / advisory | 无——只入台账，不修 |

**M 级 objection 窄门**（唯一放行申请通道，脚本终判）：

- 只允许 **cluster 级** objection（禁逐 hit）；对象必须是 `pipeline/review/{scene_id}.machine_directive.yaml` 中 `level: M` 的 entry
- 落盘 `pipeline/review/{scene_id}.machine_objection.yaml`：

```yaml
scene_id: S02
objections:                    # 全场 ≤2 条、同 family ≤1 条，超额条目会被脚本忽略
  - target_entry_id: S02-silence_pause_cliche-2
    family: silence_pause_cliche
    device_claim: naked_line   # 必须是本场景 phase5_scenes.yaml literary_device 已声明的装置
    evidence_quote: "≥10 字正文原句，精确截取"
    function_claim: "≤50 字，说明该形态承载的具体功能"
```

- 生效条件全部由脚本验算（family 白名单 / 装置已声明且预算覆盖 / 证据命中正文）；你写完文件即结束，**不等待、不复核、不在 verdict 里预设 objection 结果**
- `function_claim` 禁用不可证伪表述："节奏需要停顿" / "强化氛围" / "保留文学性 / 这是 voice" / "读者可能漏看" / "美感 / 留白 / 顿挫"——写具体承载功能，否则脚本按证据不齐驳回
- 没有值得 objection 的 M 级 entry → 不写该文件（缺文件 = 无 objection，合法常态）

scene-reviewer 读：A/B/C findings + scene_card。判档只基于**叙事 findings**（A 组语义维度 / B / C / prose_risk_contract violation / dialogue·lexical 联动信号）——ai_filler 病灶不参与你的 PATCH 翻译，它们有自己的修复通道；你只在判"场景整体是否成立"（ROLLBACK / REWRITE）时把 ai_filler 报告当语境参考。

**信息过载分流**（reader-review §10 / A 组报"信息过载"型 finding 时）：

scene-reviewer 读 `scene_card.reader_track`，对照正文判 reader 是否能跟住主线。按现象分流：

| 现象 | 档位 |
|---|---|
| 少量解释句、重复线索、局部物证过密——可由 reviser 删几句降密度 | PATCH |
| reader_track 失焦、角色轮流交付专业结论、多机制同等展开（main 层超载） | **ROLLBACK** |
| 场景目标和信息结构整体错位（reader_track 与 scene_tasks main 任务无法对齐） | **REWRITE** |

scene-reviewer 只读 `scene_card.reader_track`，**不**重新解释 Phase 3 / Phase 4 字段——分流决策基于 A/B/C + lint + scene_card，不上溯设计层。

## 承载完整性信号（与 craft_carrier / narrator_distance 联动）

A 组 §11 输出的 `carrier_*` finding 与 B 组 narrator_distance 漂移 finding 走专有判档路径——这些信号涉及"设计与正文偏离"，**不**走通用 PATCH/ROLLBACK 启发式，而是按 `patch_kind` 直接绑定档位：

| 信号 | 现象 | 档位 | patch_kind |
|---|---|---|---|
| `carrier_then_explain` | carrier 出现并完成意义后，正文又解释一遍 | PATCH | `carrier_then_explain` |
| `omission_violated` | scene_card 声明 `omission_plan`，正文偏要解释 | PATCH | `omission_violated` |
| `omission_filled_in` | writer 把名著式留白填实了 | PATCH | `omission_filled_in` |
| `carrier_missing` | scene_card 声明 carrier，正文找不到 anchor | **ROLLBACK** | `carrier_missing`（设计与正文偏离，超出定点修范围） |
| `narrator_distance_global_drift` | narrator_distance 跨场景漂移 / 场景内基调反复跳 | **ROLLBACK** | `narrator_distance_global_drift`（场景整体节奏问题，非局部） |

完整 enum + 各 patch_kind 的修订方向见单一来源 [`../revision/references/patch-kind-registry.md`](../revision/references/patch-kind-registry.md)。scene-reviewer 写 patch_kind 时按 registry 的 PATCH 类填；若 finding 属于 ROLLBACK 类（registry `requires_rollback_reason` 段）→ 直接定 ROLLBACK 档，**不**写 patch_directive。

## prose_risk_contract compliance check

scene_card 含 `## 写作层 AI pattern 预防 (prose_risk_contract)` 段且 `used=true` 时（schema 见 [`../phase5-scene-arrangement/references/output-schema.md`](../phase5-scene-arrangement/references/output-schema.md) `## prose_risk_contract`），scene-reviewer 把 contract 当审阅闭环的语义上游：读 contract 后比对正文，正文残留 contract `risk_families` 命中 family 的 pattern → 标 `source: prose_risk_contract_violation`（区别于 lint finding / A 组 finding），写入 finding 的 `issue` 描述（让下游 reviser 通过 patch_directive 看到这是 writer 未遵守 contract，非新发现）。

severity 按密度判（描述性）：单点轻度残留 → `major`（PATCH）；同 span 多 family 共现 / 全场反复同 family 命中 → `blocker`（ROLLBACK）；全场反复多 family 命中 + scene_card 已声明 `used=true` → ROLLBACK。

**PATCH 档契约**（用现有 patch_directive schema，不引入新字段）：

- `issue`：把 contract `risk_families` 命中信息写入（如"contract 声明 risk_families=`动作清单化`，本 patch 段落仍出现该 family 形态：'去 A，去 B' 连续 3 拍"）
- `suggested_action`：把 contract `positive_strategy` / `bad_shape_examples` 翻译成本 patch 的修订指引（如"按 contract positive_strategy 把连续动作合并到关系压力变化点；本 patch 段落具体改：删两个流水动作 + 保留一个有关系变化的动作"）
- 不引入新字段——保持 schema 闭合在现有 patch_directive 的 `issue` / `suggested_action`

边界：

- 缺段 → 不做 compliance check，按通用四档分流走
- scene-reviewer 不修 contract 本身——contract 本身有误（family 命名错 / positive_strategy 无意义）→ 升 REWRITE 回 Phase 5
- contract violation finding 不替代 lint / A 组 finding——三者可并存

## 低读者收益动作链分流

scene-reviewer 不问动作是否真实，只问动作是否值得读者完整阅读。凡是没有新增危险、欲望、关系、世界规则、人物裂隙、情绪转折或形式惊艳的动作链，优先压缩或删除。

**判档信号（信号词，无句数阈值）**：

| 现象 | 档位 |
|---|---|
| 少量机械过渡动作，局部减法即可清 | PATCH |
| 形成可识别的低收益链（同构句式连续呈现），需压成结果 + 锚点 | PATCH |
| 主戏被库存 / 路线 / 检查动作吞没，核心戏剧变化不可见 | ROLLBACK |
| 场景设计目标本身只剩搜集 / 移动 / 说明 / 盘点，无戏剧变化 | REWRITE |

**PATCH 档的修订方向必须是减法**：写清"压缩目标 / 保留项 / 删除项"。禁止只要求"写得更生动"，也不要落具体句数硬阈值。

**协议层不变**：本规则上游信号来自 A 组 §6 段级判读（A 组主链路）；reader-review finding 由 Phase 7 的 manuscript-reviser（manuscript-revision 职责层）消费，scene-review **不**消费 reader-review。下方「豁免后处理」段描述的是 manuscript-reviser 消费 reader-review finding 前的豁免过滤逻辑，由 manuscript-reviser 执行，scene-reviewer 不在运行时介入。

## 豁免后处理（消费 reader-review finding 时）

reader-review 是盲读体验代理人，不知道 scene_card 设计意图。manuscript-reviser 拿到 reader-review 的"出戏 / 反应过淡 / 信息不足 / 心理空白"类 finding 后，对照 [`prose-craft/references/ai-cliche-patterns.md`](../prose-craft/references/ai-cliche-patterns.md) §"名著式合法手法豁免"清单，按 4 类前置过滤：

1. 该位置是否对应 `scene_card.pov_constraint.intentional_blind_spot` → 是 = 豁免，不报
2. 该位置是否对应 `scene_card.omission_plan` → 是 = 豁免，不报
3. 该位置是否对应 `scene_card.narrator_distance` 的合法选择（`archival_zero` / `unreliable_first` 等）→ 是 = 豁免，不报
4. 该长独白是否满足 reframing 三项以上（详见 [`story-review/references/A_aesthetic-micro_language.md`](../story-review/references/A_aesthetic-micro_language.md#reframing-独白判读) §reframing 独白判读）→ 是 = 豁免，不报

四类都过不了 → reader-review 的 finding 由 manuscript-reviser 按通常规则定档（PATCH / ROLLBACK / REWRITE）并执行修订。

**硬约定**：豁免要求 scene_card 字段**显式声明**（不允许 manuscript-reviser 脑补"这是名著手法"）。scene_card 漏标但正文出现合法名著手法时，仍报上去——orchestrator 决定是补 phase5 字段（ROLLBACK 回 Phase 5）还是 PATCH 修正，不在本层吞掉。

## 输出

### 1. `pipeline/review/scene_{scene_id}.yaml`（所有档必产）

**scene-reviewer 产物 schema**（input 全在场时由 subagent 写）：

```yaml
scene_id: S01
verdict: PASS | PATCH | ROLLBACK | REWRITE        # scene-reviewer 永不写 ESCALATED
review_incomplete: false                          # scene-reviewer 始终 false
missing_inputs: []                                # scene-reviewer 始终空
written_by: scene-reviewer                        # 标注产出来源
rationale: |
  (3-5 句说明为什么这一档；引用最关键的 1-3 条 finding。
   若 ROLLBACK/REWRITE，说明是哪个维度触发的升档硬约定)

findings_summary:
  total: 7
  by_source:
    lint: 3          # L1 脚本
    A: 3             # 模型审阅
    B: 1
    C: 0
  by_severity:
    blocker: 0       # 必须修（触发 PATCH 以上）
    major: 2
    minor: 5

# 可选：若 PATCH/ROLLBACK/REWRITE，列出主要问题的 finding_id 或 location
key_findings:
  - source: A
    dimension: on_the_nose
    location: "L45"
    severity: major
```

orchestrator input_gate 降级 yaml schema 见 phase6 execution-protocol §1.5；本 skill 不产该文件。

### 2. `pipeline/scene_{scene_id}/patch_directive.yaml`（仅 PATCH 档）

**Traceability 短锚**（hard gate，详见 [`references/traceability-protocol.md`](references/traceability-protocol.md)）：每 patch 必须含 ≥ 8 字 `anchor_quote` 命中当前 `pipeline/scenes/scene_{id}.md`；`issue_id` / `issue` 不得引用 C 组黑名单 finding（user_accepted / next_round_only；裸 `status=persists` 不入黑名单）。**校验由 `check-reviser-patch` hook 在 reviser dispatch 前自动执行**；未通过 → stderr WARN。**scene-reviewer 自身职责**：每个 patch 写 `anchor_quote` 字段（原句精确截取），不靠在 location 字段里塞引号；不主动跑 verify 脚本——hook 接管。

schema 对齐 reviser 消费（`revision` skill 的 patch_directive.yaml schema）：

```yaml
source: scene_review     # scene-reviewer 自动产出
scene_id: S01

patches:
  - anchor_quote: "就在这时，他抬起头看了看远方"      # ≥ 8 字精确原句，verify 脚本直接 substring match
    location: "L23 附近"                               # 人读定位提示（reviser 用）
    issue: "AI 口癖'就在这时'重复 3 次（S1 lint confidence=high）+ 中断叙事节奏（A §1 判读）"
    suggested_action: "删除 2 处，保留 1 处或改为具体动作衔接"
    issue_id: A-on_the_nose-L23+lint-S1-parallel_negation-1
    patch_kind: null                                   # 通用 patch；不属于反 AI 化定向类时填 null

  - anchor_quote: "她声音有些颤，说话的间隙比平时要长"
    location: "L45 附近"
    issue: "对白前后无神态/动作描写（S3 isolated_speech_beat）+ 声音'有些颤'是库存短语（A §1-D）"
    suggested_action: "删'有些颤'，加一个指节/视线/呼吸的具体细节替代"
    issue_id: A-voice_narrow-L45+lint-S3-isolated-2
    patch_kind: null
```

**`patch_kind` 字段**（可选，反 AI 化定向修订时填）：

```yaml
patch_kind: "<see ../revision/references/patch-kind-registry.md PATCH 类>"
# 物理 enum 在 MUSE-writing/skills/revision/references/patch-kind-registry.md
# scene-reviewer 写 patch_kind 时按 registry 的 PATCH 类填（carrier_then_explain /
# omission_violated / narrator_self_corrects / emotion_naming_under_face_loss /
# care_tone_violence_dropped / omission_filled_in）；
# 通用 patch（非反 AI 化定向）填 null
# 若 finding 属于 ROLLBACK 类（epic_death_facing / mirror_loosened / carrier_missing /
# narrator_distance_global_drift）→ scene-reviewer 直接定 ROLLBACK 档，不写 patch_directive
```

完整 enum + 各 patch_kind 的修订方向参见 [`../revision/references/patch-kind-registry.md`](../revision/references/patch-kind-registry.md)（单一来源；本 SKILL.md 不复制 enum 块）。

**Schema 强化短锚**：每个 patch 必须含 `anchor_quote` 字段（≥ 8 字精确原句），verify 脚本直接 substring match 当前 `pipeline/scenes/scene_{id}.md`。完整规则与 why 见 [`references/traceability-protocol.md §1`](references/traceability-protocol.md)。

**rewrite 类 schema 扩展**：

```yaml
patches:
  # 单 anchor 类型：delete_token / replace_phrase / 现有 PATCH 类
  - patch_id: patch_01
    patch_kind: delete_token | replace_phrase | carrier_then_explain | omission_violated
    anchor_quote: "不少于 8 字的当前正文原句"
    location:
      line_range: [23, 23]
    issue: "定位到的病灶"
    suggested_action: "定点删除或替换"

  # rewrite_sentence：单句 semantic_rewriter
  - patch_id: patch_02
    patch_kind: rewrite_sentence
    anchor_quote: "不少于 8 字的当前正文原句"
    location:
      line_range: [31, 31]
    rewrite_directive:
      semantic_function: "这句在场景里必须保住的功能"
      preserve:
        - "必须保留的人物意图 / 关系信息 / 物件功能"
      remove_patterns:
        - "要消除的 family / cluster / 具体模板"
      target_style: "可见动作 / 物件 / 关系压力承载，不扩写"
      max_sentences: 1
      allowed_carrier_changes:
        low_intensity: true
        plot_adjacent: []

  # rewrite_span：多句到一段 semantic_rewriter
  - patch_id: patch_03
    patch_kind: rewrite_span
    anchor_quote_start: "old_span 开头的精确原句"
    anchor_quote_end: "old_span 结尾的精确原句"
    old_span: "从 anchor_quote_start 到 anchor_quote_end 的完整旧 span"
    location:
      line_range: [40, 43]
    rewrite_directive:
      semantic_function: "该段必须保住的场景功能"
      preserve:
        - "plot fact / relationship fact / object state"
      remove_patterns:
        - "同 span 要消除的 family / cluster"
      target_style: "重组承载方式，保留事实，不新增 plot fact"
      max_sentences: 4
      allowed_carrier_changes:
        low_intensity: true
        plot_adjacent:
          - "仅当 preserve 明示允许时才替换的 carrier"
```

### patch 组装优先级 + 同位置冲突处理

**优先级**（高到低）：

| 优先级 | 来源 | 备注 |
|---|---|---|
| 1 最高 | C 组 `pipeline_crosscheck` / `timeline_plot` / `world_building` | CRITICAL 级已触发升档 ROLLBACK 不入 PATCH；非 CRITICAL 作主 patch |
| 2 | B 组 `characterization` / `factual_detail` / `narrative_style` | blocker 同 C；非 CRITICAL 作主 patch |
| 3 | A 组语义维度（voice_consistency / value_change / on_the_nose / credibility / action_log / micro_language / sensory_balance / pov_boundary / scene_ending） | 作主 patch 的 issue 来源 |

**patch 总量收敛**（罩住 delete 类与 reader_yield recommendation，判据是信号不是数字门槛）：组装完成后看整体——patch 量超出 reviser 单轮可靠施工量的信号：定点 patch 铺满全场多数段落、或多条 patch 针对同一深层叙述形态的不同表层位置。命中时不要全部下发：同形态的合并为 span 级 rewrite patch（一个 cluster 一条）；合并后仍超载说明问题是结构性的——升档 ROLLBACK 让 writer 重写，比海量定点修更可靠。

## 机器台账（只读）

ai_filler 病灶台账 `pipeline/review/{scene_id}.machine_ledger.yaml` 由机器通道脚本写入与回写（issued / observed / resolved / escalated / objection_granted），**你不写它**。post-revision review 需要残余状态时读该文件；若既有 run 只有 `scene_{scene_id}.lint_resolution_ledger.yaml`（缺 machine ledger 的旧产物），按其最后一个 update 块解释残余状态。

**弱表述候选路由**：`dialogue_lint` 的 `weak_character_expression_candidate` 只是 L1 候选提示，不能单独转 PATCH。只有 A 组已确认 `dimension: micro_language, subkind: weak_character_expression`，且给出可命中的 `evidence_quote` / 原句引述时，才可进入 `patch_directive.yaml`。

**合并规则**：

1. **同位置 + 动作方向兼容**（都偏删 / 都偏加 / 高层修局部 + 低层模式层补充） → 合并一个 patch，`issue` 汇总，`suggested_action` 取最高优先级方向，`issue_id` 用 `+` 拼接
2. **同位置 + 动作方向冲突**（一个偏删 / 一个偏加） → **禁止合并**，两种处置任选：
   - (a) 拆成两个独立 patch，按优先级顺序排列（reviser 按序施工）
   - (b) 若高优先级那条涉及 C/B blocker → 直接升档 ROLLBACK，不产 patch_directive
3. **跨位置** finding 无冲突概念——各自独立成 patch

## verdict 单一权威源规则

**`scene_{id}.yaml` 的 `verdict` 字段 = 唯一权威源**。

post-revision review 使用同一 schema，但写入 `pipeline/review/scene_{scene_id}.post_revision.yaml`，用于 PATCH 闭合验证。

Task reply 文本也**必须**回显 verdict 作 orchestrator 快速提示：

```
done scene-review for scene S01; verdict=PATCH (3 patches, 0 blockers)
```

orchestrator 按 phase6 execution-protocol §1.5 解析 verdict。Task reply 不能替代 `scene_{id}.yaml`；即便 reply 写 PASS，文件缺失仍判 ESCALATED。

## ESCALATED 停机 reason 分类

scene-reviewer 本身可能触发的 ESCALATED reason（orchestrator 区分运行时失败 vs 审阅正常分档）：

| reason | 触发场景 |
|---|---|
| `already_reviewed` | 幂等前置命中（`scene_{id}.yaml` 已存在） |
| `verdict_missing` | 写了但字段格式错 / 或根本没写（通常 agent 崩溃） |
| `verdict_source_conflict` | Task reply 与 scene_{id}.yaml 的 verdict 不一致 |

**`dispatch_failed` / `lint_script_failed` / `model_review_failed`** 在 orchestrator 侧判定，不是 scene-reviewer 自己的 reason。

`verdict=ROLLBACK` / `verdict=REWRITE` **不是 ESCALATED**——它们是正常档位决策，orchestrator 按分档路由。

## 不越界（红线）

- 不改 `pipeline/scenes/scene_{scene_id}.md` / scene_card / role_briefs / 任何上游文件
- 不对 `scene_id=null` 的全文级 finding 做归属猜测
- 不对其他场景做评审——一个 scene-reviewer dispatch 只负责一个 scene_id
- 不加载其他 skill 做风格重构（可按需读 `dialogue-craft` / `prose-craft` 的具体原则参考，但通过运行时 skill 入口加载，不 Read）
- 不写 patch_directive 时"创造"新 issue——patches 必须基于 A/B/C findings 或 lint hits 有据可查
- 不在 scene_{id}.yaml / patch_directive.yaml 之外写任何文件

## Fresh session 约定

- 每次 dispatch = fresh session（对齐 writer / reviser）
- 不读其他场景的 scene_{id}.yaml（都是独立决策）
- PATCH → reviser 改 → 下一轮 orchestrator 再次评审时，新的 scene-reviewer 看到的已是**新的 scene_{id}.yaml 不存在 + 已被 reviser Edit 过的 `pipeline/scenes/scene_{scene_id}.md` 当前版**（orchestrator 清理历史的责任）；当前 scope 每场景仅跑一次正常流程

## 减法哲学（与 reviser 一致）

- 默认做减法——PATCH 档的 suggested_action 优先 "删" 而非 "改写" 或 "加更长版本"
- 模糊定位的 finding（"某段末尾有问题" 没给具体句） → 不进 patch_directive；在 rationale 里注明"不可定点修"；若这类占大多数 → 升档 ROLLBACK
- 不追求华丽，只追求聚焦
