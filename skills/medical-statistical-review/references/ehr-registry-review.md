## EHR And Registry Signal Validity Rule

For EHR, registry, chart-derived, claims-linked, or other real-world-data work,
do not treat a recorded field as a direct measurement of the target clinical
state. The analyzable signal is jointly shaped by the underlying state, the
opportunity to observe it, the care/documentation/coding process, and the
extraction or transformation path. Review those mechanisms together before
interpreting a count, rate, phenotype, outcome, association, or model result.

Produce one `ehr_registry_signal_validity_ref` under
`registry_signal_validity_pack`:

- `paper_identity_ref` must lock the paper type, target population, unit, source
  and time window, intended inference, and scientific identity. A descriptive
  registry atlas, phenotype validation study, association study, and prediction
  study cannot share an unstated validity target.
- `chart_review_validation_ref` must state what chart review validates, in which
  sampling frame and review unit, against what reference standard, and with what
  abstraction, adjudication, blinding, and agreement evidence. Positive
  predictive value in a selected sample does not establish sensitivity,
  representativeness, source completeness, or validity for every downstream
  phenotype and outcome.
- `phenotype_outcome_coupling_ref` must show that phenotype assignment and the
  outcome or target signal refer to compatible people, episodes, time windows,
  eligibility rules, denominators, and source coverage. Valid-looking components
  cannot be combined into an unvalidated joint endpoint.
- `availability_mechanism_ref` must distinguish true absence from not
  applicable, structurally unavailable, not ordered, not measured, not
  documented, not extracted, and site/time-specific capture. The statistical
  handling and denominator must follow the actual mechanism rather than treating
  every blank as one missing-data state.
- `observation_opportunity_bias_ref` must examine whether encounter frequency,
  follow-up, testing, referral, access, survival, site workflow, or care pathway
  changes who can acquire a recorded signal. Adjust, stratify, sensitize,
  restrict, or bound the claim when observation opportunity differs materially.
- `source_generation_quality_ref` must bind the signal to clinical workflow,
  measurement/coding/documentation rules, ingestion, deduplication,
  transformation, release/version, lineage, and source-QA evidence. Clean model
  output cannot repair an unidentified or unstable source-generation process.
- `claim_boundary_ref` must state the strongest supported descriptive,
  association, prediction, or causal wording and name forbidden inferences.
  Recorded-field positivity or availability is not automatically prevalence or
  incidence; missing recorded treatment is not automatically non-treatment or a
  treatment gap; site support is not automatically site performance or external
  validity.

Judge the seven member refs as one coupled validity argument. A chart-review
strength in one component cannot waive an availability, observation-opportunity,
source-generation, coupling, or claim-boundary failure elsewhere. When evidence
is incomplete, return a bounded claim downgrade, sensitivity requirement, or
`route_back_candidate` rather than a binary validity label.

Route phenotype-definition and ascertainment inputs to
`medical-cohort-phenotyping`, method decomposition to
`medical-methodology-planner`, source lineage and generation evidence to
`medical-data-governance`, prose calibration to `medical-manuscript-writing`,
and independent pressure testing to `medical-manuscript-review`. The integrated
ref returns here before MAS or the domain owner records acceptance.
`medical-registry-atlas-story-architect` may contribute optional narrative
framing only; it does not produce or own the integrated validity ref. The ref
remains refs-only/no-authority and cannot establish cohort truth, dataset validity,
analysis acceptance, an owner receipt, a typed blocker, a quality verdict, or
publication readiness.
