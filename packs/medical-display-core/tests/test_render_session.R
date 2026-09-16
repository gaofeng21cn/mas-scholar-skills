#!/usr/bin/env Rscript
source("packs/medical-display-core/rlib/medicaldisplaycore/render_session.R")
root <- tempfile("render-session-")
dir.create(root)
session <- new.env(parent = globalenv())
initial_directory <- getwd()
initial_options <- options()
initial_environment <- Sys.getenv()
set.seed(91)
initial_seed <- .Random.seed
session$render_evidence_request <- function(request_path, expected_template_id) {
  options(render_test_option = 1)
  Sys.setenv(RENDER_TEST_VARIABLE = "changed")
  setwd(root)
  runif(1)
  pdf(file.path(root, "temporary.pdf"))
  assign("renderer_temporary_state", 42, envir = .GlobalEnv)
  session$temporary <- TRUE
  if (expected_template_id == "fail") stop("expected isolated failure")
}
job <- list(case_id = "fail", template_id = "fail", request_path = file.path(root, "request.json"), render_mode = "final")
result <- run_render_job(job, session)
stopifnot(!result$ok, is.null(result$restoration_error), identical(getwd(), initial_directory),
  identical(options(), initial_options), identical(Sys.getenv(), initial_environment),
  identical(.Random.seed, initial_seed), is.null(dev.list()),
  !exists("renderer_temporary_state", .GlobalEnv, inherits = FALSE), !exists("temporary", session, inherits = FALSE))
job$template_id <- "pass"
result <- run_render_job(job, session)
stopifnot(result$ok)
# An irrecoverable alteration to a previously open device must stop a batch.
pdf(file.path(root, "prior.pdf"))
session$render_evidence_request <- function(...) dev.off()
result <- run_render_job(job, session)
stopifnot(!result$ok, !is.null(result$restoration_error))
unlink(root, recursive = TRUE)
cat("render session state restoration: PASS\n")
