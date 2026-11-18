# Validasi seluruh keluaran Rmd: kelengkapan, rentang, konsistensi silang, CSV = JSON = RDS, PNG, laporan HTML.
# Jalankan dari folder proyek: Rscript tests/validate_outputs.R
suppressPackageStartupMessages({ library(jsonlite); library(dplyr) })
ok <- 0L; fail <- character()
chk <- function(name, cond) { if (isTRUE(cond)) ok <<- ok + 1L else fail <<- c(fail, name) }
rd <- function(f) read.csv(file.path("output/csv", f), check.names = FALSE, encoding = "UTF-8")

csvs <- list.files("output/csv", "\\.csv$")
chk("jumlah CSV >= 40", length(csvs) >= 40)
for (f in csvs) { d <- rd(f); chk(paste("CSV tidak kosong:", f), nrow(d) > 0 && ncol(d) > 0) }

g <- rd("05_global_moran_geary_semua_spesifikasi.csv")
chk("global: 384 baris", nrow(g) == 384)
chk("global: 32 spesifikasi x 6 variabel x 2 indeks", length(unique(g$spec_id)) == 32 && length(unique(g$var)) == 6)
chk("global: tidak ada NA pada kolom inti", !anyNA(g[, c("stat", "expected", "z_perm", "p_two", "es", "p_mc_se")]))
chk("global: p dalam [2/(R+1), 1]", all(g$p_two >= 2 / 10000 - 1e-12 & g$p_two <= 1))
chk("global: E(I) = -1/48", all(abs(g$expected[g$index == "Moran's I"] + 1 / 48) < 1e-12))
chk("global: E(C) = 1", all(abs(g$expected[g$index == "Geary's C"] - 1) < 1e-12))
chk("global: ES = I - E(I) dan 1 - C", all(abs(ifelse(g$index == "Moran's I", g$stat - g$expected, g$expected - g$stat) - g$es) < 1e-12))
chk("global: kesimpulan konsisten dengan p dan arah", all(
  (g$p_two >= 0.05 & g$conclusion == "Tidak signifikan") |
  (g$p_two < 0.05 & g$es > 0 & g$conclusion == "Positif") | (g$p_two < 0.05 & g$es < 0 & g$conclusion == "Negatif")))
chk("global: IK Monte Carlo memuat p", all(g$p_mc_lo <= g$p_two & g$p_two <= g$p_mc_hi))

a <- rd("11_kesepakatan_moran_geary.csv")
m <- g |> select(spec_id, var, index, conclusion) |> tidyr::pivot_wider(names_from = index, values_from = conclusion)
aa <- left_join(a, m, by = c("spec_id", "var"))
chk("kesepakatan: 192 baris dan cocok dengan global", nrow(a) == 192 && all(aa$M == aa$`Moran's I`) && all(aa$G == aa$`Geary's C`))

si <- rd("07_sensitivitas_inferensial.csv")
re <- g |> group_by(var, index) |> summarise(ps = 100 * mean(p_two < 0.05), sdz = sd(z_perm), .groups = "drop")
x <- left_join(si, re, by = c("var", "index"))
chk("sensitivitas inferensial: % signifikan dan SD z cocok dengan global", all(abs(x$`% signifikan` - x$ps) < 1e-9) && all(abs(x$`SD z` - x$sdz) < 1e-9))
sn <- rd("06_sensitivitas_numerik.csv")
re2 <- g |> group_by(var, index) |> summarise(r = max(es) - min(es), .groups = "drop")
chk("sensitivitas numerik: rentang ES cocok", all(abs(left_join(sn, re2, by = c("var", "index")) |> with(`Rentang ES` - r)) < 1e-12))

l <- rd("19_lisa_semua_spesifikasi.csv"); ls <- rd("20_lisa_ringkasan_per_spesifikasi.csv")
chk("LISA: 9408 baris (32 x 6 x 49)", nrow(l) == 32 * 6 * 49)
chk("LISA: p dan p_fdr dalam [0,1], p_fdr >= p", all(l$p >= 0 & l$p <= 1 & l$p_fdr >= l$p - 1e-12 & l$p_fdr <= 1))
chk("LISA: kelas FDR hanya bila p_fdr < 0.05", all((l$class_fdr != "NS") == (l$p_fdr < 0.05)))
re3 <- l |> group_by(spec_id, var) |> summarise(n = sum(class_fdr != "NS"), hh = sum(class_fdr == "HH"), .groups = "drop")
y <- left_join(ls, re3, by = c("spec_id", "var"))
chk("LISA ringkasan cocok dengan tabel detail", nrow(ls) == 192 && all(y$`Sig. (FDR)` == y$n) && all(y$HH == y$hh))
# BH dihitung ulang
re4 <- l |> group_by(spec_id, var) |> mutate(bh = p.adjust(p, "BH")) |> ungroup()
chk("LISA: p_fdr = BH(p) per peta", max(abs(re4$bh - re4$p_fdr)) < 1e-12)

au <- rd("05b_audit_metodologi.csv"); chk("audit global tersedia (9 baris)", nrow(au) == 9)
lau <- rd("19b_audit_lisa.csv"); chk("audit LISA: klasifikasi sendiri = spdep", grepl("^98 dari 98", lau$Nilai[4]))
eq <- rd("01b_kesetaraan_geoda_spdata.csv"); chk("kesetaraan GeoDa = spData", all(eq$Hasil[c(1, 3, 4)] == "0") && eq$Hasil[5] == "TRUE")

# CSV = JSON = RDS
J <- fromJSON("output/json/columbus_results.json"); R <- readRDS("output/rds/columbus_results.rds")
jg <- as.data.frame(J$global); rg <- as.data.frame(R$global)
key <- function(d) paste(d$spec_id, d$var, d$index)
for (col in c("stat", "z_perm", "p_two", "es")) {
  chk(paste("JSON = CSV:", col), max(abs(jg[[col]][match(key(g), key(jg))] - g[[col]]) / pmax(1, abs(g[[col]]))) < 1e-9)
  chk(paste("RDS = CSV:", col), max(abs(rg[[col]][match(key(g), key(rg))] - g[[col]]) / pmax(1, abs(g[[col]]))) < 1e-12)
}
jl <- as.data.frame(J$lisa); kl <- function(d) paste(d$spec_id, d$var, d$POLYID)
chk("JSON = CSV: kelas LISA", all(jl$class_fdr[match(kl(l), kl(jl))] == l$class_fdr))
chk("JSON: versi 2 dan waktu sama dengan RDS", identical(J$meta$version, "2") && identical(J$meta$generated, R$meta$generated))
chk("JSON: kunci untuk dashboard lengkap", all(c("sensitivity_num", "sensitivity_inf", "sensitivity_local", "comparison", "jackknife", "rank",
                                                  "standardization", "noise_dz", "lisa", "lisa_summary", "edges", "regions") %in% names(J)))

# PNG: tanda tangan, ukuran, dimensi dari header IHDR
pngs <- list.files("output/png", "\\.png$", full.names = TRUE)
chk("jumlah PNG >= 20", length(pngs) >= 20)
for (f in pngs) {
  b <- readBin(f, "raw", 32); w <- sum(as.integer(b[17:20]) * 256^(3:0)); h <- sum(as.integer(b[21:24]) * 256^(3:0))
  chk(paste("PNG valid:", basename(f)), identical(b[1:8], as.raw(c(0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a))) &&
        file.size(f) > 20000 && w >= 900 && h >= 400)
}

# Laporan HTML
h <- paste(readLines("reports/Columbus_Spatial_Analysis.html", warn = FALSE, encoding = "UTF-8"), collapse = "\n")
body <- gsub("<script.*?</script>|<style.*?</style>", "", h, perl = TRUE)
chk("laporan: tidak ada keluaran error R", !grepl("## Error", body, fixed = TRUE))
chk("laporan: tidak ada em dash", !grepl("—", body))
chk("laporan: dua bahasa (tombol EN/ID, teks .en dan .id)", grepl('data-lang="id"', h, fixed = TRUE) && grepl('class="en"', body, fixed = TRUE) && grepl('class="id"', body, fixed = TRUE))
chk("laporan: memuat 11 bab, termasuk simulasi dan rekomendasi", all(sapply(c("why", "data", "matrices", "global", "agreement", "influence", "local", "simulation", "practice", "limits", "repro"),
                                                                  function(id) grepl(sprintf('<section class="chap" id="%s">', id), body, fixed = TRUE))))
chk("laporan: hanya CRIME yang ditampilkan (tidak ada judul variabel lain)", !grepl("<h4>(HOVAL|INC|OPEN|PLUMB|DISCBD)</h4>", body))
chk("laporan: rekomendasi simulasi tertulis", grepl("Recommended when nothing is known", body, fixed = TRUE))
chk("laporan: tidak ada sisa <U+....> dari locale", !grepl("<U+", body, fixed = TRUE))
idx <- paste(readLines("dashboard_html/index.html", warn = FALSE, encoding = "UTF-8"), collapse = "\n")
chk("dashboard HTML: data tersemat dengan waktu yang sama", grepl(R$meta$generated, idx, fixed = TRUE))
chk("dashboard HTML: font Inter tersemat (4 @font-face)", lengths(regmatches(idx, gregexpr("@font-face\\{font-family:'Inter'", idx))) == 4)
chk("dashboard HTML: hasil simulasi CRIME tersemat", grepl("const SIM = {", idx, fixed = TRUE))
chk("RDS hasil simulasi tersedia", file.exists("output/rds/simulasi_crime.rds"))

cat(sprintf("Validasi keluaran: %d lolos, %d gagal\n", ok, length(fail)))
if (length(fail)) { cat(paste("GAGAL:", fail), sep = "\n"); quit(status = 1) }
