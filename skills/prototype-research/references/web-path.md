# web 路径 — tavily / WebSearch / WebFetch 调用

## 何时走 web

原型属于以下类型时走 web 路径：
- **电影 / 电视 / 戏剧 / 戏曲**（MUSE-canon-distill 不覆盖影视戏曲）
- **真实人物 / 历史人物**（如劳伦·丁利环保家、文革当事人）
- **真实地点**（如乌镇、20s 上海）
- **历史事件**（如赤壁之战、法国大革命）
- **神话 / 民间传说**（如北欧神话、希腊神话）
- **职业原型**（如法医、纪录片导演的工作日常）

判别启发式：原型在公开互联网有丰富资料、但不在 MUSE-canon-distill 名著语料库内——即走 web。

## MCP 优先级与降级链

| 优先级 | MCP | 适用 |
|---|---|---|
| 1 | tavily | 综合检索；返回多源摘要；最少 token |
| 2 | WebSearch | tavily 不可用时；返回搜索结果列表 |
| 3 | WebFetch | 已知具体 URL 时；从指定页面抽取信息 |

通常组合用法：
1. tavily 出整体认知（人物 / 事件 / 地点的基本事实）
2. 命中关键源（如维基、官方简介），用 WebFetch 拉详情
3. 多源交叉验证（避免单源偏差）

## 检索策略（按 prototype_type 分）

### film / drama（电影 / 电视 / 戏剧 / 戏曲）

关键词模板：`{作品名} character analysis` / `{作品名} 角色分析` / `{作品名} plot summary`

抽取目标：
- 主要角色的性格 / 关系 → `key_traits`
- 剧情结构 / 张力曲线 → `style_signature.pacing`
- 标志性场面调度（如戏曲的程式动作）→ `world_rules`
- 创作背景（导演 / 编剧风格）→ `style_signature.voice`

### real-person / 历史人物

关键词模板：`{人物名} biography` / `{人物名} 生平` / `{人物名} 主要事迹`

抽取目标：
- 公开事实（出生、教育、职业经历）→ `key_traits`
- 社会位置 / 行为矛盾 / 价值观 → `key_traits` + `constraints`
- 典型经历 / 标志性事件 → `key_traits`
- 公开访谈 / 自述（如有）→ `style_signature.voice`

**注意**：避免抽取仅来自单一八卦源 / 私人猜测的内容；公开档案优先。

### real-location（真实地点）

关键词模板：`{地点名} 地理` / `{地点名} 风俗文化` / `{地点名} 历史`

抽取目标：
- 地理 / 气候 / 物产 → `world_rules`
- 风俗 / 节庆 / 方言 → `world_rules`
- 历史沿革（如旧城改造前后）→ `world_rules`
- 著名地标 / 街区 → `sources` 引用

### historical-event（历史事件）

关键词模板：`{事件名} 经过` / `{事件名} 时间线` / `{事件名} 关键人物`

抽取目标：
- 事件经过 → 拼接到 `world_rules`
- 关键人物 → 列入 `key_traits`（但本 skill 不替这些人物建独立 prototype card；如需可由派发方再触发 prototype-research）
- 后果 / 影响 → `constraints`（如"必须尊重事件结局"）

### myth（神话）

关键词模板：`{神话体系} 主要神祇` / `{神话体系} 创世神话` / `{神话体系} 核心母题`

抽取目标：
- 神祇谱系 → `key_traits`
- 创世 / 末日 / 重生母题 → `world_rules`
- 设定规则（如北欧神话的命运观）→ `constraints`

## distill 到 prototype card

web 检索返回大量原文 / 多段摘要——本 skill 必须做 distill 而非堆砌：

- 每个字段保持简洁（一行一条；不超过 30 字）
- 不复制网页长段——paraphrase
- 多源交叉后取共识，不取单源争议内容
- sources 字段记录所有用过的 URL，便于事后 audit

## 降级与错误处理

| 情况 | 处理 |
|---|---|
| tavily 不可用 → WebSearch 不可用 | 仅用 WebFetch（需用户提供具体 URL）；若无 URL，prototype card 标 `retrieval_path: direct` 让用户提供资料 |
| 网络全部不可用 | 报告失败，不静默生成空 prototype card |
| 资料严重不足（如冷门小众戏曲） | prototype card 各字段可留空；sources 标"web 资料不足"，提示派发方降级到 direct 路径或舍弃原型 |
| 检索到的资料与用户描述明显矛盾 | 报告冲突，让派发方决定走哪个版本 |

## 输出映射到 phase seeds（衍生模式 — web 路径降级）

`reuse_mode != reference_only` 时，web 路径反推 phase seeds 受限：

| 目标 seed | web 路径反推能力 | 降级标记 |
|---|---|---|
| `seeds/phase0_conception.seed.yaml` | 可产（从作品名 + 主题搜索） | full |
| `seeds/phase1_world.seed.yaml.world_rules` | 可产（设定 wiki / fan wiki） | full / partial |
| `seeds/phase2_character.seed.yaml.characters[]` | 可产但粒度有限（角色 wiki paraphrase） | partial（需手工补充关系网 / 弧光）|
| `seeds/phase3_spine.seed.yaml.inherited_spine` | **基本不可产**（plot summary 通常只是事件流，不含 spine 设计语义）| 标 `seed_quality: not_available`；建议调用方退回 reference_only |
| `seeds/phase4_structure.seed.yaml` | 同上 | not_available |
| `seeds/phase5_scenes.seed.yaml.inherited_scenes[]` | 仅可粗粒度产（章节标题 + 概要） | partial |
| `text/continuity_anchors.yaml` | 可产（专名 / 短表达可从 wiki 抽） | full |
| `text/tail_window_summary.yaml` | 仅小说类原型可产（电影 / 戏剧 web 资料通常无场级状态） | partial / not_available |
| `text/scene_map.yaml` | 仅有详细 wiki 时可产 | partial |
| `text/style_fewshot_notes.yaml` | 可产（风格分析文章） | full / partial |

**结论**：web 路径适合 `reference_only` 与 `cross_style_rewrite`（仅需 scene_map 粗粒度）+ 部分 `fan_fiction`（Phase 0/1 + 角色轮廓）；**不适合 `sequel`**（spine / structure / unresolved_threads 反推几乎不可能）。

调用方收到 web 路径 `sequel` 模式产物含 `seed_quality: not_available` 时应：
1. 提示用户：原作只有 web 资料，无法精确反推续写所需的设计骨架
2. 选项 A：降级为 `fan_fiction` 模式（不需精确接续，只需世界 + 角色继承）
3. 选项 B：要求用户提供原作具体文本片段，走 `retrieval_path: direct`
