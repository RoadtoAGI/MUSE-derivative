# 排练输出格式

Phase 6 情境排练按**四项固定结构**产出，orchestrator 不做二次提取（见 `situational-method.md §4 落盘契约`）。审稿校验产出自由文本，orchestrator 从 agent 的自然应答中提取所需反馈。

## Phase 6 情境排练

Actor 产出**四项固定内容**（见 `situational-method.md §4 落盘契约`）：
- 想说但不会直说
- 台词候选（2-4 条）
- 禁用语气
- 动作或停顿

产出路径：`pipeline/staging/scene_{scene_id}/{slug}_rehearsal.md`

orchestrator 不做二次提取——Actor 直接按固定结构产，writer 直接消费。

## 审稿：角色校验

orchestrator 提取：
- **一致性反馈** → `pipeline/staging/scene_{scene_id}/{slug}_validation.md`
- 内容："像/不像" + 具体段落指出 + 角色会怎么说的替代建议
