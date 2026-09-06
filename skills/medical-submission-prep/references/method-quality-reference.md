## External Learning Quality Floor

Fixed learning revisions, current source status and license boundaries are in
[upstream provenance](upstream-provenance.md). Use this reference only for the
submission, reporting, availability or response issue currently in scope.

### Venue, Reporting And Availability Decisions

Resolve the exact journal, article type and submission stage from the current
package. Initial submission, revision and final production can have different
requirements. Official instructions and author-specified requirements outrank
corpus-derived style preferences; a generic or locally adapted template is not
an official current template. Preserve its actual source date and version rather
than changing a filename's year to imply a refresh.

Select reporting guidance by design. Versions checked on 2026-09-06 are
[CONSORT 2025](https://doi.org/10.1136/bmj-2024-081123) for randomized trial
reports, [SPIRIT 2025](https://doi.org/10.1136/bmj-2024-081477) for trial
protocols, [TRIPOD+AI 2024](https://doi.org/10.1136/bmj-2023-078378) for
regression or machine-learning clinical prediction models,
[STARD-AI 2025](https://doi.org/10.1038/s41591-025-03953-8) for AI diagnostic
accuracy, and [PRISMA 2020](https://doi.org/10.1136/bmj.n71) for systematic
reviews. TRIPOD+AI replaces TRIPOD 2015; the TRIPOD-LLM extension is specific to
applicable biomedical/health LLM studies. STARD-AI's
[2026 correction](https://doi.org/10.1038/s41591-026-04570-9) adds a committee
member without changing the reporting items. Use official Explanation &
Elaboration and appropriate extensions when needed. Reporting coverage does
not certify methodological quality; other designs retain their own standards.

Inventory supporting data and code by their actual access route: public,
controlled, within the paper, reused, restricted, justified request or not
applicable. Map each item to its location and real stable identifier when one
exists. Do not invent accession numbers, repository DOIs, ethics approvals,
committee names, consent or embargo terms. A justified request-only route can
be legitimate; check the real restriction and target journal's policy.

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
