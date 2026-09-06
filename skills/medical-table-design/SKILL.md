---
name: medical-table-design
description: "Design and audit medical manuscript tables, including shells, denominators, units, source traceability, footnotes and claim alignment."
---

# Medical Table Design

Use this skill when a MAS paper needs a new table, a repaired table shell, or a
table quality review before writing, review, figure, statistics, or submission
handoff.

This professional specialist skill is maintained in `mas-scholar-skills` /
MAS Scholar Skills. MAS stage operating prompts may sync and consume it, while
MAS still owns stage routing, study truth, table artifacts, evidence ledgers,
owner receipts, typed blockers, human gates, current packages, and publication
readiness.

Shared refs: use `docs/no-authority-boundary.md` for owner-boundary limits and
`references/professional-quality-ref-templates.md` for reusable refs-only
quality-floor handoff shapes. Keep specialty details in this skill; do not copy
long boundary or checklist text here.
When MAS supplies `figure_evidence_contract_pack` and the right surface is a
table or source-data/statistics audit, consume
`references/professional-quality-ref-templates.md#mas-journal-family-pack-foldback`.
Return table/source metric candidate refs and route visual display work back to
`medical-figure-design`.

Optional local helper: `kernel.py` provides deterministic stdlib-only table
shell, column normalization, footnote/completeness lint, and numeric-format
hints. It is refs-only and cannot create artifacts or claim readiness.

Sibling skill routes are `medical-statistical-review` for statistical judgment,
`medical-manuscript-writing` for text/table narrative binding,
`medical-manuscript-review` for full-paper critique, and
`medical-figure-design` for visual displays, `medical-submission-prep` for
submission-facing table package checks, and `medical-data-governance` for
clinical data manifests, source readiness support, version impact,
privacy/access tiers, and lifecycle guardrails.

## Core Rule

Tables are evidence compression surfaces. A good medical table should make the
reader understand cohort, comparisons, estimates, uncertainty, and limitations
without turning the table into a data dump.

Do not create a table until the table job is clear. Do not use formatting to hide
uncertain denominators, missing units, unsupported comparisons, or weak claims.

## AI-First Table Judgment

The skill should decide whether a table is the right evidence surface, whether
it belongs in main text or supplement, whether a figure or prose sentence is
clearer, and whether a negative/equivocal result needs visible table support.
Emit `table_verdict_candidate`, `table_vs_figure_decision_ref`,
`claim_table_alignment_ref`, `table_repair_actions_ref`, and
`route_back_candidate` when source metrics, denominators, or claim alignment
are not defensible.

These judgments are candidate handoff refs only. MAS or the consuming owner
must still accept, reject, mutate, or route the table through its authority
surface.

## Method References

When the task needs a method, reporting-standard, source or quality detail beyond the current accepted context, load [method quality reference](references/method-quality-reference.md). Reuse applicable current evidence; load only resources needed by the selected task mode.

## Table Contract

Before drafting a table, create or refresh:

- `table_job_ref`: baseline description, cohort flow, primary outcome,
  model result, sensitivity result, missingness atlas, supplementary support, or
  submission checklist.
- `table_vs_figure_decision_ref`: why the information belongs in a table,
  figure, supplement, or prose.
- `table_shell_ref`: rows, columns, stratification, units, denominator columns,
  footnotes, abbreviations, and statistic display format.
- `source_metric_ref`: source table/model/output refs for every metric.
- `denominator_ref`: N, available N, missing N, analysis set, and exclusions.
- `statistical_display_ref`: estimate, uncertainty, p-value policy, effect-size
  display, and multiplicity note when relevant.
- `claim_table_alignment_ref`: which manuscript claim each table supports.
- `journal_table_contract_ref`: target location, editable format, title, notes,
  and supplementary-vs-main placement.

If source metrics or denominators are unclear, route to
`medical-statistical-review`, `medical-manuscript-review`, `analysis-campaign`,
or a MAS owner gate before producing final-looking tables.

For eligible percentages, candidate percentages, resolved percentages, and
absolute flagged counts, consume `denominator_semantics_matrix_ref`. Every
metric must expose its numerator, denominator ref, denominator role, formula,
unit, and visual semantic in the shell or footnote contract. Two percentages
may share one real denominator when those declarations are explicit and
self-consistent. Do not place a percent and an absolute count under the same
visual semantic or unit, and do not describe absolute flagged-record volume as
measured workload.

Before owner handoff, produce `final_embedding_readability_ref` for the actual
journal-width table or composed PDF page. Check font size, wrapping, hierarchy,
footnotes, and scanability at final embedding size. Programmatic non-overflow is
necessary but cannot substitute for human-readable final-size inspection.

## Main-Table Information Budget

Every main-text table should answer one reader question.
Treat templates and gallery examples as a reference quality floor, not as a
required layout or a substitute for professional judgment. A table may use a
new shell when its
reader question or data structure does not fit an existing template, but it
must still consume this Skill and document the information-budget decision.

Use these defaults as a review trigger rather than a universal journal law:

- at most 15 body rows and 8 columns, including the row-label column;
- at most 350 body words and 24 words in the longest body cell;
- at most 45 words of reader-visible footnotes;
- one explicit reader question and one final embedded page.

An over-budget main table should normally become a compact reader-facing
projection with the complete matrix, audit inventory, subgroup detail, or
sensitivity grid moved to a named supplementary table. A journal-specific or
table-specific exception is allowed only when it remains readable at final
size and the handoff states why compression would obscure the clinical
comparison. Do not satisfy the budget by shrinking text, abbreviating beyond
recognition, deleting denominators, or hiding uncertainty.

Produce `main_table_information_budget_ref` for every main table with its role,
reader question, row and column counts, body-word count, longest-cell word
count, footnote-word count, supplementary-detail refs, and final embedded page
span. Run `lint_main_table_information_budget()` before handoff. The lint emits
refs-only quality debt; MAS decides whether to continue, route back, or accept a
documented exception.

## Workflow

1. Identify the table's job and manuscript location.
2. Choose the minimum useful table type: baseline, cohort flow, result summary,
   model coefficient, subgroup, sensitivity, missingness, data dictionary, or
   submission/admin table.
3. Decide whether the exact values and denominators need a table, or whether a
   figure or prose sentence is the clearer display.
4. Define row and column grammar before values are inserted.
5. Bind every metric to `source_metric_ref` and every denominator to
   `denominator_ref`.
6. Normalize units, decimal places, effect-size display, p-value policy,
   confidence intervals, and missingness notation.
7. Add abbreviations and footnotes only where they remove ambiguity.
8. Check text/table/figure consistency.
9. Produce a candidate table manifest and route-back list.

If a table note, benchmark, guideline, endpoint definition, or clinical
interpretation needs biomedical literature support, route it to
`medical-research-lit`. Record `opl_connect_search_ref`,
`opl_connect_reference_verification_ref`, and `pubmed_source_refs` as candidate
refs only. OPL Connect owns provider transport and receipts; MAS still decides
medical support strength, citation acceptance, and manuscript use.

## Quality Checks

Check:

- title says what the table contains, not what the authors hope it proves;
- all denominators are visible or recoverable;
- percentages have clear denominators;
- units and transformations are explicit;
- p-values are not used as the only evidence and are paired with effect sizes or
  uncertainty when inferential;
- CI/SE/SD/IQR choices match the statistic;
- p-value and multiplicity policy is stated when relevant;
- abbreviations are defined once and used consistently;
- table body avoids internal workflow labels and runtime names;
- main tables are not overloaded with supplementary-only detail.
- every main table has one reader question and an explicit information-budget
  assessment at final embedding size;
- complete detail removed from a compact main table remains available through
  a named supplementary-detail ref.

## Journal Footnote Discipline

Reader-visible table notes should explain the table, not reproduce the paper's
Methods, Limitations, generation ledger, or authority boundary.

- Do not render a standalone `Notes` heading for a routine main table. Use a
  compact unlabelled general footnote or keyed footnotes only when needed.
- Keep main-table notes to zero to two concise items by default. More than two
  requires a table-specific or journal-specific reason and should be returned as
  a quality-debt finding until justified.
- Use notes only for denominators, statistical display format, abbreviations,
  missingness or `NA` semantics, and one essential anti-misinterpretation guard
  that is necessary to read that table correctly.
- State global estimand definitions, study-wide caveats, ascertainment limits,
  and non-causal interpretation once in Methods or Limitations. Do not copy the
  same long disclaimer below multiple tables.
- Keep generation IDs, source hashes, runtime state, owner/authority flags, and
  submission-readiness metadata in manifests or receipts, never in
  reader-facing table Markdown, DOCX, PDF, or XLSX notes.
- Prefer one unnumbered general note plus a compact abbreviation line when no
  table cell uses a specific footnote marker. Numbered lists are not a substitute
  for real cell-level footnote markers.
- Supplementary tables may retain table-specific operational detail, but notes
  should still be concise; move full algorithms, model specifications, and
  sensitivity inventories to Methods or dedicated supplementary prose.

Run `lint_table_note_inventory()` before handoff. Treat overloaded notes,
repeated long notes, and internal audit metadata as repairable candidate quality
debt. This deterministic lint does not decide table acceptance or publication
readiness.

For prediction-model external validation, load [external-validation tables](references/external-validation-tables.md). Table numbers are template positions; preserve each table's scientific job and use the manuscript's actual numbering.

For phenotype-atlas comparisons, load [registry tables](references/registry-tables.md). Choose numbering and layout for the current manuscript rather than requiring a literal Table 2.

## Handoff Shape

Return refs-only candidate output:

- `table_job_ref`
- `table_vs_figure_decision_ref`
- `table_shell_ref`
- `source_metric_ref`
- `denominator_ref`
- `statistical_display_ref`
- `table_qc_ref`
- `claim_table_alignment_ref`
- `claim_type_ref`
- `graph_warnings_ref`
- `annotation_to_source_regeneration_ref`
- `critique_as_repair_hint_ref`
- `triggered_meta_review_ref`
- `rerun_receipt_ref`
- `journal_table_contract_ref`
- `main_table_information_budget_ref`
- `supplementary_detail_ref`
- `table_repair_actions_ref`
- `baseline_table_traceability_ref` when Table 1 is present
- `route_back_candidate`
- `owner_gate_handoff_ref`

## MAS Boundary

This skill can prepare candidate table shells, table manifests, QC notes, and
route-back refs where the workspace permits candidate material. It must not
write MAS table authority, paper truth, owner receipts, typed blockers, human
gates, publication eval, current package authority, runtime queues, or provider
attempts.

Do not claim table acceptance, artifact authority, quality verdict, owner
acceptance, submission readiness, or publication readiness. MAS or the domain
owner must consume the refs and issue any owner receipt, typed blocker,
route-back, artifact mutation, or publication decision.
