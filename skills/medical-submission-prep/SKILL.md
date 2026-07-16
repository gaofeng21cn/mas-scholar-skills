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

Shared refs: use `docs/no-authority-boundary.md` for owner-boundary limits and
`references/professional-quality-ref-templates.md` for reusable refs-only
quality-floor handoff shapes. Keep specialty details in this skill; do not copy
long boundary or checklist text here.
When MAS supplies `journal_response_pack`, `data_availability_fair_pack`, or
`paper_presentation_pack`, use
`references/professional-quality-ref-templates.md#mas-journal-family-pack-foldback`
to keep response, declaration, package, presentation, and author-input judgment
inside existing professional skills while MAS keeps owner-gate authority.

Optional local helper: `kernel.py` provides deterministic stdlib-only package
manifest, required-document checklist, file-label normalization, and required
document lint helpers. It is refs-only and cannot submit or claim readiness.

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

## AI-First Submission Judgment

Submission prep should judge the package state before formatting it. Decide
whether the paper can proceed to owner review, needs manuscript/statistics/
figure/table/literature/data repair, needs author or institutional input, or
must stop because a package claim would overstate readiness.

Emit `submission_verdict_candidate`, `package_consistency_ref`,
`author_input_needed_ref`, `submission_action_matrix_ref`,
`stop_or_continue_recommendation`, and `route_back_candidate`. These refs are
not submission readiness, journal acceptance, owner receipt, typed blocker,
current-package authority, or publication readiness.

## External Learning Quality Floor

This skill adapts maintainable patterns from Nature-style data availability,
reviewer response, citation, and submission workflows:

- load journal instructions and article type before formatting advice;
- record the current venue instruction source, access date, and template or
  author-guide version before applying rules;
- inventory every required file and declaration;
- separate ready-to-paste text from fields the author must supply;
- map every reviewer response claim to a manuscript location or explicit
  placeholder;
- treat data/code availability and FAIR metadata as submission surfaces, not as
  decorative end matter;
- preserve MAS owner gates for readiness and final submission decisions.
- adapt K-Dense `venue-templates` as an instruction-mapping discipline, not a
  guarantee that a generic template is current or accepted.

Use `professional_ai_quality_floor_ref` for submission-package judgment.
Convert every checklist or reviewer-response critique into
`critique_as_repair_hint_ref` with the affected file, declaration, author field,
journal instruction, citation, figure/table, data/code availability, or response
claim. Use `opportunistic_knowledge_prefetch_ref` only for current venue
instructions, reporting guideline, declaration, source, package, or prior
review refs needed by this package. Add `claim_type_ref` and
`graph_warnings_ref` for package claims that are unsupported, stale, circular,
missing-source, source/body divergent, or inconsistent across manuscript,
figures, tables, supplement, and response files. Use
`annotation_to_source_regeneration_ref` for reviewer comments that must trace
back to manuscript/source refs, and consume `rerun_receipt_ref` only as
re-export, package-check, or reopen-readback evidence.

## Submission Contract

Before preparing the package, create or refresh:

- `journal_instruction_ref`: target journal, article type, word/figure/table
  limits, file format, reporting checklist, and disclosure rules.
- `journal_instruction_source_ref`: official author instruction URL or local
  source, access date, article type, template version when present, and whether
  graphical abstract, highlights, or reporting files are required.
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
2. Read the current journal instructions or accepted local snapshot before
   formatting advice. Do not rely on memory or a generic template when the
   target venue is named.
3. Build a package inventory and classify each item as ready, needs repair,
   needs author input, not applicable, or owner decision needed.
4. Map reporting guideline items to manuscript locations and missing fields.
5. Audit data/code availability, source data, supplementary files, and dataset
   citations. Do not invent DOIs, accession numbers, committees, embargo dates,
   licenses, or repository names.
   For BibTeX-backed exports, protect proper nouns and acronyms that CSL
   sentence-casing may lowercase, such as country/place names, cohort names,
   population labels, tool names, and abbreviations (`{Hong Kong}`,
   `{Nanjing, China}`, `{U.S. adults}`, `{NHANES}`, `{HbA1c}`).
6. Check figures and tables against journal format and manuscript claims. For a
   medical prediction or external-validation paper, absence of supplementary
   tables/figures should be an explicit inventory decision, not a silent
   default; route back when cohort construction details, variable
   ascertainment, additional calibration or sensitivity displays, or
   claim-evidence traceability no longer fit cleanly in the main text.
   When supplementary figures or tables are retained, the human review package
   should expose a readable supplementary PDF and a combined review PDF/DOCX
   when the exporter supports it, rather than leaving only hidden source
   markdown, CSV, or generated image files.
7. Treat
   graphical abstracts or highlights as required only when the venue instruction
   or owner request says so.
8. Check declarations: ethics, consent, trial/registry registration when
   relevant, funding, COI, author contributions, acknowledgments, AI/tool
   disclosure, and data-use restrictions.
9. Draft candidate cover-letter or response-letter material only when source
   instructions and manuscript changes support it.
10. Produce a submission action matrix and owner-gate handoff.

If journal-facing background, reporting-standard, data-sharing, guideline, or
reviewer-response text needs biomedical literature support, route it to MAS
`research-integrity-reference-verification`. Record `mas_provider_lookup_ref`
and `pubmed_source_refs` as candidate refs only; MAS still decides citation
acceptance and manuscript use.

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
- `journal_instruction_source_ref`
- `submission_inventory_ref`
- `reporting_guideline_ref`
- `data_code_availability_ref`
- `declaration_completeness_ref`
- `package_consistency_ref`
- `cover_letter_candidate_ref`
- `reviewer_response_candidate_ref`
- `author_input_needed_ref`
- `submission_action_matrix_ref`
- `claim_type_ref`
- `graph_warnings_ref`
- `annotation_to_source_regeneration_ref`
- `critique_as_repair_hint_ref`
- `opportunistic_knowledge_prefetch_ref`
- `rerun_receipt_ref`
- `input_scope_signature_ref` when exact-input provenance is available
- `route_back_candidate`
- `owner_gate_handoff_ref`

For `input_scope_signature_ref`, use `scope_id=submission_prep` and bind the
exact delivery files and manifest, journal-instruction snapshot,
declarations/checklists, export or reopen QA, and upstream scope digests
consumed by the package; each candidate receipt ref remains only a locator
outside the digest. Build commands, scripts, checkout/model state,
mtimes, and locators remain method provenance unless the explicit review claim
is reproducibility; changing them does not invalidate scientific-scope receipts
when their input bytes are unchanged. A mismatch makes only the prior
`submission_prep` candidate receipt non-reusable; it is not a lock, signature
authority, quality verdict, submission-readiness decision, or global blocker.

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
