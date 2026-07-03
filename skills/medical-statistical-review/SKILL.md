---
name: medical-statistical-review
description: "Use when a MAS medical-paper task needs professional statistical review before writing, review, figure, table, or submission handoff. Covers analysis-plan fit, estimand/outcome clarity, denominator and missingness checks, assumption diagnostics, effect-size and uncertainty reporting, multiplicity/sensitivity review, statistical prose repair, and refs-only route-back. This professional specialist skill is maintained in mas-scholar-skills; MAS keeps study truth, analysis authority, owner receipts, typed blockers, artifact authority, and publication readiness."
---

# Medical Statistical Review

Use this skill when a MAS paper task needs an expert statistical pressure test
over a methods plan, result package, table, figure, or manuscript claim.

This professional specialist skill is maintained in `mas-scholar-skills` /
MAS Scholar Skills. MAS stage operating prompts may sync and consume it, while
MAS still owns stage routing, study truth, analysis artifacts, evidence ledgers,
owner receipts, typed blockers, human gates, current packages, and publication
readiness.

Sibling skill routes are `medical-table-design` for table shells and formatting,
`medical-figure-design` for figure design, `medical-manuscript-writing` for
statistical prose repair, `medical-manuscript-review` for full-paper critique,
`medical-research-lit` for PubMed-oriented literature support, and
`medical-submission-prep` for submission-facing statistical checklist items, and
`medical-data-governance` for clinical data manifests, source readiness support,
version impact, privacy/access tiers, and lifecycle guardrails.

## Core Rule

Statistical review is not a script picker. Start from the clinical question,
estimand, data-generating context, outcome definition, denominator, missingness,
and claim strength. Use tests, models, diagnostics, and reporting checklists as
evidence tools.

Do not make a weak or under-specified analysis look acceptable by adding a more
complex model. If the design cannot support the claim, produce a claim
downgrade or route-back candidate.

## External Learning Quality Floor

This skill absorbs maintainable patterns from broad statistical-analysis,
scientific-critical-thinking, Nature-style data, and reviewer-response skills:

- select tests from question, variable type, independence, repeated measures,
  censoring, clustering, and distribution, not from a name in a draft;
- check assumptions before interpreting results;
- report effect sizes, uncertainty, denominators, missingness, and multiplicity;
- separate statistical significance from clinical meaning;
- bind every statistical claim to an analysis output, table, figure, or source
  ref;
- preserve the no-authority boundary: this skill proposes candidate judgments,
  while MAS or the domain owner accepts, rejects, or routes them back.

## Review Contract

Before judging the analysis, create or refresh:

- `statistical_question_ref`: clinical question, population, exposure or
  intervention, comparator, outcome, time horizon, and intended claim.
- `estimand_or_target_parameter_ref`: what quantity is being estimated and why.
- `analysis_plan_ref`: model/test family, covariates, stratification,
  clustering, repeated-measure, censoring, multiplicity, and sensitivity plan.
- `denominator_and_missingness_ref`: analysis set, exclusions, missingness
  pattern, imputation or complete-case strategy, and denominator consistency.
- `effect_size_and_uncertainty_ref`: effect measure, confidence interval or
  credible interval, p-value policy, and clinically meaningful threshold.
- `assumption_diagnostic_ref`: required diagnostics and observed concerns.
- `claim_strength_calibration_ref`: wording allowed by the evidence.

If these refs are missing, route back before polishing statistical language.

## Workflow

1. Identify the paper type: descriptive registry, observational association,
   prediction, time-to-event, intervention, diagnostic, systematic review, or
   other.
2. Map each statistical claim to the exact result artifact, table, figure,
   model output, or manuscript sentence that carries it.
3. Verify denominator, inclusion/exclusion, data window, missingness, and
   endpoint ascertainment before reviewing tests or models.
4. Check whether the model/test family matches the design: independence,
   pairing, repeated measures, clustering, distribution, censoring, competing
   risks, confounding, and sample size.
5. Require effect size and uncertainty for every inferential claim. P-values
   alone are not enough.
6. Check assumptions and diagnostics. Name the diagnostic that supports or
   weakens interpretation.
7. Check multiplicity, subgroup, sensitivity, and robustness claims. Downgrade
   exploratory or underpowered claims.
8. Check whether figures and tables show the same estimates, denominators, and
   uncertainty as the manuscript text.
9. Produce a statistical action matrix and route-back candidate.

If a statistical method, reporting claim, guideline statement, or clinical
interpretation needs biomedical literature support, use:

```bash
opl connect pubmed search --query "<query>" --limit <n> --json
```

Record returned `pubmed_source_refs` and
`pubmed_connector_invocation_ref`. The results are candidate refs only; MAS
still decides citation acceptance and manuscript use.

## Common Route-Backs

Route back when:

- the outcome, exposure, comparator, or time horizon is not defined;
- denominators differ across abstract, text, tables, and figures;
- missingness is high or differential without an explicit strategy;
- a selected diagnostic-field positive rate is written as prevalence or burden;
- a prediction model lacks validation, calibration, decision utility, or target
  population clarity;
- a time-to-event result omits censoring, risk set, proportional hazards, or
  competing-risk considerations when relevant;
- subgroup or sensitivity claims are stronger than their design allows;
- statistical prose claims causality, clinical deployment, or treatment benefit
  without supporting design.

## Handoff Shape

Return refs-only candidate output:

- `statistical_question_ref`
- `estimand_or_target_parameter_ref`
- `analysis_plan_ref`
- `denominator_and_missingness_ref`
- `assumption_diagnostic_ref`
- `effect_size_and_uncertainty_ref`
- `multiplicity_and_sensitivity_ref`
- `table_figure_consistency_ref`
- `statistical_action_matrix_ref`
- `claim_strength_calibration_ref`
- `route_back_candidate`
- `owner_gate_handoff_ref`

## MAS Boundary

This skill may write or propose candidate review notes only where the active
workspace permits candidate material. It must not write MAS domain truth,
analysis authority, publication eval, controller decisions, owner receipts,
typed blockers, human gates, current package authority, runtime queues, or
provider attempts.

Do not claim statistical approval, quality verdict, artifact authority,
publication readiness, owner acceptance, or submission readiness. MAS or the
domain owner must consume the refs and issue any owner receipt, typed blocker,
route-back, artifact mutation, or publication decision.
