# Phase 5 输出 Schema

交付物文件：`pipeline/phase5_scenes.yaml`

> **scene_card 概念 vs 物理**：scene_card 是 L2 设计中的**逻辑单位**（每场景一个）；**物理落地**为本文件交付的 `pipeline/phase5_scenes.yaml` 的 `scenes[]` 列表——每元素对应一个 scene_card。不存在"每场景独立文件"的物理布局。

```yaml
sequence_expansions:
  - seq_id: ARC1-SEQ1
    scenes:
      - scene_id: S01
        arc_id: ARC-1              # 派生字段：从 seq_id 归属 Arc 获得
        title: "场景标题"
        pov: "视角角色名"
        narration_style: close-third  # close-third=紧贴 pov 角色内心 | third-omniscient=全知叙述者 | first=第一人称
        participants:
          - "角色 slug"
        location_time: "本场景时空坐标（如 '破宅 / 黄昏'）"
        conflict: "核心冲突描述"
        value_start: "开始时的关键叙事状态（语义按 spine_mode 解释：desire=价值状态 / information=信息或认知状态 / observe-motif=关系或感知状态；schema 字段名保留作向后兼容）"
        value_end: "结束时的关键叙事状态（语义同上，必须与 value_start 实质不同——按当前 mode 的状态语义判定）"
        reader_track: "本场读者跟随的单一阅读问题 / 行动线（如『小龙女判断陌生人证据是否可信，并决定是否纳入寻找杨过的行动』）"
        scene_tasks:
          - abstract_function: "角色第三层自欺话术被击穿"
            physical_carrier:
              - text: "杯沿停在唇边却没喝"
                function_link: "杯沿停顿 → 自欺裂缝可观察化"
            reader_yield:
              - "关系压力"
              - "自欺破裂"
            rendering:
              default: summary
              expand_only_if: "动作改变关系 / 危险 / 欲望"
        inspiration_refs:           # optional，引用 inspiration_ledger 中 type=pattern 的 INS-* 卡
          - INS-001
          - INS-007
        handoff: "衔接到下一场景的方式"
        beat_direction: "（仅关键场景）节拍的大致方向和鸿沟位置"

        # —— 以下 5 字段全部 optional（缺字段时 writer 走通用 Craft Preflight，不强约束）——
        pov_constraint:
          can_perceive: [字符串]
          cannot_perceive: [字符串]
          intentional_blind_spot: "关键遮蔽（描述）"

        craft_carrier:
          type: "object | bodily_action | silence | procedural_form | second_hand_story | sensory_shock | scale_shift | expectation_reversal"
          concrete_anchor: "具体物件 / 动作 / 声音 / 文体"
          replaces: "它替代了哪段解释 / 心理 / 背景"

        # world_disclosure_plan：授权 / 禁止 writer 借物披露世界规则的边界。
        # 缺省 = 沿用旧"不解释一切"约束。
        # 详细语义与渲染契约见下方 `world_disclosure_plan` 小节。
        world_disclosure_plan:
          forbid:
            - "终极成因（病原 / 战争 / AI / 神秘灾变到底是什么）"
            - "救援 / 未来 / 重建宏大总结"
          allow:
            - "主角第一人称口吻披露崩坏过程（信号 → 水电 → 人声依次消失等）"
            - "行动规则（可信资源的判定 / 物理衰退的判定 / 幸存者行为规则）"
            - "由眼前物 / 动作触发，极简短句即止；不做百科说明"

        omission_plan:
          - "本场故意不解释什么"

        irreversible_action:
          - "一个可见且不可撤销的动作"

        reveal_method:
          type: "direct_action | indirect_evidence | witness_chain | object_trace | official_record | overheard_fragment | bodily_reaction | delayed_revelation"

        # —— 以下 4 字段全部 optional（缺字段时 writer 走通用 Craft Preflight，不强约束）——
        narrator_distance:
          mode: "intimate_first | reminiscing_first | reporter_third_close | reporter_third_distant | archival_zero | omniscient_satirist | bilingual_drifter | unreliable_first"
          # enum 与 phase0 narrator_position.primary 同源（phase0 锁定 → phase5 同名继承）
          reason: "为什么选这个距离 — 写一句"

        scale_inversion:
          used: true        # true | false
          bridge: "连接大命题与小物件的具体桥（粮票 / 二向箔 / 5kg 生态球 / 一只手 / 一句回家）"

        precedent_mirror:
          mirrors_scene: "S_XX | null"
          mirror_kind: "failure | success | irony | null"
          preserved_anchors: ["同样的动作 / 物件 / 命令词清单"]
          removed_premises: ["前者成功 / 失败 / 完整的前提，本场景被删除的"]

        # 高潮场景的 pattern 选择 — writer 只执行被选中的 pattern，
        # climax=true 不再触发自动加载全部高潮模板
        climax_pattern:
          primary: "layered_revelation | ineffable_realization | passive_death | mask_hard_cut | unfinished_action | anti_epic_failure | scale_shrink | null"
          secondary: "同上或 null"
          forbidden_moves: ["不得追加解释链", "不得宏大辞藻堆叠"]
          # 仅 scene_card.climax / sequence_climax / arc_climax = true 时显式选择；
          # 缺字段时 writer 不加载任何高潮模板（fallback = 走通用 Craft Preflight）

        # 对白偏好的 scene 级 hint；writer 在 dialogue-craft 工坊阶段消费。
        # 缺字段 = writer 走通用 dialogue 设计（不强约束）。
        dialogue_hints:
          - speaker: "<角色名 | null（表示对全场 hint）>"
            attribution_strategy: "neutral_tag | action_bridge | object_bridge | listener_reaction | omitted_tag"
            # 5 enum：句子在 narrative 中怎么被标注（纯归属策略）
            dialogue_form: "diagnostic_verdict | single_word_winner | caretaker_tone_violence | monosyllable_confession | co_creation_as_confession | null"
            # 5 enum + null：对白本身呈现的形态
            reason: "为什么本场偏好这个组合 — 写一句（可选）"

        # 反先验场景标记：本场景的核心设计 = "高情感语境中嵌入不合适的日常行为"
        # 参考：《挪威的森林》scene 10 — 医院 + 黄瓜 + 欧里庇得斯。
        # used=true 时 phase6 dispatcher 触发 fast-path：orchestrator 读子字段
        # 拼额外约束注入 writer dispatch prompt。
        # 缺字段 / used=false → writer 不收特殊注入，走通用 Craft Preflight。
        counter_prior_scene:
          used: true                                  # true | false
          kind: "ritual_with_food | hospital_with_lecture | death_with_chore | farewell_with_chess | custom"
          mundane_action: "吃黄瓜 / 讲课 / 整理衣服 / 闲聊（具体描述：让 writer 知道嵌入的日常动作是什么）"
          emotional_context: "临终 / 崩溃 / 高压告别 / 灾难现场（高情感语境）"
          forbidden_moves:
            - "不得把日常动作解释成象征"
            - "不得在动作后追加心理解释"

        # 写作层 AI pattern 预防：声明本场 writer 应主动规避的风险族 + 本场特化正向策略。
        # used=true 时 scene_card.md 渲染 `## 写作层 AI pattern 预防 (prose_risk_contract)` 段；
        # 缺字段 / used=false → 不渲染，writer 走通用 Craft Preflight。
        prose_risk_contract:
          used: true                                  # true | false
          risk_families:                              # 本场 high-risk family；family 名锚 ai-cliche-patterns.md 现有条目（F 类 snake_case 或 A-G 中文短语）
            - "动作清单化"
            - "psychological_overfill"
            - "情绪库存短语"
          positive_strategy:                          # 本场特化策略；通用修法 writer 通过 prose-craft skill 查 ai-cliche-patterns.md
            - "本场社交调度场景，动作合并必须落到关系压力变化点（不是单纯减字数）"
            - "本场短比喻只在感官替代功能成立时出现（不是通用『少用比喻』）"
          bad_shape_examples:                         # 可选；1-3 条；"长相"参考，writer 遇同结构形态改写而非字面规避
            - "他停下，低头，看门缝，伸手，推开"
            - "像某种没有声音的重量"

tension_curve:
  description: "张力曲线的文字描述"
  peaks:
    - "高张力场景 ID"
  valleys:
    - "低张力场景 ID"

scene_causal_chain: "S01 →（因为…）S02 →（因此…）S03 → ..."
```

## scene_task 字段（对象结构）

每条 scene_task 必含四字段（schema error 阻断缺一）：

```yaml
scene_task:
  abstract_function: <str>            # 允许保留戏剧意图概括（"角色第三层自欺话术被击穿"）
  physical_carrier:                   # 必须 ≥1 项可观察戏剧承载物（list of object）
    - text: <str>                     # 载体描述（"杯沿停在唇边却没喝"）
      function_link: <str>            # 对应 abstract_function 子节点 ID 或描述；非空非 placeholder（不接受 "TODO" / "待定" / "" / "-"）
  reader_yield: [<str>, ...]          # 必须 ≥1 项读者收益类型
  rendering:
    default: summary | expand
    expand_only_if: <str>             # expand 条件（"动作改变关系 / 危险 / 欲望"）
```

### 必备字段校验

任一字段缺失或为空 list → schema error。

### abstract_function 字段 field-specific pattern（其他字段禁用心理装置词）

仅 abstract_function 字段允许出现心理装置 / 抽象词。其他字段（task 名 / physical_carrier.text / reader_yield）按以下 pattern 识别 → error：

- **pattern A**：抽象名词 + 动作类后缀（完成 / 呈现 / 显形 / 落地 / 到位 / 形成 / 进入临界 / 出现裂缝）
- **pattern B**：phase 字段名整词命中（language_boundaries / converts_into / dramatic_function / 内驱力 / 节拍组 / 转场 / 母题级）
- **pattern C**：心理装置名独立做主语或谓语（装置 / 系统 / 边界 / 机制 / 模式 单独成主语 + 抽象动词）

**放行**（不命中即合法）：实体名 + 具体修饰使其成为具体物（"火药装置被搬上案" / "边界线被第一次越过" / "自欺装置首次裂缝——他第一次开漆匣"）。

### physical_carrier 正例正则

每条必须含 ≥1 个可观察元素：具体物件名 / 动作链 / 引号台词 / 具体感官词 / 时间标记。

### anti-action_log 检测（function_link 字段关系）

三条件同时：
1. ≥3 条同主语连续动作短句
2. 每条扁平结构（无戏剧张力词）
3. **任一 physical_carrier 项的 function_link 为空 / placeholder → error**

## scene_tasks 语义（重要）

Phase 5 新产物必须使用上方 scene_task 对象结构。历史字符串列表仍由下游渲染兼容，但不作为新输出格式。

```yaml
scene_tasks: |
  本场景必须完成的叙事工作 + 创意灵感 list。
  每条按双 marker 格式：[priority][reader_layer] 任务描述。
  写"叙事工作"（事件进展 / 关系变化 / 认知翻转）或"创意灵感"（具体写作指示 / 惊艳点 / 留白设计）。
  ❌ 不写抽象读者反应（任何"让读者 X" / "读者会感到 X" / "营造 X 氛围" / "产生 X 效果"等以读者反应 / 氛围为目标反推的表述）——模型不知道读者怎么想，写事件 / 写进展 / 写具体动作，读者感受自然产生。
```

### scene_tasks 双 marker 格式（必填）

每条 scene_tasks 用两个 marker 描述任务的两个正交维度：

| Marker 位 | 取值 | 维度 | 回答 |
|----------|------|------|------|
| 第一位（priority） | `核心` / `灵感` / `惊艳` | 叙事必要性 | 是否必须交付？ |
| 第二位（reader_layer） | `main` / `support` / `atmosphere` | 创作取舍 | 这段读者要不要亲历？ |

格式示例：

```yaml
scene_tasks:
  - "[核心][main] 小龙女判断陌生人证据是否可信"
  - "[核心][support] 陆青漪用药理证明传闻被操控（仅给结论）"
  - "[灵感][atmosphere] 鞋底水痕、湿绳作为压力线索（不解释成机制）"
  - "[惊艳][main] 小龙女从沈雁舟鞋底水痕反推他刚从禁渡夜船回来"
```

**`reader_layer` 语义**（创作取舍维度，不是密度刻度）：

| 值 | 语义 |
|---|---|
| `main` | 本场正面戏，读者必须亲历的关键变化 / 危险 / 选择；**不等于完整过程** |
| `support` | 给结果 + 一个必要锚点，不展开步骤 |
| `atmosphere` | 背景压力，只给感受和画面，不解释成机制 |

**关键判断**：main 不是"多写"，而是"写不可替代的戏剧变化"。搜寻、移动、整理、检查、交接等低读者收益动作，除非带来新危险、新规则、新误判或人物裂缝，否则降为 support 或省略。

**不当处理示例**：

| Layer | 不当处理 |
|-------|---------|
| `support` | 详解药粉成分、补给点位置等步骤展开 |
| `atmosphere` | 把"灯影不稳"解释成"敌人在监视"（追加因果，解释成机制） |

**约束**：每条 scene_tasks 必须能解释它如何服务 `reader_track`——服务不了的不是必须删，但**不能当 main 展开**。

**Marker 缺位 fallback**：第二位 marker 缺失（仅写 `[核心]`）→ writer 视为 `support`。但 Phase 5 产出必须写全双 marker，让 reader_layer 明确而不依赖 fallback。

## 字段说明

| 字段 | 必需 | 下游使用 |
|------|------|---------|
| `sequence_expansions[].seq_id` | 是 | 关联 Phase 4 的序列设计 |
| `scenes[].scene_id` | 是 | Phase 6（按 ID 展开每个场景为叙事文本）。**必须匹配 `^S\d{2}$`**（`S01` / `S02` / ... / `S99`）；不得含 `scene_` 前缀或纯数字格式，否则下游路径模板 `pipeline/scene_{scene_id}/` 会撞双前缀（如 `scene_scene_1`）|
| `scenes[].arc_id` | 是 | Phase 6（快速定位当前幕的价值方向）。派生字段：从 seq_id 归属 Arc 获得 |
| `scenes[].title` | 是 | Phase 6（场景标识） |
| `scenes[].pov` | 是 | Phase 6（叙事视角锚定） |
| `scenes[].narration_style` | 是 | Phase 6（叙事腔调锚）。close-third=紧贴 pov 角色内心；third-omniscient=全知叙述者；first=第一人称 |
| `scenes[].participants` | 是 | Phase 6（确定对白角色）、character-rehearsal（Actor 分配） |
| `scenes[].location_time` | 是 | Phase 6（时空坐标，引用 Phase 1 世界观切片） |
| `scenes[].conflict` | 是 | Phase 6（节拍围绕冲突展开） |
| `scenes[].value_start` / `value_end` | 是 | Phase 6（节拍序列驱动**关键叙事状态**从 start 到 end，语义按 `spine_mode` 解释——desire=价值状态 / information=信息或认知状态 / observe-motif=关系或感知状态；schema 字段名保留不变作向后兼容；填法承载所有 mode 的状态描述，不限于价值语义）|
| `scenes[].reader_track` | 是 | Phase 6（writer 单一阅读主线锚点——本场读者跟随什么问题/行动线；scene_tasks 必须服务此线） |
| `scenes[].scene_tasks` | 是 | Phase 6（叙事工作 + 创意灵感；双 marker 格式 `[priority][reader_layer]`；不写抽象读者反应 / 氛围目标） |
| `scenes[].inspiration_refs` | 否 | Phase 6（writer 通过 scene_card.md 看见本场 INS-* 引用，再按 ledger 的 carrier / disclosure_ladder 消费）；字段存在时数组长度建议 ≤ 2 |
| `scenes[].handoff` | 是 | Phase 6（场景衔接） |
| `scenes[].beat_direction` | 否 | Phase 6（仅关键场景：序列高潮、Arc 高潮、激励事件） |
| `scenes[].pov_constraint` | 否 | Phase 6（writer：限定本场 POV 可感知/不可感知项，定位 intentional_blind_spot；缺字段=无 POV 限制） |
| `scenes[].craft_carrier` | 否 | Phase 6（writer：鸿沟由 type+concrete_anchor 承载，replaces 指明它替代了哪段解释/心理/背景；缺字段=由 writer 临场决定承载） |
| `scenes[].world_disclosure_plan` | 否 | Phase 6（writer：授权 / 禁止借物披露世界规则的边界；`{forbid, allow}` 字符串列表 × 2；缺字段=沿用旧"不解释一切"约束） |
| `scenes[].omission_plan` | 否 | Phase 6（writer：本场故意不解释什么；缺字段=不强约束省略点） |
| `scenes[].irreversible_action` | 否 | Phase 6（writer：本场必须出现的可见且不可撤销动作清单；缺字段=不强约束） |
| `scenes[].reveal_method` | 否 | Phase 6（writer：信息揭示方式锚——direct_action / object_trace / overheard_fragment 等；缺字段=writer 自由选择揭示路径） |
| `scenes[].narrator_distance` | 否 | Phase 6（writer：本场叙事距离 mode + reason；enum 与 phase0 narrator_position.primary 同源——8 值；缺字段=继承 phase0 默认） |
| `scenes[].scale_inversion` | 否 | Phase 6（writer：是否启用大命题↔小物件反转 + 具体桥；缺字段=不强约束） |
| `scenes[].precedent_mirror` | 否 | Phase 6（writer：本场镜像哪场 + 镜像类型 + 保留锚点 + 删除前提；缺字段=不构造镜像关系） |
| `scenes[].climax_pattern` | 否 | Phase 6（writer：高潮场景 pattern 锚——primary/secondary 7 enum + null；仅 climax/sequence_climax/arc_climax=true 时显式选择；缺字段=不加载任何高潮模板，走通用 Craft Preflight） |
| `scenes[].dialogue_hints` | 否 | Phase 6（writer 在 dialogue-craft 工坊阶段消费：每条 hint = `{speaker, attribution_strategy(5 enum), dialogue_form(5 enum + null), reason}`；缺字段=走通用 dialogue 设计，不强约束） |
| `scenes[].counter_prior_scene` | 否 | Phase 6（dispatcher 反先验场景 fast-path 信号——结构化对象：`{used, kind, mundane_action, emotional_context, forbidden_moves}`。`used=true` 时 orchestrator 在 writer dispatch prompt 附加额外约束段；缺字段 / `used=false` → writer 不收特殊注入，走通用 Craft Preflight）|
| `scenes[].prose_risk_contract` | 否 | Phase 6（写作层 AI pattern 预防——结构化对象：`{used, risk_families, positive_strategy, bad_shape_examples}`。`used=true` 时 scene_card.md 渲染 contract 段供 writer / scene-reviewer 读；phase6 dispatcher fast-path 仅激活提醒；scene-reviewer 在首次评审时读 contract 做 violation 识别；reviser 不直接消费；缺字段 / `used=false` → writer 走通用 Craft Preflight）|
| `tension_curve` | 否 | Phase 7（验证全文张力分布） |
| `scene_causal_chain` | 否 | Phase 7（因果链审查） |

#### inspiration_refs（optional）

| 子字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `inspiration_refs[]` | string[] | 字段存在时数组长度 ≤ 2 | INS-* ID 引用 ledger 中 type=pattern 的卡 |

**Budget**：普通场景 0-1，key_scene 0-2（描述性范围，不强校验数量）。

**Hard gate**（`validate_phase5_r10.py`）：双向一致性匹配——ledger 内 INS-* 的 `project_encoding[]` 必须有对应 `(phase=5, scene_id, adoption_kind ∈ {scene_carrier, reveal_carrier, structure_carrier, craft_carrier})` 项。

## `world_disclosure_plan` (optional, str list × 2)

授权 / 禁止 writer 借物披露世界规则的边界。缺省 = 沿用旧"不解释一切"约束。

```yaml
world_disclosure_plan:
  forbid:                       # 禁止披露的内容
    - 终极成因（病原 / 战争 / AI / 神秘灾变到底是什么）
    - 救援 / 未来 / 重建宏大总结
  allow:                        # 允许披露的内容
    - 主角第一人称口吻披露崩坏过程（信号 → 水电 → 人声依次消失等）
    - 行动规则（可信资源的判定 / 物理衰退的判定 / 幸存者行为规则）
    - 由眼前物 / 动作触发，极简短句即止；不做百科说明
```

**渲染契约**（由 `extract_scene_card.py` 实施）：

- 段标题精确字面量：`## 世界观披露 (world_disclosure_plan)`
- 字段缺失 OR `forbid` 与 `allow` 同时为空 → 整段不输出
- 任一非空 → 输出段标题 + 该非空列表（另一侧空则不输出对应子标题）
- 渲染位置：在 scene_card.md 内输出即可（渲染位置软化契约）；位置 executor 按现有 `_render_v3_fields` 结构判断

## `prose_risk_contract` (optional, 4 子字段对象)

写作层 AI pattern 预防：声明本场 writer 应主动规避的 AI pattern 风险族 + 本场特化正向策略。family 命名锚 `prose-craft/references/ai-cliche-patterns.md` 现有条目（F 类已用 snake_case；A-G 类与观察层用中文短语——两者都接受）。

**字段语义**：

| 字段 | 必需 | 语义 |
|---|---|---|
| `used` | 是 | `true` 时 scene_card.md 渲染 contract 段作 writer / reviewer 可见 canonical source；`false` 或缺整段对象 → 不渲染 |
| `risk_families` | 是 | 本场 high-risk family 清单。family 名锚 ai-cliche-patterns.md 现有条目；未知 family 不阻断 writer，按 prose-craft 内置 cliche 库默认规避 fallback |
| `positive_strategy` | 是 | 本场特化策略——只写"本场为什么特殊 / 怎么做才贴合本场"（如"本场社交调度，动作合并必须落到关系压力变化点"）；不重复 family 通用修法（通用修法 writer 通过 prose-craft skill 查 ai-cliche-patterns.md） |
| `bad_shape_examples` | 否 | 本场具体形态示例，"长相"参考非字面禁词；1-3 条上限；writer 遇相同**结构**形态即改写叙述形态，禁止字面规避（同义替换 = 回流陷阱）|

**设计原则**：

- 不写数字阈值（违反 feedback_no_rigid_rules + D1）——用 `positive_strategy` 写判据信号让 writer 临场按场景判
- `bad_shape_examples` 是结构示例不是禁词——writer 不做字面规避

**渲染契约**（由 `extract_scene_card.py` 实施）：

- 段标题精确字面量：`## 写作层 AI pattern 预防 (prose_risk_contract)`
- 字段缺失 OR `used != true` OR 三个子列表（risk_families / positive_strategy / bad_shape_examples）皆空 → 整段不输出

**与 `counter_prior_scene` 同场冲突兜底**（不引入 priority 字段；本规则为本字段冲突 SSOT，其他 SKILL 不复述）：

- 两字段语义多数正交；冲突时按以下顺序裁决：(a) 更具体的 scene_card contract 优先于全局 craft 规则；(b) 不得违反事实 / 视角 / scene_card 设计意图 / revision 红线；(c) 无法同时满足时避免解释和升华，保留场景功能（不靠加内容解决冲突）
- 极端冲突 writer 无法自决 → 在 subagent 最终 reply 报告 orchestrator，由 scene-reviewer 升 ROLLBACK 由 writer fresh session 重写
