# MAS Scholar Skills Capability Modules

Owner: `One Person Lab`
Purpose: 说明 `MAS Scholar Skills` 能力增强包的机器入口、八个 active 专业 Skill-backed module、runtime environment bridge 和 domain-agent 消费边界。
State: `active_structural_baseline`
Machine boundary: 本文是人读导航。本 repo 的 module catalog snapshot 与 Skill pack 真相以 `contracts/scholar-skills-capability-modules.json`、`.codex-plugin/plugin.json`、`skills/mas-scholar-skills/SKILL.md`、`skills/medical-manuscript-writing/SKILL.md`、`skills/medical-manuscript-review/SKILL.md`、`skills/medical-figure-design/SKILL.md`、`skills/medical-research-lit/SKILL.md`、`skills/medical-statistical-review/SKILL.md`、`skills/medical-table-design/SKILL.md`、`skills/medical-submission-prep/SKILL.md`、`skills/medical-data-governance/SKILL.md` 与 gallery manifest 为准；`skills/opl-scholarskills/SKILL.md` 只作为 legacy alias。可执行 `opl scholar-skills *` CLI 和 Connect 同步行为仍以 OPL Framework readback 为准。

## 基本定位

`MAS Scholar Skills` 是 `mas-scholar-skills` 仓的正式产品名：服务 MAS 医学论文能力的 OPL-owned 外置增强包。历史 `opl-scholarskills` 仅作为 legacy alias 和 provenance。它不是通用 OPL runtime 基座，不是第十一个 OPL 品牌模块，也不是 MAS domain truth owner。它给 MAS overlay 和 MAS stage operating prompts 提供可发现、可校验、可接入 OPL runtime env 的能力模块说明、source pack、quality floor、template、candidate ref 和外部学习吸收材料；同时维护 `medical-manuscript-writing`、`medical-manuscript-review`、`medical-figure-design`、`medical-research-lit`、`medical-statistical-review`、`medical-table-design`、`medical-submission-prep`、`medical-data-governance` 这些专业 Codex skill，供 MAS 同步消费。

十大 OPL 品牌模块仍保持原职责，MAS Scholar Skills 不新增品牌模块：

- `Atlas` 发现与索引能力模块。
- `Pack` 承载 descriptor、schema、artifact/ref lifecycle 与 packaging。
- `Stagecraft` 把能力模块挂到 stage / current-owner-delta 所需的 ref family。
- `Runway` 承载 runtime invocation / attempt / queue 的通用执行骨架。
- `Vault` 记录 evidence、receipt、lineage 与 refs。
- `Console` 投影 operator readback 和安全动作。
- `Connect` 分发、安装、skill/plugin 同步。
- `Charter`、`Workspace`、`Foundry Lab` 分别承载治理、workspace 和 agent factory 边界。

MAS Scholar Skills 不改 `BrandModuleId` 枚举；它作为这些品牌模块共同管理、但面向 MAS 消费的增强包存在。

## 当前模块目录

当前 canonical contract 固定八个 active module id，全部由真实可同步 Codex 专业 Skill 支撑：

- `opl.scholarskills.display` / `Scholar Display`
- `opl.scholarskills.tables` / `Scholar Tables`
- `opl.scholarskills.stats` / `Scholar Stats`
- `opl.scholarskills.lit` / `Scholar Lit`
- `opl.scholarskills.write` / `Scholar Write`
- `opl.scholarskills.review` / `Scholar Review`
- `opl.scholarskills.submit` / `Scholar Submit`
- `opl.scholarskills.data` / `Medical Data Governance` legacy descriptor

每个 module 都声明 input / output schema refs、dependency profile refs、run-context refs、invocation entries、artifact refs、receipt policy、quality evidence 和 authority boundary。`opl scholar-skills inspect/invoke/receipt` 现在会为每个 module 返回 module-specific `module_profile`、artifact candidate ref families 和 unsigned execution receipt ref families，而不是把所有模块都折叠成 Display 的 receipt 形状。

MAS Scholar Skills 正式承接八个 active 专业模块的 MAS 增强材料 source / contract / docs：`lit`、`tables`、`stats`、`submit`、`write`、`review`、`data` 与 `display` 同级进入本仓 contract snapshot、Skill 入口和人读说明。这个承接只限 refs-only / no-authority handoff。所有 active module 都必须能说明 `source_pack_ref`、`candidate_package_ref`、`execution_receipt_ref` 和 `owner_gate_handoff_ref`，但这些 ref 只描述候选输入、候选包、未签执行回执和下游 owner gate 交接点，不写 MAS domain truth、owner receipt、typed blocker、human gate、publication readiness authority、runtime queue 或 provider attempt。

组学能力在 MAS 形成稳定、可维护、可同步的真实组学专业 workflow 后，再作为新的真实专业 Skill 加入本仓。通用 source / external-learning intake 归 OPL Framework 或 MAS stage/source surface，不在 MAS Scholar Skills 专业 Skill 库中占位。

## 模块与 Skill 分层

当前固定采用两类物理形态，避免把能力目录误读成“假 Skill”：

| 层级 | 当前对象 | 作用 |
| --- | --- | --- |
| Active 专业模块合同 | `display`、`tables`、`stats`、`lit`、`write`、`review`、`submit`、`data` | 统一 module id、vocabulary、ref family、checklist、candidate handoff、receipt shape 和 owner gate，并明确对应真实专业 Skill。 |
| 真实专业 Skill | `medical-manuscript-writing`、`medical-manuscript-review`、`medical-figure-design`、`medical-research-lit`、`medical-statistical-review`、`medical-table-design`、`medical-submission-prep`、`medical-data-governance` | 给 Codex 执行稳定医学论文专业流程的 AI-first playbook，并通过 OPL Connect 同步到 workspace / quest `.codex/skills/`。 |

主动临床数据治理已经升级为 `medical-data-governance`，历史 Data module id 只保留 descriptor/readback 兼容。MAS Scholar Skills 只维护这八个有真实专业 Skill 单源的 active module；没有稳定专业 Skill 的能力不在本仓预留占位。

## 专业 Skill 质量地板

本轮继续吸收 `K-Dense-AI/scientific-agent-skills` 与 `Yuan1z0825/nature-skills` 的可迁移经验，但落点是八个真 Skill 的 AI-first 工作流，不新增并列 stage authority，也不要求先安装外部 runtime。

| Skill | 新增质量要求 |
| --- | --- |
| `medical-figure-design` | figure contract、core conclusion、evidence chain、figure archetype、renderer decision、style brief、candidate set、critic review、final-scale visual QA 和 reviewer packet。 |
| `medical-manuscript-writing` | one-sentence argument、terminology ledger、paragraph job map、section contract、claim-strength calibration、citation integrity、figure/table binding、data/code availability audit。 |
| `medical-manuscript-review` | review fact base、technical/significance/reader reviewer lanes、cross-review synthesis、reviewer action matrix、citation repair、revision delta audit、route-back closeout。 |
| `medical-research-lit` | PubMed-first source routing、query plan、fallback source refs、deduplication、retain/reject/watchlist screening、source verification、support-strength matrix、citation integrity floor。 |
| `medical-statistical-review` | statistical question、estimand/target parameter、analysis plan fit、denominator/missingness、assumption diagnostics、effect size/uncertainty、multiplicity/sensitivity、statistical action matrix。 |
| `medical-table-design` | table job、table shell、source metric、denominator、statistical display、table QC、claim-table alignment、journal table contract。 |
| `medical-submission-prep` | journal instruction、reporting guideline、declaration inventory、data/code availability、package consistency、reviewer response candidate、author-input fields、submission action matrix。 |
| `medical-data-governance` | data asset manifest、dataset manifest、data dictionary/codebook、cleaning/normalization readiness、source lineage、version-diff impact、study binding、privacy/access tier、lifecycle/retention guardrail、owner-gate handoff。 |

组学专属 source routing 和材料接入专属 adoption check 分别归 MAS/OPL 对应 owner surface；当 MAS 需要 Codex 主动执行稳定、可维护、可同步的独立专业流程时，再升级为新的真实 Skill。

## MAS 默认入口与技能正文边界

MAS overlay skill 是医学论文工作的 runtime 主入口，MAS stage operating prompts 负责阶段进入、证据门槛、路由、owner gate 和采纳边界。MAS stage 主提示词的 canonical source 是 MAS domain-agent 仓的 `agent/stages/` 和 `agent/prompts/`；overlay Skill、workspace/quest `.codex/skills/` 同步副本只是 Codex 投影或兼容入口，不是 stage authority source。写作、审阅、图件、文献、统计、表格、投稿和数据治理八类高频专业执行默认走本仓八个 `medical-*` skill；这些专业 skill 由本仓维护并同步给 MAS 消费。MAS 继续持有 study truth、artifact authority、owner receipt、typed blocker、human gate、current package 和 publication readiness。本仓不规划 `opl-scholar-write`、`opl-scholar-review` 或 `opl-scholar-display` 作为与这些 skill 并列的默认入口。

当这些 skill 需要能力增强时，可以读取同仓的模块说明、source pack、quality floor、template、candidate refs 或 route-back hints。如果写作、审阅、图件、文献、统计、表格或投稿专业执行质量不足，修复方向是更新本仓对应的 `medical-*` 专业 Skill；如果问题出在阶段判定、证据门槛、route-back、owner gate 或采纳边界，修复方向是 MAS 的 stage operating prompt。

默认 defense 分三段：

- **Stage prompt**：归 MAS `agent/stages/` 与 `agent/prompts/`，负责 stage policy、路由、证据门槛、owner gate、route-back、owner receipt、typed blocker、human gate、publication readiness 和 artifact authority。
- **Professional specialist skill**：默认放在消费它的 domain-agent 仓；只有重型、跨 workspace、或需要独立发布/同步时，才拆到外部 pack。本仓是 MAS 写作、审阅、图件、文献、统计、表格、投稿、数据治理、Display/source refs 和 source packs 的外部 pack 单源。
- **Tool connector**：归 OPL Connect/Fabric 或具体 connector，负责工具/API 调用、标准化只读回执和资源错误；不负责 stage policy、专业判断、owner receipt、typed blocker、human gate、publication readiness 或 artifact authority。

## Runtime Env 关系

MAS Scholar Skills 只声明 dependency intent 与 run-context refs。实际依赖准备、缓存、run-context 生成和 fail-closed doctor 由 OPL runtime environment substrate 处理：

```bash
opl runtime env prepare --domain mas-scholar-skills --profile <profile> --platform <platform> --requirement-profile <path> --paper-root <path> --json
opl runtime env run-context --domain mas-scholar-skills --profile <profile> --json
```

MAS Scholar Skills 自身提供的 bridge 命令只构建 deterministic refs-only envelope，不调用 renderer，不安装依赖，不写 runtime state，不写 artifact body，不签 owner receipt，也不声明 cache hit：

```bash
opl scholar-skills prepare --module <module_id> --profile <profile> --platform <platform> --requirement-profile <path> --paper-root <path> --json
opl scholar-skills run-context --module <module_id> --profile <profile> --json
opl scholar-skills invoke --module <module_id> --input-ref <ref> --artifact-root <ref> --json
opl scholar-skills receipt --module <module_id> --input-ref <ref> --artifact-root <ref> --json
opl scholar-skills materialize --module <module_id> --input-ref <ref> --artifact-root <ref-or-path> --output-root <path> --json
```

`receipt` / `invoke` 返回的 `scholar_skills_receipt_candidate` / `execution_receipt_candidate` 会提供 deterministic `execution_receipt_ref`。所有 active module 共享 `input_fingerprint_ref`、`dependency_profile_ref`、`prepared_run_context_ref`、`source_pack_ref`、`candidate_package_ref`、`execution_receipt_ref`、`owner_gate_handoff_ref`，并按模块追加专业 ref family：Display 使用 `render_cache_ref`、`artifact_manifest_ref`、`visual_audit_or_gallery_preview_ref`、`visual_qa_preview_ref`、`programmatic_figure_audit_ref`、`grayscale_color_vision_check_ref`、`panel_to_code_review_ref`、`complex_heatmap_or_oncoprint_ref`、`figure_table_volume_and_clinical_value_ref`、`figure_polish_alignment_ref`；Tables 使用 `table_manifest_ref`、`table_qc_ref`、`table_shell_ref`、`metric_extraction_ref`、`booktabs_or_minimal_ink_table_ref`、`claim_table_alignment_ref`；Stats 使用 `analysis_manifest_ref`、`analysis_plan_ref`、`effect_size_or_metric_extraction_ref`、`reproducibility_check_ref`、`statistical_review_ref`；Lit 使用 `query_ref`、`citation_manifest_ref`、`source_verification_ref`、`citation_coverage_ref`、`evidence_map_ref`、`metadata_scrape_ref`、`claim_support_ref`、`reference_integrity_floor_ref`；Write 使用 `section_outline_ref`、`reverse_outline_ref`、`claim_evidence_map_ref`、`source_trace_ref`、`unsupported_claim_route_back_ref`、`section_draft_manifest_ref`、`manuscript_body_volume_floor_ref`、`internal_report_prose_route_back_ref`；Review 使用 `reviewer_report_ref`、`adversarial_review_ref`、`revision_action_ref`、`halt_or_revert_rule_ref`、`route_back_ref`、`residual_risk_ref`、`reference_integrity_floor_ref`、`manuscript_body_volume_floor_ref`、`figure_table_volume_and_clinical_value_ref`、`internal_report_prose_route_back_ref`、`figure_polish_alignment_ref`、`registry_descriptive_scientific_boundary_ref`、`submission_declaration_completeness_ref`、`registry_data_lock_enrollment_boundary_ref`、`diagnostic_provenance_caveat_ref`、`figure_caption_content_consistency_ref`、`supplementary_missingness_atlas_ref`、`adult_bmi_sensitivity_ref`；Submit 使用 `submission_checklist_ref`、`journal_rule_ref`、`format_sanity_ref`、`ai_disclosure_ref`、`rebuttal_audit_ref`、`export_package_ref`；Data 使用 `data_manifest_ref`、`dataset_manifest_ref`、`metadata_scrape_ref`、`source_lineage_ref`、`artifact_bundle_manifest_ref`、`data_asset_manifest_ref`、`lifecycle_classification_ref`、`data_dictionary_ref`、`agent_log_aggregation_ref`、`registry_lineage_ref`、`semantic_readiness_ref`、`study_binding_ref`、`privacy_access_tier_ref`、`retention_guardrail_ref`、`storage_tier_ref`、`authoritative_body_boundary_ref`、`derived_copy_inventory_ref`、`analytical_format_strategy_ref`、`cold_restore_proof_ref`、`completed_project_closeout_ref`、`important_result_reproduction_ref`、`data_body_boundary_ref`、`study_impact_ref`、`owner_decision_ref`、`prune_dry_run_ref`、`post_cleanup_readback_ref`、`lifecycle_catalog_ref`、`read_model_boundary_ref`、`lineage_readiness_ref`。这些字段只计为 unsigned candidate artifact refs，显式保持 `counts_as_paper_truth=false`、`counts_as_owner_receipt=false`、`can_authorize_publication_readiness=false`。

Data 的 storage refs 是为大体量医学队列数据准备的最小治理层：`storage_tier_ref` 说明 hot/warm/cold/external 放置理由，`authoritative_body_boundary_ref` 区分权威 release body、interchange 文件和可重建 working copy，`data_asset_manifest_ref` 和 `lifecycle_classification_ref` 把数据体、父级/provenance、paper-facing 现用体、active runtime、语义关闭、字节关闭、可删 cache 与 tombstone 分类机器化；`derived_copy_inventory_ref` 盘点 CSV/SQLite/Parquet/分析抽取/缓存等副本，`analytical_format_strategy_ref` 记录大表查询格式选择，`cold_restore_proof_ref` 要求 cold-store checksum、restore index、owner authorization 和 rehydrate verification，`completed_project_closeout_ref`、`important_result_reproduction_ref`、`data_body_boundary_ref`、`study_impact_ref`、`owner_decision_ref`、`prune_dry_run_ref`、`post_cleanup_readback_ref` 与 `lifecycle_catalog_ref` 则把已完成/停放项目的结果复现路径、审计链、dry-run 和生命周期对象管理统一到一个读面。它们只帮助 MAS/domain owner 判断 retention 和读面效率，不授权 MAS Scholar Skills 移动或删除数据体。

Data lifecycle 状态固定为 `hot_current_body`、`warm_parent_or_provenance`、`paper_facing_current`、`active_runtime`、`semantic_closed`、`byte_closed`、`delete_safe_cache`、`retired_tombstone`。这些是 contract label，不是 owner decision；`owner_decision_ref` 只指向下游 owner 需要签收或拒绝的位置。

已完成项目的数据清理标准是“重要结果可复现 + 可审计”，不要求保留每个中间 runtime 字节。Data 模块应默认建议语义复现迁移：当前 cohort body 保持 hot；能靠文档、source refs、命令和 lineage 重建重要结果时使用 semantic reproducible capsule，并删除被覆盖的 raw history；只有 active analysis、法律/监管、外部交接或 owner 明确要求精确恢复时才保留 byte-level capsule；只有 owner 明确放弃复现时才使用 audit-only tombstone；普通 cache 直接删除。

`materialize` 是 `receipt` candidate 的确定性文件化 surface。它只在显式 `--output-root` 下写出 `manifest.json`、`execution_receipt_candidate.json`、`module_candidate.json`、`refs_manifest.json`，并返回 `surface_kind/status/module_id/input_ref/artifact_root_ref/output_root/output_root_ref/execution_receipt_ref/execution_receipt_candidate_path/module_candidate_path/artifact_manifest_path/written_files/sha256/authority_flags` 等 JSON 字段。`module_candidate.json` 是模块专属的 refs-only candidate payload，包含 module profile、artifact candidate refs、required receipt ref families、quality checklist 和 owner-consumption requirement；八个 active module 都会写出自己的 payload 形状，不再只有通用 refs manifest。该 package 是 refs-only unsigned candidate handoff，不写 runtime DB、domain truth、MAS 文件、owner receipt、typed blocker、paper body 或 artifact body authority；`authority_flags.counts_as_paper_truth`、`authority_flags.counts_as_owner_receipt`、`authority_flags.can_authorize_publication_readiness` 以及相关写权限标志保持 false。

`module_candidate.json` 仍不是 domain authority 的最终结果体：Display 不在这里直接声明可发表图，Stats 不在这里直接声明临床分析结论，Lit 不在这里直接声明文献证据裁决，Submit 不在这里直接声明投稿包 ready。它提供的是 OPL-owned standard handoff payload，使 MAS 等 domain agent 可以用同一消费入口读取候选 refs、质量检查需求和 owner gate 要求；真实图表、分析、文稿、审阅、投稿或数据结果体仍归 domain artifact surface，并必须由 domain owner gate 接收或拒绝。

Display 的 quality floor 现在覆盖通用科研做图，不只 graphical abstract：数据证据图、页面级组合图、graphical abstract / illustration shell 都进入 `scholarskills_scientific_figure_quality_floor.v1`。数据证据图仍优先消费 MAS Display Pack 的 R/ggplot2 证据模板与 paper-local visual audit；graphical abstract 不应复用 gallery 中单个 `submission_graphical_abstract` 作为最终模板。它应走 `brief_first_reference_guided_ai_candidate_not_single_template_reuse`：先锁定核心主张、证据链、figure contract、参考风格和 reviewer rubric，再由 AI 执行者自由选择合适图型、布局、面板层级、backend 和候选数量，最后提供 critic review、final-size inspection、source preservation 和 domain owner gate refs。这样提高质量下限，但不把 MAS Scholar Skills 变成质量 verdict、artifact authority 或 publication-ready owner。

医学 SCI 初稿质量 floor 分布在多个模块：Lit 负责 `reference_integrity_floor_ref`，用于提示缺失参考文献、占位 citation 和 claim/source 覆盖缺口；Write 负责 `manuscript_body_volume_floor_ref` 与 `internal_report_prose_route_back_ref`，用于提示正文体量不足和内部报告式工作流文风；Display 负责 `figure_table_volume_and_clinical_value_ref` 与 `figure_polish_alignment_ref`，用于提示结果图表体量、临床解释价值和新版 figure-polish 技能一致性；Review 汇总为 `scholarskills_medical_sci_initial_draft_quality_floor.v1`，并加入 `registry_descriptive_scientific_boundary_ref`、`submission_declaration_completeness_ref`、`registry_data_lock_enrollment_boundary_ref`、`diagnostic_provenance_caveat_ref`、`figure_caption_content_consistency_ref`、`supplementary_missingness_atlas_ref` 和 `adult_bmi_sensitivity_ref`，用于提示 descriptive registry / atlas 初稿不要把可用性、缺失性、诊断字段阳性或描述性分布写成因果、预测、患病率/负担或 publication-ready 结论，也不要遗漏伦理/知情同意/数据可得性/基金/COI、把 visit-date coverage 写成 enrollment/data-lock、让图注提到未呈现领域，只口头声称 missingness atlas 而不物化补充表，或在有儿童/年龄缺失记录时缺少成人已知年龄 BMI 敏感性表。这些 ref 只能生成 `verdict_candidate`、`route_back_candidate` 和 `stop_or_continue_recommendation`，不能声明 MAS publication ready、owner accepted、typed blocker、current_package authority、quality verdict 或 reviewer receipt。

本轮外部学习只吸收可迁移模式，不导入外部 runtime：`scientific-agent-skills` 的 discoverable skill pack/provenance、`nature-skills` 的 figure contract 与 final QA、PaperVizAgent / PaperBanana 的 reference-driven planner/stylist/visualizer/critic loop、FigMirror 的 reference target + reviewer preserve list、以及极简 plotting skill 的少量硬性出图规则，都落为 Display refs-only quality-floor refs，而不是第二套绘图 agent authority。

新增外部学习同样覆盖 Tables、Stats、Lit、Write、Review、Submit、Data 和 Display 这八个 active module，并落到 refs-only module contract 与 deterministic candidate engine。进度优先：智能体可以先产出 candidate refs/checklists 并继续进入 owner gate；缺少外部 runtime 安装不阻塞推进，除非 owner 明确要求那个 runtime 生成的可执行 artifact。

本轮外部学习还吸收 Parsifal、paper-search-mcp、LocalCitationNetwork、lit-review-orchestrator、AI-Scientist、FAROS 和 AutoR 的可迁移模式。落点是文献筛选/排除理由、检索与 citation graph 证据、local citation-network audit、literature-review orchestration、自动实验/写作流程中的 reviewer loop、route-back budget 和 stop/continue decision pattern；不接入这些项目的 runtime，不把它们变成 MAS authority，也不要求先安装外部服务才能推进 MAS Scholar Skills candidate refs。

MAS 消费 MAS Scholar Skills 时采用 `progress_first_ai_auto_judgment_first`：AI 能根据 evidence refs 判断的内容应尽量自动判断，并输出 AI-consumable evidence、`verdict_candidate`、`route_back_candidate` 和 `stop_or_continue_recommendation`。只有判断会越权到 domain truth、publication readiness、owner receipt、typed blocker、artifact authority、current package authority 或真实 human gate 时，才停止在 MAS Scholar Skills 侧并交给 MAS/domain owner。

FeedbackOps adapter 同样保持 refs-only：`feedbackops_refs_only_adapter_policy` 把 MAS Scholar Skills 声明为 OPL FeedbackOps 的 capability adapter，profile 为 `target_agent_feedback_external_suite`。它可以从 `delivery_feedback_ref` / `feedbackops_intake_ref` 生成 `candidate_refs`、quality hints、Display/Write/Review capability suggestions、`route_back_candidate_ref` 和 `stop_or_continue_recommendation_ref`，供 MAS 或 OMA 作为 evidence input 消费。MAS/OMA 消费后若要签 `owner_receipt_ref`、产出 typed blocker、质量 verdict、artifact mutation 或 current-package update，必须回到各自 owner surface；MAS Scholar Skills 不能写 MAS/current_package，也不能声明 quality verdict、owner acceptance、typed blocker 或 publication readiness。

当 `materialize --emit-candidate-artifacts` 显式启用时，MAS Scholar Skills 会调用八个 OPL-owned deterministic candidate artifact engine，为每个 active module 写出专业候选体、`input_requirements`、`validation_checks`、`engine_receipt_ref` 和 sha256 refs。Display 输出 SVG visual-plan candidate；Write/Review/Submit 输出 Markdown candidate；Tables/Stats/Lit/Data 输出 JSON structured candidate。该 engine 输出比 refs-only body 更接近可消费 artifact，但仍保持 `counts_as_paper_truth=false`、`counts_as_owner_receipt=false`、`can_authorize_publication_readiness=false`、`can_claim_quality_verdict=false`、`can_claim_artifact_authority=false`，不能替代 domain owner consumption。

仓内提供 repo-tracked Codex plugin surface：`.codex-plugin/plugin.json`、`skills/mas-scholar-skills/SKILL.md`，以及真实医学论文专业 Skill `skills/medical-manuscript-writing/SKILL.md`、`skills/medical-manuscript-review/SKILL.md`、`skills/medical-figure-design/SKILL.md`、`skills/medical-research-lit/SKILL.md`、`skills/medical-statistical-review/SKILL.md`、`skills/medical-table-design/SKILL.md`、`skills/medical-submission-prep/SKILL.md`、`skills/medical-data-governance/SKILL.md`。本仓是 MAS Scholar Skills skill pack、module catalog snapshot、医学论文专业 skill 和 gallery review refs 的 source of truth；该 skill pack 把 canonical contract snapshot、CLI readback 入口、AI-first specialist-skill workflow 和 no-authority guard 暴露给 Codex discovery / sync layer。`skills/opl-scholarskills/SKILL.md` 只保留 legacy alias。它不能替代 OPL Framework 中的 executable `opl scholar-skills *` CLI、MAS runtime owner surface、domain owner receipt、typed blocker、runtime evidence 或 paper artifact authority。

## Connect 同步与安装落点

MAS Scholar Skills 的默认消费方是 MAS paper workspace 或 runtime quest 的 local Codex discovery path，而不是用户系统级 Codex skill registry，也不是 MAS 程序仓 `plugins/` mirror。推荐落点是：

```text
<workspace_root>/.codex/skills/mas-scholar-skills/
<workspace_root>/.codex/skills/medical-manuscript-writing/
<workspace_root>/.codex/skills/medical-manuscript-review/
<workspace_root>/.codex/skills/medical-figure-design/
<workspace_root>/.codex/skills/medical-research-lit/
<workspace_root>/.codex/skills/medical-statistical-review/
<workspace_root>/.codex/skills/medical-table-design/
<workspace_root>/.codex/skills/medical-submission-prep/
<workspace_root>/.codex/skills/medical-data-governance/
<quest_root>/.codex/skills/mas-scholar-skills/
<quest_root>/.codex/skills/medical-manuscript-writing/
<quest_root>/.codex/skills/medical-manuscript-review/
<quest_root>/.codex/skills/medical-figure-design/
<quest_root>/.codex/skills/medical-research-lit/
<quest_root>/.codex/skills/medical-statistical-review/
<quest_root>/.codex/skills/medical-table-design/
<quest_root>/.codex/skills/medical-submission-prep/
<quest_root>/.codex/skills/medical-data-governance/
```

该目录是 OPL-managed local discovery copy，只承载消费方会话需要发现的 `SKILL.md`、plugin/module refs、紧凑 gallery review refs 和轻量 manifest。它不是 MAS domain truth、不是 MAS owner receipt、不是 typed blocker、不是 runtime queue，也不是 publication/package authority。不要把本 repo 整仓、MAS 渲染输出、gallery 中间产物或 OPL/MAS 程序源码复制到论文目录或 quest。

OPL Connect 的预期命令是：

```bash
opl connect sync-skills --domain mas-scholar-skills --scope workspace --target-workspace <workspace_root> --json
opl connect sync-skills --domain mas-scholar-skills --scope quest --target-quest <quest_root> --json
```

`workspace` scope 用于论文 workspace 级发现；`quest` scope 用于 runtime quest 级发现。二者都应保持 compact install：只复制 local discovery 和 review 所需 refs，不复制 heavy gallery intermediate outputs。

系统级 Codex 注册仍保留为显式开发者路径：

```bash
opl connect sync-skills --domain mas-scholar-skills --scope codex --json
```

只有显式 `--scope codex` 才写用户 Codex plugin registry / config。旧的 MAS program-repo mirror 只能作为历史迁移或显式开发 surface，不是推荐的 runtime quest discovery surface。App/workbench 若暴露 sync action，应路由到同一 workspace/quest-local install model，并支持 dry-run readback。历史 `--domain scholarskills` 只用于既有工作区兼容；新同步使用 `--domain mas-scholar-skills`。

需要把 module id 绑定到真实 OPL runtime environment substrate 时，使用 runtime bridge 命令。它们复用 `opl runtime env prepare/run-context` 的实现，可在明确 `--apply` 时写入 OPL 管理依赖库和 `paper/build/dependency_environment_lock.json`、`dependency_environment_receipt.json`、`dependency_run_context.json`，但仍不写 domain truth、artifact body、owner receipt、typed blocker 或 runtime queue：

```bash
opl scholar-skills runtime-prepare --module <module_id> --profile <profile> --platform <platform> --requirement-profile <path> --paper-root <path> [--apply] --json
opl scholar-skills runtime-run-context --module <module_id> --profile <profile> --platform <platform> --paper-root <path> --json
```

`prepared_ref_envelope`、`run_context_ref_envelope`、`invocation_ref_envelope`、`receipt_candidate_unsigned`、runtime dependency lock、runtime dependency receipt、bound run-context、`cache hit`、`descriptor exists` 或 `doctor pass` 只能证明 OPL substrate 的结构/读面成立，不能声明 domain ready、runtime ready、quality verdict、artifact authority、owner receipt、typed blocker 或 production ready。

## MAS 消费边界

MAS 可以把八个 active `opl.scholarskills.*` 模块作为 `current_owner_delta` 的 refs-only capability request，桥接到 MAS Scientific Capability Registry 的 candidate artifact refs。Display 仍可复用 MAS Display Pack 的 candidate artifact refs；Tables、Stats、Lit、Write、Review、Submit 和 Data 则通过同一 OPL module descriptor / execution receipt 形状暴露专业候选 refs。但 MAS 仍持有 study truth、publication truth、quality verdict、artifact authority、owner receipt、typed blocker、human gate 和当前 package authority。

目标调用链：

```text
MAS current_owner_delta
  -> OPL Atlas capability discovery
  -> OPL Pack descriptor / contract validation
  -> OPL runtime env prepare / run-context
  -> OPL Runway invocation envelope
  -> candidate artifact refs + execution receipt
  -> MAS owner gate consume / reject
```

当前 OPL 侧落地范围是八个 active module capability catalog、descriptor validation、CLI readback、module-specific refs-only invoke/receipt candidate 与 runtime env bridge refs。真实 domain owner consumption 要回到 MAS 等 domain repo 的 owner surface；OPL 的 unsigned candidate receipt 不会签 owner receipt，也不会把候选图、表、分析、文本、review、submission package 或 data manifest 晋级为论文 truth。

Contract 中的 `accepted_receipt_refs` 只表示 MAS/domain owner 可以消费后返回的 ref family；命名为 `owner_receipt_ref`、`typed_blocker_ref`、`reviewer_receipt_ref` 或 `route_back_evidence_ref` 的字段都不是 MAS Scholar Skills 自己已接受、已签发、已阻断或已授权 publication/current-package readiness 的证据。

## Display Gallery 人审入口

`opl.scholarskills.display` 的人审 gallery 发布包放在本 repo 的 `gallery/medical-display/`，方便安装、运维和审阅时直接打开。该发布包复制自 MAS Display Pack 的最终 docs/gallery surface，只保留 PDF、manifest、reference、status、quality audit 和 snapshot，不复制 MAS 渲染中间目录。

- `gallery/medical-display/medical_display_gallery.pdf`
- `gallery/medical-display/medical_display_gallery_reference.md`
- `gallery/medical-display/display_pack_gallery_status.md`
- `gallery/medical-display/display_pack_gallery_quality_audit.md`
- `gallery/medical-display/gallery_manifest.json`
- `gallery/medical-display/gallery_snapshot.json`

这些 refs 证明有人可审的 Display gallery surface 存在；它们不证明 visual parity 完成、publication-ready、owner accepted 或 MAS paper artifact ready。当前 MAS gallery truth 仍需按 MAS Display Pack owner gate 与 fresh artifact inspection 判定，MAS Scholar Skills 只能把它作为 `visual_audit_or_gallery_preview_ref` 的下游人审入口。

## CLI Readback

```bash
opl scholar-skills list --json
opl scholar-skills inspect --module opl.scholarskills.display --json
opl scholar-skills prepare --module opl.scholarskills.display --profile display --platform macos-arm64 --requirement-profile renderer_dependency_profile.json --paper-root paper --json
opl scholar-skills run-context --module opl.scholarskills.display --profile display --json
opl scholar-skills runtime-prepare --module opl.scholarskills.display --profile display --platform macos-arm64 --requirement-profile renderer_dependency_profile.json --paper-root paper --apply --json
opl scholar-skills runtime-run-context --module opl.scholarskills.display --profile display --platform macos-arm64 --paper-root paper --json
opl scholar-skills invoke --module opl.scholarskills.display --input-ref mas:current_owner_delta/display-intent --artifact-root artifact-root:display-pack-candidates --json
opl scholar-skills receipt --module opl.scholarskills.display --input-ref mas:current_owner_delta/display-intent --artifact-root artifact-root:display-pack-candidates --json
opl scholar-skills materialize --module opl.scholarskills.display --input-ref mas:current_owner_delta/display-intent --artifact-root artifact-root:display-pack-candidates --output-root /tmp/scholarskills-display-candidate --json
opl scholar-skills interfaces --json
opl scholar-skills validate --json
opl scholar-skills doctor --json
```

这些命令是 OPL-owned readback，保持无 domain write、无 runtime state write、无 artifact body mutation、无 owner receipt signing。
