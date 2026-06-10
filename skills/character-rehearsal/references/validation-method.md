# 角色校验方法

> **当前 scope**：审稿阶段的 dispatch prompt 仍走 adapter-only（读 `pipeline/characters/{角色名}.md`），未升级到 Phase 6 的 skill-backed 加载（skill + state + role_brief）。升级是独立任务，未触发前保持 adapter-only 兼容。

## 用途

审稿阶段的角色校验协议。以角色视角审查场景文本的声音一致性。

---

## 时机

Phase 6 全部场景完成后，审稿模块（`story-review`）执行期间。`pipeline/characters/{角色名}.md` 可用。

---

## 执行步骤

### 1. dispatch 预定义 agent `character-actor`

orchestrator 向 agent 传递路径和校验指令：

```
你是角色 {角色名}（role_slug: {slug}）。
读取 pipeline/characters/{角色名}.md，进入角色。
我要给你看一些文本，请告诉我这像不像你说的话。
```

Agent 自行读取人设文件。

### 2. 展示关键段落

选择情感密度高或声音特征最突出的段落，逐段展示给 agent。

### 3. 收集反馈

问："这像你会说的话吗？哪里不像？你会怎么说？"

### 4. 落盘与反馈处理

Agent 将校验反馈写入 `pipeline/staging/scene_{scene_id}/{slug}_validation.md`，返回一句确认。orchestrator 按需读取。

（slug 同 Phase 6 情境排练，语义见 `situational-method.md §4`；由 character-persona `build-meta.yaml` 落定。）

将反馈纳入审稿报告的声音一致性维度，供 Phase 7 修订使用。

注意：角色 subagent 的反馈是参考而非权威——同一个模型可能倾向于同意自己的产出。重点关注角色说"不像"的地方。
