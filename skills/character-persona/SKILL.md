---
name: character-persona
description: 角色人格构建器 — Phase 2 完成后，将结构化人物设计转化为标准化的运行时角色 Skill 包。当 Phase 2 人物系统设计完成、需要为角色生成独立的人格 Skill 时使用。只构建，不执行角色扮演。
user-invocable: true
argument-hint: "build | rebuild <role-slug>"
allowed-tools: Read Write Edit Bash Glob
version: 1
---

# 角色人格构建器（Character Persona Builder）

> 本 Skill 是**元技能/构建器**：把 Phase 2 的结构化人物数据转化为可被角色 Agent 加载的标准 Skill 包。
> 它不执行角色扮演、不触发排练。

## 接口约束（违反会导致下游断裂）

| # | 约束 | 违反后果 |
|---|------|---------|
| 1 | 使用 `role_slug` 作为 skill 目录名（小写字母 + 连字符，如 `li-an`、`xiao-long-nv`），不拼接故事前缀。隔离由工作目录承担（`pipeline/story-character-skills/`，每个 query 独立目录） | 角色 Skill 无法被当前运行时发现，或与同名角色（不同来源）冲突 |
| 2 | `pipeline/characters/{角色名}.md`（adapter）是 SKILL.md 的只读派生物，**禁止手改** | adapter 与 SKILL.md 出现双源漂移，审稿和校验以哪个为准不明确 |
| 3 | SKILL.md frontmatter 的 `version` 字段应与 build-meta.yaml 同步维护 | adapter 物理校验由 `adapter_sha256` 锁定 |
| 4 | `rebuild` 绝不覆盖 state.md（state.md 包含角色 agent 的运行时记忆） | 角色失忆，破坏跨场景的主观状态连续性 |
| 5 | 资产写入路径固定：`pipeline/story-character-skills/.claude/skills/{role-slug}/` + `pipeline/characters/{角色名}.md` | 与 pipeline 全局目录契约（init_derivative_run.py 建的 work_dir 骨架）不一致，下游消费方读取失败 |

## 触发条件

- Phase 2（人物系统设计）全部步骤完成
- `pipeline/phase2_character.yaml` 已生成
- orchestrator 准备为角色创建独立的人格 Skill

## 输入

### 主输入（必须）

`pipeline/phase2_character.yaml` — Phase 2 产出的结构化人物数据。

需要从中提取的关键字段：
- `protagonist`：desire_system, character_arc, characterization_vs_truth, voice_traits, voice_boundaries, backstory, daily_life, empathy_mechanism
- `deuteragonist`（若存在）：结构同 protagonist，按同一路径提取 desire_system, character_arc, characterization_vs_truth, voice_traits, voice_boundaries, backstory, daily_life, empathy_mechanism
- `antagonist`：name, motivation, desire, voice_traits, voice_boundaries
- `supporting_cast[]`：name, function, relationship, voice_traits_summary
- `contrast_axes`：角色间的极化关系
- `relationships`：权力动态、关键张力

### 补充输入（可选，按需读取）

| 文件 | 读取条件 | 提取内容 |
|------|---------|---------|
| `pipeline/phase0_conception.yaml` | 角色声音需要与作品整体风格对齐时 | `style_directives`（风格指令）、`core_value`（核心价值） |
| `pipeline/phase1_world.yaml` | 角色身份与处境需要世界规则支撑时 | `daily_life`（日常生活）、`world_rules`（世界规则）、`creative_constraints`（创作约束） |

读取原则：**不整体吞入**，只提取与当前角色直接相关的片段。

---

## 执行流程

### Step 1：读取输入，确定构建范围

1. 读 `pipeline/phase2_character.yaml`
2. 角色筛选 + slug 命名：按下面"关于角色选择与 slug 命名"小节执行——先判断哪些角色需要构建，再为每个角色确定 `role_slug`，并推导 `story_slug`
3. 按需读取 phase0/phase1 补充输入

### 关于角色选择与 slug 命名

（story_slug 只作元数据与报告标题，不参与 skill 命名；role_slug 作为 skill 目录名与 build-meta 字段）

- 判断哪些角色需要构建独立 Skill：
  - **protagonist、deuteragonist（若存在）和 antagonist**：总是构建
  - **配角**：根据叙事需求判断——如果这个配角有独立对白场景、会与主角产生关键互动、或声音需要与其他角色区分开，就值得构建。Phase 2 阶段可能无法完全确定，Phase 5 场景分配后可通过 `/character-persona build` 补充
- 确定 `story_slug`（按优先级）：
  - 数据集创作：使用 `{数据集名}_{index}`（如 `writing-bench_184`）
  - 独立创作：从 `phase0_conception.yaml` 的 title 推导（如 `desert-outpost`）
  - 以上都不可用时：根据 premise 自拟简短 slug，并在 build-report 中说明
- 为每个角色生成 `role_slug`（小写字母 + 连字符，从中文名音译，如 `li-an`、`xiao-long-nv`、`chen-mo`），既是 skill 目录名也是 build-meta 中的字段

### Step 2：为每个角色生成 Skill 包

对每个角色执行以下操作。参考 `${SKILL_DIR}/references/skill-template.md` 中的模板；填写启发见 [`${SKILL_DIR}/references/runtime-writing-guide.md`](references/runtime-writing-guide.md)。

#### 2a. 生成 SKILL.md（静态人格定义）

从 Phase 2 数据中提炼角色的人格定义，按 skill-template.md 的结构落盘。

生成时遵循以下**创作启发**（质量倾向，不是硬约束；理论依据见 `${SKILL_DIR}/references/mckee-voice-principles.md`）：

- **用自然语言，不用结构化参数**：voice_traits 转化时保留倾向性描述，去掉"情感→修辞"映射关系
- **保留矛盾和棱角**：characterization_vs_truth 的裂隙是角色的戏剧张力来源，不要在转化中打磨圆滑
- **边界比描述更重要**：voice_boundaries 比 voice_traits 更能防止 AI 套路
- **写给"演员"看，不是写给"分析师"看**：角色 Skill 的读者是角色 Agent，需要的是身份/欲望/说话方式/边界，不是叙事功能分析
- **保留来源注解**：skill-template.md 中的 `<!-- 来源：phase2_X → 字段 -->` HTML 注释必须原样保留在最终产出 SKILL.md 中，不得删除或转换为其他形式——这是下游 evidence-map / reviewer 追溯每节内容到 Phase 2 依据的唯一锚点

#### 2b. 生成 state.md（初始主观状态）

state.md 是角色的"记忆和感受"，在创作过程中由角色 Agent 通过 state_delta 更新（orchestrator 统一落盘）。

初始化内容：
- **当前情绪**：故事开始时的主观状态（从 character_arc.start_state 推导；语义按 `character_arc.mode` 解释——`transformative`/`degenerative` 下是"变化前的初始情绪"；`revelatory` 下是"稳定核的开场情绪色，不是变化前的基线"；`static` 下是"稳定核本身的情绪色，start 与 end 同值"。**不要**把 static/revelatory 角色的当前情绪解读为"缓慢转变的起点"）
- **已知信息**：故事开始时角色知道什么（从 backstory + world 推导）
- **关系感知**：对其他角色的初始看法（从 relationships 推导）
- **经历摘要**：空（故事尚未开始）
- **内心冲突**：初始的内在矛盾（从 desire_system 的自觉/不自觉欲望矛盾推导）

#### 2c. 生成 references/backstory.md（可选）

如果 Phase 2 的 backstory 数组包含 3 个以上事件，将其整理为独立的幕后故事参考文件。角色 Agent 在需要回忆过去时可按需读取。

#### 2d. 生成 build-meta.yaml（构建元数据 + provenance）

build-meta.yaml 是该角色 Skill 包的 provenance 证据——下游 verify_phase2_assets 凭此校验"产物来自本 builder"。

```yaml
generated_by: character-persona                          # 固定字符串，标记本 builder 产出
character_slug: {role-slug}                              # = skill 目录名 = SKILL.md frontmatter name
character_display_name: {中文角色名}
input_sources:                                           # 实际读取的输入文件列表（用于追溯）
  - pipeline/phase2_character.yaml
  # - pipeline/phase0_conception.yaml   （按需）
  # - pipeline/phase1_world.yaml        （按需）
adapter_path: pipeline/characters/{中文角色名}.md          # adapter 文件路径
adapter_sha256: {adapter 文件实际内容 sha256 前 16 位}      # 防 adapter 手改的物理校验
```

**字段语义关键点**：

- `generated_by: character-persona` 是 verify 区分"本 builder 产出"vs"其他来源"的唯一标识，**禁止删除或改写**。
- `adapter_sha256` 锁住 adapter 文件不被手改。

#### 2e. 章节不变量（结构白名单运行时派生）

> **章节白名单的权威来源是 [`references/skill-template.md`](references/skill-template.md)，不在本 SKILL.md 或 verify 脚本中硬编码章节名**——避免与模板漂移、避免误杀历史合法章节。

具体规则：

- `references/skill-template.md` 中嵌入的角色 SKILL.md 模板里，每个顶级 `## 章节` 紧跟一行 HTML 注释：
  - `<!-- required -->` → 必备章节（生成的角色 SKILL.md 缺此章节即 fail）
  - `<!-- optional -->` → 允许追加的章节（特殊角色可酌情裁剪）
- 生成本角色 SKILL.md 时，顶级 `##` 章节集合必须满足：
  - 必备章节集 ⊆ 实际章节集
  - 实际章节集 ⊆ (必备 ∪ 可选)
- verify_phase2_assets 在校验时**运行时解析**这两个 HTML 注释组装白名单——本 SKILL.md / verify 脚本不允许出现章节名硬编码列表。
- 修改 skill-template.md 必备/可选标注前，先 audit 旧高质量样本下的角色 SKILL.md 章节集；旧样本因模板升级而 fail 是合法的（应迁移），但不允许因白名单"漏列了模板里就有的章节"而误杀。

#### 2f. 描述性质量信号（reviewer HOW 判据，不计数）

> 不在本 SKILL.md 或下游 reviewer 中规定「`<!-- 来源：` 出现 ≥N 次」「确定性标记 ≥N 次」等人肉计数门槛——这种门槛会诱导 builder 凑数。

落盘的角色 SKILL.md 需满足以下**描述性信号**（reviewer 据此做 HOW 判定，无固定数量阈值）：

1. **声音段必须解释 HOW**：「声音框架」段说明角色如何说话——节奏 / 句法 / 用词 / 在被挑战时的确定性表现（断言？反问？迟疑？沉默？转移话题？）——而不是堆 trait 标签（"冷静 / 强硬 / 温柔"等）。
2. **边界段必须给 reason 或反例**：「边界（Layer 0 硬规则）」每一条要么说明"为什么这条边界存在"（角色心理 / 经验 / 价值锚），要么给出具体反例（"在伤心时不会用俏皮话掩饰，ta 就是直接沉默"），而不是单一禁令清单。
3. **来源注解覆盖关键断言**：`<!-- 来源：phase2_X → 字段 -->` HTML 注释应覆盖每一节的核心断言，让 reviewer 能反查 Phase 2 依据；**不规定具体数量**——一条覆盖一节的核心断言、还是按子项分散覆盖，由 builder 按节内容密度判断。
4. **预测性可执行**：读完角色 SKILL 后，应能预测：这个人在压力下会怎样沉默、怎样行动、怎样处理物件，而不只是会说哪类句子。

reviewer 校验落点：读完该节是否能预测出角色一句具体台词或一类具体反应？能 = 通过；只看到形容词标签 = fail。

### Step 3：生成兼容 adapter

为每个角色在 `pipeline/characters/{中文角色名}.md` 生成旧格式 adapter 文件。

**adapter 是从 SKILL.md 单向生成的只读文件**，格式沿用现有消费方期望的结构：

```markdown
# {角色名}

## 身份与处境
{从 SKILL.md 的"身份与处境"章节提取}

## 欲望
{从 SKILL.md 的"核心欲望"章节提取}

## 声音
{从 SKILL.md 的"声音框架"章节提取}

## 边界
{从 SKILL.md 的"边界"章节提取}

## 弧光
{从 SKILL.md 的"**人物轨迹**"章节提取——包含 `mode / start_state / end_state / 轨迹机制` 四字段。adapter 标题保留 `## 弧光` 作为 compatibility alias（下游 Phase 6 / design-validation / 审稿 B 组消费方按此标题定位内容），但内容语义由 SKILL 模板"人物轨迹"段提供的 mode-aware 字段决定——static/revelatory 角色填入的内容不是"变化轨迹"}
```

### Step 4：生成 build-report.md（应构建集声明 + 决策记录）

在 `pipeline/story-character-skills/build-report.md` 生成 `build-report.md`，记录本次应构建集判定与每个角色的决策。本文件同时承担 **name → slug 映射桥梁**——下游 verify_phase2_assets 凭它把 phase2_character.yaml 中的 `name`（真实 schema 主键）反查到 builder 产出的 `slug`，**不要求** phase2_character.yaml 自带 slug 字段。

#### 应构建集声明（两阶段）

> **真实 phase2_character.yaml schema**：`protagonist.name` / `deuteragonist.name` / `antagonist.name` / `supporting_cast[].name` —— 全部以 `name` 为主键，没有 `slug` 字段。本 builder 在 build-report 中显式建立 name → slug 映射。

| 阶段 | 必建 | 推迟（Phase 5 补建） |
|---|---|---|
| **Phase 2** | `protagonist.name` + `deuteragonist.name`（若该键存在）+ `antagonist.name` + 满足上文判据的 `supporting_cast[].name`（独立对白场景 / 关键互动 / 声音区分） | `supporting_cast[].name` 中"背景人物 / 转述人物 / 群体敌人"等不满足判据的 |
| **Phase 5+** | `phase5_scenes.yaml.participants` 中"直接登场且有对白或关键行动"但 Phase 2 未建的 name | — |

Phase 2 阶段调用本 skill 时，**phase2 列出的每个 name 必须在 build-report 已构建表或未构建表里出现一次**——任一 name 缺判定 = builder 漏过判断 = phase2 hard gate fail。

#### build-report.md 模板

```markdown
# Build Report — {story_slug}

构建时间：{ISO 时间}
来源：pipeline/phase2_character.yaml
本次阶段：{phase2 | phase5_supplement}

## 已构建

| name | slug | 类型 | 深度 | 4 产物落盘 |
|------|------|------|------|------------|
| {phase2 中的 name} | {role-slug} | protagonist | 完整 | ✅ |
| ... | ... | ... | ... | ... |

## 未构建

| name | 类型 | skip_reason |
|------|------|-------------|
| {phase2 中的 name} | supporting_cast | {为什么本阶段不需要独立 Skill；引用本 SKILL.md §"是否构建独立 Skill 的判据" 段判据} |

## 补充输入

{是否读取了 phase0/phase1，读取了哪些字段，为什么}
```

**字段约束**：

- 已构建表的 `name` 必须在 phase2_character.yaml 中存在（不允许幻觉构建未授权角色）
- 未构建表每行必须填 `skip_reason`（缺失 = phase2 hard gate fail）
- `4 产物落盘` 列指向下文 §Step 4.1，4 件产物全齐才标 ✅

#### Step 4.1：4 产物清单（builder 自检参考）

每个落入"已构建"表的角色，必须产出以下 4 个文件——builder 自查路径：

| # | 产物 | 路径 | 生产步骤 |
|---|------|------|----------|
| 1 | 角色 SKILL.md | `pipeline/story-character-skills/.claude/skills/{slug}/SKILL.md` | Step 2a |
| 2 | state.md | `pipeline/story-character-skills/.claude/skills/{slug}/state.md` | Step 2b |
| 3 | build-meta.yaml | `pipeline/story-character-skills/.claude/skills/{slug}/build-meta.yaml` | Step 2d |
| 4 | adapter | `pipeline/characters/{display_name}.md` | Step 3 |

**Phase 2 hard gate**：4 产物 + 应构建集声明完整后，由 `verify_phase2_assets.py` 校验。
**详细字段断言与错误码以脚本为权威**：[`MUSE-writing/scripts/verify_phase2_assets.py`](../../scripts/verify_phase2_assets.py)。
本 SKILL.md 不复述校验维度；脚本调用与退出码处理见 [`phase2-character/SKILL.md §7`](../phase2-character/SKILL.md)。

### Step 5：验证

**接口约束自检**：对照本文件顶部"接口约束"6 条逐一核验，外加 frontmatter 完整性（包含 name、description、version、allowed-tools）。必须全部通过，否则构建失败。

**builder 写作动作自检**（脚本兜底之前 builder 自身要做的事）：
- `<!-- 来源：phase2_X → 字段 -->` 注解是否覆盖每节核心断言（脚本不校验注解内容，靠 builder 自觉）
- 角色 SKILL.md 章节是否按 §Step 2e 不变量从 skill-template.md HTML 注释派生（不照抄硬编码章节名）
- build-report.md 中 phase2 列出的每个 name 都已落入"已构建"或"未构建"任一表（漏判 = builder bug）

字段断言、4 产物完整性、sha 一致性等结构校验以 `verify_phase2_assets.py` 为权威，本 SKILL.md 不复述。

**创作质量自检（描述性 HOW 信号，reviewer 判定，不计数）**：
- SKILL.md 的章节是否充分覆盖角色关键特征？特殊角色（神秘人物 / 只出现在他人叙述中的角色）可在可选章节范围内裁剪
- 「声音框架」是否解释了 HOW（节奏 / 句法 / 用词 / 在被挑战时的确定性表现），而不是堆 trait 标签？
- 「边界」每一条是否给出 reason 或具体反例，而不是单一禁令清单？
- `<!-- 来源：phase2_X → 字段 -->` 注解是否覆盖每节的核心断言？（不规定具体数量；按节内容密度判断）
- 多角色场景中各角色的声音框架是否有可辨识差异（参照 contrast_axes 做判断）
- state.md 初始状态是否与故事起点一致

### Step 6：汇报

向 orchestrator 汇报构建结果：

```
✅ 角色 Skill 包构建完成

已构建：
- {角色名} → pipeline/story-character-skills/.claude/skills/{role-slug}/
  adapter → pipeline/characters/{角色名}.md
- ...

决策详情见 pipeline/story-character-skills/build-report.md

提醒：确保当前运行时已挂载或可发现 `pipeline/story-character-skills`；若运行时需要显式加入项目目录，按其目录挂载机制加入该路径。
```

---

## 输出目录结构

```
pipeline/
├── story-character-skills/
│   ├── .claude/skills/               ← 当前兼容挂载点
│   │   ├── {role-a}/                 # 直接以 role-slug 命名（如 li-an）
│   │   │   ├── SKILL.md              # 静态人格定义
│   │   │   ├── state.md              # 初始主观状态
│   │   │   ├── references/
│   │   │   │   └── backstory.md      # 幕后故事（可选）
│   │   │   └── build-meta.yaml       # 构建元数据
│   │   └── {role-b}/
│   │       └── ...
│   └── build-report.md               ← 构建决策记录
│
└── characters/                       ← 兼容 adapter
    ├── {角色名A}.md
    └── {角色名B}.md
```

---

## 职责边界

本 Skill **只负责**：
- 把结构化人物设计转成角色 Skill 包
- 初始化 state.md
- 生成兼容 adapter
- 生成 build-meta.yaml

本 Skill **不负责**：
- 触发运行时情境排练（那是 character-rehearsal 的职责）
- 决定 scene-local objective（那是运行时推导的）
- 执行角色扮演（那是角色 Agent 加载 Skill 后的事）
- 修改 Phase 2 的设计（如果设计有问题，回 Phase 2 修改）

---

## rebuild 命令

当 Phase 2 数据更新（如设计修订后调整了 voice_traits）或需要重新生成某个角色的 Skill 时：

```
/character-persona rebuild li-an
```

这会：
1. 重新读取 phase2_character.yaml 中对应角色的数据
2. 重新生成 SKILL.md 和 adapter
3. 更新 build-meta.yaml 时间戳
4. 维护 SKILL.md frontmatter 的 version

state.md **不会被覆盖**（它包含运行时状态）。

也可用于 Phase 5 后为新确认的重要配角补充构建：
```
/character-persona build
```
此时会重新扫描 phase2_character.yaml，为尚未构建 Skill 的配角生成新的 Skill 包。
