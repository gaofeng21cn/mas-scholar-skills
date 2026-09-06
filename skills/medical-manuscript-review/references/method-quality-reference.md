## External Learning Quality Floor

Load this reference for the active review question; fixed revisions, licenses
and historical source status are in [upstream provenance](upstream-provenance.md).

### Evidence And Reporting Review

Separate reporting completeness from methodological validity. Check the central
claim first; a substantive concern should identify its location, observation,
supporting evidence, consequence and proportionate repair. A new experiment is
one possible repair when a central claim requires it; narrowing the claim,
explaining a limitation or adding a supported sensitivity analysis may be enough.
Missing input can support a bounded review with named limits.

For an applicable reporting audit, use the current official standard rather
than a fixed journal recipe. Versions checked on 2026-09-06 are
[CONSORT 2025](https://doi.org/10.1136/bmj-2024-081123) for randomized trial
reports and [SPIRIT 2025](https://doi.org/10.1136/bmj-2024-081477) for their
protocols; [TRIPOD+AI 2024](https://doi.org/10.1136/bmj-2023-078378) for
clinical prediction models, replacing TRIPOD 2015 for regression and machine
learning; [STARD-AI 2025](https://doi.org/10.1038/s41591-025-03953-8) for AI
diagnostic accuracy; and [PRISMA 2020](https://doi.org/10.1136/bmj.n71) for
systematic reviews. STARD-AI's [2026 correction](https://doi.org/10.1038/s41591-026-04570-9)
only adds a committee member. Use the relevant Explanation & Elaboration and
extensions from [CONSORT/SPIRIT](https://www.consort-spirit.org/),
[TRIPOD](https://www.tripod-statement.org/) or
[PRISMA](https://www.prisma-statement.org/prisma-2020) when needed. Other study
designs retain their applicable reporting framework.

If independent reviewer lanes are requested and permitted, give each the same
frozen source package and scope, finish its own findings before synthesis, and
do not share other reviewers' conclusions as the initial fact base. No fixed
reviewer count follows from these upstream examples. Separate scientific
comments for authors from genuinely confidential editorial-process concerns.

For statistical claims, distinguish measured units, analysis units and the
population of inference; account for dependence, nesting and multiplicity.
An interaction needs evidence about the difference, not a comparison of two
separate significance labels. Confidence and prediction intervals answer
different questions. Overlapping error bars alone establish neither no
difference nor equivalence; a p-value is not the probability an effect exists.
Apply the accepted analysis contract and route a disputed scientific standard
to its owner instead of changing kernel thresholds through review prose.

This skill absorbs useful reviewer patterns from Nature-style reviewer skills
and K-Dense-style peer-review skills:

- extract a shared manuscript fact base before judging;
- evaluate significance, originality, technical soundness, readability, and
  audience fit separately;
- simulate multiple reviewer emphases when that helps identify hidden risk;
- consolidate findings into a cross-review synthesis instead of averaging them
  away;
- tie every major concern to a route-back action and owner surface.

Use these patterns as stricter review discipline, not as a foreign journal
verdict. The skill may say a Nature-style case is weak, but it cannot claim an
editorial decision or publication readiness.

K-Dense `scientific-critical-thinking` contributes evidence-quality discipline
to review, not a separate authority layer. Use it to name internal validity,
external validity, construct validity, statistical conclusion validity, bias,
confounding, reproducibility, ethics, and reporting-standard problems when the
manuscript evidence supports the concern.

K-Dense `scholar-evaluation` contributes evaluation discipline for positioning,
novelty, rigor, and likely reviewer reception. Use it to make the review
decision more explicit: separate "interesting but unsupported", "technically
adequate but low contribution", "clinically useful but under-explained", and
"submission-fit issue" findings. These are route-back labels, not editorial
accept/reject decisions.

For claim/citation disputes, read
`references/professional-quality-ref-templates.md` and use
`claim_citation_quality_loop_ref` plus `citation_quality_action_matrix_ref`.
These refs let the AI reviewer recommend keep, downgrade, replace, route back,
human gate, or stop without issuing a quality verdict, owner receipt, typed
blocker, or publication readiness claim.

Historical ResearAI/OpenScience `f120290` contributes local-first claim-warning discipline, not
a second skill catalog. For disputed manuscript, figure/table, or citation
claims, add refs-only `claim_type_ref` and `graph_warnings_ref` before the
reviewer action matrix when source material permits it. Use `claimType` to
separate descriptive, association, prediction, causal, methods, and governance
claims; use `graphWarnings` for unsupported, stale, circular, missing-source, or
source/body drift risks. When a reviewer annotation points at a claim gap, add
`annotation_to_source_regeneration_ref` that maps the annotation back to source
refs, claim-evidence refs, citation refs, or the missing ref family, then emit
`claim_warning_route_back_candidate_ref` if repair is needed. These refs are
review hints only: they are not reviewer receipts, MAS owner receipts, typed
blockers, publication verdicts, or quality verdicts.

`skill_pack_governance_policy_ref` may record allowed scope, dependency or
permission notes, and stage-use policy for the synced skill pack. Do not copy an
OpenScience skill catalog, create a new MAS default skill source, or treat this
governance ref as owner acceptance.

Use `professional_ai_quality_floor_ref` for Co-Scientist-style JIT review
affordance inside this existing skill. Every major critique should produce
`critique_as_repair_hint_ref`, not only a severity label: name the affected
claim/source/figure/table/data/package refs, the repair route, and the evidence
needed to clear it. Extract `reusable_lesson_ref` only when the concern is a
repeatable manuscript-quality lesson. Trigger `triggered_meta_review_ref` when
findings conflict, route-back repeats, claim type crosses disciplines, or a
candidate would approach MAS truth, owner receipt, typed blocker, artifact
authority, or readiness. Use `opportunistic_knowledge_prefetch_ref` for bounded
source, journal, prior-review, figure/table, data, or rerun refs needed for the
review; consume `rerun_receipt_ref` as evidence only when fingerprints and
limits are visible.

AcademicForge/Claude Science paper-narrative contributes a handling-editor deck
review pattern. Use it when the draft has figures, captions, or a manuscript
PDF: infer the pitch and figure claims from the work itself, then review the
full deck for `fig1_hook_ref`, `deck_arc_ref`, `figure_moves_ref`,
`missing_panels_ref`, and `kill_list_ref`. These are action-matrix inputs only;
they do not create editorial acceptance, reviewer receipt, publication
readiness, or a MAS owner verdict.

AcademicForge/Claude Science pdf-explore contributes a PDF evidence-extraction
boundary. For long PDFs or supplements, parse once, then use outline, scan,
grep, and crop refs to find evidence. Keep extraction separate from judgment:
`pdf_evidence_extraction_ref` can support review findings, but MAS still owns
source acceptance, citation acceptance, claim repair, and readiness labels. Do
not block review on Claude Science helper availability; use the current
workspace's PDF reader, text extraction, image crop, or manual page readback and
record the method as part of the extraction ref.
