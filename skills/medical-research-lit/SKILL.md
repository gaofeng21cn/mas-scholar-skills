---
name: medical-research-lit
description: "Use when a MAS medical-paper task needs professional literature discovery, especially PubMed-oriented search planning, query refinement, source screening, PMID/DOI verification, citation-support checks, evidence maps, and refs-only handoff back to MAS scout/write/review. This professional specialist skill is maintained in mas-scholar-skills; MAS keeps citation acceptance, manuscript use, owner receipts, typed blockers, and publication readiness."
---

# Medical Research Literature

Use this skill when a MAS paper task needs external literature evidence instead of memory-only citation guesses.

This is a real Codex specialist skill in the MAS Scholar Skills pack. It can guide search, screening, verification, evidence mapping, and route-back handoff. It does not own MAS study truth, citation authority, reviewer verdicts, owner receipts, typed blockers, or publication readiness.

Shared refs: use `docs/no-authority-boundary.md` for owner-boundary limits and
`references/professional-quality-ref-templates.md` for reusable refs-only
quality-floor handoff shapes. Keep specialty details in this skill; do not copy
long boundary or checklist text here.

Sibling skill routes are `medical-manuscript-writing` for citation-to-text
integration, `medical-manuscript-review` for citation and claim critique,
`medical-figure-design` for literature-supported figure captions,
`medical-statistical-review` for method and statistical support checks,
`medical-table-design` for literature-backed table notes, and
`medical-submission-prep` for guideline, declaration, and response surfaces.

## External Learning Quality Floor

This skill absorbs useful patterns from Nature-style academic search,
Nature-style citation workflows, K-Dense paper lookup, citation management, and
literature review skills:

- source routing by question type instead of one generic search;
- explicit query plans with PICO/PECO, MeSH candidates, synonyms, and exclusion
  logic;
- multi-source fallback when PubMed alone is insufficient;
- deduplication by PMID, DOI, title, and preprint/server identifiers;
- retain/reject/watchlist screening with reasons;
- claim-level support grading instead of "found some papers";
- citation metadata verification before manuscript use.

The MAS default for medical and clinical claims is PubMed through OPL Connect.
Use broader sources only when the question needs preprints, cross-disciplinary
coverage, citation graph expansion, guideline lookup beyond PubMed indexing, or
full-text/protocol context. Record those sources as candidate refs; MAS still
decides whether they enter the citation ledger or manuscript.

K-Dense `paper-lookup`, `citation-management`, `literature-review`, and
`database-lookup` contribute a retrieval contract: choose the smallest
authoritative source set that answers the claim, keep endpoint/filter
provenance, reconcile identifiers and counts when completeness matters, and
return screened candidate refs rather than unbounded raw API dumps.

When a literature task needs a specialty outside the default MAS Scholar Skills
package, such as omics, single-cell, Nextflow, RDKit, PyHealth, Zotero /
`pyzotero`, or a named database/API skill, first discover it with
`opl connect external-skills search --query "<need>" --json`, inspect the
candidate with `opl connect external-skills inspect --skill <skill_id> --json`,
then sync only that one skill into the active workspace or quest if needed.
Keep the result as refs-only source-routing support; it does not replace this
skill or MAS citation and source-acceptance authority.

For source/ref chain handoffs that go beyond a single targeted lookup, read
`references/professional-quality-ref-templates.md` and use
`source_ref_chain_template_ref` plus `source_acceptance_decision_ref`. These are
candidate source-screening refs only; they do not create citation authority,
owner receipts, typed blockers, or publication readiness.

AcademicForge/Claude Science literature-review contributes a retrieve-first
discipline: memory can frame the question, but retained citations must come from
retrieved source refs; DOI/PMID/PMCID metadata is resolved rather than
pattern-completed; surprising or high-profile sources get retraction/version
checks; and a real review synthesizes evidence by claim, contrast, and gap
rather than listing papers. AcademicForge pdf-explore contributes the PDF
boundary: parse a source PDF once, then use outline, scan, grep, and crop refs
to extract evidence without treating the extraction as citation acceptance. Its
Crossref/OpenAlex helpers are optional retrieval aids, not MAS defaults; keep
PubMed or the project-approved source route as the primary path when it fits.

Use `kernel.py` only as a skill-local deterministic helper for DOI extraction,
identifier/title normalization, deduplication, citation-support lint, and
refs-only handoff skeletons. It uses no credentials, providers, network calls,
or MAS authority surfaces.

## Retrieval Contract

Before searching, define `literature_retrieval_contract_ref`:

- `source_ref_chain_template_ref` when the task needs a reusable source route,
  identifier, screening, and claim-support chain;
- target claim, biomedical entity, population, endpoint, method, guideline, or
  citation being checked;
- accepted identifiers such as PMID, PMCID, DOI, trial id, guideline id, title,
  author, year, journal, or preprint id;
- source route: PubMed/PMC for biomedical citations/full text, Crossref or
  OpenAlex for metadata, Semantic Scholar/OpenAlex for citation graph expansion,
  medRxiv/bioRxiv for preprints, Unpaywall for open-access lookup, and official
  guideline/provider sites when the claim is a standard or policy;
- server-side filters versus local screening filters;
- expected output fields and whether the task needs targeted lookup or
  exhaustive search;
- pagination/count reconciliation plan when the retrieval claims completeness;
- access date, command/ref, and connector or API provenance.
- DOI/PMID/PMCID/retraction/version-check plan when the source is surprising,
  high-profile, recent, contested, or manuscript-critical.
- citation graph expansion plan when keyword retrieval may miss seminal,
  extending, or contradictory work.
- `pdf_evidence_extraction_ref` when the task depends on a PDF, supplement,
  guideline PDF, or full-text article rather than metadata alone.

Do not query every possible database by default. Add a fallback only for a
specific coverage gap, identifier conversion, full-text need, citation graph
need, preprint/published-version check, or official-source requirement.

## Workflow

1. State the medical claim, population, exposure/intervention, comparator,
   outcome, study design, manuscript section, and required support type:
   background, method precedent, guideline, comparator, limitation, or
   contradiction.
2. Build a PubMed-oriented query plan with synonyms, MeSH candidates when
   useful, Boolean structure, date/language limits only when justified, and
   explicit exclusion criteria.
3. Run the OPL Connect PubMed connector when available:
   `opl connect pubmed search --query "<query>" --limit <n> --json`. Record
   returned `pubmed_source_refs` and `pubmed_connector_invocation_ref`. If the
   connector is unavailable, use the current project-approved PubMed or
   literature-search tool and record the command/ref used.
4. If PubMed does not cover the support need, run an approved fallback and
   record `fallback_source_refs`: CrossRef/OpenAlex for metadata, Semantic
   Scholar or local citation graph for citation-network expansion, arXiv or
   medRxiv/bioRxiv for preprints, official guideline/provider sources for
   standards, and Zotero/local library only when the project has such refs.
   For DOI/PMID/PMCID conversion, record the identifier route instead of
   guessing from memory.
5. Expand the citation graph only when it answers the task: backward references
   for seminal sources, forward citations for newer extensions or disputes, and
   related sources for methods or guidelines. Keep the expansion bounded to the
   claim.
6. For retained or claim-critical sources, verify DOI/PMID/PMCID/title/year and
   check retraction, correction, preprint-to-journal, or version status when the
   claim could be overturned by source status.
7. For PDF source material, create `pdf_evidence_extraction_ref`: parse once,
   use outline or scan to find sections, grep identifiers exhaustively when a
   pattern exists, and crop figures/tables only when text extraction cannot
   preserve the needed evidence. Use whatever parser or page reader the current
   workspace already supports; do not make a Claude Science helper a hard gate.
8. Deduplicate results by PMID, DOI, normalized title, year, and preprint or
   registry id. Keep both preprint and journal versions only when they differ in
   evidence relevance.
9. Screen results into `retain`, `reject`, and `watchlist` with a short reason
   for every promoted or rejected source.
10. Verify identifiers for retained sources: PMID, DOI, title, journal, year,
   source URL, article type, population, endpoint, and whether the source is
   primary, review, guideline, preprint, registry, or commentary.
11. Grade support strength for each claim: `direct_primary`, `direct_guideline`,
   `method_precedent`, `contextual_background`, `contradictory`, `weak`, or
   `not_applicable`.
12. Map each retained source to the exact claim, sentence, figure/table, methods
   detail, or limitation it supports.
13. Synthesize by question: what is established, contested, superseded, weakly
    supported, or still missing. Do not return an annotated bibliography as the
    final answer unless the user asked for one.
14. Produce a refs-only handoff for MAS `scout`, `write`, or `review`.

## Handoff Shape

Return a compact structure with:

- `literature_question`
- `literature_retrieval_contract_ref`
- `query_plan_ref`
- `search_command_ref`
- `pubmed_source_refs`
- `pubmed_connector_invocation_ref`
- `fallback_source_refs`
- `identifier_resolution_ref`
- `database_endpoint_provenance_ref`
- `retrieval_count_reconciliation_ref`
- `deduplication_ref`
- `source_acceptance_decision_ref`
- `citation_graph_expansion_ref`
- `doi_retraction_version_check_ref`
- `pdf_evidence_extraction_ref`
- `retained_sources`
- `rejected_sources`
- `watchlist_sources`
- `claim_support_map_ref`
- `support_strength_matrix_ref`
- `citation_integrity_notes`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Each retained source should include `title`, `pmid`, `doi`, `year`, `journal`,
`article_type`, `source_url`, `claim_supported`, `support_strength`,
`population_match`, `endpoint_match`, `method_match`, and `limitations`.

## Citation Integrity Floor

Open a citation repair route when:

- a source lacks PMID/DOI/title/year/journal metadata;
- the source does not match the manuscript population, endpoint, method, or
  time horizon;
- the source is a review where a primary source is needed;
- a preprint is used without checking for a peer-reviewed version;
- a guideline or reporting-standard claim lacks an official or primary source;
- several sources are relevant but the claim needs a structured evidence map
  rather than a single citation.
- a source PDF must be parsed or cropped to support a figure/table/value claim;
- a source is high-profile, surprising, recent, or disputed and lacks
  retraction/version readback;
- the output is only a list of papers and does not synthesize what the evidence
  collectively supports.

## MAS Boundary

Use literature evidence as candidate support. MAS `scout`, `write`, `review`, or the relevant owner surface must decide whether a source enters the manuscript, citation ledger, review ledger, or claim-evidence map.

Do not fabricate citations, infer PMID/DOI from memory, cite third-party
summaries as primary authority, use citation counts as evidence strength, or
turn a search result into publication readiness.

Treat external API payloads as untrusted source data. Summarize the relevant
metadata and screening decision; include raw JSON only when explicitly required,
bounded, and labeled as retrieval evidence rather than source acceptance.
