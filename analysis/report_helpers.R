# Display helpers for the bilingual report (Columbus_Spatial_Analysis.Rmd).
# Nothing here computes statistics: every number comes from objects built in analysis/core.Rmd
# and analysis/simulation.Rmd. Text is produced twice, once per language, and the page shows one.

# ---------- number formatting ----------
minus <- function(s) sub("^-", "−", s)
FE <- function(x, d = 3) minus(formatC(x, format = "f", digits = d, big.mark = ","))
FI <- function(x, d = 3) minus(formatC(x, format = "f", digits = d, big.mark = ".", decimal.mark = ","))
FL <- function(x, d = 3, lang = "en") if (lang == "id") FI(x, d) else FE(x, d)
NE <- function(x) formatC(x, format = "d", big.mark = ",")
NI <- function(x) formatC(x, format = "d", big.mark = ".")
PE <- function(p) if (p < 0.001) "< 0.001" else FE(p, 3)
PI <- function(p) if (p < 0.001) "< 0,001" else FI(p, 3)
PL <- function(p, lang = "en") if (lang == "id") PI(p) else PE(p)
esc <- function(s) htmltools::htmlEscape(as.character(s))
and_list <- function(x, lang = "en") {
  x <- as.character(x); k <- length(x)
  if (k == 0) return(if (lang == "id") "tidak ada" else "none")
  if (k == 1) return(x)
  paste0(paste(x[-k], collapse = ", "), if (lang == "id") " dan " else " and ", x[k])
}

# ---------- weights-matrix labels ----------
FAM <- list(en = c("Contiguity" = "Contiguity", "KNN" = "K nearest neighbours", "Distance band" = "Distance band", "Inverse distance" = "Inverse distance"),
            id = c("Contiguity" = "Kontiguitas", "KNN" = "K tetangga terdekat", "Distance band" = "Pita jarak", "Inverse distance" = "Invers jarak"))
spec_lab <- function(id, lang = "en") {
  if (!length(id)) return(character(0))
  s <- specs[match(id, specs$id), ]
  v <- if (lang == "id") gsub("(\\d)\\.(\\d)", "\\1,\\2", s$variant) else s$variant
  st <- ifelse(s$family == "Inverse distance" & s$style == "B", if (lang == "id") "mentah" else "raw", s$style)
  paste0(v, " · ", st)
}
# simulation labels (Indonesian strings built in analysis/simulation.Rmd) back to ids
lab_to_id <- function(s) names(lab)[match(s, lab)]
relabel_list <- function(s, lang) paste(spec_lab(lab_to_id(strsplit(s, "; ", fixed = TRUE)[[1]]), lang), collapse = "; ")

# ---------- tables ----------
# df: data.frame of already formatted text. raw: columns holding HTML (badges). left: left-aligned columns.
html_table <- function(df, raw = character(), left = 1, wide = character(), hl = NULL) {
  nm <- names(df)
  cls <- function(j) paste(c(if (j %in% left || nm[j] %in% left) "l", if (nm[j] %in% wide) "w"), collapse = " ")
  th <- paste0(vapply(seq_along(nm), function(j) sprintf('<th scope="col" class="%s">%s</th>', cls(j), esc(nm[j])), ""), collapse = "")
  rows <- vapply(seq_len(nrow(df)), function(i) {
    td <- vapply(seq_along(nm), function(j) {
      v <- df[[j]][i]; v <- if (nm[j] %in% raw) as.character(v) else esc(v)
      sprintf('<td class="%s">%s</td>', cls(j), v)
    }, "")
    sprintf('<tr%s>%s</tr>', if (!is.null(hl) && isTRUE(hl[i])) ' class="hl"' else "", paste0(td, collapse = ""))
  }, "")
  paste0('<div class="tbl-wrap"><table><thead><tr>', th, '</tr></thead><tbody>', paste0(rows, collapse = ""), '</tbody></table></div>')
}
# fun(lang) returns list(df = , cap = , foot = ) ; everything else goes to html_table
bi_table <- function(fun, ..., cls = "") {
  out <- vapply(c("en", "id"), function(l) {
    r <- fun(l)
    paste0('<div class="tbl ', l, if (nzchar(cls)) paste0(" ", cls), '">', if (!is.null(r$cap)) paste0('<p class="cap">', r$cap, '</p>'),
           html_table(r$df, ...), if (!is.null(r$foot)) paste0('<p class="foot">', r$foot, '</p>'), '</div>')
  }, "")
  cat(paste0(out, collapse = "\n"), "\n")
}
badge <- function(cls, lang = "en") {
  k <- c(Robust = "robust", Menengah = "mid", Sensitif = "sens")[cls]
  t <- if (lang == "id") cls else c(Robust = "Robust", Menengah = "Intermediate", Sensitif = "Sensitive")[cls]
  sprintf('<span class="badge %s">%s</span>', k, t)
}
pass <- function(ok, lang = "en") sprintf('<span class="badge %s">%s</span>', if (ok) "pass" else "fail",
                                          if (ok) (if (lang == "id") "Lulus" else "Pass") else (if (lang == "id") "Gagal" else "Fail"))

# ---------- figures ----------
# Colours and theme come from analysis/style.R (loaded by core.Rmd), so report figures, output/png and the dashboard agree.
if (!exists("ARC")) source("analysis/style.R")
PAL <- list(bg = ARC$field, text = ARC$ink, muted = ARC$muted, faint = ARC$faint, moran = ARC$moran, geary = ARC$geary,
            accent = ARC$maroon, band = ARC$band, ns = ARC$ns, robust = ARC$robust, mid = ARC$mid, sens = ARC$sens)
PF <- ARC_FONT
theme_case <- function(base = 12.5) theme_archive(base)
png_uri <- function(p, w, h) {
  f <- tempfile(fileext = ".png")
  if (capabilities("cairo")) png(f, width = w, height = h, units = "in", res = 144, type = "cairo", bg = PAL$bg)
  else png(f, width = w, height = h, units = "in", res = 144, bg = PAL$bg)
  print(p); dev.off()
  knitr::image_uri(f)
}
EXN <- 0L
# make(lang) returns a ggplot (or an HTML string when html = TRUE). title/cap/alt: named c(en = , id = ).
exhibit <- function(make, title, cap, alt = title, w = 9, h = 5.5, html = FALSE, bilingual = TRUE) {
  EXN <<- EXN + 1L
  body <- function(l) {
    obj <- make(l)
    if (html) obj else sprintf('<img src="%s" alt="%s" width="%d" height="%d" loading="lazy">', png_uri(obj, w, h), esc(alt[[l]]), round(w * 100), round(h * 100))
  }
  b <- if (bilingual) paste0('<div class="en">', body("en"), '</div><div class="id">', body("id"), '</div>') else body("en")
  cat(sprintf('<figure class="exhibit" id="ex%d"><div class="ex-head"><span class="tag"><span class="en">Figure %d</span><span class="id">Gambar %d</span></span><span class="ex-title"><span class="en">%s</span><span class="id">%s</span></span></div><div class="ex-body">%s</div><figcaption><p><span class="en">%s</span><span class="id">%s</span></p></figcaption></figure>\n',
              EXN, EXN, EXN, title[["en"]], title[["id"]], b, cap[["en"]], cap[["id"]]))
}

# ---------- inline SVG maps (no text inside, so one map serves both languages) ----------
.bb <- NULL
map_paths <- function() {
  bb <- sf::st_bbox(col); s <- 600 / (bb[["xmax"]] - bb[["xmin"]])
  .bb <<- list(x0 = bb[["xmin"]], y1 = bb[["ymax"]], s = s, H = (bb[["ymax"]] - bb[["ymin"]]) * s)
  vapply(rings, function(rs) paste0(vapply(rs, function(m) {
    m <- matrix(unlist(m), ncol = 2)
    paste0("M", paste(sprintf("%.1f,%.1f", (m[, 1] - .bb$x0) * s, (.bb$y1 - m[, 2]) * s), collapse = "L"), "Z")
  }, ""), collapse = ""), "")
}
svg_map <- function(fill, tip, label, edges = NULL, nodes = FALSE, hl = NULL) {
  P <- map_paths(); s <- .bb$s
  px <- (cc[, 1] - .bb$x0) * s; py <- (.bb$y1 - cc[, 2]) * s
  reg <- paste0(sprintf('<path class="%s" d="%s" fill="%s"><title>%s</title></path>',
                        if (is.null(hl)) "reg" else ifelse(hl, "reg hl", "reg"), P, fill,
                        esc(tip)), collapse = "")
  e <- if (!is.null(edges) && nrow(edges)) paste0(sprintf('<line class="edge" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>',
                                                          px[edges[, 1]], py[edges[, 1]], px[edges[, 2]], py[edges[, 2]]), collapse = "") else ""
  nd <- if (nodes) paste0(sprintf('<circle class="node" cx="%.1f" cy="%.1f" r="2.2"/>', px, py), collapse = "") else ""
  sprintf('<svg class="map" viewBox="0 0 600 %.0f" role="img" aria-label="%s">%s%s%s</svg>', .bb$H, esc(label), reg, e, nd)
}
legend_html <- function(cols, labs, title = NULL) paste0('<div class="legend">', if (!is.null(title)) paste0('<b class="lt">', title, '</b>'),
  paste0(sprintf('<span><i class="sw" style="background:%s"></i>%s</span>', cols, labs), collapse = ""), '</div>')
# class legend with the number of areas in each class, e.g. "High-High (4)"
legend_count <- function(cols, labs, n, title = NULL) legend_html(cols, sprintf('%s <span class="n">(%d)</span>', labs, n), title)
