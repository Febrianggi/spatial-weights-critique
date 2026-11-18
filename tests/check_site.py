"""Build the GitHub Pages site and check that every page, asset and link works under a repository subpath.

    python tests/check_site.py                      # build into _site and run all checks
    python tests/check_site.py --build-only _site   # only assemble the site (used by the Pages workflow)

Checks:
  1. static: every relative href/src/url() in every HTML page resolves to a file inside the site, every
     #anchor exists, and no link starts with "/" (a root-absolute link breaks under /<repo>/ on GitHub Pages);
  2. browser: the site is served at http://127.0.0.1:<port>/<subpath>/ like GitHub Pages serves a project site,
     then the landing page, report and dashboard are opened and the links between them are clicked in both
     languages. Any 4xx/5xx response, request outside the subpath, or console error fails the check.
Set CHROME_PATH to use a specific Chrome binary.
"""
import functools, http.server, os, pathlib, re, shutil, sys, threading
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

ROOT = pathlib.Path(__file__).resolve().parent.parent
SUBPATH = os.environ.get("SITE_SUBPATH", "spatial-weights-critique")

# Everything the website needs. Paths are the same as in the repository, so links work identically
# when the files are opened locally and when they are served from GitHub Pages.
SITE_FILES = [
    "index.html",
    "dashboard_html/index.html",
    "reports/Columbus_Spatial_Analysis.html",
    "assets/fonts/inter-latin-400-normal.woff2",
    "assets/fonts/inter-latin-500-normal.woff2",
    "assets/fonts/inter-latin-600-normal.woff2",
    "assets/fonts/inter-latin-700-normal.woff2",
    "assets/fonts/OFL-Inter.txt",
]


def build(dst: pathlib.Path) -> pathlib.Path:
    if dst.exists():
        shutil.rmtree(dst)
    for rel in SITE_FILES:
        src = ROOT / rel
        if not src.is_file():
            sys.exit(f"missing site file: {rel}")
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst / rel)
    (dst / ".nojekyll").write_text("")  # serve files as they are, without Jekyll processing
    return dst


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self._style = [], set(), False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k) is not None:
                self.refs.append((tag, a[k]))
        if a.get("style"):
            self.refs += [(tag, u) for u in re.findall(r"url\(['\"]?([^'\")]+)", a["style"])]
        self._style = tag == "style"

    def handle_endtag(self, tag):
        if tag == "style":
            self._style = False

    def handle_data(self, data):
        if self._style:
            self.refs += [("style", u) for u in re.findall(r"url\(['\"]?([^'\")]+)", data)]


def static_check(site: pathlib.Path) -> int:
    pages = {p: Links() for p in site.rglob("*.html")}
    for p, parser in pages.items():
        parser.feed(p.read_text(encoding="utf-8"))
    errors, n = [], 0
    for p, parser in pages.items():
        for tag, ref in parser.refs:
            if re.match(r"^(data:|https?:|mailto:|javascript:)", ref) or ref.startswith("?"):
                continue
            n += 1
            parts = urlsplit(ref)
            if ref.startswith("/"):
                errors.append(f"{p.relative_to(site)}: root-absolute link {ref!r} breaks under /{SUBPATH}/")
                continue
            target = (p.parent / unquote(parts.path)).resolve() if parts.path else p
            if site.resolve() not in target.parents and target != site.resolve():
                errors.append(f"{p.relative_to(site)}: {ref!r} points outside the site")
            elif not target.is_file():
                errors.append(f"{p.relative_to(site)}: {ref!r} -> missing {target.relative_to(site.resolve())}")
            elif parts.fragment and target.suffix == ".html":
                ids = pages[next(k for k in pages if k.resolve() == target)].ids
                if parts.fragment not in ids:
                    errors.append(f"{p.relative_to(site)}: anchor {ref!r} not found")
    for e in errors:
        print("FAIL", e)
    print(f"static: {n} relative links and assets checked in {len(pages)} pages, {len(errors)} broken")
    return len(errors)


def browser_check(site: pathlib.Path) -> int:
    from playwright.sync_api import sync_playwright
    serve_root = site.parent / "_serve"
    if serve_root.exists():
        shutil.rmtree(serve_root)
    shutil.copytree(site, serve_root / SUBPATH)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=str(serve_root))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/{SUBPATH}/"
    problems, steps = [], 0
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(args=["--no-sandbox"], **({"executable_path": os.environ["CHROME_PATH"]} if os.environ.get("CHROME_PATH") else {}))
            ctx = b.new_context(viewport={"width": 1366, "height": 900})
            page = ctx.new_page()
            page.on("console", lambda m: problems.append(f"console error on {page.url}: {m.text}") if m.type == "error" else None)
            page.on("pageerror", lambda e: problems.append(f"page error on {page.url}: {e}"))
            page.on("response", lambda r: problems.append(f"HTTP {r.status} {r.url}") if r.status >= 400 else None)
            page.on("request", lambda r: problems.append(f"request outside /{SUBPATH}/: {r.url}")
                    if r.url.startswith("http") and not (r.url + "/").startswith(base) else None)

            def expect(cond, msg):
                nonlocal steps
                steps += 1
                if not cond:
                    problems.append(msg)

            # landing page, with and without the trailing slash GitHub Pages redirects
            page.goto(base.rstrip("/"))
            expect(page.url == base, f"no redirect to {base}: {page.url}")
            expect(page.evaluate("document.fonts.check('600 16px Inter')"), "Inter font not loaded on landing page")
            # landing -> dashboard (English)
            page.click("#goDash"); page.wait_for_selector(".idx")
            expect(page.url == base + "dashboard_html/index.html?lang=en", f"dashboard url {page.url}")
            expect(page.evaluate("document.documentElement.lang") == "en", "dashboard not English")
            # dashboard -> report (English)
            page.click("#lnRep"); page.wait_for_selector("section.chap#simulation")
            expect(page.url == base + "reports/Columbus_Spatial_Analysis.html?lang=en", f"report url {page.url}")
            expect(page.evaluate("document.documentElement.dataset.lang") == "en", "report not English")
            expect(page.evaluate("document.querySelectorAll('.exhibit img').length") > 0, "report figures missing")
            expect(page.evaluate("""async () => { const im = [...document.querySelectorAll('.exhibit img')];
                im.forEach(i => { i.loading = 'eager'; }); await Promise.all(im.map(i => i.decode()));
                return im.every(i => i.naturalWidth > 0) }"""), "a report figure did not load")
            # report: case index anchors scroll to existing chapters
            page.click(".toc a[href='#simulation']")
            expect(page.url.endswith("#simulation"), "case index link did not navigate")
            # switch report to Indonesian, then follow the dashboard link
            page.click(".lang button[data-lang='id']")
            expect(page.evaluate("document.documentElement.dataset.lang") == "id", "report language switch failed")
            page.click(".topbar .dash"); page.wait_for_selector(".idx")
            expect(page.url == base + "dashboard_html/index.html?lang=id", f"dashboard url after switch {page.url}")
            expect(page.evaluate("document.documentElement.lang") == "id", "dashboard did not open in Indonesian")
            expect(page.locator("#lnRep").inner_text() == "Laporan penelitian", "report link not translated")
            # dashboard (Indonesian) -> report keeps Indonesian
            page.click("#lnRep"); page.wait_for_selector("section.chap#simulation")
            expect(page.evaluate("document.documentElement.dataset.lang") == "id", "report did not open in Indonesian")
            # dashboard language links stay on the same page
            page.goto(base + "dashboard_html/index.html"); page.wait_for_selector(".idx")
            page.click("#lnId"); page.wait_for_selector(".idx")
            expect(page.url == base + "dashboard_html/index.html?lang=id", f"language link url {page.url}")
            # landing page in Indonesian points both cards to Indonesian pages
            page.goto(base + "?lang=id")
            expect(page.get_attribute("#goReport", "href") == "reports/Columbus_Spatial_Analysis.html?lang=id", "landing report link not localized")
            page.click("#goReport"); page.wait_for_selector("section.chap#why")
            expect(page.evaluate("document.documentElement.dataset.lang") == "id", "landing -> report lost Indonesian")
            # mobile: no horizontal scroll on any page
            m = ctx.new_page(); m.set_viewport_size({"width": 375, "height": 800})
            for path in ["", "dashboard_html/index.html", "reports/Columbus_Spatial_Analysis.html"]:
                m.goto(base + path); m.wait_for_timeout(300)
                sx = m.evaluate("() => { document.documentElement.style.scrollBehavior = 'auto'; window.scrollTo(300, 0); return window.scrollX }")
                expect(sx == 0, f"horizontal scroll on mobile: /{path} (scrollX {sx})")
            b.close()
    finally:
        srv.shutdown()
        shutil.rmtree(serve_root, ignore_errors=True)
    for e in problems:
        print("FAIL", e)
    print(f"browser: {steps} navigation checks at {base}, {len(problems)} problems")
    return len(problems)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--build-only":
        out = build(pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "_site").resolve())
        print(f"site built in {out}: {len(SITE_FILES)} files + .nojekyll")
        sys.exit(0)
    site = build((ROOT / "_site").resolve())
    bad = static_check(site)
    bad += browser_check(site)
    print("OK: site ready for GitHub Pages" if bad == 0 else f"FAILED: {bad} problems")
    sys.exit(1 if bad else 0)
