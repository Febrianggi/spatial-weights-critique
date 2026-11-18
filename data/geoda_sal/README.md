columbus
========

Columbus neighborhood crime data 1980
-------------------------------------

Files in this folder:

* columbus.shp: polygon shapefile (n = 49).
* columbus.shx: shapefile index.
* columbus.dbf: attribute table (k = 20 variables).
* columbus.gal: Queen contiguity in GAL format (49 regions, 236 directed links).
* columbus.html: original SAL metadata page (variable definitions and source).

There is no `.prj` file: the coordinates are projected but in arbitrary map units, with no coordinate
reference system defined.

The analysis reads only `columbus.shp` (with its `.shx` and `.dbf`) and `columbus.gal`
(`analysis/core.Rmd`). The upstream GeoDa/SAL example set also distributes a `columbus.json`
(the same shapes and attributes in JSON). It is not included here, because the analysis does not use it.

Origin: the GeoDa/SAL Columbus example files, taken as data only from the `libpysal` package on PyPI.
Metadata identical to <https://geodacenter.github.io/data-and-lab/columbus/>.
`analysis/core.Rmd` checks that these files match `spData::columbus.shp` and Anselin's typed table
(`spData::columbus`): all 20 attributes and all vertices are identical.

Anselin, Luc (1988). Spatial Econometrics. Boston, Kluwer Academic, Table 12.1, p. 189.
