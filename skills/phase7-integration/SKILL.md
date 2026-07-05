---
name: phase7-integration
description: MUSE Phase 7 — 整合与读者审查。将所有场景拼接为完整作品，dispatch reader-review subagent 做读者体验审查，dispatch manuscript-reviser 完成正文修订，输出终稿 story.md。pipeline 内部件：由 orchestrator 跑完 Phase 6 后路由进入；强依赖 phase0/2/6 产物，不独立承接用户语义入口。
---

# Phase 7: 整合与读者审查

## 核心原则

> 「一个故事，即使是在表达混乱的时候，也必须是统一的。无论出自什么样的情节，下面这个句子都应该是合乎逻辑的：'因为激励事件，高潮必须发生。'」
> —— 《故事》第十二章

整合不是简单的拼接——全文必须作为有机体运作。进入 Phase 7 时，场景文件已经过 Pass 1 技术诊断并由 orchestrator 修复，Phase 7 的任务是将这些场景组装为完整故事，并通过读者视角发现全文层面的问题。

## 两轮审查体系中的位置

```
Phase 6 → Pass 1 story-review(场景级技术诊断) → orchestrator 修场景
        → Phase 7: 拼接 → Pass 2 reader-review(全文读者体验) → manuscript-reviser 修订 → 输出
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

> **本 gate 由 orchestrator 显式执行**：进入 Step 1 拼接前必跑
> `python3 <本包 scripts 目录>/verify_review_complete.py {work_dir}`——
> exit 非 0 时禁止调用 assemble_story.py，按下方"缺失时的处置"三选一。
> 规则全文以脚本为权威，本节仅描述协议语义。

**进入 Phase 7 的第一动作**——orchestrator 必须先执行 `verify_review_complete.py` 验证 [`phase6-scene-development/references/execution-protocol.md`](../phase6-scene-development/references/execution-protocol.md) §1.5 审阅链路（L1 lint → L2 A/B/C → L3 scene-reviewer → reviser）已跑完，**才能**进入 Step 1 拼接。

**判据**（任一条不满足 = §1.5 未跑完）：

1. 扫 `pipeline/review/scene_{scene_id}.yaml`——每个场景一份，verdict ∈ `{PASS, PATCH, ROLLBACK, REWRITE, ESCALATED}`
2. 若有 PATCH verdict → 对应 `pipeline/scene_{scene_id}/patch_directive.applied.yaml` 必须存在（reviser 已消费）
3. 若有 ROLLBACK / REWRITE verdict → scene 应已重新走完 writer 链路并产新版 scene_*.md

**缺失时的处置（互斥三选一）**：

| 选项 | 条件 | 动作 |
|---|---|---|
| **A. 回 §1.5 补跑**（默认） | orchestrator 时间充裕 / 用户未声明 quick mode | dispatch story-reviewer → scene-reviewer → 等所有 verdict 产出后再进 Step 1 |
| **B. 显式声明跳过**（escape hatch） | 评测窗口 / 用户明示 quick mode / 临时 smoke test | 在 `pipeline/audit/skip_review.yaml` 写 `{reason: "...", timestamp: "...", risk_acknowledged: true, missing_scenes: [...]}`，然后正常进 Step 1 拼接；残留 lint/scene finding 由 Step 3 的 manuscript-reviser 无条件消费作兜底 |
| **C. 不允许沉默跳过** | — | 无 `skip_review.yaml` 且 `scene_*.yaml` 不完整 = 流程错误，orchestrator 必须停下来选 A 或 B，**不允许**直接进 Step 1 |

**为什么必须 gate**：审阅链路被跳过时，lint 产物全部停在文件里无人消费、AI 病灶直达成品。Step 0 入口 gate 事前堵漏；manuscript-reviser 无条件消费 `pipeline/review/` 残留 finding 作事后兜底——双保险防"设计白费"。

**声明 escape hatch 的最低门槛**：`reason` 必须是具体可审计的（如 `evaluation_time_window_2026-05-20` / `user_quick_mode_smoke_test` / `phase6_rerun_after_design_change`），不允许 `"skip"` / `"manual_choice"` 这类无信息空洞理由。

### 1. 拼接场景 → story.md

**不要用 Read 工具逐个读取场景文件。** 调用拼接脚本，由脚本完成全部文件操作：

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/assemble_story.py {work_dir}
```

脚本按 `phase6_development.yaml` 中 `scenes` 列表的顺序读取每个 `file_path`，拼接后写入 `{work_dir}/story.md`。orchestrator 无需接触场景文件内容。

### 2. 全文终验状态机（Step 1 拼接后的唯一路径）

```text
assemble story.md（Step 1）
   │
   ▼
whole-text lint：python ${CLAUDE_PLUGIN_ROOT}/scripts/wholetext_gate.py
                 --story {work_dir}/story.md --lang <phase0.language> --work-dir {work_dir}
   │  报告落 pipeline/review/wholetext_gate.yaml
   ├─ exit 1（超限）─> dispatch manuscript-reviser（de-AI 模式）─> 重跑 wholetext_gate
   │                    └─ de-AI 修订上限 2 轮；第 2 轮后仍 exit 1 ─> ESCALATED（见下）
   ▼ exit 0（达标 / 修后达标）
reader-review【条件步骤】
   ├─ 跳过（低产判据命中）：写 pipeline/audit/reader_review_skip.yaml（具体可审计理由；
   │   不复用 skip_review.yaml），直接进 final gate
   └─ 执行（盲读接近 lint-clean 的稿）─> dispatch manuscript-reviser（reader 模式，1 轮）
   ▼
final gate：再跑一次 wholetext_gate.py（同命令）
   ├─ exit 0 ─> story.md 即终稿，出稿
   ├─ exit 1 ─> ESCALATED：mark pending_human + 不出稿；story.md 保留，写
   │            pipeline/audit/quality_gate_failed.yaml（{reason, gate_report:
   │            pipeline/review/wholetext_gate.yaml, timestamp}）——不删稿，人工介入需要现场
   └─ exit 2 ─> 脚本输入错误，按 dispatch_failed 处理，ESCALATED
```

**dispatch 约定**：manuscript-reviser 两种模式由 dispatch prompt 关键字区分——`de-AI` / `reader`；均仅传 `work_dir` + 模式词。修订轮 status 消费沿用 complete/partial/failed 语义（读 `pipeline/revision_summary.md` 顶部 status）；`failed` 直接 ESCALATED，不计入轮数重试；`partial` 计入轮数。

**轮数是硬上限**：de-AI ≤2 轮、reader 修订 1 轮——不随超限次数增长。全程 orchestrator 不 Read / Edit story.md。

### 3. 写入最终文件

- 最终正文：`story.md`（与 `pipeline/` 同级）——Phase 7 的唯一交付物；final gate exit 0 才算发布
- gate FAIL 时 `story.md` 保留在原位 + `pipeline/audit/quality_gate_failed.yaml` 标注，不作为交付物对外

## 输出

- 正文：`story.md`（final gate exit 0 时为最终作品；FAIL 时保留但标 quality_gate_failed，不出稿）
- `pipeline/review/wholetext_gate.yaml`（终验报告，脚本产）
- `pipeline/revision_summary.md`（manuscript-reviser 状态工件，非交付物；缺失表示修订被跳过）
