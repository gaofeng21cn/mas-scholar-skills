# One task, one prepared environment. No dependency installation occurs here.
load_render_session <- function(pack_root, template_ids) {
  session <- new.env(parent = globalenv())
  before <- Sys.getenv("MAS_DISPLAY_RENDERER_SOURCE_ONLY", unset = NA_character_)
  on.exit(if (is.na(before)) Sys.unsetenv("MAS_DISPLAY_RENDERER_SOURCE_ONLY") else Sys.setenv(MAS_DISPLAY_RENDERER_SOURCE_ONLY = before))
  Sys.setenv(MAS_DISPLAY_RENDERER_SOURCE_ONLY = "1")
  if (any(template_ids != "cohort_flow_figure")) {
    source(file.path(pack_root, "rlib/medicaldisplaycore/evidence_renderer.R"), local = session)
    source(file.path(pack_root, "rlib/medicaldisplaycore/candidate_renderer.R"), local = session)
  }
  if ("cohort_flow_figure" %in% template_ids) {
    session$cohort_renderer <- new.env(parent = globalenv())
    source(file.path(pack_root, "rlib/medicaldisplaycore/cohort_flow_renderer.R"), local = session$cohort_renderer)
  }
  session
}

write_render_json <- function(value, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  temporary <- tempfile(pattern = ".render-", tmpdir = dirname(path))
  on.exit(unlink(temporary))
  jsonlite::write_json(value, temporary, auto_unbox = TRUE, pretty = TRUE, null = "null")
  if (!file.rename(temporary, path)) stop("cannot publish render result: ", path)
}

run_render_job <- function(job, session) {
  old_options <- options()
  old_environment <- Sys.getenv()
  old_devices <- dev.list()
  old_search <- search()
  old_directory <- getwd()
  old_global <- as.list(.GlobalEnv, all.names = TRUE)
  old_session <- as.list(session, all.names = TRUE)
  started <- proc.time()[["elapsed"]]
  output <- character()
  error <- NULL
  restoration_error <- NULL
  tryCatch({
    output <- capture.output({
      if (!is.null(job$seed)) set.seed(as.integer(job$seed))
      Sys.setenv(MAS_DISPLAY_RENDER_MODE = job$render_mode)
      if (identical(job$template_id, "cohort_flow_figure")) {
        session$cohort_renderer$render_cohort_flow_request(job$request_path)
      } else {
        session$render_evidence_request(job$request_path, expected_template_id = job$template_id)
      }
    }, type = "output")
  }, error = function(condition) error <<- conditionMessage(condition))
  tryCatch({
    added_options <- setdiff(names(options()), names(old_options))
    if (length(added_options)) options(stats::setNames(rep(list(NULL), length(added_options)), added_options))
    options(old_options)
    Sys.unsetenv(setdiff(names(Sys.getenv()), names(old_environment)))
    do.call(Sys.setenv, as.list(old_environment))
    for (device in rev(setdiff(dev.list(), old_devices))) dev.off(device)
    for (entry in rev(setdiff(search(), old_search))) detach(entry, character.only = TRUE, unload = FALSE)
    setwd(old_directory)
    restore_bindings <- function(target, before) {
      added <- setdiff(ls(target, all.names = TRUE), names(before))
      if (length(added)) rm(list = added, envir = target)
      list2env(before, envir = target)
    }
    restore_bindings(.GlobalEnv, old_global)
    restore_bindings(session, old_session)
    if (!identical(options(), old_options) || !identical(Sys.getenv(), old_environment) ||
        !identical(dev.list(), old_devices) || !identical(search(), old_search) ||
        !identical(getwd(), old_directory) ||
        !identical(as.list(.GlobalEnv, all.names = TRUE), old_global)) stop("state verification failed")
  }, error = function(condition) restoration_error <<- conditionMessage(condition))
  result <- list(case_id = job$case_id, template_id = job$template_id,
    request_path = job$request_path, ok = is.null(error) && is.null(restoration_error),
    stdout = paste(output, collapse = "\n"), error = error,
    restoration_error = restoration_error, elapsed_ms = (proc.time()[["elapsed"]] - started) * 1000,
    execution_id = Sys.getenv("OPL_ENV_EXECUTION_ID", unset = ""),
    environment_manifest_ref = Sys.getenv("OPL_ENV_MANIFEST_REF", unset = ""))
  write_render_json(result, paste0(job$request_path, ".execution.json"))
  result
}

run_render_batch <- function(batch_path, pack_root) {
  batch <- jsonlite::fromJSON(batch_path, simplifyVector = FALSE)
  jobs <- batch$jobs
  if (!is.list(jobs) || !length(jobs)) stop("batch requires non-empty jobs")
  ids <- vapply(jobs, function(job) if (is.null(job$case_id)) "" else job$case_id, character(1))
  if (any(!nzchar(ids)) || anyDuplicated(ids)) stop("batch case_id values must be unique and non-empty")
  outputs <- character()
  for (index in seq_along(jobs)) {
    job <- jobs[[index]]
    if (is.null(job$template_id) || !nzchar(job$template_id)) stop("batch job requires template_id")
    if (is.null(job$render_mode)) job$render_mode <- "final"
    if (!(job$render_mode %in% c("final", "candidate"))) stop("render mode must be final or candidate")
    job$request_path <- normalizePath(job$request_path, mustWork = TRUE)
    request <- jsonlite::fromJSON(job$request_path, simplifyVector = FALSE)
    paths <- unlist(request[c("output_png_path", "output_pdf_path", "layout_sidecar_path")], use.names = FALSE)
    paths <- c(paths, unlist(request$output_paths, use.names = FALSE))
    # Aliases within one request are normal; collisions between requests are not.
    paths <- unique(vapply(paths, function(path) {
      parent <- dirname(path)
      missing <- character()
      while (!dir.exists(parent)) { missing <- c(basename(parent), missing); parent <- dirname(parent) }
      do.call(file.path, as.list(c(normalizePath(parent), missing, basename(path))))
    }, character(1)))
    paths <- unique(c(paths, paste0(job$request_path, ".execution.json")))
    if (any(paths %in% outputs)) stop("batch output paths conflict")
    outputs <- c(outputs, paths)
    jobs[[index]] <- job
  }
  result_path <- if (is.null(batch$result_path)) paste0(batch_path, ".results.json") else batch$result_path
  if (normalizePath(result_path, mustWork = FALSE) %in% outputs) stop("batch result path conflicts with output")
  session <- load_render_session(pack_root, vapply(jobs, `[[`, character(1), "template_id"))
  results <- list()
  write_render_json(list(results = results, complete = FALSE), result_path)
  for (job in jobs) {
    result <- run_render_job(job, session)
    results[[length(results) + 1L]] <- result
    write_render_json(list(results = results, complete = length(results) == length(jobs)), result_path)
    if (!is.null(result$restoration_error)) break
  }
  payload <- list(results = results, complete = length(results) == length(jobs))
  jsonlite::write_json(payload, stdout(), auto_unbox = TRUE, null = "null")
  invisible(if (payload$complete && all(vapply(results, `[[`, logical(1), "ok"))) 0L else 1L)
}
