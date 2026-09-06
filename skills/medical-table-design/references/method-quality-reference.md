## External Learning Quality Floor

Fixed upstream revisions and license status are recorded in
[upstream provenance](upstream-provenance.md); consult it for a source update,
not as a prerequisite to every table repair.

### Table Evidence Decisions

Keep the measured unit, analysis unit and claim population distinct. Show
denominators, available values and missingness at the level used by each
estimate; zero, missing and not estimable need different representations.
Define effect measures and uncertainty, including whether an interval is a
confidence or prediction interval. Report multiplicity and dependence when
they change interpretation. Two separate significance labels do not test an
interaction, and lack of significance does not establish equivalence.

Bind a table's data-availability or source note to actual public, controlled,
within-paper, reused, restricted, justified-request or not-applicable evidence.
Do not invent an accession, DOI, ethical approval or access route to complete
the format. Table numbering and layout follow the manuscript and journal;
source traceability and the table's scientific job survive renumbering.

This skill adapts maintainable patterns from clinical data-presentation,
spreadsheet-quality, statistical-analysis, and Nature-style data workflows:

- preserve existing table conventions when the paper already has a style;
- design the table shell before filling cells;
- keep formulas/statistics traceable to source refs;
- verify denominators, units, decimal places, and footnotes;
- make table claims match manuscript and figure claims;
- keep data availability and source lineage visible without moving authority
  into this skill.
- use K-Dense scientific-writing/statistical-visualization discipline to choose
  a table only when exact values, denominators, subgroup structure, or compact
  multi-metric comparison are more useful than a figure.

Use `professional_ai_quality_floor_ref` for table-specific AI judgment.
`critique_as_repair_hint_ref` should convert table critique into a concrete
source metric, denominator, statistic, claim, footnote, figure-vs-table, or
submission repair. Add `claim_type_ref` and `graph_warnings_ref` when table
titles, notes, row labels, or manuscript-linked claims risk unsupported,
stale, circular, missing-source, denominator-drift, or table/body drift. Use
`annotation_to_source_regeneration_ref` for reviewer annotations that must trace
back to source metrics or analysis outputs. Consume `rerun_receipt_ref` only as
table rebuild/check evidence, and trigger `triggered_meta_review_ref` when
table and text/figure/statistics disagree materially.
