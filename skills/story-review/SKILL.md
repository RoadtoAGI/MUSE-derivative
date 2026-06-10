---
name: story-review
description: MUSE Pass 1 技术诊断与一致性审查 — Phase 6 场景完成后、Phase 7 整合前，由 orchestrator adaptive dispatch 1-3 组 subagent 执行（默认 A；B/C 按信号触发）。orchestrator 只传工作目录和组别，subagent 自行读取审查指南和目标文件。orchestrator 从 pipeline/review/ 读取报告后修复。
---

# 审稿模块（Pass 1: 技术诊断 + 一致性审查）

## 核心原则

> 「一旦通过适当的方式来研究一个场景，其瑕疵便会一目了然。」
> —— 《故事》第十一章

审稿走 adaptive dispatch，**不默认三组全开**——A 是场景级技术诊断的主用组、B/C 是长篇 / 复杂世界一致性审计，按需触发。**orchestrator 不读取 `references/` 下的审查指南文件**——每组 subagent 根据自己的指南自行定位并读取所需文件。

> **两轮审查体系**：本模块是 Pass 1（技术诊断 + 一致性审查），由 1-3 组 subagent 并行执行（按 adaptive 规则决定）。Pass 2（读者体验审查）由 `reader-review` 模块在 Phase 7 拼接后执行，以纯粹读者视角审查完整故事。

## Dispatch 表 + adaptive 触发

| 组别 | Subagent 读取的审查指南 | 审查粒度 | adaptive 触发条件 |
|------|------------------------|----------|------------------|
| **A 审美组** | `references/A_aesthetic.md` | 场景级 | **默认必跑** |
| **B 叙事一致性** | `references/B_narrative_consistency.md` | 全文级 | 满足任一即跑：长篇（多 arc / 场景数足以发生跨场景矛盾）/ 复杂角色关系（多角色高频互动）/ design-validation 已发现风险 / reader-review 报告理解断裂 / 用户明确要求 |
| **C 结构一致性** | `references/C_structural_consistency.md` | 全文级 + 设计文档级 | 满足任一即跑：复杂世界规则 / 多时间线 / pipeline_crosscheck 风险 / design-validation 已发现风险 / 用户明确要求 |

**判据是信号，不是数字门槛**——orchestrator 现场判断本 run 是否触发 B/C；判定无明显信号时按短篇默认（仅 A）。

每组 subagent 的审查指南中已包含：输入契约（读哪些文件）、审查维度、输出格式。orchestrator 无需了解具体审查内容。

**副使用场景**：Phase 7 之后若 `story.md` 已存在，B/C 组可用 `story.md` 替代 `scenes/*.md` 作为正文来源进行二次审查。A 组始终以场景文件为单位工作。

## 注意事项（三组通用）

- 审稿的价值在于**定位问题**，不在于确认"通过"。不要列出通过项，只列出发现的问题。
- 如果某个维度没有发现问题，直接跳过，不要写"未发现问题"。
- 引用原文时保留足够上下文，让 orchestrator 无需回查场景文件即可理解问题。
- **只标记真实存在的矛盾**，不要捏造、推测或想象不存在的问题。没有问题就是没有问题。
- **区分文学手法和真正的错误**——不可靠叙述者、比喻表达、有意的风格对比都不是矛盾。当存在疑问时，倾向文学解读而非错误判定。
- 一致性维度（B/C 组）的发现应尽量提供 `contradiction_pair`，引用矛盾的两端让 orchestrator 快速定位。

## INS-* carrier 可见性 / inference path 检测

读 `pipeline/inspiration_ledger.yaml` 获取所有 `status ∈ {accepted, bound}` 的 INS-*，对每个 INS-* 做闭环检测。本段产出的 finding **全部归入 C 组 `dimension=pipeline_crosscheck`**（subkind 见下表），落 `pipeline/review/C_structural_consistency.yaml`。它检查 ledger ↔ phase YAML ↔ 正文之间的设计-文档交叉一致性，不新开 dimension（A 组 10 维 / B 组 3 维 / C 组 3 维已固定）。

**重要措辞边界**：reviewer 不能稳定证明"读者一定 get 到"，只能判断"carrier 是否可见 + inference path 是否成立 + 是否触禁"。subkind 命名按此原则。

**检测逻辑**：

1. 对每个 INS-* 检查 `project_encoding[]` 的 `field_path` 是否真在对应 phase YAML 字段被引用
2. 对每个 INS-* 的 `disclosure_ladder[]` 每 layer：
   - 检查 `scene_id` 对应 `pipeline/scenes/scene_{sid}.md` 正文里是否存在该 `carrier`（物件 / 动作 / 视角 / 留白等）
   - 检查 carrier 是否承担了 `reader_inference` 描述的信息变化
   - 检查是否触发该 layer 的 `do_not_explain[]` 禁项（"显示而非告诉"规则）

**输出 finding 5 类（dimension=pipeline_crosscheck，subkind 取下表 code；默认严重度写入 finding 的 `severity` 字段）**：

| subkind | 含义 | 默认严重度 |
|---|---|---|
| `inspiration_bound_but_no_visible_carrier` | INS-* status=bound 但正文找不到 disclosure_ladder 指定的 carrier | CRITICAL |
| `carrier_visible_but_inference_gap` | 正文有 carrier 但没让它承担信息变化（如写了"夜灯"但没让夜灯承载选择压力） | IMPORTANT |
| `carrier_overexplained` | carrier 出现但过度解释了（违反 `do_not_explain` 中的"不说意味着 X"类禁项） | IMPORTANT |
| `archetype_declared_but_no_recognition_path` | phase2 挂了 archetype INS-A* 但 phase2 `recognition_path` / `voice_traits` 字段未体现 archetype 学习面 | IMPORTANT |
| `inspiration_accepted_but_never_bound` | INS-* status=accepted 但跨多 phase rerun 后始终未被任何 phase YAML 引用（候选累积成垃圾场） | INFO |

**输出 schema 落点**：字段约定与 finding 样例见 `references/output-schema.md` "INS-* carrier 闭环 finding 样例"节（唯一权威，本节不镜像 yaml）。`contradiction_pair` 必须标明 ledger 内 INS-* ID + 字段路径（如 `INS-001 disclosure_ladder[early_signal].carrier`），让 orchestrator 可一键定位 ledger 卡定位修复方向。

**字段缺席降级**：ledger 文件不存在 / 所有 INS-* status=candidate → 整段跳过，不报错。
