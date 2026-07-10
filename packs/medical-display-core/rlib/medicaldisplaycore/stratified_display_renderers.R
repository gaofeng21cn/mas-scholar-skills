# Purpose-first renderers for reusable stratified mismatch and support displays.

stratified_metric_definitions_df <- function(metric_definitions) {
  if (!is.list(metric_definitions) || length(metric_definitions) < 1) {
    stop("stratified display payload requires non-empty metric_definitions")
  }
  do.call(rbind, lapply(seq_along(metric_definitions), function(index) {
    item <- metric_definitions[[index]]
    data.frame(
      metric_index = index,
      metric_id = candidate_non_empty(item$metric_id, sprintf("metric_%d", index)),
      metric_label = candidate_non_empty(item$metric_label, sprintf("Metric %d", index)),
      stringsAsFactors = FALSE
    )
  }))
}

stratified_group_rows_df <- function(rows) {
  if (!is.list(rows) || length(rows) < 1) {
    stop("stratified display payload requires non-empty rows")
  }
  do.call(rbind, lapply(seq_along(rows), function(index) {
    item <- rows[[index]]
    data.frame(
      row_index = index,
      group_label = candidate_non_empty(item$group_label, sprintf("Group %d", index)),
      group_share = candidate_numeric(item$group_share, 0),
      stringsAsFactors = FALSE
    )
  }))
}

stratified_metric_value <- function(metrics, metric_id, field, default = NA_real_) {
  if (!is.list(metrics)) {
    return(default)
  }
  for (item in metrics) {
    if (identical(candidate_non_empty(item$metric_id, ""), metric_id)) {
      value <- item[[field]]
      if (is.null(value)) {
        return(default)
      }
      return(candidate_numeric(value, default))
    }
  }
  default
}

stratified_mismatch_rates_long_df <- function(rows, metric_definitions) {
  definitions_df <- stratified_metric_definitions_df(metric_definitions)
  do.call(rbind, lapply(seq_along(rows), function(row_index) {
    row <- rows[[row_index]]
    do.call(rbind, lapply(seq_len(nrow(definitions_df)), function(metric_index) {
      definition <- definitions_df[metric_index, ]
      data.frame(
        group_label = candidate_non_empty(row$group_label, sprintf("Group %d", row_index)),
        metric_id = definition$metric_id,
        metric_label = definition$metric_label,
        metric_index = definition$metric_index,
        value = stratified_metric_value(row$metrics, definition$metric_id, "value"),
        stringsAsFactors = FALSE
      )
    }))
  }))
}

stratified_burden_long_df <- function(rows, metric_definitions) {
  definitions_df <- stratified_metric_definitions_df(metric_definitions)
  do.call(rbind, lapply(seq_along(rows), function(row_index) {
    row <- rows[[row_index]]
    group_size <- candidate_numeric(row$group_size, 0)
    do.call(rbind, lapply(seq_len(nrow(definitions_df)), function(metric_index) {
      definition <- definitions_df[metric_index, ]
      event_count <- stratified_metric_value(row$metrics, definition$metric_id, "event_count", 0)
      denominator <- stratified_metric_value(row$metrics, definition$metric_id, "denominator", group_size)
      explicit_rate <- stratified_metric_value(row$metrics, definition$metric_id, "rate")
      rate <- if (!is.na(explicit_rate)) explicit_rate else if (denominator > 0) event_count / denominator else 0
      data.frame(
        group_label = candidate_non_empty(row$group_label, sprintf("Group %d", row_index)),
        metric_id = definition$metric_id,
        metric_label = definition$metric_label,
        metric_index = definition$metric_index,
        event_count = event_count,
        denominator = denominator,
        rate_percent = rate * 100,
        stringsAsFactors = FALSE
      )
    }))
  }))
}

transition_support_rows_df <- function(rows) {
  if (!is.list(rows) || length(rows) < 1) {
    stop("transition support payload requires non-empty transition_rows")
  }
  do.call(rbind, lapply(seq_along(rows), function(index) {
    item <- rows[[index]]
    data.frame(
      source_group_label = candidate_non_empty(item$source_group_label, sprintf("Source %d", index)),
      target_group_label = candidate_non_empty(item$target_group_label, sprintf("Target %d", index)),
      unit_count = candidate_numeric(item$unit_count, 0),
      transition_share = candidate_numeric(item$transition_share, 0),
      stringsAsFactors = FALSE
    )
  }))
}

support_distribution_rows_df <- function(rows) {
  if (!is.list(rows) || length(rows) < 1) {
    stop("transition support payload requires non-empty support_rows")
  }
  do.call(rbind, lapply(seq_along(rows), function(index) {
    item <- rows[[index]]
    data.frame(
      support_label = candidate_non_empty(item$support_label, sprintf("Support group %d", index)),
      unit_count = candidate_numeric(item$unit_count, 0),
      support_share = candidate_numeric(item$support_share, 0),
      stringsAsFactors = FALSE
    )
  }))
}

stratified_source_renderer <- function(template_id) {
  sprintf("fenggaolab.org.medical-display-core::%s", template_id)
}

stratified_label_wrap <- function(values, width = 22) {
  vapply(values, function(value) paste(strwrap(as.character(value), width = width), collapse = "\n"), character(1))
}

plot_stratified_mismatch_matrix <- function(payload) {
  rows_df <- stratified_group_rows_df(payload$rows)
  rows_df$group_label <- factor(rows_df$group_label, levels = rev(rows_df$group_label))
  definitions_df <- stratified_metric_definitions_df(payload$metric_definitions)
  heat_df <- stratified_mismatch_rates_long_df(payload$rows, payload$metric_definitions)
  heat_df$group_label <- factor(heat_df$group_label, levels = levels(rows_df$group_label))
  heat_df$metric_label <- factor(heat_df$metric_label, levels = definitions_df$metric_label)
  heat_df$label <- ifelse(is.na(heat_df$value), "N/A", sprintf("%.0f%%", heat_df$value * 100))
  palette <- candidate_palette(payload)
  composition_plot <- ggplot(rows_df, aes(x = group_share * 100, y = group_label)) +
    geom_col(fill = palette$primary, width = 0.62) +
    geom_text(
      aes(label = sprintf("%.1f%%", group_share * 100)),
      hjust = -0.12,
      size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.26,
      colour = palette$text
    ) +
    coord_cartesian(xlim = c(0, max(rows_df$group_share * 100, na.rm = TRUE) * 1.20), clip = "off") +
    labs(
      title = candidate_non_empty(payload$composition_panel_title, "Group share"),
      x = candidate_non_empty(payload$composition_axis_label, "Share of cohort (%)"),
      y = ""
    ) +
    candidate_theme(payload) +
    theme(axis.text.y = element_text(size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.82))
  heat_plot <- ggplot(heat_df, aes(x = metric_label, y = group_label, fill = value)) +
    geom_tile(colour = "white", linewidth = 0.45) +
    geom_text(aes(label = label), size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.24, colour = palette$text) +
    scale_fill_gradient(
      low = style_color(payload, "heatmap_seq_low", "heatmap_seq_low", "#F4F8FA"),
      high = style_color(payload, "heatmap_seq_high", "heatmap_seq_high", "#0B4F6C"),
      limits = c(0, 1),
      na.value = "#ECEFF3",
      labels = function(x) sprintf("%.0f%%", x * 100),
      name = candidate_non_empty(payload$heatmap_scale_label, "Mismatch rate")
    ) +
    labs(
      title = candidate_non_empty(payload$heatmap_panel_title, "Mismatch pattern"),
      x = "",
      y = ""
    ) +
    candidate_theme(payload) +
    theme_publication_colorbar(payload) +
    theme(
      axis.text.x = element_text(
        angle = 0,
        hjust = 0.5,
        vjust = 1,
        lineheight = 0.86,
        size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.50
      ),
      axis.text.y = element_blank(),
      axis.ticks.y = element_blank(),
      legend.position = "right"
    )
  patchwork::wrap_plots(list(composition_plot, heat_plot), ncol = 2, widths = c(0.95, 1.25))
}

plot_transition_support_matrix <- function(payload) {
  transition_df <- transition_support_rows_df(payload$transition_rows)
  source_levels <- unique(transition_df$source_group_label)
  target_levels <- unique(transition_df$target_group_label)
  transition_df$source_group_label <- factor(transition_df$source_group_label, levels = rev(source_levels))
  transition_df$target_group_label <- factor(transition_df$target_group_label, levels = target_levels)
  transition_df$label <- ifelse(
    transition_df$transition_share >= 0.04,
    sprintf("%.1f%%", transition_df$transition_share * 100),
    ""
  )
  support_df <- support_distribution_rows_df(payload$support_rows)
  support_df$support_label <- factor(support_df$support_label, levels = support_df$support_label)
  palette <- candidate_palette(payload)
  transition_plot <- ggplot(transition_df, aes(x = target_group_label, y = source_group_label, fill = transition_share)) +
    geom_tile(colour = "white", linewidth = 0.45) +
    geom_text(aes(label = label), size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.24, colour = palette$text) +
    scale_fill_gradient(
      low = style_color(payload, "heatmap_seq_low", "heatmap_seq_low", "#F4F8FA"),
      high = style_color(payload, "heatmap_seq_high", "heatmap_seq_high", "#0B4F6C"),
      labels = function(x) sprintf("%.0f%%", x * 100),
      name = candidate_non_empty(payload$heatmap_scale_label, "Transition share")
    ) +
    labs(
      title = candidate_non_empty(payload$transition_panel_title, "State transition support"),
      x = candidate_non_empty(payload$target_axis_label, "Follow-up group"),
      y = candidate_non_empty(payload$source_axis_label, "Index group")
    ) +
    candidate_theme(payload) +
    theme_publication_colorbar(payload) +
    theme(
      axis.text.x = element_text(angle = 35, hjust = 1, vjust = 1, size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.70),
      axis.text.y = element_text(size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.70),
      legend.position = "right"
    )
  support_plot <- ggplot(support_df, aes(x = support_share * 100, y = support_label)) +
    geom_col(fill = palette$secondary, width = 0.58) +
    geom_text(
      aes(label = sprintf("%.1f%%", support_share * 100)),
      hjust = -0.12,
      size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.27,
      colour = palette$text
    ) +
    coord_cartesian(xlim = c(0, max(support_df$support_share * 100, na.rm = TRUE) * 1.18), clip = "off") +
    labs(
      title = candidate_non_empty(payload$support_panel_title, "Held-out support"),
      x = candidate_non_empty(payload$support_axis_label, "Share of units (%)"),
      y = ""
    ) +
    candidate_theme(payload) +
    theme(panel.grid.major.y = element_blank())
  patchwork::wrap_plots(list(transition_plot, support_plot), ncol = 2, widths = c(1.50, 0.82))
}

plot_stratified_mismatch_burden <- function(payload) {
  long_df <- stratified_burden_long_df(payload$rows, payload$metric_definitions)
  definitions_df <- stratified_metric_definitions_df(payload$metric_definitions)
  long_df$group_label_wrapped <- stratified_label_wrap(long_df$group_label, width = 22)
  long_df$group_label_wrapped <- factor(long_df$group_label_wrapped, levels = rev(unique(long_df$group_label_wrapped)))
  long_df$metric_label <- factor(long_df$metric_label, levels = definitions_df$metric_label)
  palette <- candidate_palette(payload)
  ggplot(long_df, aes(x = rate_percent, y = group_label_wrapped)) +
    geom_col(fill = palette$primary, width = 0.62) +
    geom_text(
      aes(label = ifelse(
        event_count > 0,
        sprintf(
          "%.1f%% (%s/%s)",
          rate_percent,
          format(round(event_count), big.mark = ",", scientific = FALSE),
          format(round(denominator), big.mark = ",", scientific = FALSE)
        ),
        "0"
      )),
      hjust = -0.08,
      size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.20,
      colour = palette$text
    ) +
    facet_wrap(~metric_label, ncol = 2, scales = "fixed") +
    coord_cartesian(xlim = c(0, max(1, max(long_df$rate_percent, na.rm = TRUE) * 1.55)), clip = "off") +
    labs(
      title = NULL,
      x = candidate_non_empty(payload$x_label, "Mismatch rate (% of eligible denominator)"),
      y = candidate_non_empty(payload$y_label, "Clinical group")
    ) +
    candidate_theme(payload) +
    theme(
      axis.text.y = element_text(size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.76),
      strip.text = element_text(size = style_numeric(style_typography(payload), "panel_label_size", 11.0) * 0.82, face = "bold"),
      panel.grid.major.y = element_blank()
    )
}

stratified_metric_rows <- function(rows) {
  lapply(rows %|||% list(), function(item) as.list(item))
}

stratified_small_multiple_layout <- function(panel_count) {
  panel_count <- max(1, min(4, as.integer(panel_count)))
  layout_boxes <- list(candidate_box("shared_y_axis_title", "y_axis_title", 0.02, 0.34, 0.06, 0.64))
  panel_boxes <- list()
  for (index in seq_len(panel_count)) {
    row_index <- floor((index - 1) / 2)
    column_index <- (index - 1) %% 2
    letter <- LETTERS[[index]]
    x_min <- if (column_index == 0) 0.10 else 0.56
    x_max <- if (column_index == 0) 0.44 else 0.90
    title_x_min <- if (column_index == 0) 0.14 else 0.58
    title_x_max <- if (column_index == 0) 0.38 else 0.84
    title_y_min <- if (row_index == 0) 0.10 else 0.50
    title_y_max <- if (row_index == 0) 0.14 else 0.54
    panel_y_min <- if (row_index == 0) 0.16 else 0.58
    panel_y_max <- if (row_index == 0) 0.42 else 0.84
    layout_boxes[[length(layout_boxes) + 1]] <- candidate_box(
      sprintf("panel_label_%s", letter), "panel_label", x_min - 0.03, title_y_min, x_min, title_y_max
    )
    layout_boxes[[length(layout_boxes) + 1]] <- candidate_box(
      sprintf("metric_title_%s", letter), "subplot_title", title_x_min, title_y_min, title_x_max, title_y_max
    )
    panel_boxes[[length(panel_boxes) + 1]] <- candidate_box(
      sprintf("mismatch_burden_panel_%s", letter), "mismatch_burden_panel", x_min, panel_y_min, x_max, panel_y_max
    )
  }
  list(layout_boxes = layout_boxes, panel_boxes = panel_boxes)
}

stratified_display_layout_override <- function(template_id, display_payload) {
  if (identical(template_id, "phenotype_gap_structure_figure")) {
    definitions_df <- stratified_metric_definitions_df(display_payload$metric_definitions)
    return(list(
      layout_boxes = list(
        candidate_box("panel_label_A", "panel_label", 0.07, 0.10, 0.10, 0.14),
        candidate_box("panel_label_B", "panel_label", 0.53, 0.10, 0.56, 0.14),
        candidate_box("composition_title", "subplot_title", 0.14, 0.10, 0.38, 0.14),
        candidate_box("mismatch_title", "subplot_title", 0.60, 0.10, 0.82, 0.14),
        candidate_box("composition_x_axis_title", "x_axis_title", 0.18, 0.90, 0.34, 0.94),
        candidate_box("mismatch_x_axis_title", "x_axis_title", 0.64, 0.90, 0.80, 0.94),
        candidate_box("colorbar_title", "colorbar_title", 0.87, 0.18, 0.95, 0.22)
      ),
      panel_boxes = list(
        candidate_box("composition_panel", "composition_panel", 0.08, 0.18, 0.43, 0.84),
        candidate_box("mismatch_heatmap_panel", "mismatch_heatmap_panel", 0.54, 0.18, 0.84, 0.84)
      ),
      guide_boxes = list(candidate_box("colorbar", "colorbar", 0.88, 0.26, 0.94, 0.80)),
      metrics = list(
        source_renderer = stratified_source_renderer(template_id),
        figure_purpose = "group_composition_plus_mismatch_rate_matrix",
        rendered_title_policy = "figure_title_metadata_only_not_drawn_inside_plot",
        rows = stratified_metric_rows(display_payload$rows),
        mismatch_labels = definitions_df$metric_label
      )
    ))
  }
  if (identical(template_id, "site_held_out_stability_figure")) {
    return(list(
      layout_boxes = list(
        candidate_box("panel_label_A", "panel_label", 0.07, 0.10, 0.10, 0.14),
        candidate_box("panel_label_B", "panel_label", 0.58, 0.10, 0.61, 0.14),
        candidate_box("transition_title", "subplot_title", 0.16, 0.10, 0.42, 0.14),
        candidate_box("support_title", "subplot_title", 0.66, 0.10, 0.90, 0.14),
        candidate_box("transition_x_axis_title", "x_axis_title", 0.20, 0.90, 0.42, 0.94),
        candidate_box("transition_y_axis_title", "y_axis_title", 0.02, 0.36, 0.06, 0.62),
        candidate_box("support_x_axis_title", "x_axis_title", 0.66, 0.90, 0.84, 0.94),
        candidate_box("support_y_axis_title", "y_axis_title", 0.50, 0.36, 0.54, 0.62),
        candidate_box("colorbar_title", "colorbar_title", 0.90, 0.18, 0.97, 0.22)
      ),
      panel_boxes = list(
        candidate_box("transition_heatmap_panel", "transition_heatmap_panel", 0.09, 0.18, 0.49, 0.84),
        candidate_box("support_distribution_panel", "support_distribution_panel", 0.60, 0.18, 0.86, 0.84)
      ),
      guide_boxes = list(candidate_box("colorbar", "colorbar", 0.91, 0.26, 0.96, 0.80)),
      metrics = list(
        source_renderer = stratified_source_renderer(template_id),
        figure_purpose = "state_transition_stability_plus_held_out_support",
        rendered_title_policy = "figure_title_metadata_only_not_drawn_inside_plot",
        transition_cell_label_policy = "major_share_percent_only_no_counts",
        support_label_policy = "percent_only_counts_remain_in_table",
        transition_rows = stratified_metric_rows(display_payload$transition_rows),
        support_rows = stratified_metric_rows(display_payload$support_rows)
      )
    ))
  }
  if (identical(template_id, "treatment_gap_alignment_figure")) {
    definitions_df <- stratified_metric_definitions_df(display_payload$metric_definitions)
    small_multiples <- stratified_small_multiple_layout(nrow(definitions_df))
    return(list(
      layout_boxes = small_multiples$layout_boxes,
      panel_boxes = small_multiples$panel_boxes,
      guide_boxes = list(),
      metrics = list(
        source_renderer = stratified_source_renderer(template_id),
        figure_purpose = "stratified_indicator_mismatch_burden_small_multiples",
        rendered_title_policy = "figure_title_metadata_only_not_drawn_inside_plot",
        rows = stratified_metric_rows(display_payload$rows),
        panels = lapply(seq_len(nrow(definitions_df)), function(index) {
          list(metric_id = definitions_df$metric_id[[index]], metric_label = definitions_df$metric_label[[index]])
        })
      )
    ))
  }
  NULL
}
