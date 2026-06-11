# reuse_mode=spin_off 执行细则

> 适用：调用方注入 `reuse_mode=spin_off` 时。其他模式不读本文件。产物矩阵 SSOT 仍在 [prototype-card-schema.md](prototype-card-schema.md)。

# reuse_mode=spin_off

产 card + reuse_profile + seeds/phase0_1 + seeds/phase2（标 partial，含 `role_promotion` 段）+ text/continuity_anchors。

`reuse_profile.yaml.phase_execution_plan`：
- phase0/1: `instantiate`
- phase2: `role_promotion`（详 phase2-character SKILL.md 内 role_promotion mode 段）
- phase3/4/5: `rebuild`
- phase6: `write_full`
- phase7: `continuity_review`（轻量，只检查不破坏 canon）

canon 路径反推 phase2 seed：
- `canonical_protagonist` ← character-kb-distill 原主角档案 + `role_in_spin_off` 字段（background / supporting / cameo 由用户 query 决定）
- `role_promotion` ← character-kb-distill 升格的原配角档案 + 用户 query 暗示的 expanded conflicts
