# Phase 6 Execution Protocol

本文档承载 Phase 6 完整 pipeline 执行时的操作细节。SKILL.md 承载 orchestrator 调度职责；具体写作细节通过加载 `prose-craft` + `dialogue-craft` skill 获得；dispatcher 具体流程（scene-level 分流、role_brief runtime 派生、链路调度、writer 接线）在此展开。

**何时读此文档**：orchestrator 走完整 8 阶段 pipeline、需要 dispatch 多场景时。单场景重写、对白修订等小任务可跳过本协议，orchestrator 自己加载 prose-craft / dialogue-craft 直接写。

## 目录

- [§0 本文件范围](#0-本文件范围)
- [§1 Dispatcher 伪代码](#1-dispatcher-伪代码)
- [§1.5 Step 5 scene-review 审阅阶段](#15-step-5-scene-review-审阅阶段per-scene-loop-结束后)
- [Step 6 Post-revision review](#step-6-post-revision-review)
- [§2 role_brief 派生协议](#2-role_brief-派生协议)
- [§4 direct-writer 链路](#4-direct-writer-链路)
- [§3.5 scene-reference 调度与消费语义（扩展包行为）](#35-scene-reference-调度与消费语义仅在装有-muse-canon-distill-扩展包时生效)
- [§5 流程违规常见错误](#5-流程违规常见错误)

---

## 0. 本文件范围

本文件定义 Phase 6 的权威执行流程。

---

## 1. Dispatcher 伪代码

```python
phase6_dispatcher(scenes_in_order):
    for scene in scenes_in_order:
        # ============ Step 2.1: role_brief runtime 派生 ============
        # orchestrator 通过当前运行时的 subagent dispatch 启动 role-brief-deriver
        # 仅传 scene_id 作为动态标识；输入路径 / 输出 schema / fallback 语义
        # 全部在 ${CLAUDE_PLUGIN_ROOT}/skills/role-brief-deriver/SKILL.md 静态约定
        result = Task(
            subagent_type="role-brief-deriver",
            prompt=f"为场景 {scene.id} 派生 role_brief。按 SKILL.md 规定读输入文件、产出 "
                   f"pipeline/scene_{scene.id}/role_briefs.md（合集版）。"
                   f"完成后回复 'done role_brief for scene {scene.id}'。",
        )
        if not result.success:
            mark_scene_pending_human(
                scene.id,
                reason="role_brief derivation failed (Task-tool dispatch)",
                status="ESCALATED",
            )
            continue  # 跳过本场景

        # ============ Step 2.2: direct-writer 链路 ============
        #
        # 串行约束：dispatcher for 循环逐场景处理——draft_tail_k 产出后
        # scene_{k+1} writer 才启动。
        #
        # writer 直接读 phase0 reference_materials.{summary,key_details}
        # + phase1 domain_knowledge 全量。
        run_script("extract_scene_card.py", scene_id=scene.id, work_dir=WORKDIR)

            # ============ Step 4b: performance 素材 fan-out（writer 前）============
            # **前置依赖**：role_briefs.md（合集，全部在场角色各一段 YAML）已由 Step 2.1
            # role-brief-deriver 落盘（actor 静态清单第 3 项硬引用该文件）
            #
            # 为本场景每个在场角色 dispatch character-actor subagent 产 performance 素材
            # 产出 pipeline/staging/scene_{scene.id}/{slug}_performance.md（schema 权威源：
            # character-rehearsal skill 的 references/output-schema.md）
            #
            # 触发（条件硬依赖，机器可数）：role_briefs.md 内 `character:` 段数 ≥ 2 →
            # 必跑，per-role 并行 fan-out 全部在场角色，无裁量空间。
            # 豁免仅两类，且必须**逐场**写 audit/skip_performance.yaml 条目（无声明即漏步，
            # Step 4d 覆盖检查会阻断 writer dispatch）：
            #   ① 单角色场（判据自动成立，声明一句即可；也可不豁免、照常为该角色产素材——
            #      覆盖检查二者认其一）
            #   ② 多角色但确无对白交锋的过渡/群像场（reason 必须引本场 scene_card 的
            #      无对白/过渡/群像证据，不得泛写 run 级理由）
            #
            #   skip_performance.yaml 契约——一条记录 = 一个精确 scene_id；
            #   禁 all/通配/列表/区间（批量声明会被覆盖检查整体拒绝）：
            #     - scene_id: S03          # 精确单场
            #       reason: 单角色内心戏   # 多角色豁免须引 scene_card 证据
            #
            # 失败语义：actor 返回"排练未完成 + 缺项名" → 不中断本场其余角色的 fan-out；
            # 该角色缺 performance 文件会被 Step 4d 覆盖检查拦下，须补产该角色素材（或补本场
            # 合法 skip 条目）后才放行 writer；二次仍失败 → ESCALATED，本场不产 draft。
            # writer 的"素材缺席降级"分支只在**本场有合法 skip 条目**时到达。
            #
            # 静态 / 动态分层（§0.4 约定）：
            # - 元配置：${CLAUDE_PLUGIN_ROOT}/agents/character-actor.md
            # - 职责：${CLAUDE_PLUGIN_ROOT}/skills/character-rehearsal/references/
            #   output-schema.md（schema 权威源）+ situational-method.md（方法 + self-check）
            # - orchestrator 动态传：仅 {scene_id, role_slug} 二元组——情境由 actor 自读
            #   scene_card.md，输出路径由 skill 契约拼定，不在 prompt 里转述情境/枚举路径
            #
            # **默认 = per-participant fan-out**：orchestrator 在 scene loop 内对每个
            # 在场角色直接 dispatch character-actor，**不**在 character-actor 内部嵌套
            # spawn。per-role 注意力隔离是声音独立性的前提；一个 actor 同时演多角色等于
            # 回到"场景语言整理器"，丢失隔离。
            expected_roles = parse_role_slugs(f"pipeline/scene_{scene.id}/role_briefs.md")  # `^character:\s*(\S+)` 去重
            if decide_skip(scene):
                # 仅上述两类豁免可走此分支；写声明是豁免生效的前提（先声明后跳过）
                append_skip_entry("pipeline/audit/skip_performance.yaml",
                                  scene_id=scene.id,
                                  reason="<两类豁免判据之一；多角色豁免引 scene_card 证据>")
            else:
                for role_slug in expected_roles:  # 全部在场角色；相互独立，可并行 dispatch
                    performance_result = Task(
                        subagent_type="character-actor",
                        prompt=(
                            f"为场景 {scene.id} 角色 {role_slug} 产出 performance 素材。\n"
                            f"按 character-actor 定义的静态清单自读输入，产物按 character-rehearsal skill 的 schema\n"
                            f"Write 到 pipeline/staging/scene_{scene.id}/{role_slug}_performance.md。"
                        ),
                    )
                    # actor 失败不升级 ESCALATED——继续下一角色；
                    # 该角色无 performance 文件，writer 按素材缺席降级分支兜底
                    # 成功的产物 writer 按条件读路径自动命中；不需要额外落档

            # ============ Step 4c: 反先验场景 fast-path（counter_prior_scene） ============
            # scene_card.counter_prior_scene.used=true 时附加结构化约束段；
            # used=false / 字段缺失 → 不注入，走通用 Craft Preflight。
            # schema 见 phase5 output-schema.md（结构化对象，不是扁平 enum）。
            # writer 不 fork 新分支，仅 dispatch prompt 多一段约束。
            cps = getattr(scene.card, "counter_prior_scene", None)
            counter_prior_extra = ""
            if cps and cps.get("used") is True:
                kind = cps.get("kind", "custom")
                mundane = cps.get("mundane_action", "<未指定具体日常动作>")
                emo_ctx = cps.get("emotional_context", "<未指定高情感语境>")
                forbidden = cps.get("forbidden_moves") or [
                    "不得把日常动作解释成象征",
                    "不得在动作后追加心理解释",
                ]
                forbidden_block = "\n".join(f"    * {m}" for m in forbidden)
                counter_prior_extra = (
                    "\n\n本场景标记 counter_prior_scene。\n"
                    f"  - 类型：{kind}\n"
                    f"  - 嵌入的日常动作：{mundane}\n"
                    f"  - 高情感语境：{emo_ctx}\n"
                    f"  - 禁止：\n{forbidden_block}\n"
                    "保留嵌入的日常行为；不允许把日常行为升华成象征；"
                    "不允许在日常行为后追加心理解释。"
                )

            # ============ Step 4d: performance 覆盖检查（writer dispatch 硬前置）============
            # 两包通用协议步骤——derivative 分发形态无 hooks/，本步骤是其唯一 enforce 面；
            # 主包另有 PreToolUse hook 兜底（可解析时双保险，不互替）。
            # 命令：python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_performance_coverage.py \
            #       --work-dir <run根> --scene {scene.id}    # exit 0 通过 / exit 1 阻断
            rc = run_script("verify_performance_coverage.py",
                            work_dir=WORKDIR, scene=scene.id)
            if rc != 0:
                # exit 1 → 不得 dispatch writer：按 stderr 的缺失 slug 清单回 Step 4b
                # 补 fan-out，或补 audit/skip_performance.yaml 合法条目，然后重跑本检查
                fix_step_4b_gap(scene)  # 补素材或补声明
                rc = run_script("verify_performance_coverage.py",
                                work_dir=WORKDIR, scene=scene.id)
                if rc != 0:
                    mark_scene_pending_human(scene.id,
                        reason="performance_coverage_failed", status="ESCALATED")
                    continue

            result = Task(
                subagent_type="writer",
                work_dir=WORKDIR,   # 结构化字段：让 PreToolUse 覆盖检查 hook 无需从 prompt 猜 run 根
                prompt=f"为场景 {scene.id} 首次生成 draft。按 SKILL.md 读输入、"
                       f"产 pipeline/scenes/scene_{scene.id}.md（单路径协议；fresh session 即便看到已存在文件也忽略）。"
                       f"完成回复 'done draft for scene {scene.id}'。"
                       + counter_prior_extra,
            )
            if not result.success:
                mark_scene_pending_human(scene.id,
                    reason="writer_dispatch_failed", status="ESCALATED")
                continue

            # ============ Step 4.5: PATCH 档 reviser 接线 ============
            # writer 成功后**先判 patch 触发**（Step 4.5 C1 修订：tail + publish
            # 时机挪到 patch 判定之后，避免 reviser 失败时下游读到未验收的 writer
            # 版 draft_tail）
            patch_path = WORKDIR / f"pipeline/scene_{scene.id}/patch_directive.yaml"
            if patch_path.exists():
                # patch_directive.yaml.source 权威 enum：`scene_review`（scene-reviewer
                # verdict=PATCH 分支自动产出）。其它 source 已废。
                revision_result = Task(
                    subagent_type="reviser",
                    prompt=f"为场景 {scene.id} 执行 PATCH 档修订。按 revision SKILL "
                           f"规定读 pipeline/scenes/scene_{scene.id}.md + "
                           f"patch_directive.yaml，定点 Edit 修，产 "
                           f"revision_summary.md（顶部含 status 字段）。完成回复 "
                           f"'done revision for scene {scene.id}; "
                           f"status=<complete|partial|failed>'。",
                )

                if not revision_result.success:
                    # dispatch 层面失败（agent 没跑完 / timeout / 产出缺失）
                    mark_scene_pending_human(scene.id,
                        reason="dispatch_failed",
                        detail=f"reviser agent failed: {revision_result.error}",
                        status="ESCALATED")
                    continue

                # 双源 status 解析（权威源 = revision_summary.md；reply 仅提示）
                # 缺文件 / 缺字段 / 双源冲突一律返回 "failed"
                revision_status = parse_revision_status_strict(
                    summary_path=WORKDIR / f"pipeline/scene_{scene.id}/revision_summary.md",
                    task_reply=revision_result.reply_text,
                )

                if revision_status == "failed":
                    # agent 跑完但零 applied / summary 不达标 / 双源冲突
                    # 例外：summary reason=should_be_rollback（patch 批全为 ROLLBACK 类，
                    # reviser 无权施工）→ 不是 pending_human：orchestrator 按
                    # scene-reviewer verdict 升级判断，重派 writer fresh session 走 ROLLBACK
                    mark_scene_pending_human(scene.id,
                        reason="revision_failed_zero_applied",
                        detail=(f"revision_summary status=failed 或 "
                                f"缺文件/缺字段/双源冲突；reply: "
                                f"{revision_result.reply_text}"),
                        status="ESCALATED")
                    continue

                if revision_status == "complete":
                    # 原子改名 pending → applied（幂等保证）
                    run_script("mark_patch_applied.py",
                               scene_id=scene.id, work_dir=WORKDIR)

                # revision_status == "partial":
                #   - reviser 已自行 Edit patch_directive.yaml 移除 applied 条目
                #     只留 not_applied（下轮重试清单语义）
                #   - orchestrator 不 mark_applied（保持 pending 让 orchestrator /
                #     Step 5 scene-review 决定是否重派 reviser）
                #   - pending 内 reason=should_be_rollback 的条目**不再重派 reviser**
                #     （reviser 无权改事件因果/全场基调）——orchestrator 按 scene-reviewer
                #     verdict 升级判断是否重派 writer 走 ROLLBACK
                #   - 仍进下方 tail + publish：已应用部分的 revised draft 落地

            # tail 在唯一权威 scene_{id}.md 上执行（单路径协议——无 publish 中间步骤）
            #   - 无 patch：writer 版 scene_{id}.md 即权威
            #   - complete：reviser Edit 后 scene_{id}.md 即权威
            #   - partial：reviser Edit 后（部分应用）scene_{id}.md 即权威
            #   - failed / dispatch 失败：上方 continue 走掉本行不到
            run_script("extract_draft_tail.py", scene_id=scene.id, work_dir=WORKDIR)

        # ============ Step 2.3: scene-review 四档分流（每场景入口占位）============
        # Phase 6 per-scene loop 内**不跑** scene-review——scene-review 设计为 Phase 6
        # **全场景 draft 完成后**的独立审阅阶段（见本文件 §1.5）。

```

**关键约束**：
- 所有 subagent 调用 **一律 fresh session + 极简 dispatch**（仅传 `scene_id` + 档位决策）；输入文件清单、工具限制、skill 加载清单、system prompt 静态分层见 SKILL.md 和 `${CLAUDE_PLUGIN_ROOT}/agents/{agent}.md`（遵守 §0.4 三层约定）
- orchestrator **全程不产 prose**——不改写 / 整合 / 兼职修订

---

## 1.5. Step 5 scene-review 审阅阶段（per-scene loop 结束后）

**时机**：`phase6_dispatcher` 完成所有场景的 per-scene loop 后，**Phase 7 整合前**。此时所有场景已各自有 `pipeline/scenes/scene_{id}.md`（Step 4 writer + 可选 Step 4.5 reviser 修订产出）。

**三层职责分工**：

| 层 | 执行 | 产出 |
|---|---|---|
| L1 脚本 lint（Phase A） | orchestrator 对每场景调三脚本 | `pipeline/review/lint/{scene_id}.{ai_filler,lexical_stats,dialogue}.yaml` + `{scene_id}.machine_directive.yaml`（机器通道时点①） |
| L2 story-review adaptive（Phase B） | orchestrator A 默认必跑；B/C 按信号 conditional dispatch（长篇 / 复杂角色 / 复杂世界规则 / design-validation 风险 / 用户要求 / strict 全开） | `A_aesthetic.yaml`（必产）+ `B_narrative_consistency.yaml` / `C_structural_consistency.yaml`（按需产）|
| L3 scene-review 四档分流 + input gate | orchestrator 跑 input gate → 通过则 dispatch scene-reviewer；缺失则 orchestrator 原子写 ESCALATED 降级 yaml | `pipeline/review/scene_{id}.yaml`；scene-reviewer 只写 PASS/PATCH/ROLLBACK/REWRITE，ESCALATED 仅由 orchestrator input_gate 写 |

### scene-reviewer input gate（orchestrator 责任，硬约束）

orchestrator 在 dispatch scene-reviewer 前 **MUST** 执行：

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verify_scene_review_inputs.py \
  --scene-id {scene_id} --pipeline-root .
```

退出码处置：

| exit | 处置 |
|---|---|
| 0 | 继续 dispatch scene-reviewer |
| 1 | 写降级 yaml 到 `pipeline/review/scene_{scene_id}.yaml`：`scene_id` / `verdict: ESCALATED` / `review_incomplete: true` / `missing_inputs: [...]` / `written_by: orchestrator_input_gate`；**不** dispatch scene-reviewer；跳过本场进 Step 7 或停机决策 |
| 非 0/1 | 当作 `dispatch_failed`，记入运行日志，标 ESCALATED |

**禁止**：

- orchestrator 跳过此 gate 直接 dispatch scene-reviewer
- 任何 scene-reviewer 产物 yaml 若 `written_by: scene-reviewer` 但 `missing_inputs` 不为空 → 视为协议违反，回滚到 ESCALATED 并人工介入

下方 `phase6_5_review` 伪代码（L3 段 Step 2.0）是本硬约束的执行示例；规则源以本节为权威，伪代码与本节冲突时以本节为准。

```python
def phase6_5_review(scenes_in_order):
    """Step 5 审阅阶段：L1 lint → L2 A/B/C → L3 scene-reviewer → verdict 路由。"""

    # ============ L1: 对每场景跑 lint 三件套（Phase A）============
    # 可以 orchestrator 串行直接调脚本（每场景 3 调用），或写循环脚本批跑。
    # lint 脚本 fail-fast；任一 exit 非 0 → mark_scene_pending_human(reason="lint_script_failed")
    # 对每场景：
    for scene in scenes_in_order:
        for script in ["ai_filler_lint", "lexical_stats", "dialogue_lint"]:
            extra_args = []
            if script == "lexical_stats" and phase1.genre == "武侠":
                extra_args += ["--visual-ratio-threshold", "0.85"]
            if phase1.genre:
                extra_args += ["--genre", phase1.genre]
            rc = run_script(
                f"{script}.py",
                scene_id=scene.id, work_dir=WORKDIR,
                extra=extra_args,
            )
            if rc != 0:
                mark_scene_pending_human(scene.id,
                    reason="lint_script_failed",
                    detail=f"{script}.py exit {rc}", status="ESCALATED")
                # 继续其他脚本，收集最大信息；scene 标 ESCALATED 由下游跳过

        # 机器通道时点①：ai_filler lint 落盘后立即产修复指令基础 + 台账 issued
        # （orchestrator 无条件执行，不看任何 verdict）
        run_script("machine_directive.py", scene_id=scene.id, work_dir=WORKDIR)

    # ============ L2: adaptive dispatch story-review A / B / C ============
    # standard 模式默认只跑 A；B / C 由 orchestrator 现场判断是否触发——满足任一信号即跑：
    #   - 长篇（多 arc / 场景数足以发生跨场景矛盾） → B
    #   - 复杂角色关系（多角色高频互动） → B
    #   - 复杂世界规则 / 多时间线 / pipeline_crosscheck 风险 → C
    #   - design-validation 已发现风险 → B + C
    #   - reader-review 报告理解断裂（仅 Phase 7 二次审查时） → B
    #   - 用户明确要求"严格审查" → A + B + C
    # 判据是信号不是数字门槛；判定无信号时仅 A。三组共用 agent 模板，靠 group 参数区分。
    A_result = Task(subagent_type="story-review", prompt="group=A")
    if should_run_B(scene_set, design_state, user_intent):
        B_result = Task(subagent_type="story-review", prompt="group=B")
    if should_run_C(scene_set, design_state, user_intent):
        C_result = Task(subagent_type="story-review", prompt="group=C")
    # 各组产 pipeline/review/{A_aesthetic,B_narrative_consistency,C_structural_consistency}.yaml

    # ============ L2.5: 过滤全文级 finding + 全局路由 ============
    # 从 B/C 报告分离 scene_id=null 条目，聚合到 global_findings.yaml；
    # adaptive 路径下 B/C 可能未跑，脚本会写空 global_findings.yaml 不报错
    run_script("aggregate_global_findings.py", work_dir=WORKDIR)
    global_payload = load_yaml(WORKDIR / "pipeline/review/global_findings.yaml") or {}
    global_findings = global_payload.get("global_findings", [])

    global_blockers = [f for f in global_findings if f.get("severity") == "CRITICAL"  # severity 枚举 CRITICAL/IMPORTANT/INFO（story-review output-schema 权威）；缺省按 IMPORTANT，不触发全局升级]
    if global_blockers:
        # 记录全局路由决策（升级人工 / 回退 Phase 5 以上）
        # **注意**：不阻止下方 per-scene scene-review 继续跑——两层并行（brief §5.2 r4）
        mark_global_escalation(reason="global_critical",
                               findings=global_blockers, status="ESCALATED")

    # ============ L3: 对每场景 input gate → dispatch scene-reviewer ============
    # 入口前置：scene-reviewer dispatch 之前必须跑 verify_scene_review_inputs.py
    # 校验 required input 完整性。
    # 失败时 orchestrator 原子写降级 yaml（verdict=ESCALATED），不 dispatch。
    # 不再让 L1 失败 silent `continue`——任何 L1/L2 失败都会让 input gate fail
    # → 必产 ESCALATED yaml（可观测），而不是被 continue 静默跳过。
    for scene in scenes_in_order:
        verdict_path = WORKDIR / f"pipeline/review/scene_{scene.id}.yaml"

        # ---- Step 2.0: input gate ----
        gate_rc, gate_out = run_script_capture(
            "verify_scene_review_inputs.py",
            "--scene-id", scene.id,
            "--pipeline-root", str(WORKDIR),
        )
        # gate_out 是 YAML：{status, scene_id, missing_inputs}
        if gate_rc != 0:
            # 缺 required input → 原子写降级 yaml，不 dispatch scene-reviewer
            atomic_write_yaml(verdict_path, {
                "scene_id": scene.id,
                "verdict": "ESCALATED",
                "review_incomplete": True,
                "missing_inputs": gate_out["missing_inputs"],
                "written_by": "orchestrator_input_gate",
                "written_at": now_iso8601(),
                "rationale": (
                    "required input 缺失，无判定基础。补齐 missing_inputs "
                    "后由 orchestrator 原子移动本文件到 "
                    f"scene_{scene.id}.input_gate.yaml 再 dispatch scene-reviewer。"
                ),
            })
            # dispatcher 短路：不计 prose_quality；review_completeness=False；不派 reviser
            continue

        # ---- Step 2.5: 降级 yaml 清理协议 ----
        # 若 verdict_path 已存在且是上一次 input gate 失败写的 ESCALATED 降级 yaml
        # （written_by=orchestrator_input_gate），原子移动到 .input_gate.yaml 保留
        # audit，scene-reviewer 启动时见 verdict_path 不存在，幂等前置正常通过。
        # scene-reviewer 自身的产物（written_by=scene-reviewer 或无 written_by 字段
        # 的 scene-reviewer 产物）**不允许**移动——保留 scene-reviewer 幂等规则。
        if verdict_path.exists():
            existing = load_yaml(verdict_path)
            if existing.get("written_by") == "orchestrator_input_gate" \
                    and existing.get("verdict") == "ESCALATED":
                atomic_rename(
                    verdict_path,
                    WORKDIR / f"pipeline/review/scene_{scene.id}.input_gate.yaml",
                )
            # 否则：scene-reviewer 产物存在 → 走 scene-reviewer 自身的 already_reviewed
            # 幂等（dispatcher 不主动清理）

        # ---- Step 2.6: dispatch scene-reviewer ----
        review_result = Task(
            subagent_type="scene-reviewer",
            prompt=f"为场景 {scene.id} 做 scene-review。按 scene-review SKILL 读 "
                   f"draft + scene_card + A findings（必产，筛 scene_id=={scene.id}）"
                   f"+ lint report 合集；B/C findings 若文件存在则筛 scene_id=={scene.id} 读取，"
                   f"缺席不阻断（adaptive dispatch）；"
                   f"产 scene_{{id}}.yaml（含 verdict 字段；"
                   f"verdict ∈ PASS/PATCH/ROLLBACK/REWRITE，永不写 ESCALATED——"
                   f"ESCALATED 仅由 orchestrator input_gate 写）；"
                   f"若 PATCH 档额外产 patch_directive.yaml (source=scene_review)。"
                   f"完成回复 'done scene-review for scene {scene.id}; "
                   f"verdict=<...> (n patches, m critical)'。",
        )

        if not review_result.success:
            mark_scene_pending_human(scene.id,
                reason="dispatch_failed",
                detail=f"scene-reviewer agent failed: {review_result.error}",
                status="ESCALATED")
            continue

        verdict = parse_scene_verdict_strict(
            review_path=WORKDIR / f"pipeline/review/scene_{scene.id}.yaml",
            task_reply=review_result.reply_text,
        )
        # 规则：
        # - verdict ∈ {PASS, PATCH, ROLLBACK, REWRITE} → 正常路由（下方）
        # - verdict=ESCALATED + written_by=orchestrator_input_gate → 不应到此分支
        #   （input gate 失败时 dispatcher 已 continue，不会走到 parse 步骤）；
        #   若到此说明 scene-reviewer 误写 ESCALATED → 当作 verdict_missing 升级
        # - 文件缺失 / 字段缺失 / 值非法 → ESCALATED(verdict_missing)
        # - Task reply 与文件不一致 → ESCALATED(verdict_source_conflict)
        # - ESCALATED(already_reviewed) → 幂等前置命中，人工决定是否清理

        if verdict in ("ESCALATED_missing", "ESCALATED_conflict", "ESCALATED_already"):
            reason_map = {
                "ESCALATED_missing": "verdict_missing",
                "ESCALATED_conflict": "verdict_source_conflict",
                "ESCALATED_already": "already_reviewed",
            }
            mark_scene_pending_human(scene.id,
                reason=reason_map[verdict], status="ESCALATED")
            continue

        # ============ L3 verdict 路由 ============
        if verdict == "PASS":
            # PASS 只裁决叙事通道；机器通道不受 verdict 影响——
            # 本场景是否还有机器修复待执行，统一在下方 Step 5.6 检查
            # （PASS -> maybe_machine_distribution -> continue）
            continue

        if verdict == "PATCH":
            # scene-reviewer 已产 pipeline/scene_{scene.id}/patch_directive.yaml
            # (source=scene_review)；走现有 reviser 接线消费之。
            #
            # traceability gate（dispatch reviser **前** 必须跑）：
            # 校验 anchor_quote 仍在当前正文 + 不引用 user_accepted finding
            # 失败 → 不 dispatch reviser，标 ESCALATED；
            # 防"A/B/C 是新的但 patch 引用已 resolved 的旧 finding / 已删除的句子"
            trace_rc, trace_out = run_script_capture(
                "verify_patch_directive_traceability.py",
                "--scene-id", scene.id, "--pipeline-root", str(WORKDIR),
            )
            if trace_rc != 0:
                mark_scene_pending_human(scene.id,
                    reason="patch_directive_untraceable",
                    detail=trace_out.get("findings", []),
                    status="ESCALATED")
                continue

            # 单路径协议下 reviser 直接 Edit pipeline/scenes/scene_{scene.id}.md。
            # 复用 §1 Step 4.5 段的 reviser dispatch + status 判定 +
            # mark_patch_applied + tail 全流程；本文件不重复伪代码。
            #
            # post-revision 复审 fast-path（脚本先行，免二次 dispatch）：
            # revision status=complete 且 v2 无新增 family → 脚本 PASS 即闭合
            fp_rc = run_script("family_gate.py",
                extra=["--before", f"pipeline/review/lint/{scene.id}.ai_filler.yaml",
                       "--after",  f"pipeline/review/lint/{scene.id}.ai_filler.v2.yaml"])
            if revision_status == "complete" and fp_rc == 0:
                atomic_write_yaml(
                    WORKDIR / f"pipeline/review/scene_{scene.id}.post_revision.yaml",
                    {"scene_id": scene.id, "verdict": "PASS",
                     "written_by": "orchestrator_fastpath_gate",
                     "rationale": "patch 全 applied 且 v2 无新增 family（脚本判定）"})
                # 跳过 post-revision scene-reviewer dispatch；不满足则走下方正常复审
            else:
                # reviser Edit 完成后必须重派 scene-reviewer 做 post-revision review，输出：
                #   pipeline/review/scene_{scene.id}.post_revision.yaml
                # 只有 post_revision verdict=PASS 才算 PATCH 闭合；否则交 orchestrator 升级处理。
                dispatch_post_revision_review(scene.id)

        elif verdict == "ROLLBACK":
            # 重派 writer fresh session 重写本场景
            # 注意：不读旧 scene_{id}.md（对齐 writer SKILL "fresh session" 约定）
            # 单路径协议下 writer 直接 overwrite pipeline/scenes/scene_{scene.id}.md
            result = Task(
                subagent_type="writer",
                prompt=f"为场景 {scene.id} **重写** scene_{scene.id}.md（ROLLBACK）。"
                       f"scene-reviewer verdict=ROLLBACK，rationale 见 "
                       f"pipeline/review/scene_{scene.id}.yaml；按 writer SKILL 读 "
                       f"scene_card + role_briefs + 上下文重新生成 "
                       f"pipeline/scenes/scene_{scene.id}.md。"
                       f"完成回复 'done draft for scene {scene.id} (rollback)'。",
            )
            if not result.success:
                mark_scene_pending_human(scene.id,
                    reason="dispatch_failed",
                    detail="writer rollback failed", status="ESCALATED")
                continue
            # 单路径协议：writer 已直接 overwrite scene_{id}.md，无 publish 步骤

            # post-rewrite review（与 PATCH 分支对称）
            # publish 后必须重派 scene-reviewer 做 post-rewrite review，输出
            #   pipeline/review/scene_{scene.id}.post_revision.yaml（复用 PATCH 路径文件名）
            # 只有 verdict=PASS 才算 ROLLBACK 闭合
            # scene-reviewer 通过 dispatch prompt "post-rewrite" 关键字进入 post-revision 模式
            rewrite_review_result = Task(
                subagent_type="scene-reviewer",
                prompt=f"为场景 {scene.id} 做 **post-rewrite review**（ROLLBACK 后）。"
                       f"读 writer 重写后的 pipeline/scenes/scene_{scene.id}.md + "
                       f"scene_card + 当前批次 A findings（必产）+ lint report；"
                       f"B/C findings 若本轮 dispatch 且文件存在则一并读取，缺席不阻断"
                       f"（adaptive dispatch）；产 "
                       f"pipeline/review/scene_{scene.id}.post_revision.yaml（含 "
                       f"review_round: post_revision_round1）；"
                       f"verdict=PASS 才算 ROLLBACK 闭合。"
                       f"完成回复 'done post-revision review for scene {scene.id}; "
                       f"verdict=<...> (round 1, n patches, m critical)'。",
            )
            if not rewrite_review_result.success:
                mark_scene_pending_human(scene.id,
                    reason="dispatch_failed",
                    detail="post-rewrite review failed", status="ESCALATED")
                continue

        elif verdict == "REWRITE":
            # 涉及 Phase 3-5 设计层缺陷——不在 Phase 6 范围解决
            mark_scene_pending_human(scene.id,
                reason="rewrite_upstream_design",
                detail="scene_card / spine / structure 需回上游 Phase 修订",
                status="ESCALATED")
            continue

    # ============ Step 5.6: 机器通道 distribution lane（verdict 路由全部完成后）============
    # 顺序硬约束：先点状（叙事 patch，anchor 敏感）后分布（场景级改写会挪 anchor）。
    # scene-review verdict=PASS 的场景也照样进入本步——机器指令不经 verdict 裁决。
    for scene in scenes_in_order:
        directive_path = WORKDIR / f"pipeline/review/{scene.id}.machine_directive.yaml"
        if not directive_path.exists():
            continue
        # 时点②：读 revision_summary 注入保护区 + objection 验算 + pre_dist 快照，置 dispatch_ready
        run_script("machine_directive.py", scene_id=scene.id, work_dir=WORKDIR,
                   extra=["--refresh"])
        directive = load_yaml(directive_path)
        if not any(e["status"] == "pending" for e in directive["entries"]):
            continue  # objection 全生效 / 已 resolved → 本场景机器通道闭合

        attempt = 1
        while attempt <= 2:
            result = Task(
                subagent_type="distribution-reviser",
                prompt=f"为场景 {scene.id} 执行分布修复（attempt {attempt}）。按 "
                       f"distribution-revision SKILL 读 machine_directive + 正文，"
                       f"场景级改写，产 distribution_summary.md。完成回复 "
                       f"'done distribution for scene {scene.id}; status=<...>'。")
            status = parse_summary_status(  # 权威源 = distribution_summary.md 顶部 status
                WORKDIR / f"pipeline/scene_{scene.id}/distribution_summary.md")
            if not result.success or status == "failed":
                mark_scene_pending_human(scene.id,
                    reason="distribution_failed", status="ESCALATED")
                break
            # re-lint（独立 suffix，保留审计链）+ 复合验收（全脚本，无 override）
            run_script("ai_filler_lint.py", scene_id=scene.id, work_dir=WORKDIR,
                       extra=["--output-suffix", f"dist{attempt}"])
            gate_rc = run_script("distribution_gate.py", scene_id=scene.id,
                       work_dir=WORKDIR,
                       extra=["--attempt", str(attempt), "--max-attempts", "2"])
            if gate_rc == 0:
                run_script("extract_draft_tail.py", scene_id=scene.id, work_dir=WORKDIR)
                break  # 复合验收 PASS，entries 已由脚本置 resolved
            if gate_rc == 2:
                mark_scene_pending_human(scene.id,
                    reason="distribution_gate_error", status="ESCALATED")
                break
            if attempt == 2:
                # 脚本已把残余 entries 置 escalated
                mark_scene_pending_human(scene.id,
                    reason="distribution_gate_failed_2_rounds", status="ESCALATED")
                break
            # 残余重生成（机器权威——reviser 不写 directive）+ 再刷新
            run_script("machine_directive.py", scene_id=scene.id, work_dir=WORKDIR,
                       extra=["--lint-suffix", f"dist{attempt}"])
            run_script("machine_directive.py", scene_id=scene.id, work_dir=WORKDIR,
                       extra=["--refresh"])
            attempt += 1

    # 进 Phase 7 的门（assemble 前 hook 机器强制）：所有场景无 pending machine
    # directive，或对应 distribution_gate 已 PASS / entries 已 escalated

    # Phase 7 整合直接读 scenes/scene_*.md
```

## Step 6: Post-revision review

reviser 完事且 `status=complete` 后，orchestrator 先重跑全场 lint：

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_filler_lint.py \
  --scene-id S01 --work-dir "$WORK_DIR" \
  --output-suffix v2
# 输出：pipeline/review/lint/S01.ai_filler.v2.yaml
```

随后对 `patch_directive.applied.yaml` 中每个 patch 重跑 local lint。脚本用
`old_span` 或 `anchor_quote` 作为 v1，用当前 `scene_{id}.md` 的
`location.line_range` 提取 new span 作为 v2：

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/run_local_lint.py \
  --scene-id S01 --work-dir "$WORK_DIR" \
  --patch-id patch_01 \
  --output pipeline/review/lint/S01.patch_01.local.v1.yaml \
  --output-v2 pipeline/review/lint/S01.patch_01.local.v2.yaml
```

最后 dispatch scene-reviewer，prompt 必须含 `post-revision`。subagent 读取：

- `pipeline/scenes/scene_{id}.md`
- `pipeline/review/lint/{scene_id}.ai_filler.v1.yaml`
- `pipeline/review/lint/{scene_id}.ai_filler.v2.yaml`
- `pipeline/review/lint/{scene_id}.{patch_id}.local.v1.yaml`
- `pipeline/review/lint/{scene_id}.{patch_id}.local.v2.yaml`
- `pipeline/scene_{scene_id}/revision_summary.md`
- `pipeline/review/{scene_id}.machine_ledger.yaml`

**关键差异于 Step 4.5 per-scene 入口**（不要混淆）：

| | Step 4.5 per-scene 入口 | Step 5 §1.5 批次路径 |
|---|---|---|
| 时机 | writer 成功后立即判 patch_directive | 所有场景 draft 完成后统一审 |
| patch 来源 | 用户紧急构造（`source: scene_review` 字段手填） | scene-reviewer 自动产出 (`source: scene_review`) |
| 覆盖档 | 仅 PATCH（无 patch_directive → 直接跳过） | PASS / PATCH / ROLLBACK / REWRITE 全四档 |
| 场景切换 | 本场景内 writer → 可选 reviser → tail + publish → 下一场景 | 全部场景先跑完 per-scene loop，再跑批次 |

两条路径**共存**：per-scene 入口作紧急修订用；批次入口是 Phase 6 完整 pipeline 的默认路径。**不要在同一次 pipeline 运行中同时使用**——per-scene 用完留下的 `patch_directive.yaml` 会干扰批次路径判幂等锚点。

---

## 2. role_brief 派生协议

**触发**：dispatcher 进入每场景的**第一步**。

**执行机制**：orchestrator 通过当前运行时的 subagent dispatch 启动 `role-brief-deriver`：

```
dispatch_subagent(type="role-brief-deriver",
                  prompt="为场景 {scene_id} 派生 role_brief ...")
```

Agent 元配置在 `${CLAUDE_PLUGIN_ROOT}/agents/role-brief-deriver.md`，职责层在 `${CLAUDE_PLUGIN_ROOT}/skills/role-brief-deriver/SKILL.md`。Agent 通过 StoryStudio 工作区运行时 agents 软链（`.claude/agents` 或 `.codex/agents` → `${CLAUDE_PLUGIN_ROOT}/agents`）注册，权威注册名 `role-brief-deriver`（无 plugin 前缀）。

**产出**（按 `role-brief-deriver` SKILL.md 落盘）：
- `pipeline/scene_{scene_id}/role_briefs.md` — writer / reviser 消费

**role_brief schema**：权威源是 `role-brief-deriver` SKILL.md 的"输出契约"节——字段全集 / 必填可选划分 / fallback 语义以其为准，本协议不镜像 schema 表。writer 重点消费字段见 writer skill"人物语言素材消费优先级"节。

**失败语义**：subagent dispatch 返回失败（agent 找不到 / timeout / schema 校验不过 / 输出缺文件）→ orchestrator 调 `mark_scene_pending_human(scene_id, reason=..., status="ESCALATED")`，**跳过本场景**继续下一场景；story-review 全书审时统一人工介入。dispatcher 不在本场景内重试 role_brief 派生。

**静态 / 动态分层**（§0.4 约定）：

| 层 | 位置 | 内容 |
|---|---|---|
| 元配置 | `${CLAUDE_PLUGIN_ROOT}/agents/role-brief-deriver.md` | `name` / `description` / `model: sonnet`；工具限制在 body 自然语言声明 |
| 职责静态 | `${CLAUDE_PLUGIN_ROOT}/skills/role-brief-deriver/SKILL.md` | 输入文件路径硬约定 / 输出 schema / fallback 语义 / 跨源推理指引 |
| orchestrator 动态 | subagent dispatch prompt | 仅 `scene_id` |

---

## 3. direct-writer 链路

- writer subagent 吃 `scene_card.md`（`extract_scene_card.py` 产）+ `role_briefs.md`（Step 2 role-brief-deriver 产）+ 角色 runtime package（`story-character-skills/.claude/skills/{slug}/SKILL.md` + `state.md`）+ `phase3_spine.yaml.spine_statement` + `phase0 reference_materials / phase1 domain_knowledge` + `(上一场景 draft_tail.md)`
- writer 直接产 `pipeline/scenes/scene_{scene_id}.md`（单路径协议；正文权威，对齐 generate_phase6_index / assemble_story / phase7 消费）
- dispatcher 紧跟调 `extract_draft_tail.py` 产 `pipeline/scene_{scene_id}/draft_tail.md`（下一场景衔接）
- writer 入口 **极简 dispatch**：orchestrator 通过当前运行时的 subagent dispatch 仅传 `scene_id`；工具限制 / skill 加载清单 / 输入文件路径清单全部在 `${CLAUDE_PLUGIN_ROOT}/agents/writer.md`（元配置）和 `${CLAUDE_PLUGIN_ROOT}/skills/writer/SKILL.md`（职责层）静态约定
- writing 细节由 writer 启动后加载 `prose-craft` + `dialogue-craft` skill——散文原则 / 创意执行 / 对白工坊从这两个 skill 获得

---

## 3.5. scene-reference 调度与消费语义（仅在装有 MUSE-canon-distill 扩展包时生效）

> 本节定义 orchestrator 侧的**调度时点 + 判据** 与 writer 侧的**消费契约**。`scene-reference` skill 由 `MUSE-canon-distill` 扩展包提供，主干 plugin 单独运行时本节默认 graceful skip。扩展包内部检索策略、query 构造、脚本入口、KB 内容描述均归扩展包自身职责（细节由扩展包 `scene-reference` SKILL.md 自身承载，按 D7 闭包纪律不构造 link）。

### 3.5.1 调度（orchestrator 侧）

**触发时点**：per-scene loop 内，**dispatch role-brief-deriver 之后、dispatch writer 之前**——理由：reference 是 writer 的 few-shot 输入，必须先于 writer 落盘；同时晚于 role_brief 派生，避免 role_brief 失败 ESCALATED 时白跑 reference。

**前置条件**：
- **装包**：`MUSE-canon-distill` 扩展包可见（通过 `Skill scene-reference` 是否可触发判定）。未装包时本节整层跳过，下面三段不适用。

**触发判据**（满足前置条件后，任一命中即调）：
- **场景命中 key_scene 信号**（由 orchestrator 现场判断，不规定数字门槛）：开篇 / 收束 / 高潮 / 主要转折 / 高压对峙 / 情感转折 / 高难对白 / 群戏（≥3 角色同时在场）/ scene_card `beat_direction` 显示重型节拍 / 上一场连续命中 AI 陈腔 lint hits → 强制启用 reference 校准文风
- **用户指定"每场都查"**：用户在主对话明示路径 A 全开时每场调

**强制关闭**：
- 用户在主对话明示"不要参考" / "不查 reference" / 等价表达 → 本 run 全场景关闭，覆盖触发判据

**默认跳过**（前置条件满足 + 未命中触发判据 + 未被强制关闭时）：
- 串场 / 过渡 / 单 POV 内心独白 / 短段落收尾 / 已经在前序相似场景吸收过同题材 reference

**调度方式**：`Skill scene-reference` 触发扩展包 skill，传 `scene_id` + 当前场景的检索 query 信号（场景类型 / 冲突 / 情绪 / 关键动作，2-5 个短语）；扩展包内部 query 构造 + kb_query.py 调用 + 产物落盘均由 skill 自身负责。orchestrator 不直接调用 `kb_query.py`。

**失败处理**：
- 扩展包未装（`Skill scene-reference` 不可触发）→ 整层跳过，不进入本步
- KB 缺失 / 脚本退出非 0 / genre 过滤后无场景 → 扩展包内部已处理，stderr 提示，orchestrator 看到非零退出**跳过本场 reference 环节，writer 照常 dispatch**，不阻断主干

### 3.5.2 消费（writer 侧）

- **装/未装判据**：物理文件 `pipeline/references/{sid}_ref.md` 存在性
- **装时消费**：writer 动笔前最后读取该文件，按文件内嵌 `<usage_protocol>` 做 style anchor 提取 + 正向贴近（完整消费契约见 writer skill 输入清单 #10）
- **未装降级**：writer 跳过 reference 消费，主流程继续，不报错

### 3.5.3 ref 对齐校验（orchestrator 侧，writer 落盘后）

ref 存在的场景，writer 产出 `pipeline/scenes/scene_{sid}.md` 后、scene-review dispatch 前，orchestrator 跑密度对比：

```bash
python <MUSE-canon-distill>/knowledge-base/scripts/paragraph_density.py \
  --compare pipeline/scenes/scene_{sid}.md <ref_source_file> \
  --format yaml > pipeline/review/lint/{sid}.density_vs_ref.yaml
```

`<ref_source_file>` 从 ref 文件参考条目的 `ref_source_file:` 元数据行取（取 rank 1）。脚本不可用 / ref 文件无该行 → 跳过本步，不阻断。产物供 scene-reviewer 作密度偏离信号消费（见 scene-review SKILL.md 输入清单）。

### 3.5.4 per-scene 流程图（带扩展包时）

```
per-scene loop:
  1. dispatch role-brief-deriver  → pipeline/scene_{sid}/role_briefs.md
  2. [扩展包 + key_scene / 用户全开] Skill scene-reference  → pipeline/references/{sid}_ref.md
  3. dispatch writer              → pipeline/scenes/scene_{sid}.md  （writer 自读 ref.md，最后读）
  3b. [有 ref] paragraph_density --compare → pipeline/review/lint/{sid}.density_vs_ref.yaml
  4. scene-review L1/L2/L3        → pipeline/review/scene_{sid}.yaml
  5. verdict 路由（PASS / PATCH / ROLLBACK / REWRITE）
```

Step 2 / 3b 在不命中判据 / 未装扩展包时**整步跳过**，不影响后续编号。

---

## 4. 流程违规常见错误

| ❌ 错误 | 为什么错 | ✅ 正确 |
|---------|---------|--------|
| 把 role_brief 派生写成 `run_script("derive_role_brief.py")` 或平台 CLI wrapper | 唯一入口 = 运行时 subagent dispatch；不存在 script / CLI wrapper 路径 | orchestrator 通过运行时 dispatch `role-brief-deriver` subagent |
| orchestrator 自己用 Write 写 `pipeline/scenes/scene_*.md`（绕过 writer subagent） | orchestrator 上下文混杂 design / audit / 多场景信息，自己产正文会让 prose 沾染噪声；per-role subagent 隔离是声音独立性前提（参 SKILL.md §⚠️ 硬约束）| 永远 `Task(subagent_type="writer", prompt="为场景 {id} 派 writer")`，writer 自产正文 |
| orchestrator 直接 Edit `pipeline/scenes/scene_*.md` 做修订（绕过 reviser subagent） | 同上；reviser 走 patch_directive 链路保证可追溯 / 可回滚 | dispatch reviser，喂 patch_directive.yaml |
| Subagent dispatch prompt 里塞文件路径清单 / skill 加载清单 / role 定位 | 违反 §0.4 三层约定；静态清单应在 `${CLAUDE_PLUGIN_ROOT}/agents/{agent}.md` + SKILL.md | dispatch prompt 只含 `scene_id` + 档位决策；其他信息由 subagent 自读文件 |
| role_brief 派生失败时反复重试 / 继续分流 | role_brief 是本场景认知基础；失败应立即 ESCALATED，story-review 统一人工介入 | subagent dispatch 失败 → `mark_scene_pending_human` + `continue`，不在本场景内重试 |
| writer 成功后立即切 draft_tail + publish，不等 PATCH 判定 | reviser 失败 → continue；但下一场景已读 writer 版 tail + 旧 scenes/；正文双路径失去不变量 | tail + publish 一律在 patch 判定后执行；无 patch / 有 patch-成功 共用同一分支末尾；reviser 失败 continue 不产任何下游工件 |
| reviser status=complete 后 dispatcher 忘调 `mark_patch_applied.py` | `patch_directive.yaml` 仍 pending → rerun 同场景重触发 reviser | status=complete 唯一路径上必须调 `mark_patch_applied.py` 改名为 `.applied.yaml`；dispatcher 只消费 pending 文件名 |
| reviser status=partial 时 orchestrator 也调 `mark_patch_applied.py` | applied 改名后 pending 文件消失，未应用 patch 永久丢失 | partial 档 reviser 已自行 Edit `patch_directive.yaml` 只留 not_applied；orchestrator **不**调 mark_patch_applied，保留 pending 文件让下轮重试 |
| 从 Task reply 文本解析 status 作为决策依据 | Task reply 是快速提示不是权威源；reply 与 summary 不一致时以 summary 为准 | `revision_summary.md` 顶部 `status` 字段 = 唯一权威源；reply 仅作 log；缺文件/缺字段/双源冲突一律判 `failed` 走 ESCALATED |
| reviser 改了 patches 未指出的段落（"顺手润色"） | 违反 revision SKILL 的"不越界"红线 | reviser 只能改 patches 列出的位置；其余保留；自检：patches 未覆盖的段落与原 draft `diff` 一致 |
| 把 Step 5 §1.5 批次路径和 Step 4.5 per-scene 路径**混用**（per-scene 留下 `patch_directive.yaml` 后又跑 §1.5 批次） | per-scene 的 `patch_directive.yaml` 会让 §1.5 scene-reviewer 幂等前置误判 "已评审"（`scene_{id}.yaml` 存在检查）或产生 schema 冲突 | 单次 pipeline 只走一条路径；per-scene 是手工触发测试路径；批次是 Phase 6 完整 pipeline 默认路径 |
| scene-reviewer 幂等锚点用 `patch_directive.yaml` 存在性 | 只覆盖 PATCH 档；PASS / ROLLBACK / REWRITE 档下 rerun 不会被 block | 锚点 = `pipeline/review/scene_{id}.yaml`——所有四档的统一产出 |
| scene-reviewer 对 `scene_id: null` 的 B/C finding 做归属猜测（硬塞给某一场景） | 全文级 finding 没有定点修可能；会稀释 scene 级 patch 信号 | `scene_id=null` 由 orchestrator 走全局路由（global_findings.yaml）；scene-reviewer 只筛 `scene_id == 本场景` 条目 |
| 全局有 CRITICAL 级 finding 就短路所有单场景 scene-review | 丢失局部 PATCH/ROLLBACK 信息；后续 orchestrator 无处判断是否要局部修 | 全局路由与单场景 scene-review **两层并行**；orchestrator 汇总后按全局优先级决定是否覆盖局部执行 |
| PATCH 档同位置 A 组"偏删" + lint 模式"偏加"合并成单个 patch | reviser 自由拼接不稳定；违反 patch_directive 组装优先级约束 | 同位置方向冲突 → 拆成两个独立 patch（按优先级 C > B > A > lint 排序），或升档 ROLLBACK；动作方向兼容才可合并 |
| scene-reviewer 产完 verdict=PATCH 后 orchestrator 直接喂 `pipeline/scenes/scene_{id}.md` 给 reviser | 单路径协议下 reviser 直接 Edit `pipeline/scenes/scene_{id}.md`——不存在 draft 与 scenes 同步问题 | §1.5 verdict=PATCH 分支直接 dispatch reviser，reviser 输入即 `pipeline/scenes/scene_{id}.md`；无需前置同步、无需 republish |
| 单条 character-actor dispatch 同时为本场所有角色产 performance 素材 | 角色身份边界被破坏；多角色共用一个 actor 等于回到"场景语言整理器"，丢失 per-role 隔离 | 默认 per-participant fan-out：每个在场角色一条 dispatch，只锚该角色的 `{slug}_performance.md` |
| §1.5 L3 在 dispatch scene-reviewer 前不跑 input gate（直接 dispatch） | required input（A/B/C/lint）missing 时 scene-reviewer 仍可能给 PASS | dispatch 前必须跑 `verify_scene_review_inputs.py --scene-id <id>`；非 0 → orchestrator 原子写降级 yaml（verdict=ESCALATED + review_incomplete=true + missing_inputs + written_by=orchestrator_input_gate）+ continue 不 dispatch |
| L1 lint 失败的场景用 `continue` 静默跳过 + 不写 scene_{id}.yaml | 跳过的场景在 review/ 缺 yaml，与"还没跑 review" 不可区分 | 任何 L1/L2 失败都让 input gate 自然 fail（lint yaml 缺）→ 写 ESCALATED 降级 yaml（可观测）；不让 silent continue 静默降级 |
| orchestrator 见 `verdict_path` 已存在直接 dispatch scene-reviewer，scene-reviewer 走 already_reviewed 短路 | input gate 写的 ESCALATED 降级 yaml 被 scene-reviewer 幂等卡死；补输入后无法重审 | dispatch 前 Step 2.5 检查：现存 yaml 若 `written_by=orchestrator_input_gate` + `verdict=ESCALATED` → 原子移动到 `scene_{id}.input_gate.yaml` 保留 audit；scene-reviewer 产物（written_by=scene-reviewer 或无字段）仍不允许覆盖 |
| scene-reviewer 自身在 `scene_{id}.yaml` 主体写 `verdict: ESCALATED` | ESCALATED 是 input_gate 失败专用档，scene-reviewer 写 ESCALATED 会与 orchestrator 写的混淆，且无 missing_inputs 字段不可消费 | scene-reviewer 永远只写 PASS/PATCH/ROLLBACK/REWRITE 四档；ESCALATED 仅由 orchestrator input_gate 写到主体；scene-reviewer 的运行时失败用 Task reply `ESCALATED(reason)` 表达（不同 channel）|
| `counter_prior_scene.used=true` 时 orchestrator 不读子字段就直接 dispatch writer（让 writer 自己从 scene_card 里翻） | writer dispatch prompt 静态最简（仅 `scene_id`）；不显式注入 fast-path 段，writer 不会知道要保留嵌入的日常行为，会按通用 Craft 自动把日常动作解释成象征 | dispatcher 进 direct-writer 链路时显式检查 `counter_prior_scene.used`，true 时拼 `{kind / mundane_action / emotional_context / forbidden_moves}` 附加到 writer dispatch prompt（参 §1 Step 4c 伪代码） |
| 把 `counter_prior_scene` 当扁平 enum（`counter_prior_scene: "ritual_with_food"`） | 扁平 enum 不告诉 writer 嵌入的日常动作具体是什么，writer 只能临场猜——撞 AI 套路率高 | 结构化对象 `{used, kind, mundane_action, emotional_context, forbidden_moves}`；schema 见 phase5 output-schema.md |
| verdict=PASS 就跳过本场景直接进 Phase 7，不查 machine_directive | PASS 只裁决叙事通道；机器指令不经 verdict——跳过 = 机器主权被旁路 | PASS/PATCH 闭合后一律走 Step 5.6：存在 pending machine directive 就派 distribution-reviser |
| distribution-reviser 消费未 --refresh 的 directive（dispatch_ready=false） | 保护区未注入——分布改写会回退点状修复成果 | orchestrator 先跑 machine_directive.py --refresh；reviser 侧见 dispatch_ready 非 true 拒绝施工 |
| distribution 改写后不跑 re-lint + distribution_gate 就 publish | 复合验收（清零/密度/family/保护区）是纯脚本 gate，跳过 = 无验收出稿 | 每 attempt 后必跑 ai_filler_lint --output-suffix dist{N} + distribution_gate.py；exit 0 才闭合 |
| 重修轮由 reviser 自己决定"还剩什么要修" | 指令权威在脚本；reviser 自决 = 豁免权变相回流 | 残余指令由 machine_directive.py --lint-suffix dist{N} 按 re-lint 结果重新生成 |
