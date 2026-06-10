# 题材世界观 few-shot 参考

> Phase 1 Step 3「选择类型的冲突生成机制」按需加载本目录单题材文件。本目录是 SKILL.md §3 跨题材对照表的**扩展实证库**——对照表给方向（题材 → driver 范畴），本目录给名著锚点 + 平台样态 + 高频禁区。
>
> **不复述** SKILL.md §3 的"原因 vs 后果"原则、末世 4 反例、"互斥 driver 并列"禁令——那些是通用规则，已在 SKILL.md 正文。本目录文件只承载**单题材内的实例 / 取材 / 平台习惯 / 禁区清单**。

## 题材 slug 表

| 中文题材 | slug | 文件 | canon 锚点 |
|---|---|---|---|
| 末世 | `apocalypse` | [`apocalypse.md`](apocalypse.md) | 长路 / I Am Legend / 流浪地球 |
| 悬疑 | `mystery` | [`mystery.md`](mystery.md) | 2666 |
| 科幻 | `scifi` | [`scifi.md`](scifi.md) | 三体Ⅰ/Ⅱ/Ⅲ / 流浪地球 |
| 武侠 | `wuxia` | [`wuxia.md`](wuxia.md) | 射雕英雄传 / 神雕侠侣 |
| 言情 | `romance` | [`romance.md`](romance.md) | 挪威的森林 / 月亮与六便士 / 斯通纳 |
| 仙侠 | `xianxia` | [`xianxia.md`](xianxia.md) | （canon 暂无锚点，仅 driver 范畴 + 平台样态） |
| 宫斗 / 权谋 | `palace-intrigue` | [`palace-intrigue.md`](palace-intrigue.md) | 白鹿原（宗族向，部分类比） |

## 加载方式

Phase 1 执行 Step 3 时，orchestrator 按 Phase 0 `genre.primary` 映射 slug，**按需加载**对应单文件——不要把整个 `genre-worldbuilding/` 目录全读。本目录是 reference，不是 SKILL.md 必读资源。

混合题材（如"科幻末世"）→ 按主导 driver 选一份主文件，必要时附加读第二份；不允许同时声明两个互斥 driver（SKILL.md §3 已锁）。

## 单文件结构约定

每份题材文件按以下骨架组织（行数控制在 80-150 行）：

1. **generative_driver 选型范畴** — 本题材 driver 必须回答的核心问题；platform_mode（平台显式钩子型）vs classic_mode（名著留白型）区分
2. **名著锚点（few-shot）** — N 部 canon-distill 实证拆解：driver_type、原因、扩散/运作方式、局部表现、派生 world_rules 节选、canon 路径
3. **平台样态参考** — 起点 / 番茄 / 知乎盐言常见显式钩子（精简列表，标注更新观察时间）
4. **高频禁区** — 该题材特有的"结果状态冒充 driver"具体形式、临场脑补高发点

## 维护

- canon 锚点的 **driver 拆解 + world_rules 关键条直接内嵌本目录**（模型读 reference 即可工作，不需要跳转）；底部"参考产物"行写 canon-distill 内逻辑路径，**不构造 markdown link**——跨 plugin 物理路径在不同安装位置上不可靠，但语义路径保留 traceability
- 平台样态参考是观察性的，季度审查（番茄首页 / 盐言主题 / 起点类目会滚动变）；标注上次审查时间
- 新增题材：补到本 README slug 表 + 创建对应 `.md`；SKILL.md §3 对照表同步加一行
- 仙侠 / 宫斗 / 武侠 等 canon 锚点不全的，标"待补"，不强行编

## 设计起源

本目录的题材 slug 表 + platform/classic mode 区分采纳自一份离线深度调研报告。**不采纳**报告里"跨 13 个 skill 全量铺开"的重方案——只在 Phase 1 落 few-shot 库，下游 Phase 2/5/6 按需消费 `generative_driver` 字段，不在自己 skill 里维护题材副本。
