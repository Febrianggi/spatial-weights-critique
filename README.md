# When the Definition of Neighbours Changes Spatial Reality

**A critique of Moran's I, Geary's C and LISA through weights-matrix sensitivity, using the Columbus (Ohio, 1980) crime data.**

[Bahasa Indonesia](README.id.md)

## Why this project exists

Moran's I, Geary's C and LISA are easy to misuse. A spatial weights matrix is often picked after the results are seen, and the most significant or tidiest version gets reported. Yet both statistics are functions of two objects, the data *and* the weights matrix *W*. Change *W* and the "spatial reality" you report can change with it, even though the data stay exactly the same.

This project measures how far the results move when only the definition of neighbours changes. The goal is simple: method and matrix choices should rest on a substantive reason and come with a sensitivity check, not on which output looks best.

## Key findings (CRIME)

| Finding | Evidence |
|---|---|
| Local cluster maps can be cherry-picked | Significant LISA cluster regions (FDR 5%) range from **0 to 30** across the 32 matrices; the Queen · W reference gives **4** |
| Effect size depends heavily on *W* | Moran's I ranges from **0.153 to 0.607** for the same data (Geary's C: 0.325 to 0.846) |
| The direction is stable | CRIME is significantly clustered under all 32 matrices; no matrix flips the sign |
| Some matrices are far more robust | In a simulation with 5 known spatial patterns, **1/d · W** loses at most 12 percentage points of power against the best matrix for each pattern; **k = 2** and wide distance bands lose up to 39 |
| For weaker signals, even significance can be picked | In the same pipeline, the significant/not-significant conclusion for HOVAL, OPEN and Geary's C on PLUMB depends on which *W* is used (`output/csv/05d_risiko_specification_searching.csv`) |

**Recommendation.** With no prior information about the spatial process, use **1/d · W** (row-standardized inverse distance) for Moran's I and report other reasonable matrices as a sensitivity check. Queen · W remains reasonable when interaction is expected across shared borders.

## Report

`reports/Columbus_Spatial_Analysis.html` is what you get when you knit the Rmd. It is a single self-contained page (no internet needed) that follows **CRIME only**, in English and Bahasa Indonesia: switch with the EN / ID buttons at the top, or open `Columbus_Spatial_Analysis.html?lang=id`. It walks through the critique in eleven chapters:

1. Why the report exists, and what a good-looking result does not prove
2. The data
3. The 32 neighbour definitions, with neighbour-graph maps
4. Global Moran's I and Geary's C under all 32 matrices, and what a specification search could pick
5. Moran versus Geary
6. The influence of one neighbourhood (jackknife, rank transform)
7. Local clusters (LISA, Gi*, Local Geary) under several matrices
8. The robustness simulation and the answer to the revision: robust, sensitive and recommended matrices
9. What to do instead
10. Limits
11. How to reproduce, references and the R session

## Dashboard

Open `dashboard_html/index.html` in any browser. It works offline, needs no R or server, and contains:

- the critique and the evidence above, computed from the results;
- results for any of the 32 weights matrices (Moran's I, Geary's C, permutation tests, effect sizes);
- CRIME map and local clusters (LISA, Local Geary, Getis–Ord Gi*);
- sensitivity curves and the full 32-matrix table;
- the robustness simulation: robust vs sensitive matrices, power by pattern, and the diagonal vs placement tests.

English is the default. Use the language switch in the header, or open `index.html?lang=id`, for Bahasa Indonesia.

## Repository structure

| Path | Contents |
|---|---|
| `Columbus_Spatial_Analysis.Rmd` | The file to knit. Runs everything below and writes the bilingual CRIME report |
| `analysis/core.Rmd` | All computations for 6 variables × 32 matrices; writes `output/` and the dashboard |
| `analysis/simulation.Rmd` | Robustness simulation for CRIME; writes `output/simulasi/` |
| `analysis/report_helpers.R` | Formatting, bilingual tables, figures and maps for the report (no statistics) |
| `report_assets/` | Page template, CSS and script of the report |
| `reports/Columbus_Spatial_Analysis.html` | Knitted report, self-contained, English and Bahasa Indonesia |
| `dashboard_html/index.html` | Bilingual dashboard with all results embedded |
| `dashboard_html/template.html` | Dashboard template; the Rmd fills it to produce `index.html` |
| `data/geoda_sal/` | Columbus data (GeoDa/SAL distribution): shapefile, `columbus.gal`, metadata |
| `output/csv/` | 42 result tables (data checks, global tests, sensitivity, LISA, jackknife, …) |
| `output/simulasi/` | Simulation results: criteria per matrix, power, calibration, computational tests, figures |
| `output/png/`, `output/json/`, `output/rds/` | Figures, JSON for the dashboard, R objects (results and 32 `listw` objects) |
| `assets/fonts/` | Inter (SIL Open Font License, included) |
| `tests/` | Output validation, reproducibility check, dashboard browser test |
| `docs/CHANGELOG.id.md` | Change log (Bahasa Indonesia) |

## Methods in brief

- **Data:** 49 Columbus neighbourhoods, 1980 (Anselin, 1988). The report, dashboard and simulation focus on **CRIME** (residential burglaries and vehicle thefts per 1,000 households). The computation also covers HOVAL, INC, OPEN, PLUMB and DISCBD; those results are in `output/csv/`.
- **32 weights matrices:** Queen and Rook contiguity; k-nearest neighbours (k = 2, 3, 4, 5, 6, 8); six distance bands; inverse distance 1/d and 1/d². Each in binary or raw form and row-standardized.
- **Global tests:** Moran's I and Geary's C with 9,999 permutations, two-sided p-values with Monte Carlo confidence intervals, oriented z-scores and effect sizes.
- **Local tests:** LISA with conditional permutation without replacement (Anselin, 1995) and Benjamini–Hochberg FDR correction; Local Geary and Getis–Ord Gi* as support.
- **Robustness simulation:** the real CRIME values are rearranged on the map following five known processes (SAR on Queen, k = 4 and a distance band; a geostatistical process; a radial trend). Pattern strength is calibrated so that the best matrix reaches the same power for every process. 25,000 datasets × 32 matrices × 2 indices = 1.6 million tests. Criteria (test size, mean power, maximum regret, worst-case power, Moran–Geary agreement) and class thresholds were fixed before running the simulation.
- **Diagonal vs placement:** computational tests show the results depend on *which* regions are neighbours, not on region labels; the diagonal must be zero (a non-zero diagonal inflates Moran's I).

## Reproduce

Requirements: R ≥ 4.3 with `sf`, `spdep` (≥ 1.3), `spData`, `dplyr`, `tidyr`, `ggplot2`, `patchwork`, `jsonlite`, `knitr`, `rmarkdown`, `scales`, and Pandoc (bundled with RStudio).

```r
install.packages(c("sf", "spdep", "spData", "dplyr", "tidyr", "ggplot2", "patchwork",
                   "jsonlite", "knitr", "rmarkdown", "scales"))
rmarkdown::render("Columbus_Spatial_Analysis.Rmd", output_dir = "reports")
```

Run this from the repository root, or press **Knit** in RStudio (the Rmd sends the HTML to `reports/`). It takes about 10 to 15 minutes and rewrites `output/`, `reports/` and `dashboard_html/index.html`. The seed is fixed (`20261112` for the main analysis, `20261117` for the simulation), so results are identical on every run.

## Tests

```bash
Rscript tests/validate_outputs.R                       # 106 checks on tables, JSON, RDS, figures and report
Rscript tests/check_reproducibility.R <run_a> <run_b>  # two independent knits must match byte for byte
python tests/test_html_dashboard.py . <screenshot_dir> # dashboard vs CSV, both languages, keyboard, mobile (Playwright)
```

Set `CHROME_PATH` to use a specific Chrome binary for the browser test.

## Data source

The Columbus files come from the GeoDa/SAL distribution (metadata identical to <https://geodacenter.github.io/data-and-lab/columbus/>; Anselin, 1988, Table 12.1). The report proves they match `spData::columbus.shp` and Anselin's typed table (`spData::columbus`): all 20 attributes and all 1,196 vertices are identical, and Queen contiguity from the geometry equals GeoDa's `columbus.gal` (236 links). Coordinates have no defined CRS, so distances are in map units; Moran's I and Geary's C are shown numerically to be invariant to distance scaling.

## References

- Anselin, L. (1988). *Spatial Econometrics: Methods and Models*. Kluwer Academic.
- Anselin, L. (1995). Local indicators of spatial association: LISA. *Geographical Analysis, 27*(2), 93–115.
- Anselin, L. (2019). A local indicator of multivariate spatial association: Extending Geary's c. *Geographical Analysis, 51*(2), 133–150.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate. *Journal of the Royal Statistical Society B, 57*(1), 289–300.
- Bradley, J. V. (1978). Robustness? *British Journal of Mathematical and Statistical Psychology, 31*(2), 144–152.
- Cliff, A. D., & Ord, J. K. (1981). *Spatial Processes: Models and Applications*. Pion.
- Geary, R. C. (1954). The contiguity ratio and statistical mapping. *The Incorporated Statistician, 5*(3), 115–145.
- Moran, P. A. P. (1950). Notes on continuous stochastic phenomena. *Biometrika, 37*(1/2), 17–23.
- Ord, J. K., & Getis, A. (1995). Local spatial autocorrelation statistics. *Geographical Analysis, 27*(4), 286–306.

## Author

Febrianggi Caesar Immanuel, Statistics, Universitas Padjadjaran.
