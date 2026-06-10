# Phase 0 输出 Schema

交付物文件：`pipeline/phase0_conception.yaml`

```yaml
premise: 故事的核心前提（如果……将会发生什么？）
core_value:
  positive: 正面价值极
  negative: 负面价值极
  spectrum:
    positive: 正面
    contradictory: 矛盾
    contrary: 相反
    negation_of_negation: 否定之否定
controlling_idea:
  value: 正面或负面价值判断
  cause: 原因/条件
  full_statement: "[价值] 因为/当 [原因]"
  type: idealistic | pessimistic | ironic
genre:
  primary: 主导类型
  conventions:
    setting: 常规背景
    characters: 常规角色
    events: 常规事件
    values: 常规价值负荷
primary_drive: shift | reveal | observe | mix
target_length:
  words: 8000             # 用户参考目标（不是阻断硬数字）
  range: 6000-10000       # 描述性区间，写作不必落入
originality_statement:
  unique_angle: 本故事的独特切入点
  cliches_to_avoid:
    - 要规避的陈词滥调
requirements:
  - id: R1
    text: 硬约束原文
    target_phase: 5
reference_materials:
  summary: 用户提供素材的一句话概述
  key_details:
    - 对创作有价值的具体细节（摘要，非原文复制）
  applicable_phases:
    - phase1
    - phase6
style_directives:
  - 作品层面的风格要求（如"金庸武侠风格"、"现实主义细节描摹"）
craft_targets:
  dominant_carriers:
    - 该参考作品常用什么承载情绪 / 主题：动作、物件、程序文体、POV 遮蔽、日常闲聊等
  omission_style:
    - 哪些内容常被省略：心理、过程、解释、关键画面、历史背景
  scale_strategy: 高潮倾向（放大 | 收缩 | 反高潮 | 对位 | 混合）
  characterization_method:
    - 人物主要通过自述 / 行动 / 他人证词 / 误读 / 物件痕迹 / 压力选择中的哪一种被认识
  narrator_position:
    primary: "enum: intimate_first | reminiscing_first | reporter_third_close | reporter_third_distant | archival_zero | omniscient_satirist | bilingual_drifter | unreliable_first"
    permission: 字符串
    examples_in_reference_work:
      - 字符串
canon_reference_profile:
  desired_domains:
    - world_rule
    - reveal_structure
    - protagonist_archetype
    - scene_carrier
  avoid_domains:
    - prose_style_imitation
  user_reference_materials:
    - work: "斯通纳"
      stance: prefer
      reason: "register 接近主角"
```

## 字段说明

| 字段 | 必需 | 下游使用 |
|------|------|---------|
| `premise` | 是 | Phase 1（设定需围绕前提）、Phase 3（脊椎需回应前提） |
| `core_value` | 是 | Phase 3（脊椎围绕核心价值的正负极——`spine_mode=desire` 下=价值脊椎；其他 mode 下作为参考性正负极锚点）、Phase 4（高潮体现轨迹跃迁——desire=价值翻转 / information=真相披露 / motif=母题变奏）、Phase 5-6（每场景有**实质性叙事增量**——desire=价值变化 / information=信息揭示 / motif 或观察驱动=关系或感知重构；语义随 `spine_mode` 解释）|
| `controlling_idea` | 是 | Phase 4（高潮必须表达主控思想）、Phase 7（硬约束终验） |
| `genre` | 是 | Phase 1（类型惯例影响设定）、Phase 4（结构遵循类型常规） |
| `primary_drive` | 是 | **全局默认**——声明"这本故事主要靠什么前进"，下游 Phase 2/3/5 据此翻译为各自 phase-local mode（非条件分支，近端消费）；mode_alignment companion report 据此判对齐。enum：`shift`（变化驱动／麦基默认）\| `reveal`（揭示驱动／侦探·档案·观念显影）\| `observe`（观察驱动／氛围·旅行·群像）\| `mix`（多驱动共同主导，不是"未定"——填 mix 时 phase-local mode 仍须各自落到明确值）。**`mix` 组成关系持久化义务**：当 `primary_drive=mix` 时，**必须**在本 YAML 的 `originality_statement.unique_angle` 字段写清组成驱动及其关系（哪些驱动共同主导、各自承担什么）；不要求主次，但要求组合**可被复盘**。design-validation 只能读 YAML 文件，未持久化的主对话解释对 mode_alignment 无效——`originality_statement.unique_angle` 未写组成关系且 Phase 2/3/5 无法自洽组合时才 `suspicious_divergence`。**既有产物 fallback**：`phase0_conception.yaml` 缺此字段时兼容层按 `shift` 解释，下游读取既有产物不视为缺必需字段 |
| `target_length` | 是 | Phase 5（场景数量规划——参考目标，不强制单场景字数分配）、Phase 6（写作时知道目标即可，**不为凑字数做 second pass**） |
| `originality_statement` | 否 | Phase 7（原创性验证） |
| `requirements` | 条件 | 仅在用户有显式硬约束时生成。Phase 5（场景分配）、Phase 7（`requirements_status[]` 终验） |
| `reference_materials` | 条件 | 仅在用户提供背景素材时生成。Phase 1（融入 `domain_knowledge`）、Phase 6（创作参考） |
| `style_directives` | 条件 | 仅在用户有作品风格要求时生成。Phase 6（与 `voice_traits` 共同指导写作） |
| `craft_targets` | 条件 | 仅在生成 `reference_materials` 时同期生成。Phase 6（writer Craft Preflight 选 carrier 时直接参考） |
| `canon_reference_profile` | 否 | Phase 1+（design-doc-reference 的 query refine 方向 hint）；字段缺席时退到 genre / primary_drive 推方向。Phase 1-5 一律先调用一次 design-doc-reference，由 skill 返回值决定降级（无关闭档）|

### canon_reference_profile（optional）

| 子字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `desired_domains` | string[] | optional | 用户希望从 canon 学什么 |
| `avoid_domains` | string[] | optional | 用户明示不要从 canon 学什么（模型据此自主收敛，不是关闭开关）|
| `user_reference_materials` | object[] | optional | 用户主动指定参考 / 禁用作品；每项含 work / stance ∈ {prefer, avoid} / reason |
