"""Uji dashboard HTML (satu halaman, khusus CRIME): konsol bersih, kontrol berfungsi, mobile tanpa overflow,
dan angka yang tampil sama dengan CSV hasil Rmd. Jalankan: python3 -I test_html_dashboard.py <proyek> <folder_screenshot>"""
import csv, json, os, sys, pathlib
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright

proj, shots = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
shots.mkdir(parents=True, exist_ok=True)
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=proj))
Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_port}/dashboard_html/index.html"
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
    assert page.locator("#bars .sel .bl").inner_text() == labs[spec]
    assert page.locator("#cmp tbody tr").first.get_attribute("data-spec") == spec

errors = []
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"], **({"executable_path": os.environ["CHROME_PATH"]} if os.environ.get("CHROME_PATH") else {}))
    page = b.new_page(viewport={"width": 1400, "height": 900})
    page.on("console", lambda m: m.type == "error" and errors.append(m.text))
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(url); page.wait_for_selector("[role=tab][aria-selected=true]")
    n = 0
    assert page.locator("[role=tabpanel]:visible").count() == 1
    assert page.locator("#panel-compare").is_visible()
    assert page.locator("[role=tab]").count() == 7 and page.locator("#selVar").count() == 0
    classes = {(r["spec_id"], r["POLYID"]): r["class_fdr"] for r in lisa if r["var"] == V}
    assert page.locator("#comp-spec, #board button").count() == 0
    assert page.locator("#comp-ref-count").inner_text() == "4 dari 49 signifikan"
    for spec in ("idw1_W", "knn2_W", "band165_W"):
        if spec == "knn2_W":
            page.get_by_role("button", name="K tetangga terdekat", exact=True).click()
        elif spec == "band165_W":
            page.get_by_role("button", name="Ambang jarak", exact=True).click()
            page.select_option("#selParam", "d ≤ 1.65")
        for panel, matrix in (("ref", "queen_W"), ("alt", spec)):
            marks = page.locator(f"#comp-{panel}-map path.reg")
            assert marks.count() == 49
            assert marks.evaluate_all("(marks) => marks.every(mark => mark.hasAttribute('fill'))")
            assert marks.evaluate_all("(marks) => Object.fromEntries(marks.map(mark => [mark.dataset.polyid, mark.dataset.lisa]))") == {
                district: category for (matrix_id, district), category in classes.items() if matrix_id == matrix
            }
    page.get_by_role("button", name="K tetangga terdekat", exact=True).click()
    assert page.locator("#comp-alt-count").inner_text() == "0 dari 49 signifikan"
    assert "Tidak ada wilayah signifikan" in page.inner_text("#comp-status")
    assert page.locator("#comp-alt-map .reg").first.evaluate("(mark) => getComputedStyle(mark).transitionDuration") == "0.46s"
    page.emulate_media(reduced_motion="reduce")
    assert page.locator("#comp-alt-map .reg").first.evaluate("(mark) => getComputedStyle(mark).transitionDuration") == "0s"
    page.emulate_media(reduced_motion="no-preference")
    page.click("#btnRec")
    page.select_option("#comp-region", "16")
    mark = page.locator('#comp-alt-map [data-polyid="25"]')
    mark.dispatch_event("click")
    assert page.locator("#comp-region").input_value() == "25"
    assert all(path.get_attribute("d") == mark.get_attribute("d") for path in page.locator(".compare-outline").all())
    page.click("#comp-open"); check_cards(page, "idw1_W")
    assert page.locator("#h-hasil").evaluate("(heading) => heading === document.activeElement")
    page.click("#btnRef")
    check_cards(page, "queen_W"); n += 1
    page.screenshot(path=str(shots / "html_desktop_awal.png"), full_page=True)
    # rekomendasi
    best = min((r for r in crit if r["K1 Moran"] == "Wajar"), key=lambda r: float(r["K3 penyesalan maks Moran"]))
    assert page.inner_text(".hero .pick").strip() == best["Spesifikasi"]
    page.click("#btnRec"); check_cards(page, best["W"]); n += 1
    # keluarga + parameter + skema
    page.get_by_role("button", name="K tetangga terdekat", exact=True).click()
    page.select_option("#selParam", "k = 6"); check_cards(page, "knn6_W"); n += 1
    page.locator("#segStyle button").first.click(); check_cards(page, "knn6_B"); n += 1
    page.get_by_role("button", name="Ambang jarak", exact=True).click()
    page.select_option("#selParam", "d ≤ 1.65"); check_cards(page, "band165_B"); n += 1
    page.get_by_role("button", name="Invers jarak", exact=True).click(); check_cards(page, "idw1_B"); n += 1
    page.click("#tab-sensitivity")
    page.click("#btnRef")
    page.select_option("#selParam", "Rook")
    check_cards(page, "rook_W"); n += 1
    assert page.locator("#dotplot .sel .spec-label").inner_text() == labs["rook_W"]
    page.click("#tab-simulation")
    page.get_by_role("button", name="K tetangga terdekat", exact=True).click()
    page.locator("#segStyle button").first.click()
    check_cards(page, "knn2_B"); n += 1
    page.get_by_role("button", name="Ambang jarak", exact=True).click()
    page.select_option("#selParam", "d ≤ 0.90")
    page.locator("#segStyle button").last.click()
    check_cards(page, "band090_W"); n += 1
    # lapisan peta + link
    page.click("#tab-maps")
    page.click("#btnRef")
    page.set_viewport_size({"width": 1120, "height": 640})
    page.locator("#mapLisa").evaluate("(map) => map.scrollIntoView({block:'center'})")
    assert page.evaluate("scrollY > document.querySelector('.masthead').offsetHeight")
    assert abs(page.locator("#toolbar").bounding_box()["y"] - page.locator(".tab-strip").bounding_box()["height"]) < 2
    assert page.locator("#segFam button").first.evaluate("(b) => { const r=b.getBoundingClientRect(); return b.contains(document.elementFromPoint(r.x+r.width/2, r.y+r.height/2)); }")
    # Verify real CSS transitions on the existing polygons and final colors after a rapid change.
    def change_colors(selector, change):
        return page.locator(selector).evaluate("""(map, action) => {
          const marks = [...map.querySelectorAll("path.reg")];
          marks.forEach(m => getComputedStyle(m).fill);
          if (action === "matrix") document.querySelector("#btnRec").click();
          else {
            const layer = document.querySelector("#selLayer");
            layer.value = action;
            layer.dispatchEvent(new Event("change"));
          }
          getComputedStyle(marks[0]).fill;
          return marks.every(m => map.contains(m)) && marks.some(m => m.getAnimations().some(a => a.transitionProperty === "fill"));
        }""", change)
    assert change_colors("#mapLisa", "matrix")
    assert change_colors("#mapLisa", "sig")
    page.select_option("#selLayer", "raw")
    page.wait_for_function("""() => [...document.querySelectorAll("#mapLisa .reg")].every(m => {
      const hex = m.getAttribute("fill");
      const channels = hex.slice(1).match(/../g).map(x => parseInt(x,16));
      return getComputedStyle(m).fill === "rgb(" + channels.join(", ") + ")";
    })""")
    page.emulate_media(reduced_motion="reduce")
    assert not change_colors("#mapLisa", "fdr")
    assert page.locator("#mapLisa .reg").first.evaluate("m => getComputedStyle(m).transitionDuration") == "0s"
    page.emulate_media(reduced_motion="no-preference")
    page.set_viewport_size({"width": 1400, "height": 900})
    for lay in ["raw", "sig", "gi", "lc", "stab", "fdr"]:
        page.select_option("#selLayer", lay)
        assert page.locator("#mapLisa path.reg").count() == 49
    page.check("#chkLinks"); assert page.locator("#mapVal line").count() > 0
    page.click("#btnRef"); check_cards(page, "queen_W"); n += 1
    # tabel 32 matriks + kolom simulasi
    assert page.locator("#cmp tbody tr").count() == 32
    for tid, nrow in [("#sensNum", 6), ("#sensInf", 7), ("#sensOut", 6), ("#cmpTbl", 6)]:
        assert page.locator(f"{tid} tbody tr").count() == nrow, tid
    assert page.locator("#concl .panel").count() == 3
    page.click("#tab-tables")
    headers = page.locator("#cmp th")
    rows = page.locator("#cmp tbody tr")
    def row_ids():
        return rows.evaluate_all("rows => rows.map(row => row.dataset.spec)")
    original = row_ids()
    header = headers.filter(has_text="Moran I")
    header.get_by_role("button").click()
    assert header.get_attribute("aria-sort") == "ascending"
    def check_moran_sort(active, descending):
        ids = row_ids()
        assert len(ids) == len(set(ids)) == 32 and ids[0] == active
        values = [float(G[(V, spec, "Moran's I")]["stat"]) for spec in ids[1:]]
        assert values == sorted(values, reverse=descending)
    check_moran_sort("queen_W", False)
    header.get_by_role("button").press("Enter")
    check_moran_sort("queen_W", True)
    page.click("#btnRec")
    check_moran_sort(best["W"], True)
    page.click("#tab-simulation")
    page.click("#btnRef")
    page.click("#tab-tables")
    check_moran_sort("queen_W", True)
    for sort_button in headers.get_by_role("button").all():
        sort_button.click()
        assert len(set(row_ids())) == len(original) and row_ids()[0] == "queen_W"
    page.click("#btnRec")
    with (proj / "output/json/columbus_results.json").open(encoding="utf-8") as source:
        specs = json.load(source)["specs"]
    default_order = [spec for _, spec in sorted(zip(specs["order"], specs["id"]))]
    assert row_ids() != default_order and row_ids()[0] != default_order[0]
    with page.expect_download() as d1: page.get_by_role("button", name="Unduh tabel perbandingan (CSV)").click()
    with page.expect_download() as d2: page.get_by_role("button", name="Unduh hasil konfigurasi ini (JSON)").click()
    with open(d1.value.path(), encoding="utf-8-sig", newline="") as downloaded:
        assert [r["spec_id"] for r in csv.DictReader(downloaded)] == default_order
    assert d1.value.suggested_filename.endswith(".csv") and d2.value.suggested_filename.endswith(".json")
    # simulasi: penyesalan dan daya = CSV
    f3 = lambda x: fmt(float(x), 3); f2 = lambda x: fmt(float(x), 2)
    assert page.locator("#board button, #bars [role=button]").count() == 0 and page.locator("#bars .brow").count() == 32
    page.click("#tab-simulation")
    for ix, col in [("Moran's I", "K3 penyesalan maks Moran"), ("Geary's C", "K3 penyesalan maks Geary")]:
        page.locator("#segIx button", has_text=ix).click()
        bars = {r.split("\n")[0].strip(): r.split("\n")[-1].strip() for r in page.locator("#bars .brow").all_inner_texts()}
        for r in crit:
            assert bars[r["Spesifikasi"]] == f3(r[col]), (ix, r["Spesifikasi"]); n += 1
    page.locator("#segIx button", has_text="Moran's I").click()
    for cls in ["Robust", "Menengah", "Sensitif"]:
        assert int(page.locator(f".classboard .col:has(.b-{cls}) .num").inner_text().split()[0]) == sum(r["Kelas"] == cls for r in crit), cls
    for lv in ["0,30", "0,90"]:
        page.locator("#segLv button", has_text=lv).click()
        cells = page.locator("#pheat .c").all_inner_texts(); rlab = page.locator("#pheat .rl").all_inner_texts()
        assert len(cells) == 160
        for i, lab in enumerate(rlab):
            for j, gn in enumerate(["G1", "G2", "G3", "G4", "G5"]):
                row = next(r for r in powr if labs.get(r["W"]) == lab and r["gen"] == gn and abs(float(r["level"]) - float(lv.replace(",", "."))) < 1e-9)
                assert cells[i * 5 + j] == f2(row["pow_I"]), (lab, gn, lv); n += 1
    assert page.locator("#mult svg").count() == 5
    # Keyboard navigation, direct links, history and language continuity.
    page.goto(url)
    page.focus("#home-link")
    for want in ["lnEn", "lnId", "lnRep", "tab-compare"]:
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.id") == want
    page.keyboard.press("ArrowRight")
    assert page.locator("#panel-maps").is_visible()
    page.keyboard.press("End")
    assert page.locator("#panel-tables").is_visible()
    page.go_back()
    assert page.locator("#panel-maps").is_visible()
    page.reload()
    assert page.locator("#panel-maps").is_visible()
    page.click("#lnEn")
    assert page.locator("#tab-maps").inner_text() == "Local maps" and page.locator("#panel-maps").is_visible()
    page.click("#lnId")
    page.click("#tab-results")
    # Read animation keyframes in the interaction task, independent of the test runner's speed.
    page.click("#tab-tables")
    page.click("#btnRef")
    # Let the rows settle first: a row still sliding from the previous selection already sits near its new place.
    page.evaluate("document.getAnimations().forEach(a => a.finish())")
    def pin_motion():
        return page.evaluate("""() => {
            document.querySelector("#btnRec").click();
            const row = document.querySelector("#cmp tbody tr");
            const anim = row.getAnimations().find(a => a.id === "dashboard-motion");
            return {id: row.dataset.spec, frames: anim?.effect.getKeyframes().map(k => k.transform)};
        }""")
    movement = pin_motion()
    assert movement["id"] == best["W"] and movement["frames"][-1] == "none"
    assert float(movement["frames"][0].split("(")[1].split("px")[0]) > 0
    page.click("#tab-methods")
    assert not page.locator("#toolbar").is_visible()
    assert page.evaluate("curSpec().id") == best["W"]
    page.click("#tab-simulation")
    assert page.locator("#toolbar").is_visible()
    assert page.evaluate("""() => {
        document.querySelector("#segIx button:last-child").click();
        return !!document.querySelector("#segIx .moving-highlight")?.getAnimations().length;
    }""")
    page.emulate_media(reduced_motion="reduce")
    page.click("#tab-tables")
    page.click("#btnRef")
    assert pin_motion().get("frames") is None
    assert page.evaluate("document.getAnimations().every(a => a.id !== 'dashboard-motion')")
    page.emulate_media(reduced_motion="no-preference")
    # semua 32 matriks: kartu hasil = CSV
    for s in sorted({k[1] for k in G}):
        page.evaluate(f"selectSpec('{s}')"); check_cards(page, s); n += 1
    page.evaluate("selectSpec('queen_W')")
    page.screenshot(path=str(shots / "html_desktop_penuh.png"), full_page=True)
    # ---- versi Inggris (bawaan): format angka, terjemahan, dan bagian tujuan ----
    e = b.new_page(viewport={"width": 1400, "height": 900})
    e.on("pageerror", lambda x: errors.append(str(x)))
    e.goto(base); e.wait_for_selector("[role=tab][aria-selected=true]")
    assert e.evaluate("document.documentElement.lang") == "en"
    assert e.locator(".idx .big").first.inner_text() == "{:.4f}".format(float(G[(V, "idw1_W", "Moran's I")]["stat"]))
    assert e.inner_text(".hero .pick").strip() == best["Spesifikasi"].replace(",", ".")
    assert e.locator(".classboard .b-Menengah").first.inner_text().strip() == "Intermediate"
    lc = next(r for r in csv.DictReader(open(proj / "output/csv/20b_sensitivitas_lokal.csv", encoding="utf-8")) if r["var"] == V)
    assert f"{lc['Sig. FDR min']}–{lc['Sig. FDR maks']}" in e.inner_text("#tujuan"), e.inner_text("#tujuan")[:200]
    assert e.locator("#lnEn[aria-current='true']").count() == 1
    e.click("#lnId"); e.wait_for_selector("[role=tab][aria-selected=true]"); assert e.evaluate("document.documentElement.lang") == "id"
    e.screenshot(path=str(shots / "html_desktop_en_id.png"))
    # mobile
    m = b.new_page(viewport={"width": 390, "height": 844})
    m.on("pageerror", lambda e: errors.append(str(e)))
    m.goto(url); m.wait_for_selector("[role=tab][aria-selected=true]"); m.wait_for_timeout(400)
    over = m.evaluate("document.documentElement.scrollWidth - innerWidth")
    left = m.locator("#comp-ref-map svg").bounding_box()
    right = m.locator("#comp-alt-map svg").bounding_box()
    assert abs(left["y"] - right["y"]) < 1 and abs(left["height"] - right["height"]) < 1
    m.screenshot(path=str(shots / "html_mobile.png"), full_page=True)
    small = 0
    for tab in m.get_by_role("tab").all():
        tab.click()
        shows_weights = tab.get_attribute("id") != "tab-methods"
        assert m.locator("#filter-toggle").is_visible() == shows_weights
        m.evaluate("window.scrollTo(0, 350)")
        if shows_weights:
            assert abs(m.locator("#filter-toggle").bounding_box()["y"]) < 2
        m.evaluate("window.scrollTo(0, 0)")
        assert m.locator("[role=tabpanel]:visible").count() == 1
        over = max(over, m.evaluate("document.documentElement.scrollWidth - innerWidth"))
        small += m.locator(".toolbar button:visible, .toolbar select:visible, section .btn:visible, .seg button:visible, #cmp th button:visible, [role=tab]:visible").evaluate_all(
            "(items) => items.filter(e => e.getBoundingClientRect().height < 44).length")
    m.click("#tab-maps")
    assert not m.locator("#matrix-controls").is_visible()
    m.locator("#mapLisa").evaluate("(map) => map.scrollIntoView({block:'center'})")
    assert m.evaluate("scrollY") > 100
    assert abs(m.locator("#filter-toggle").bounding_box()["y"]) < 2
    before = m.locator("#mapLisa").bounding_box()["y"]
    m.click("#filter-toggle")
    assert abs(m.locator("#mapLisa").bounding_box()["y"] - before) < 2
    assert m.locator("#matrix-controls").is_visible()
    m.click("#btnRec")
    assert best["Spesifikasi"] in m.inner_text("#filter-toggle")
    m.click("#filter-toggle")
    assert m.locator("#mapLisa svg").bounding_box()["y"] > m.locator("#mapVal svg").bounding_box()["y"]
    b.close()

server.shutdown()
assert not errors, errors
assert over <= 0, f"overflow horizontal mobile {over}px"
assert small == 0, f"{small} kontrol < 44px"
print(f"OK: {n} pemeriksaan angka cocok dengan CSV (CRIME, data asli dan simulasi), versi Inggris dan Indonesia, konsol bersih, mobile tanpa overflow, target sentuh >= 44px")
