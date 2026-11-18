"""Uji dashboard HTML (satu halaman, khusus CRIME): konsol bersih, kontrol berfungsi, mobile tanpa overflow,
dan angka yang tampil sama dengan CSV hasil Rmd. Jalankan: python3 -I test_html_dashboard.py <proyek> <folder_screenshot>"""
import csv, os, sys, pathlib
from playwright.sync_api import sync_playwright

proj, shots = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
shots.mkdir(parents=True, exist_ok=True)
base = (proj / "dashboard_html/index.html").resolve().as_uri()
url = base + "?lang=id"          # angka diperiksa dengan format Indonesia; versi Inggris diperiksa terpisah di bawah
V = "CRIME"
glob = list(csv.DictReader(open(proj / "output/csv/05_global_moran_geary_semua_spesifikasi.csv", encoding="utf-8")))
G = {(r["var"], r["spec_id"], r["index"]): r for r in glob}
crit = list(csv.DictReader(open(proj / "output/simulasi/S06_kriteria_per_matriks.csv", encoding="utf-8")))
powr = list(csv.DictReader(open(proj / "output/simulasi/S02_hasil_simulasi_lengkap.csv", encoding="utf-8")))
lisa = list(csv.DictReader(open(proj / "output/csv/19_lisa_semua_spesifikasi.csv", encoding="utf-8")))
fmt = lambda x, d: ("−" if x < 0 else "") + f"{abs(x):.{d}f}".replace(".", ",")
fp = lambda p: "< 0,001" if p < 0.001 else fmt(p, 4)
labs = {r["W"]: r["Spesifikasi"] for r in crit}
C = {r["W"]: r for r in crit}

def check_cards(page, spec):
    cards = page.locator(".idx")
    for i, ix in enumerate(["Moran's I", "Geary's C"]):
        r = G[(V, spec, ix)]
        big = cards.nth(i).locator(".big").inner_text()
        assert big == fmt(float(r["stat"]), 4), (spec, ix, big, r["stat"])
        dd = cards.nth(i).locator("dd").all_inner_texts()
        assert dd[2] == fmt(float(r["z_perm"]), 3) and dd[3] == fp(float(r["p_two"])), (spec, ix, dd)
        assert dd[6] == fmt(float(r["es"]), 4), (spec, ix, "ES", dd[6], r["es"])
    # panel simulasi di kartu hasil dan rincian mengikuti matriks yang sama
    sim = page.locator(".side .wstats").first.inner_text()
    assert fmt(float(C[spec]["K3 penyesalan maks Moran"]), 3) in sim, (spec, sim)
    assert labs[spec] in page.inner_text("#detail h3"), (spec, page.inner_text("#detail h3"))
    assert page.locator(".chip[aria-pressed='true']").inner_text().strip() == labs[spec]

errors = []
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"], **({"executable_path": os.environ["CHROME_PATH"]} if os.environ.get("CHROME_PATH") else {}))
    page = b.new_page(viewport={"width": 1400, "height": 900})
    page.on("console", lambda m: m.type == "error" and errors.append(m.text))
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(url); page.wait_for_selector(".idx")
    n = 0
    # satu halaman, tanpa tab dan tanpa pilihan variabel
    assert page.locator("[role=tab]").count() == 0 and page.locator("#selVar").count() == 0
    assert page.locator("#bgfx svg").count() >= 6, "siluet latar"
    hot = sorted(int(r["POLYID"]) for r in lisa if r["var"] == V and r["spec_id"] == "queen_W" and r["class_fdr"] == "HH")
    got = page.evaluate("[...document.querySelectorAll('#lineup text')].map(t => t.textContent).filter(t => t.startsWith('POLYID'))")
    assert got == [f"POLYID {h}" for h in hot[:5]], (got, hot)
    check_cards(page, "queen_W"); n += 1
    page.screenshot(path=str(shots / "html_desktop_awal.png"), full_page=True)
    # rekomendasi
    best = min((r for r in crit if r["K1 Moran"] == "Wajar"), key=lambda r: float(r["K3 penyesalan maks Moran"]))
    assert page.inner_text(".hero .pick").strip() == best["Spesifikasi"]
    page.click("#btnRec"); check_cards(page, best["W"]); n += 1
    # keluarga + parameter + skema
    page.get_by_role("button", name="KNN", exact=True).click()
    page.select_option("#selParam", "k = 6"); check_cards(page, "knn6_W"); n += 1
    page.locator("#segStyle button").first.click(); check_cards(page, "knn6_B"); n += 1
    page.get_by_role("button", name="Distance band", exact=True).click()
    page.select_option("#selParam", "d ≤ 1.65"); check_cards(page, "band165_B"); n += 1
    page.get_by_role("button", name="Inverse distance", exact=True).click(); check_cards(page, "idw1_B"); n += 1
    page.locator("#dotplot button", has_text="Rook · W").click(); check_cards(page, "rook_W"); n += 1
    # klik di bagian simulasi mengubah pilihan seluruh halaman
    page.locator(".chip", has_text="k = 2 · B").click(); check_cards(page, "knn2_B"); n += 1
    page.locator("#bars .brow", has_text="d ≤ 0,90 · W").click(); check_cards(page, "band090_W"); n += 1
    # lapisan peta + link
    for lay in ["raw", "sig", "gi", "lc", "fdr"]:
        page.select_option("#selLayer", lay)
        assert page.locator("#mapLisa path.reg").count() == 49
    page.check("#chkLinks"); assert page.locator("#mapVal line").count() > 0
    page.click("#btnRef"); check_cards(page, "queen_W"); n += 1
    # tabel 32 matriks + kolom simulasi
    assert page.locator("#cmp tbody tr").count() == 32
    for tid, nrow in [("#sensNum", 6), ("#sensInf", 7), ("#sensOut", 6), ("#cmpTbl", 6)]:
        assert page.locator(f"{tid} tbody tr").count() == nrow, tid
    assert page.locator("#concl .panel").count() == 3
    with page.expect_download() as d1: page.get_by_role("button", name="Unduh tabel perbandingan (CSV)").click()
    with page.expect_download() as d2: page.get_by_role("button", name="Unduh hasil konfigurasi ini (JSON)").click()
    assert d1.value.suggested_filename.endswith(".csv") and d2.value.suggested_filename.endswith(".json")
    # simulasi: penyesalan dan daya = CSV
    f3 = lambda x: fmt(float(x), 3); f2 = lambda x: fmt(float(x), 2)
    assert page.locator(".chip").count() == 32 and page.locator("#bars .brow").count() == 32
    for ix, col in [("Moran's I", "K3 penyesalan maks Moran"), ("Geary's C", "K3 penyesalan maks Geary")]:
        page.locator("#segIx button", has_text=ix).click()
        bars = {r.split("\n")[0].strip(): r.split("\n")[-1].strip() for r in page.locator("#bars .brow").all_inner_texts()}
        for r in crit:
            assert bars[r["Spesifikasi"]] == f3(r[col]), (ix, r["Spesifikasi"]); n += 1
    page.locator("#segIx button", has_text="Moran's I").click()
    for cls in ["Robust", "Menengah", "Sensitif"]:
        assert page.locator(f".classboard .col:has(.b-{cls}) .chip").count() == sum(r["Kelas"] == cls for r in crit), cls
    for lv in ["0,30", "0,90"]:
        page.locator("#segLv button", has_text=lv).click()
        cells = page.locator("#pheat .c").all_inner_texts(); rlab = page.locator("#pheat .rl").all_inner_texts()
        assert len(cells) == 160
        for i, lab in enumerate(rlab):
            for j, gn in enumerate(["G1", "G2", "G3", "G4", "G5"]):
                row = next(r for r in powr if labs.get(r["W"]) == lab and r["gen"] == gn and abs(float(r["level"]) - float(lv.replace(",", "."))) < 1e-9)
                assert cells[i * 5 + j] == f2(row["pow_I"]), (lab, gn, lv); n += 1
    assert page.locator("#mult svg").count() == 5
    # keyboard: Tab pertama ke kontrol toolbar
    page.reload(); page.wait_for_selector(".idx")
    for want in ["lnEn", "lnId", "lnRep"]:
        page.keyboard.press("Tab"); assert page.evaluate("document.activeElement.id") == want
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.closest('#segFam') !== null"), page.evaluate("document.activeElement.outerHTML")
    # semua 32 matriks: kartu hasil = CSV
    for s in sorted({k[1] for k in G}):
        page.evaluate(f"selectSpec('{s}')"); check_cards(page, s); n += 1
    page.evaluate("selectSpec('queen_W')")
    page.screenshot(path=str(shots / "html_desktop_penuh.png"), full_page=True)
    # ---- versi Inggris (bawaan): format angka, terjemahan, dan bagian tujuan ----
    e = b.new_page(viewport={"width": 1400, "height": 900})
    e.on("pageerror", lambda x: errors.append(str(x)))
    e.goto(base); e.wait_for_selector(".idx")
    assert e.evaluate("document.documentElement.lang") == "en"
    assert e.locator(".idx .big").first.inner_text() == "{:.4f}".format(float(G[(V, "queen_W", "Moran's I")]["stat"]))
    assert e.inner_text(".hero .pick").strip() == best["Spesifikasi"].replace(",", ".")
    assert e.locator(".classboard .b-Menengah").first.inner_text().strip() == "Intermediate"
    lc = next(r for r in csv.DictReader(open(proj / "output/csv/20b_sensitivitas_lokal.csv", encoding="utf-8")) if r["var"] == V)
    assert f"{lc['Sig. FDR min']}–{lc['Sig. FDR maks']}" in e.inner_text("#tujuan"), e.inner_text("#tujuan")[:200]
    assert e.locator("#lnEn[aria-current='true']").count() == 1
    e.click("#lnId"); e.wait_for_selector(".idx"); assert e.evaluate("document.documentElement.lang") == "id"
    e.screenshot(path=str(shots / "html_desktop_en_id.png"))
    # mobile
    m = b.new_page(viewport={"width": 390, "height": 844})
    m.on("pageerror", lambda e: errors.append(str(e)))
    m.goto(url); m.wait_for_selector(".idx"); m.wait_for_timeout(400)
    over = m.evaluate("document.documentElement.scrollWidth - innerWidth")
    m.screenshot(path=str(shots / "html_mobile.png"), full_page=True)
    small = m.evaluate("""[...document.querySelectorAll('.toolbar button, .toolbar select, section .btn, .seg button, .chip')].filter(e=>e.getBoundingClientRect().height<44).length""")
    b.close()

assert not errors, errors
assert over <= 0, f"overflow horizontal mobile {over}px"
assert small == 0, f"{small} kontrol < 44px"
print(f"OK: {n} pemeriksaan angka cocok dengan CSV (CRIME, data asli dan simulasi), versi Inggris dan Indonesia, konsol bersih, mobile tanpa overflow, target sentuh >= 44px")
