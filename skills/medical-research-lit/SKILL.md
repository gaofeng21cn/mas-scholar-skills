---
name: medical-research-lit
description: "Use for MAS medical-paper literature discovery, especially PubMed-oriented search planning, query refinement, source screening, PMID/DOI verification, citation-support checks, evidence maps, and refs-only handoff back to MAS scout/write/review."
---

# Medical Research Literature

Use this skill when a MAS paper task needs external literature evidence instead of memory-only citation guesses.

This is a real Codex specialist skill in the MAS Scholar Skills pack. It can guide search, screening, verification, evidence mapping, and route-back handoff. It does not own MAS study truth, citation authority, reviewer verdicts, owner receipts, typed blockers, or publication readiness.

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
5. Deduplicate results by PMID, DOI, normalized title, year, and preprint or
   registry id. Keep both preprint and journal versions only when they differ in
   evidence relevance.
6. Screen results into `retain`, `reject`, and `watchlist` with a short reason
   for every promoted or rejected source.
7. Verify identifiers for retained sources: PMID, DOI, title, journal, year,
   source URL, article type, population, endpoint, and whether the source is
   primary, review, guideline, preprint, registry, or commentary.
8. Grade support strength for each claim: `direct_primary`, `direct_guideline`,
   `method_precedent`, `contextual_background`, `contradictory`, `weak`, or
   `not_applicable`.
9. Map each retained source to the exact claim, sentence, figure/table, methods
   detail, or limitation it supports.
10. Produce a refs-only handoff for MAS `scout`, `write`, or `review`.

## Handoff Shape

Return a compact structure with:

- `literature_question`
- `query_plan_ref`
- `search_command_ref`
- `pubmed_source_refs`
- `pubmed_connector_invocation_ref`
- `fallback_source_refs`
- `deduplication_ref`
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

## MAS Boundary

Use literature evidence as candidate support. MAS `scout`, `write`, `review`, or the relevant owner surface must decide whether a source enters the manuscript, citation ledger, review ledger, or claim-evidence map.

Do not fabricate citations, infer PMID/DOI from memory, cite third-party
summaries as primary authority, use citation counts as evidence strength, or
turn a search result into publication readiness.
