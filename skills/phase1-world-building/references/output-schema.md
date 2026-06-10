# Phase 1 输出 Schema

交付物文件：`pipeline/phase1_world.yaml`

```yaml
setting:
  era: 时代描述（具体年代或架空设定）
  duration: 故事时间跨度
  location: 空间范围描述
  conflict_levels:
    - 按故事需要列出该世界中存在的冲突维度
genre_conventions:
  primary_genre: 主导类型
  secondary_genre: 次要类型（可选）
  conventions:
    - convention: 惯例描述
      planned_subversion: 计划的颠覆（可选）
generative_driver:
  # 本题材的冲突生成机制——回答"为什么会这样 / 如何扩散 / 在故事局部场景的具体表现"
  # 子字段命名按题材自然组织，不强制；至少覆盖原因 + 扩散或运作方式 + 局部表现
  # 末世示例（仅供参考，不是强制 schema）：
  #   driver_type: "陨石孢子感染型末世"
  #   primary_cause: 灾变成因的一句话描述
  #   propagation: 扩散/升级机制
  #   local_manifestations:
  #     - 在故事主要场景中的具体表现（道具、风险、可信任 vs 不可信任的细节）
  # 悬疑示例：
  #   driver_type: "封闭别墅密室作案"
  #   hidden_event: 隐藏的核心事件
  #   leak_channels: 线索泄漏路径
  # 见 SKILL.md §3 题材→生成机制对照表
world_rules:
  physical:
    - 物理规则
  social:
    - 社会规则
  psychological:
    - 心理规则
daily_life:
  - dimension: 维度名称（如 livelihood / rituals / values / power_dynamics，也可以是其他维度）
    findings:
      - detail: 具体发现
        story_implication: 对故事创作的启示
domain_knowledge:
  - topic: 领域主题（如"行草书法技法"、"军事调度理论"）
    details:
      - 用户提供的专业知识要点
    source: user_provided
creative_constraints:
  - constraint: 限制描述
    narrative_function: 叙事功能
```

## 字段说明

| 字段 | 必需 | 下游使用 |
|------|------|---------|
| `setting` | 是 | Phase 2（人物背景受设定约束）、Phase 5（场景地点来自设定） |
| `genre_conventions` | 是 | Phase 4（结构遵循类型常规）、Phase 5（事件编排考虑惯例） |
| `generative_driver` | 是 | Phase 2（人物背景受 driver 约束——例如末世孢子感染下角色的免疫史）、Phase 5（场景威胁与可用资源来自 driver）、Phase 6（叙事细节锚定 driver，禁止临场发明与之矛盾的世界事实） |
| `world_rules` | 是 | Phase 2（世界规则约束人物可能性）、Phase 6（叙事必须遵守世界规则）。每条规则应能追溯到 `generative_driver`；灾后状态描述（基础设施 / 信息 / 秩序 / 物资）写在 `social` 或 `physical` 层，不与 driver 并列 |
| `daily_life` | 按需（世界远离当代日常时必需）。数组结构，维度不固定——livelihood/rituals/values/power_dynamics 是常见维度，但可根据世界特点增减 | Phase 2（人物日常和幕后故事的素材）、Phase 6（叙事细节的来源） |
| `domain_knowledge` | 条件（Phase 0 有 `reference_materials` 时生成） | Phase 6（创作时融入专业细节）。与 `daily_life` 互补：`daily_life` 来自 agent 调研，`domain_knowledge` 来自用户提供的素材 |
| `creative_constraints` | 否 | Phase 4-6（限制产生冲突来源） |

## Sidecar Artifact

当执行了世界调研（步骤 5），完整调研报告存为 `pipeline/world_research.md`。`daily_life` 字段是调研的精华摘要，sidecar 保留完整上下文供后续阶段按需查阅。
