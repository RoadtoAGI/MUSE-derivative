# canon 路径 — MUSE-canon-distill 调用

## 何时走 canon

原型属于以下类型时强制走 canon 路径：
- **小说**（含网络文学、严肃文学、类型小说）
- **文学作品**（诗集、散文集——但通常 MUSE 写作不涉及）
- **童话 / 寓言**（如安徒生、格林）

判别启发式：作品在公开渠道有完整文本可检索 + 属于"被研究过的文学作品"——MUSE-canon-distill 知识库以名著为主，覆盖了主要中外名著。

## 触发方式

跨 plugin 调用走 Claude Code 官方 skill 触发机制，不用 Read 工具读物理路径。三个 skill 各司其职：

| 子 skill | 用途 | 触发命令 |
|---|---|---|
| `scene-reference` | 检索原作某场景的设计原理 / 节拍 / 视角 / 风格 | `Skill scene-reference` |
| `character-kb-distill` | 抽炼原作某人物的档案（声音、关系、弧光、价值观） | `Skill character-kb-distill` |
| `novel-analysis` | 抽炼整部小说的结构分析（三幕、控制思想、类型公约）| `Skill novel-analysis` |

按 prototype 需求决定调几个：
- 仅需人物档案 → `character-kb-distill`
- 需人物 + 关键场景作风格指纹 → `character-kb-distill` + `scene-reference`
- 需整部作品的世界规则 / 结构 → `novel-analysis`（粒度最粗，最经济）

## 输出映射到 prototype card schema

MUSE-canon-distill 子 skill 的输出格式各自不同；本 skill 负责映射到统一的 prototype card schema：

| canon 子 skill 输出 | 映射到 prototype card 字段 |
|---|---|
| character-kb-distill: `voice_signature` | `style_signature.voice` |
| character-kb-distill: `key_traits[]` | `key_traits[]` |
| character-kb-distill: `relationships{}` | 拼接到 `key_traits` 末尾（"与 X 的关系：..."）|
| novel-analysis: `world_rules[]` | `world_rules[]` |
| novel-analysis: `controlling_idea` | 拼接到 `constraints`（"控制思想：..."）|
| scene-reference: `pacing_pattern` | `style_signature.pacing` |
| scene-reference: 章节锚点 | `sources[]` |

## 降级链

| 情况 | 降级处理 |
|---|---|
| MUSE-canon-distill 姊妹 plugin 未安装 | 转走 web 路径；prototype_type 仍标 `novel`，retrieval_path 标 `web`（标注降级原因到 sources）|
| canon 知识库不含目标作品（如冷门小说） | 转走 web 路径；同上 |
| 跨 plugin skill 触发失败 | 报告失败、降级到 web；不静默退化 |

降级不是失败——很多作品 canon 没收录但 web 资料丰富；只要 prototype card schema 字段被填上就 OK。

## 错误处理

- 触发 `Skill scene-reference` 等失败：报告原因，降级 web
- 子 skill 返回字段不全：尽量填，缺的字段留空（schema 字段除 prototype_id / type / source_label / retrieval_path / retrieved_at / sources 外均 optional）
- 同名作品歧义（如多个《飘》）：source_label 写明作者消歧（如 "Margaret Mitchell《飘》" vs 其他）

## 输出映射到 phase seeds（衍生模式）

`reuse_mode != reference_only` 时，canon 路径需反推 phase seeds。映射表：

| 目标 seed 字段 | canon 子 skill 输出来源 |
|---|---|
| `seeds/phase0_conception.seed.yaml.{premise,controlling_idea,genre}` | novel-analysis |
| `seeds/phase1_world.seed.yaml.world_rules[]` | novel-analysis: `world_rules` + design-doc-reference 世界设定档案 |
| `seeds/phase1_world.seed.yaml.4d_setting` | design-doc-reference（如有） |
| `seeds/phase2_character.seed.yaml.characters[]` | character-kb-distill 输出（按 query 涉及角色组合） |
| `seeds/phase3_spine.seed.yaml.inherited_spine` | novel-analysis: spine 段 |
| `seeds/phase3_spine.seed.yaml.continuation_point` | 用户 query + scene-reference 章节锚点 |
| `seeds/phase3_spine.seed.yaml.unresolved_threads[]` | scene-reference 检索原作结尾 N 章 + character-kb-distill 未达成欲望 |
| `seeds/phase4_structure.seed.yaml.inherited_structure` | novel-analysis: 三幕段 |
| `seeds/phase5_scenes.seed.yaml.inherited_scenes[]` | scene-reference 全场景索引 |
| `text/continuity_anchors.yaml.proper_nouns[]` | character-kb-distill: 角色名 / aliases；novel-analysis: 关键术语 |
| `text/continuity_anchors.yaml.signature_phrases[]` | scene-reference: ≤ 15 字标志性短表达 |
| `text/tail_window_summary.yaml` | scene-reference: 原作结尾 N 章状态摘要（不存原文） |
| `text/scene_map.yaml.scenes[]` | scene-reference: 全场景 `scene_function` + `canon_facts` |
| `text/style_fewshot_notes.yaml.voice_markers` | novel-analysis: 风格指纹；character-kb-distill: voice_signature |

canon 路径**最完整**支持衍生模式：novel-analysis 提供 spine / structure / world / genre；scene-reference 提供场景索引 + 短表达 + 状态摘要；character-kb-distill 提供角色档案 + 关系网。

部分字段无法反推时，标 `seed_quality: partial` 在对应 seed 文件 metadata 段；调用方按 partial 决定是否退回 reference_only 模式。
