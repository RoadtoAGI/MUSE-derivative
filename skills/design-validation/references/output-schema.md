# 设计校验报告格式

design-validation subagent 产出**两份独立报告**：
1. `pipeline/review/design_validation.yaml`——hard-check 三类（时间线 / 世界规则 / 引用闭合），见下方 §1
2. `pipeline/review/mode_alignment.yaml`——companion report（phase-local mode 对齐性），见下方 §2

两份文件**不复用**对方的 schema；mode_alignment 不复用 hard-check 的 `review_findings` / `summary.total_issues` 计数语义。

---

## 1. `design_validation.yaml`（hard-check）

### 报告结构

```yaml
review_findings:
  - dimension: temporal_math       # 三个可选值见下方
    scene_id: null                 # 设计层问题通常为 null
    location: >
      phase2_character.yaml: "age_apparent: 52"
    contradiction_pair: >
      phase1_world.yaml: "era: approximately 2140";
      phase2_character.yaml: backstory — "active in 2023"
    source: pipeline               # 设计校验的 source 固定为 pipeline
    issue: 出生年 ~2088，不可能在 2023 年工作
    suggestion: 调整 backstory 年份或补充跨时代机制

summary:
  total_issues: 1
  by_dimension:
    temporal_math: 1
```

### 维度

| 维度 | 含义 |
|------|------|
| `temporal_math` | 时间线数学矛盾：年份、年龄、时长的算术不自洽 |
| `world_rule_violation` | 世界规则违反：Phase 2-5 中的断言违反 Phase 1 设定的硬规则 |
| `reference_integrity` | 引用完整性：Phase 间的 ID/角色/结构引用不闭合或指向不存在的实体 |

### 字段说明

| 字段 | 必需 | 说明 |
|------|------|------|
| `dimension` | 是 | 三个维度之一 |
| `scene_id` | 是 | 关联的场景 ID，设计层问题通常为 `null` |
| `location` | 是 | 矛盾一端的引用，标注文件名和字段 |
| `contradiction_pair` | 是 | 矛盾另一端的引用 |
| `source` | 是 | 固定为 `pipeline` |
| `issue` | 是 | 矛盾的具体描述，包含关键数字/推导过程 |
| `suggestion` | 是 | 修复方向 |

### 持久化

报告写入 `pipeline/review/design_validation.yaml`。

如果没有发现任何问题，写入空报告 `review_findings: []` + `summary.total_issues: 0`。

---

## 2. `mode_alignment.yaml`（companion，非阻断）

校验 phase-local mode（`primary_drive` / `character_arc.mode` / `spine_mode`）与场景叙事增量语义的**对齐性**。使用状态语义，不输出 findings 列表。

### 报告结构

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
  status: aligned   # aligned | explainable_divergence | suspicious_divergence
  rationale: |
    全部命中默认对齐矩阵；S04 出现 value-shift dominant 是单场景偏离，
    不影响全书"信息脊椎 + 稳定核显形"主线。
```

### 字段说明

| 字段 | 必需 | 说明 |
|------|------|------|
| `mode_alignment.scene_id` | 是 | 全书级，固定为 `null`（mode_alignment 不是场景级报告）|
| `mode_alignment.primary_drive` | 是 | 从 `phase0_conception.yaml` 取值，enum 见 phase0-conception/output-schema |
| `mode_alignment.load_bearing_roles` | 是 | Phase 2 认定的 load-bearing 角色 slug list；**当前 = `[protagonist.slug]`**（antagonist / supporting_cast 字段尚未开放）|
| `mode_alignment.evaluated_roles` | 是 | 本报告实际评估的角色 slug list；**必须等于** `load_bearing_roles`，若排除某角色（合并 / 删除）必须在 `rationale` 中显式说明排除原因 |
| `mode_alignment.phase_local_modes.character_arc_mode` | 是 | dict[slug → mode]；当前仅含 protagonist；mode enum 见 phase2-character/output-schema |
| `mode_alignment.phase_local_modes.spine_mode` | 是 | 从 `phase3_spine.yaml` 取值，enum: `desire | information | motif` |
| `mode_alignment.phase_local_modes.inferred_delta_kind_sample` | 否 | 从 `phase5_scenes.yaml` 抽样推断的 Phase 5 delta 语义模式（仅作 mode_alignment 报告视角，不写入 Phase 5 产物）|
| `mode_alignment.status` | 是 | 三态枚举：`aligned`（命中默认对齐矩阵）/ `explainable_divergence`（偏离但 rationale 成立）/ `suspicious_divergence`（偏离无解释或主驱动做反）|
| `mode_alignment.rationale` | 是 | 状态的判据说明；**`explainable_divergence` 硬约定**：必须明确写偏离发生在哪个 phase-local mode、为什么不违背全局主驱动；空泛免责（如"按需要选择"）→ 降级为 `suspicious_divergence`。**`mix` 专项**：当 `primary_drive=mix` 时 rationale 须说明**组成驱动及其关系**（哪些驱动共同主导、各自承担什么）；未说明组成关系**不直接** `suspicious_divergence`——先看 Phase 2/3/5 phase-local mode 是否自洽组合，下游可自洽 → `aligned` 或 `explainable_divergence`，无法自洽才 `suspicious_divergence` |

### 不复用 hard-check 字段

`mode_alignment.yaml` **不复用** `review_findings` / `summary.total_issues`——这些字段属于 hard-check 语义。mode_alignment 用 `status` 三态 + `rationale` 表达对齐性判据，物理结构上和 hard-check 报告解耦。

### 持久化

报告写入 `pipeline/review/mode_alignment.yaml`（独立文件，**不并入** `design_validation.yaml`）。

写入后只返回完成信号，不返回报告内容。orchestrator 在 `story-writing/SKILL.md §3x step 3.5` 消费此报告并按 `status` 决定放行 / 回溯（**非阻断**——orchestrator 自行判断）。

---

## inspiration_ledger.yaml schema

文件位置：`pipeline/inspiration_ledger.yaml`

### 两层架构（candidate / accepted）

| 层 | 文件 | 写者 | 状态 |
|---|---|---|---|
| **候选层** | `pipeline/references/canon_candidates_phase{N}.yaml` | canon-researcher subagent | 临时研究产物，per-phase 覆写 |
| **正式 ledger** | `pipeline/inspiration_ledger.yaml` | orchestrator 主对话 promote 后写入 | SSOT；status enum 控制生命周期 |

`status` enum:

| status | 语义 | 谁能引用 |
|---|---|---|
| `candidate` | 仅在 candidates 文件，未进 ledger | 不被 phase YAML / writer / story-review 引用 |
| `accepted` | orchestrator 已 promote 到 ledger，phase YAML 可挂 | phase YAML / writer / story-review 全可引用 |
| `bound` | 已被至少一个 phase YAML 显式引用 | 同 accepted；表示已落地 |
| `retired` | 曾 accepted 但后续 phase rerun 时被弃用 | 不再被新 phase YAML 引用；旧引用保留作 audit |

写入规则：

- subagent 只产 candidates 文件，**不动 ledger**
- orchestrator 主对话**显式 promote**：从 candidates 选中 -> 分配正式 INS-* ID -> 写入 `inspiration_ledger.yaml` 并设 `status: accepted`
- phase YAML 引用某 INS-* 时，orchestrator 同时把 ledger 内该卡 status `accepted -> bound`
- rerun 时旧 INS-* 不强制保留；若 phase YAML 不再引用，orchestrator 显式标 `retired`

### 通用字段（pattern 和 archetype 共用）

```yaml
- id: INS-001                   # 全局唯一；type=archetype 用 INS-A01 前缀，type=pattern 用 INS-001 数字
  type: pattern                  # pattern | archetype
  status: accepted               # candidate | accepted | bound | retired
  source:
    work: "三体Ⅲ-死神永生"        # canon-distill KB 内书名（不跨 plugin 校验存在性，见下方校验边界）
    kb_id: "novel:three-body-3"  # canon-distill 内部稳定 ID
    pattern_name: "scale_shrink"
    learned_mechanism: "宇宙级命题最终落到小物件 / 小动作"
    verified_by: "design-doc-reference"
  abstraction:
    what_to_learn: "尺度收缩"
  fit_signal:
    - "末世题材 + 文明级危机"
    - "需要把宏大设定收缩到个人选择的高潮场景"
  project_encoding:
    - phase: 1
      field_path: "world_rules[2]"
      adoption_kind: "world_rule"
      design_value: "宏大灾变的局部后果必须能落到家庭器物"
    - phase: 3
      field_path: "reader_spine.reveal_ladder_seed"
      adoption_kind: "reveal_logic"
      design_value: "读者等待文明级危机是否真改变个人生活"
    - phase: 5
      field_path: "scenes[S12].inspiration_refs"
      adoption_kind: "scene_carrier"
      scene_id: "S12"
  disclosure_ladder:
    - layer: early_signal
      scene_id: "S03"
      carrier: "儿童夜灯"
      reader_inference: "物件与家庭安全感有关，价值未解释"
      do_not_explain:
        - "不说它象征文明"
        - "不交代完整来历"
    - layer: mid_reframe
      scene_id: "S08"
      carrier: "夜灯电池"
      reader_inference: "物件进入资源稀缺逻辑"
      do_not_explain:
        - "不把主题总结出来"
    - layer: final_confirmation
      scene_id: "S12"
      carrier: "是否点亮夜灯的动作"
      reader_inference: "宏大危机被压缩为家庭选择"
      do_not_explain:
        - "不扩张到星河 / 黎明 / 全人类"
```

### type=archetype 额外字段

```yaml
- id: INS-A01
  type: archetype
  status: accepted
  archetype_role: protagonist     # protagonist | deuteragonist | antagonist | supporting_cast
  archetype_target_slug: "main"   # 引用 phase2 哪个角色 slot
  weight: dominant                # dominant | secondary
  merge_boundary: "只学习沉默中的行动推断，不学习人生轨迹"  # weight=secondary 时必填
  source:
    work: "斯通纳"
    kb_id: "novel:stoner"
    character: "威廉·斯通纳"
    canon_path: "characters/威廉·斯通纳.md"
    register: "表达力弱但感受力强的主角"
    verified_by: "design-doc-reference"
  abstraction:
    what_to_learn: "极简对白 + 内心独白缺失；用外部行为推断内心；知道自己曾经是谁式弧光"
  fit_signal: []
  project_encoding:
    - phase: 2
      field_path: "protagonist.voice_traits"
      adoption_kind: "voice_anchor"
      design_value: "极简短句 + 沉默承载情感"
    - phase: 2
      field_path: "protagonist.recognition_path"
      adoption_kind: "recognition_seed"
      design_value: "通过外部行为推断主角内心"
```

### Schema 约束（design-validation 校验）

重要校验边界：MUSE-writing `design-validation` **不跨 plugin 读 KB 物理路径**。`source.work` / `source.kb_id` / `source.canon_path` 的真实性校验由 canon-distill 内部在生成 candidate 卡时完成（通过 `verified_by` 字段证明），MUSE-writing 侧只做 ledger 自洽校验。

| 约束 | 适用 type | 校验方 |
|---|---|---|
| `id` 全局唯一（在同一 ledger 文件内） | both | MUSE-writing design-validation |
| `status` ∈ enum {candidate, accepted, bound, retired} | both | MUSE-writing design-validation |
| `source.verified_by` 非空 | both | MUSE-writing design-validation |
| `source.work` / `source.kb_id` 非空（**不验存在性**，仅验非空） | both | MUSE-writing design-validation |
| `disclosure_ladder` 三 layer（early_signal / mid_reframe / final_confirmation）至少各 1 项 + 引用真实 scene_id（**仅在 phase5_scenes.yaml 存在时校验**） | pattern | MUSE-writing design-validation |
| `disclosure_ladder[].carrier` 非空 + `do_not_explain` 至少 1 项 | pattern | MUSE-writing design-validation |
| `archetype_target_slug` 必须对应 phase2_character.yaml 实际角色（**仅在 phase2 已 ship 时校验**） | archetype | MUSE-writing design-validation |
| **每 archetype_role：1 默认 / 2 例外 / ≥3 报错**；1 张为默认推荐，2 张为例外（必须 dominant + secondary 且 secondary 有 merge_boundary），≥3 张报错（用户语义："一个不少，两个也行，三个就多了"） | archetype | MUSE-writing design-validation |
| `project_encoding` 至少 1 项 + 每项 `field_path` 非空 | both | MUSE-writing design-validation |
| phase YAML 引用的 INS-* 必须在 ledger 内且 `status ∈ {accepted, bound}` | both | MUSE-writing design-validation |
