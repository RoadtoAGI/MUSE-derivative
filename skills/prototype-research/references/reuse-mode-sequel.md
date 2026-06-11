# reuse_mode=sequel 执行细则

> 适用：调用方注入 `reuse_mode=sequel` 时。其他模式不读本文件。产物矩阵 SSOT 仍在 [prototype-card-schema.md](prototype-card-schema.md)。

# reuse_mode=sequel

产 card + reuse_profile + seeds/phase0-5 + text/continuity_anchors + text/tail_window_summary。

`reuse_profile.yaml.phase_execution_plan`：
- phase0/1/2: `instantiate`
- phase3/4/5: `append_edit`（含 `continuation_point` + `unresolved_threads` + `append_constraints`）
- phase6: `new_scenes_only`
- phase7: `continuity_review`

canon 路径反推 phase3-5 seeds：
- phase3 seed `inherited_spine` ← novel-analysis 输出的 spine 段
- phase3 seed `continuation_point` ← 用户 query（如"续第 N 章"或"接结尾"）
- phase3 seed `unresolved_threads` ← scene-reference 检索原作结尾 N 章 + character-kb-distill 角色未达成欲望
- phase4 seed `inherited_structure` + `append_target` ← novel-analysis 结构段
- phase5 seed `inherited_scenes` + `new_scene_slots` ← scene-reference 原场景索引
- text/tail_window_summary ← scene-reference 原作结尾几场状态

web 路径下 sequel：原则上不推荐（资料粒度不足）；如必须，仅产 reference_only 降级 + 在 sources 标 `degraded_from: sequel`。
