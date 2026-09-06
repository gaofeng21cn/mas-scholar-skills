# External-Validation Tables

The numbered tables below describe information jobs, not required literal
positions. Bind them to the manuscript's current numbering and journal format.

For prediction-model external-validation manuscripts, require table shells to
separate three jobs instead of compressing them into prose:

- Table 1: development and validation cohort characteristics, endpoint counts,
  key predictor distributions, units, missingness or available N, and SMD or a
  clear reason SMD cannot be computed;
- Table 2: validation performance, including validation N, event count, mean
  predicted risk, observed risk, C-statistic, O:E, Brier or prediction error,
  calibration intercept/slope, and uncertainty where available;
- grouped calibration table: group or decile, N, events, mean predicted risk,
  observed risk with interval, and O:E or risk difference when it supports the
  central claim.

When follow-up can end before the prediction horizon, label Table 1 event
percentages as recorded event count fractions, not observed risks. Put the
censoring-aware observed risk and its estimator in the performance or grouped
calibration table. Table notes must identify Kaplan-Meier, cumulative-incidence,
IPCW, or other estimands and keep event counts, risk estimates, O:E, and
prediction error semantically distinct.

If development-cohort individual data are unavailable, make the source of
summary statistics explicit and route missing rows to review or human gate
rather than inventing comparable Table 1 cells.

Before initial-draft handoff, build `baseline_table_traceability_ref` for every
Table 1 variable. Bind the variable and unit, each group's total N, available N,
missing N, displayed denominator, group/source identity, source metric, and the
source/table SMD values. Require `available_n + missing_n = group_n` and the
displayed summary denominator to equal the available N. A single global cohort
denominator cannot replace variable-level denominators. Reconcile SMDs across
source and Table 1 within an explicit rounding tolerance; do not omit SMD or
invent comparability when a source cohort lacks individual-level data.
