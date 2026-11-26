# Ketika Definisi Tetangga Mengubah Realitas Spasial

**Kritik terhadap Moran's I, Geary's C, dan LISA melalui uji sensitivitas matriks bobot, dengan data kejahatan Columbus (Ohio, 1980).**

[English](README.md)

## Mengapa proyek ini dibuat

Moran's I, Geary's C, dan LISA mudah disalahgunakan. Matriks bobot spasial sering dipilih setelah hasilnya terlihat, lalu versi yang paling signifikan atau paling rapi yang dilaporkan. Padahal kedua statistik ini adalah fungsi dari dua objek, yaitu data *dan* matriks bobot *W*. Bila *W* diganti, "realitas spasial" yang dilaporkan bisa ikut berubah, meskipun datanya sama persis.

Proyek ini mengukur seberapa jauh hasil bergeser bila yang diganti hanya definisi tetangga. Tujuannya sederhana: pemilihan metode dan matriks harus didasarkan pada alasan substantif dan disertai uji sensitivitas, bukan pada keluaran yang terlihat paling bagus.

## Temuan utama (CRIME)

| Temuan | Bukti |
|---|---|
| Peta klaster lokal bisa dipilih sesuka hati | Jumlah wilayah dengan LISA signifikan setelah FDR 5% berkisar **0 sampai 30** di antara 32 matriks (klaster Tinggi-Tinggi dan Rendah-Rendah ditambah pencilan Tinggi-Rendah dan Rendah-Tinggi; Tinggi-Tinggi saja **0 sampai 22**); acuan Queen · W memberi **4**, semuanya Tinggi-Tinggi |
| Besar efek sangat bergantung pada *W* | Moran's I berkisar **0,153 sampai 0,607** untuk data yang sama (Geary's C: 0,325 sampai 0,846) |
| Arahnya stabil | CRIME mengelompok secara signifikan pada ke-32 matriks; tidak ada matriks yang membalik tandanya |
| Sebagian matriks jauh lebih robust | Dalam simulasi dengan 5 pola spasial yang diketahui, **1/d · W** paling banyak kehilangan 12 poin persen daya dibanding matriks terbaik untuk setiap pola; **k = 2** dan pita jarak lebar kehilangan sampai 39 |
| Pada sinyal yang lebih lemah, signifikansi pun bisa dipilih | Dalam pipeline yang sama, kesimpulan signifikan/tidak signifikan untuk HOVAL, OPEN, dan Geary's C pada PLUMB bergantung pada *W* yang dipakai (`output/csv/05d_risiko_specification_searching.csv`) |

**Rekomendasi.** Bila tidak ada informasi awal tentang proses spasialnya, gunakan **1/d · W** (invers jarak yang distandardisasi baris) untuk Moran's I, dan laporkan matriks lain yang masuk akal sebagai uji sensitivitas. Queen · W tetap wajar bila interaksi diperkirakan terjadi lewat batas wilayah.

## Laporan

`reports/Columbus_Spatial_Analysis.html` adalah hasil knit dari Rmd. Berkas ini satu halaman mandiri (tidak butuh internet) yang hanya membahas **CRIME**, dalam bahasa Inggris dan Indonesia: ganti bahasa dengan tombol EN / ID di bagian atas, atau buka `Columbus_Spatial_Analysis.html?lang=id`. Isinya sebelas bab:

1. Mengapa laporan ini dibuat, dan hal yang tidak dibuktikan oleh hasil yang terlihat bagus
2. Data
3. 32 definisi tetangga, dengan peta graf ketetanggaan
4. Moran's I dan Geary's C global pada ke-32 matriks, dan apa yang bisa dipilih lewat *specification searching*
5. Moran versus Geary
6. Pengaruh satu lingkungan (jackknife, transformasi peringkat)
7. Klaster lokal (LISA, Gi*, Local Geary) pada beberapa matriks
8. Simulasi robustness dan jawaban atas revisi: matriks robust, sensitif, dan yang direkomendasikan
9. Yang sebaiknya dilakukan
10. Keterbatasan
11. Cara reproduksi, referensi, dan sesi R

## Cara membaca dashboard

Buka `dashboard_html/index.html` (atau jalankan server lokal dari folder utama repositori; lihat bagian **Cara menjalankan di lokal dan reproduksi** di bawah). Bahasa Inggris adalah bawaan; gunakan tombol **EN / ID** di header atau tambahkan `?lang=id` untuk bahasa Indonesia. Satu pemilih matriks bobot di bilah kontrol menyinkronkan seluruh tab analitis secara otomatis (disembunyikan pada tab **Metode**).

| Tab | Isi utama | Cara memakai |
|---|---|---|
| **Perbandingan LISA** | Peta klaster CRIME Columbus berdampingan antara acuan **Queen · W** dan matriks pilihan | Ganti matriks di bilah kontrol untuk melihat perubahan kelas klaster tiap wilayah secara langsung (arahkan kursor atau klik wilayah untuk membandingkan nilai LISA-nya). |
| **Peta lokal** | Indikator spasial lokal untuk matriks terpilih: LISA, Local Geary, dan Getis-Ord Gi* | Bandingkan wilayah mana yang tetap signifikan sebagai hotspot setelah koreksi FDR Benjamini-Hochberg 5% di tiap metode lokal. |
| **Hasil matriks** | Moran's I global, Geary's C, p-value 9.999 permutasi, skor-z, dan ukuran efek untuk matriks aktif | Lihat seberapa jauh besar autokorelasi spasial bergeser walau arah pengelompokannya tetap positif. |
| **Sensitivitas** | Kurva sensitivitas pada seluruh 32 matriks bobot | Amati rentang pergeseran Moran's I (`0,153` sampai `0,607`) dan Geary's C (`0,325` sampai `0,846`) saat definisi tetangga diubah. |
| **Simulasi** | Simulasi robustness pada 5 pola spasial yang diketahui (1,6 juta uji) | Bandingkan matriks yang robust vs sensitif (seperti **1/d · W** dibanding **k = 2** dan pita jarak lebar) serta daya uji per pola. |
| **Metode** | Uji komputasi diagonal vs letak serta ringkasan rancangan | Lihat bukti mengapa diagonal matriks wajib nol dan mengapa struktur tetangga (bukan urutan label) yang menentukan statistik. |
| **Tabel & unduhan** | Tabel perbandingan 32 matriks yang bisa diurutkan dengan matriks aktif disematkan di baris teratas | Urutkan kolom mana saja untuk membandingkan matriks, atau klik **Unduh tabel perbandingan (CSV)** untuk menyimpan tabel lengkapnya. |

## Struktur repositori

| Lokasi | Isi |
|---|---|
| `Columbus_Spatial_Analysis.Rmd` | Berkas yang di-knit. Menjalankan semua bagian di bawah dan menulis laporan CRIME dua bahasa |
| `analysis/core.Rmd` | Seluruh komputasi untuk 6 variabel × 32 matriks; menulis `output/` dan dashboard |
| `analysis/simulation.Rmd` | Simulasi robustness untuk CRIME; menulis `output/simulasi/` |
| `analysis/report_helpers.R` | Format angka, tabel dua bahasa, grafik, dan peta laporan (tanpa perhitungan statistik) |
| `report_assets/` | Template halaman, CSS, dan skrip laporan |
| `reports/Columbus_Spatial_Analysis.html` | Laporan hasil knit, mandiri, bahasa Inggris dan Indonesia |
| `dashboard_html/index.html` | Dashboard dua bahasa dengan semua hasil tersemat |
| `dashboard_html/template.html` | Template dashboard; Rmd mengisinya menjadi `index.html` |
| `data/geoda_sal/` | Data Columbus (distribusi GeoDa/SAL): shapefile, `columbus.gal`, metadata |
| `output/csv/` | 42 tabel hasil (validasi data, uji global, sensitivitas, LISA, jackknife, …) |
| `output/simulasi/` | Hasil simulasi: kriteria per matriks, daya, kalibrasi, uji komputasi, grafik |
| `output/png/`, `output/json/`, `output/rds/` | Grafik, JSON untuk dashboard, objek R (hasil dan 32 objek `listw`) |
| `analysis/style.R` | Palet arsip dan tema ggplot bersama: satu warna per kelas di semua grafik, peta, dan dashboard |
| `assets/fonts/` | Inter dan Source Serif 4 (SIL Open Font License, disertakan) |
| `assets/cover/` | Ilustrasi sampul (rumah dan sedan) untuk halaman depan dan laporan |
| `tests/` | Validasi keluaran, cek reprodusibilitas, uji dashboard di browser |
| `docs/CHANGELOG.id.md` | Catatan perubahan |

## Ringkasan metode

- **Data:** 49 lingkungan Columbus, 1980 (Anselin, 1988). Laporan, dashboard, dan simulasi berfokus pada **CRIME** (pencurian rumah dan kendaraan per 1.000 rumah tangga). Komputasinya juga mencakup HOVAL, INC, OPEN, PLUMB, dan DISCBD; hasilnya ada di `output/csv/`.
- **32 matriks bobot:** kontiguitas Queen dan Rook; k tetangga terdekat (k = 2, 3, 4, 5, 6, 8); enam pita jarak; invers jarak 1/d dan 1/d². Masing-masing dalam bentuk biner atau mentah dan bentuk standardisasi baris.
- **Uji global:** Moran's I dan Geary's C dengan 9.999 permutasi, p-value dua sisi dengan selang kepercayaan Monte Carlo, skor-z berorientasi, dan ukuran efek.
- **Uji lokal:** LISA dengan permutasi bersyarat tanpa pengembalian (Anselin, 1995) dan koreksi FDR Benjamini–Hochberg; Local Geary dan Getis–Ord Gi* sebagai pendukung.
- **Simulasi robustness:** nilai CRIME yang asli disusun ulang di peta mengikuti lima proses yang diketahui (SAR dengan Queen, k = 4, dan pita jarak; proses geostatistik; tren radial). Kekuatan pola dikalibrasi agar matriks terbaik mencapai daya yang sama untuk setiap proses. 25.000 kumpulan data × 32 matriks × 2 indeks = 1,6 juta uji. Kriteria (ukuran uji, daya rata-rata, penyesalan maksimum, daya terburuk, kesepakatan Moran–Geary) dan batas kelas ditetapkan sebelum simulasi dijalankan.
- **Diagonal vs letak:** uji komputasi menunjukkan hasil bergantung pada wilayah *mana* yang bertetangga, bukan pada label wilayah; diagonal wajib nol (diagonal yang tidak nol menggelembungkan Moran's I).

## Cara menjalankan di lokal dan reproduksi

### 1. Membuka situs, dashboard, dan laporan di lokal

Jalankan server HTTP lokal dari folder utama repositori agar tautan antara halaman pembuka, dashboard, dan laporan berjalan penuh:

```bash
python -m http.server 8000
```

Lalu buka:
- http://localhost:8000 (halaman pembuka)
- http://localhost:8000/dashboard_html/?lang=id (dashboard interaktif bahasa Indonesia; hapus `?lang=id` untuk bahasa Inggris)
- http://localhost:8000/reports/Columbus_Spatial_Analysis.html?lang=id (laporan HTML dua bahasa)

Hentikan server dengan `Ctrl+C`. Baik `dashboard_html/index.html` maupun `reports/Columbus_Spatial_Analysis.html` juga bersifat mandiri dan bisa dibuka offline langsung dari disk.

### 2. Menjalankan ulang analisis R dari awal

Kebutuhan: R ≥ 4.3 dengan `sf`, `spdep` (≥ 1.3), `spData`, `dplyr`, `tidyr`, `ggplot2`, `patchwork`, `jsonlite`, `knitr`, `rmarkdown`, `scales`, serta Pandoc (sudah termasuk di RStudio).

```r
install.packages(c("sf", "spdep", "spData", "dplyr", "tidyr", "ggplot2", "patchwork",
                   "jsonlite", "knitr", "rmarkdown", "scales"))
rmarkdown::render("Columbus_Spatial_Analysis.Rmd", output_dir = "reports")
```

Jalankan dari folder utama repositori, atau tekan **Knit** di RStudio (Rmd mengirim HTML-nya ke `reports/`). Prosesnya sekitar 10 sampai 15 menit dan menulis ulang `output/`, `reports/`, dan `dashboard_html/index.html`. Seed ditetapkan (`20261112` untuk analisis utama, `20261117` untuk simulasi), sehingga hasilnya identik setiap kali dijalankan.

## Pengujian

```bash
Rscript tests/validate_outputs.R                       # pemeriksaan tabel, JSON, RDS, grafik, dan laporan
Rscript tests/check_reproducibility.R <run_a> <run_b>  # dua knit independen harus identik byte per byte
python tests/test_html_dashboard.py . <screenshot_dir> # dashboard vs CSV, dua bahasa, keyboard, mobile (Playwright)
python tests/check_site.py                             # memeriksa tautan halaman pembuka, dashboard, dan laporan
```

Atur `CHROME_PATH` untuk memakai Chrome tertentu pada uji browser.

## Sumber data

Berkas Columbus berasal dari distribusi GeoDa/SAL (metadata identik dengan <https://geodacenter.github.io/data-and-lab/columbus/>; Anselin, 1988, Tabel 12.1). Analisis membuktikan berkas ini sama dengan `spData::columbus.shp` dan tabel ketik-ulang Anselin (`spData::columbus`): ke-20 atribut dan ke-1.196 verteks identik, dan kontiguitas Queen dari geometri sama dengan `columbus.gal` milik GeoDa (236 link). Koordinat tidak memiliki CRS, sehingga jarak memakai satuan peta; Moran's I dan Geary's C terbukti secara numerik invarian terhadap skala jarak.

## Referensi

- Anselin, L. (1988). *Spatial Econometrics: Methods and Models*. Kluwer Academic.
- Anselin, L. (1995). Local indicators of spatial association: LISA. *Geographical Analysis, 27*(2), 93–115.
- Anselin, L. (2019). A local indicator of multivariate spatial association: Extending Geary's c. *Geographical Analysis, 51*(2), 133–150.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate. *Journal of the Royal Statistical Society B, 57*(1), 289–300.
- Bradley, J. V. (1978). Robustness? *British Journal of Mathematical and Statistical Psychology, 31*(2), 144–152.
- Cliff, A. D., & Ord, J. K. (1981). *Spatial Processes: Models and Applications*. Pion.
- Geary, R. C. (1954). The contiguity ratio and statistical mapping. *The Incorporated Statistician, 5*(3), 115–145.
- Moran, P. A. P. (1950). Notes on continuous stochastic phenomena. *Biometrika, 37*(1/2), 17–23.
- Ord, J. K., & Getis, A. (1995). Local spatial autocorrelation statistics. *Geographical Analysis, 27*(4), 286–306.

## Penulis

- Febrianggi Caesar Immanuel, Statistika, Universitas Padjadjaran.
- Rayyan Ilyas Fadani
- Gregorius Adiyatma Pradana
- Bijan Ramadhan Aditri
