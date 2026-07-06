#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
request_path <- Sys.getenv("MAS_DISPLAY_RENDER_REQUEST", unset = "")
template_id <- Sys.getenv("MAS_DISPLAY_TEMPLATE_ID", unset = "")
render_mode <- Sys.getenv("MAS_DISPLAY_RENDER_MODE", unset = "")

index <- 1
while (index <= length(args)) {
  token <- args[[index]]
  if (identical(token, "--request") && index < length(args)) {
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

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- sub("^--file=", "", grep("^--file=", script_args, value = TRUE)[[1]])
pack_root <- dirname(normalizePath(script_file, mustWork = TRUE))

old_source_only <- Sys.getenv("MAS_DISPLAY_RENDERER_SOURCE_ONLY", unset = "")
old_render_mode <- Sys.getenv("MAS_DISPLAY_RENDER_MODE", unset = "")
Sys.setenv(MAS_DISPLAY_RENDERER_SOURCE_ONLY = "1")
Sys.setenv(MAS_DISPLAY_RENDER_MODE = render_mode)
source(file.path(pack_root, "rlib", "medicaldisplaycore", "evidence_renderer.R"))
source(file.path(pack_root, "rlib", "medicaldisplaycore", "candidate_renderer.R"))
if (nzchar(old_source_only)) {
  Sys.setenv(MAS_DISPLAY_RENDERER_SOURCE_ONLY = old_source_only)
} else {
  Sys.unsetenv("MAS_DISPLAY_RENDERER_SOURCE_ONLY")
}
if (nzchar(old_render_mode)) {
  Sys.setenv(MAS_DISPLAY_RENDER_MODE = old_render_mode)
} else {
  Sys.unsetenv("MAS_DISPLAY_RENDER_MODE")
}

render_evidence_request(request_path, expected_template_id = template_id)
