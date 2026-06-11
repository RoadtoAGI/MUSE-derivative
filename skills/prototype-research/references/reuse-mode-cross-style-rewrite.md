# reuse_mode=cross_style_rewrite 执行细则

> 适用：调用方注入 `reuse_mode=cross_style_rewrite` 时。其他模式不读本文件。产物矩阵 SSOT 仍在 [prototype-card-schema.md](prototype-card-schema.md)。

# reuse_mode=cross_style_rewrite

产 card + reuse_profile + seeds/phase0-5 + text/scene_map（推荐加 text/continuity_anchors 沿用专名）。

`reuse_profile.yaml.phase_execution_plan`：
- phase0-5: `locked`（不重新生成 `pipeline/phase{N}_*.yaml`；下游直接读 seed）
- phase6: `rewrite_only`
- phase7: 风格一致性 + 信息保真审查

canon 路径反推 text/scene_map：
- 每个场景的 `scene_function` + `canon_facts` ← scene-reference 输出
- `rewrite_policy.style_target` ← 用户 query（如"轻喜剧"、"赛博朋克"、"鲁迅式"）
