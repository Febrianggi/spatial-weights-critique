# Archive style shared by every figure: output/png (core.Rmd), output/simulasi (simulation.Rmd)
# and the report exhibits (report_helpers.R). The same colours are used in dashboard_html/template.html,
# report_assets/report.css and index.html, so a class has one colour wherever it appears.

ARC <- list(
  paper = "#F1F1EC", field = "#FAFAF7", rule = "#C9D3DF", grid = "#E3E6EA",
  ink = "#17233B", muted = "#4B5566", faint = "#5A6271", maroon = "#7D1F31",
  moran = "#24477A", geary = "#9A3D24",          # series: Moran solid circle, Geary hollow triangle
  ns = "#E2E0D8", ns_line = "#FFFFFF",
  band = "#E8EAEE",                               # |z| < 1.96 and other "nothing here" bands
  ok_band = "#DCE8DE", bad_band = "#F1DCDC",      # acceptable / sensitive zones
  robust = "#2D6A4A", mid = "#5F6673", sens = "#A3263A"
)

# Local classes. Clusters (HH, LL) are saturated, outliers (HL, LH) are light, not significant is warm grey.
COL_LISA <- c(HH = "#A3263A", LL = "#24477A", HL = "#E7A9AE", LH = "#A9C1DE", NS = ARC$ns)
LISA_LAB <- list(en = c(HH = "High-High", LL = "Low-Low", HL = "High-Low", LH = "Low-High", NS = "Not significant"),
                 id = c(HH = "Tinggi-Tinggi", LL = "Rendah-Rendah", HL = "Tinggi-Rendah", LH = "Rendah-Tinggi", NS = "Tidak signifikan"))
COL_GI <- c("Hot spot" = COL_LISA[["HH"]], "Cold spot" = COL_LISA[["LL"]], "Tidak signifikan" = ARC$ns)
COL_LC <- c("High-High" = COL_LISA[["HH"]], "Low-Low" = COL_LISA[["LL"]], "Other Positive" = "#C99A2E",
            "Negative" = "#6A4C93", "Tidak signifikan" = ARC$ns)
# p after FDR: the smallest p is the darkest.
SIG_LV <- c("p ≤ 0,001", "p ≤ 0,01", "p ≤ 0,05", "Tidak signifikan")
COL_SIG <- setNames(c("#17233B", "#4A6A99", "#A9BCD6", ARC$ns), SIG_LV)
# Moran-Geary agreement (distinct colours: Hanya Moran signifikan uses teal-blue to avoid colliding with LL/Sepakat negatif)
COL_AGREE <- c("Sepakat: positif" = COL_LISA[["HH"]], "Sepakat: negatif" = COL_LISA[["LL"]], "Sepakat: tidak signifikan" = ARC$ns,
               "Hanya Moran signifikan" = "#2B7A8B", "Hanya Geary signifikan" = ARC$geary, "Arah berlawanan" = "#6A4C93")
COL_CONC <- c("Positif" = COL_LISA[["HH"]], "Negatif" = COL_LISA[["LL"]], "Tidak signifikan" = "#9AA0A8")
COL_IDX <- c("Moran's I" = ARC$moran, "Geary's C" = ARC$geary)
SHP_IDX <- c("Moran's I" = 16, "Geary's C" = 2)
# values (any variable): light to dark ink-blue, five classes
RAMP_VAL <- c("#E6EBF1", "#BCC9DA", "#8AA1BF", "#55739D", "#24477A")
# continuous scales (weights, power, agreement): paper through ink-blue to ink
SEQ_LO <- "#F4F4F0"; SEQ_HI <- "#17233B"
SEQ_RAMP <- c(SEQ_LO, "#BCC9DA", "#55739D", "#24477A", SEQ_HI)
seq_col <- function(t) scales::gradient_n_pal(SEQ_RAMP)(pmin(pmax(t, 0), 1))

ARC_FONT <- local({
  ok <- nzchar(Sys.which("fc-list")) && any(grepl("^Inter", suppressWarnings(system2("fc-list", ":family", stdout = TRUE))))
  if (ok) "Inter" else "sans"
})

theme_archive <- function(base = 11, family = ARC_FONT) {
  ggplot2::theme_minimal(base_size = base, base_family = family) +
    ggplot2::theme(
      plot.background = ggplot2::element_rect(fill = ARC$field, colour = NA),
      panel.background = ggplot2::element_rect(fill = ARC$field, colour = NA),
      text = ggplot2::element_text(colour = ARC$ink),
      plot.title = ggplot2::element_text(face = "bold", colour = ARC$ink, size = ggplot2::rel(1.12)),
      plot.title.position = "plot", plot.caption.position = "plot",
      plot.subtitle = ggplot2::element_text(colour = ARC$muted, margin = ggplot2::margin(b = 6)),
      plot.caption = ggplot2::element_text(colour = ARC$faint, hjust = 0, size = ggplot2::rel(.85)),
      axis.text = ggplot2::element_text(colour = ARC$muted), axis.title = ggplot2::element_text(colour = ARC$muted, size = ggplot2::rel(.92)),
      axis.line.x = ggplot2::element_line(colour = ARC$rule, linewidth = .4),
      panel.grid = ggplot2::element_line(colour = ARC$grid, linewidth = .35), panel.grid.minor = ggplot2::element_blank(),
      strip.text = ggplot2::element_text(colour = ARC$ink, face = "bold", hjust = 0, size = ggplot2::rel(.95)),
      legend.position = "top", legend.justification = "left",
      legend.title = ggplot2::element_text(colour = ARC$muted, size = ggplot2::rel(.9)),
      legend.text = ggplot2::element_text(colour = ARC$ink), legend.key = ggplot2::element_rect(fill = ARC$field, colour = NA),
      plot.margin = ggplot2::margin(10, 14, 10, 10))
}
# maps: no axes, same paper field, regions outlined in white
theme_archive_map <- function(base = 10) {
  theme_archive(base) + ggplot2::theme(axis.text = ggplot2::element_blank(), axis.title = ggplot2::element_blank(),
                                       axis.ticks = ggplot2::element_blank(), axis.line.x = ggplot2::element_blank(),
                                       panel.grid = ggplot2::element_blank())
}
# text on a filled tile: black or white, whichever has the higher WCAG contrast (>= 4.58:1 across any luminance)
ink_on <- function(hex) {
  lum <- function(h) { m <- grDevices::col2rgb(h) / 255; m <- ifelse(m <= .03928, m / 12.92, ((m + .055) / 1.055)^2.4)
    .2126 * m[1, ] + .7152 * m[2, ] + .0722 * m[3, ] }
  L <- lum(hex)
  ifelse((L + .05) / .05 >= 1.05 / (L + .05), "#000000", "#FFFFFF")
}
# power curves: three most robust (green, solid), three most sensitive (red, dashed), Queen · W (ink, dotted)
CUR_COL <- c("#1F5A3C", "#3E8A60", "#7DB892", "#E58A93", "#C2485A", "#8A1B2E", ARC$ink)
CUR_SHP <- c(16, 17, 15, 1, 2, 0, 4)
CUR_LTY <- c("solid", "solid", "solid", "22", "22", "22", "11")
