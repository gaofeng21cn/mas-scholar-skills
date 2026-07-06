suppressPackageStartupMessages({
  library(jsonlite)
  library(ggplot2)
  library(ggsci)
  library(grid)
})

`%||%` <- function(left, right) {
  if (is.null(left)) right else left
}

source_renderer_helper <- function(file_name) {
  script_args <- commandArgs(trailingOnly = FALSE)
  script_file_args <- grep("^--file=", script_args, value = TRUE)
  script_dir <- ""
  if (length(script_file_args) > 0) {
    script_path <- sub("^--file=", "", script_file_args[[length(script_file_args)]])
    script_dir <- dirname(normalizePath(script_path, mustWork = FALSE))
  }
  frame_files <- vapply(sys.frames(), function(frame) {
    value <- frame$ofile %||% ""
    trimws(as.character(value))
  }, character(1))
  for (source_path in rev(frame_files[nzchar(frame_files)])) {
    helper_path <- file.path(dirname(normalizePath(source_path, mustWork = FALSE)), file_name)
    if (file.exists(helper_path)) {
      source(helper_path)
      return(invisible(TRUE))
    }
  }
  fallback_paths <- c(
    if (nzchar(script_dir)) file.path(script_dir, file_name) else character(0),
    file.path("..", "..", "rlib", "medicaldisplaycore", file_name),
    file_name
  )
  for (helper_path in fallback_paths) {
    if (file.exists(helper_path)) {
      source(helper_path)
      return(invisible(TRUE))
    }
  }
  stop(sprintf("renderer helper `%s` was not found", file_name))
}

source_renderer_helper("embedding_workflow.R")
source_renderer_helper("lidocaineq_publication_renderers.R")
source_renderer_helper("lidocaineq_curve_renderers.R")
source_renderer_helper("lidocaineq_survival_effect_heatmap_renderers.R")
source_renderer_helper("lidocaineq_ml_omics_renderers.R")

normalize_template_id <- function(value) {
  template_id <- trimws(as.character(value %||% ""))
  if (!nzchar(template_id)) {
    stop("template_id must be non-empty")
  }
  parts <- strsplit(template_id, "::", fixed = TRUE)[[1]]
  parts[[length(parts)]]
}

canonical_template_aliases <- function(expected_template_id) {
  switch(
    expected_template_id,
    time_dependent_roc_horizon = c(
      "time_dependent_roc_horizon",
      "time_dependent_roc_comparison_panel",
      "time_to_event_discrimination_calibration_panel",
      "time_to_event_landmark_performance_panel"
    ),
    risk_layering_monotonic_bars = c(
      "risk_layering_monotonic_bars",
      "time_to_event_risk_group_summary"
    ),
    expected_template_id
  )
}

read_render_request <- function(request_path) {
  request_json <- if (file.exists(request_path)) {
    paste(readLines(request_path, warn = FALSE), collapse = "\n")
  } else {
    request_path
  }
  request <- fromJSON(request_json, simplifyVector = FALSE)
  if (is.null(request$display_payload)) {
    stop("render request must contain display_payload")
  }
  request
}

payload_from_request <- function(request) {
  display_payload <- request$display_payload
  data_payload <- display_payload$data_payload
  if (!is.null(data_payload) && is.list(data_payload)) {
    merged_payload <- display_payload
    for (field_name in names(data_payload)) {
      merged_payload[[field_name]] <- data_payload[[field_name]]
    }
    displays <- merged_payload$displays
    if (is.list(displays) && length(displays) > 0) {
      short_template_id <- trimws(as.character(request$short_template_id %||% request$template_id %||% ""))
      selected_display <- displays[[1]]
      for (display in displays) {
        display_template_id <- trimws(as.character(display$template_id %||% ""))
        display_template_short <- sub("^.*::", "", display_template_id)
        if (
          nzchar(short_template_id)
          && (identical(display_template_id, short_template_id) || identical(display_template_short, short_template_id))
        ) {
          selected_display <- display
          break
        }
      }
      for (field_name in names(selected_display)) {
        merged_payload[[field_name]] <- selected_display[[field_name]]
      }
    }
    return(merged_payload)
  }
  display_payload
}

as_numeric_vector <- function(values, field_name) {
  if (!is.list(values) || length(values) < 2) {
    stop(sprintf("%s must contain at least two numeric values", field_name))
  }
  numeric_values <- vapply(values, function(item) {
    if (!is.numeric(item)) {
      stop(sprintf("%s must contain only numeric values", field_name))
    }
    as.numeric(item)
  }, numeric(1))
  numeric_values
}

source_renderer_helper("evidence_renderer_parts/style.R")

source_renderer_helper("evidence_renderer_parts/data_frames.R")

plot_binary_curve <- function(display_payload) {
  series_payload <- display_payload$series
  if (!is.list(series_payload) || length(series_payload) < 1) {
    stop("series must contain at least one curve")
  }
  curve_df <- build_curve_dataframe(series_payload)
  reference_df <- build_reference_dataframe(display_payload$reference_line)
  focus_window <- display_payload$decision_focus_window %||% display_payload$axis_window %||% list()
  xlim <- c(
    as.numeric(focus_window$xmin %||% 0),
    as.numeric(focus_window$xmax %||% 1)
  )
  ylim <- c(
    as.numeric(focus_window$ymin %||% min(curve_df$y, 0, na.rm = TRUE)),
    as.numeric(focus_window$ymax %||% max(curve_df$y, 1, na.rm = TRUE))
  )
  plot <- ggplot(curve_df, aes(x = x, y = y, colour = label)) +
    geom_line(linewidth = style_numeric(style_stroke(display_payload), "primary_linewidth", 2.2) * 0.42) +
    coord_cartesian(xlim = xlim, ylim = ylim) +
    scale_color_manual(
      values = style_series_palette(display_payload, unique(curve_df$label)),
      guide = publication_legend_guides(display_payload, curve_df$label)
    ) +
    labs(
      title = trimws(as.character(display_payload$title %||% "")),
      x = trimws(as.character(display_payload$x_label %||% "")),
      y = trimws(as.character(display_payload$y_label %||% ""))
    ) +
    theme_publication(display_payload)
  if (!is.null(reference_df)) {
    plot <- plot + geom_line(
      data = reference_df,
      aes(x = x, y = y),
      inherit.aes = FALSE,
      colour = style_color(display_payload, "reference_line", "neutral", "#6B7280"),
      linewidth = style_numeric(style_stroke(display_payload), "reference_linewidth", 1.0) * 0.6,
      linetype = "dashed"
    )
  }
  plot
}

plot_kaplan_meier <- function(display_payload) {
  groups_payload <- display_payload$groups
  if (!is.list(groups_payload) || length(groups_payload) < 1) {
    stop("groups must contain at least one survival series")
  }
  censor_frames <- list()
  frames <- lapply(seq_along(groups_payload), function(index) {
    item <- groups_payload[[index]]
    x <- as_numeric_vector(item$times, sprintf("groups[%d].times", index))
    y <- as_numeric_vector(item$values, sprintf("groups[%d].values", index))
    if (length(x) != length(y)) {
      stop(sprintf("groups[%d].times and groups[%d].values must have the same length", index, index))
    }
    label <- trimws(as.character(item$label %||% ""))
    censor_times <- item$censor_times %||% list()
    if (is.list(censor_times) && length(censor_times) > 0) {
      censor_x <- vapply(censor_times, as.numeric, numeric(1))
      censor_y <- vapply(censor_x, function(value) {
        eligible <- which(x <= value)
        if (length(eligible) < 1) y[[1]] else y[[max(eligible)]]
      }, numeric(1))
      censor_frames[[length(censor_frames) + 1]] <<- data.frame(
        label = rep(label, length(censor_x)),
        x = censor_x,
        y = censor_y,
        stringsAsFactors = FALSE
      )
    }
    data.frame(
      label = rep(label, length(x)),
      x = x,
      y = y,
      stringsAsFactors = FALSE
    )
  })
  curve_df <- do.call(rbind, frames)
  censor_df <- if (length(censor_frames) > 0) do.call(rbind, censor_frames) else NULL
  risk_table <- display_payload$risk_table %||% list()
  risk_rows <- if (is.list(risk_table) && length(risk_table) > 0) risk_table else list()
  risk_df <- if (length(risk_rows) > 0) {
    do.call(rbind, lapply(seq_along(risk_rows), function(index) {
      row <- risk_rows[[index]]
      data.frame(
        label = trimws(as.character(row$label %||% row$group_label %||% sprintf("Group %d", index))),
        time = vapply(row$times %||% list(), as.numeric, numeric(1)),
        at_risk = vapply(row$at_risk %||% row$counts %||% list(), as.integer, integer(1)),
        row_index = index,
        stringsAsFactors = FALSE
      )
    }))
  } else {
    NULL
  }
  y_lower <- if (is.null(risk_df)) 0 else -0.19
  palette_values <- style_series_palette(display_payload, unique(curve_df$label))
  plot <- ggplot(curve_df, aes(x = x, y = y, colour = label)) +
    geom_step(linewidth = style_numeric(style_stroke(display_payload), "primary_linewidth", 2.2) * 0.42, direction = "hv") +
    coord_cartesian(xlim = c(0, max(curve_df$x)), ylim = c(y_lower, 1), clip = "off") +
    scale_color_manual(
      values = palette_values,
      guide = publication_legend_guides(display_payload, curve_df$label)
    ) +
    scale_y_continuous(breaks = c(0, 0.25, 0.50, 0.75, 1.00)) +
    labs(
      title = trimws(as.character(display_payload$title %||% "")),
      x = trimws(as.character(display_payload$x_label %||% "")),
      y = trimws(as.character(display_payload$y_label %||% ""))
    ) +
    theme_publication(display_payload)
  if (!is.null(censor_df)) {
    plot <- plot + geom_point(
      data = censor_df,
      aes(x = x, y = y, colour = label),
      inherit.aes = FALSE,
      shape = 124,
      stroke = 0.9,
      size = style_numeric(style_stroke(display_payload), "marker_size", 3.4) * 0.86,
      show.legend = FALSE
    )
  }
  if (!is.null(risk_df)) {
    row_count <- length(unique(risk_df$row_index))
    risk_df$risk_y <- -0.055 - (risk_df$row_index - 1) * 0.055
    risk_label_df <- unique(risk_df[, c("label", "row_index", "risk_y"), drop = FALSE])
    risk_title <- trimws(as.character(display_payload$risk_table_title %||% "At risk"))
    max_time <- max(curve_df$x, na.rm = TRUE)
    risk_label_x <- -max_time * 0.055
    plot <- plot +
      annotate(
        "text",
        x = risk_label_x,
        y = -0.025,
        label = risk_title,
        hjust = 1,
        size = style_numeric(style_typography(display_payload), "tick_size", 10.0) * 0.30,
        colour = style_text_color(display_payload)
      ) +
      geom_text(
        data = risk_label_df,
        aes(x = risk_label_x, y = risk_y, label = label, colour = label),
        inherit.aes = FALSE,
        hjust = 1,
        size = style_numeric(style_typography(display_payload), "tick_size", 10.0) * 0.28,
        show.legend = FALSE
      ) +
      geom_text(
        data = risk_df,
        aes(x = time, y = risk_y, label = at_risk),
        inherit.aes = FALSE,
        size = style_numeric(style_typography(display_payload), "tick_size", 10.0) * 0.28,
        colour = style_text_color(display_payload)
      ) +
      theme(plot.margin = margin(10, 12, 22 + row_count * 5, 42))
  }
  annotation <- trimws(as.character(display_payload$annotation %||% ""))
  if (nzchar(annotation)) {
    annotation_y <- if (grepl("cumulative", tolower(trimws(as.character(display_payload$y_label %||% ""))))) {
      max(curve_df$y, na.rm = TRUE) * 0.52
    } else {
      0.08
    }
    plot <- plot + annotate(
      "text",
      x = max(curve_df$x) * 0.98,
      y = annotation_y,
      label = annotation,
      hjust = 1,
      vjust = 0,
      size = style_numeric(style_typography(display_payload), "tick_size", 10.0) * 0.33,
      colour = style_text_color(display_payload)
    )
  }
  plot
}

plot_embedding_scatter <- function(display_payload) {
  points_payload <- display_payload$points
  if (!is.list(points_payload) || length(points_payload) < 1) {
    stop("points must contain at least one observation")
  }
  point_df <- build_point_dataframe(points_payload)
  plot <- ggplot(point_df, aes(x = x, y = y, colour = group)) +
    geom_point(size = style_numeric(style_stroke(display_payload), "marker_size", 4.5) * 0.62, alpha = 0.9) +
    scale_color_manual(
      values = style_series_palette(display_payload, unique(point_df$group)),
      guide = publication_legend_guides(display_payload, point_df$group)
    ) +
    labs(
      title = trimws(as.character(display_payload$title %||% "")),
      x = trimws(as.character(display_payload$x_label %||% "")),
      y = trimws(as.character(display_payload$y_label %||% ""))
    ) +
    theme_publication(display_payload)
  plot
}

plot_heatmap <- function(display_payload) {
  cells_payload <- display_payload$cells
  if (!is.list(cells_payload) || length(cells_payload) < 1) {
    stop("cells must contain at least one matrix entry")
  }
  column_order <- if (is.null(display_payload$column_order)) NULL else extract_label_vector(display_payload$column_order, "column_order")
  row_order <- if (is.null(display_payload$row_order)) NULL else extract_label_vector(display_payload$row_order, "row_order")
  heat_df <- build_heatmap_dataframe(cells_payload, column_order = column_order, row_order = row_order)
  heat_df$text_colour <- heatmap_text_colours(display_payload, heat_df$value)
  plot <- ggplot(heat_df, aes(x = x, y = y, fill = value)) +
    geom_tile(colour = "white", linewidth = 0.5) +
    geom_text(aes(label = sprintf("%.2f", value), colour = text_colour), size = style_numeric(style_typography(display_payload), "tick_size", 10.0) * 0.31, show.legend = FALSE) +
    scale_colour_identity() +
    heatmap_fill_scale(display_payload, heat_df$value) +
    labs(
      title = trimws(as.character(display_payload$title %||% "")),
      x = trimws(as.character(display_payload$x_label %||% "")),
      y = trimws(as.character(display_payload$y_label %||% ""))
    ) +
    theme_publication(display_payload) +
    theme_publication_colorbar(display_payload) +
    theme(axis.text.x = element_text(angle = 25, hjust = 1))
  plot
}

plot_performance_heatmap <- function(display_payload) {
  cells_payload <- display_payload$cells
  if (!is.list(cells_payload) || length(cells_payload) < 1) {
    stop("cells must contain at least one matrix entry")
  }
  metric_name <- trimws(as.character(display_payload$metric_name %||% ""))
  if (!nzchar(metric_name)) {
    stop("metric_name must be non-empty")
  }
  column_order <- if (is.null(display_payload$column_order)) NULL else extract_label_vector(display_payload$column_order, "column_order")
  row_order <- if (is.null(display_payload$row_order)) NULL else extract_label_vector(display_payload$row_order, "row_order")
  heat_df <- build_heatmap_dataframe(cells_payload, column_order = column_order, row_order = row_order)
  heat_df$text_colour <- heatmap_text_colours(display_payload, heat_df$value)
  plot <- ggplot(heat_df, aes(x = x, y = y, fill = value)) +
    geom_tile(colour = "white", linewidth = 0.5) +
    geom_text(aes(label = sprintf("%.2f", value), colour = text_colour), size = style_numeric(style_typography(display_payload), "tick_size", 10.0) * 0.31, show.legend = FALSE) +
    scale_colour_identity() +
    heatmap_fill_scale(display_payload, heat_df$value, name = metric_name, limits = c(0, 1)) +
    labs(
      title = trimws(as.character(display_payload$title %||% "")),
      x = trimws(as.character(display_payload$x_label %||% "")),
      y = trimws(as.character(display_payload$y_label %||% ""))
    ) +
    theme_publication(display_payload) +
    theme_publication_colorbar(display_payload) +
    theme(axis.text.x = element_text(angle = 25, hjust = 1))
  plot
}

plot_confusion_matrix_heatmap <- function(display_payload) {
  cells_payload <- display_payload$cells
  if (!is.list(cells_payload) || length(cells_payload) < 1) {
    stop("cells must contain at least one matrix entry")
  }
  metric_name <- trimws(as.character(display_payload$metric_name %||% ""))
  if (!nzchar(metric_name)) {
    stop("metric_name must be non-empty")
  }
  normalization <- trimws(as.character(display_payload$normalization %||% ""))
  if (!normalization %in% c("row_fraction", "column_fraction", "overall_fraction")) {
    stop("normalization must be one of row_fraction, column_fraction, or overall_fraction")
  }
  column_order <- if (is.null(display_payload$column_order)) NULL else extract_label_vector(display_payload$column_order, "column_order")
  row_order <- if (is.null(display_payload$row_order)) NULL else extract_label_vector(display_payload$row_order, "row_order")
  heat_df <- build_heatmap_dataframe(cells_payload, column_order = column_order, row_order = row_order)
  heat_df$text_colour <- heatmap_text_colours(display_payload, heat_df$value)
  plot <- ggplot(heat_df, aes(x = x, y = y, fill = value)) +
    geom_tile(colour = "white", linewidth = 0.7) +
    geom_text(aes(label = sprintf("%.0f%%", value * 100), colour = text_colour), size = style_numeric(style_typography(display_payload), "axis_title_size", 11.0) * 0.38, fontface = "bold", show.legend = FALSE) +
    scale_colour_identity() +
    heatmap_fill_scale(display_payload, heat_df$value, name = metric_name, limits = c(0, 1)) +
    labs(
      title = trimws(as.character(display_payload$title %||% "")),
      x = trimws(as.character(display_payload$x_label %||% "")),
      y = trimws(as.character(display_payload$y_label %||% ""))
    ) +
    theme_publication(display_payload) +
    theme_publication_colorbar(display_payload) +
    theme(
      axis.text.x = element_text(angle = 0, hjust = 0.5),
      axis.text.y = element_text(face = "bold"),
      axis.text = element_text(face = "bold"),
      panel.grid.major = element_blank()
    )
  plot
}

plot_forest <- function(display_payload) {
  rows_payload <- display_payload$rows
  if (!is.list(rows_payload) || length(rows_payload) < 1) {
    stop("rows must contain at least one effect estimate")
  }
  forest_df <- build_forest_dataframe(rows_payload)
  reference_value <- as.numeric(display_payload$reference_value %||% 1.0)
  plot <- ggplot(forest_df, aes(y = label, x = estimate)) +
    geom_vline(xintercept = reference_value, colour = style_color(display_payload, "reference_line", "neutral", "#6B7280"), linewidth = style_numeric(style_stroke(display_payload), "reference_linewidth", 1.0) * 0.6, linetype = "dashed") +
    geom_segment(aes(x = lower, xend = upper, y = label, yend = label), linewidth = style_numeric(style_stroke(display_payload), "primary_linewidth", 2.2) * 0.42, colour = style_color(display_payload, "model_curve", "primary", "#1F4E79")) +
    geom_point(size = style_numeric(style_stroke(display_payload), "marker_size", 4.5) * 0.62, colour = style_color(display_payload, "model_curve", "primary", "#1F4E79")) +
    labs(
      title = trimws(as.character(display_payload$title %||% "")),
      x = trimws(as.character(display_payload$x_label %||% "")),
      y = ""
    ) +
    theme_publication(display_payload)
  plot
}

source_renderer_helper("evidence_renderer_parts/layouts.R")

build_evidence_plot <- function(template_id, payload) {
  lidocaineq_plot <- if (exists("build_lidocaineq_evidence_plot", mode = "function")) {
    build_lidocaineq_evidence_plot(template_id, payload)
  } else {
    NULL
  }
  if (!is.null(lidocaineq_plot)) {
    return(lidocaineq_plot)
  }
  switch(
    template_id,
    roc_curve_binary = plot_binary_curve(payload),
    pr_curve_binary = plot_binary_curve(payload),
    calibration_curve_binary = plot_binary_curve(payload),
    decision_curve_binary = plot_binary_curve(payload),
    time_dependent_roc_horizon = plot_binary_curve(payload),
    kaplan_meier_grouped = plot_kaplan_meier(payload),
    cumulative_incidence_grouped = plot_kaplan_meier(payload),
    umap_scatter_grouped = plot_dimensionality_reduction_embedding(template_id, payload),
    pca_scatter_grouped = plot_dimensionality_reduction_embedding(template_id, payload),
    tsne_scatter_grouped = plot_dimensionality_reduction_embedding(template_id, payload),
    heatmap_group_comparison = plot_heatmap(payload),
    confusion_matrix_heatmap_binary = plot_confusion_matrix_heatmap(payload),
    forest_effect_main = plot_forest(payload),
    if (exists("build_candidate_evidence_plot", mode = "function")) {
      build_candidate_evidence_plot(template_id, payload)
    } else {
      stop(sprintf("unsupported evidence template `%s`", template_id))
    }
  )
}

render_evidence_request <- function(request_path, expected_template_id = NULL) {
  request <- read_render_request(request_path)
  template_id <- normalize_template_id(request$short_template_id %||% request$template_id)
  if (!is.null(expected_template_id)) {
    expected <- normalize_template_id(expected_template_id)
    allowed_template_ids <- canonical_template_aliases(expected)
    if (!(template_id %in% allowed_template_ids)) {
      stop(sprintf("render request template `%s` does not match expected template `%s`", template_id, expected))
    }
  }
  payload <- payload_from_request(request)
  output_png <- trimws(as.character(request$output_png_path %||% ""))
  output_pdf <- trimws(as.character(request$output_pdf_path %||% ""))
  output_layout <- trimws(as.character(request$layout_sidecar_path %||% ""))
  if (!nzchar(output_png) || !nzchar(output_pdf) || !nzchar(output_layout)) {
    stop("render request must contain output_png_path, output_pdf_path, and layout_sidecar_path")
  }
  dir.create(dirname(output_png), recursive = TRUE, showWarnings = FALSE)
  dir.create(dirname(output_pdf), recursive = TRUE, showWarnings = FALSE)
  dir.create(dirname(output_layout), recursive = TRUE, showWarnings = FALSE)
  plot <- build_evidence_plot(template_id, payload)
  layout_sidecar <- build_layout_sidecar(plot, template_id, payload)
  write_json(layout_sidecar, output_layout, auto_unbox = TRUE, pretty = TRUE, null = "null")
  output_width <- render_device_dimension(payload, "output_width_in", "MAS_DISPLAY_OUTPUT_WIDTH_IN", 7.2)
  output_height <- render_device_dimension(payload, "output_height_in", "MAS_DISPLAY_OUTPUT_HEIGHT_IN", 5.0)
  save_rendered_plot(plot, output_png, output_pdf, output_width, output_height)
  invisible(list(template_id = template_id, output_png_path = output_png, output_pdf_path = output_pdf, layout_sidecar_path = output_layout))
}

render_legacy_payload <- function(template_id, payload_path, output_png, output_pdf, output_layout) {
  payload <- fromJSON(payload_path, simplifyVector = FALSE)
  request <- list(
    short_template_id = template_id,
    display_payload = payload,
    output_png_path = output_png,
    output_pdf_path = output_pdf,
    layout_sidecar_path = output_layout
  )
  request_path <- tempfile(fileext = ".render_request.json")
  write_json(request, request_path, auto_unbox = TRUE, pretty = TRUE, null = "null")
  on.exit(unlink(request_path), add = TRUE)
  render_evidence_request(request_path, expected_template_id = template_id)
}

if (!identical(Sys.getenv("MAS_DISPLAY_RENDERER_SOURCE_ONLY", unset = ""), "1")) {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) == 0) {
    invisible(NULL)
  } else if (length(args) == 2 && args[[1]] %in% c("--request", "--file")) {
    render_evidence_request(args[[2]])
  } else if (length(args) == 5) {
    render_legacy_payload(args[[1]], args[[2]], args[[3]], args[[4]], args[[5]])
  } else {
    stop("expected args: --request <request_json> or <template_id> <payload_json> <output_png> <output_pdf> <output_layout>")
  }
}
