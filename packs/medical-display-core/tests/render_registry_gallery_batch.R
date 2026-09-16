#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("usage: render_registry_gallery_batch.R <batch-request.json>")
batch <- jsonlite::fromJSON(args[[1]], simplifyVector = FALSE)
source(file.path(batch$pack_root, "rlib/medicaldisplaycore/render_session.R"))
quit(status = run_render_batch(args[[1]], batch$pack_root))
