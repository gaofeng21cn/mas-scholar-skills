---
name: opl-scholarskills
description: "Legacy compatibility alias for MAS Scholar Skills. Use only when an existing workspace still references opl-scholarskills; for new MAS medical-paper work prefer mas-scholar-skills plus the real skill sources medical-manuscript-writing, medical-manuscript-review, medical-figure-design, medical-research-lit, medical-statistical-review, medical-table-design, and medical-submission-prep."
---

# OPL ScholarSkills Legacy Alias

This is a compatibility entry for existing local Codex installs that still reference `opl-scholarskills`.

For new work, use:

- `mas-scholar-skills` for the aggregate MAS Scholar Skills capability map.
- `medical-manuscript-writing` for medical manuscript writing and revision.
- `medical-manuscript-review` for adversarial medical review and route-back.
- `medical-figure-design` for medical manuscript figures.
- `medical-research-lit` for PubMed-oriented literature discovery.
- `medical-statistical-review` for statistical assumptions, estimands,
  denominator/missingness checks, effect sizes, and route-back.
- `medical-table-design` for clinical table shells, table QC, denominators,
  footnotes, and table-to-claim alignment.
- `medical-submission-prep` for journal instructions, declarations, reporting
  checklists, data/code availability, reviewer response, and package audit.

Do not treat this alias as a separate source of truth. The canonical repository and plugin name is `mas-scholar-skills`; the writing, review, figure, literature, statistics, table, and submission professional skills are maintained there and synced for MAS consumption.
