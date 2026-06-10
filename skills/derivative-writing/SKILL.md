---
name: derivative-writing
description: 基于已有作品的小说写作 orchestrator（产物 markdown story.md）。覆盖同人 / 续写 / 番外 / 跨文风改编四档复用深度 × 5 档交付物（角色档案 / 情节框架 / 大纲 / 小说正文 / 跨风格 prose 重写）。**只要 query 涉及"续《X》/《X》同人/《X》外传/把《X》改成 Y 风/接《X》第 N 章往下写"等基于已有作品的创作，必触发本 skill**。优先级：让位给 screenplay-writing（剧本同人 / 跨媒介改编到剧本）；优于 novel-outline / plot-design / character-design / story-writing（无原作约束的原创路径）。执行模型：与 MUSE-writing 主干**几乎一致**——只在跑 pipeline 前用 init_derivative_run.py 把可继承的 phase 设计 yaml 从 canon 蒸馏物 / 用户已有 pipeline **预置**到 work_dir，phase1-5 检测到已有 yaml 就在其上完善（否则从零生成），下游消费与 MUSE-writing 一致。
---

# derivative-writing — 同人 / 续写 / 番外 / 改编小说 orchestrator（MUSE-derivative）

## §0 何时用 / 让位与优先

覆盖**所有"基于已有作品的小说创作"**——续写 / 同人 / 番外 / 跨文风改编，含衍生大纲 / 衍生情节框架 / 衍生角色档案 / 衍生正文 / 跨风格 prose 重写。

- **让位给** `screenplay-writing`（跨媒介改编到剧本——剧本产物优先于改编属性）
- **优于** `novel-outline` / `plot-design` / `character-design` / `story-writing`（无原作约束的原创路径）

**何时不走本 skill**：原作只是**参考**而非**继承基线**——"参考《X》风格写新故事 / 类似《X》的感觉 / 灵感来自《X》"。强衍生信号是"续/同人/改写/接着写"，弱原型信号是"参考/类似/灵感"。

**核心理念**：derivative ≈ MUSE-writing。唯一区别是**提前准备一部分 phase 设计 yaml**——把原作可继承的设计（世界 / 角色 / 脊椎等）预置成 work_dir 内的 `pipeline/phaseN_*.yaml`，phase1-5 检测到就在其上**完善**而非从零生成。下游（phase6 写正文 / phase7 整合）消费 yaml 的逻辑与 MUSE-writing 完全一致。

**渐进披露**：进入对应阶段才通过 `Skill` 工具触发下游 phase skill。

## §1 第一步：必调 init_derivative_run.py（预置 + skeleton，权威路径）

触发本 skill 后**第一动作**——脚本同时建 work_dir 骨架 + 复制 canon 物料 + **按 reuse_mode 预置 phase 设计 yaml**：

```bash
# canon_distill source（从 muse-canon-distill 取蒸馏物）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_derivative_run.py \
  --novel "<原作名>" --query "<需求一句话>" --reuse-mode <fan_fiction|sequel|spin_off|cross_style_rewrite>

# existing_pipeline source（用户已有部分 phaseN 文档）
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_derivative_run.py \
  --existing-pipeline "<已有 pipeline 目录绝对路径>" --query "<需求>" --reuse-mode <...>
# stdout 末行 = work_dir 绝对路径
```

`--reuse-mode` 决定预置哪些 phase yaml（脚本 `REUSE_SEED_PHASES`）：fan_fiction/spin_off 预置 phase1-2；sequel 预置 phase1-5；cross_style_rewrite 预置 phase0-5。canon 缺某 phase 蒸馏则该 phase 不预置 → 从零生成。**禁止**手动 cp / mkdir。

## §2 判档：reuse_mode × deliverable_type

| reuse_mode | 触发信号 | 复用本质 |
|---|---|---|
| `fan_fiction` | "《X》同人 / 某 CP 同人" | 继承世界+角色，**写新事件**（phase3-5 rebuild）|
| `sequel` | "续《X》/ 接 N 章往下写" | 接原时间线，phase3-5 在继承设计上**追加** |
| `spin_off` | "《X》外传 / 配角 X 的故事" | 继承世界，phase2 把配角**升格**为主角，phase3-5 rebuild |
| `cross_style_rewrite` | "把《X》改成 Y 风" | 保留原 phase0-5，仅 phase6 换风格**重写** |

| deliverable_type | 信号 | 终点 phase |
|---|---|---|
| `character_profile` | 角色档案 / 角色卡 | phase 2 |
| `plot_framework` | 情节框架 / 三幕结构 | phase 4 |
| `outline` | 大纲 / 章节 outline | phase 5 |
| `full_prose`（默认）| 写《X》同人 / 续《X》 | phase 7 |
| `prose_rewrite`（仅 cross_style）| 把《X》改成 Y 风 | phase 7 |

拿不准：reuse_mode 倾向 `sequel`，deliverable_type 倾向 `full_prose`。`cross_style_rewrite` 只支持 full_prose / prose_rewrite。

## §3 执行 phase0→7（到 deliverable 终点截断）

`Skill phase0-conception` → … → 截断 phase。**phase1-5 自带 honor 逻辑**：检测到 work_dir 已有 `pipeline/phaseN_*.yaml`（§1 预置）就在其上完善，否则从零生成——orchestrator 不需注入任何 mode 参数。各 reuse_mode 的 phase 行为（由"预置了哪些 yaml"自然分流）：

| phase | fan_fiction | sequel | spin_off | cross_style_rewrite |
|---|---|---|---|---|
| 0 conception | 调（新构想）| 调（续写构想）| 调（外传构想）| **不调**（用预置 locked）|
| 1 world | 调 honor（完善继承）| 调 honor | 调 honor | **不调**（用预置 locked）|
| 2 character | 调 honor（继承角色）| 调 honor | 调 honor（升格配角=完善）| **不调**（用预置 locked）|
| 3 spine | 调（无预置→rebuild）| 调 honor（末端追加）| 调（rebuild）| **不调** |
| 4 structure | 调（rebuild）| 调 honor（追加序列）| 调（rebuild）| **不调** |
| 5 scene-arrange | 调（rebuild）| 调 honor（追加 continuation_scenes，`scenes:`=待写）| 调（rebuild）| **不调** |
| 6 scene-dev | 调（正常写）| 调（写 phase5 `scenes:` 列出的续写场景）| 调（正常写）| 调（按 style_target 改写 canon 场景）|
| 7 integration | 调（正常整合）| 调（整合 + 接缝连续性核对）| 调（正常整合）| 调（整合 + 风格保真核对）|

**"不调"= cross_style 的 phase0-5 已预置 locked，直接用预置 yaml，不触发该 phase skill**（避免无 honor 逻辑的 phase0 重生成覆盖）。

**phase6 续写/改写 dispatch 细节**：
- sequel：phase5 honor 已把 `scenes:` 收为续写新增场景（inherited 原作场景不在 `scenes:`，不重写）；phase6 正常写 `scenes:` = 只写续写段。首条续写场景须接 canon 末场状态（phase5 honor 已锚定）。
- cross_style：phase6 dispatch prompt 加"按 `style_target` 重写 canon scene `{id}`，保留 scene_function + canon_facts 全部元素，只改文风/措辞/节奏"；writer 读 `canon/<slug>/scenes/scene_{id}.md` 作改写蓝本。

## §4 早停包装 + 长篇约束

deliverable 早停档（character_profile / plot_framework / outline）跑到终点 phase 后按 [`references/deliverable-packaging.md`](references/deliverable-packaging.md) 包装 `story.md`；full_prose / prose_rewrite 走 phase7。

**长篇正文约束**：`canon/<slug>/LONG_NOVEL_NOTICE.md` 存在时禁 Read 任何 `full_text.*`；所有原作信息从蒸馏物提取。**任何情形不复制原作 prose ≥ 20 字连续段落**（≤ 15 字 signature_phrase 允许）。

## §5 输出

| 文件 | 何时产 |
|---|---|
| `pipeline/references/canon/<slug>/` | 必产（init 脚本复制）|
| `pipeline/phaseN_*.yaml`（N≤终点）| 预置的继承 + 各 phase 完善/生成产物（标 `source: derived_from=...`）|
| `pipeline/scenes/scene_{id}.md` | full_prose / prose_rewrite phase6 产 |
| `story.md` | **所有 deliverable 必产**（早停档按 §4 包装；full_prose/prose_rewrite 走 phase7）|

## §6 不做

- 不向 phase skill 注入 mode 参数——衍生行为由"预置了哪些 yaml" + phase1-5 honor 逻辑自然分流
- 不 fork 改写 phase 内容决策——只调脚本 + 触发 phase skill + 早停包装
- 不写剧本格式——剧本同人改走 `screenplay-writing`
- 不手动 cp canon 物料 / 不手动预置——init_derivative_run.py 唯一权威
- 不 Read 长篇正文 / 不复制原作 prose ≥ 20 字连续段落
