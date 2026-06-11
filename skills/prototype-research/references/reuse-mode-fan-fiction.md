# reuse_mode=fan_fiction 执行细则

> 适用：调用方注入 `reuse_mode=fan_fiction` 时。其他模式不读本文件。产物矩阵 SSOT 仍在 [prototype-card-schema.md](prototype-card-schema.md)。

# reuse_mode=fan_fiction

产 card + reuse_profile + seeds/phase0_1_2 + text/continuity_anchors（推荐加 text/style_fewshot_notes）。

`reuse_profile.yaml.phase_execution_plan`：
- phase0/1/2: `instantiate`
- phase3/4/5: `rebuild`
- phase6: `write_full`
- phase7: 常规

canon 路径反推 seeds：
- phase0 seed ← novel-analysis 输出的 `controlling_idea` + `genre` + `premise`
- phase1 seed ← novel-analysis 输出的 `world_rules` + design-doc-reference 的世界设定档案
- phase2 seed ← character-kb-distill 输出的角色档案（按用户 query 涉及的角色组合）

web 路径反推 seeds：通常仅能产 phase0 + phase1 部分；phase2 角色档案需手工 paraphrase。降级标 `seed_quality: partial`。
