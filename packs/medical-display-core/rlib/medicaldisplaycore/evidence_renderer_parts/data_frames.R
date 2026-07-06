build_curve_dataframe <- function(series_payload) {
  frames <- lapply(seq_along(series_payload), function(index) {
    item <- series_payload[[index]]
    x <- as_numeric_vector(item$x, sprintf("series[%d].x", index))
    y <- as_numeric_vector(item$y, sprintf("series[%d].y", index))
    if (length(x) != length(y)) {
      stop(sprintf("series[%d].x and series[%d].y must have the same length", index, index))
    }
    data.frame(
      label = rep(trimws(as.character(item$label %||% "")), length(x)),
      x = x,
      y = y,
      stringsAsFactors = FALSE
    )
  })
  do.call(rbind, frames)
}

build_reference_dataframe <- function(reference_line) {
  if (is.null(reference_line)) {
    return(NULL)
  }
  x <- as_numeric_vector(reference_line$x, "reference_line.x")
  y <- as_numeric_vector(reference_line$y, "reference_line.y")
  if (length(x) != length(y)) {
    stop("reference_line.x and reference_line.y must have the same length")
  }
  data.frame(x = x, y = y)
}

build_point_dataframe <- function(points_payload, x_field = "x", y_field = "y") {
  frames <- lapply(seq_along(points_payload), function(index) {
    item <- points_payload[[index]]
    data.frame(
      x = as.numeric(item[[x_field]]),
      y = as.numeric(item[[y_field]]),
      group = trimws(as.character(item$group %||% "")),
      stringsAsFactors = FALSE
    )
  })
  do.call(rbind, frames)
}

extract_label_vector <- function(items_payload, field_name) {
  if (!is.list(items_payload) || length(items_payload) < 1) {
    stop(sprintf("%s must contain at least one labeled item", field_name))
  }
  labels <- vapply(seq_along(items_payload), function(index) {
    item <- items_payload[[index]]
    label <- trimws(as.character(item$label %||% ""))
    if (!nzchar(label)) {
      stop(sprintf("%s[%d].label must be non-empty", field_name, index))
    }
    label
  }, character(1))
  labels
}

build_heatmap_dataframe <- function(cells_payload, column_order = NULL, row_order = NULL) {
  frames <- lapply(seq_along(cells_payload), function(index) {
    item <- cells_payload[[index]]
    data.frame(
      x = trimws(as.character(item$x %||% "")),
      y = trimws(as.character(item$y %||% "")),
      value = as.numeric(item$value),
      stringsAsFactors = FALSE
    )
  })
  heat_df <- do.call(rbind, frames)
  x_levels <- if (is.null(column_order)) unique(heat_df$x) else column_order
  y_levels <- if (is.null(row_order)) rev(unique(heat_df$y)) else rev(row_order)
  heat_df$x <- factor(heat_df$x, levels = x_levels)
  heat_df$y <- factor(heat_df$y, levels = y_levels)
  heat_df
}

build_forest_dataframe <- function(rows_payload) {
  frames <- lapply(seq_along(rows_payload), function(index) {
    item <- rows_payload[[index]]
    data.frame(
      label = trimws(as.character(item$label %||% "")),
      estimate = as.numeric(item$estimate),
      lower = as.numeric(item$lower),
      upper = as.numeric(item$upper),
      stringsAsFactors = FALSE
    )
  })
  forest_df <- do.call(rbind, frames)
  forest_df$label <- factor(forest_df$label, levels = rev(forest_df$label))
  forest_df
}

