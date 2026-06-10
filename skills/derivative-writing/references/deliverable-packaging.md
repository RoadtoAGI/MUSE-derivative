# 早停交付物包装口径（衍生）

衍生早停档（`deliverable_type` ∈ character_profile / plot_framework / outline）跑到终点 phase 后**必须**把 phase yaml 包装为 `story.md`（人类可读交付物）。口径自含——不跨包 link MUSE-writing 入口 skill。

通则：**YAML 是结构 SSOT；story.md 是人类阅读 SSOT**，是设计文档不是小说正文。衍生档在文档顶部注明继承基线（`继承自《X》` + reuse_mode），正文主体写新设计/续写部分。

## character_profile（终点 phase 2）

phase 0/1/2 完成后包装为**衍生角色设计文档**：
- 主体来自 `phase2_character.yaml`；按需引用 phase0（核心命题）+ phase1（世界）作背景
- 结构：继承声明 → 核心命题 → 一句话画像 → 设计立意 → 欲望系统 / 弧光 / 声音 / 关系 → 关键场景预设（如有）
- spin_off 显式写**升格主角 ← 原配角**、**原主角降格**、二者关系动态
- 600-1500 字

## plot_framework（终点 phase 4）

phase 0-4 完成后包装为**衍生情节框架文档**：
- 主体来自 `phase3_spine.yaml` + `phase4_structure.yaml`；引用 phase0（核心命题）+ phase2（人物）作背景
- 结构：继承声明 → 核心命题 → 戏剧问题 → 激励事件 → 三幕（各幕冲突+转折）→ 危机 → 高潮 → 结局
- sequel 的 spine 含继承+续写段时，明确区分"原作已发生（不重写）"与"续写新增"
- 800-2000 字

## outline（终点 phase 5）

phase 0-5 完成后包装为**衍生大纲文档**：
- 主体来自 `phase5_scenes.yaml`；引用 phase0（核心命题）+ phase3（脊椎）+ phase4（三幕）作骨架
- 结构：继承声明 → 主要人物简介 → 三幕骨架 → 章节大纲（每章冲突/事件/出场人物）
- sequel 只展开续写新增章节，原作章节一行标"原作章节（接续点之前）"
- 1500-3000 字

## full_prose / prose_rewrite（终点 phase 7）

不走本早停包装——由 phase7 整合落 story.md。scene 拼接遍历 `pipeline/scenes/scene_*.md`（sequel 即续写段，cross_style 即改写版）。

## 不做

- 不跨 plugin 调 MUSE-writing 的 character-design/plot-design/novel-outline 入口 skill（口径自含本文件）
- 早停档不写超出该档粒度的内容（character_profile 不写情节、plot_framework 不写章节大纲、outline 不写 prose）
