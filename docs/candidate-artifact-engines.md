# MAS Scholar Skills Candidate Artifact Engines

Owner: `One Person Lab`
Purpose: 说明 `MAS Scholar Skills` 八个 active 专业模块非权威 candidate artifact body 生成器的 CLI 入口、输出边界和 authority guard。
State: `active_executable_candidate_artifact_engine_surface`
Machine boundary: 本文是人读导航。机器真相以 `src/scholar-skills.ts`、`src/scholar-skills-parts/artifact-engines.ts`、`src/cli/cases/public-command-specs-parts/scholar-skills.ts`、`tests/src/cli/cases/scholar-skills-artifact-engines.test.ts` 与 `opl scholar-skills materialize --json` readback 为准。

## 品牌模块边界

本能力属于 MAS Scholar Skills，也就是 OPL-owned `mas-scholar-skills` 外置增强包；历史 `opl-scholarskills` 只作为 legacy alias 和 provenance。它不新增第十一个 OPL 品牌模块，也不是 MAS specialist skill。

- 主模块：`Pack` 承载 candidate package、manifest、body paths 和 sha256。
- 协同模块：`Atlas` 发现 module descriptor，`Runway` 承载 invocation / execution receipt candidate 形状，`Ledger` 承载 refs、lineage 和 evidence refs，`Console` 读取 CLI JSON readback。
- 不触碰范围：`Connect` / system install surfaces、MAS/Yang/domain authority、runtime DB、runtime queues、owner receipts、typed blockers、publication readiness、domain truth 和 paper truth。

MAS 默认 runtime 入口仍是 MAS overlay，写作、审阅、图件、文献、统计、表格、投稿和临床数据治理的专业 skill 由本仓八个 `medical-*` Skill 单源维护并同步给 MAS 消费。Candidate engines 只为这些入口提供 refs-only candidate bodies、quality floors 和 route-back hints；不新增 `opl-scholar-write/review/display/data` 并列默认入口。

Candidate engine 不是 Skill。当前 active engine 只服务已经有真实专业 Skill 支撑的模块。临床数据治理已经升级为 `medical-data-governance` 真 Skill；历史 Data engine 继续提供 refs-only 候选体和 legacy module descriptor 兼容。通用 source / external-learning intake 归 OPL Framework 或 MAS stage/source surface，不在本仓保留合同占位；组学能力在形成稳定 MAS 专业 workflow 后再以真实 Skill 进入本仓。

## CLI 入口

默认 `materialize` 仍保持 refs-only package：

```bash
opl scholar-skills materialize --module <module_id> --input-ref <ref> --artifact-root <ref-or-path> --output-root <path> --json
```

只有显式 opt-in 时才写非权威 candidate artifact bodies：

```bash
opl scholar-skills materialize --module <module_id> --input-ref <ref> --artifact-root <ref-or-path> --output-root <path> --emit-candidate-artifacts --payload-file <path> --json
opl scholar-skills materialize --module <module_id> --input-ref <ref> --artifact-root <ref-or-path> --output-root <path> --emit-candidate-artifacts --payload-json <json> --json
```

`--payload-json` 与 `--payload-file` 二选一。提供 payload 但没有 `--emit-candidate-artifacts` 会 fail closed；请求 `--emit-candidate-artifacts` 但没有 payload 也会 fail closed。这样可以保证既有 smoke 和 refs-only consumers 不被隐式 artifact body 写入影响。

## Candidate Engine 形状

八个 active module 都会在 `output-root/candidate_artifacts/<profile>/` 下写出 deterministic executable candidate artifact body：

- Display: SVG visual-plan candidate。
- Write / Review / Submit: Markdown draft/report/package candidate。
- Tables / Stats / Lit / Data: JSON structured candidate。

每个 body 都携带模块专属 `engine_id`、`engine_version`、`input_requirements`、`validation_checks`、`engine_receipt_ref`、`payload_sha256`、`body_sha256`、`body_policy=opl_generated_non_authoritative_candidate_body_requires_domain_owner_consumption` 和全 false `authority_flags`。JSON body 的根对象是 `opl_scholarskills_executable_candidate_artifact`；Markdown/SVG body 也会嵌入 engine id、payload hash、owner-gate requirement 和 no-authority boundary。`manifest.json`、`module_candidate.json`、`execution_receipt_candidate.json`、`refs_manifest.json` 和顶层 readback 会记录 `candidate_artifact_bodies[].body_path`、`body_ref`、`body_sha256`、`body_format`、`engine_id`、`engine_receipt_ref`、`validation_status`、`input_requirements`、`body_policy` 与 authority flags。

Candidate body 应优先服务 MAS 的 AI 自动候选判断，而不是把判断默认推给人类。只要 evidence 足够，engine/readback 应暴露 `verdict_candidate`、`route_back_candidate`、`stop_or_continue_recommendation` 和可机读 AI-consumable evidence refs；只有越权到 domain truth、publication readiness、owner receipt、typed blocker、artifact authority、current package authority 或真实 human gate 时才停止在 owner surface。

FeedbackOps 输入走同一 refs-only engine 边界。`target_agent_feedback_external_suite` profile 下，MAS Scholar Skills 可以把 delivery feedback 转成 `candidate_refs`、quality hints、Display/Write/Review capability suggestions、`route_back_candidate_ref` 和 `stop_or_continue_recommendation_ref`；这些 refs 只作为 MAS/OMA 的 `feedbackops_intake_ref` 或 route-back evidence input。MAS/OMA 可以消费它们并在自己的 owner surface 签 owner receipt、typed blocker、quality verdict、artifact mutation 或 current-package update；MAS Scholar Skills engine 不能写 MAS/current_package，不能签 owner receipt，不能创建 typed blocker，也不能 claim quality verdict、owner acceptance 或 publication readiness。

当前八个 engine 是 OPL-owned deterministic candidate builder：

- Display: `scholar_display_candidate_visual_plan_engine`
- Tables: `scholar_tables_candidate_table_manifest_engine`
- Stats: `scholar_stats_candidate_analysis_engine`
- Lit: `scholar_lit_candidate_evidence_map_engine`
- Write: `scholar_write_candidate_section_engine`
- Review: `scholar_review_candidate_report_engine`
- Submit: `scholar_submit_candidate_package_engine`
- Data governance: `scholar_data_candidate_lineage_engine`，由 `medical-data-governance` 专业 Skill 消费和解释。

这些 engine 可以生成更专业的可消费候选体、输入要求、质量检查清单和 receipt metadata；它们不运行 MAS/MAG/RCA domain workflow，不做医学分析裁决，不签 owner receipt，也不把候选体晋级为论文 truth。

八个 active module 共用同一 handoff 骨架：`source_pack_ref` 指向 MAS Scholar Skills / OPL-owned 能力来源或模块说明，`candidate_package_ref` 指向 `materialize` 产生的 refs-only package，`execution_receipt_ref` 指向 unsigned execution receipt candidate，`owner_gate_handoff_ref` 指向 MAS 或 consuming domain owner 的消费入口。Lit、Tables、Stats、Submit、Write、Review 和 Data 与 Display 一样由本仓维护 source / contract / docs，但这些 ref family 都是 no-authority candidate refs，不创建 runtime、owner receipt、typed blocker 或 human gate。

如果 readback 或 manifest 暴露 `owner_receipt_ref`、`typed_blocker_ref`、`reviewer_receipt_ref`、`route_back_evidence_ref` 或 current-package ref，这些字段只说明下一跳 owner-consumption 需要读写的目标 ref family；它们不能被解释为 engine acceptance、typed blocker creation、publication readiness 或 current package authority。

## 单模块外部学习落点

本轮只吸收外部 repo 的可迁移 ref shape 和质量检查要求，不接入外部 runtime，也不让 MAS Scholar Skills 成为 domain truth owner。

- Display 从 `Haojae/scipilot-figure-skill`、`littlepeachs/NaturePanelForge`、`Marsilea-viz/marsilea` 和 `Boom5426/Awesome-Virtual-Cell` 吸收 `visual_qa_preview_ref`、`programmatic_figure_audit_ref`、`grayscale_color_vision_check_ref`、`panel_to_code_review_ref`、`complex_heatmap_or_oncoprint_ref`，并为医学 SCI 初稿提供 `figure_table_volume_and_clinical_value_ref`、`figure_polish_alignment_ref`。
- Tables 从 `Master-cai/Research-Paper-Writing-Skills`、`Ar9av/PaperOrchestra` 和 Papers-with-Code/SOTA result registry patterns 吸收 `table_shell_ref`、`metric_extraction_ref`、`booktabs_or_minimal_ink_table_ref`、`table_qc_ref`、`claim_table_alignment_ref`、`dataset_metric_benchmark_ref` 和 `result_metric_registry_ref`。
- Stats 从 `Ar9av/PaperOrchestra`、`Imbad0202/academic-research-skills` 和 Papers-with-Code/SOTA result registry patterns 吸收 `analysis_plan_ref`、`effect_size_or_metric_extraction_ref`、`reproducibility_check_ref`、`statistical_review_ref`、`dataset_metric_benchmark_ref` 和 `result_metric_registry_ref`；Stats 不能 claim statistical conclusion。
- Lit 从 `Imbad0202/academic-research-skills(-codex)`、`Ar9av/PaperOrchestra`、`Future-Scholars/paperlib`、`vitorfs/parsifal`、`openags/paper-search-mcp`、`LocalCitationNetwork` 和 `kennethkhoocy/lit-review-orchestrator` 吸收 `query_ref`、`citation_manifest_ref`、`source_verification_ref`、`citation_coverage_ref`、`evidence_map_ref`、`metadata_scrape_ref`、`claim_support_ref`、`systematic_review_protocol_ref`、`inclusion_exclusion_criteria_ref`、`data_extraction_schema_ref`、`quality_appraisal_ref`、`citation_graph_snowball_ref`、`multi_source_paper_search_ref`、`confirm_or_drop_source_verification_ref` 和 `reference_integrity_floor_ref`。
- Write 从 `Master-cai/Research-Paper-Writing-Skills`、ARS、PaperOrchestra 和 `kennethkhoocy/lit-review-orchestrator` 吸收 `section_outline_ref`、`reverse_outline_ref`、`claim_evidence_map_ref`、`source_trace_ref`、`unsupported_claim_route_back_ref`、`section_draft_manifest_ref`、`confirm_or_drop_source_verification_ref`、`manuscript_body_volume_floor_ref` 和 `internal_report_prose_route_back_ref`。
- Review 从 ARS reviewer、PaperOrchestra refinement 和 `kennethkhoocy/lit-review-orchestrator` 吸收 `reviewer_report_ref`、`adversarial_review_ref`、`revision_action_ref`、`halt_or_revert_rule_ref`、`route_back_ref`、`residual_risk_ref`、`confirm_or_drop_source_verification_ref`，并以 `scholarskills_medical_sci_initial_draft_quality_floor.v1` 聚合 `reference_integrity_floor_ref`、`manuscript_body_volume_floor_ref`、`figure_table_volume_and_clinical_value_ref`、`internal_report_prose_route_back_ref`、`figure_polish_alignment_ref`、`registry_descriptive_scientific_boundary_ref`、`pdf_nonblank_figure_export_qc_ref`、`journal_figure_numbering_ref`、`wide_table_routing_ref` 和 `discussion_theme_compression_ref`。
- Submit 从 ARS disclosure/format/rebuttal 和 PaperOrchestra LaTeX sanity 吸收 `submission_checklist_ref`、`journal_rule_ref`、`format_sanity_ref`、`ai_disclosure_ref`、`rebuttal_audit_ref`、`export_package_ref`；Submit 不能 authorize publication readiness。

新增学习源只学 pattern，不接 runtime：Parsifal 提供 systematic-review protocol、screening decision 和 exclusion reason 形状；paper-search-mcp 提供可机读 search/query/source refs；LocalCitationNetwork 提供 citation graph、seed-paper expansion 和 local network audit 形状；lit-review-orchestrator 提供 literature workflow orchestration、gap map 和 handoff refs；AI-Scientist、FAROS、AutoR 提供自动实验/写作/review loop 的 `verdict_candidate`、`route_back_candidate`、budgeted retry 和 stop/continue decision pattern。MAS Scholar Skills engine 只把这些模式转成 deterministic candidate bodies 和 AI-consumable evidence，不安装或调用外部 runtime。

## Data Storage Candidate Refs

Data candidate body 应优先暴露 `data_manifest_ref`、`dataset_manifest_ref`、`metadata_scrape_ref`、`source_lineage_ref`、`artifact_bundle_manifest_ref`、`data_asset_manifest_ref`、`lifecycle_classification_ref`、`data_dictionary_ref`、`agent_log_aggregation_ref`、`data_governance_handoff_ref`、`data_governance_assessment_ref`、`data_operation_receipt_ref`、`manifest_completeness_check_ref`、`privacy_tier_check_ref`、`study_impact_check_ref`、`privacy_access_tier_ref`、`retention_guardrail_ref`、`storage_tier_ref`、`authoritative_body_boundary_ref`、`derived_copy_inventory_ref`、`analytical_format_strategy_ref`、`cold_restore_proof_ref`、`read_model_boundary_ref`、`systematic_review_protocol_ref`、`inclusion_exclusion_criteria_ref`、`data_extraction_schema_ref`、`quality_appraisal_ref`、`dataset_metric_benchmark_ref`、`result_metric_registry_ref`、`important_result_reproduction_ref`、`data_body_boundary_ref`、`study_impact_ref`、`owner_decision_ref`、`post_cleanup_readback_ref`、`prune_dry_run_ref` 和 `lifecycle_catalog_ref`。这些 refs 借鉴 paper library 的 metadata/source organization、data package resource inventory、FAIR metadata discipline、`vitorfs/parsifal` 的 SLR protocol / criteria / extraction / appraisal shape，以及 Papers-with-Code/SOTA result registry patterns；它们只作为 domain owner gate 的候选输入。

AI 可以基于上述 refs 自动产出 `verdict candidate` 或 `route-back candidate`，例如来源是否 confirm/drop、指标是否缺失 registry 映射、SLR 抽取表是否缺 appraisal 字段；这些 judgment 仍然是 refs-only candidate，不能签 domain truth、owner receipt、quality verdict、publication readiness 或 runtime readiness。

Data operation receipt category 固定为 `ingest`、`clean`、`deidentify`、`normalize`、`update`、`diff`、`release`、`retire` 之一；Data engine 同时应暴露 `manifest_completeness_declared`、`privacy_access_tier_declared`、`study_impact_declared`、`operation_receipt_category_declared`、`legacy_opl_scholarskills_data_alias_only` 和 `no_authority_flags_false`。这些字段是 assessment checks，不是 source readiness verdict。

医学 SCI 初稿 candidate body 可以基于新增 quality-floor refs 自动提示引用完整性、正文体量、图表体量与临床价值、内部报告式文风、figure-polish skill 一致性和 registry/descriptive 科学边界。若证据不足，输出最小 `route_back_candidate`，指向 Lit/Write/Display/Review 的下游 owner gate；不得把这些检查升级成 MAS publication ready、owner accepted、typed blocker、current_package authority 或 reviewer receipt。

对于医学队列数据，Data engine 的存储候选体必须把受限原始层、去标识 source-semantic 层、分析冻结层、study-local 派生物、runtime/cache 残留分开表达。CSV、SQLite、DuckDB 或 Parquet 可以是高效分析布局，但除非 domain manifest 明确升级，它们不能互相覆盖 source of truth；任何 dataset body 下线都需要 cold-store checksum、restore index、owner authorization 和 rehydrate verification。

Data lifecycle contract 使用固定状态：`hot_current_body`、`warm_parent_or_provenance`、`paper_facing_current`、`active_runtime`、`semantic_closed`、`byte_closed`、`delete_safe_cache`、`retired_tombstone`。`prune_dry_run_ref` 和 `post_cleanup_readback_ref` 只能证明候选清理计划和读回存在，不能证明删除授权、owner receipt 或 domain truth 已更新。

## Authority Guard

这些 body 是 OPL-generated candidate artifacts，只能作为 domain owner gate 的输入或 handoff refs。它们不能声明：

- paper truth / domain truth；
- owner receipt / typed blocker；
- quality verdict / artifact authority；
- publication readiness / runtime ready / production ready；
- runtime DB、runtime queue、MAS/Yang 或 domain repo 写入。

`artifact_body_written=true` 只表示当前 `output-root` 内写了非权威 candidate body 文件；它不改变 `can_mutate_artifact_body=false`，也不授权任何 domain-owned artifact mutation。
