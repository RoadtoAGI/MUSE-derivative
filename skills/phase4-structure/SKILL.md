---
name: phase4-structure
description: MUSE Phase 4 — 序列设计（pipeline 内部阶段，由 orchestrator 进入 Phase 4 时路由触发，不直接承接用户自然语言入口）。接收 Phase 3 的幕/Arc 框架，为每个 Arc 设计内部序列（递进的场景群），明确每个序列的核心冲突、递进方向、序列高潮、闭合/打开，并验证 Arc 内递进与序列间因果。产物 pipeline/phase4_structure.yaml 供 Phase 5 展开场景。
---

# Phase 4: 展开幕/Arc + 设计序列

## 核心原则

节拍 → 场景 → 序列层层递进，序列终结场景必须实施比序列内单场景更强的转折（原文见 `../phase5-scene-arrangement/references/mckee-scenes.md §转折层级`）。进展纠葛 = 对抗力量升级 + 不归点（原文见 `references/mckee-structure.md §进展纠葛`）。

序列是场景的递进组合——每个序列内场景的冲击力递增，序列高潮比序列内任何场景的冲击都更强。

## 输入契约

从 Phase 3 接收（核心依赖）：
- `arcs[]` — 幕/Arc 框架（逐 Arc 展开为序列）
- `inciting_incident` — 第一个序列围绕激励事件展开
- `opposing_forces` — 对抗力量分配到序列
- `story_climax_design` — 最终 Arc 的序列设计需要导向此高潮

从 Phase 0 接收（参考依赖）：
- `core_value` — 序列内冲突围绕核心价值的正负极

从 Phase 2 接收（参考依赖）：
- `protagonist.desire_system` — 序列的障碍来自欲望追求
- `deuteragonist`（若存在）— 双主角 / 守护者形态下按 protagonist 等价结构读取，参与序列对照与障碍设计
- `antagonist` — 对抗力量的具体来源

## Canon/design reference（设计前置必跑）

**本段必跑**：进入本阶段先调用 `Skill design-doc-reference`——**不要**基于"当前可见 skill 列表里没看到"或"猜测 MUSE-canon-distill 未装"做预判跳过。**先调，再由 skill 自身返回值决定是否降级**：

```
phase=4
genre=<Phase 0 genre.primary>
signals=<JSON: 至少含 structure_mode, arc_count_hint, climax_shape, pov_mode 中能填的>
```

调用成功 → Read `pipeline/references/phase4_design_ref.md`，只学习：

- **结构卷构如何编织**（Arc 间的对位、递进、嵌套）
- **卷末对位**（卷末场景如何承担跨系统编织功能 — 个人 / 群体 / 世界）
- **跨系统编织**（多主线 / 多 POV 在同一卷构内的排布逻辑）

**合法降级条件**：仅当 skill **实际返回** 扩展包未装 / KB 不可达 / 无匹配 三类信号时，才跳过本段按下方步骤自主设计。"看不到 skill 名"、"未确认是否安装"**不是**合法降级理由——这两类情况必须先调一次再判。

## 衍生前置：已有 `phase4_structure.yaml` 则在其上完善（MUSE-derivative）

本 skill 在 **MUSE-derivative**（衍生写作）运行——与 MUSE-writing 的唯一区别在此段。执行 §执行步骤 前先看 work_dir 是否已有 `pipeline/phase4_structure.yaml`（derivative 入口经 `init_derivative_run.py` 从 canon 蒸馏物 / 用户已有 pipeline 预置的继承基线）：

- **已有（继承基线）** → 不从零重生成，把它当起点在其上**完善**：续写 = 保留继承的 arc/序列/因果链不重排，在其末端追加续写段的新序列（causality 从原因果链末端展开）；跨风格 = 保留不动；其余若入口未预置则按"没有"分支重建。元数据标 `source: derived_from=<canon-slug | existing_pipeline>`。此时 §执行步骤 作**完善检查表**（缺则补），非从零产出指令。
- **没有** → 按 §执行步骤 从零生成（与 MUSE-writing 完全一致）。

两种情形产物 schema 与下游消费都与 MUSE-writing 一致——这是 derivative ≈ MUSE-writing 的根本。

## 执行步骤

### 1. 逐 Arc 设计序列

对 Phase 3 的每个 Arc，设计其内部序列。每个序列是一组递进的场景群，具有：

- **核心冲突**：这个序列围绕什么对抗展开（也是序列尺度的读者追问——读者跟住这个冲突读完整段）
- **递进方向**：冲突从哪递进到哪（不是量的增加，而是层次的深入；= 读者在本序列被带向什么方向）
- **序列高潮**：哪个事件/场景是这个序列的顶点
- **闭合/打开**：这个序列闭合了什么（= 读者本段获得什么答案），同时打开了什么新问题（= 读者被带入下一段跟住什么新问题）

这四个字段同时承载**序列级读者路径**——读者在本序列跟住什么、获得什么、被带向什么。Phase 5 的 `reader_track` 是其在单场尺度的进一步具体化。

**⚠ 设计字段是作者笔记，不是正文。** 所有字段（sequence_climax、core_conflict、escalation_direction 等）用指令性语言描述"发生什么"，**禁止写成可直接进入正文的叙事句**。Phase 6 读取这些字段时应将其视为设计意图，而非可复制的文本。

```
❌ "这个命令的潜台词只有他自己知道。"        ← 叙事句，会被 Phase 6 直接搬进正文
✅ "沈牧辰下达弹性防御令，暗含奇袭准备"      ← 指令性描述，Phase 6 需自行转化为叙事
```

**关键规则**：
- 序列高潮闭合当前问题但同时打开新问题（不做完整矛盾解决）
- 每个 Arc 内序列的冲击力递增——后一个序列的高潮比前一个更强
- 对抗力量交替或叠加分配到不同序列

序列数量由 Arc 的复杂度决定，不预设。

**对位序列（counterpoint sequence）**：除线性递进外，允许并应主动设计"对位序列"——两个序列（或同序列内两个高潮场景）在内容 / 节奏 / 价值上形成结构性对照，让读者在两条线索之间获得意义反差。常见对位轴：

- 死亡 ↔ 诞生
- 私人情感 ↔ 公共责任
- 宏大事件 ↔ 日常动作
- 法律文本 ↔ 物理暴力
- 胜利外观 ↔ 伦理失败

设计对位时，给对位中的一方（或两方都）填写 `sequence_counterpoint` 字段：

```yaml
sequence_counterpoint:
  paired_with: "另一个序列 / 场景 ID"
  contrast_axis: "死亡 / 诞生、私人 / 公共、宏大 / 日常等"
  concrete_bridge: "连接二者的物件 / 声音 / 动作 / 意象（用具体物，不写'读者感受到反差'之类抽象效果）"
```

`concrete_bridge` 必须落到具体可感知物（如"同一种鼓声从婚礼现场延入战场"），不写抽象读者效果——抽象效果是设计副产品，不是设计输入。

名著锚点：《冰与火之歌Ⅰ》奈德处刑（孩子 POV 遮蔽死亡）与丹妮火中生龙（仪式与火焰完成诞生）形成卷末"死亡 / 诞生"对位；《神雕侠侣》郭襄生日三件礼物把私人庆典与战争 / 后勤 / 江湖政治编织成跨系统对位。

### 2. 验证 Arc 内递进

检查每个 Arc 内部：
- 序列之间是否构成递进（后一个比前一个更深层次）？
- 每个序列的高潮是否都在推动 Arc 向其高潮事件靠拢？
- 是否存在纯平行排列的序列（仅增加量，不增加深度）？

### 3. 验证序列间因果

从第一个序列到最后一个序列，每一步之间是否存在因果关系？

```
ARC1-SEQ1 →（因此）ARC1-SEQ2 →（因此）ARC1-SEQ3 →（因此）ARC2-SEQ1 → ...
```

如果某两个序列之间只是时间顺序（"然后"而非"因此"），因果链断裂——需要补强序列间的因果连接，或考虑删除/合并序列。

## 输出

→ YAML 输出结构见 `references/output-schema.md`

交付物写入 `pipeline/phase4_structure.yaml`，包含：arc_expansions[]（每个 Arc 展开为序列）、causal_chain（序列级因果链）。

## 常见错误（快速 checklist）

| 错误 | 失败症状（"后果"信号） | 修正 |
|------|--------------------|------|
| 序列只堆量不递进 | 第二幕塌陷 | 每个序列的障碍必须比前一个更深层次，不是更多数量 |
| 序列高潮完全闭合矛盾 | 后续动力丧失 | 序列高潮必须同时打开新问题 |
| 在本阶段决定具体场景 | 越权到 Phase 5 | Phase 4 只设计序列方向，场景是 Phase 5 的事 |

→ 理论深度参考见 `references/mckee-structure.md`
