# prototype bundle schema（card + reuse_profile + seeds + text）

> **当前消费边界**：本 skill 只消费 `reference_only` prototype card，经 inspiration_ledger 进入后续 phase。基于既有作品的同人 / 续写 / 外传 / 跨风格改编走 derivative-writing 的 canon-distill 继承路径，不经本 prototype bundle。

> prototype 为目录 bundle。`reference_only` 调用仅产 card；非 `reference_only` 档仅作为外部调用方显式要求时的兼容 schema，不作为当前 derivative-writing dispatch 合同。

## 目录结构

每个 prototype 是一个目录 bundle，落到 `pipeline/references/prototypes/{slug}/`：

```
pipeline/references/prototypes/{slug}/
├── prototype_card.yaml            # 必产：原型基础描述（向后兼容旧 schema）
├── reuse_profile.yaml             # 衍生写作模式必产：推荐复用策略
├── seeds/                         # 按 reuse_mode 决定产几个 phase seed
│   ├── phase0_conception.seed.yaml
│   ├── phase1_world.seed.yaml
│   ├── phase2_character.seed.yaml
│   ├── phase3_spine.seed.yaml
│   ├── phase4_structure.seed.yaml
│   └── phase5_scenes.seed.yaml
└── text/                          # 按 reuse_mode 决定产几个；只存策略+锚点不存原文
    ├── continuity_anchors.yaml    # 称呼/专名/标志性短表达（所有衍生类型推荐）
    ├── tail_window_summary.yaml   # 续写：原作结尾状态+待续线索
    ├── scene_map.yaml             # 跨风格改编：场景功能映射（不存原文）
    └── style_fewshot_notes.yaml   # 同人：风格 few-shot 笔记
```

`{slug}` 用 ASCII kebab-case（如 `three-body-yejiwentong`、`stark-tony-mcu`）。

## reuse_mode → 产物矩阵

prototype-research 按调用方注入的 `reuse_mode` 参数决定本次产哪些文件。**调用方决定 mode，本 skill 不自行判档**：

| reuse_mode（调用方传） | 必产 | 推荐产 | 不产 |
|---|---|---|---|
| `reference_only`（默认；弱原型软约束模式）| card | — | seeds/ + text/ 全部 |
| `fan_fiction`（同人 — Phase 0/1/2 继承）| card + reuse_profile + seeds/phase0_1_2 + text/continuity_anchors | text/style_fewshot_notes | seeds/phase3_4_5 + text/tail_window + text/scene_map |
| `sequel`（续写 — Phase 0-5 继承+追加）| card + reuse_profile + seeds/phase0-5 + text/continuity_anchors + text/tail_window_summary | — | text/scene_map / style_fewshot 可选 |
| `spin_off`（外传 — Phase 0/1 继承 + Phase 2 部分）| card + reuse_profile + seeds/phase0_1 + seeds/phase2（标记 partial）+ text/continuity_anchors | text/style_fewshot_notes | seeds/phase3-5 + text/tail_window |
| `cross_style_rewrite`（跨文风 — Phase 0-5 全复用）| card + reuse_profile + seeds/phase0-5 + text/scene_map | text/continuity_anchors（专名沿用）| text/tail_window + text/style_fewshot |

调用方主要是 `derivative-writing` 内部 dispatcher（按 query 信号判 mode 后注入）；`character-design` / `plot-design` 等内的弱原型调用默认 `reference_only`。

## prototype_card.yaml（向后兼容旧 schema）

```yaml
prototype_id: PROT-{slug}
prototype_type: novel | film | drama | opera | real-person | real-location | historical-event | myth | user-provided
source_label: "原作名 / 人物名 / 事件名（人类可读）"
retrieval_path: canon | web | direct
retrieved_at: 2026-05-23T12:00:00Z   # ISO 8601
reuse_mode_recommended: reference_only | fan_fiction | sequel | spin_off | cross_style_rewrite  # 推荐档（仅参考，最终由调用方拍板）

# 风格指纹（作品 / 人物 / 戏曲原型时填）
style_signature:
  voice: "人物声音 / 作品文风（短句描述）"
  pacing: "叙事节奏"

# 关键特征（人物 / 角色原型时用）
key_traits:
  - "性格 / 行为 / 关系特征（paraphrase 不复制原文）"

# 世界规则（作品 / 设定原型时用）
world_rules:
  - "可推动情节的世界设定规则"

# 连贯性参考（用于 inspiration_ledger 软约束注入）
constraints:
  - "世界规则与人物声音的连贯性参考"

# 来源
sources:
  - "原作章节锚点 / 网页 URL / 用户提供资料标识"
```

字段语义：

| 字段 | 必填 | 说明 |
|---|---|---|
| `prototype_id` | yes | 全局唯一 ID，格式 `PROT-{slug}` |
| `prototype_type` | yes | 9 种枚举之一 |
| `source_label` | yes | 人类可读名 |
| `retrieval_path` | yes | 三路之一 |
| `retrieved_at` | yes | 时间戳 |
| `reuse_mode_recommended` | recommended | 本 skill 按 query / type 信号推荐的档；调用方可覆盖 |
| `style_signature` | optional | 作品 / 人物原型推荐填 |
| `key_traits` | optional | 人物 / 角色原型必填 |
| `world_rules` | optional | 作品 / 设定 / 历史事件原型必填 |
| `constraints` | optional | reference_only 模式核心字段；衍生模式由 reuse_profile + seeds 承载更精确语义 |
| `sources` | yes | 至少 1 条 |

## reuse_profile.yaml（衍生写作模式必产）

```yaml
# 调用方传入或本 skill 推荐的档位
recommended_mode: fan_fiction | sequel | spin_off | cross_style_rewrite

# 复用深度（设计层）
design_reuse_level: D2_inherit_phase0_2 | D3_append_edit_phase3_5 | D4_reuse_phase0_5
# - D2: Phase 0/1/2 直接继承原作（同人 / spin_off 局部）
# - D3: Phase 0-2 继承 + Phase 3/4/5 在原作基础上追加/编辑（续写）
# - D4: Phase 0-5 全部复用，仅 Phase 6 prose 重写（跨文风改编）

# 文本复用程度
text_reuse_level: T1_style_fewshot | T2_continuity_anchors | T3_scene_function_rewrite
# - T1: 仅借鉴风格（同人）
# - T2: 沿用专名+短锚点+continuity 关系（续写 / spin_off 默认）
# - T3: 保留场景功能 + 极短引用，重写 prose（跨文风改编）

# 推理依据
rationale: |
  query "续《三体》某场景" → sequel：接原作时间线继续 → Phase 0-2 继承 + Phase 3-5 追加 + Phase 6 新写

# 判档信号（debug 用）
classification_signals:
  - "query 含 '续' + 已知原作"
  - "用户明示接续原作时间线"

# 调用方下游 dispatcher 用
phase_execution_plan:
  phase0: instantiate           # instantiate | append_edit | role_promotion | rebuild | locked
  phase1: instantiate
  phase2: instantiate            # 或 role_promotion / partial_inherit
  phase3: append_edit            # 或 rebuild
  phase4: append_edit
  phase5: append_edit
  phase6: new_scenes_only        # 或 rewrite_only / write_full
  phase7: continuity_review      # 续写场景特殊：检查接缝
```

## seeds/phase{N}_*.seed.yaml

各 phase seed 完全**镜像对应 phase skill 的输出 schema**（详 phase{N} skill 内的 schema 段；本 reference 不重复 schema 全文）。derivative-writing 在执行 phase N 时按 `phase_execution_plan.phaseN`：

| plan 值 | 行为 |
|---|---|
| `instantiate` | 直接 `cp pipeline/references/prototypes/{slug}/seeds/phase{N}_*.seed.yaml → pipeline/phase{N}_*.yaml`；不调 phase skill |
| `append_edit` | 调 phase skill 的 `append_edit` mode（传 `base_yaml` 路径 = seed 文件 + `delta_request`）；产物写到 `pipeline/phase{N}_*.yaml` |
| `role_promotion` | 调 phase2-character 的 `role_promotion` mode（仅 phase2 支持）|
| `rebuild` | 调 phase skill 的常规 mode（不读 seed） |
| `locked` | 跳过；不产 `pipeline/phase{N}_*.yaml`（用 prototype 的 seed 作 SSOT；下游 phase 直接读 seed）|
| `new_scenes_only` | 调 phase6-scene-development 的 `new_scenes_only` mode（仅写续写新增场景）|
| `rewrite_only` | 调 phase6-scene-development 的 `rewrite_only` mode（按 scene_map 重写 prose）|
| `continuity_review` | 调 phase7-integration 的 `continuity_review` mode（检查接缝 + 人物连续性 + 未解决线索闭合）|

### seeds/phase3_spine.seed.yaml 特殊字段（续写场景用）

```yaml
# 原作脊椎（继承）— 镜像 phase3-spine 输出 schema
inherited_spine:
  inciting_incident: "..."
  desire_object: "..."
  controlling_idea: "..."
  dramatic_question: "..."

# 续写切入点
continuation_point: "ch12_end"   # 原作章节 / 时间锚点
unresolved_threads:
  - thread_id: "T-revenge"
    description: "主角对反派的复仇未达成"
    state_at_continuation: "刚得到关键线索，未行动"

# 续写延伸约束（phase3-spine append_edit 模式读）
append_constraints:
  locked:                          # 不可推翻
    - "主角已确认反派身份"
    - "副 CP 已分手"
  editable:                        # 可在续写中调整
    - "复仇方式"
    - "新事件触发"
  append_only:                     # 只能在原 spine 末尾追加
    - "新 conflict 必须在 unresolved_threads 之后展开"
```

### seeds/phase2_character.seed.yaml 特殊字段（spin_off 用）

```yaml
# 原主角（spin_off 后降为配角 / 背景）
canonical_protagonist:
  name: "原主角名"
  role_in_spin_off: "background | supporting | cameo"
  preserved_traits: ["..."]
  visibility_limit: "原作已明确的行为不可推翻"

# 升格的新主角（原配角）
role_promotion:
  source_role: supporting_cast
  target_role: protagonist
  source_character_name: "原配角名"
  preserved_traits:
    - "原作中已确认的性格 / 关系"
  expanded_private_conflicts:
    - "原作未写的内心冲突可在此扩展"
  canon_visibility_limits:
    - "原作已明确的公开行为不能推翻"
    - "原作已确认的关系性质不能反转"
```

## text/continuity_anchors.yaml（所有衍生模式推荐）

```yaml
# 称呼与专名（writer 不可改写）
proper_nouns:
  - canonical: "叶文洁"
    aliases: ["叶教授", "叶女士"]
    no_translate: true

# 标志性短表达（≤ 15 字短引；可保留沿用）
signature_phrases:
  - phrase: "不要回答！不要回答！不要回答！"
    source: "《三体》第一部第 27 章"
    usage_policy: "续写如涉及向宇宙发信号场景可保留沿用"

# canonical 关系（writer 不可改写关系性质）
canonical_relationships:
  - between: ["叶文洁", "杨冬"]
    nature: "母女"
    inalterable: true
```

## text/tail_window_summary.yaml（续写专用）

```yaml
# 原作结尾状态（不存原文，只存状态摘要）
ending_state:
  last_scene_summary: "主角在山顶望向远方，等待援军"
  protagonist_emotional_state: "决意但忧虑"
  protagonist_physical_state: "重伤待愈"
  setting: "雪山顶第三日"
  time_of_day: "黄昏"

# 未解决线索（续写延展锚点）
unresolved_threads:
  - id: "T-rescue"
    description: "援军是否会到"
    must_resolve_in_continuation: true
  - id: "T-villain"
    description: "反派下落不明"
    must_resolve_in_continuation: false   # 可留为下一卷悬念

# 续写起点建议
continuation_anchor:
  recommended_start: "援军到达瞬间 / 反派现身瞬间 / 主角伤势恶化某瞬间"
  must_not_skip: "雪山场景必须收束（不要直接切到山下）"
```

## text/scene_map.yaml（跨风格改编专用）

```yaml
# 原作场景功能清单（不存原文，存功能与关键事实）
scenes:
  - source_scene_id: "ch03_s05"
    scene_function: "主角第一次意识到代价"
    involved_characters: ["主角", "导师"]
    canon_facts:
      - "导师在此场说出'权力的代价'"
      - "主角第一次拒绝权力"
    emotional_arc: "犹豫 → 觉醒"

    # 改编时保留 / 重写策略
    rewrite_policy:
      preserve: ["导师角色", "拒绝权力的决定"]
      allow_rewrite: ["对白具体措辞", "场景描写细节", "时长占比"]
      style_target: "轻喜剧化（增加误会 + 滑稽 mismatch）"

# 允许的极短引用（≤ 15 字 / 场景）
allowed_short_quotes:
  - "权力的代价你担不起"   # 关键 callback
```

## text/style_fewshot_notes.yaml（同人专用）

```yaml
# 风格指纹（同人创作风格参考 — 不是抄原文）
voice_markers:
  - "短句 + 留白"
  - "对白少标点（破折号代替）"
  - "心理描写贴近第三人称限知"

pacing_markers:
  - "动作场景节拍快（每行 1-2 拍）"
  - "回忆插叙节拍慢（每段 1 长拍）"

# 关键修辞（推荐借鉴形式不复制内容）
rhetorical_devices:
  - "三段递进列举"
  - "明喻而非暗喻"

# 不复制清单（避免抄袭）
do_not_copy:
  - "原作长段落"
  - "原作连续超 20 字的句子"
  - "原作命名独创的术语（除非 continuity_anchors 已列）"
```

## 样例 bundle — 续《三体》sequel 模式

```
pipeline/references/prototypes/three-body-yejiwentong-sequel/
├── prototype_card.yaml       # reuse_mode_recommended: sequel；retrieval_path: canon
├── reuse_profile.yaml         # recommended_mode: sequel; design_reuse_level: D3; phase_execution_plan: phase0-2 instantiate / phase3-5 append_edit / phase6 new_scenes_only / phase7 continuity_review
└── seeds/
    ├── phase0_conception.seed.yaml    # 三体世界 / 黑暗森林控制思想
    ├── phase1_world.seed.yaml          # 三体设定 / ETO / 红岸 / 智子封锁
    ├── phase2_character.seed.yaml      # 叶文洁 / 罗辑 / 章北海 等
    ├── phase3_spine.seed.yaml          # inherited_spine + continuation_point: "黑暗森林末" + unresolved_threads
    ├── phase4_structure.seed.yaml      # 原三幕 + 续写续接段
    └── phase5_scenes.seed.yaml          # 原场景清单 + 续写新场景占位
└── text/
    ├── continuity_anchors.yaml         # 叶文洁/罗辑/智子等专名 + 经典短句
    └── tail_window_summary.yaml         # 黑暗森林结尾状态 + 未解决线索
```

## 样例 — 同人 fan_fiction 模式

```
pipeline/references/prototypes/harry-potter-marauders-fanfic/
├── prototype_card.yaml
├── reuse_profile.yaml         # recommended_mode: fan_fiction; design_reuse_level: D2; phase_execution_plan: phase0/1/2 instantiate / phase3+ rebuild
└── seeds/
    ├── phase0_conception.seed.yaml    # HP 世界观 / 魔法体系
    ├── phase1_world.seed.yaml          # 霍格沃茨 / 魔法部 / 巫师社会
    └── phase2_character.seed.yaml      # James Potter / Lupin / Sirius / Lily 等 OC 可挂在末尾
└── text/
    ├── continuity_anchors.yaml         # 魔法咒语 / 学院名 / 经典魔法生物
    └── style_fewshot_notes.yaml         # 罗琳风格特征 paraphrase
```

## 样例 — 跨风格改编 cross_style_rewrite 模式

```
pipeline/references/prototypes/mudanting-romcom-rewrite/
├── prototype_card.yaml
├── reuse_profile.yaml         # recommended_mode: cross_style_rewrite; design_reuse_level: D4; phase_execution_plan: phase0-5 instantiate / phase6 rewrite_only / phase7 style_review
└── seeds/
    ├── phase0_conception.seed.yaml    # 牡丹亭原构想（梦中相会 / 生死爱情）
    ├── phase1_world.seed.yaml          # 明代背景 / 戏曲程式
    ├── phase2_character.seed.yaml      # 杜丽娘 / 柳梦梅 / 杜母 / 春香
    ├── phase3_spine.seed.yaml
    ├── phase4_structure.seed.yaml
    └── phase5_scenes.seed.yaml
└── text/
    ├── scene_map.yaml                   # 各场景功能 + rewrite_policy.style_target: "轻喜剧 / 现代都市"
    └── continuity_anchors.yaml          # 杜丽娘 / 柳梦梅 等专名沿用
```

## 字段填写工作流（按调用方注入的 reuse_mode）

详 [`../SKILL.md`](../SKILL.md) §3 "按 reuse_mode 执行" 段。

## 不写什么

- 不复制原作原文长段——只 paraphrase + 锚点 + 极短引（≤ 15 字 / 句）
- 不写"该如何续写 / 改编"——那是 derivative-writing 的事
- 不写质量评判——本 skill 是中性资料层
- seed yaml 不包含 phase skill **执行细节**（如 phase2-character 的 backstory 生成规则）；只包含 phase 输出 schema 镜像数据
- text bundle 不存大段原文（避免变 prose 复写器）；最多 ≤ 15 字短引 + 状态摘要 + 策略锚点
