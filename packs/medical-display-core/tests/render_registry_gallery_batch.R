#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) {
  stop("usage: render_registry_gallery_batch.R <batch-request.json>")
}

suppressPackageStartupMessages(library(jsonlite))
batch_path <- normalizePath(args[[1]], mustWork = TRUE)
batch <- fromJSON(batch_path, simplifyVector = FALSE)
pack_root <- normalizePath(batch$pack_root, mustWork = TRUE)

old_source_only <- Sys.getenv("MAS_DISPLAY_RENDERER_SOURCE_ONLY", unset = "")
Sys.setenv(MAS_DISPLAY_RENDERER_SOURCE_ONLY = "1")
source(file.path(pack_root, "rlib", "medicaldisplaycore", "evidence_renderer.R"))
source(file.path(pack_root, "rlib", "medicaldisplaycore", "candidate_renderer.R"))
cohort_renderer <- new.env(parent = globalenv())
source(file.path(pack_root, "rlib", "medicaldisplaycore", "cohort_flow_renderer.R"), local = cohort_renderer)
if (nzchar(old_source_only)) {
  Sys.setenv(MAS_DISPLAY_RENDERER_SOURCE_ONLY = old_source_only)
} else {
  Sys.unsetenv("MAS_DISPLAY_RENDERER_SOURCE_ONLY")
}

restore_environment <- function(before) {
  after_names <- names(Sys.getenv())
  before_names <- names(before)
  added <- setdiff(after_names, before_names)
  if (length(added)) Sys.unsetenv(added)
  if (length(before_names)) do.call(Sys.setenv, as.list(before))
}

restore_options <- function(before) {
  added <- setdiff(names(options()), names(before))
  if (length(added)) options(stats::setNames(rep(list(NULL), length(added)), added))
  options(before)
}

run_case <- function(job) {
  old_options <- options()
  old_environment <- Sys.getenv()
  old_devices <- dev.list()
  old_search_path <- search()
  old_global_names <- ls(envir = .GlobalEnv, all.names = TRUE)
  old_seed_exists <- exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  if (old_seed_exists) old_seed <- get(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  output <- character()
  error <- NULL
  tryCatch(
    {
      output <- capture.output({
        if (identical(job$template_id, "cohort_flow_figure")) {
          cohort_renderer$render_cohort_flow_request(job$request_path)
        } else {
          Sys.setenv(MAS_DISPLAY_RENDER_MODE = job$render_mode)
          render_evidence_request(job$request_path, expected_template_id = job$template_id)
        }
      }, type = "output")
    },
    error = function(condition) error <<- conditionMessage(condition),
    finally = {
      restore_options(old_options)
      restore_environment(old_environment)
      current_devices <- dev.list()
      current_device_ids <- if (is.null(current_devices)) integer() else current_devices
      old_device_ids <- if (is.null(old_devices)) integer() else old_devices
      new_devices <- setdiff(current_device_ids, old_device_ids)
      for (device in rev(new_devices)) try(dev.off(device), silent = TRUE)
      added_search_entries <- setdiff(search(), old_search_path)
      for (entry in rev(added_search_entries[grepl("^package:", added_search_entries)])) {
        try(detach(entry, character.only = TRUE, unload = FALSE), silent = TRUE)
      }
      added_global_names <- setdiff(
        ls(envir = .GlobalEnv, all.names = TRUE),
        c(old_global_names, ".Random.seed")
      )
      if (length(added_global_names)) rm(list = added_global_names, envir = .GlobalEnv)
      if (old_seed_exists) {
        assign(".Random.seed", old_seed, envir = .GlobalEnv)
      } else if (exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)) {
        rm(".Random.seed", envir = .GlobalEnv)
      }
      seed_restored <- if (old_seed_exists) {
        identical(get(".Random.seed", envir = .GlobalEnv, inherits = FALSE), old_seed)
      } else {
        !exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
      }
      state_restored <- identical(options(), old_options) &&
        identical(Sys.getenv(), old_environment) &&
        identical(dev.list(), old_devices) &&
        identical(search(), old_search_path) &&
        identical(ls(envir = .GlobalEnv, all.names = TRUE), old_global_names) &&
        seed_restored
      if (!state_restored && is.null(error)) error <<- "batch harness failed to restore case state"
    }
  )
  list(case_id = job$case_id, ok = is.null(error), stdout = paste(output, collapse = "\n"), error = error)
}

results <- lapply(batch$jobs, run_case)
write_json(list(results = results), stdout(), auto_unbox = TRUE, null = "null")
