# patch_directive Traceability 协议

本文件承载 `pipeline/scene_{scene_id}/patch_directive.yaml` 的 traceability gate 完整协议——schema 字段、黑名单边界、失败语义与兼容规则。SKILL.md 只留短锚（≥8 字原句引述 / C 组黑名单 / 失败 → ESCALATED），完整规则在此。

每次 dispatch 不读本文件——`check-reviser-patch` hook 在 reviser PreToolUse 时自动调 `verify_patch_directive_traceability.py`；scene-reviewer 写 patch 时 SKILL.md 短锚 + schema 例子已足；新人 / Codex 审阅 / 协议升级才回查本文件。

---

## 1. Schema 段：anchor_quote 显式字段

每个 patch 必须含 `anchor_quote` 字段——精确截取自 `pipeline/scenes/scene_{id}.md` 的 ≥ 8 字原句，verify 脚本直接 substring match。

校验规则：
- `verify_patch_directive_traceability.py` 读 `anchor_quote` 字段
- anchor_quote 未命中正文 → `anchor_quote_not_in_scene_md`
- anchor_quote 长度 < 8 → `anchor_quote_too_short`
- `anchor_quote` 字段缺失 → `missing_anchor_quote`

**为什么显式字段**：
- 无引述的"删 L23 某段"无法被脚本验证，等于 traceability 失效
- 显式 `anchor_quote`：scene-reviewer 不再为"满足格式"而写出别扭的 location；reviser 直接读 anchor_quote 锚定修改点；verify 逻辑变成 `anchor_quote in scene_md_text` 的一行判断

## 2. C 组黑名单策略（user_accepted / next_round_only 边界）

`issue_id` / `issue` 不得引用 C 组**显式 user_accepted / next_round_only finding**——具体信号：

- `category ∈ {user_accepted_as_known_issue, next_round_only}`
- `suggestion` 含同类标记
- `escalation_decision.user_accepted_findings[]` 列出

引用上述任一 → 校验失败，patch 被判 untraceable。

**裸 `status=persists` 不入黑名单**——persists 表示"问题仍未解决"，可能正是当前轮要修的 C 组问题，scene-reviewer 应正常对其产 patch。

## 3. 失败语义

校验失败（`untraceable` / `missing_anchor_quote` / 黑名单命中）→ `patch_directive.yaml` 不 promote，**orchestrator 不 dispatch reviser，标 ESCALATED**。

ESCALATED 来源边界（不变量）：本路径下 ESCALATED 由 orchestrator input_gate 写入 review yaml；scene-reviewer 自身**不**写 ESCALATED。
