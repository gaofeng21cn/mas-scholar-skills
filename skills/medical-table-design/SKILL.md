---
name: medical-table-design
description: "Use when a MAS medical-paper task needs professional clinical table design, table shell planning, statistical table QA, footnote and abbreviation discipline, table-to-claim alignment, journal-ready table handoff, or refs-only table repair routing. This professional specialist skill is maintained in mas-scholar-skills; MAS keeps study truth, artifact authority, owner receipts, typed blockers, current-package authority, and publication readiness."
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

## External Learning Quality Floor

This skill adapts maintainable patterns from clinical data-presentation,
spreadsheet-quality, statistical-analysis, and Nature-style data workflows:

- preserve existing table conventions when the paper already has a style;
- design the table shell before filling cells;
- keep formulas/statistics traceable to source refs;
- verify denominators, units, decimal places, and footnotes;
- make table claims match manuscript and figure claims;
- keep data availability and source lineage visible without moving authority
  into this skill.
- use K-Dense scientific-writing/statistical-visualization discipline to choose
  a table only when exact values, denominators, subgroup structure, or compact
  multi-metric comparison are more useful than a figure.

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
interpretation needs biomedical literature support, use:

```bash
opl connect pubmed search --query "<query>" --limit <n> --json
```

Record returned `pubmed_source_refs` and
`pubmed_connector_invocation_ref`. The results are candidate refs only; MAS
still decides citation acceptance and manuscript use.

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

For prediction-model external-validation manuscripts, require table shells to
separate three jobs instead of compressing them into prose:

- Table 1: development and validation cohort characteristics, endpoint counts,
  key predictor distributions, units, missingness or available N, and SMD or a
  clear reason SMD cannot be computed;
- Table 2: validation performance, including validation N, event count, mean
  predicted risk, observed risk, C-statistic, O:E, Brier or prediction error,
  calibration intercept/slope, and uncertainty where available;
- grouped calibration table: group or decile, N, events, mean predicted risk,
  observed risk with interval, and O:E or risk difference when it supports the
  central claim.

If development-cohort individual data are unavailable, make the source of
summary statistics explicit and route missing rows to review or human gate
rather than inventing comparable Table 1 cells.

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
- `journal_table_contract_ref`
- `table_repair_actions_ref`
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
