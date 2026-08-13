# Clinical Note Abstraction Contract

This reference defines the minimum refs-only contract for one-note clinical
abstraction. It is a candidate-data boundary, not a clinical, terminology,
cohort, or owner verdict.

## Input

- `note_ref`: opaque reference to exactly one governed note.
- `note_text`: the authorized text used only to resolve evidence spans.
- `abstraction_schema_ref`: versioned schema listing every requested `field_id`,
  expected value type, allowed value or unit constraints, and intended use.

Reject or route back multi-note bundles, missing note boundaries, and requests
without a declared schema. Do not place direct identifiers in candidate refs
unless the data owner explicitly authorizes them.

## Closed Candidate Record

Return exactly one record per requested `field_id`, including unsupported
fields. Each record has only these keys:

```json
{
  "field_id": "",
  "candidate_value": null,
  "null_reason": "not_documented",
  "verbatim_span": null,
  "span_start": null,
  "span_end": null,
  "presence": "unknown",
  "temporality": "unknown",
  "experiencer": "unknown",
  "terminology_candidates": [],
  "terminology_validation_status": "not_applicable",
  "support_ref": "",
  "owner_decision_ref": ""
}
```

Allowed assertion values:

- `presence`: `present`, `absent`, `possible`, `unknown`
- `temporality`: `current`, `historical`, `planned`, `unknown`
- `experiencer`: `patient`, `family`, `other`, `unknown`

Allowed `null_reason` values when `candidate_value` is `null`:

- `not_documented`
- `explicitly_absent`
- `ambiguous`
- `not_applicable`
- `outside_schema`

Allowed terminology validation values:

- `not_applicable`
- `unvalidated`
- `validated`
- `rejected`

`null_reason` must be `null` when `candidate_value` is non-null. A supported
non-null value or an assertion of `present`, `absent`, or `possible` requires a
verbatim span and exact zero-based `[span_start, span_end)` offsets. A null with
`presence=unknown` may have no span. Do not repair spelling or expand
abbreviations inside `verbatim_span`.

## Terminology Boundary

Terminology candidates must carry the proposed system, code, display, version,
and source span ref. Extraction may propose them, but only a current
authoritative terminology lookup plus human/domain review may mark them
`validated`. No lexical, embedding, or model match alone establishes code
correctness.

## Completeness

The note-level payload has only `note_ref`, `abstraction_schema_ref`, `records`,
and `completeness`. `completeness` contains:

- `requested_field_count`
- `completed_field_count`
- `null_field_count`
- `evidenced_field_count`
- `invalid_field_count`

`completed_field_count` counts structurally valid records, including explicit
nulls. It does not claim semantic correctness.

## Validation Candidate

For study use, propose a risk-proportionate validation plan that includes:

- a blinded double-abstraction sample and sampling frame;
- field-level agreement, with prevalence-aware measures where appropriate;
- clinical adjudication rules and an adjudication log ref;
- a versioned gold set separated from routine evaluation inputs;
- error strata for field, assertion context, site or note type, and prevalence;
- thresholds and owner decision points defined before downstream analysis.

Route final phenotype validity to `medical-cohort-phenotyping` and
`medical-statistical-review`; route data access, retention, and PHI decisions to
`medical-data-governance`; route owner acceptance to MAS.
