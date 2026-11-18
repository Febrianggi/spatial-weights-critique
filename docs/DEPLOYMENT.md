# Publishing, dependencies and tests

## Website (GitHub Pages)

The website is the landing page `index.html`, the knitted report `reports/Columbus_Spatial_Analysis.html`
and the dashboard `dashboard_html/index.html`. Both pages are self-contained (figures, data and fonts are
embedded), and every link between them is relative, so the same files work when opened from a local folder
and when served from `https://<user>.github.io/<repository>/`.

One-time setup: in the repository, open **Settings > Pages > Build and deployment** and set **Source** to
**GitHub Actions**. After that, every push to `main` (or `master`) runs `.github/workflows/pages.yml`, which:

1. installs the Python test dependencies and Chromium;
2. runs `tests/test_html_dashboard.py` (dashboard numbers against the CSV results, both languages, mobile);
3. runs `tests/check_site.py`, which assembles `_site/` and checks every link and asset with the site served
   under `/<repository>/`, exactly as GitHub Pages serves a project site;
4. deploys `_site/`.

The workflow does not run R. Knit `Columbus_Spatial_Analysis.Rmd` locally and commit `reports/`,
`dashboard_html/index.html` and `output/` before pushing.

## R packages (renv)

`renv.lock` records the R version (4.3.3) and the exact versions of the 75 packages (the 12 used directly
and their dependencies) that produced the committed results. To install those versions into a
project library:

```r
install.packages("renv")
renv::restore()
```

`renv::restore()` asks before it changes anything. The project does not activate renv automatically, so
knitting with your usual library keeps working; run `renv::restore()` when you want the locked versions.
On a newer R, or on Windows without matching binaries, some packages (for example `sf`, `s2`, `units`) are
built from source and need Rtools (Windows) or GDAL, GEOS, PROJ and UDUNITS (Linux, macOS).

## Tests

```bash
Rscript tests/validate_outputs.R                       # tables, JSON, RDS, figures and report
Rscript tests/check_reproducibility.R <run_a> <run_b>  # two independent knits must match byte for byte
python -m pip install -r requirements-test.txt
python -m playwright install chromium
python tests/test_html_dashboard.py . tests/screenshots # dashboard against the CSV results
python tests/check_site.py                             # website links and assets under a repository subpath
```

Set `CHROME_PATH` to use a specific Chrome binary for the browser tests, and `SITE_SUBPATH` to test a
repository name other than `spatial-weights-critique`.
