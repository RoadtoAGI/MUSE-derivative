---
name: revision
description: MUSE Phase 6 reviser subagent 的职责层 — PATCH 档定点修订。吃 pipeline/scenes/scene_{scene_id}.md + patch_directive.yaml，按 patches 定点修（不越界），就地 Edit scene_{scene_id}.md + 产 revision_summary.md（顶部 status 字段 complete|partial|failed）。partial 档额外 Edit patch_directive.yaml 保留未应用条目。由 orchestrator 通过当前运行时的 subagent dispatch 启动 reviser，reviser 启动后通过运行时 skill 机制加载本 skill 获取输入路径硬约定 / schema / status 语义 / 减法哲学 / 不越界约束。
---

# Revision — PATCH 档定点修订

## 输入文件（硬约定）

**必读**：

1. `pipeline/scenes/scene_{scene_id}.md` — 待修正文（writer 首产或前一轮 reviser Edit 后的当前版）
2. `pipeline/scene_{scene_id}/patch_directive.yaml` — 修订指令（见下方 schema）

**按条件读**：

3. `pipeline/scene_{scene_id}/scene_card.md` — 仅在 patch suggested_action 引用 scene_tasks 时读（reviser **不**因 prose_risk_contract 命中而主动读 scene_card——contract 已由 scene-reviewer 翻译进 patch_directive 的 issue / suggested_action 字段；详见下方 "prose_risk_contract 输入边界" 段）
4. `pipeline/scene_{scene_id}/role_briefs.md` — 仅在 patch suggested_action 引用角色 boldness / desire 时读

**不读**：
- 其他场景的文件（注意力集中）
- phase0-5 yaml 全量（patches 应自含足够上下文）
- 本场景之前的 revision_summary.md（fresh session 约定）
- 任何 skill 的 `SKILL.md` / `references/*.md`（通过运行时 skill 入口加载同名 skill，不用 Read）

## patch_directive.yaml schema

```yaml
# pipeline/scene_{scene_id}/patch_directive.yaml
# 消费语义：
# - complete 状态下由 orchestrator 调 mark_patch_applied.py 改名为
#   patch_directive.applied.yaml
# - partial 状态下 reviser 自己 Edit 本文件，移除已 applied 条目只留
#   not_applied 条目（下轮重试清单）

source: scene_review                # 当前唯一入口；patch_directive.yaml 由 scene-reviewer 产
scene_id: S02

patches:
  - location: "Turn 3 末段" | "句群 S5-S7" | "对白：'你一个人？'后" | "段落 L23"
    issue: "动作后又补一遍心理，重复"
    suggested_action: "保留动作，删去其后的心理解释"
    issue_id: B-37           # 可选透传
    patch_kind: "<see references/patch-kind-registry.md PATCH 类>"
    # 物理 enum 在 references/patch-kind-registry.md（单一来源；本 SKILL.md 不复制）
    # reviser 收到 patch_directive.yaml 时按 registry direction 字段执行修订模板
    # 若 scene-reviewer 漏标 patch_kind → 字段缺省即可，reviser 按通用减法哲学处理
  - ...
```

- `anchor_quote`：≥ 8 字精确原句，reviser 用它在 `pipeline/scenes/scene_{scene_id}.md` 中定位修改点；reviser 启动前 `check-reviser-patch` hook 自动校验 anchor_quote 命中
- `location` 是**人读**的定位描述（如 "L23 附近" / "对白前一行"），不是精确行号——`scene_{scene_id}.md` 修订过程中行号会变
- `issue` 简述问题
- `suggested_action` 给出动作方向（增 / 删 / 调）——reviser 执行此方向，不做更激进的改动
- `issue_id` **可选透传字段**——reviser 本身不消费，但不得在 revision_summary.md 中丢弃

## 输出

1. `pipeline/scenes/scene_{scene_id}.md`（就地 Edit，**纯 Markdown 正文**，无批注）
2. `pipeline/scene_{scene_id}/revision_summary.md`（顶部 status 字段 + 完整审计记录）
3. **partial 状态下额外**：Edit `pipeline/scene_{scene_id}/patch_directive.yaml` 移除已 applied 条目只留 not_applied

### revision_summary.md 格式

```markdown
# Revision Summary: S02（round N）

**status**: complete | partial | failed
**patch directive source**: scene_review
**patches applied**: 2 / 3                    # 分子/分母

## 改动明细

1. **[patch 1 · issue_id B-37 · applied · patch_kind=rewrite_sentence]** 删冗余心理
   - 位置：L23 附近
   - old_span：原 anchor 或 old_span
   - new_span：修订后的句 / 段
   - 改动：删除"他感到一阵寒意袭来"一句，保留前面的"他的手停住"动作
   - 理由（引自 patch）：动作后又补心理，重复
   - consumed_patterns:
     - family: silence_pause_cliche
       cluster: silence_pause_cliche
       rule: stock_silence_pause_phrase
   - preserved_function:
     - "保留人物停住手的迟疑功能"
   - added_carriers: []
   - contract_conflict:
     observed: false
     note: null

2. **[patch 2 · issue_id B-38 · not_applied]** 无法定位
   - 位置：patch 写"Turn 4 末段"但 draft 无 Turn 标记，语义含糊
   - 动作：未改动；交 orchestrator 决定（重写 patch / 或接受 partial 结果）
   - patch_kind: rewrite_span
   - consumed_patterns: []
   - preserved_function: []
   - contract_conflict:
     observed: false
     note: null

## 未动的部分

（patches 未指出的段落一律未动——本段留空或简述"其余段落完全保留"）
```

## status 语义（完整版）

| status | 语义 | reviser 动作 | orchestrator 端效果 |
|---|---|---|---|
| `complete` | 全部 patches 成功应用 | Edit `scene_{scene_id}.md` + 写 revision_summary.md（所有 patch 标 applied） | mark_patch_applied 改名 pending→applied + tail |
| `partial` | 部分 applied / 部分无法定位、语义不明或权限不足（`should_be_rollback`） | Edit `scene_{scene_id}.md`（已应用部分落地） + 写 revision_summary.md（applied + not_applied 完整审计）+ **Edit `patch_directive.yaml` 只留 not_applied** | 不 mark_applied；仍 tail；pending 文件 = 下轮重试清单 |
| `failed` | 零 patches 应用（全部无法定位 / 或内部错误） | 不改 `scene_{scene_id}.md`；写 revision_summary.md 记录原因 | mark_scene_pending_human(reason="revision_failed_zero_applied")；不 tail |

### status 权威源规则

**revision_summary.md 顶部 `status` 字段 = 唯一权威源**。

Task reply 文本也**必须**回显 status 作 orchestrator 快速提示：

```
done revision for scene S02; status=partial (2/3 patches applied; 1 unreachable)
```

orchestrator 的 `parse_revision_status_strict` 判定规则：

1. 打开 revision_summary.md，读顶部 `status` 字段
2. 若文件不存在 / 字段缺失 / 字段值非 `complete|partial|failed` → 判 `failed`
3. 若文件 status 值与 Task reply 回显的 status **不一致** → 判 `failed`（双源冲突 = 下游不能信任）
4. 其他情况返回 summary 里的 status 值

**Task reply 不能替代 summary**——即便 reply 写 complete，若 revision_summary.md 缺失也判 failed。

### partial 的 reviser 职责

partial 状态下 reviser 必须完成三件事：

1. **Edit `patch_directive.yaml`**：移除 applied 条目，只留 not_applied 条目。pending 文件语义 = 下轮重试清单
2. **revision_summary.md 保留完整审计**：applied + not_applied 两类条目都列明；下轮 reviser rerun（fresh session）不读此文件，审计链留给 orchestrator 查
3. **`scene_{scene_id}.md` 就地 Edit**：已应用部分的改动落地，未应用部分的段落保持原状

## 减法哲学（default preference）

- 当 patch_kind 属于减法 mode（delete_token / replace_phrase / carrier_then_explain 等） → **默认做减法**，suggested_action 若可"删"则删
- 当 patch_kind 属于 semantic_rewriter mode（rewrite_sentence / rewrite_span） → 按 `rewrite_directive` 指引重写，仍优先用最短表达（保留减法 spirit），**不为重写而扩写**
- 始终不新增事实：设定 / 事件结果 / 角色动机不动——这些是 ROLLBACK 或 REWRITE 档职责，不是 PATCH

## 反 AI 化定点修订（patch_kind ≠ NULL 时）

scene-reviewer 标注的 patch_kind 让 reviser 知道这条 patch 是要恢复名著实践已验证的承载方式。每个 patch_kind 的修订方向**在 [`references/patch-kind-registry.md`](references/patch-kind-registry.md) 单一来源中维护**——reviser 按 `direction` 字段执行，不在本 SKILL.md 复制。

**硬约束**：reviser 收到 patch_kind ∈ ROLLBACK 类（`epic_death_facing` / `mirror_loosened` / `carrier_missing` / `narrator_distance_global_drift`）= **该条 patch 不应用**，在 revision_summary.md 记 `not_applied`（reason `should_be_rollback`）。reviser 没有改事件因果 / 镜像结构 / 全场基调的权限。

**混合批次语义**：同一 directive 内其余合法 patch 正常应用，最终 status 按应用结果定——其余全部 applied → `partial`（pending directive 只留 should_be_rollback 条目）；**全部** patches 均为 ROLLBACK 类（零应用）→ `failed` + reason `should_be_rollback`（与"failed = 零 patches 应用"定义自洽）。orchestrator 看到任一 `should_be_rollback` 条目即升级判断是否重派 writer 走 ROLLBACK。

**patch_kind 与 status 无关**：patch_kind 是修订方向标签；status 仍由 patches 应用结果（complete / partial / failed）决定。唯一例外即全 ROLLBACK 类批次——此时 status=failed 由"权限不足"而非"patch 应用失败"触发，revision_summary.md `reason` 字段写 `should_be_rollback` 以便 orchestrator 区分。

## semantic_rewriter mode 切换

前提：lint 命中只是定位，修订目标是消除 AI 叙述形态。

当 `patch_kind ∈ {rewrite_sentence, rewrite_span}` 时，reviser 进入 `semantic_rewriter mode`：修订目标不是删一个词，而是在 anchor 边界内消除 AI 叙述形态，同时保住 `rewrite_directive.preserve` 列出的功能。

| mode | 触发 patch_kind | 允许动作 | 禁止动作 |
|---|---|---|---|
| 减法 mode | delete_token / replace_phrase / 既有定点 PATCH 类 | 删冗余词、删解释、替换库存短语 | 改写未授权句群；新增事实 |
| semantic_rewriter mode | rewrite_sentence / rewrite_span | anchor 内重写句法结构、合并连续动作、把抽象解释改成可见动作或物件承载 | 跳出 anchor；新增 plot fact；把 `preserve` 项改掉 |

**voice 保真判据**（semantic_rewriter / cluster 重写共用）：`preserve` 字段只保功能，voice 一致性由本判据兜住——重写句落地前对照前后文自检三项：语域（文白比例 / 口语度）、句长节奏、叙述声音（语态 / 人称 / 修辞密度）与上下文一致。重写后通读修订 span 与前后衔接句，出现"换了个作者"的断口感 → 收窄改动幅度重写：优先保留原句的词汇与句式骨架，只动病灶成分。

## Cluster patch 治理

接到含 `cluster_id` 字段的 patch directive 时，按以下硬协议：

1. **patch_kind 限定**
   - 仅允许 `cluster_alert.governance.required_patch_kind_options` 内的 patch_kind（默认 rewrite_sentence / rewrite_span）
   - 禁用 `delete_token` / `replace_phrase`（违规由 post-revision-gate 硬阻断）
   - 禁用所有非 allowlist 内 PATCH 类（如 `carrier_then_explain` / `omission_violated` 等 legacy PATCH 类不能用于 cluster patch）

2. **同构替换硬禁**
   - 禁"删而"（"不是A而是B" → "不是A是B"）
   - 禁"改其实 / 改真正 / 改表面实际"（同功能迁移，会被 F1.E semantic_function_migration gate 抓住）
   - 必须改成可见场面动作（参见 design doc §6.5 通过/失败判据示例）

3. **同 cluster patch_set**
   - 所有 patch directive 挂同 cluster_id
   - 各 patch 各自针对一个 cluster 内 hit 改写

### carrier 边界规则

- **低强度 carrier**：语气、停顿、视线、手势、杯子/门/灯等轻量承载物。`allowed_carrier_changes.low_intensity=true` 时可压缩、合并或替换，但仍要保留 `semantic_function`。
- **plot-adjacent carrier**：会影响事件因果、人物关系结论、空间位置变化或物件状态变化的承载物。只有 `allowed_carrier_changes.plot_adjacent` 明确列名时才可替换。
- 例：`"接电话去了"` 可在授权下改为 `"对陈嘉抬了抬手，让出空间接电话"`，因为它保留"离开对话焦点 / 制造空间隔离"的功能；不得改成"她收到关键密信后离开"，那会新增 plot fact。

## prose_risk_contract 输入边界

scene_card 渲染 `## 写作层 AI pattern 预防 (prose_risk_contract)` 段时（schema 见 phase5 `output-schema.md`），**reviser 不直接消费 contract**——contract 由 scene-reviewer 翻译进 patch_directive 的 `issue` / `suggested_action` 字段传递；reviser 按现有 `patch-kind-registry.md` 处理，本 SKILL.md 的 "不越界（红线）" 段不变（即使察觉 contract `risk_families` 命中点在场景其他段落，patches 未列段落一律不动）。

scene-reviewer 的翻译职责见 [`../scene-review/SKILL.md`](../scene-review/SKILL.md) "prose_risk_contract compliance check" 段。

## 不越界（红线）

核心不变量：patches 未列位置不动；不跳 anchor 外；不新增 plot fact。
plot fact 包括：人物动机 / 事件结果 / 关系结论 / 空间位置变化 / 物件状态变化。

| 限制 | 减法 mode | semantic_rewriter mode | ROLLBACK 类 |
|---|---|---|---|
| patches 未列位置不动 | 强制 | 强制 | 不应用，记 `not_applied`（`should_be_rollback`） |
| 不跳 anchor 外 | 只改 `anchor_quote` 命中处 | rewrite_sentence 只改单句；rewrite_span 只改 `old_span` / line_range 内 | 该条不应用（记 not_applied） |
| anchor 内重写句法 | 不允许，除非 suggested_action 明确 | 允许；目标是消除 AI 叙述形态并保留 preserve 项 | 该条不应用（记 not_applied） |
| 新增 plot fact | 禁止 | 禁止 | 禁止；交 writer |
| 改人物动机 / 关系结论 | 禁止 | 禁止 | 禁止；交 writer |
| 改空间位置 / 物件状态 | 禁止，除非只是删冗余标签 | 仅 `allowed_carrier_changes` 明示时允许低强度 carrier 合并 | 禁止；交 writer |
| 加载其他 skill 做通盘风格重构 | 禁止 | 禁止；只按 patch_directive 内指令改 | 禁止 |

失败语义：patches 写得含糊无法定位 → 在 revision_summary.md 对应条目写 `not_applied` + 原因，**不瞎猜**；部分 patches 无法定位 → status=partial；全部 patches 无法定位 → status=failed。

## 产出约束

- `scene_{scene_id}.md` 保持**纯 Markdown 正文**——无 `<!-- reviser_note -->` / 无 HTML 注释 / 无批注
- `revision_summary.md` 是**单独文件**，承载改动记录——`scene_{scene_id}.md` 不碰
- 未指出的段落与原 `scene_{scene_id}.md` 应 `diff` 一致——自检方式：reviser 完成前对比 patches 未覆盖的段落和 Edit 前版本，如有差异必须恢复

## Fresh Session 约定

- reviser 每次 dispatch 都是 fresh session（对齐 Step 4 writer "一层一件事"）
- 不读本场景之前的 revision_summary（若有）——每轮 reviser 从 `pipeline/scenes/scene_{scene_id}.md` 当前版开始
- partial 档下轮重跑时，reviser 看到的 pending `patch_directive.yaml` 已被上轮 reviser 裁剪（只剩未应用 patch）——不会重复处理已改段落
- ROLLBACK 档 / REWRITE 档不由 reviser 承担——orchestrator 分流到 writer fresh session 或上游 phase
