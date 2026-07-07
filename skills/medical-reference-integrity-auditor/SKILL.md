---
name: medical-reference-integrity-auditor
description: "Use when a MAS medical-paper task needs refs-only reference integrity audit: PMID/DOI/title/year checks, citation-source fit, retraction/version checks, placeholder detection, claim-citation support maps, route-back, and owner-gate handoff. This optional specialist does not accept references, write MAS truth, sign owner receipts, create typed blockers, or claim readiness."
---

# Medical Reference Integrity Auditor

Use this optional MAS Scholar Skills specialist when citations, reference lists,
or claim-citation links need integrity review before MAS/domain owner use.

This skill is refs-only and no-authority. It can prepare reference audit refs,
support maps, `route_back_candidate`, and `owner_gate_handoff_ref`; it cannot
accept a reference into a manuscript, write MAS truth, sign owner receipts,
create typed blockers, or claim publication readiness.

Optional helper: use `kernel.py` for deterministic DOI/PMID/PMCID
normalization, duplicate keys, unresolved identifier lint, and inventory
scaffolds. It is stdlib-only and no-authority.

## Workflow

1. Build `reference_inventory_ref`: citation keys, manuscript locations, title,
   authors, year, journal, PMID, PMCID, DOI, URL, and source type.
2. Verify identifiers in `identifier_integrity_ref`: PMID/DOI/title/year
   consistency, duplicate refs, preprint/published versions, and missing fields.
3. Check `source_status_ref`: retraction, correction, guideline version,
   superseded standard, or official-source status when relevant.
4. Build `claim_citation_support_map_ref`: claim text, cited source, support
   type, population/endpoint/method fit, and support strength.
5. Produce `route_back_candidate` for placeholders, fabricated-looking refs,
   identifier mismatch, source mismatch, weak support, or missing primary source.

## Handoff Shape

Return:

- `reference_inventory_ref`
- `identifier_integrity_ref`
- `source_status_ref`
- `claim_citation_support_map_ref`
- `duplicate_or_placeholder_ref`
- `support_gap_ref`
- `candidate_package_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not treat a clean audit candidate as citation acceptance, source truth,
owner receipt, typed blocker, reviewer receipt, or publication readiness.
