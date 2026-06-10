---
name: phase3-spine
description: MUSE Phase 3 — 故事脊椎 + 幕/Arc 框架。设计激励事件、戏剧问题、按 spine_mode（desire/information/motif）构建故事组织力，并决定故事需要几个幕/Arc 及每个 Arc 的重大轨迹跃迁。由 orchestrator 在 pipeline 推进到 Phase 3 时触发（上游 Phase 0/1/2 产物已就绪，下游 Phase 4 结构设计的输入）。
---

# Phase 3: 故事脊椎 + 幕/Arc 框架

## 核心原则

脊椎 = 故事的**组织力**——**默认适用于单主角、冲突驱动、目标明确的戏剧型故事**（麦基框架"主角恢复生活平衡的深层欲望 + 不懈努力"；原文见 `references/mckee-spine.md §故事脊椎`）。群像 / 调查 / 拼图 / 反结构作品可用**信息脊椎**（真相显形 / 碎片聚拢）或**母题脊椎**（观念 / 意象 / 风格驱动的组织力）替代——脊椎类型由 `spine_mode` 字段显式声明（enum：`desire | information | motif`；边界定义见 Step 3）。

不论 `spine_mode`，每个场景要么推进脊椎，要么与脊椎形成张力——与脊椎无关的场景不属于这个故事（所有 mode 通用的场景取舍测试）。

## 输入契约

从 Phase 0 接收（核心依赖）：
- `premise` — 激励事件应回应前提
- `core_value` — 脊椎围绕核心价值运动
- `controlling_idea` — 故事高潮必须通过行动表达主控思想
- `primary_drive` — **仅作 Step 3 `spine_mode` 判定的近端默认建议**，不作条件分支权威源（Phase 3 独立判定 spine_mode，不回读 primary_drive 做 if-else；两层对齐由 mode_alignment companion report 事后校验）

从 Phase 1 接收（参考依赖）：
- `setting` — 激励事件发生在这个世界内

从 Phase 2 接收（**mode-aware**，依赖强度按 `spine_mode` 调整）：
- `protagonist.desire_system` — **核心**（`spine_mode=desire`）/ **参考**（`information` / `motif`）：desire 下用于激发主角欲望、构建脊椎；非 desire mode 可参考但不强制构建欲望脊椎
- `protagonist.characterization` — **核心**（`spine_mode=desire`）/ **参考**（其他）：desire 下作为脊椎起点（主角初始生活平衡）；非 desire mode 仅作角色画像参考
- `deuteragonist`（若存在）— **条件依赖**：双主角 / 守护者形态下按 protagonist 等价结构读取，参与 spine 组织力判断
- `antagonist` — **条件依赖**：若对抗由人物承载（多数 desire mode + 部分 information mode）则读取；纯 information / motif 故事如对抗来自信息缺口或形式约束本身，可不读

## Canon/design reference（设计前置必跑）

**本段必跑**：进入本阶段先调用 `Skill design-doc-reference`——**不要**基于"当前可见 skill 列表里没看到"或"猜测 MUSE-canon-distill 未装"做预判跳过。**先调，再由 skill 自身返回值决定是否降级**：

```
phase=3
genre=<Phase 0 genre.primary>
signals=<JSON: 至少含 spine_mode, protagonist_desire 或 information_goal, crisis_type 中能填的>
```

调用成功 → Read `pipeline/references/phase3_design_ref.md`，只学习：

- **脊椎字段如何收束**（spine_statement / desire / antagonist / crisis 之间的字段密度比例）
- **激励事件 → 危机 → 高潮**形成因果链的组织方式（不是"事件清单"而是"因果链"）
- **desire / information / motif spine** 三种模式各自的脊椎组织差异

**合法降级条件**：仅当 skill **实际返回** 扩展包未装 / KB 不可达 / 无匹配 三类信号时，才跳过本段按下方步骤自主设计。"看不到 skill 名"、"未确认是否安装"**不是**合法降级理由——这两类情况必须先调一次再判。

## reveal_ladder_seed 字段

`reader_spine.withheld_answer` 是单点字段——只说"哪个答案不能早说"。`reveal_ladder_seed` 是多段字段，承担**真相显形路径**的高层骨架：

```yaml
reader_spine:
  reader_waits_to_know: "..."
  recognition_object: "..."
  withheld_answer: "..."          # 已有
  reveal_ladder_seed:             # 新增字段（全 optional）
    early_signals:                # 早期信号：读者首次接触相关物件 / 行为 / 异常，价值未解释
      - "..."
    mid_reframes:                 # 中段重构：物件 / 行为意义被部分修正 / 升级
      - "..."
    final_confirmation:           # 终局确认：真相在具体载体上显形
      - "..."
```

**与 inspiration_ledger 的关系**：

phase3 `reveal_ladder_seed` 是**本作真相显形路径的高层骨架**，不强制引用 INS-*；但灵感卡的 `disclosure_ladder` 可以**与本字段对齐**——同一 INS-* 的 disclosure_ladder 三 layer 应能映射到 phase3 reveal_ladder_seed 的 early/mid/final 三段。

phase5 scene_card 后再具体绑定 INS-* `disclosure_ladder[].scene_id` 到具体场景。

字段不存在 → 不报错（向后兼容）；存在则 design-validation 检查三段是否各至少 1 项（仅在字段非空时校验）。

## 衍生前置：已有 `phase3_spine.yaml` 则在其上完善（MUSE-derivative）

本 skill 在 **MUSE-derivative**（衍生写作）运行——与 MUSE-writing 的唯一区别在此段。执行 §执行步骤 前先看 work_dir 是否已有 `pipeline/phase3_spine.yaml`（derivative 入口经 `init_derivative_run.py` 从 canon 蒸馏物 / 用户已有 pipeline 预置的继承基线）：

- **已有（继承基线）** → 不从零重生成，把它当起点在其上**完善**：续写（sequel）= 保留继承 spine 全字段不重排不重写、在其末端追加续写段的新激励事件 / 新危机高潮（由原作未解决线索推导，不与已发生事件冲突）；跨风格 = 保留 spine 不动；同人/外传若入口未预置 phase3 yaml 则按"没有"分支重建。元数据标 `source: derived_from=<canon-slug | existing_pipeline>`。此时 §执行步骤 作**完善检查表**（缺则补），非从零产出指令。
- **没有** → 按 §执行步骤 从零生成（与 MUSE-writing 完全一致）。

两种情形产物 schema 与下游消费都与 MUSE-writing 一致——这是 derivative ≈ MUSE-writing 的根本。

## 执行步骤

### 1. 设计激励事件

激励事件是打破主角日常生活平衡的那个事件——必须动态、具体、彻底打破平衡（原文见 `references/mckee-spine.md §激励事件`）。它必须：
- **足够重大**：主角无法忽视，无法回到原来的生活
- **动态而具体**：不是"渐渐厌倦了工作"，而是一个明确的事件
- **发生方式**：主角的主动决定（decision），或降临到主角身上的意外（accident）

```
日常平衡 → 激励事件 → 失衡（正向或负向偏离）
```

### 2. 确定欲望对象（`spine_mode=desire` 时必填；其他 mode 可空或 null）

激励事件打破平衡后，按 `spine_mode` 决定是否以及如何提取欲望对象（`spine_mode` 的判定在 Step 3 收敛；本步骤先按用户 query / Phase 0 `primary_drive` 近端建议直观判定激励事件带起的是欲望、谜团还是母题激活）：

- **`desire` mode（麦基默认）**：激励事件在主角心中激起恢复平衡的欲望（原文见 `references/mckee-spine.md §激励事件`）。提取：
  - **自觉欲望对象**：主角明确追求的（必须具体——读者能想象主角得到它时的画面）
  - **不自觉欲望对象**：主角真正需要但不自知的（来自 Phase 2 的欲望系统设计）
  - **张力**：两种欲望之间如何冲突
- **`information` mode**：激励事件暴露待显形的真相或打开信息缺口；此时 `desire_object` 可为 null，核心是在 Step 3 的 `spine_statement` 中表述真相显形路径
- **`motif` mode**：激励事件引入或激活将在故事中展开的母题；此时 `desire_object` 可为 null，核心是在 Step 3 中表述母题如何组织叙事

### 3. 构建故事脊椎

**Step 3.1：判定 `spine_mode`**（Phase 3 独立判定——**不回读** Phase 0 `primary_drive` 做条件分支；`primary_drive` 仅作近端默认建议，Phase 3 根据故事组织力性质独立落选，两层对齐由 `mode_alignment` companion report 事后校验）：

| `spine_mode` | 语义 | 典型场景 |
|---|---|---|
| `desire`（麦基默认）| 主角有明确欲望对象，不懈努力追求 | 冲突驱动戏剧、单主角目标追求 |
| `information` | 真相逐步显形 / 碎片逐步聚拢 | 侦探 / 调查 / 档案拼图 / 解谜 |
| `motif` | 观念 / 意象 / 风格驱动的组织力 | 观念小说 / 文献拼贴 / 群像 / 氛围累积 |

**不加 `structural` 第四档**——形式约束型作品落 `motif` 或 `information`，防"其他都塞这里"垃圾桶。

**Step 3.2：按 mode 构建脊椎陈述（`spine_statement`）**——所有 mode 都必须产出一句话 `spine_statement`，语义按 mode 解释：

| `spine_mode` | `spine_statement` 范式 |
|---|---|
| `desire` | "主角想要 X，为此克服 Y，最终获得/失去 X" |
| `information` | "真相 T 如何逐步显形：从初见象到完整理解的路径" |
| `motif` | "母题 M 在故事中如何展开、呼应、变形" |

**Step 3.3：desire mode 下的 spine_type 子类判定**（仅 `spine_mode=desire` 时适用）：
- 主角只有自觉欲望：自觉欲望 = 脊椎（`spine_type: conscious`）
- 主角同时有不自觉欲望：不自觉欲望 = 脊椎（`spine_type: unconscious`，因为它才是故事真正要讲的东西）

`information` / `motif` mode 下 `spine_type` 字段为 null（不适用）。

**Step 3.4：场景取舍测试**（所有 mode 通用）——如果一个场景既不推进也不挑战脊椎，它可能不属于这个故事：
- `desire` mode：不推进"欲望 + 不懈努力"的场景可删
- `information` mode：不贡献"真相显形"关键碎片 / 不给出新信息差的场景可删
- `motif` mode：不呼应 / 不变形 / 不展开母题的场景可删

**Step 3.5：读者认知脊椎（`reader_spine`）**（所有 mode 通用）——脊椎是角色 / 信息 / 母题的组织力；`reader_spine` 是**读者**在整篇追踪、等待被确认 / 推翻的认知线。角色脊椎和读者脊椎可以错位（角色追欲望 X，读者真正等的是关于 X 的某个真相显形 / 误解推翻）。

```yaml
reader_spine:
  reader_waits_to_know: "读者真正等什么被确认 / 推翻"
  recognition_object: "最终通过什么动作 / 物件 / 图像 / 选择确认"
  withheld_answer: "哪些答案不能过早解释"
```

`recognition_object` 必须是可感知的具体载体（动作 / 物件 / 图像 / 选择），不允许"读者最终意识到 X"式纯抽象解释。`withheld_answer` 用于约束 Phase 5 / Phase 6 不要把这些答案过早写出。

### 4. 设定戏剧问题

激励事件在读者脑中激发的核心问题。戏剧问题在故事开头被提出，在最终高潮被回答。

`dramatic_question` 同时是**全篇读者追问**——读者整篇跟随的最大问题。Phase 5 的 `reader_track` 是其在单场尺度的具体化（每场读者跟随的局部问题，最终汇入这条全篇主线）。

### 5. 确定对抗力量

根据故事需要，确定主角将面对的对抗力量。麦基将对抗分为内在（自我）、个人（人际）、外在（社会/环境）三层，但不必拘泥于此分类——按故事实际需要决定对抗的类型和数量。

### 6. 设计幕/Arc 框架

> 「根据亚里士多德的原理……作品越长，重大的逆转便越多。」
> 「三幕故事节奏就已成为故事艺术的基础。但它只是一个基础而已，不是公式。」
> —— 《故事》第九章

根据故事的长度和复杂度，决定需要几个幕/Arc。每个 Arc 必须有：
- **轨迹起点→终点**：进入和离开时关键叙事状态不同（重大逆转 / 重大跃升 / 重大变形），语义按 `spine_mode` 解释：
  - `desire` mode：**价值状态**起点→终点（重大价值逆转，麦基默认）
  - `information` mode：**信息 / 认知状态**起点→终点（重大信息跃升 / 真相显形的关键节点）
  - `motif` mode：**母题状态**起点→终点（重大母题变形 / 呼应 / 转调）
- **高潮事件**：一句话描述导致本 Arc 轨迹跃迁的关键事件（desire 下是价值逆转、information 下是真相披露、motif 下是母题变奏）
- Arc 之间的冲击力必须递增

不预设 Arc 数量——有多少个真正的重大**轨迹跃迁**（按 spine_mode 解释），就有多少个 Arc。

**Schema 字段语义**：Arc 的 `value_at_start / value_at_end` 字段名沿用，但**语义按 `spine_mode` 解释**（不一定是"价值状态"；承载的是"Arc 轨迹的起点 / 终点关键状态"）。Phase 4 当前按 desire mode 语义消费这些字段。

### 7. 设计故事高潮

故事级的危机、高潮和结局——与 `inciting_incident`、`spine_statement` 同级的故事层决策：

- **危机**：主角面临的终极两难（不可调和的两善择一或两恶择轻）
- **高潮**：危机选择的行动及其结果——通过行动表达主控思想
- **结局**：高潮后的新平衡状态

> 「故事高潮必须充满意义……当价值处于最大负荷时所发生的绝对而不可逆转的价值摇摆。」
> —— 《故事》第十三章

**高潮形态允许"失败型"**：高潮不必等同于主角能力胜利。允许三种失败型形态：

- **`hero_fails_world_completes`**：主角失败，但世界机制 / 副角色欲望 / 长期伏笔完成结果（《指环王》末日裂隙：弗罗多失败，咕噜夺戒坠落毁掉魔戒）
- **`withdrawal_as_resolution`**：事件尺度收缩，主角主动退场作为解决；不是更大的对抗，而是从对抗中抽身（《三体Ⅲ》终局从宇宙广播收缩到 5kg 生态球）
- **`silence_after_truth`**：最终胜利伴随不可修复损伤；真相揭示后角色沉默不解释，由读者承担余味（《指环王》终章山姆回家但弗罗多必须离开）

失败型高潮仍必须通过**具体行动 / 选择 / 物件**表达主控思想，不允许"主角什么都没做，世界自己解决了"式叙事塌陷。`reader_spine.recognition_object` 在失败型高潮中尤其关键——读者最终确认的不是主角能力胜利，而是 controlling_idea 通过哪个具体载体被确认。

## 输出

→ YAML 输出结构见 `references/output-schema.md`

交付物写入 `pipeline/phase3_spine.yaml`，包含：inciting_incident, spine_mode, spine_statement, reader_spine, dramatic_question, opposing_forces, arcs[], story_climax_design。`desire_object` 与 `spine_type`：仅 `spine_mode=desire` 时必填，其他 mode 下为 null。`reader_spine` 所有 mode 通用；`story_climax_design.climax.climax_form` 可选（默认 `hero_succeeds`，失败型高潮三档详见"故事高潮"段）。

**既有产物 fallback**：`phase3_spine.yaml` 缺 `spine_mode` 时兼容层按 `desire` 解释，下游读取既有产物不视为缺必需字段。新生成路径必须依据故事组织力性质显式选择最贴近的一类，不允许以"不确定"为由跳过判定。

## 常见错误

| 错误 | 后果 | 修正 |
|------|------|------|
| 戏剧问题太快回答 | 故事失去悬念 | 戏剧问题的答案必须保留到最终高潮 |
| 激励事件与前提脱节 | Phase 0 的构想被浪费 | 激励事件应是前提的具体化 |
| Arc 数量预设而非由故事决定 | 结构刚性 | 先确定有几个重大轨迹跃迁（按 `spine_mode` 解释：desire=价值逆转 / information=信息跃升 / motif=母题变形），再划分 Arc |
| 危机/高潮放在 Phase 4 设计 | 故事层决策与序列层混杂 | 危机/高潮是故事级决策，在本阶段完成 |

→ 理论深度参考见 `references/mckee-spine.md`
