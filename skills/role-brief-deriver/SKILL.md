---
name: role-brief-deriver
description: MUSE Phase 6 runtime role_brief 派生职责。为单个场景的每个在场角色读入 Phase 5 scene_card / Phase 2 人物系统 / 角色 runtime package / 前场景 draft 尾段，产出合集版 role_briefs.md。由 role-brief-deriver agent 加载，不直接被 orchestrator 或用户调用。
---

# role-brief-deriver：Phase 6 runtime role_brief 派生

## 核心原则

> role_brief 是 Phase 6 为每个场景、每个在场角色派生的一次性执行指令。它把 Phase 2 的静态人设 + Phase 5 的场景规划 + runtime 动态（state / 前场景动量）收敛成 writer 能直接消费的 13 字段结构。

**范围边界**：
- **只做派生**，不产正文 / 叙事 / 对白
- **只读文件**，不推理场景走向、不调其他 skill
- **一场景一次调用**，由 orchestrator 通过当前运行时 subagent dispatch 启动；不通过脚本 / CLI wrapper 启动（详见 [phase6-scene-development/references/execution-protocol.md](../phase6-scene-development/references/execution-protocol.md) §反模式表）

## 输入契约

每次调用针对**单个 scene_id**。所有路径相对 `pipeline/`（cwd 为 StoryStudio 工作区根）。

| 文件 | 必需 | 路径（相对 `pipeline/`） | 缺失时的处理 |
|---|---|---|---|
| Phase 5 scene_card | 必需 | `phase5_scenes.yaml`（定位 `sequence_expansions[].scenes[]` 中 scene_id 匹配项） | 失败退出 |
| Phase 2 角色系统 | 必需 | `phase2_character.yaml`（单数；Phase 2 产出） | 失败退出 |
| 角色 runtime package | 必需 | `story-character-skills/.claude/skills/{slug}/SKILL.md`（角色长期人设 / 声音权威源） | 失败退出 |
| 角色 build-meta | 必需 | `story-character-skills/.claude/skills/{slug}/build-meta.yaml`（读取 `character_display_name`，用于反查 Phase 2 baseline） | 失败退出 |
| 角色 runtime state | 可选 fallback | `story-character-skills/.claude/skills/{slug}/state.md` | state 字段回退到 phase2_character.yaml baseline |
| 前场景 draft 尾段 | 可选 fallback | `scene_{scene_id-1}/draft_tail.md` | `desire_now` / `fear_now` / `misread_now` 仅依赖 state.md，不融前场景动量；`misread_now` 可为 `null` |

## 输出契约

### 输出路径硬约定

- **合集版**：`pipeline/scene_{scene_id}/role_briefs.md`（writer 消费；每 participant 一份 YAML body 顺序拼接）

### 输出 schema（13 字段）

**Fallback 语义单一真相规则**：**缺输入 → 字段用空 list `[]` 或 `null`**，**不使用任何注释 / 标记 / "pending" 占位**。理由：(1) validator 能用同一逻辑（dict 解析 + 非空检查）；(2) 模型不用记住"要注 'pending'"的格式约定；(3) 空值本身就是 fallback 的单一真相。

每角色 YAML body：

```yaml
scene_id: S0X
character: <slug>
primary_objective: <string>
suppressed_pressure: <string>
scene_stake: <string>
known_constraints: [<string>, ...]
info_boundary: [<string>, ...]
relevant_facts: [<string>, ...]
boldness_guardrails: <string>
desire_now: <string>
fear_now: <string>
misread_now: <string | null>
carrier_hint:
  role_in_carrier: "actor | witness | object_holder | bystander | absent"
  what_to_do: "如果是 actor / object_holder，本场景需要他完成什么具体动作或物件操作"
  what_not_to_explain: "如果是 actor / witness，本场景他绝对不能内心解释 carrier 的意义"
omission_now:
  - "<本场景该角色绝对不能说 / 不能想 / 不能让读者知道的部分>"
irreversibility_now:
  - "<本场景该角色将完成的不可逆动作，或 null>"
```

### 必填 / 可选划分（validator 权威）

- **必填非空**（6 字段）：`primary_objective` / `suppressed_pressure` / `scene_stake` / `boldness_guardrails` / `desire_now` / `fear_now`
- **必填 list 非空**（1 字段）：`known_constraints`（至少 1 项）
- **可选 fallback**（3 字段）：`info_boundary`（无 runtime 客观世界状态 → `[]`）/ `relevant_facts`（同）/ `misread_now`（无 state.md 且无 draft_tail → `null`）
- **可选 fallback**（3 字段，scene_card 缺对应字段时 fallback）：
  - `carrier_hint`：scene_card 无 `craft_carrier` 字段时 = `{role_in_carrier: bystander, what_to_do: null, what_not_to_explain: null}`
  - `omission_now`：scene_card 无 `omission_plan` 时 = `[]`
  - `irreversibility_now`：scene_card 无 `irreversible_action` 或本角色非执行者时 = `[]`
- **`boldness_guardrails`**：占位文本即可，非空。

### 合集版 role_briefs.md 格式

各角色 YAML body 拼接（顺序同 scene_card.participants），顶部加：

```markdown
# Scene {scene_id} role_briefs

生成时间：{ISO8601 时间戳}

---

（逐角色 YAML body 内容，各角色之间用 `---` 分隔）
```

## 执行步骤

1. 读 `pipeline/phase5_scenes.yaml`，定位 `sequence_expansions[].scenes[]` 中 `scene_id == {当前 scene_id}` 的 scene_card，提取 `participants`（slug 列表）和 `title` / `location_time` / `conflict` / `value_start` / `value_end` / `reader_track` / `scene_tasks` / `beat_direction` / `handoff` 等上下文（字段权威源见 [`phase5-scene-arrangement/SKILL.md §1`](../phase5-scene-arrangement/SKILL.md)；禁用字段名 `intent` / `beat_hint` 不消费）
2. 读 `pipeline/phase2_character.yaml`，准备按角色 `name` 反查 baseline（protagonist / deuteragonist / antagonist / supporting_cast / relationships；提取 `desire` / `fear` / `voice_traits` 等可用字段）
3. 对每个 participant slug：
   - 读 `pipeline/story-character-skills/.claude/skills/{slug}/build-meta.yaml`，取 `character_display_name`
   - 用 `character_display_name` 在 `phase2_character.yaml` 的 `name` 字段中匹配 baseline
   - 读 `pipeline/story-character-skills/.claude/skills/{slug}/SKILL.md`（run 级角色资产文件，非 skill 入口加载）
   - 试读 `pipeline/story-character-skills/.claude/skills/{slug}/state.md`（缺则用 phase2 baseline）
   - 试读 `pipeline/scene_{前一场景 id}/draft_tail.md`（缺则 `misread_now` = `null`）
   - `info_boundary` / `relevant_facts` 取 `[]`（主干 plugin 无 runtime 客观世界状态）
   - 读 `pipeline/phase5_scenes.yaml` 中本 scene 的 `craft_carrier` / `omission_plan` / `irreversible_action`（若存在）
   - 按 participant 角色判断 `carrier_hint.role_in_carrier`：
     - 角色名出现在 `irreversible_action` 描述中 → `actor`
     - 角色名出现在 `craft_carrier.concrete_anchor` → `object_holder`
     - 该角色仅"在场观察" → `witness`
     - POV 但关键事件不发生于 ta 视野 → `bystander`
     - 角色刻意缺席 → `absent`
   - 从 `omission_plan` 筛选属于本角色 voice 范围的条目，填 `omission_now`
   - 从 `irreversible_action` 筛选本角色执行的动作，填 `irreversibility_now`
   - 收敛为 13 字段 YAML
4. 写 `pipeline/scene_{scene_id}/role_briefs.md`（合集，participants 顺序拼接）

## 完成信号

全部文件写毕后回复：

```
done role_brief for scene {scene_id}
```

## 不做清单

- 不产正文 / 叙事 / 对白
- 不推理场景走向（`conflict` / `value_start` / `value_end` / `reader_track` / `beat_direction` 已在 scene_card 中）
- 不调其他 skill（不借 character-persona 等）
- 不改写 Phase 2 / Phase 5 文件
- 不创建 `scene_{scene_id}/` 以外的目录

## 不读

- `pipeline/characters/{中文角色名}.md`（adapter，build-time 校验视图；slug→display_name 反查走 `build-meta.yaml.character_display_name`）
