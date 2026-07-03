---
name: medical-submission-prep
description: "Use when a MAS medical-paper task needs professional submission preparation, journal instruction mapping, reporting-guideline checklist, title page and declaration inventory, data/code availability statement planning, cover-letter or reviewer-response package audit, export package QA, or refs-only submission route-back. This professional specialist skill is maintained in mas-scholar-skills; MAS keeps artifact authority, owner receipts, typed blockers, human gates, current-package authority, and publication readiness."
---

# Medical Submission Prep

Use this skill when a MAS paper needs submission-package preparation or a
pre-submission audit after the manuscript, figures, tables, and evidence package
are substantially assembled.

This professional specialist skill is maintained in `mas-scholar-skills` /
MAS Scholar Skills. MAS stage operating prompts may sync and consume it, while
MAS still owns stage routing, study truth, submission artifacts, publication
eval, controller decisions, owner receipts, typed blockers, human gates, current
packages, and publication readiness.

Sibling skill routes are `medical-manuscript-writing` for manuscript text,
`medical-manuscript-review` for adversarial critique,
`medical-table-design` for tables, `medical-figure-design` for figures, and
`medical-research-lit` for biomedical source support,
`medical-statistical-review` for statistical checklist and reporting issues,
and `medical-data-governance` for clinical data manifests, source readiness
support, version impact, privacy/access tiers, and lifecycle guardrails.

## Core Rule

Submission prep is a completeness and consistency workflow, not a publication
verdict. It turns a near-complete paper into an owner-reviewable package:
manuscript files, declarations, reporting checklist, data/code availability,
figures/tables, supplementary files, cover letter, reviewer response when
relevant, and route-back actions.

Do not say a paper is ready because a checklist is filled. Use the checklist to
find missing owner decisions, missing files, unsupported claims, and mismatched
package parts.

## External Learning Quality Floor

This skill adapts maintainable patterns from Nature-style data availability,
reviewer response, citation, and submission workflows:

- load journal instructions and article type before formatting advice;
- inventory every required file and declaration;
- separate ready-to-paste text from fields the author must supply;
- map every reviewer response claim to a manuscript location or explicit
  placeholder;
- treat data/code availability and FAIR metadata as submission surfaces, not as
  decorative end matter;
- preserve MAS owner gates for readiness and final submission decisions.

## Submission Contract

Before preparing the package, create or refresh:

- `journal_instruction_ref`: target journal, article type, word/figure/table
  limits, file format, reporting checklist, and disclosure rules.
- `submission_inventory_ref`: manuscript, title page, abstract, figures, tables,
  supplement, cover letter, highlights, graphical abstract, ethics, consent,
  funding, COI, author contributions, data/code availability, acknowledgments,
  and reviewer-response files when relevant.
- `reporting_guideline_ref`: STROBE, CONSORT, PRISMA, TRIPOD, RECORD, CARE, or
  study-specific checklist and item-level status.
- `data_code_availability_ref`: dataset inventory, repository/access route,
  accession/DOI placeholders, restrictions, code availability, and unresolved
  author fields.
- `package_consistency_ref`: title/abstract/main text/figures/tables/supplement
  consistency checks.
- `author_input_needed_ref`: fields that require a human or institutional owner.

If journal instructions, declarations, or owner-supplied metadata are missing,
produce route-back rather than inventing content.

## Workflow

1. Identify target journal, article type, submission stage, and whether this is
   first submission, revision, resubmission, or appeal-like.
2. Build a package inventory and classify each item as ready, needs repair,
   needs author input, not applicable, or owner decision needed.
3. Map reporting guideline items to manuscript locations and missing fields.
4. Audit data/code availability, source data, supplementary files, and dataset
   citations. Do not invent DOIs, accession numbers, committees, embargo dates,
   licenses, or repository names.
5. Check figures and tables against journal format and manuscript claims.
6. Check declarations: ethics, consent, trial/registry registration when
   relevant, funding, COI, author contributions, acknowledgments, AI/tool
   disclosure, and data-use restrictions.
7. Draft candidate cover-letter or response-letter material only when source
   instructions and manuscript changes support it.
8. Produce a submission action matrix and owner-gate handoff.

If journal-facing background, reporting-standard, data-sharing, guideline, or
reviewer-response text needs biomedical literature support, use:

```bash
opl connect pubmed search --query "<query>" --limit <n> --json
```

Record returned `pubmed_source_refs` and
`pubmed_connector_invocation_ref`. The results are candidate refs only; MAS
still decides citation acceptance and manuscript use.

## Reviewer Response Mode

When reviewer comments or editor letters are present:

- extract editor instructions and reviewer comments into stable IDs;
- preserve each comment before responding;
- classify comments by action: text repair, analysis repair, figure/table
  repair, citation repair, disagreement, impossible request, or author input;
- map every claimed change to manuscript location, figure/table/supplement
  ref, or an explicit placeholder;
- mark missing author information as `AUTHOR_INPUT_NEEDED`;
- route statistical, literature, writing, table, and figure repairs to sibling
  skills instead of pretending the response letter itself fixes the paper.

## Handoff Shape

Return refs-only candidate output:

- `journal_instruction_ref`
- `submission_inventory_ref`
- `reporting_guideline_ref`
- `data_code_availability_ref`
- `declaration_completeness_ref`
- `package_consistency_ref`
- `cover_letter_candidate_ref`
- `reviewer_response_candidate_ref`
- `author_input_needed_ref`
- `submission_action_matrix_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

## MAS Boundary

This skill can prepare submission checklists, declaration inventories, candidate
cover-letter text, reviewer-response drafts, and route-back refs where the
workspace permits candidate material. It must not submit files, mutate MAS
publication eval, write controller decisions, sign owner receipts, create typed
blockers, create human gates, update current package authority, write runtime
queues, or claim publication readiness.

Do not claim submission readiness, publication readiness, quality verdict,
owner acceptance, artifact authority, or journal acceptance. MAS or the domain
owner must consume the refs and issue any owner receipt, typed blocker,
route-back, artifact mutation, or final submission decision.
