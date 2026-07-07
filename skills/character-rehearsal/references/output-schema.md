# performance 素材产物 schema

本文件是 Phase 6 performance 素材产物的**唯一权威 schema**。审稿校验(validation)的输出契约见文末。

## Phase 6 performance 素材

产出路径:`pipeline/staging/scene_{scene_id}/{slug}_performance.md`,per-role 独立文件(并行 fan-out 各写各的,无写冲突)。

Actor 按以下 schema 产出,orchestrator 不做二次提取,writer 直接消费:

```yaml
character: {slug}
goal_anchor: <一行,锚 role_brief 本场目标——引用不复制>

decisions:        # 行为/决策素材
  - at: <本场压力点/节拍>
    what: <决策倾向,如"被逼问时转向整理马具而不是回答">
    why_visible: <读者能看见的动机线索——不是动机说明书>

actions:          # 2-4 个具体身体动作/物件处理候选,带对象

lines:            # 3-5 条台词候选
  - to: <对象角色>
    intent: <行动目的:说服/威胁/试探/隐瞒/求证…>
    text: "…"
    subtext: <不可直说的信息差 / 对对方施加的可推断压力——不是内心陈述>

reactions:        # 交互素材:per 对手角色
  - vs: <对手 slug>
    if: <对手可能的动作/立场(从其 role_brief 段推)>
    then: <我的反应候选>
    misread_surfaced: <我对他的误读如何在交锋中露出来>

tells:            # 心理的唯一合法形态:外显信号
  - <身体信号/错位台词/沉默时长/视线落点>

forbidden:        # 硬约束,writer 不可违反
  - <禁用语气/绝不说的话 + 一句理由>
```

字段值中文、key 英文(与 role_brief 风格一致)。

**slug** = 角色的 `role_slug`(与 `pipeline/story-character-skills/.claude/skills/{slug}/` 和 `role_briefs.md` 内 `character: {slug}` 字段对齐;中文名 → slug 的映射由 character-persona build-meta.yaml 落定)。

## 三条防病灶纪律(schema 的灵魂)

1. **目标/动机不重新生产**——role_brief 是权威源,`goal_anchor` 只锚定。角色 agent 是 role_brief 的消费者,不是第二作者(防第二权威源);
2. **心理只准 tells 外显**——产物任何字段(**含 `lines.subtext`**)出现"我感到/我其实/我害怕/我爱你/我恨你/他其实/他心里"类内心直译句,self-check 重跑;subtext 只准写信息差与施压方向,不准写心理陈述;
3. **`why_visible` 必须是可见线索**——writer 拿到的已是外显素材,没有内心说明书可翻译,从生产端封"旁白翻译潜台词"。

落盘前 self-check 全项见 `situational-method.md`。

## 审稿:角色校验

orchestrator 提取:
- **一致性反馈** → `pipeline/staging/scene_{scene_id}/{slug}_validation.md`
- 内容:"像/不像" + 具体段落指出 + 角色会怎么说的替代建议
