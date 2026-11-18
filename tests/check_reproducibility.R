# Bandingkan keluaran dua knit independen. Pemakaian: Rscript tests/check_reproducibility.R <folder_a> <folder_b>
a <- commandArgs(TRUE)[1]; b <- commandArgs(TRUE)[2]
fa <- sort(list.files(file.path(a, "output/csv"))); fb <- sort(list.files(file.path(b, "output/csv")))
stopifnot(identical(fa, fb))
same <- vapply(fa, function(f) identical(unname(tools::md5sum(file.path(a, "output/csv", f))), unname(tools::md5sum(file.path(b, "output/csv", f)))), TRUE)
ja <- jsonlite::fromJSON(file.path(a, "output/json/columbus_results.json")); jb <- jsonlite::fromJSON(file.path(b, "output/json/columbus_results.json"))
ja$meta$generated <- jb$meta$generated <- NULL
json_same <- identical(ja, jb)
pa <- sort(list.files(file.path(a, "output/png"))); png_same <- vapply(pa, function(f) identical(unname(tools::md5sum(file.path(a, "output/png", f))), unname(tools::md5sum(file.path(b, "output/png", f)))), TRUE)
cat(sprintf("CSV identik byte per byte: %d dari %d\n", sum(same), length(same)))
cat(sprintf("JSON identik (di luar stempel waktu): %s\n", json_same))
cat(sprintf("PNG identik byte per byte: %d dari %d\n", sum(png_same), length(png_same)))
if (!all(same) || !json_same) { cat("Berbeda:", fa[!same], "\n"); quit(status = 1) }
