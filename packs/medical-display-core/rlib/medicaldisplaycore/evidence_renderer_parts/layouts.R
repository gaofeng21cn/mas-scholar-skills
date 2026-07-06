box_record <- function(box_id, box_type, x0, y0, x1, y1) {
  list(
    box_id = box_id,
    box_type = box_type,
    x0 = as.numeric(x0),
    y0 = as.numeric(y0),
    x1 = as.numeric(x1),
    y1 = as.numeric(y1)
  )
}

layout_box_from_indices <- function(widths, heights, left, right, top, bottom, box_id, box_type) {
  x0 <- if (left <= 1) 0 else sum(widths[seq_len(left - 1)])
  x1 <- sum(widths[seq_len(right)])
  y1 <- 1 - if (top <= 1) 0 else sum(heights[seq_len(top - 1)])
  y0 <- 1 - sum(heights[seq_len(bottom)])
  box_record(box_id, box_type, x0, y0, x1, y1)
}

resolved_layout_unit_sizes <- function(units, total_inches, axis) {
  unit_types <- as.character(grid::unitType(units))
  sizes <- numeric(length(units))
  null_weights <- numeric(length(units))
  for (index in seq_along(units)) {
    if (identical(unit_types[[index]], "null")) {
      null_weights[[index]] <- max(0, as.numeric(units[index]))
      next
    }
    converted <- suppressWarnings(if (identical(axis, "width")) {
      grid::convertWidth(units[index], "in", valueOnly = TRUE)
    } else {
      grid::convertHeight(units[index], "in", valueOnly = TRUE)
    })
    if (is.finite(converted)) {
      sizes[[index]] <- max(0, as.numeric(converted))
    }
  }
  null_total <- sum(null_weights)
  if (null_total > 0) {
    remaining <- max(as.numeric(total_inches) - sum(sizes), 0)
    sizes[null_weights > 0] <- remaining * null_weights[null_weights > 0] / null_total
  }
  if (!is.finite(total_inches) || total_inches <= 0) {
    return(sizes)
  }
  sizes / as.numeric(total_inches)
}

find_layout_box <- function(gt, widths, heights, prefixes, box_id, box_type) {
  layout_names <- gt$layout$name
  layout_index <- integer(0)
  for (prefix in prefixes) {
    matches <- which(startsWith(layout_names, prefix))
    if (length(matches) > 0) {
      layout_index <- matches
      break
    }
  }
  if (length(layout_index) < 1) {
    return(NULL)
  }
  row <- gt$layout[layout_index[1], , drop = FALSE]
  layout_box_from_indices(widths, heights, row$l[[1]], row$r[[1]], row$t[[1]], row$b[[1]], box_id, box_type)
}

map_value_to_panel_x <- function(value, panel_box, x_min, x_max) {
  if (!is.finite(x_min) || !is.finite(x_max) || identical(x_min, x_max)) {
    return((panel_box$x0 + panel_box$x1) / 2)
  }
  span <- panel_box$x1 - panel_box$x0
  panel_box$x0 + ((value - x_min) / (x_max - x_min)) * span
}

map_row_to_panel_y <- function(row_index, row_count, panel_box) {
  row_height <- (panel_box$y1 - panel_box$y0) / max(row_count, 1)
  panel_box$y1 - ((row_index - 0.5) * row_height)
}

build_forest_layout <- function(display_payload, panel_box, axis_left_box) {
  rows <- display_payload$rows
  if (!is.list(rows) || length(rows) < 1) {
    return(list(layout_boxes = list(), guide_boxes = list(), metrics = list(rows = list())))
  }
  reference_value <- as.numeric(display_payload$reference_value %||% 1.0)
  lower_values <- vapply(rows, function(item) as.numeric(item$lower), numeric(1))
  estimate_values <- vapply(rows, function(item) as.numeric(item$estimate), numeric(1))
  upper_values <- vapply(rows, function(item) as.numeric(item$upper), numeric(1))
  x_min <- min(c(lower_values, estimate_values, upper_values, reference_value), na.rm = TRUE)
  x_max <- max(c(lower_values, estimate_values, upper_values, reference_value), na.rm = TRUE)
  if (identical(x_min, x_max)) {
    x_min <- x_min - 0.5
    x_max <- x_max + 0.5
  }
  row_count <- length(rows)
  label_box <- axis_left_box %||% box_record("axis_left", "axis_left", 0.02, panel_box$y0, max(0.03, panel_box$x0 - 0.04), panel_box$y1)
  row_height <- (panel_box$y1 - panel_box$y0) / max(row_count, 1) * 0.55
  layout_boxes <- list()
  metric_rows <- list()
  for (index in seq_along(rows)) {
    row <- rows[[index]]
    row_center <- map_row_to_panel_y(index, row_count, panel_box)
    lower_x <- map_value_to_panel_x(as.numeric(row$lower), panel_box, x_min, x_max)
    estimate_x <- map_value_to_panel_x(as.numeric(row$estimate), panel_box, x_min, x_max)
    upper_x <- map_value_to_panel_x(as.numeric(row$upper), panel_box, x_min, x_max)
    layout_boxes[[length(layout_boxes) + 1]] <- box_record(
      sprintf("row_label_%d", index),
      "row_label",
      label_box$x0,
      row_center - row_height / 2,
      label_box$x1,
      row_center + row_height / 2
    )
    layout_boxes[[length(layout_boxes) + 1]] <- box_record(
      sprintf("estimate_marker_%d", index),
      "estimate_marker",
      estimate_x - 0.01,
      row_center - row_height / 4,
      estimate_x + 0.01,
      row_center + row_height / 4
    )
    layout_boxes[[length(layout_boxes) + 1]] <- box_record(
      sprintf("ci_segment_%d", index),
      "ci_segment",
      lower_x,
      row_center,
      upper_x,
      row_center
    )
    metric_rows[[length(metric_rows) + 1]] <- list(
      row_id = trimws(as.character(row$label %||% sprintf("row_%d", index))),
      label = trimws(as.character(row$label %||% "")),
      lower = as.numeric(row$lower),
      estimate = as.numeric(row$estimate),
      upper = as.numeric(row$upper)
    )
  }
  reference_x <- map_value_to_panel_x(reference_value, panel_box, x_min, x_max)
  guide_boxes <- list(
    box_record("reference_line", "reference_line", reference_x, panel_box$y0, reference_x, panel_box$y1)
  )
  list(layout_boxes = layout_boxes, guide_boxes = guide_boxes, metrics = list(rows = metric_rows))
}

build_embedding_metrics <- function(display_payload, panel_box) {
  points <- display_payload$points
  if (is.null(panel_box) || !is.list(points) || length(points) < 1) {
    return(list(points = list()))
  }
  x_values <- vapply(points, function(item) as.numeric(item$x), numeric(1))
  y_values <- vapply(points, function(item) as.numeric(item$y), numeric(1))
  x_min <- min(x_values)
  x_max <- max(x_values)
  y_min <- min(y_values)
  y_max <- max(y_values)
  if (identical(x_min, x_max)) {
    x_min <- x_min - 0.5
    x_max <- x_max + 0.5
  }
  if (identical(y_min, y_max)) {
    y_min <- y_min - 0.5
    y_max <- y_max + 0.5
  }
  point_metrics <- lapply(points, function(item) {
    list(
      x = map_value_to_panel_x(as.numeric(item$x), panel_box, x_min, x_max),
      y = panel_box$y0 + ((as.numeric(item$y) - y_min) / (y_max - y_min)) * (panel_box$y1 - panel_box$y0),
      group = trimws(as.character(item$group %||% ""))
    )
  })
  list(points = point_metrics)
}

build_metrics <- function(template_id, display_payload, panel_box) {
  lidocaineq_metrics <- if (exists("build_lidocaineq_metrics", mode = "function")) {
    build_lidocaineq_metrics(template_id, display_payload, panel_box)
  } else {
    NULL
  }
  if (!is.null(lidocaineq_metrics)) {
    return(lidocaineq_metrics)
  }
  switch(
    template_id,
    roc_curve_binary = list(series = display_payload$series, reference_line = display_payload$reference_line),
    pr_curve_binary = list(series = display_payload$series, reference_line = display_payload$reference_line),
    calibration_curve_binary = list(series = display_payload$series, reference_line = display_payload$reference_line),
    decision_curve_binary = list(series = display_payload$series, reference_line = display_payload$reference_line),
    time_dependent_roc_horizon = list(
      series = display_payload$series,
      reference_line = display_payload$reference_line,
      title = trimws(as.character(display_payload$title %||% "")),
      caption = trimws(as.character(display_payload$caption %||% "")),
      time_horizon_months = if (!is.null(display_payload$time_horizon_months)) as.integer(display_payload$time_horizon_months) else NULL
    ),
    kaplan_meier_grouped = list(
      groups = display_payload$groups,
      annotation = trimws(as.character(display_payload$annotation %||% ""))
    ),
    cumulative_incidence_grouped = list(
      groups = display_payload$groups,
      annotation = trimws(as.character(display_payload$annotation %||% ""))
    ),
    umap_scatter_grouped = build_dimensionality_reduction_metrics(template_id, display_payload, panel_box),
    pca_scatter_grouped = build_dimensionality_reduction_metrics(template_id, display_payload, panel_box),
    tsne_scatter_grouped = build_dimensionality_reduction_metrics(template_id, display_payload, panel_box),
    heatmap_group_comparison = list(metric_scope = "heatmap_group_comparison"),
    confusion_matrix_heatmap_binary = list(
      matrix_cells = display_payload$cells,
      metric_name = trimws(as.character(display_payload$metric_name %||% "")),
      normalization = trimws(as.character(display_payload$normalization %||% ""))
    ),
    forest_effect_main = list(rows = display_payload$rows),
    if (exists("build_candidate_metrics", mode = "function")) {
      build_candidate_metrics(template_id, display_payload, panel_box)
    } else {
      list()
    }
  )
}

default_renderer_metrics <- function(template_id, display_payload, panel_box) {
  declared_panel_ids <- vapply(display_payload$panels %||% list(), function(panel) {
    trimws(as.character(panel$panel_id %||% ""))
  }, character(1))
  declared_panel_ids <- declared_panel_ids[nzchar(declared_panel_ids)]
  observed_panel_ids <- if (length(declared_panel_ids) == 1 && !is.null(panel_box)) declared_panel_ids else character(0)
  list(
    renderer = "r_ggplot2_evidence_subprocess_v1",
    renderer_family = "r_ggplot2",
    renderer_role = "default",
    template_id = template_id,
    source_renderer = sprintf("MAS/DisplayPack::%s", template_id),
    figure_purpose = figure_purpose_for_template(template_id),
    rendered_title_policy = "figure_title_metadata_only_not_drawn_inside_plot",
    data_fields = sort(names(display_payload)),
    panel_ids = observed_panel_ids,
    panel_box_present = !is.null(panel_box)
  )
}

figure_purpose_for_template <- function(template_id) {
  switch(
    template_id,
    roc_curve_binary = "binary_discrimination_curve_with_reference_line",
    time_dependent_roc_horizon = "time_to_event_discrimination_curve_at_fixed_horizon",
    time_to_event_discrimination_calibration_panel = "time_to_event_discrimination_plus_calibration_summary",
    calibration_curve_binary = "observed_vs_predicted_calibration_assessment",
    pr_curve_binary = "precision_recall_tradeoff_for_imbalanced_binary_outcome",
    decision_curve_binary = "clinical_net_benefit_threshold_utility_curve",
    time_to_event_decision_curve = "time_to_event_net_benefit_plus_treated_fraction_summary",
    risk_layering_monotonic_bars = "risk_stratification_monotonicity_and_event_gradient",
    time_to_event_risk_group_summary = "time_to_event_risk_group_gradient_plus_event_counts",
    kaplan_meier_grouped = "grouped_time_to_event_survival_curve",
    cumulative_incidence_grouped = "grouped_cumulative_incidence_curve",
    time_to_event_multihorizon_calibration_panel = "multi_horizon_time_to_event_calibration_assessment",
    center_transportability_governance_summary_panel = "transportability_discrimination_plus_recalibration_governance_decision_matrix",
    phenotype_gap_structure_figure = "phenotype_composition_plus_treatment_gap_matrix",
    site_held_out_stability_figure = "phenotype_transition_stability_plus_site_held_out_support",
    treatment_gap_alignment_figure = "guideline_linked_treatment_gap_burden_small_multiples",
    sprintf("purpose_first_%s", template_id)
  )
}

ensure_renderer_metrics <- function(template_id, display_payload, panel_box, metrics) {
  if (is.null(metrics) || !is.list(metrics)) {
    metrics <- list()
  }
  renderer_metrics <- default_renderer_metrics(template_id, display_payload, panel_box)
  missing_fields <- setdiff(names(renderer_metrics), names(metrics))
  c(renderer_metrics[missing_fields], metrics)
}

style_profile_sidecar <- function(display_payload) {
  render_context <- render_context_from_payload(display_payload)
  palette <- render_context$palette %||% list()
  list(
    style_profile_id = render_context$style_profile_id %||% "",
    style_profile_ref = render_context$style_profile_ref %||% "",
    style_profile_sha256 = render_context$style_profile_sha256 %||% "",
    journal_palette_ref = render_context$journal_palette_ref %||% "",
    palette_keys = names(palette),
    semantic_roles = render_context$semantic_roles %||% list(),
    typography = render_context$typography %||% list(),
    stroke = render_context$stroke %||% list(),
    grid = render_context$grid %||% list()
  )
}

render_device_dimension <- function(display_payload, field_name, env_name, fallback) {
  render_context <- render_context_from_payload(display_payload)
  layout_override <- render_context$layout_override %||% list()
  value <- layout_override[[field_name]]
  if (is.null(value)) {
    value <- Sys.getenv(env_name, unset = "")
  }
  if (is.null(value) || !nzchar(trimws(as.character(value)))) {
    return(as.numeric(fallback))
  }
  numeric_value <- suppressWarnings(as.numeric(value))
  if (!is.finite(numeric_value) || numeric_value <= 0) {
    return(as.numeric(fallback))
  }
  numeric_value
}

is_grid_renderable <- function(plot) {
  inherits(plot, "grob") || inherits(plot, "gTree") || inherits(plot, "gtable")
}

is_base_graphics_renderable <- function(plot) {
  inherits(plot, "lidocaine_base_graphics_plot") && is.function(plot$draw)
}

save_grid_renderable <- function(plot, output_png, output_pdf, output_width, output_height) {
  grDevices::png(output_png, width = output_width, height = output_height, units = "in", res = 320, bg = "white")
  grid::grid.newpage()
  grid::grid.draw(plot)
  grDevices::dev.off()
  grDevices::pdf(output_pdf, width = output_width, height = output_height, bg = "white")
  grid::grid.newpage()
  grid::grid.draw(plot)
  grDevices::dev.off()
}

save_base_graphics_renderable <- function(plot, output_png, output_pdf, output_width, output_height) {
  grDevices::png(output_png, width = output_width, height = output_height, units = "in", res = 320, bg = "white")
  plot$draw()
  grDevices::dev.off()
  grDevices::pdf(output_pdf, width = output_width, height = output_height, bg = "white", useDingbats = FALSE)
  plot$draw()
  grDevices::dev.off()
}

save_rendered_plot <- function(plot, output_png, output_pdf, output_width, output_height) {
  if (is_base_graphics_renderable(plot)) {
    save_base_graphics_renderable(plot, output_png, output_pdf, output_width, output_height)
    return(invisible(TRUE))
  }
  if (is_grid_renderable(plot)) {
    save_grid_renderable(plot, output_png, output_pdf, output_width, output_height)
    return(invisible(TRUE))
  }
  ggsave(output_png, plot = plot, width = output_width, height = output_height, dpi = 320, units = "in", bg = "white")
  ggsave(output_pdf, plot = plot, width = output_width, height = output_height, units = "in", bg = "white")
  invisible(TRUE)
}

build_layout_sidecar <- function(plot, template_id, display_payload) {
  declared_panel_ids <- vapply(display_payload$panels %||% list(), function(panel) {
    trimws(as.character(panel$panel_id %||% ""))
  }, character(1))
  declared_panel_ids <- declared_panel_ids[nzchar(declared_panel_ids)]
  if (is_base_graphics_renderable(plot)) {
    panel_box <- list(box_id = "base_graphics_panel", box_type = "panel", x0 = 0.04, y0 = 0.06, x1 = 0.96, y1 = 0.94)
    if (length(declared_panel_ids) == 1) {
      panel_box$panel_id <- declared_panel_ids[[1]]
    }
    metrics <- ensure_renderer_metrics(template_id, display_payload, panel_box, build_metrics(template_id, display_payload, panel_box))
    return(list(
      template_id = template_id,
      device = list(x0 = 0.0, y0 = 0.0, x1 = 1.0, y1 = 1.0),
      layout_boxes = list(),
      panel_boxes = list(panel_box),
      guide_boxes = list(),
      metrics = metrics,
      render_context = render_context_sidecar(display_payload),
      style_profile = style_profile_sidecar(display_payload)
    ))
  }
  if (is_grid_renderable(plot)) {
    grob_panel_type <- if (template_id %in% c("heatmap_group_comparison")) "heatmap_tile_region" else "table_region"
    grob_panel_id <- if (identical(grob_panel_type, "heatmap_tile_region")) "heatmap_panel" else "table_panel"
    guide_boxes <- if (identical(grob_panel_type, "heatmap_tile_region")) {
      list(list(box_id = "heatmap_colorbar", box_type = "colorbar", x0 = 0.86, y0 = 0.18, x1 = 0.96, y1 = 0.86))
    } else {
      list()
    }
    panel_box <- list(box_id = grob_panel_id, box_type = grob_panel_type, x0 = 0.04, y0 = 0.06, x1 = 0.96, y1 = 0.94)
    if (length(declared_panel_ids) == 1) {
      panel_box$panel_id <- declared_panel_ids[[1]]
    }
    metrics <- ensure_renderer_metrics(template_id, display_payload, panel_box, build_metrics(template_id, display_payload, panel_box))
    return(list(
      template_id = template_id,
      device = list(x0 = 0.0, y0 = 0.0, x1 = 1.0, y1 = 1.0),
      layout_boxes = list(list(box_id = paste0(grob_panel_id, "_title"), box_type = "title", x0 = 0.04, y0 = 0.91, x1 = 0.96, y1 = 0.98)),
      panel_boxes = list(panel_box),
      guide_boxes = guide_boxes,
      metrics = metrics,
      render_context = render_context_sidecar(display_payload),
      style_profile = style_profile_sidecar(display_payload)
    ))
  }
  tmp_pdf <- tempfile(fileext = ".pdf")
  output_width <- render_device_dimension(display_payload, "output_width_in", "MAS_DISPLAY_OUTPUT_WIDTH_IN", 7.2)
  output_height <- render_device_dimension(display_payload, "output_height_in", "MAS_DISPLAY_OUTPUT_HEIGHT_IN", 5.0)
  grDevices::pdf(tmp_pdf, width = output_width, height = output_height)
  on.exit({
    grDevices::dev.off()
    unlink(tmp_pdf)
  }, add = TRUE)
  gt <- ggplotGrob(plot)
  grid::grid.newpage()
  grid::grid.draw(gt)
  grid::grid.force()
  widths <- resolved_layout_unit_sizes(gt$widths, output_width, "width")
  heights <- resolved_layout_unit_sizes(gt$heights, output_height, "height")
  title_box <- find_layout_box(gt, widths, heights, c("title"), "title", "title")
  x_axis_title_box <- find_layout_box(gt, widths, heights, c("xlab-b"), "x_axis_title", "x_axis_title")
  y_axis_title_box <- find_layout_box(gt, widths, heights, c("ylab-l"), "y_axis_title", "y_axis_title")
  panel_box <- find_layout_box(
    gt,
    widths,
    heights,
    c("panel"),
    "panel",
    if (template_id %in% c("heatmap_group_comparison", "performance_heatmap", "confusion_matrix_heatmap_binary", "correlation_heatmap", "clustered_heatmap", "gsva_ssgsea_heatmap")) "heatmap_tile_region" else "panel"
  )
  if (length(declared_panel_ids) == 1 && !is.null(panel_box)) {
    panel_box$panel_id <- declared_panel_ids[[1]]
  }
  guide_box <- find_layout_box(
    gt,
    widths,
    heights,
    c("guide-box"),
    if (template_id %in% c("heatmap_group_comparison", "performance_heatmap", "confusion_matrix_heatmap_binary", "correlation_heatmap", "clustered_heatmap", "gsva_ssgsea_heatmap")) "colorbar" else "legend",
    if (template_id %in% c("heatmap_group_comparison", "performance_heatmap", "confusion_matrix_heatmap_binary", "correlation_heatmap", "clustered_heatmap", "gsva_ssgsea_heatmap")) "colorbar" else "legend"
  )
  axis_left_box <- find_layout_box(gt, widths, heights, c("axis-l"), "axis_left", "axis_left")
  layout_boxes <- Filter(Negate(is.null), list(title_box, x_axis_title_box, y_axis_title_box))
  guide_boxes <- Filter(Negate(is.null), list(guide_box))
  metrics <- build_metrics(template_id, display_payload, panel_box)
  if (template_id %in% c("forest_effect_main", "subgroup_forest", "multivariable_forest") && !is.null(panel_box)) {
    forest_layout <- build_forest_layout(display_payload, panel_box, axis_left_box)
    layout_boxes <- c(layout_boxes, forest_layout$layout_boxes)
    guide_boxes <- c(guide_boxes, forest_layout$guide_boxes)
    metrics <- c(metrics[setdiff(names(metrics), names(forest_layout$metrics))], forest_layout$metrics)
  }
  if (exists("build_candidate_layout_override", mode = "function")) {
    candidate_override <- build_candidate_layout_override(template_id, display_payload, panel_box, guide_box)
    if (!is.null(candidate_override)) {
      layout_boxes <- candidate_override$layout_boxes %||% layout_boxes
      panel_boxes <- candidate_override$panel_boxes %||% Filter(Negate(is.null), list(panel_box))
      guide_boxes <- candidate_override$guide_boxes %||% guide_boxes
      candidate_only <- identical(Sys.getenv("MAS_DISPLAY_RENDERER_CANDIDATE_ONLY", unset = ""), "1")
      metrics <- if (!candidate_only && !is.null(metrics$source_renderer)) metrics else candidate_override$metrics %||% metrics
      metrics <- ensure_renderer_metrics(template_id, display_payload, panel_box, metrics)
      return(list(
        template_id = template_id,
        device = list(x0 = 0.0, y0 = 0.0, x1 = 1.0, y1 = 1.0),
        layout_boxes = layout_boxes,
        panel_boxes = panel_boxes,
        guide_boxes = guide_boxes,
        metrics = metrics,
        render_context = render_context_sidecar(display_payload),
        style_profile = style_profile_sidecar(display_payload)
      ))
    }
  }
  metrics <- ensure_renderer_metrics(template_id, display_payload, panel_box, metrics)
  list(
    template_id = template_id,
    device = list(x0 = 0.0, y0 = 0.0, x1 = 1.0, y1 = 1.0),
    layout_boxes = layout_boxes,
    panel_boxes = Filter(Negate(is.null), list(panel_box)),
    guide_boxes = guide_boxes,
    metrics = metrics,
    render_context = render_context_sidecar(display_payload),
    style_profile = style_profile_sidecar(display_payload)
  )
}

