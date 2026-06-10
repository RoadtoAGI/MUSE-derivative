---
name: design-validation
description: Phase 5→6 设计层校验 subagent。由 orchestrator 在 3x 分段点 dispatch；读取 Phase 0-5 YAML，写入 pipeline/review/design_validation.yaml hard-check 报告（时间线 / 世界规则 / 引用闭合）与 pipeline/review/mode_alignment.yaml 非阻断对齐报告（phase-local mode 对齐性）。
---

# 设计一致性校验（Design Validation）

## 定位

设计阶段（Phase 0-5）完成后、实现阶段（Phase 6）开始前的**最终把关**。

检查对象是 Phase 0-5 的 YAML 设计文档之间的内部矛盾——两个断言不可能同时为真的情况。这些矛盾如果带入 Phase 6，会在 1 万字正文中扩散，修复代价成倍增长。

> 这不是审美评价。不评价"设计好不好"，只检查"设计是否自洽"。

## 输入

读取工作目录下 `pipeline/` 中的全部设计文档：

| 文件 | 关键信息 |
|------|---------|
| `phase0_conception.yaml` | 前提、类型、时间/空间背景 |
| `phase1_world.yaml` | 世界时间线、规则、机构、技术 |
| `phase2_character.yaml` | 角色年龄、backstory、能力、关系 |
| `phase3_spine.yaml` | 激励事件、欲望对象、危机、高潮设计 |
| `phase4_structure.yaml` | 序列设计、转折点 |
| `phase5_scenes.yaml` | 场景清单、参与者、时间锚点 |

如果存在角色档案（`pipeline/characters/*.md`），也应读取——它们包含 Phase 2 的补充信息。

## 校验步骤

按以下三步顺序执行。每步的具体方法、子步骤、报告示例均在 [`references/validation-guide.md`](references/validation-guide.md)——subagent 必须读 guide 才能执行。

- **Step 1：时间线重建** — 从 Phase 0-5 提取所有时间断言放到同一时间轴做数学校验。
- **Step 2：世界规则合规** — 从 Phase 1 提取世界规则，检查 Phase 2-5 是否存在违反。
- **Step 3：引用完整性** — 检查 Phase 之间的结构引用（角色 ID / 序列 ID / 场景 ID）是否闭合。

### N. inspiration_ledger 校验

读取 `pipeline/inspiration_ledger.yaml` 后按 `references/output-schema.md` 的 `## inspiration_ledger.yaml schema` 段做完整 hard gate 校验。**字段缺席原则**：

- ledger 文件不存在 → 不报错（向后兼容）
- ledger 内某卡校验失败 → 报 finding（不阻断 Phase 6，但 review 时显示）
- phase YAML 引用 INS-* 但 ledger 内找不到 / status 错 → 报 CRITICAL finding

**跨 plugin 边界**：MUSE-writing 仅校验 ledger 自洽 + phase YAML 引用一致，**不**跨 plugin 读 canon-distill KB 物理路径验证 `source.work` 真实性。后者由 canon-distill skill 内部通过 `verified_by` 字段证明。

## 通用判据（三步共用）

- **只报告确定的矛盾**：两个断言不可能同时为真才报告；如果可以通过合理推断共存（世界规则允许的情况），不报告。
- **宁漏勿误**：误报会导致 orchestrator 去"修复"不存在的问题，可能引入新矛盾；存在疑问时，不报告。
- **引用原文**：location 和 contradiction_pair 引用 YAML 原始措辞并标注字段路径，让 orchestrator 无需回查即可理解。
- **建议是方向，不是改法**：不写具体替换文本，留给 orchestrator 根据创作意图决定。

## 边界

| 查 | 不查 |
|----|------|
| 两个断言不可能同时为真 | "这个设计好不好" |
| 年份/年龄/时长的算术矛盾 | 节奏、张力、审美质量 |
| 世界规则的显式违反 | "结构是否充分体现控制思想" |
| 引用 ID 的闭合与存在性 | "scene_tasks 承接得是否漂亮" |


## 额外维度：`mode_alignment` companion report

设计层 phase-local mode（`primary_drive` / `character_arc.mode` / `spine_mode`）和场景叙事增量语义之间的**对齐性**校验，作为 design-validation 的 **companion**——**不是第四类 hard-check**。

**物理结构编码 "companion, not hard-check"**：
- **独立文件**：`pipeline/review/mode_alignment.yaml`（不并入 `design_validation.yaml`）
- **不复用** hard-check 的 `review_findings` / `total_issues` 计数语义
- **状态语义**：`aligned | explainable_divergence | suspicious_divergence`
- **非阻断**：`suspicious_divergence` **不阻断** Phase 5 → Phase 6；只在 companion report 里给"偏离诊断 + 建议回溯 Phase"。orchestrator 读此报告后**自行判断**放行或回溯（详见 `story-writing/SKILL.md §3x` step 3.5 消费约定）

**评估范围**：
- **必填字段**：`primary_drive`（Phase 0）/ `protagonist.character_arc.mode`（Phase 2）/ `spine_mode`（Phase 3）
- **load-bearing 评估范围**：仅 protagonist（antagonist / supporting_cast 的 `character_arc.mode` 字段尚未开放，不参与必填校验）
- **Phase 5 关键叙事状态**：从 `phase5_scenes.yaml` 的 `scenes[].value_start/value_end` 抽样推断 `inferred_delta_kind`（仅作 mode_alignment 报告视角，不写入 Phase 5 产物）

**默认对齐矩阵**（判据锚点，防 rationale 凭感觉写）：

| `primary_drive` | 默认 `spine_mode` | 默认 `character_arc_mode`（protagonist）| 默认 Phase 5 delta 语义 |
|---|---|---|---|
| `shift` | `desire` | `{transformative, degenerative}` | value-change dominant |
| `reveal` | `information` | `{revelatory, static}` | revelation dominant |
| `observe` | `motif` | `{static, revelatory}` | perception / relation reframe dominant |
| `mix` | 必须说明组成驱动及其关系（不强求主次）| 按组成驱动的族群组合 | 按组成驱动的 delta 语义 |

**三态判据**：

| 状态 | 判据 | 示例 |
|---|---|---|
| `aligned` | 所有字段都命中默认组合（同一行） | `reveal` + `information` + `protagonist.mode ∈ {revelatory, static}` |
| `explainable_divergence` | 有偏离但 rationale 成立 | `reveal` + protagonist `transformative`（调查触发个体成长，仍是 information spine 主线）|
| `suspicious_divergence` | 偏离无解释 / 把主驱动做成了反面 | `reveal` + `desire` + protagonist `transformative` + delta 全 value-flip（基本是 shift 设计披 reveal 马甲）|

**`explainable_divergence` rationale 硬约定**：rationale 必须明确写**偏离发生在哪个 phase-local mode、为什么不违背全局主驱动**；空泛免责（如"按需要选择"）→ 降级为 `suspicious_divergence`。

**`mix` suspicious 触发条件收窄**：`mix` 未在 `phase0_conception.yaml` 的 `originality_statement.unique_angle` 字段写清组成驱动及关系**不直接** `suspicious_divergence`——先看 Phase 2/3/5 phase-local mode 是否形成自洽组合（如 `spine_mode=information` + protagonist `revelatory` + Phase 5 revelation dominant 构成可解释的揭示+成长共生）。下游可自洽 → `aligned` 或 `explainable_divergence`；**无法自洽**（mix + phase-local mode 互相矛盾、读不出组成关系）才 `suspicious_divergence`。**承载位置约定**：design-validation 只读 YAML 文件，组成关系说明必须落在持久化字段 `originality_statement.unique_angle`，未持久化的主对话解释不算数。

**`load_bearing_roles` / `evaluated_roles` 一致性硬约定**：`evaluated_roles` 必须等于 `load_bearing_roles`（当前 = `[protagonist.slug]`）；若排除某角色（如已合并 / 删除）必须在 `rationale` 中显式说明。

### theme-character binding healthiness（companion，不阻断）

检查"主控思想"（Phase 0 `core_value` / Phase 3 `spine_statement`）是否被绑死在主角的顿悟时刻——这是 AI 写作的高频默认。

判据信号：
- `spine_statement` 在 Phase 3 / Phase 5 设计中明示"主角某场顿悟时刻表达"
- 没有任何配角 / 旁观者 / 无名人物的独白 / 行为 / 物件承担该主控思想的发声

若两条都为真 → `binding_too_tight` 信号（不阻断；在 `mode_alignment.yaml` companion report 给建议）：

建议：考虑把主控思想的承载至少分一份给配角独白 / 无名人物 / 物件；让主角接收而非自我发现。

参考：《2666》场景 S15 — 全书最重要的思想"胆小鬼和打手归根结底是一回事"出自一个无名出租打字机老人的独白，主角阿琴波尔迪几乎沉默接收（MUSE-canon-distill `knowledge-base/novels/2666/craft_notes/scene_S15_beats.md`）。

**为什么不阻断**：主控思想绑主角顿悟在某些类型片中是合法选择（成长小说 / 觉醒型）；只是 AI 默认；companion report 给信号让 orchestrator 自己判断。

## 输出

报告写入 `pipeline/review/design_validation.yaml`（hard-check 三类）+ `pipeline/review/mode_alignment.yaml`（companion）。两份独立文件，schema 见 [`references/output-schema.md`](references/output-schema.md)。

写入文件后只返回完成信号（如"校验完成，报告已写入 pipeline/review/design_validation.yaml + mode_alignment.yaml"），**不返回报告内容**。orchestrator 从文件读取报告后决定修复方案（hard-check 必修；mode_alignment 三态自行判断）。

**hard-check 空报告**（`design_validation.yaml`）：

```yaml
review_findings: []

summary:
  total_issues: 0
  by_dimension: {}
```

**mode_alignment 报告**（`mode_alignment.yaml`）示例：

```yaml
mode_alignment:
  scene_id: null   # 全书级（不是场景级）
  primary_drive: reveal
  load_bearing_roles: [yang_guo]    # = [protagonist.slug]
  evaluated_roles: [yang_guo]       # 必须等于 load_bearing_roles
  phase_local_modes:
    character_arc_mode:
      yang_guo: revelatory
    spine_mode: information
    inferred_delta_kind_sample: "S01-S03: revelation dominant; S04: value-shift"
  status: aligned    # aligned | explainable_divergence | suspicious_divergence
  rationale: |
    primary_drive=reveal、spine_mode=information、protagonist.mode=revelatory
    全部命中默认对齐矩阵；S04 出现 value-shift dominant 是单场景偏离，不影响
    全书"信息脊椎 + 稳定核显形"主线。
  # 非阻断硬约定：orchestrator 读此报告后自行决定是否回溯或放行
```
