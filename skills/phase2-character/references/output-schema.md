# Phase 2 输出 Schema

交付物文件：`pipeline/phase2_character.yaml`

```yaml
protagonist:
  name: 姓名
  characterization:
    age: 年龄
    gender: 性别
    occupation: 职业
    appearance: 外貌特征
    background: 社会背景摘要
  desire_system:
    conscious: 自觉欲望（明确追求的具体目标）
    unconscious: 不自觉欲望（真正需要但不自知的）
    core_flaw: 核心缺陷（阻碍获得真正所需的弱点）
  character_arc:
    mode: transformative | revelatory | static | degenerative
    start_state: 初始状态（或 revelatory/static 下的稳定核初见）
    end_state: 最终状态（或 revelatory 下稳定核显形后的读者/人物认知；static 下同 start_state）
    transformation: 轨迹核心描述——transformative/degenerative 写转变 / 退化核心；revelatory 写揭示了什么稳定核、怎么揭示；static 写稳定核是什么、在压力下如何维持
  characterization_vs_truth:
    surface: 外在人物塑造（别人眼中的他）
    deep_truth: 压力下暴露的性格真相
    gap: 两者之间的裂隙描述
  backstory:
    - event: 过去事件描述
      impact: 对当前人物的影响
      narrative_use: 可如何被 Phase 4-6 采收（闪回/对话/动机）
  daily_life: 主角在这个世界里的日常：怎么吃饭、工作、消遣、与人打交道
  voice_traits:
    vocabulary: 词汇特征描述
    syntax: 句法特征描述
    rhetoric: 修辞特征描述
    rhythm: 节奏特征描述
    catchphrase: 口头禅（可选）
  empathy_mechanism: 读者认同主角的理由
  voice_boundaries: "角色不会怎么说话的负空间描述（例：'不会在每次恐惧时都用技术隐喻'）"
  inner_capacity:                    # required
    primary: 幻想 | 写作 | 共情 | 信任 | 修复 | 信仰 | 自我说服 | <自定>
    why_load_bearing: 1 句——为什么这能力是 ta 的存在基础
    loss_trigger: 什么场景 / 事件会触发能力失灵
    loss_signal: 失灵时如何在正文中显示——必须是可执行的具体动作 / 反应缺席
  recognition_path:                  # optional
    primary_method: direct_action | object_evidence | second_hand_story | misread_evidence | procedural_record | silence | bodily_reaction
    first_false_reading: 读者或其他角色最初可能误读什么
    correction_method: 后续如何修正
  backstory_harvest:                 # optional
    method: embedded_storyteller | object_trace | witness_chain | contradictory_testimony | sensory_trigger | official_record
    carrier: 具体承载物 / 讲述者 / 证据
    withheld_part: 故意不交代的部分
  misread_matrix:                    # optional, list of observer→target rows
    - observer: 谁
      target: 误读谁
      evidence_seen: 看见 / 听见 / 拿到的证据
      wrong_conclusion: 错误结论
      narrative_value: 制造反讽 / 冲突 / 迟滞 / 悬念
  canon_archetype:                   # optional
    - id: INS-A01
      weight: dominant
    - id: INS-A02
      weight: secondary
      merge_boundary: "只学习 X，不学习 Y"

antagonist:
  name: 姓名
  relationship_to_protagonist: 与主角的关系
  power_source: 威胁主角的能力来源
  motivation: 从对手视角看的合理动机
  desire: 对手追求的目标
  voice_traits:
    vocabulary: 词汇特征描述
    syntax: 句法特征描述
    rhetoric: 修辞特征描述
    rhythm: 节奏特征描述
    catchphrase: 口头禅（可选）
  voice_boundaries: （可选）对手声音的负空间描述
  subjectivity_object:               # optional（antagonist 若有退场场景则建议填）
    what: 具体物件描述
    created_when: 什么时候该角色创造的
    where_it_lives: 在故事中以什么形式存在（藏在脑海 / 写在纸上 / 留给他人 / 物理实体）
    potential_use: 如果该角色面临退场场景，此物件如何成为退场承载
  canon_archetype:                   # optional
    - id: INS-A04
      weight: dominant

deuteragonist: null
# optional。若存在，必须使用与 protagonist 完全相同的字段结构；不允许只写 name。
# deuteragonist.character_arc.mode 与 protagonist.character_arc.mode 使用同一 enum 和同一必填规则；canon_archetype 同样 optional。

supporting_cast:
  - name: 姓名
    function: 叙事功能
    relationship: 与主角的关系
    voice_traits_summary: 声音特征摘要（1-2句）
    subjectivity_object:             # optional（victim 类 / 会退场的配角建议填）
      what: 具体物件描述
      created_when: 什么时候该角色创造的
      where_it_lives: 在故事中以什么形式存在（藏在脑海 / 写在纸上 / 留给他人 / 物理实体）
      potential_use: 如果该角色面临退场场景，此物件如何成为退场承载

contrast_axes: 主要角色之间的极化对比描述（在同一情境下反应如何截然不同）
relationships:
  power_dynamics: 权力动态描述
  key_tensions:
    - 关键关系张力
  potential_shifts:
    - 关系可能的转变
```

## 字段说明

| 字段 | 必需 | 下游使用 |
|------|------|---------|
| `protagonist.characterization_vs_truth` | 是 | Phase 5（设计揭示性格真相的场景）、Phase 6（压力下行为的依据） |
| `protagonist.backstory` | 是 | Phase 4（危机设计可引用过去事件）、Phase 6（闪回/对话素材） |
| `protagonist.daily_life` | 否 | Phase 6（叙事细节素材） |
| `protagonist.desire_system` | 是 | Phase 3（构建故事脊椎）、Phase 4（设计危机两难） |
| `protagonist.voice_traits` | 是 | Phase 6（对白差异化）、dialogue-craft（潜台词设计） |
| `protagonist.character_arc` | 是 | Phase 4（弧光轨迹在高潮体现；transformative/degenerative=转变、revelatory=显形、static=在极端压力下保持）；**消费者** character-persona（派生 runtime 角色包 + state.md，按 mode 分支）；Phase 5 通过 value_start/end 语义间接消费轨迹语义，对齐由 mode_alignment companion 校验 |
| `protagonist.character_arc.mode` | 是 | **phase-local operational enum**——声明人物轨迹类型。enum：`transformative`（经典弧光，从起点到终点的可识别变化）\| `revelatory`（暴露：人物稳定核原本就在那里，故事做"显形"不是"改造"；**vs static**——有无"揭示稳定核"的组织线，有即 revelatory）\| `static`（静态：不以转变为组织力，也不以逐步显形为主要组织力；固定透镜 / 讽刺常量 / 见证者 / 反结构稳定存在；**vs revelatory**——没有"揭示稳定核"的组织线，只是固定存在）\| `degenerative`（退化：堕落 / 悲剧 / 不可逆衰败轨迹）。**消费者**：character-persona（Phase 2 Step 7 生成 runtime 角色 Skill 包 + state.md 按 mode 分支派生）；Phase 5 通过 value_start/end 语义间接消费 mode 语义，对齐由 mode_alignment companion 校验。**既有产物 fallback**：`phase2_character.yaml` 的 `character_arc` 缺 `mode` 字段时兼容层按 `transformative` 解释，新生成路径必须显式依据角色性质选择最贴近的一类，不允许以"不确定"为由跳过判定 |
| `antagonist` | 是 | Phase 3（对抗力量设计）、Phase 5（对手出现的场景） |
| `deuteragonist` | 否 | 双主角 / 守护者形态时使用（结构同 protagonist；若存在则 `character_arc.mode` 必填）；消费方与 protagonist 等价（Phase 3/4/5/6 各处按 optional 处理）；下游 character-persona 按 optional 派生 runtime skill 包 |
| `supporting_cast` | 是 | Phase 5（场景人物分配）、Phase 6（对白涉及的角色） |
| `relationships` | 否 | Phase 5（关系动态影响场景编排） |
| `protagonist.voice_boundaries` | 否 | Phase 6（负空间约束：角色不会做什么） |
| `protagonist.recognition_path` | 否（enrichment） | Phase 6（把主角"被认出"的方式落到 action/evidence/转述/误读/沉默/身体反应，避免被解释化）；7-enum `primary_method`；下游暂未硬消费，纯数据层 |
| `protagonist.backstory_harvest` | 否（enrichment） | Phase 4-6（指明 backstory 用哪种采收方式呈现：内嵌讲述者 / 物件痕迹 / 见证链 / 矛盾证词 / 感官触发 / 官方记录）；6-enum `method`；下游暂未硬消费 |
| `protagonist.misread_matrix` | 否（enrichment） | Phase 6（提供 observer→target 误读对，制造反讽 / 冲突 / 迟滞 / 悬念）；list 结构允许 N×N 对；下游暂未硬消费 |
| `protagonist.canon_archetype` / `deuteragonist.canon_archetype` / `antagonist.canon_archetype` | 否 | 引用 `pipeline/inspiration_ledger.yaml` 中 `type=archetype` 的 INS-* 卡；字段不存在或空数组时走原创路径；字段存在时由资产校验检查引用闭环 |
| `protagonist.inner_capacity` | 是 | character-persona（派生 `## 内在生存能力` 章节）、Phase 6（写"失去"场景时落 loss_signal 的具体反应缺席）。4 字段：`primary` 能力名 / `why_load_bearing` 1 句根基说明 / `loss_trigger` 失灵触发 / `loss_signal` 失灵的可观察显示 |
| `antagonist.voice_boundaries` | 否 | 对手声音的负空间约束 |
| `antagonist.subjectivity_object` | 否（有退场场景时建议填） | character-persona（派生 `## 主体性物件` 章节）、Phase 6（退场场景的承载物——避免角色"消失"为空白）。4 字段：`what` / `created_when` / `where_it_lives` / `potential_use` |
| `supporting_cast[].subjectivity_object` | 否（victim 类 / 会退场配角建议填） | 同上 antagonist.subjectivity_object |

### canon_archetype（optional）

引用 `pipeline/inspiration_ledger.yaml` 中 `type=archetype` 的 INS-* 卡。可挂在 `protagonist` / `deuteragonist` / `antagonist` 角色节点下，字段不存在或空数组时不报错。

| 子字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | 必填 | INS-A* 格式 ID |
| `weight` | enum | 必填 | `dominant` / `secondary` |
| `merge_boundary` | string | weight=secondary 时必填 | 与 dominant 原型的合并边界 |

**约束**（脚本 hard gate 见 `verify_phase2_assets.py`）：

- 数组长度 0 / 1 / 2 允许；≥3 报错
- 长度 = 1 时必须为 `dominant`
- 长度 = 2 时必须 1 dominant + 1 secondary，且 secondary 必须填写 `merge_boundary`

## 角色资产：双层结构

Phase 2 完成后，通过调用 `character-persona` 构建器生成两类角色资产：

### 1. 运行时 Skill 包（主资产）

```
pipeline/story-character-skills/
├── .claude/skills/
│   └── {role-slug}/           # 直接以 role-slug 命名（如 li-an）
│       ├── SKILL.md           # 角色人格定义（静态）
│       ├── state.md           # 主观状态（动态，语义归角色 agent，物理写入归 orchestrator）
│       ├── references/
│       │   └── backstory.md   # 幕后故事（可选）
│       └── build-meta.yaml    # 构建元数据
└── build-report.md            # 构建决策记录
```

- 通过 `claude --add-dir pipeline/story-character-skills` 挂载
- subagent 通过 `skills` 字段按需加载，orchestrator 不直接读取
- 命名隔离由工作目录承担：每个 query 的 `pipeline/` 互不可见，`role-slug` 只需在单 query 内唯一
- `story-slug` 仅作为 build-report 标题与 build-meta 元数据保留（独立创作用 phase0 title，数据集创作用 query_index），**不参与 skill 命名**

### 2. 兼容 adapter（派生资产）

`pipeline/characters/{角色名}.md`，每角色一个文件。该文件：
- 由 character-persona 从 SKILL.md 单向自动生成，**不可手改**
- 供现有消费方（Phase 6 写作、design-validation、审稿 B 组）读取
- 包含身份、欲望、声音、边界、**人物轨迹**——从 SKILL.md 对应章节提取（adapter 的轨迹段标题保留 `## 弧光` 作为 compatibility alias，下游消费方按此标题定位内容；但内容来源是 SKILL.md 的"## 人物轨迹"段，含 mode / start_state / end_state / 轨迹机制四字段。static/revelatory 角色的该段不是"变化轨迹"）
- 不包含 contrast_axes、relationships 等分析字段（这些留在 YAML 中供下游 Phase 结构化读取）

### 生成时机

Phase 2 步骤 7 调用 `character-persona`。详见 `character-persona/SKILL.md`。
