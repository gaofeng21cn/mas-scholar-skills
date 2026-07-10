# Registry Gallery renderers. Sourced by candidate_renderer.R after shared helpers.

registry_gallery_template_ids <- c(
  "dot_range_summary_panel",
  "availability_bar_panel",
  "adult_multidimensional_phenotype_heatmap",
  "xiangya_psychobehavioral_overlap_heatmap",
  "adult_bmi_waist_central_adiposity_bar"
)

registry_required_collection <- function(payload, field_name, template_id) {
  values <- payload[[field_name]]
  if (!is.list(values) || length(values) < 1) {
    stop(sprintf("%s requires non-empty %s", template_id, field_name))
  }
  values
}

registry_required_text <- function(item, field_name, context) {
  value <- item[[field_name]]
  text <- if (is.null(value) || length(value) < 1) "" else trimws(as.character(value[[1]]))
  if (!nzchar(text)) {
    stop(sprintf("%s.%s must be non-empty", context, field_name))
  }
  text
}

registry_required_number <- function(item, field_name, context) {
  value <- item[[field_name]]
  if (is.list(value)) {
    value <- unlist(value, recursive = TRUE, use.names = FALSE)
  }
  numeric_value <- suppressWarnings(as.numeric(value))
  if (length(numeric_value) != 1 || !is.finite(numeric_value)) {
    stop(sprintf("%s.%s must be one finite number", context, field_name))
  }
  numeric_value
}

registry_required_count <- function(item, field_name, context) {
  value <- registry_required_number(item, field_name, context)
  if (value < 0 || abs(value - round(value)) > 1e-6) {
    stop(sprintf("%s.%s must be a non-negative integer", context, field_name))
  }
  as.integer(round(value))
}

registry_required_percent <- function(item, field_name, context) {
  value <- registry_required_number(item, field_name, context)
  if (value < 0 || value > 100) {
    stop(sprintf("%s.%s must be between 0 and 100", context, field_name))
  }
  value
}

registry_count_pair <- function(item, numerator_field, denominator_field, context) {
  numerator <- registry_required_count(item, numerator_field, context)
  denominator <- registry_required_count(item, denominator_field, context)
  if (denominator < 1) {
    stop(sprintf("%s.%s must be positive", context, denominator_field))
  }
  if (numerator > denominator) {
    stop(sprintf("%s.%s cannot exceed %s", context, numerator_field, denominator_field))
  }
  c(numerator = numerator, denominator = denominator)
}

registry_count_percent <- function(
  item,
  numerator_field,
  denominator_field,
  percent_field,
  context
) {
  counts <- registry_count_pair(item, numerator_field, denominator_field, context)
  percent <- registry_required_percent(item, percent_field, context)
  derived_percent <- counts[["numerator"]] / counts[["denominator"]] * 100
  if (abs(percent - derived_percent) > 0.051) {
    stop(sprintf(
      "%s.%s must match %s/%s within one-decimal rounding tolerance",
      context,
      percent_field,
      numerator_field,
      denominator_field
    ))
  }
  c(counts, percent = percent)
}

registry_compact_number <- function(value) {
  if (abs(value - round(value)) < 1e-8) {
    return(sprintf("%.0f", value))
  }
  digits <- if (abs(value) >= 10) 1 else 2
  sub("\\.?0+$", "", sprintf(paste0("%.", digits, "f"), value))
}

candidate_plot_dot_range_summary <- function(payload) {
  template_id <- "dot_range_summary_panel"
  rows <- registry_required_collection(payload, "rows", template_id)
  dot_df <- do.call(rbind, lapply(seq_along(rows), function(index) {
    item <- rows[[index]]
    context <- sprintf("%s.rows[%d]", template_id, index)
    values <- registry_count_percent(
      item,
      "positive_n",
      "available_n",
      "percent",
      context
    )
    data.frame(
      bmi_category = registry_required_text(item, "bmi_category", context),
      measure = registry_required_text(item, "measure", context),
      positive_n = values[["numerator"]],
      available_n = values[["denominator"]],
      percent = values[["percent"]],
      stringsAsFactors = FALSE
    )
  }))
  dot_df$bmi_category <- factor(dot_df$bmi_category, levels = rev(unique(dot_df$bmi_category)))
  dot_df$measure <- factor(dot_df$measure, levels = unique(dot_df$measure))
  dot_df$count_label <- sprintf("%d/%d", dot_df$positive_n, dot_df$available_n)
  dot_df$label_x <- ifelse(dot_df$percent >= 90, dot_df$percent - 4.5, dot_df$percent + 4.5)
  dot_df$label_hjust <- ifelse(dot_df$percent >= 90, 1, 0)
  palette <- candidate_palette(payload)
  ggplot(dot_df, aes(y = bmi_category)) +
    geom_segment(
      aes(x = 0, xend = percent, yend = bmi_category),
      colour = palette$light,
      linewidth = style_numeric(style_stroke(payload), "primary_linewidth", 2.2) * 0.72,
      lineend = "round"
    ) +
    geom_point(
      aes(x = percent, size = available_n),
      colour = palette$primary,
      alpha = 0.94
    ) +
    geom_text(
      aes(x = label_x, label = count_label, hjust = label_hjust),
      size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.27,
      colour = palette$text,
      show.legend = FALSE
    ) +
    facet_wrap(~measure, nrow = 1) +
    scale_x_continuous(
      limits = c(0, 100),
      breaks = c(0, 25, 50, 75, 100),
      labels = function(value) sprintf("%d%%", value),
      expand = expansion(mult = c(0, 0.13))
    ) +
    scale_size_continuous(
      range = c(2.6, 6.2),
      breaks = continuous_scale_breaks(dot_df$available_n, max_breaks = 3),
      name = candidate_non_empty(payload$size_scale_label, "Available n")
    ) +
    coord_cartesian(clip = "off") +
    labs(
      title = candidate_non_empty(payload$title, "BMI-stratified phenotype prevalence"),
      x = candidate_non_empty(payload$x_label, "Participants with measure-defined phenotype (%)"),
      y = candidate_non_empty(payload$y_label, "BMI category")
    ) +
    candidate_theme(payload) +
    guides(size = guide_legend(nrow = 1, byrow = TRUE)) +
    theme(
      panel.grid.major.y = element_blank(),
      legend.position = "bottom",
      legend.title = element_text(
        size = style_numeric(style_typography(payload), "legend_size", 10.0),
        colour = palette$text,
        margin = margin(r = 8, unit = "pt")
      ),
      plot.margin = margin(9, 28, 9, 12)
    )
}

candidate_plot_availability_bar <- function(payload) {
  template_id <- "availability_bar_panel"
  rows <- registry_required_collection(payload, "rows", template_id)
  availability_df <- do.call(rbind, lapply(seq_along(rows), function(index) {
    item <- rows[[index]]
    context <- sprintf("%s.rows[%d]", template_id, index)
    values <- registry_count_percent(
      item,
      "available_n",
      "denominator_n",
      "percent",
      context
    )
    data.frame(
      measure = registry_required_text(item, "measure", context),
      available_n = values[["numerator"]],
      denominator_n = values[["denominator"]],
      percent = values[["percent"]],
      stringsAsFactors = FALSE
    )
  }))
  availability_df$measure <- factor(availability_df$measure, levels = rev(availability_df$measure))
  availability_df$count_label <- sprintf(
    "%d/%d (%.1f%%)",
    availability_df$available_n,
    availability_df$denominator_n,
    availability_df$percent
  )
  palette <- candidate_palette(payload)
  availability_df$label_x <- ifelse(availability_df$percent >= 35, availability_df$percent - 1.2, availability_df$percent + 1.2)
  availability_df$label_hjust <- ifelse(availability_df$percent >= 35, 1, 0)
  availability_df$text_colour <- ifelse(availability_df$percent >= 35, "#FFFFFF", palette$text)
  ggplot(availability_df, aes(x = percent, y = measure)) +
    geom_vline(
      xintercept = 100,
      colour = palette$reference,
      linewidth = style_numeric(style_stroke(payload), "reference_linewidth", 1.0) * 0.55,
      linetype = "dashed"
    ) +
    geom_col(fill = palette$primary, width = 0.62) +
    geom_text(
      aes(x = label_x, label = count_label, hjust = label_hjust, colour = text_colour),
      size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.29,
      show.legend = FALSE
    ) +
    scale_colour_identity() +
    scale_x_continuous(
      limits = c(0, 105),
      breaks = c(0, 25, 50, 75, 100),
      labels = function(value) sprintf("%d%%", value),
      expand = expansion(mult = c(0, 0))
    ) +
    labs(
      title = candidate_non_empty(payload$title, "Availability of registry phenotype measures"),
      x = candidate_non_empty(payload$x_label, "Available participants (%)"),
      y = candidate_non_empty(payload$y_label, "Registry measure")
    ) +
    candidate_theme(payload) +
    theme(
      panel.grid.major.y = element_blank(),
      legend.position = "none"
    )
}

candidate_plot_adult_multidimensional_phenotype_heatmap <- function(payload) {
  template_id <- "adult_multidimensional_phenotype_heatmap"
  cells <- registry_required_collection(payload, "cells", template_id)
  heat_df <- do.call(rbind, lapply(seq_along(cells), function(index) {
    item <- cells[[index]]
    context <- sprintf("%s.cells[%d]", template_id, index)
    data.frame(
      bmi_category = registry_required_text(item, "bmi_category", context),
      feature = registry_required_text(item, "feature", context),
      unit = registry_required_text(item, "unit", context),
      median = registry_required_number(item, "median", context),
      available_n = registry_required_count(item, "available_n", context),
      stringsAsFactors = FALSE
    )
  }))
  feature_unit_counts <- tapply(heat_df$unit, heat_df$feature, function(values) length(unique(values)))
  if (any(feature_unit_counts != 1)) {
    stop(sprintf("%s must use exactly one unit per feature", template_id))
  }
  heat_df$scaled_value <- ave(heat_df$median, heat_df$feature, FUN = function(values) {
    value_range <- range(values, na.rm = TRUE)
    if (identical(value_range[[1]], value_range[[2]])) {
      return(rep(0.5, length(values)))
    }
    (values - value_range[[1]]) / (value_range[[2]] - value_range[[1]])
  })
  feature_units <- stats::setNames(heat_df$unit[!duplicated(heat_df$feature)], heat_df$feature[!duplicated(heat_df$feature)])
  heat_df$feature_label <- sprintf("%s (%s)", heat_df$feature, feature_units[heat_df$feature])
  heat_df$cell_label <- sprintf(
    "%s\nn=%d",
    vapply(heat_df$median, registry_compact_number, character(1)),
    heat_df$available_n
  )
  heat_df$text_colour <- heatmap_text_colours(payload, heat_df$scaled_value)
  heat_df$bmi_category <- factor(heat_df$bmi_category, levels = unique(heat_df$bmi_category))
  heat_df$feature_label <- factor(heat_df$feature_label, levels = rev(unique(heat_df$feature_label)))
  ggplot(heat_df, aes(x = bmi_category, y = feature_label, fill = scaled_value)) +
    geom_tile(colour = "white", linewidth = 0.55) +
    geom_text(
      aes(label = cell_label, colour = text_colour),
      size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.26,
      lineheight = 0.92,
      show.legend = FALSE
    ) +
    scale_colour_identity() +
    heatmap_fill_scale(
      payload,
      heat_df$scaled_value,
      name = candidate_non_empty(payload$heatmap_scale_label, "Within-feature relative level"),
      limits = c(0, 1)
    ) +
    labs(
      title = candidate_non_empty(payload$title, "Adult multidimensional phenotype profile"),
      x = candidate_non_empty(payload$x_label, "BMI category"),
      y = candidate_non_empty(payload$y_label, "Phenotype feature")
    ) +
    candidate_theme(payload) +
    theme_publication_colorbar(payload) +
    theme(
      axis.text.x = element_text(angle = 20, hjust = 1),
      panel.grid = element_blank()
    )
}

candidate_plot_xiangya_psychobehavioral_overlap_heatmap <- function(payload) {
  template_id <- "xiangya_psychobehavioral_overlap_heatmap"
  cells <- registry_required_collection(payload, "cells", template_id)
  heat_df <- do.call(rbind, lapply(seq_along(cells), function(index) {
    item <- cells[[index]]
    context <- sprintf("%s.cells[%d]", template_id, index)
    data.frame(
      phq9_status = registry_required_text(item, "phq9_status", context),
      gad7_status = registry_required_text(item, "gad7_status", context),
      count = registry_required_count(item, "count", context),
      declared_row_percent = registry_required_percent(item, "row_percent", context),
      stringsAsFactors = FALSE
    )
  }))
  row_total <- ave(heat_df$count, heat_df$phq9_status, FUN = sum)
  if (any(row_total < 1)) {
    stop(sprintf("%s each PHQ-9 row must contain a positive total count", template_id))
  }
  heat_df$row_percent <- heat_df$count / row_total * 100
  if (any(abs(heat_df$declared_row_percent - heat_df$row_percent) > 0.051)) {
    stop(sprintf(
      "%s row_percent must match the percentage derived from same-row counts within one-decimal rounding tolerance",
      template_id
    ))
  }
  heat_df$cell_label <- sprintf("%d\n%.1f%%", heat_df$count, heat_df$row_percent)
  heat_df$text_colour <- heatmap_text_colours(payload, heat_df$row_percent)
  heat_df$gad7_status <- factor(heat_df$gad7_status, levels = unique(heat_df$gad7_status))
  heat_df$phq9_status <- factor(heat_df$phq9_status, levels = rev(unique(heat_df$phq9_status)))
  ggplot(heat_df, aes(x = gad7_status, y = phq9_status, fill = row_percent)) +
    geom_tile(colour = "white", linewidth = 0.8) +
    geom_text(
      aes(label = cell_label, colour = text_colour),
      size = style_numeric(style_typography(payload), "axis_title_size", 11.0) * 0.31,
      fontface = "bold",
      lineheight = 0.92,
      show.legend = FALSE
    ) +
    scale_colour_identity() +
    heatmap_fill_scale(
      payload,
      heat_df$row_percent,
      name = candidate_non_empty(payload$heatmap_scale_label, "Row percentage (%)"),
      limits = c(0, 100)
    ) +
    labs(
      title = candidate_non_empty(payload$title, "Psychobehavioral symptom overlap"),
      x = candidate_non_empty(payload$x_label, "GAD-7 status"),
      y = candidate_non_empty(payload$y_label, "PHQ-9 status")
    ) +
    candidate_theme(payload) +
    theme_publication_colorbar(payload) +
    theme(
      axis.text.x = element_text(angle = 0, hjust = 0.5),
      panel.grid = element_blank()
    )
}

candidate_plot_adult_bmi_waist_central_adiposity_bar <- function(payload) {
  template_id <- "adult_bmi_waist_central_adiposity_bar"
  rows <- registry_required_collection(payload, "rows", template_id)
  bar_df <- do.call(rbind, lapply(seq_along(rows), function(index) {
    item <- rows[[index]]
    context <- sprintf("%s.rows[%d]", template_id, index)
    values <- registry_count_percent(
      item,
      "central_obesity_n",
      "available_n",
      "central_obesity_percent",
      context
    )
    data.frame(
      bmi_category = registry_required_text(item, "bmi_category", context),
      percent = values[["percent"]],
      available_n = values[["denominator"]],
      central_obesity_n = values[["numerator"]],
      stringsAsFactors = FALSE
    )
  }))
  bar_df$bmi_category <- factor(bar_df$bmi_category, levels = unique(bar_df$bmi_category))
  bar_df$count_label <- sprintf("%.1f%%\nn=%d", bar_df$percent, bar_df$available_n)
  palette <- candidate_palette(payload)
  ggplot(bar_df, aes(x = bmi_category, y = percent)) +
    geom_col(fill = palette$primary, width = 0.62) +
    geom_text(
      aes(label = count_label),
      vjust = -0.28,
      lineheight = 0.90,
      size = style_numeric(style_typography(payload), "tick_size", 10.0) * 0.28,
      colour = palette$text
    ) +
    scale_y_continuous(
      limits = c(0, 108),
      breaks = c(0, 25, 50, 75, 100),
      labels = function(value) sprintf("%d%%", value),
      expand = expansion(mult = c(0, 0))
    ) +
    labs(
      title = candidate_non_empty(payload$title, "Central adiposity across adult BMI categories"),
      x = candidate_non_empty(payload$x_label, "BMI category"),
      y = candidate_non_empty(payload$y_label, "Central adiposity prevalence (%)")
    ) +
    candidate_theme(payload) +
    theme(
      axis.text.x = element_text(angle = 20, hjust = 1),
      panel.grid.major.x = element_blank(),
      legend.position = "none"
    )
}
