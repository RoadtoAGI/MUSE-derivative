---
name: prototype-research
description: MUSE 写作前置调研层 — 调用方传入原型描述 + reuse_mode 时执行 canon / web / direct 三路检索，按 reuse_mode 产出 prototype bundle（card + reuse_profile + 各 phase seed + text 锚点）到 pipeline/references/prototypes/{slug}/。**仅由 screenplay-writing（改编/历史/戏曲题材时触发）/ 其他原创写作 skill（按调用方判定，默认 reference_only）内部调用，不被用户直接触发**。同人/续写/番外/跨风格改编由姊妹包 muse-derivative 走 canon-distill 硬继承路径（不经本调研层）。不写正文，不直接被 writer 读取——card / seeds / text 经下游 phase skill 与 inspiration_ledger INS-* 闭环消费。
---

# prototype-research — MUSE 写作前置调研层

## 何时使用

**仅由其他写作 skill 内部调用，不被用户直接触发**——本 skill 是调研层 wrapper，调用方决定何时触发 + 何 reuse_mode。

调用方触发规则：

| 调用方 | 触发策略 | reuse_mode 注入 |
|---|---|---|
| `screenplay-writing` | **改编/历史/戏曲题材时触发** | 通常 `reference_only`（剧本链路不走衍生复用深度模型）|
| `story-writing` / `novel-outline` / `plot-design` / `character-design` | 按调用方判定 query 含明确原型信号时触发 | 默认 `reference_only`（弱原型，软约束） |

适用场景示例：
- 同人续写需要原作世界规则与人物声音参考（如续《三体》→ 调研叶文洁人物档案 + ETO 设定，reuse_mode=sequel）
- 改编已有作品（如《美人鱼》→ 都市奇幻，reuse_mode=cross_style_rewrite）
- 角色设计参照现实人物或电影角色（reuse_mode=reference_only）
- 场景设计参照真实地点 / 历史事件 / 戏曲形式（reuse_mode=reference_only）

## §1. 输入 / 输出契约

**输入**（由调用方注入）：
- `prototype_description`（必填）：原型描述（作品名 / 人物名 / 真实事件 / 真实地点 / 时代背景等自然语言）
- `reuse_mode`（必填）：枚举 `reference_only | fan_fiction | sequel | spin_off | cross_style_rewrite`；决定本次产物范围
- `slug`（可选）：调用方建议的目录名 slug；缺省时本 skill 自动生成

**输出**：
- `pipeline/references/prototypes/{slug}/`（目录 bundle，详 [`references/prototype-card-schema.md`](references/prototype-card-schema.md)）

调用方决定后续是否触发 promote 到 inspiration_ledger（reference_only 模式）或直接消费 seeds/text（衍生模式）。

## §2. 路径判定决策

按原型类型选择检索路径——三路互斥：

| 原型类型 | 路径 | 检索方式 | 适合 reuse_mode |
|---|---|---|---|
| 小说 / 文学作品 / 童话 | **canon** | MUSE-canon-distill design-doc-reference / scene-reference / character-kb-distill / novel-analysis | 全部 5 档（canon 路径反推 phase seed 最完整） |
| 电影 / 电视 / 戏剧 / 戏曲 | **web** | tavily / WebSearch / WebFetch | reference_only / cross_style_rewrite（web 资料反推 phase seed 粒度有限）|
| 真实人物 / 历史人物 / 职业原型 | **web** | tavily / WebSearch | reference_only（不适合 fan_fiction / sequel）|
| 真实地点 / 时代背景 / 历史事件 | **web** | tavily / WebSearch | reference_only |
| 神话 / 民间传说 | **web** | tavily / WebSearch | reference_only / fan_fiction |
| 用户提供资料（query 内嵌长文本）| **direct** | 结构化摘要 | 按用户提供资料粒度决定 |

路径选择不是审美决定——由原型类型本身决定。

## §3. 按 reuse_mode 执行

按调用方注入的 `reuse_mode` 决定本次产哪些文件。**产物矩阵 SSOT 在 [`references/prototype-card-schema.md`](references/prototype-card-schema.md) "reuse_mode → 产物矩阵" 表**。

通用步骤：

1. 创建目录 `pipeline/references/prototypes/{slug}/`（已由 `init_run.py` 落地父目录 `references/prototypes/`，本步只 mkdir slug 子目录）
2. **必产**：`prototype_card.yaml`（按 §2 选定的路径检索后填字段；标 `reuse_mode_recommended` = 调用方传入的 mode 或本 skill 按原型类型推荐的）
3. 按 `reuse_mode` 决定是否产 `reuse_profile.yaml` + `seeds/` + `text/`：

### reuse_mode=reference_only

仅产 card。调用方走 inspiration_ledger 软约束注入路径。

### 衍生四档（fan_fiction / sequel / spin_off / cross_style_rewrite）

执行对应模式前 Read 该模式的执行细则文件，再按其产物清单与 phase_execution_plan 执行：

| reuse_mode | 执行细则 |
|---|---|
| fan_fiction | [references/reuse-mode-fan-fiction.md](references/reuse-mode-fan-fiction.md) |
| sequel | [references/reuse-mode-sequel.md](references/reuse-mode-sequel.md) |
| spin_off | [references/reuse-mode-spin-off.md](references/reuse-mode-spin-off.md) |
| cross_style_rewrite | [references/reuse-mode-cross-style-rewrite.md](references/reuse-mode-cross-style-rewrite.md) |

## §4. canon 路径

详 [`references/canon-path.md`](references/canon-path.md)。

跨 plugin 调用：通过 `Skill design-doc-reference` / `Skill scene-reference` / `Skill character-kb-distill` / `Skill novel-analysis` 触发 MUSE-canon-distill 姊妹包内的 skill。**不要**用 Read 工具读跨 plugin 物理路径——plugin 安装位置由 marketplace 决定，物理路径不可靠。

MUSE-canon-distill 未安装时 canon 路径降级：转走 web 路径（用 tavily / WebSearch 查作品名 + 章节）；衍生模式下标 `degraded_from: canon`。

## §5. web 路径

详 [`references/web-path.md`](references/web-path.md)。

MCP 优先级：tavily → WebSearch → WebFetch。降级链在 references 内说明。

## §6. 与 inspiration_ledger 闭环（reference_only 模式）

prototype card 落盘后流向（reference_only 模式）：

```
prototype card (PROT-{slug})
  → inspiration candidate（候选池）
  → Phase 1 世界 / Phase 2 人物 / Phase 5 编排选择性 promote
  → inspiration_ledger.yaml ledger entry（含 INS-* 编号）
  → scene_card.inspiration_refs 引用
  → writer 经现有 inspiration_ledger 接口消费
```

writer **不直接读** prototype card；只读 `scene_card.inspiration_refs` 引用的 ledger entry。

**衍生模式（fan_fiction / sequel / spin_off / cross_style_rewrite）不由本 skill 消费**——基于既有作品的同人 / 续写 / 外传 / 跨风格改编走 derivative-writing 的 canon-distill 硬继承路径。本 skill 只承担 `reference_only` 弱原型软约束 → ledger 注入。

## §7. 不做

- 不写正文 — 调研层职责，不入 prose 链路
- 不改 story design — 不替 Phase 0-5 做创意决策（seeds 是参考输入，不是 design 决策）
- 不被 writer 直接读取 — writer 输入合同保持现状
- 不被用户直接触发 — 由调用方写作 skill 按需触发
- 不自行判 reuse_mode — 由调用方 dispatcher 注入；本 skill 可在 card 里写 `reuse_mode_recommended` 但不替调用方拍板
- text bundle 不存大段原文 — 最多 ≤ 15 字短引；存策略 + 锚点 + 状态摘要
