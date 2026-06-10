# MUSE-derivative — 衍生写作姊妹包

同人 / 续写 / 番外 / 跨风格改编的独立 plugin。与 MUSE-writing 主干**几乎一致**，唯一区别是跑 pipeline 前**预置可继承的 phase 设计 yaml**，phase1-5 在其上完善。

## 定位

| 包 | 职责 |
|---|---|
| **muse-writing** | 纯从零原创 pipeline（phase0→7）+ 原创写作入口 |
| **muse-canon-distill** | 名著语料 + 蒸馏（继承基线供应） |
| **muse-derivative（本包）** | 同人/续写/番外/跨风格改编；自含整条 pipeline（phase0-7 + 辅助 skill），phase1-5 honor 预置 yaml |

本包**完全独立分发**（自带 `.claude-plugin/` + 整条 pipeline skill）。与 muse-writing 同名的 phase/辅助 skill 是 derivative 版本（phase1-5 含 honor 逻辑），由 plugin 命名空间区分。

## 执行模型：derivative ≈ MUSE-writing + 预置 + honor

入口 `derivative-writing` 的唯一区别：

1. **预置**：第一步 `init_derivative_run.py --reuse-mode <...>` 把原作可继承的 phaseN 设计 yaml 从 canon 蒸馏物 / 用户已有 pipeline 复制到 work_dir `pipeline/`：
   - `fan_fiction` / `spin_off` → 预置 phase1-2（世界 + 角色）
   - `sequel` → 预置 phase1-5（全设计层作续写基线）
   - `cross_style_rewrite` → 预置 phase0-5（全锁定，仅 phase6 改风格）
2. **honor**：phase1-5 检测到 work_dir 已有 `pipeline/phaseN_*.yaml` 就**在其上完善**（保留继承字段 + 按衍生需求深化）；没有则从零生成（同 MUSE-writing）。
3. **下游一致**：phase6 写正文 / phase7 整合的消费逻辑与 MUSE-writing 完全一致。reuse_mode 差异完全由"预置了哪些 yaml"自然分流，**phase 不需 mode 参数**。

## skills

- `derivative-writing` — 唯一用户入口（判档 → init+预置 → 跑 phase0-7 honor → deliverable 早停）
- `phase0-conception` … `phase7-integration` — 衍生 pipeline（phase1-5 含"honor 已有 yaml"前置段，其余与 MUSE-writing 一致）
- `writer` / `prose-craft` / `dialogue-craft` / `reader-review` / `scene-review` / `story-review` / `revision` / `character-rehearsal` / `character-persona` / `role-brief-deriver` / `design-validation` / `prototype-research` — pipeline 辅助 skill（与 MUSE-writing 一致）

## scripts

- `init_derivative_run.py` — 自含 work_dir 初始化 + canon 物料复制 + `--reuse-mode` 预置 phase yaml；不依赖 muse-writing 脚本

## 依赖

- **可选**：muse-canon-distill（`canon_distill` source 取蒸馏物；无蒸馏物时走 `--existing-pipeline` 挂载用户已有 phase 文档）

## 设计源

主仓 design SSOT：续写/衍生写作技能包抽取设计（Level 2 methods/pipeline）。**注**：该 design 早期版本（§A 决策档案）描述的是"执行计划 + 显式 action"模型；现行实现按用户决定改为更简的"fork + 预置 + phase1-5 honor yaml"模型（design 待回写对齐）。
