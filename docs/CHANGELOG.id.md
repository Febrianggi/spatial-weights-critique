# Ringkasan perubahan versi 2 dan hasil pengujian

## 1. Audit metodologi

| Temuan | Tindakan | Dampak |
|---|---|---|
| `localmoran_perm`, `localC_perm`, dan `localG_perm` (spdep 1.3) secara default mengambil sampel tetangga **dengan pengembalian** (`no_repeat_in_row = FALSE`), bukan permutasi bersyarat Anselin (1995) | Semua uji lokal kini memakai `no_repeat_in_row = TRUE`, dan permutasi bersyarat ditulis ulang tanpa spdep sebagai verifikasi | Pada Queen·W: CRIME ber-FDR 0 → 4, PLUMB 1 → 8, DISCBD 4 → 9. Total CRIME pada 32 W: 174 → 416 |
| Temuan v1 "CRIME signifikan global tanpa klaster LISA setelah FDR" | Dikoreksi di Bagian 9.5 | Temuan itu artefak dari default spdep. Pembahasan kini menjelaskan hubungan global–lokal yang sebenarnya, termasuk lompatan keputusan BH (KNN k=4: 0, k=5: 18 wilayah) |
| I dan C belum diverifikasi secara independen | Dihitung ulang dengan aljabar matriks untuk 192 kasus | Selisih maksimum 1.11e-16 (I) dan 4.44e-16 (C) |
| Uji permutasi global belum diverifikasi | Ditulis ulang tanpa spdep (Queen·W, 6 variabel) | Selisih p maksimum 2.6 kali √2·SE Monte Carlo |
| Ketidakpastian Monte Carlo pada p-value tidak dilaporkan | Ditambahkan SE dan IK 95% untuk setiap p, plus penanda kasus di batas α | 14 dari 384 uji di batas α |
| Selisih z tidak punya batas noise | Batas noise empiris dari pasangan KNN B/W (I dan C identik, z berbeda hanya karena permutasi) | Batas = 0.11 |
| Risiko *specification searching* tidak dibahas | Tabel rentang p antar-W (Bagian 5.3) | HOVAL, OPEN, dan Geary-PLUMB kesimpulannya bisa "dipilih" |
| Rasio audit permutasi memakai SE tunggal | Diganti √2·SE (dua estimasi Monte Carlo) | Rasio maksimum 2,6 (global) dan 2,4 (lokal) |

## 2. Analisis sensitivitas

* **Dihapus:** uji binomial atas 42 perbandingan kriteria (tidak independen) dan semua ukuran relatif terhadap |z| (meledak saat z ≈ 0, misalnya OPEN).
* **Dipisah menjadi tiga jenis:**
  * **numerik:** ukuran efek ES = I − E(I) dan 1 − C, deterministik;
  * **inferensial:** z, kesimpulan, perubahan terhadap acuan, kasus di batas α;
  * **lokal:** jumlah wilayah ber-FDR, % kelas sama, kappa, Jaccard.
* **Semua ukuran absolut.** Kemiringan terhadap k dan d dalam satuan aslinya.
* **Perbandingan Moran vs Geary kini deskriptif.** Per dimensi dan dua skala, dengan ambang setara yang dinyatakan eksplisit, tanpa p-value.
* **Efek standardisasi dijelaskan secara mekanis.** Efeknya nol pada KNN dan berkorelasi dengan CV jumlah bobot per baris (Spearman ρ ≈ 0,96).
* **Jackknife dan uji peringkat** kini melaporkan ΔES dan Δz absolut, serta jumlah W yang signifikan sebelum dan sesudah transformasi peringkat.

## 3. Validasi dataset dan bobot

* **Sumber utama** kini berkas GeoDa/SAL (`data/geoda_sal/`, dari `libpysal` di PyPI, diambil sebagai data saja). Kesetaraannya dengan spData terbukti: selisih 20 atribut = 0, dan 1.196 verteks identik. Tabel ketik-ulang Anselin juga identik.
* **Queen dari geometri identik dengan `columbus.gal` GeoDa.** Matriks asli Anselin (`col.gal.nb`) berbeda pada 3 pasangan (POLYID 5–16, 25–30, 31–39). Dampaknya pada I dan C dilaporkan.
* **Tabel justifikasi dan risiko** untuk tiap keluarga bobot (Queen/Rook/KNN/pita jarak/IDW, B vs W).
* **Satuan jarak:** invariansi terhadap skala terbukti numerik (~1e-15). Pilihan titik pusat (centroid geometri vs titik X/Y Anselin) terbukti tidak netral untuk KNN (88–94% tetangga sama).

## 4. Pembahasan

Ditulis ulang. Ada analisis berlapis untuk PLUMB (data, mekanisme rumus, uji kontrafaktual peringkat) dan HOVAL (Monte Carlo, jackknife, peringkat), koreksi terbuka atas temuan CRIME dari v1, serta implikasi metodologis baru (periksa default perangkat lunak, laporkan ketidakpastian Monte Carlo).

## 5. Dashboard

* **Fitur v1 dipertahankan:** filter, peta, kurva, heatmap, tabel, dan ekspor.
* **Kartu hasil** kini menampilkan ukuran efek, IK 95% Monte Carlo p, dan penanda batas α.
* **Ringkasan sensitivitas** diganti empat tabel: numerik, inferensial, outlier/standardisasi, dan perbandingan per dimensi.
* **Perbaikan Shiny:** pembuatan tabel ringkasan (bug yang ditemukan uji).

## 6. Hasil pengujian (semua dijalankan pada keluaran final)

| Uji | Hasil |
|---|---|
| Knit Rmd dari folder keluaran kosong | Berhasil, 42 CSV, 20 PNG, RDS, JSON, laporan HTML |
| Reproduksibilitas: knit kedua yang independen, dibandingkan dengan yang pertama | CSV identik byte per byte: 42 dari 42; JSON identik (di luar stempel waktu): TRUE; PNG identik byte per byte: 20 dari 20 |
| `tests/validate_outputs.R` | Validasi keluaran: 100 lolos, 0 gagal |
| Dashboard HTML (Playwright + Chrome) | OK: 201 pemeriksaan kartu cocok dengan CSV, konsol bersih, mobile tanpa overflow, target sentuh >= 44px |
| Shiny `testServer` | OK testServer: 192 konfigurasi cocok dengan CSV; ekspor CSV/JSON/PNG berfungsi |
| Shiny di browser | OK Shiny browser: kontrol, klik baris tabel, reset, lapisan peta; konsol bersih; overflow mobile = 0 |
| Audit LISA: mean(Iᵢ) = I global | 1.11e-16 |
| Audit LISA: permutasi bersyarat sendiri vs spdep | maks 2.37 kali √2·SE; klasifikasi sama 98 dari 98 |

Log lengkap ada di `tests/logs/`.

## Revisi dosen (17 November 2026): simulasi robustness matriks bobot untuk CRIME

Bab baru **10** di laporan, kode di `sim_crime_child.Rmd` (dipanggil Rmd utama sebagai *child*), hasil di `output/simulasi/`. Seluruh 42 CSV lama tetap identik byte per byte setelah render ulang.

**Diagonal atau letak (uji komputasi, `S01`).**

* Label wilayah tidak berpengaruh: x dan W diurutkan ulang bersamaan, selisih maksimum 2,2e-16.
* Letak menentukan hasil: tetangga Queen diacak (jumlah tetangga tetap), Moran's I CRIME turun dari 0,515 ke rata-rata −0,025, setara E(I).
* Diagonal harus nol: w_ii = 1 menaikkan Moran's I dari 0,515 ke 0,599. Pembilang Geary tidak berubah, nilainya hanya berubah lewat S0 (0,592 → 0,490).
* Simetrisasi (W + W')/2 dan skala c·W tidak mengubah hasil.

**Desain simulasi.**

* Nilai CRIME asli disusun ulang menurut 5 pola yang diketahui: SAR Queen, SAR k = 4, SAR pita 1,10, geostatistik eksponensial, dan tren radial.
* Kekuatan pola dikalibrasi agar daya matriks terbaik mencapai 0,30, 0,50, 0,70, dan 0,90.
* Jumlah ulangan: 5.000 untuk skenario nol dan 1.000 per skenario. Total 1,6 juta uji.
* Kriteria K1–K5 dan batas klasifikasi (0,15 dan 0,30) ditetapkan sebelum simulasi.
* Versi awal memakai SAR 1/d · W dan ρ yang sama untuk semua pembangkit. Pembangkit itu hampir tak terdeteksi, sehingga diganti. Batas klasifikasi tidak diubah.

**Uji komputasi simulasi (`S03`, `S04`).**

* Sebaran data simulasi sama persis dengan CRIME.
* Rata-rata I naik monoton terhadap kekuatan pola.
* Hasil identik bila dijalankan ulang dengan seed yang sama.
* Keputusan uji analitik sama dengan uji permutasi 999 kali pada 98% kasus (median).
* Ukuran uji ke-32 matriks berada di 0,044–0,056.

**Hasil (Moran's I).**

* Robust: 1/d · W dan 1/d · mentah.
* Sensitif: k = 2 (B/W), d ≤ 1,35 · B, d ≤ 1,65 (B/W), dan 1/d² · mentah.
* 24 matriks lainnya menengah, termasuk Queen · W (penyesalan maksimum 0,228).
* Rekomendasi bila tidak ada informasi: **1/d · W** (penyesalan maksimum 0,122).
* Untuk Geary's C: k = 6. Untuk kedua indeks sekaligus, tiga teratas hampir setara: 1/d · W, d ≤ 0,90 · W, dan k = 6 · B.

**Pengujian ulang.** `tests/validate_outputs.R`: 100 lolos, 0 gagal. Hasil simulasi dari render utama identik dengan render bab secara terpisah.

## Dashboard revisi (17 November 2026, malam)

* **Kedua dashboard kini punya dua tampilan:** *Analisis utama* (semua fitur sebelumnya, tidak ada yang dihapus) dan *Revisi: simulasi CRIME*.
* **Isi tampilan revisi:**
  * rekomendasi matriks bila tidak ada informasi (1/d · W) beserta ukuran uji, daya, dan penyesalannya;
  * pilihan terbaik untuk Geary dan untuk kedua indeks;
  * posisi Queen · W;
  * histogram uji "letak" dan daftar uji komputasi U1–U7;
  * papan klasifikasi robust/menengah/sensitif untuk Moran dan Geary;
  * grafik penyesalan maksimum dengan batas 0,15 dan 0,30;
  * rincian kriteria per matriks;
  * heatmap daya 32 matriks × 5 pola per tingkat kekuatan;
  * kurva daya matriks terpilih dibanding matriks terbaik;
  * tabel desain, kriteria, kalibrasi, pemeriksaan mesin simulasi, dan kepekaan aturan.
* **Sumber data dashboard:** bab revisi kini mengekspor `output/rds/simulasi_crime.rds` dan `output/simulasi/simulasi_crime.json`, lalu menyematkan JSON itu ke `dashboard_html/index.html`. Dashboard tidak menghitung ulang apa pun.
* **Gaya visual baru untuk keduanya:**
  * font Inter (SIL OFL) dengan angka tabular;
  * latar abu-abu terang dan panel putih dengan radius bertingkat;
  * satu aksen biru untuk pilihan dan fokus;
  * tab tampilan dengan pola ARIA (panah kiri/kanan);
  * heatmap daya dengan kontras teks minimal 4,78:1;
  * target sentuh minimal 44 px.
* **Pengujian:**
  * `tests/test_html_dashboard.py` kini juga memeriksa tampilan revisi: 64 nilai penyesalan dan 320 sel daya dicocokkan dengan CSV simulasi, klasifikasi, keyboard, dan layar 390 px;
  * `tests/test_shiny_browser.py` memeriksa tab revisi;
  * `tests/test_shiny.R` tetap lolos (192 konfigurasi).

## Dashboard satu halaman khusus CRIME (17 November 2026, malam)

* **Satu halaman, tanpa tab.** Analisis data asli dan simulasi kini satu alur:
  1. matriks yang disarankan;
  2. hasil matriks terpilih;
  3. peta CRIME dan klaster lokal;
  4. sensitivitas pada data asli;
  5. matriks robust dan sensitif;
  6. daya menurut pola;
  7. diagonal atau letak;
  8. tabel 32 matriks;
  9. ringkasan;
  10. desain simulasi.
* **Khusus CRIME.** Pilihan variabel dan heatmap kesepakatan 6 variabel dihapus. Laporan Rmd dan semua CSV tidak berubah.
* **Satu pilihan matriks untuk semuanya.** Toolbar mengendalikan kartu hasil, peta, sorotan di grafik simulasi, dan rincian kriteria. Klik matriks di bagian simulasi atau di tabel juga mengubah toolbar. Tombol baru di toolbar menampilkan matriks yang disarankan (1/d · W).
* **Data asli dan simulasi saling melengkapi.** Kartu hasil menampilkan kelas robustness dan penyesalan matriks terpilih. Tabel 32 matriks punya kolom kelas simulasi dan penyesalan.
* **Tema gelap ala ruang kendali.**
  * satu aksen kuning garis polisi untuk pilihan dan fokus;
  * pita "POLICE LINE · DILARANG MELINTAS";
  * header berupa barisan foto tahanan dengan bagan tinggi badan, papan nama berisi POLYID dan nilai CRIME dari 4 hot spot LISA (Queen · W, FDR 5%);
  * garis kapur TKP;
  * siluet detektif, garis kapur, dan kaca pembesar yang tersebar acak di latar setiap kali halaman dibuka.
  Semua siluet digambar sendiri dalam SVG; gambar contoh bertanda air stok tidak dipakai. Kontras teks minimal 4,72:1 (WCAG AA).
* **Pengujian:**
  * `tests/test_html_dashboard.py`: 426 pemeriksaan angka cocok dengan CSV, termasuk barisan hot spot dan sinkronisasi pilihan;
  * `tests/test_shiny.R`: 32 konfigurasi CRIME, termasuk panel dan kolom simulasi;
  * `tests/test_shiny_browser.py`: lolos;
  * `tests/validate_outputs.R`: 102 lolos.

## Versi 3: repositori untuk GitHub

- Shiny dihapus. Hasil yang dipakai adalah HTML hasil knit Rmd dan dashboard HTML.
- `Columbus_Spatial_Analysis.Rmd` kini menjadi laporan dua bahasa (Inggris bawaan, tombol EN/ID, `?lang=id`) yang hanya menampilkan CRIME, dengan tema gelap yang sama dengan dashboard. Sekali knit langsung menulis `reports/Columbus_Spatial_Analysis.html`.
- Komputasi dipindah ke `analysis/core.Rmd` (6 variabel × 32 W) dan `analysis/simulation.Rmd` (simulasi CRIME), dipanggil sebagai child dengan `include = FALSE`. Ke-42 CSV identik byte per byte dengan versi sebelumnya.
- Perbaikan: pemeriksaan "rata-rata I naik monoton" pada simulasi sebelumnya membaca kolom yang salah (selalu bernilai benar); kini membaca kolom `Monoton naik`. Hasilnya tetap lolos.
- README Inggris (utama) dan Indonesia; uji `validate_outputs.R` disesuaikan (106 lolos), uji dashboard 426 pemeriksaan lolos.

## Versi 3.1: siap GitHub Pages

- Halaman depan `index.html`, workflow `.github/workflows/pages.yml` (uji dashboard dan uji tautan dulu, lalu deploy), dan `tests/check_site.py` (merakit `_site/` serta memeriksa semua tautan dan aset dengan situs disajikan di bawah subpath repositori).
- Navigasi antarhalaman: dashboard kini punya tautan ke laporan, dan tautan laporan ke dashboard serta tautan dari halaman depan membawa bahasa yang sedang aktif (`?lang=`). Semua tautan relatif.
- Favicon inline di ketiga halaman; path panjang dalam teks laporan kini bisa terlipat di layar ponsel.
- `renv.lock` (R 4.3.3, 75 paket), `requirements-test.txt` (Playwright 1.63.0), `docs/DEPLOYMENT.md`.
- `data/geoda_sal/README.md` disesuaikan dengan berkas yang benar-benar ada (`columbus.json` tidak disertakan dan tidak dipakai).
- Hasil komputasi tidak berubah: ke-42 CSV, 20 PNG, dan berkas simulasi identik byte per byte dengan knit sebelumnya.

## Versi 3.2: tampilan A+C (21 November 2026)

Pilihan Febri: **A** (ilustrasi rumah dan sedan) untuk halaman depan dan sampul laporan, **C** (gaya arsip statistik) untuk isi laporan, dashboard, peta, dan grafik. Tema gelap bernuansa TKP dari versi sebelumnya dihapus.

- **Dihapus dari sumber dan halaman terbitan:** pita "POLICE LINE", barisan foto tahanan, garis kapur, penanda barang bukti, dan siluet acak di latar (`report_assets/report.js`). Label "Exhibit/Bukti" menjadi "Figure/Gambar", "Berkas perkara" menjadi "Daftar isi".
- **Sampul (A):** `assets/cover/` berisi ilustrasi dalam dua ukuran WebP. Halaman depan memakai `srcset`, laporan menyematkan versi 800 px. Judul, satuan, dan sumber tetap teks dua bahasa.
- **Gaya arsip (C):** kertas terang, garis register biru, margin marun, judul serif (Source Serif 4, SIL OFL, `assets/fonts/`), angka tabular. Bidang data berlatar polos tanpa kisi. Temuan utama laporan ditulis sebagai register bernomor.
- **Satu palet untuk semua keluaran:** `analysis/style.R` dipakai `core.Rmd`, `simulation.Rmd`, dan `report_helpers.R`; dashboard memakai nilai yang sama. HH/LL jenuh, HL/LH muda, tidak signifikan abu-abu hangat; Gi* dan Local Geary memakai warna HH/LL untuk arti yang sama. Local Geary kini membedakan "Other Positive" (kuning tua) dari "Negative" (ungu). Peta signifikansi: p FDR terkecil paling gelap (urutan warna sebelumnya terbalik di dashboard). Nilai variabel memakai ramp biru tinta lima kelas dengan satuan di legenda; satuan OPEN dan DISCBD ditulis "tidak dicatat sumber" karena dokumentasi data tidak menyebutnya.
- **Pembeda selain warna:** Moran = lingkaran, Geary = segitiga, kosong = tidak signifikan, di PNG, figur laporan, dan grafik dashboard. Kurva daya memakai warna, bentuk, dan jenis garis. Teks di atas heatmap memilih tinta atau putih menurut kontras WCAG.
- **Peta baru:** laporan bab 7 punya Gambar "Seberapa kuat, dan seberapa stabil" (peta signifikansi p FDR pada Queen · W dan peta stabilitas: signifikan pada berapa dari 32 matriks). Dashboard punya lapisan "Stabilitas LISA di 32 matriks".
- **Penutup laporan:** bab 9 diakhiri dengan arti hasil bagi pencurian rumah dan kendaraan gabungan per 1.000 rumah tangga, dari angka hasil knit. Tiga hitungan dipisahkan: wilayah dengan LISA signifikan setelah FDR 5%, klaster (wilayah Tinggi-Tinggi atau Rendah-Rendah; kelompok klaster = wilayah berkelas sama yang tersambung lewat ketetanggaan Queen), dan pencilan spasial (Tinggi-Rendah, Rendah-Tinggi), yang bukan anggota klaster. Tidak satu pun menyatakan jumlah kejadian. Contoh: pada 1/d · W ada 21 wilayah signifikan, yaitu 18 Tinggi-Tinggi dalam satu kelompok dan 3 pencilan Rendah-Tinggi (POLYID 7, 9, 22).
- **Rentang 0–30 dibaca dengan benar:** di halaman depan, kedua README, ringkasan dashboard, dan register laporan, angka itu disebut "wilayah dengan LISA signifikan setelah FDR 5%" (klaster dan pencilan digabung), bukan "wilayah dalam klaster". Tinggi-Tinggi saja berkisar 0–22. Dashboard menampilkan rincian klaster/pencilan untuk kedua peta perbandingan, dan judul peta kelas LISA kini "klaster dan pencilan".
- Perbandingan LISA, sorotan POLYID di kedua peta, dan transisi warna 260 ms dengan dukungan *reduced motion* dari desain atlas dipertahankan.
- Hasil komputasi tidak berubah: ke-42 CSV dan JSON hasil identik byte per byte dengan knit sebelumnya (`tests/check_reproducibility.R`, di luar stempel waktu); berkas simulasi juga identik. Yang berubah hanya 20 PNG di `output/png/` dan 3 PNG simulasi, karena tampilannya. `tests/validate_outputs.R` 106 lolos, `tests/test_html_dashboard.py` 426 pemeriksaan lolos, `tests/check_site.py` 0 masalah (26 tautan dan aset, 20 langkah navigasi).

## 21 November 2026 · Navigasi dashboard dan peta lokal

- Dashboard dibagi menjadi tujuh tab. Perbandingan LISA membuka dashboard, dan tombol analisis membawa matriks pembanding ke tab Hasil matriks. Tautan langsung, tombol Kembali, dan pergantian EN/ID mengenali tab aktif.
- Peta tingkat pencurian dan keenam lapisan analisis lokal memakai bingkai, skala tampilan, serta tipografi peta perbandingan. Legenda tetap mengikuti satuan atau kelas masing-masing lapisan.
- Nama Spatial Weights Critique di kiri atas membawa pembaca ke beranda dalam bahasa aktif. Pilihan bahasa disingkat EN dan ID.
- Tombol beranda menjadi “Buka Dashboard” dan “Open Dashboard”. Keterangan di bawah ilustrasi sampul dihapus pada kedua bahasa.

## 21 November 2026 · Kontrol dan transisi peta

- Pada tab Peta lokal, pemilih keluarga bobot, parameter, dan skema bobot tetap terjangkau saat menggulir. Di ponsel, tombol matriks membuka kontrol di atas peta tanpa menggeser wilayah yang sedang dibaca.
- Warna wilayah bertransisi selama 460 ms ketika kelas berubah pada peta lokal dan perbandingan LISA. Batas wilayah tetap di tempat. Garis ketetanggaan yang ditampilkan muncul selama 320 ms. Pengaturan kurangi gerakan menampilkan pembaruan langsung.
- Keterangan “Illustration…” dan “Ilustrasi…” di bawah gambar sampul laporan dihapus dari sumber Rmd dan HTML terbitan.
- Nama proyek di kiri atas laporan membuka beranda situs dalam bahasa aktif, termasuk ketika pembaca datang dari tengah bab.

## 21 November 2026 · Satu pemilih matriks dan pengurutan tabel

- Kontrol keluarga bobot, parameter, dan skema mengikuti guliran di ketujuh tab. Pilihan aktif mengatur semua tampilan, termasuk peta pembanding LISA. Acuan Queen · W tetap menjadi peta pembanding tetap di kiri.
- Simulasi merangkum jumlah matriks per kelas. Grafik dan tabel daya menyorot matriks yang dipilih lewat kontrol bobot.
- Klik judul kolom di Tabel & unduhan untuk mengurutkan naik atau turun. Matriks terpilih menempati baris pertama. Saat pilihan berpindah, matriks sebelumnya kembali mengikuti urutan kolom. CSV selalu memakai urutan bawaan 32 matriks dan menyimpan nilai presisi penuh, termasuk ketika tabel sedang diurutkan dan baris terpilih berada di atas.

## 21 November 2026 · Sorotan pilihan dan pergerakan baris

- Penanda tab, kontrol bobot, dan pilihan simulasi bergerak ke posisi baru. Grafik sensitivitas, wilayah pilihan LISA, hasil matriks, serta peta daya menandai perubahan yang relevan.
- Saat pilihan matriks berganti, baris terpilih bergerak ke atas dan baris sebelumnya kembali ke urutan kolom. CSV tetap mengikuti urutan sumber. Preferensi kurangi gerakan menampilkan hasil akhir langsung.
- Tab Metode berisi penjelasan tetap sehingga pemilih bobot disembunyikan di sana. Pilihan tetap tersimpan ketika kembali ke tab analisis.
