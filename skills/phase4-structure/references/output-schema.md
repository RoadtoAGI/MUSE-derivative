# Phase 4 输出 Schema

交付物文件：`pipeline/phase4_structure.yaml`

```yaml
arc_expansions:
  - arc_id: ARC-1
    sequences:
      - seq_id: ARC1-SEQ1
        name: "序列名称"
        core_conflict: "这个序列的核心冲突（**也是序列尺度的读者追问**——读者跟住这个冲突读完整段）"
        escalation_direction: "冲突从哪递进到哪（**= 读者在本序列被带向什么方向**）"
        sequence_climax: "序列高潮（哪个事件是顶点）"
        closed: "这个序列闭合了什么（**= 读者本段获得什么答案**）"
        opened: "这个序列打开了什么新问题（**= 读者被带入下一段跟住什么新问题**）"
    arc_progression_note: "此 Arc 内序列之间的递进逻辑（可选）"

causal_chain: "ARC1-SEQ1 →（因为…）ARC1-SEQ2 →（因此…）ARC2-SEQ1 → ..."
```

## 字段说明

| 字段 | 必需 | 下游使用 |
|------|------|---------|
| `arc_expansions[].arc_id` | 是 | Phase 5（按 Arc 组织场景） |
| `arc_expansions[].sequences[].seq_id` | 是 | Phase 5（按序列展开场景） |
| `arc_expansions[].sequences[].core_conflict` | 是 | Phase 5（序列内场景的冲突围绕此展开） |
| `arc_expansions[].sequences[].sequence_climax` | 是 | Phase 5（标识序列高潮场景，触发 beat_direction 标注） |
| `arc_expansions[].sequences[].closed/opened` | 是 | Phase 5（验证序列间衔接） |
| `causal_chain` | 是 | Phase 5（验证场景间因果）、Phase 7（因果链修订） |
