#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
request_path <- Sys.getenv("MAS_DISPLAY_RENDER_REQUEST", unset = "")
template_id <- Sys.getenv("MAS_DISPLAY_TEMPLATE_ID", unset = "")
render_mode <- Sys.getenv("MAS_DISPLAY_RENDER_MODE", unset = "")

batch_path <- ""
index <- 1
while (index <= length(args)) {
  token <- args[[index]]
  if (identical(token, "--batch") && index < length(args)) {
    batch_path <- args[[index + 1]]
    index <- index + 2
  } else if (identical(token, "--request") && index < length(args)) {
    request_path <- args[[index + 1]]
    index <- index + 2
  } else if (identical(token, "--template") && index < length(args)) {
    template_id <- args[[index + 1]]
    index <- index + 2
  } else if (identical(token, "--mode") && index < length(args)) {
    render_mode <- args[[index + 1]]
    index <- index + 2
  } else {
    stop(sprintf("unknown render option `%s`", token))
  }
}

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", grep("^--file=", script_args, value = TRUE)[[1]])
pack_root <- dirname(normalizePath(script_file, mustWork = TRUE))

source(file.path(pack_root, "rlib/medicaldisplaycore/render_session.R"))
if (nzchar(batch_path)) {
  if (nzchar(request_path) || nzchar(template_id)) stop("--batch cannot be combined with a single request")
  quit(status = run_render_batch(normalizePath(batch_path, mustWork = TRUE), pack_root))
}
if (!nzchar(request_path)) {
  stop("expected --request <request_json> or MAS_DISPLAY_RENDER_REQUEST")
}
if (!nzchar(template_id)) {
  stop("expected --template <template_id> or MAS_DISPLAY_TEMPLATE_ID")
}
if (!nzchar(render_mode)) {
  render_mode <- "final"
}
if (!(render_mode %in% c("final", "candidate"))) {
  stop("render mode must be final or candidate")
}

session <- load_render_session(pack_root, template_id)
job <- list(case_id = template_id, template_id = template_id, request_path = normalizePath(request_path, mustWork = TRUE), render_mode = render_mode)
result <- run_render_job(job, session)
if (!result$ok) stop(paste(c(result$error, result$restoration_error), collapse = "; "))
