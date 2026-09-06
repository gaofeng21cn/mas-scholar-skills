## External Learning Quality Floor

The method review is pinned in [upstream provenance](upstream-provenance.md).
Consult source-specific details below only for providers used by the current
retrieval; this does not add a transport, parser or database dependency.

### Retrieval And Reference Evidence

- A successful HTTP status does not prove successful retrieval. Inspect the
  response body for provider errors, rate limits, error records and unexpected
  content types before calling it a paper or result set. Keep provider, query,
  filters, access date and returned identifiers with the actual evidence.
- A PMC/JATS response without an article body is metadata-only. An abstract,
  index record or metadata lookup does not prove that the full paper was read
  or that it supports a specific claim. Record the strongest material actually
  inspected and use the available full-text route when the claim needs it.
- arXiv can return an Atom error entry or plain-text rate-limit response;
  detect these, preserve requested versus returned/versioned identifiers and
  any query rewrite, and do not count error entries as retrieved papers.
- Keep Europe PMC's source and identifier together; an ID alone can collide
  across sources. When completeness matters, follow actual page size, cursor
  and termination behavior and reconcile duplicates/counts with the search
  contract. Do not infer completion from the requested page length.
- bioRxiv/medRxiv's metadata API is not a keyword-search endpoint. For keyword
  discovery, use an available provider that supports it, such as Europe PMC;
  retain preprint server/version identity when matching a published article.
- Crossref 404 means that provider did not return a record. Check DOI resolution,
  DataCite, the publisher or another applicable authoritative source before
  declaring an identifier incorrect. Absent DOI, volume or pages can be valid
  for a source type, online-first article or article-number publication.
- Merge candidates by verified identity while retaining source provenance and
  preprint/final-version distinctions. Keep citation keys and author order
  consistent. Verify missing author-name fields from an authoritative source
  rather than inventing or heuristically splitting names; preserve a literal
  corporate/group author when appropriate. Export BibTeX/RIS without
  overwriting the original unless the current task includes that mutation.

For a systematic review, use the applicable
[PRISMA 2020 resources](https://www.prisma-statement.org/prisma-2020) and design
extension with reproducible eligibility, screening reasons and count evidence.
A targeted source lookup does not require a screening campaign, a fixed number
of databases, an AI figure or citation-graph expansion. For a requested impact
audit, distinguish total citations, citations without overlapping authors and
the inspected citation context; these are not measures of medical validity.

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

The default discovery route for medical and clinical claims is PubMed/PMC
through OPL Connect scientific search. Candidate identifiers and metadata are
then strictly checked through OPL Connect reference verification. Record
`opl_connect_search_ref`, `opl_connect_reference_verification_ref`, and
`pubmed_source_refs` as read-only evidence inputs. Use broader sources only
when the question needs metadata
normalization, cross-disciplinary coverage, citation graph expansion, guideline
lookup beyond PubMed indexing, or full-text/protocol context. Crossref and
OpenAlex may be supplied through an explicit generic OPL Connect fallback as
`fallback_source_refs`; they are metadata, coverage, or graph evidence, not
citation acceptance. MAS still decides whether any source enters the citation
ledger or manuscript.

K-Dense `paper-lookup`, `citation-management`, `literature-review`, and
`database-lookup` contribute a retrieval contract: choose the smallest
authoritative source set that answers the claim, keep endpoint/filter
provenance, reconcile identifiers and counts when completeness matters, and
return screened candidate refs rather than unbounded raw API dumps.
