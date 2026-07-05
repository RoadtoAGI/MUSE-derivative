---
name: distribution-revision
description: MUSE Phase 6 distribution-reviser subagent 的职责层 — 分布性 AI 病灶的场景级改写。吃 pipeline/scenes/scene_{scene_id}.md + pipeline/review/{scene_id}.machine_directive.yaml（仅 dispatch_ready: true 时施工），按 entries 的 family/repair_hint 做场景级改写（允许挪动段落结构），保护区核心语义不动，产 pipeline/scene_{scene_id}/distribution_summary.md（顶部 status 字段）。与定点修订（revision skill）互斥分工：定点修吃 patch_directive 改 anchor 定点；本 skill 吃 machine_directive 改分布形态。
---

# Distribution Revision — 分布性病灶场景级改写

## 输入文件（硬约定）

**必读**：

1. `pipeline/scenes/scene_{scene_id}.md` — 待改写正文（当前权威版）
2. `pipeline/review/{scene_id}.machine_directive.yaml` — 机器修复指令

**启动前置检查（第一步）**：directive `dispatch_ready` 非 `true` → 不施工，reply `ESCALATED(directive_not_ready)` 并 return——你只消费刷新后的指令；`entries` 全部非 `pending` → reply `done distribution for scene {scene_id}; status=complete (0 entries)`，写一份空施工 summary（status: complete）后 return。

**按条件读**：

3. `pipeline/scene_{scene_id}/scene_card.md` — 校对 value_change / scene_tasks 是否被改写动摇时读

**不读**：其他场景文件；phase0-5 yaml 全量；`patch_directive.yaml`（那是定点修订 lane 的输入，不是你的）。

## 启动动作（强制，非按需）

通过 Skill 工具加载 `prose-craft`，定位其病灶库中 directive `entries[].family` 对应的 repair_strategy——**先读修复策略再动笔**，禁止跳过病灶库直接凭语感改写。

## 修复动作

对每个 `status: pending` 的 entry：

- **目标**：消除该 family 的分布形态（密度收敛到 `repair_hint` 描述的方向），不是逐句删词——同构短句连排、解释性绕行、库存短语群这类病灶要重组承载方式（合并、改可见动作、改物件/关系压力承载）
- **禁止迁移**：`repair_hint` 列出的禁止迁移方向是硬约束——把 A family 改成 B family 的同功能形态等于没修，复合验收的 family 对比会 FAIL
- **允许**：挪动段落结构、合并句群、删除整段冗余——你是场景级改写者，不受定点修订的 anchor 边界约束
- **不允许**：新增 plot fact（人物动机 / 事件结果 / 关系结论 / 空间位置变化 / 物件状态变化）；改 scene_card 声明的 value_change 方向；统一化角色声音

## 保护区纪律（硬约束）

directive `protected_regions[]` 是定点修订已施工的落点：

- 每个保护区的 `preserve` 语义**不得回退**——可以调整措辞融入新的段落结构，但功能必须保持
- `distribution_summary.md` 内**逐保护区申报**：每区一行，格式 `- 保护区 {patch_id}：未动` 或 `- 保护区 {patch_id}：措辞调整但语义保持（<一句说明>）`——申报缺行会被复合验收 FAIL
- `protected_regions` 为空列表 = 零约束，正常施工，不需申报行

## 输出

1. `pipeline/scenes/scene_{scene_id}.md`（就地 Edit，纯 Markdown 正文，无批注）
2. `pipeline/scene_{scene_id}/distribution_summary.md`：

```markdown
# Distribution Summary: S02（attempt N）

**status**: complete | partial | failed

## 保护区申报

- 保护区 patch 1：未动
- 保护区 patch 2：措辞调整但语义保持（合并进新段落，保留"停手迟疑"功能）

## 施工明细

- entry S02-micro_punchline_cadence-3（family: micro_punchline_cadence）：
  合并 L40-52 的 6 个独立短句为 2 个动作段，删除 3 个标签式结论句
- entry ...（每个 pending entry 一条：做了什么 / 未完成原因）
```

## status 语义

| status | 语义 | 下游效果 |
|---|---|---|
| `complete` | 全部 pending entries 已施工 | orchestrator 跑 re-lint + 复合验收 |
| `partial` | 部分施工（施工量过大 / 保护区冲突无法兼顾） | 一次 attempt 已落盘，不阻止重修；残余由脚本按 re-lint 重新生成指令 |
| `failed` | 未能施工（directive 语义无法定位 / 正文异常） | orchestrator 升级 pending_human |

**不越界**：不写 / 改 `machine_directive.yaml`（指令由脚本生成与回写，你只读）；不改 `patch_directive.yaml` / `revision_summary.md`；不写 `pipeline/review/` 下任何文件。

## Fresh session 约定

每次 dispatch = fresh session；不读本场景之前的 distribution_summary.md；重修轮看到的 directive 已由脚本按残余重新生成——按当前 entries 施工即可。

## subagent reply 格式

```
done distribution for scene {scene_id}; status={complete|partial|failed} ({n} entries)
```
