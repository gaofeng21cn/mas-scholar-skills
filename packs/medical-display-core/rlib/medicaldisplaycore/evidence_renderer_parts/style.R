render_context_from_payload <- function(display_payload) {
  display_payload$render_context %||% list()
}

render_context_sidecar <- function(display_payload) {
  render_context <- render_context_from_payload(display_payload)
  if (!is.list(render_context) || length(render_context) > 0) {
    return(render_context)
  }
  structure(list(), names = character())
}

style_palette <- function(display_payload) {
  render_context_from_payload(display_payload)$palette %||% list()
}

style_semantic_roles <- function(display_payload) {
  render_context_from_payload(display_payload)$semantic_roles %||% list()
}

style_roles <- function(display_payload) {
  render_context_from_payload(display_payload)$style_roles %||% list()
}

style_typography <- function(display_payload) {
  render_context_from_payload(display_payload)$typography %||% list()
}

style_stroke <- function(display_payload) {
  render_context_from_payload(display_payload)$stroke %||% list()
}

style_grid <- function(display_payload) {
  render_context_from_payload(display_payload)$grid %||% list()
}

style_numeric <- function(mapping, key, fallback) {
  value <- mapping[[key]]
  if (is.null(value)) {
    return(as.numeric(fallback))
  }
  numeric_value <- suppressWarnings(as.numeric(value))
  if (!is.finite(numeric_value)) as.numeric(fallback) else numeric_value
}

style_bool <- function(mapping, key, fallback) {
  value <- mapping[[key]]
  if (is.null(value)) {
    return(isTRUE(fallback))
  }
  if (is.logical(value)) {
    return(isTRUE(value))
  }
  normalized <- tolower(trimws(as.character(value)))
  if (normalized %in% c("true", "1", "yes", "on")) {
    return(TRUE)
  }
  if (normalized %in% c("false", "0", "no", "off")) {
    return(FALSE)
  }
  isTRUE(fallback)
}

style_color <- function(display_payload, role_name = NULL, palette_key = NULL, fallback = "#13293D") {
  roles <- style_roles(display_payload)
  semantic_roles <- style_semantic_roles(display_payload)
  palette <- style_palette(display_payload)
  candidates <- list()
  if (!is.null(role_name)) {
    candidates <- c(candidates, list(roles[[role_name]], semantic_roles[[role_name]]))
  }
  if (!is.null(palette_key)) {
    candidates <- c(candidates, list(palette_key))
  }
  for (candidate in candidates) {
    value <- trimws(as.character(candidate %||% ""))
    if (!nzchar(value)) {
      next
    }
    if (startsWith(value, "#")) {
      return(value)
    }
    palette_value <- trimws(as.character(palette[[value]] %||% ""))
    if (nzchar(palette_value)) {
      return(palette_value)
    }
  }
  fallback
}

style_text_color <- function(display_payload) {
  style_color(display_payload, role_name = "text", palette_key = "text", fallback = "#13293D")
}

style_grid_color <- function(display_payload) {
  grid_spec <- style_grid(display_payload)
  palette_key <- grid_spec$color %||% "grid"
  style_color(display_payload, role_name = "grid_line", palette_key = palette_key, fallback = "#E6EDF2")
}

publication_legend_guides <- function(display_payload, labels = NULL) {
  label_count <- length(unique(as.character(labels %||% character())))
  row_count <- if (label_count > 6) 3 else if (label_count > 3) 2 else 1
  guide_legend(
    nrow = row_count,
    byrow = TRUE,
    override.aes = list(linewidth = style_numeric(style_stroke(display_payload), "primary_linewidth", 2.0) * 0.42),
    label.position = "right",
    label.hjust = 0,
    keywidth = unit(13, "pt"),
    keyheight = unit(6, "pt")
  )
}

publication_colorbar_guide <- function(display_payload, title = NULL, bar_orientation = "vertical") {
  typography <- style_typography(display_payload)
  horizontal <- identical(bar_orientation, "horizontal")
  default_barwidth <- if (horizontal) 112.0 else 5.0
  default_barheight <- if (horizontal) 6.0 else 42.0
  label_size <- style_numeric(typography, "colorbar_label_size", 5.6)
  title_size <- style_numeric(typography, "colorbar_title_size", 6.0)
  guide_colourbar(
    title = title,
    title.position = "top",
    title.hjust = 0.5,
    label.position = if (horizontal) "bottom" else "right",
    label.hjust = if (horizontal) 0.5 else 0,
    label.theme = element_text(
      size = label_size,
      margin = if (horizontal) margin(t = 4, unit = "pt") else margin(l = 2, unit = "pt")
    ),
    title.theme = element_text(
      size = title_size,
      margin = if (horizontal) margin(b = 3.5, unit = "pt") else margin(b = 1, unit = "pt")
    ),
    barwidth = unit(
      style_numeric(
        typography,
        if (horizontal) "colorbar_horizontal_width" else "colorbar_width",
        default_barwidth
      ),
      "pt"
    ),
    barheight = unit(
      style_numeric(
        typography,
        if (horizontal) "colorbar_horizontal_height" else "colorbar_height",
        default_barheight
      ),
      "pt"
    ),
    ticks = TRUE,
    draw.llim = FALSE,
    draw.ulim = FALSE,
    frame.colour = NA,
    nbin = 120
  )
}

continuous_scale_breaks <- function(values, max_breaks = 3) {
  finite_values <- values[is.finite(values)]
  if (length(finite_values) < 1) {
    return(waiver())
  }
  range_values <- range(finite_values, na.rm = TRUE)
  if (identical(range_values[[1]], range_values[[2]])) {
    return(range_values[[1]])
  }
  max_breaks <- max(2, min(3, round(as.numeric(max_breaks))))
  breaks <- pretty(range_values, n = max_breaks)
  breaks <- breaks[breaks >= range_values[[1]] & breaks <= range_values[[2]]]
  if (length(breaks) > max_breaks) {
    breaks <- breaks[round(seq(1, length(breaks), length.out = max_breaks))]
  }
  if (length(breaks) < 2) {
    breaks <- range_values
  }
  unique(breaks)
}

heatmap_scale_components <- function(display_payload, values, name = NULL, limits = NULL, midpoint = NULL) {
  finite_values <- values[is.finite(values)]
  if (length(finite_values) < 1) {
    finite_values <- c(0, 1)
  }
  value_range <- range(finite_values, na.rm = TRUE)
  crosses_zero <- value_range[[1]] < 0 && value_range[[2]] > 0
  if (is.null(midpoint)) {
    midpoint <- if (crosses_zero) 0 else mean(value_range)
  }
  colorbar_max_breaks <- max(2, min(3, round(style_numeric(style_typography(display_payload), "colorbar_max_breaks", 3))))
  breaks <- if (is.null(limits)) {
    continuous_scale_breaks(finite_values, max_breaks = colorbar_max_breaks)
  } else {
    continuous_scale_breaks(limits, max_breaks = colorbar_max_breaks)
  }
  guide <- publication_colorbar_guide(display_payload, title = name, bar_orientation = "horizontal")
  list(
    finite_values = finite_values,
    crosses_zero = crosses_zero,
    midpoint = midpoint,
    breaks = breaks,
    guide = guide
  )
}

heatmap_fill_scale <- function(display_payload, values, name = NULL, limits = NULL, midpoint = NULL) {
  components <- heatmap_scale_components(display_payload, values, name = name, limits = limits, midpoint = midpoint)
  if (components$crosses_zero) {
    return(scale_fill_gradient2(
      low = style_color(display_payload, "heatmap_low", "heatmap_low", "#2166AC"),
      mid = style_color(display_payload, "heatmap_mid", "heatmap_mid", "#F7F7F7"),
      high = style_color(display_payload, "heatmap_high", "heatmap_high", "#B2182B"),
      midpoint = components$midpoint,
      limits = limits,
      breaks = components$breaks,
      name = name,
      guide = components$guide
    ))
  }
  scale_fill_gradientn(
    colours = c(
      style_color(display_payload, "heatmap_seq_low", "heatmap_seq_low", "#F4F8FA"),
      style_color(display_payload, "heatmap_seq_mid", "heatmap_seq_mid", "#9DD2D3"),
      style_color(display_payload, "heatmap_seq_high", "heatmap_seq_high", "#0B4F6C")
    ),
    limits = limits,
    breaks = components$breaks,
    name = name,
    guide = components$guide
  )
}

heatmap_colour_scale <- function(display_payload, values, name = NULL, limits = NULL, midpoint = NULL) {
  components <- heatmap_scale_components(display_payload, values, name = name, limits = limits, midpoint = midpoint)
  if (components$crosses_zero) {
    return(scale_color_gradient2(
      low = style_color(display_payload, "heatmap_low", "heatmap_low", "#2166AC"),
      mid = style_color(display_payload, "heatmap_mid", "heatmap_mid", "#F7F7F7"),
      high = style_color(display_payload, "heatmap_high", "heatmap_high", "#B2182B"),
      midpoint = components$midpoint,
      limits = limits,
      breaks = components$breaks,
      name = name,
      guide = components$guide
    ))
  }
  scale_color_gradientn(
    colours = c(
      style_color(display_payload, "heatmap_seq_low", "heatmap_seq_low", "#F4F8FA"),
      style_color(display_payload, "heatmap_seq_mid", "heatmap_seq_mid", "#9DD2D3"),
      style_color(display_payload, "heatmap_seq_high", "heatmap_seq_high", "#0B4F6C")
    ),
    limits = limits,
    breaks = components$breaks,
    name = name,
    guide = components$guide
  )
}

heatmap_text_colours <- function(display_payload, values) {
  finite_values <- values[is.finite(values)]
  if (length(finite_values) < 1) {
    return(rep(style_text_color(display_payload), length(values)))
  }
  value_range <- range(finite_values, na.rm = TRUE)
  if (identical(value_range[[1]], value_range[[2]])) {
    intensity <- rep(0, length(values))
  } else if (value_range[[1]] < 0 && value_range[[2]] > 0) {
    max_abs <- max(abs(value_range))
    intensity <- abs(values) / max_abs
  } else {
    intensity <- (values - value_range[[1]]) / (value_range[[2]] - value_range[[1]])
  }
  ifelse(is.finite(intensity) & intensity >= 0.72, "#FFFFFF", style_text_color(display_payload))
}

theme_publication_colorbar <- function(display_payload) {
  typography <- style_typography(display_payload)
  text_color <- style_text_color(display_payload)
  legend_size <- style_numeric(typography, "legend_size", 7.2)
  colorbar_text_size <- min(legend_size, style_numeric(typography, "colorbar_label_size", 6.0))
  theme(
    legend.position = "bottom",
    legend.box = "horizontal",
    legend.justification = "center",
    legend.title = element_text(size = colorbar_text_size, colour = text_color, margin = margin(b = 2.5, unit = "pt")),
    legend.text = element_text(size = colorbar_text_size, colour = text_color, margin = margin(t = 4, unit = "pt")),
    legend.margin = margin(4, 8, 8, 8, unit = "pt"),
    legend.spacing.x = unit(8, "pt"),
    legend.spacing.y = unit(3, "pt"),
    legend.box.spacing = unit(9, "pt")
  )
}

style_series_palette <- function(display_payload, labels) {
  labels <- as.character(labels)
  if (length(labels) < 1) {
    return(character())
  }
  role_order <- c(
    "model_curve",
    "comparator_curve",
    "series_3",
    "series_4",
    "series_5",
    "series_6",
    "reference_line",
    "highlight_band"
  )
  palette <- style_palette(display_payload)
  fallback_values <- c(
    style_color(display_payload, "model_curve", "primary", "#0B4F6C"),
    style_color(display_payload, "comparator_curve", "secondary", "#2A9D8F"),
    style_color(display_payload, "series_3", "tertiary", "#B84A3A"),
    style_color(display_payload, "series_4", "quaternary", "#D99A2B"),
    style_color(display_payload, "series_5", "violet", "#6F63B6"),
    style_color(display_payload, "series_6", "neutral_mid", "#767676"),
    style_color(display_payload, "reference_line", "neutral", "#4D4D4D"),
    style_color(display_payload, "highlight_band", "light", "#F2F5F7")
  )
  values <- vapply(seq_along(labels), function(index) {
    role_name <- role_order[[((index - 1) %% length(role_order)) + 1]]
    if (index <= length(role_order)) {
      style_color(display_payload, role_name = role_name, fallback = fallback_values[[index]])
    } else {
      palette_values <- unlist(palette, use.names = FALSE)
      if (length(palette_values) > 0) {
        palette_values[[((index - 1) %% length(palette_values)) + 1]]
      } else {
        fallback_values[[((index - 1) %% length(fallback_values)) + 1]]
      }
    }
  }, character(1))
  stats::setNames(values, labels)
}

theme_publication <- function(display_payload = list()) {
  render_context <- render_context_from_payload(display_payload)
  layout_override <- render_context$layout_override %||% list()
  show_figure_title <- style_bool(layout_override, "show_figure_title", FALSE)
  typography <- style_typography(display_payload)
  stroke <- style_stroke(display_payload)
  grid_spec <- style_grid(display_payload)
  font_family <- trimws(as.character(typography$font_family %||% "sans"))
  base_size <- style_numeric(typography, "base_size", 11.0)
  title_size <- style_numeric(typography, "title_size", 12.5)
  axis_title_size <- style_numeric(typography, "axis_title_size", 11.0)
  tick_size <- style_numeric(typography, "tick_size", 10.0)
  legend_size <- style_numeric(typography, "legend_size", tick_size)
  legend_key_width <- style_numeric(typography, "legend_key_width", 18.0)
  legend_key_height <- style_numeric(typography, "legend_key_height", 7.0)
  legend_key_spacing_x <- style_numeric(typography, "legend_key_spacing_x", 5.0)
  legend_key_spacing_y <- style_numeric(typography, "legend_key_spacing_y", 3.0)
  text_color <- style_text_color(display_payload)
  grid_linewidth <- style_numeric(stroke, "grid_linewidth", 0.25)
  axis_linewidth <- style_numeric(stroke, "axis_linewidth", 0.35)
  grid_color <- style_grid_color(display_payload)
  axis_color <- style_color(display_payload, role_name = "axis_line", palette_key = "axis", fallback = text_color)
  major_axis <- tolower(trimws(as.character(grid_spec$major_axis %||% "both")))
  minor_axis <- tolower(trimws(as.character(grid_spec$minor_axis %||% "none")))
  major_grid <- if (style_bool(grid_spec, "major", TRUE)) {
    element_line(colour = grid_color, linewidth = grid_linewidth, linetype = trimws(as.character(grid_spec$linetype %||% "solid")))
  } else {
    element_blank()
  }
  minor_grid <- if (style_bool(grid_spec, "minor", FALSE)) {
    element_line(colour = grid_color, linewidth = grid_linewidth * 0.6, linetype = trimws(as.character(grid_spec$minor_linetype %||% grid_spec$linetype %||% "solid")))
  } else {
    element_blank()
  }
  theme_classic(base_size = base_size, base_family = font_family) +
    theme(
      text = element_text(family = font_family, colour = text_color),
      plot.title = if (show_figure_title) element_text(face = "bold", colour = text_color, size = title_size, hjust = 0, margin = margin(b = 5)) else element_blank(),
      plot.subtitle = element_text(colour = text_color, size = base_size, margin = margin(b = 4)),
      axis.title = element_text(face = "plain", colour = text_color, size = axis_title_size),
      axis.text = element_text(colour = text_color, size = tick_size),
      axis.line = element_line(colour = axis_color, linewidth = axis_linewidth),
      axis.ticks = element_line(colour = axis_color, linewidth = axis_linewidth),
      axis.ticks.length = unit(1.6, "pt"),
      legend.text = element_text(size = legend_size, colour = text_color, margin = margin(r = 4, unit = "pt")),
      legend.position = "bottom",
      legend.box = "horizontal",
      legend.justification = "center",
      legend.title = element_blank(),
      legend.background = element_blank(),
      legend.box.background = element_blank(),
      legend.key = element_blank(),
      legend.key.height = unit(legend_key_height, "pt"),
      legend.key.width = unit(legend_key_width, "pt"),
      legend.spacing.x = unit(legend_key_spacing_x, "pt"),
      legend.spacing.y = unit(legend_key_spacing_y, "pt"),
      legend.box.spacing = unit(5, "pt"),
      panel.background = element_rect(fill = style_color(display_payload, role_name = "figure_background", palette_key = "background", fallback = "#FFFFFF"), colour = NA),
      panel.border = element_blank(),
      panel.grid.major.x = if (major_axis %in% c("x", "both", "all")) major_grid else element_blank(),
      panel.grid.major.y = if (major_axis %in% c("y", "both", "all")) major_grid else element_blank(),
      panel.grid.minor.x = if (minor_axis %in% c("x", "both", "all")) minor_grid else element_blank(),
      panel.grid.minor.y = if (minor_axis %in% c("y", "both", "all")) minor_grid else element_blank(),
      strip.background = element_blank(),
      strip.text = element_text(face = "bold", colour = text_color, size = style_numeric(typography, "panel_label_size", axis_title_size)),
      plot.background = element_rect(fill = style_color(display_payload, role_name = "figure_background", palette_key = "background", fallback = "#FFFFFF"), colour = NA),
      plot.margin = margin(7, 8, 7, 8)
    )
}

