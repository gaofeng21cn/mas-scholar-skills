---
name: medical-research-lit
description: "Use for MAS medical-paper literature discovery, especially PubMed-oriented search planning, query refinement, source screening, PMID/DOI verification, citation-support checks, evidence maps, and refs-only handoff back to MAS scout/write/review."
---

# Medical Research Literature

Use this skill when a MAS paper task needs external literature evidence instead of memory-only citation guesses.

This is a real Codex specialist skill in the MAS Scholar Skills pack. It can guide search, screening, verification, evidence mapping, and route-back handoff. It does not own MAS study truth, citation authority, reviewer verdicts, owner receipts, typed blockers, or publication readiness.

## Workflow

1. State the medical claim, population, exposure/intervention, comparator, outcome, study design, and manuscript section that needs support.
2. Build a PubMed-oriented query plan with synonyms, MeSH candidates when useful, date/language limits only when justified, and explicit exclusion criteria.
3. Run the OPL Connect PubMed connector when available: `opl connect pubmed search --query "<query>" --limit <n> --json`. Record returned `pubmed_source_refs` and `pubmed_connector_invocation_ref`. If the connector is unavailable, use the current project-approved PubMed or literature-search tool and record the command/ref used.
4. Screen results into `retain`, `reject`, and `watchlist` with a short reason for every promoted source.
5. Verify identifiers for retained sources: PMID, DOI, title, journal, year, and source URL when available.
6. Map each retained source to the exact claim, sentence, figure/table, methods detail, or limitation it supports.
7. Produce a refs-only handoff for MAS `scout`, `write`, or `review`.

## Handoff Shape

Return a compact structure with:

- `literature_question`
- `query_plan_ref`
- `search_command_ref`
- `pubmed_source_refs`
- `pubmed_connector_invocation_ref`
- `retained_sources`
- `rejected_sources`
- `watchlist_sources`
- `claim_support_map_ref`
- `citation_integrity_notes`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Each retained source should include `title`, `pmid`, `doi`, `year`, `journal`, `source_url`, `claim_supported`, `support_strength`, and `limitations`.

## MAS Boundary

Use literature evidence as candidate support. MAS `scout`, `write`, `review`, or the relevant owner surface must decide whether a source enters the manuscript, citation ledger, review ledger, or claim-evidence map.

Do not fabricate citations, infer PMID/DOI from memory, cite third-party summaries as primary authority, or turn a search result into publication readiness.
