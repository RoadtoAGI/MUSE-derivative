# 校验方法论

本文件是 design-validation subagent 的详细执行指南。

## Step 1：时间线重建

> 这是最重要的一步。时间线数学矛盾是设计阶段最常见也最难事后修复的错误类型——年份/年龄的算术不一致一旦写入正文，会扩散到全文各处。必须完整执行以下三个子步骤，不能跳过。

### 方法

**子步骤 A：提取时间断言**

通读 Phase 0-5 全部 YAML，找出所有包含时间信息的字段值。时间信息包括：
- 明确年份（"2023年"、"approximately 2140"）
- 年龄（"age: 52"、"age_apparent: 38"）
- 持续时间（"九年前抵达"、"服役 12 年"）
- 相对时间（"三年前分手"、"26 岁入职"）
- 时代描述（"22 世纪中叶"、"early 21st century"）
- 机构/技术年表（"TEB 2089 年成立"、"Tabula Protocol 2101 年合法化"）

**子步骤 B：建立时间轴（必须显式列出）**

将提取的断言转化为绝对年份，以表格形式列出。这一步是强制性的中间产物——先列表，再校验。

```
角色/实体         来源                  原始断言                    推导
────────────────────────────────────────────────────────────────────────
故事时间          phase1_world          era: ~2140-2150             基准年: 2145
Declan Marre      phase2_character      age: 38                     出生年: 2145-38 = 2107
  - 入职 TEB      phase2_character      "Recruited by TEB at 26"    2107+26 = 2133
  - 分手          phase2_character      "三年前"                    2145-3 = 2142
Thomas Cole       phase2_character      age_apparent: 52            出生年: 2145-52 = 2093
  - Tabula 施加   phase2_character      "at 43"                     2093+43 = 2136
  - 抵达村庄      phase2_character      "九年前"                    2145-9 = 2136 ✓
Elias Rourke      phase2_character      "archivist in 2023"         活跃年: 2023
  (= Thomas Cole) phase2_character      name_original = Rourke      出生年应 = 2093
TEB               phase1_world          "established in 2089"       成立年: 2089
Tabula Protocol   phase1_world          "legalized in 2101"         合法化: 2101
```

**子步骤 C：交叉校验**

在时间轴上逐行检查以下不等式：
- 每个角色：`backstory 事件年 ≥ 出生年`（不能在出生前做事）
  - 上表中：Rourke 2023 年活跃，但出生年 2093 → **2023 < 2093，矛盾**
- 每个机构引用：`事件年 ≥ 机构成立年`（不能引用尚未存在的机构）
- 每个技术引用：`使用年 ≥ 技术发明/合法化年`
- 场景间时间顺序与 Phase 5 编排顺序一致

### 报告示例

```yaml
- dimension: temporal_math
  scene_id: null
  location: >
    phase2_character.yaml: "Elias Rourke was a digital records archivist
    in a UK government intelligence unit in 2023"
  contradiction_pair: >
    phase1_world.yaml: "era: approximately 2140-2150";
    phase2_character.yaml: "age_apparent: 52" → 出生年 ~2088
  source: pipeline
  issue: >
    角色出生于 ~2088 年，不可能在 2023 年（出生前 65 年）从事档案工作。
  suggestion: >
    调整 backstory 年份使其落在角色出生之后，或在世界设定中补充
    时间旅行机制的解释使跨时代活动合理化。
```

## Step 2：世界规则合规

### 方法

1. **提取世界规则**：从 Phase 1 中识别具有约束力的规则。规则通常出现在：
   - `world_rules` / `axioms` / `constraints` 字段
   - `technology` / `society` / `economy` 描述中的限制性陈述
   - `magic_system` / `power_system` 的边界条件

2. **逐条对照**：对每条规则，扫描 Phase 2-5 中是否存在违反：
   - Phase 2：角色能力是否超出体系上限；backstory 事件是否与世界历史矛盾
   - Phase 3：脊椎事件是否在世界规则内可行
   - Phase 5：场景环境（地理、气候、技术水平）是否与 Phase 1 一致

3. **区分硬规则和软描述**：
   - 硬规则："此世界中没有 FTL 旅行" → 角色不能 FTL
   - 软描述："社会风气保守" → 角色行为激进不一定是矛盾，可能是角色特征
   - 只报告硬规则的违反

### 报告示例

```yaml
- dimension: world_rule_violation
  scene_id: null
  location: >
    phase2_character.yaml: backstory_of_elias_rourke:
    "Rourke copied the surviving evidence to physical archives"
  contradiction_pair: >
    phase1_world.yaml: "TEB established in 2089";
    phase0_conception.yaml: "referenced_dossier: London, early 21st century
    (approximately 2023)"
  source: pipeline
  issue: >
    Phase 0/2 暗示 2023 年存在 TEB 相关文件，但 Phase 1 设定 TEB 2089 年
    才成立。2023 年不可能存在 TEB 内部文件或程序。
  suggestion: >
    调整相关文件的年代，或将文件性质改为非 TEB 来源的历史档案。
```

## Step 3：引用完整性

### 方法

1. **收集 ID 映射**：
   - Phase 2：角色名称列表
   - Phase 4：序列 ID（seq_id）、转折点列表
   - Phase 5：场景 ID（scene_id）、每场景的 participants / pov

2. **检查引用闭合**：
   - Phase 5 的每个 `participants` 和 `pov` 角色 → 必须在 Phase 2 中有定义
   - Phase 4 的每个序列 → 至少在 Phase 5 中有一个对应场景
   - Phase 3 的激励事件、危机、高潮 → 在 Phase 4/5 中有对应的结构位置
   - Phase 5 的每个场景 → 能映射到 Phase 4 的某个序列（无孤立场景）

3. **scene_id pattern 校验**（schema 合规，硬约束）：
   - `phase5_scenes.yaml` 里每个 `scenes[].scene_id` 必须匹配正则 `^S\d{2}$`（`S01` / `S02` / ... / `S99`）
   - 命中违规（如 `scene_1` / `1` / `s01` / `第一场`）必须报告——下游路径模板 `pipeline/scene_{scene_id}/`、`pipeline/scenes/scene_{scene_id}.md` 会撞双前缀或非法字符，导致 dispatcher 错位、`extract_scene_card.py` 找不到产物路径
   - suggestion 一律改成 `S{N:02d}` 形式（保序：原顺序的第 N 场 → S0N）

4. **注意**：引用匹配是语义级别的，不要求字面完全相同。"Thomas Cole" 和 "Cole" 和 "Thomas" 可能指同一角色——结合上下文判断。scene_id 命名校验是字面级别（不语义化匹配）。

### 报告示例

```yaml
- dimension: reference_integrity
  scene_id: S07
  location: >
    phase5_scenes.yaml: S07 的 participants 包含 "Director Calloway"
  contradiction_pair: >
    phase2_character.yaml: 无 "Calloway" 或 "Director Calloway" 的角色定义
  source: pipeline
  issue: >
    S07 引用了未在 Phase 2 中定义的角色 Director Calloway。
    该角色可能在 Phase 2 时被遗漏，或名称发生了变化。
  suggestion: >
    确认 Director Calloway 是否需要在 Phase 2 中补充定义，
    或是否为已有角色的别称。

- dimension: reference_integrity
  scene_id: null
  location: >
    phase5_scenes.yaml: scenes[0].scene_id = "scene_1"
  contradiction_pair: >
    schema: scene_id 必须匹配 ^S\d{2}$（S01 / S02 / ... / S99）
  source: pipeline
  issue: >
    scene_id "scene_1" 违反 schema：含 "scene_" 前缀。
    下游路径模板 pipeline/scene_{scene_id}/ 会拼成 pipeline/scene_scene_1/ 双前缀，
    dispatcher / extract_scene_card.py / writer / reviser 全链路路径错位。
  suggestion: >
    按场景在 sequence_expansions[].scenes[] 出现的顺序重写为 S01 / S02 / ...；
    同步 phase4_structure.yaml / phase3_spine.yaml 中所有对该 scene_id 的引用。
```

## 通用原则

通用判据（只报告确定的矛盾 / 引用原文 / 宁漏勿误 / 建议是方向不是改法）已上提到 `SKILL.md §通用判据`——本文件只承载三步方法的具体操作细节。
