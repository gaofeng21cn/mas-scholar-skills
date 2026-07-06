---
name: research-pdf-evidence-explorer
description: "Use when MAS needs a refs-only PDF evidence exploration playbook inspired by AcademicForge pdf-explore. It guides parse-once, outline, scan, grep, crop, table/figure/page evidence refs, and owner-gate handoff without writing domain truth, signing owner receipts, creating typed blockers, or claiming publication readiness."
---

# Research PDF Evidence Explorer

Use this optional MAS Scholar Skills specialist when a task needs bounded PDF
inspection, page evidence, figure/table localization, or quote/source support
without repeatedly reparsing the same file. It adapts AcademicForge HEAD
`54a2f333973147a1fd703caea6f12252e1f227d6` `pdf-explore` patterns.

This skill is refs-only and no-authority. It can prepare parsed-PDF refs,
outline refs, page/region refs, crop refs, deterministic receipt refs, and
`owner_gate_handoff_ref`; it cannot write citation authority, domain truth,
owner receipt, typed blocker, quality verdict, or publication readiness.

Use `kernel.py` only as a skill-local deterministic helper for path
fingerprints, page-text normalization, outline guesses, lexical scans, regex
grep, and page/crop ref skeletons. It uses no credentials, providers, OCR
service, or authority surfaces; optional PDF parser imports are best-effort.

## Workflow

1. Parse once and record `pdf_parse_manifest_ref`, `pdf_sha256_ref`, page count,
   text extraction route, and OCR/render route if used.
2. Build `pdf_outline_ref` from headings, abstracts, captions, tables, figures,
   references, supplements, and appendices.
3. Scan before deep reading: use page ranges, figure/table captions, section
   labels, and search terms to select a bounded evidence window.
4. Grep exact terms for claims, identifiers, denominators, methods, endpoints,
   limitations, and reference metadata.
5. Crop or render only the page/region needed for human inspection, preserving
   `pdf_crop_ref`, page number, coordinates, and source hash.
6. Return compact evidence refs and route back when the PDF lacks the requested
   evidence.

## Handoff Shape

Return:

- `pdf_source_ref`
- `pdf_parse_manifest_ref`
- `pdf_outline_ref`
- `pdf_scan_ref`
- `pdf_grep_ref`
- `pdf_crop_ref`
- `page_evidence_refs`
- `table_or_figure_evidence_refs`
- `extraction_limitations_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

Do not treat extracted text, a cropped panel, or a found phrase as citation
acceptance, source truth, owner acceptance, typed blocker, or publication
readiness.
