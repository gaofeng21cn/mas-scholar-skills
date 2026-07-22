#!/usr/bin/env Rscript

renderer <- new.env(parent = globalenv())
source(
  file.path(
    "packs",
    "medical-display-core",
    "rlib",
    "medicaldisplaycore",
    "cohort_flow_renderer.R"
  ),
  local = renderer
)

payload <- list(
  flow_mode = "source_layer_accounting",
  steps = list(list(step_id = "all", label = "All records", n = 100L)),
  denominator_step_id = "all",
  source_layers = list(
    list(layer_id = "china", label = "China cohort", n = 40L),
    list(layer_id = "nhanes", label = "NHANES analysis sample", n = 60L)
  ),
  subcohort_coverage = list(
    list(coverage_id = "china_score", label = "China score", n = 40L),
    list(coverage_id = "nhanes_score", label = "NHANES score", n = 60L)
  ),
  endpoint_inventory = list(
    list(label = "China recorded deaths", n = 2L),
    list(label = "NHANES recorded deaths", n = 3L)
  ),
  left_heading = "China development",
  right_heading = "NHANES complete-case analysis sample",
  transfer_label = "Coefficients frozen before scoring"
)

plot <- renderer$build_source_layer_accounting_plot(payload)
text_labels <- vapply(plot$layers, function(layer) {
  as.character(layer$aes_params$label %||% "")
}, character(1))
stopifnot(any(text_labels == payload$left_heading))
stopifnot(any(text_labels == payload$right_heading))
stopifnot(any(text_labels == payload$transfer_label))

sidecar <- renderer$build_source_layer_layout_sidecar(
  payload,
  list(
    status = "prepared",
    run_context_ref = "test://run-context",
    run_context_fingerprint = "sha256:test"
  )
)
stopifnot(identical(sidecar$metrics$left_heading, payload$left_heading))
stopifnot(identical(sidecar$metrics$right_heading, payload$right_heading))
stopifnot(identical(sidecar$metrics$transfer_label, payload$transfer_label))

cat("cohort-flow heading override regression: PASS\n")
