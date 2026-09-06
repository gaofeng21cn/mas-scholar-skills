## External Learning Quality Floor

Use this reference for writing-method or reporting-standard decisions that are
not already settled by current accepted context. Fixed sources, license status
and the limits of this adaptation are in [upstream provenance](upstream-provenance.md).

### Current Reporting And Argument Decisions

Select the reporting standard by study design and requested section. The
following official versions were checked on 2026-09-06; consult their current
Explanation & Elaboration and applicable extensions when the task needs an
item-level decision. A local style profile or corpus-derived writing preference
does not replace an official reporting requirement.

| Study or artifact | Current reference and scope |
| --- | --- |
| Randomized trial report | [CONSORT 2025](https://doi.org/10.1136/bmj-2024-081123), 30 items; [official source](https://www.consort-spirit.org/). |
| Randomized trial protocol | [SPIRIT 2025](https://doi.org/10.1136/bmj-2024-081477), 34 items; [official source](https://www.consort-spirit.org/). |
| Clinical prediction model | [TRIPOD+AI 2024](https://doi.org/10.1136/bmj-2023-078378), 27 items for regression and machine learning; [official source](https://www.tripod-statement.org/) states it replaces TRIPOD 2015. The 19-main-item TRIPOD-LLM extension applies to the corresponding biomedical or health LLM study. |
| AI diagnostic accuracy study | [STARD-AI 2025](https://doi.org/10.1038/s41591-025-03953-8), 40 items. Its [2026-07-13 correction](https://doi.org/10.1038/s41591-026-04570-9) adds an omitted committee member and does not change the reporting items. |
| Systematic review | [PRISMA 2020](https://doi.org/10.1136/bmj.n71), published in 2021; [official checklist and resources](https://www.prisma-statement.org/prisma-2020). Select extensions for the actual review design. |

Record coverage and manuscript locations only for applicable items; coverage is
reporting evidence, not a scientific-quality score. Unresolved facts remain
explicitly unresolved. Other designs use their applicable standard, including
STROBE, RECORD or CARE when relevant, rather than being forced into this table.

For a section repair, align the problem posed in the Introduction, the evidence
reported in Results, and the claims in the Abstract and Discussion without
rewriting unrelated sections. Route a factual correction to the evidence/numeric
owner before propagating the corrected accepted record through prose. Keep negative findings,
uncertainty, author contributions and disclosures tied to actual evidence.

This skill absorbs the useful parts of Nature-style writing skills and
K-Dense-style scientific writing skills as MAS-owned writing discipline:

- write the paper argument before writing sentences;
- maintain a terminology ledger before drafting;
- map every paragraph to one job;
- draft from evidence outward;
- use full manuscript prose for final text, not bullet lists;
- treat reporting guidelines, statistics, citations, figures, tables, and data
  availability as writing inputs rather than after-the-fact formatting.

Do not import foreign defaults that conflict with MAS. A MAS medical manuscript
does not need a mandatory graphical abstract, a fixed Nature voice, or extra
figures by default. It needs a defendable medical argument with claim-evidence
traceability.

K-Dense `scientific-writing` contributes only the durable writing discipline:
two-stage outline-to-prose drafting, IMRAD/reporting guideline awareness,
citation-style control, and final full-paragraph manuscript prose. Its mandatory
graphical abstract and high figure-count defaults are rejected unless the target
journal, study charter, or MAS figure contract requires them.

For citation-heavy prose or draft repair, read
`references/professional-quality-ref-templates.md` and use
`claim_citation_quality_loop_ref`. The loop lets AI judge whether a claim should
be kept, downgraded, cited, rewritten, or routed back without turning the draft
into paper truth, owner receipt, typed blocker, or publication readiness.

Also consume `professional_ai_quality_floor_ref` from the same reference when
writing needs AI-first quality control. Treat critique as repair hints:
`critique_as_repair_hint_ref` should name the affected paragraph, claim,
citation, figure, table, or data ref and the narrowest route to repair it.
Extract `reusable_lesson_ref` only for recurring writing or evidence failures,
trigger `triggered_meta_review_ref` when the draft crosses source/statistics/
display/submission boundaries, and use `opportunistic_knowledge_prefetch_ref`
only for immediately needed source, journal, prior-review, table, or figure
refs. When source material permits it, add refs-only `claim_type_ref`,
`graph_warnings_ref`, `annotation_to_source_regeneration_ref`,
`project_local_ledger_pointer_ref`, and `rerun_receipt_ref` to consume local
hashes or rerun evidence without creating MAS truth, owner receipt, typed
blocker, current-package authority, or readiness.

AcademicForge/Claude Science paper-narrative contributes one useful writing
pattern: judge the whole manuscript/figure deck like a handling editor before
adding prose. Use `paper_narrative_arc_ref` from
`references/professional-quality-ref-templates.md` when the draft's story is
unclear: derive the deck arc from the current abstract, intro, captions, and
figure/table claims; identify `fig1_hook_ref`, `figure_moves_ref`,
`missing_panels_ref`, and `kill_list_ref`; then route concrete figure claims to
`medical-figure-design` and prose repairs back into the section contract. This
is editorial judgment and route planning, not publication readiness. The
AcademicForge prompt builders are optional aids; do the editorial pass directly
from the current manuscript and figure refs when no helper is installed.
