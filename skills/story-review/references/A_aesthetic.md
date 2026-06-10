# 审美诊断（A 组）

> 审查目标：逐场景扫描写作质量问题——AI 套路模式、角色声音偏离、价值变化缺失、潜台词泄漏、可信性瑕疵、动作流水账、微观语言错配、感官平衡、视角边界、场景收尾。

## 目录（TOC）

[输入](#输入) · [子文件指针](#子文件指针) · 主表：[§1 AI 套路](#1-ai-套路检测) · [§2 角色声音](#2-角色声音一致性) · [§3 场景价值](#3-场景价值变化) · [§4 对白↔交流](#4-对白脱离角色角色真实交流) · [§4b 设计泄漏](#4b-设计文档泄漏检测) · [§5 可信性](#5-可信性瑕疵) · [§6 动作流水账 / 低读者收益段](#6-动作流水账--低读者收益段检测) · [§7 微观语言](#7-微观语言错配)（子文件）· [§8 感官平衡](#8-感官平衡) · [§9 视角边界](#9-视角边界焦点角色感知越界) · [§10 场景收尾](#10-场景收尾) · [输出](#输出)

## 输入

- `pipeline/scenes/scene_{id}.md` — 全部场景正文（核心依赖）
- `pipeline/phase2_character.yaml` + `pipeline/characters/{角色名}.md` — 角色声音特征（核心依赖）
- `pipeline/phase5_scenes.yaml` — 场景的 value_start/end 设计（参考依赖）
- `pipeline/review/lint/{scene_id}.*.yaml` — **L1 脚本 lint 报告合集**（核心依赖，Step 5 Phase A 产出）
  - `{scene_id}.ai_filler.yaml`（S1：口癖 / Markdown / 排比 / 关联词）
  - `{scene_id}.lexical_stats.yaml`（S2：副词密度 / TTR / 感官平衡 / 高频词——统计型，读 `density.*.imbalanced/overuse/too_low` 布尔字段）
  - `{scene_id}.dialogue.yaml`（S3：纯台词 / 指代 / 说话动作孤立 / 模板说话动词）

**与 lint 分工**：lint 已定位具体位置的模式，A 组**先读 lint report 了解已定位位置**避免重复扫描；A 组工作是在此基础上做语义判读（是否真冗余 / 误报 / 可豁免）+ 覆盖脚本查不了的维度（即下方主表逐项）。

## 子文件指针

A 组规则分布在本主文件（主表 §1-§10）+ 两个子文件中。**主文件入口不变**——外部 cross-ref 指 `A_aesthetic.md` 即可：

- [`A_aesthetic-carrier.md`](A_aesthetic-carrier.md) — **§0 豁免前置** + **§11 承载完整性**：扫到 AI 病灶 / 审美问题位置先核 4 类豁免；逐场景核 craft_carrier 字段
- [`A_aesthetic-micro_language.md`](A_aesthetic-micro_language.md) — **§1bis 反 AI 化 5 条** + **§7 微观语言**（判读流程 + 修订方向）+ **§reframing 独白判读**：句级语言细节诊断 + reader-review 报"长独白可能在 reframing"症状时的二次诊断

## 审查维度

### 1. AI 套路检测

→ 模式清单见 `prose-craft` skill 的 [`references/ai-cliche-patterns.md`](../../prose-craft/references/ai-cliche-patterns.md)
→ **承载模式参考**（合法名著手法判读时按需查）：[`prose-craft/references/novel-craft-patterns.md`](../../prose-craft/references/novel-craft-patterns.md)（A 类承载点 / B 类视角 / C 类高潮 / D 类人物 / E 类形态）

逐一扫描核心层全部模式（清单见 ai-cliche-patterns.md），标记命中位置；下列五类列出本组**额外的语义判读 / lint 联动信号**：

**A. 场景焦点类**（语义判，lint 不覆盖）— 主次失焦 / "描写→说话"强制收束

**B. 修辞类**
- 语义判（lint 不覆盖）：无功能修辞 / 格言金句 / 比喻堆砌
- **lint 命中必须逐处 triage，不等于逐处 finding**。

  A 组对每个 lint hit 走豁免清单（含 scene_card_field + local_textual_evidence + function_claim 三者并存硬约束）+ 语义判读，输出 `pipeline/review/scene_{id}.lint_resolution_ledger.yaml`：

  - `triage.status: finding` → 进 patch_directive
  - `triage.status: merged` → 与其他 finding 合并（多 family 同 span → 合并为一个 rewrite_span finding）
  - `triage.status: observed` → 单次合理 advisory，不进 patch_directive
  - `triage.status: exempted` → 豁免命中（必须 scene_card_field + local_textual_evidence + function_claim 三者并存）

  **所有 lint hit 必须有 triage.status**，不允许"静默放走"。

  ledger schema：A 组写 `v1_triage` 块（immutable），scene-reviewer 后续 post-revision 追加 `post_revision_updates` 块（append-only），不覆盖 A 组首次 triage。

  ```yaml
  scene_id: S01
  v1_triage:
    immutable: true
    entries:
      - lint_id: ai_filler:span_001:stock_silence_pause_phrase
        rule: stock_silence_pause_phrase
        family: silence_pause_cliche
        cluster: silence_pause_cliche
        location:
          line_range: [12, 12]
        triage:
          status: finding | merged | observed | exempted
          merged_into: null
          reason: "为什么进 finding / merged / observed / exempted"
          exemption:
            scene_card_field: null
            local_textual_evidence: null
            function_claim: null
        resolution:
          status: unresolved | patch_planned | patched | residual_observed | exempted
          patch_id: null
          post_revision_gate: null
  post_revision_updates:
    - review_round: post_revision_round1
      updates:
        - lint_id: ai_filler:span_001:stock_silence_pause_phrase
          resolution_status_change:
            from: patch_planned
            to: patched
          patch_id: patch_01
          local_lint_v2_family_set: []
  ```
- **lint 已定位，A 组直采为 CRITICAL（写入 finding 的 severity 字段）**：`banned_markdown`（#/列表/加粗/段首方括号，S1）

**C. 情绪类**（语义判，lint 不覆盖）— 情绪压制公式（感受→微动作→压回→转任务）/ 情绪库存短语（"血液冰凉" / "心脏一缩"等）

**D. 说话描写类**
- 说话动作窄库——声音状态标签（"声音平静" / "低声道"）代替让对白本身传递情绪
- **lint 已定位**：`template_speech_verb`（"XX 地/的说道"模板，S3）；窄库其余词汇（"低吼 / 沉声道 / 压低声音"）留 A 组语义判

**E. 段落结构类** — 段落密度偏离范文。A 组**不现场运行脚本**：若 orchestrator 已产出 `pipeline/review/lint/{scene_id}.density_vs_ref.yaml`（phase6 §3.5.3 ref 对齐校验），读 output / reference / gap / verdict（SIGNIFICANT_DEVIATION）判"题材盲的均质分段"；否则跳过。**数据是参考非强制**：急促动作 / 情感收束即使 long_pct 差距大也不是问题；只在场景明显需要长景深（复杂对峙 / 空间展开 / 内心深化）却被切成均质中段落时才标记。

对每个命中：引用原文段落，说明命中了哪个模式，建议替代方向。

> §1bis 反 AI 化失守检查（与 ai-cliche-patterns.md 新 5 条联动）— 见 [`A_aesthetic-micro_language.md`](A_aesthetic-micro_language.md)
>
> §reframing 独白判读（消费 reader-review "长独白可能在 reframing" 症状时）— 见 [`A_aesthetic-micro_language.md`](A_aesthetic-micro_language.md)

### 2. 角色声音一致性

> 「没有表达性的对白，事件就少了深度，角色丧失层次，故事也变得平板。」—— 《对白》前言

对每个主要角色：(1) 从 `characters/{角色名}.md` 提取声音特征和 voice_boundaries；(2) 收集该角色在全部场景中的对白；(3) **遮名测试**：遮住名字只看对白，是否体现设计的声音特征？(4) **跨场景对比**：声音前后是否一致？

对每个问题：引用具体场景和对白，说明偏离了哪个声音特征。

### 3. 场景价值变化

→ 诊断方法见 [`references/mckee-diagnostics.md`](mckee-diagnostics.md) § 场景分析法

对每个场景：(1) 识别核心价值（什么价值在场景中被考验？）；(2) 标注开场时的价值状态（正/负）；(3) 标注结尾时的价值状态；(4) 对比：开头 = 结尾 → 标记为"无事件"场景。同时对照 Phase 5 设计的 value_start/end，检查实际文本是否实现设计意图。

### 4. 对白脱离角色↔角色真实交流

→ 诊断方法见 [`references/mckee-diagnostics.md`](mckee-diagnostics.md) § 潜台词塌缩

**根因**：对白必须服务"角色 → 角色"的真实交流，脱离这条原则即问题。脱离方向有二：内心 → 直说（§4.A）/ 角色 → 服务读者（§4.B）。

#### §4.A 潜台词塌缩（直白方向）

扫描对白和叙述，定位以下模式：

- 角色直接说出内心感受（"我很害怕"、"我终于明白了"）
- 角色替作者做主题阐释
- 角色展示超出自身认知的自我分析

对每个命中：引用对白原文，说明为什么这是"写在鼻子上"。

#### §4.B 对白脱节（隐晦 / 演讲方向）

→ 详细规则见 [`dialogue-craft/references/dialogue-rules.md`](../../dialogue-craft/references/dialogue-rules.md) § 对白交流契约

A 组在此处**只判一件事**：对白是否**优先服务场内交流**？4 类失败按 dialogue-craft 同源规则定位：

- 无场内理由的隐语 / 哑谜（无密语约定、无防偷听、无装腔铺垫）
- 对已知者重述已知信息（"as you know, Bob" 演讲式）
- 省略到接收者无法恢复指代（话语落空）
- 文学化玄言替代有效信息（双重含义堆叠 / 抒情对仗）

豁免：装腔 / 暗号 / 防偷听 / 自言自语——必须有**场内动机**和**接收逻辑**支撑。

每个命中：引用原文 + 一句失败原因（指向 4 类中的哪一类），不展开规则细节。

### 4b. 设计文档泄漏检测

扫描正文，定位**设计文档、排练素材或创作理论泄漏进正文**的痕迹。设计术语词表（下方）由 A 组自行扫描；设计意图泄漏**句式**纯语义，由 A 组判读。

**设计术语泄漏词表**（这些来自设计 YAML 字段术语，正文不应出现）：
`潜台词`、`价值转折`、`鸿沟`、`节拍`、`弧光`、`脊椎`、`主控思想`、`激励事件`、`进展纠葛`、`不归点`、`序列高潮`、`递进方向`、`冲击力`、`价值起点`、`价值终点`、`beat_direction`、`scene_tasks`、`handoff`

**设计意图泄漏句式**：
- "他知道这意味着…" / "这道命令的潜台词是…" / "真正的意思是…" → 作者在替读者解读
- "这是一个不可逆转的选择" / "从此再也无法回头" → Phase 3 crisis 标注的直接显化
- "此处体现了…" / "这一刻象征着…" → 元叙述评论
- "根据…原理" / "按照…的逻辑" → 创作理论或设计文档语言

**排练素材照搬**：staging/ 第一人称推理被直接改写为第三人称叙述，而未转化为行动 / 细节。例：❌"他知道这道命令的潜台词：他在给自己留一支可以抽调的力量"（Phase 4 sequence_climax 作者注释直译）→ ✅"传令兵跑走了。沈牧辰没有解释"（到此为止，行动 / 细节暗示潜台词）

对每个命中：引用正文段落 + 溯源上游文件（Phase 4/5 设计标注或 staging 排练素材），说明泄漏路径。

### 5. 可信性瑕疵

→ 诊断方法见 [`references/mckee-diagnostics.md`](mckee-diagnostics.md) § 可信性瑕疵

扫描：**空洞字眼**（对白只暴露信息，不推进欲望）/ **过度滥情**（情绪强度远超情境）/ **过度感知**（角色自我分析深度超出可信范围）/ **借口冒充动机**（表面理由替代真正的驱动力）。

### 6. 动作流水账 / 低读者收益段检测

**核心判断**：审查目标不是确认动作是否真实，而是确认这些动作是否值得读者完整阅读。动作必须至少新增一种**读者收益**：危险升级、欲望受阻、关系变化、世界规则显形、人物裂隙、情绪转折、形式惊艳。没有新增收益的动作，压缩或删除。

**命中类型**：

- **低读者收益动作链**：连续动作不新增 plot / character / world rule / danger / turn / formal delight
- **物资 / 空间 / 流程盘点**：同构句式（item→check→pack / move→door→walk 等）连续呈现
- **角色特质误写成正文形态**：角色清单化思考被原样搬到正文交付
- **可删除的舞台指示**：动作句答"发生了什么"但不答"发生于谁 / 如何发生"

**处理方向**：

- 优先压缩，不优先润色
- 保留读者收益最高的 1 个动作；后续同类动作只给结果
- 对不产生新收益的过渡动作直接删除

**句级细则**：

> 「优秀的写作不太强调发生了什么，而是强调发生于谁、为什么发生以及如何发生。」
> —— 分级节拍理论

扫描以下类型：

- **事件记录式动作句**——动作句只答"发生了什么"（转身、走、合上笔记本），不答"发生于谁"或"如何发生"；可集中也可分散（单独成段短动作句尤其易成流水账节奏）
- **设计动作逐字搬入**——检查正文是否把规划清单直接写成叙述顺序。设计清单只能指导取舍，不能变成正文清单
- **可删除的舞台指示**——删掉某物理动作后读者对场景理解不减少 → 冗余

对每个命中：引用原文，说明缺少反应 / 鸿沟 / 代价感，或为何可省。

### 7. 微观语言错配

→ 详细判据 / hot zone 加权 / reader-visible damage 判读流程 / 修订方向见 [`A_aesthetic-micro_language.md`](A_aesthetic-micro_language.md)

句级"看似有文气但不成立"问题。命中时 `dimension: micro_language`，并填 `subkind`（`false_literary_diction` / `sensory_mismatch` / `abstract_judgment_without_action` / `stock_speech_tag` / `weak_character_expression`）。

**只报影响阅读的句子**（reader-visible damage 原则）；每条 finding 必须给 `evidence_quote` 原句和一句失败原因。

### 8. 感官平衡


**数据来源**：S2 `lexical_stats` 产 `density.sensory_balance` 字段——含 `visual_ratio` + `counts`（视/听/触/嗅/味 五类词频）+ `imbalanced` 布尔标。

**判读方法**：
- 读 `{scene_id}.lexical_stats.yaml` 的 `density.sensory_balance.imbalanced`
- 若 `imbalanced: true` → **不直接报告**，先结合场景需求判：
  - 武侠对战 / 城市观察 / 人物外貌聚焦 → 视觉重天然合理，视为 false positive
  - 情感收束 / 亲密接触 / 夜色场景 / 回忆 → 应有触/听/嗅进入场景，`imbalanced=true` 才真命中
- `meta.thresholds.visual_ratio` 已由 orchestrator 按 `--genre` 题材自适应传入（武侠类建议 0.85，现代类 0.70）；你无需再判"阈值是否合适"

对每个真命中：引用正文段落，说明缺少哪个非视觉通道（听/触/嗅/味），建议用哪个具体细节补入。

### 9. 视角边界（焦点角色感知越界）

> 与 B 组 §3.A（**跨场景**视角切换规则）分工——A 组专注**单场景内**焦点角色感知边界。

**扫描方法**：从 `phase5_scenes.yaml` 或 `scene_card.md` 读当前场景 POV / 焦点角色。扫描正文定位以下句式：

- `[其他角色名]想 / 知道 / 感到 / 意识到 / 在心里 / 暗暗 ...` —— 焦点角色不可能知道他人心理
- `[其他角色名]紧握的手出了汗 / 心跳加速 ...` —— 生理指标焦点角色不可能察觉
- 超出焦点角色感官范围的环境细节（焦点在室内却描述室外具体动作）

**排除项**（不是越界）：焦点角色**推测**他人心理（"他看起来在生气" / "她大概是在想…"）/ 自由间接话语（free indirect discourse）有意设计 / 不可靠叙述者有意设计。

对每个命中：引用原文，说明焦点角色为何不可能知道这条信息。（当前 A 组全手工扫描）

### 10. 场景收尾

> 与 `prose-craft` §L3 写后自检 §段落节奏收束部分呼应，但 A 组场景级审查。

**扫描方法**：看每场景末段（或末 2-3 句）。命中类型：

- **哲理金句收束**（"他明白了，真正的自由是…" / "岁月终究会…" 等抽象总结）
- **对称排比收束**（末段以"不是 A，而是 B" 或 "既是 X，也是 Y" 形式收尾）
- **抽象总结无具体画面**（末段无触/听/视的具体细节，只剩概念）
- **以"说 / 道 / 问 / 答"收束**（段落必以对话出口收尾是 AI 套路，见 §1 "描写→说话"强制收束的场景级特例）

**判不命中正例**：末段以**具体小动作** / **单一感官细节** / **时间或环境的画面停格**收尾——不发议论不升华不点题。

对每个命中：引用末段原文，建议替代方向（一个具体触/视/听细节）。

> §0 豁免前置（4 类豁免）+ §11 承载完整性（craft_carrier 联动）— 见 [`A_aesthetic-carrier.md`](A_aesthetic-carrier.md)

## 输出

审查报告以 YAML 格式写入 `pipeline/review/A_aesthetic.yaml`。

→ 输出格式见 [`output-schema.md`](output-schema.md)
