---
name: phase7-integration
description: MUSE Phase 7 — 整合与读者审查。将所有场景拼接为完整作品，dispatch reader-review subagent 做读者体验审查，基于读者反馈整体修改，输出终稿 story.md。pipeline 内部件：由 orchestrator 跑完 Phase 6 后路由进入；强依赖 phase0/2/6 产物，不独立承接用户语义入口。
---

# Phase 7: 整合与读者审查

## 核心原则

> 「一个故事，即使是在表达混乱的时候，也必须是统一的。无论出自什么样的情节，下面这个句子都应该是合乎逻辑的：'因为激励事件，高潮必须发生。'」
> —— 《故事》第十二章

整合不是简单的拼接——全文必须作为有机体运作。进入 Phase 7 时，场景文件已经过 Pass 1 技术诊断并由 orchestrator 修复，Phase 7 的任务是将这些场景组装为完整故事，并通过读者视角发现全文层面的问题。

## 两轮审查体系中的位置

```
Phase 6 → Pass 1 story-review(场景级技术诊断) → orchestrator 修场景
        → Phase 7: 拼接 → Pass 2 reader-review(全文读者体验) → orchestrator 整体修改 → 输出
```

Phase 7 负责 Pass 2 及其后的修改。Pass 1 的工作已在 Phase 7 之前完成。

## 输入契约

从 Phase 0 接收（参考依赖）：
- `controlling_idea` — 验证高潮是否表达主控思想
- `core_value` — 验证价值变化的完整性

从 Phase 2 接收（参考依赖）：
- `pipeline/story-character-skills/.claude/skills/{slug}/SKILL.md` — 修订人物对白时的声音参考

从 Phase 6 接收（核心依赖）：
- `phase6_development.yaml` — 场景索引
- `scenes/scene_{id}.md` — 所有场景正文（已经过 Pass 1 修复）

## 执行步骤

### 0. §1.5 完整性 gate（Phase 6 → Phase 7 过渡硬约束）

> **本 gate 由 hook 机器强制**：调用 `assemble_story.py` 时 PreToolUse Bash hook 触发 [`scripts/verify_review_complete.py`](../../scripts/verify_review_complete.py)；缺失场景审阅产物且无有效 escape hatch → **exit 2 阻断工具调用**，orchestrator 无法绕过。本节仅描述协议语义；规则全文以脚本为权威。

**进入 Phase 7 的第一动作**——orchestrator 必须先验证 [`phase6-scene-development/references/execution-protocol.md`](../phase6-scene-development/references/execution-protocol.md) §1.5 审阅链路（L1 lint → L2 A/B/C → L3 scene-reviewer → reviser）已跑完，**才能**进入 Step 1 拼接。

**判据**（任一条不满足 = §1.5 未跑完）：

1. 扫 `pipeline/review/scene_{scene_id}.yaml`——每个场景一份，verdict ∈ `{PASS, PATCH, ROLLBACK, REWRITE, ESCALATED}`
2. 若有 PATCH verdict → 对应 `pipeline/scene_{scene_id}/patch_directive.applied.yaml` 必须存在（reviser 已消费）
3. 若有 ROLLBACK / REWRITE verdict → scene 应已重新走完 writer 链路并产新版 scene_*.md

**缺失时的处置（互斥三选一）**：

| 选项 | 条件 | 动作 |
|---|---|---|
| **A. 回 §1.5 补跑**（默认） | orchestrator 时间充裕 / 用户未声明 quick mode | dispatch story-reviewer → scene-reviewer → 等所有 verdict 产出后再进 Step 1 |
| **B. 显式声明跳过**（escape hatch） | 评测窗口 / 用户明示 quick mode / 临时 smoke test | 在 `pipeline/audit/skip_review.yaml` 写 `{reason: "...", timestamp: "...", risk_acknowledged: true, missing_scenes: [...]}`，然后走 Step 2.0 兜底扫描 |
| **C. 不允许沉默跳过** | — | 无 `skip_review.yaml` 且 `scene_*.yaml` 不完整 = 流程错误，orchestrator 必须停下来选 A 或 B，**不允许**直接进 Step 1 |

**为什么必须 gate**：审阅链路被跳过时，lint 产物全部停在文件里无人消费、AI 病灶直达成品。Step 0 入口 gate 事前堵漏，Step 2.0 兜底事后补救——双保险防"设计白费"。

**声明 escape hatch 的最低门槛**：`reason` 必须是具体可审计的（如 `evaluation_time_window_2026-05-20` / `user_quick_mode_smoke_test` / `phase6_rerun_after_design_change`），不允许 `"skip"` / `"manual_choice"` 这类无信息空洞理由。

### 1. 拼接场景 → story.md

**不要用 Read 工具逐个读取场景文件。** 调用拼接脚本，由脚本完成全部文件操作：

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/assemble_story.py {work_dir}
```

脚本按 `phase6_development.yaml` 中 `scenes` 列表的顺序读取每个 `file_path`，拼接后写入 `{work_dir}/story.md`。orchestrator 无需接触场景文件内容。

拼接完成后，如需处理场景衔接，用 Grep 定位衔接处再局部 Read，**不要通读全文**。过渡的三种铰链：

> 「一个没有进展感的故事容易从一个场景跌跌撞撞地闯入另一个场景。它几乎没有连续性，因为它的事件之间没有任何关联。」
> —— 《故事》第十二章

- 时间/空间衔接（最基本）
- 两个场景共有的元素
- 两个场景互成对照的元素

### 2. 读者审查 + 整体修改

**dispatch reader-review subagent**：将 `story.md` 交给 `reader-review` 模块。该 subagent 以纯粹读者视角顺序阅读全文，报告每一处"出戏"的地方。它不接触任何设计文档。

#### 2.0 修订前兜底扫描（防 §1.5 失守）

reader-review 完成后、按 reader_findings 修订**之前**，orchestrator **必须**扫两组遗留 finding：

- **L1 lint findings**（hook 自动产，§1.5 跳过也存在）：
  - `pipeline/review/lint/{scene_id}.ai_filler.yaml`
  - `pipeline/review/lint/{scene_id}.dialogue.yaml`
  - `pipeline/review/lint/{scene_id}.lexical_stats.yaml`
- **L2/L3 scene-review findings**（仅 §1.5 跑了才存在）：
  - `pipeline/review/scene_{scene_id}.yaml`（L3 verdict）
  - `pipeline/review/A_aesthetic*.yaml` / `B_*.yaml` / `C_*.yaml`（L2 各组报告）

**为什么必须兜底**：[`phase6-scene-development/references/execution-protocol.md`](../phase6-scene-development/references/execution-protocol.md) §1.5 审阅链路（L1 lint → L2 A/B/C → L3 scene-reviewer → reviser）在评测时间窗口紧 / orchestrator 调度疏漏时可能被整段跳过。Hook 仍自动产 lint yaml，但若无下游 dispatch，所有 finding 停留在文件里无人消费。Phase 7 是最后一道关，必须接住。

**合并语义**：
- 把所有遗留 hits 视为待处置 finding，与 `reader_findings` 一并按 §"reader-review feedback 处置协议" 同样分流处置
- 去重判据：位置（scene_id + 行号映射到 story.md 全局行号）+ pattern 名相同视为同一 finding
- **L1 lint findings 按 `group` 字段分流**：
  - `group` 缺失 / 不含 → **hard cliche**（banned_markdown / keyword_ai_cliche / conjunction_overuse / 大部分 parallel_negation）：直接进入待修 finding，与 reader_findings 合并按下面"reader-review feedback 处置协议"分流；hard cliche 的 severity 由 pattern 决定（多数为高置信硬命中）
  - `group=heuristic` → **统计异常信号**（clause_fragment_density / dash_density / repeated_clause_head / micro_action_density / short_paragraph_run / parallel_negation 软变体）：**不直接判罪**，作为风险定位信号
    - 同段 ≥ 2 个 heuristic 命中 → 升级为范围修改候选
    - 同段同时有 hard cliche + heuristic → 升级为范围修改候选
    - 单个 heuristic 孤立命中（severity=low / advisory）→ 只作 advisory，不强制修
- **L2 A_aesthetic findings 按豁免清单分流**，与 reader_findings 同语义

**降级**：lint yaml 全部缺失（plugin 未装到位 / hook 失败 / scenes/ 路径变体不匹配）→ orchestrator 在 story.md 修订 commit message 显式标 `WARN: Phase 7 兜底扫描未发现任何 lint yaml，§1.5 可能完全失守，建议复核 hook 注册与 scene 路径` 提示自查。

**理由**：reader-review 只读读者视角、从不读 lint yaml——§1.5 失守时全部 lint finding 无人消费。本兜底是双保险，不替代 §1.5 主路径。

#### 2.1 处理读者反馈

orchestrator 逐条处理合并后的 finding 集合（reader_findings + lint findings + scene-review findings），对每个发现：

1. **判断真伪**：纯粹读者可能报告"故意为之"的留白（如伏笔尚未到回收时机）。orchestrator 结合设计意图判断是否为真问题。
2. **定位修改**：根据 `location` 找到 story.md 中对应段落，根据 `expectation` 和 `absence` 理解读者需要什么。
3. **整体修改**：在 story.md 上直接修改。修改时参考角色 runtime package 的声音特征，避免修订过程中人物声音被统一化。

### reader-review feedback 处置协议

orchestrator 读 `pipeline/review/reader_review.yaml` 后按 finding 类型分流处置：

**结构性 finding（必须范围修改）**：

feeling / absence 字段语义涉及：

- "扫读 / 想跳过 / 失去耐心"类信号（节奏失效）
- "平行结构 / 重复 / 没有节奏断点"类信号（结构同构）

→ orchestrator **必须**做范围级修改：删段 / 合段 / 压缩为结果+锚点。
→ **不允许**只改字句（如换说话动词、改副词、加描写细节）——结构问题靠字句修订无法解决。

**设计意图相关 finding（按豁免清单）**：

feeling / absence 字段语义涉及：

- "出戏 / 反应过淡 / 信息不足 / 心理空白"类信号

→ 按 scene_card 设计意图判断是否豁免。豁免清单（与 [`../scene-review/SKILL.md`](../scene-review/SKILL.md) L127-136 4 类豁免同源）：

  1. `scene_card.pov_constraint.intentional_blind_spot`
  2. `scene_card.omission_plan`
  3. `scene_card.narrator_distance` 合法选择（archival_zero / unreliable_first 等）
  4. reframing 独白判读三项以上（详 [`../story-review/references/A_aesthetic-micro_language.md`](../story-review/references/A_aesthetic-micro_language.md)）

→ 豁免命中：不修；豁免不命中：做局部字句修订。

**处置完成后复合对照**：reader-review 关键 finding（"扫读" 类）+ L1 hard cliche findings + L1 heuristic 升级条目所在位置，确认 story.md 已做范围级修改——而非只改了字句。lint findings 中：
- hard cliche 高严重度（如 `不是A而是B` / `banned_markdown`）必须确认结构改了
- heuristic 升级条目（同段多信号聚合）必须确认整段重写，不是只换几个字
- heuristic 孤立 advisory 命中可以不改，但应记录在 commit message 中

**理由**：节奏失效与结构同构是结构问题，不是设计意图问题——无论 scene_card 声明什么，"读者扫读" / "lint 报硬病灶" 都不是合理的设计目标。范围修改才能真正消除流水账。

### 3. 终章形态校对：新增两个高价值形态

整合时核对最终章是否落入"AI 默认收束式"。**这不是二分法**——循环式、余波式、反讽式、开放悬置式、档案封存式仍可合法存在。本节只补两个高优默认（断裂式、收束式），用于校对 AI 默认形态是否被无意识采纳。

| 形态 | 判据 | 名著锚点 |
|---|---|---|
| **收束式** | 线索全收、情感升华、有方向感的开放 | 《指环王》终章山姆"我回来了"|
| **断裂式** | 主角做一个动作并保持进行时态，最后一个问题不被回答；线索 / 情感 / 方向都不补完 | 《挪威的森林》终章 — 渡边在电话亭说"整个世界上除了她别无他求"，绿子问"你现在哪里"，叙述在动作进行时态中停止 |
| **其他合法形态**（不强制写法） | 循环式 / 余波式 / 反讽式 / 开放悬置式 / 档案封存式 | 各自有合法用法，本节不细说；只要不是 AI 默认无意识"线索全收 + 给方向"即合法 |

**反 AI 化判据**：若整合时终章被 AI 默认写成"线索全收 + 主角内心明朗 + 给未来方向"，但 phase0 reference_materials / craft_targets.scale_strategy 暗示"反高潮 / 模糊 / 中段截断"风格，考虑改为断裂式或上述其他合法形态之一。

**禁用的 AI 终章默认信号**：
- "他知道，从今以后……"
- "无论未来如何，至少现在……"
- "故事还会继续，但是 / 至少这一刻"
- 末段以一个有"方向感"的修辞句收尾

**断裂式的具体执行**（高优反 AI 套路推荐之一，不是唯一答案）：
- 最后一个动作必须是进行时（"他不断按着 / 他还在喊 / 他始终没回答"）
- 最后一个问题必须不被回答（叙述在问题与回答之间停止）
- 不允许"她不知道答案，但她知道……"式半补全

### 4. 写入最终文件

- 最终正文：`story.md`（与 `pipeline/` 同级）——Phase 7 的唯一交付物

## 输出

- 正文：`story.md`（最终作品，唯一交付物）

Phase 7 不生成 YAML 整合报告。读者反馈的处理过程体现在 story.md 的修订中，无需额外记录。

## 常见错误

| 错误 | 后果 | 修正 |
|------|------|------|
| 人物声音在修订中被统一化 | 角色差异消失 | 修订时保持对 Phase 2 声音特征的引用 |
| 结局引入新复杂性 | 读者期待收束却遇到新问题 | 结局只展示新平衡，不开新线 |
| 把读者反馈的"故意留白"当作真问题修改 | 破坏设计意图 | orchestrator 需结合设计意图判断，不盲从读者反馈 |
| 修改 story.md 时引入新的 AI 写作模式 | 修复一个问题，制造另一个 | 修改后快速通读修改段落，检查是否引入套路 |
