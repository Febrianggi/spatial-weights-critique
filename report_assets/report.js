<script>
(function () {
  "use strict";
  var root = document.documentElement;

  /* Language: ?lang=id, then the last choice, then English. */
  function stored() { try { return localStorage.getItem("columbus-lang"); } catch (e) { return null; } }
  function remember(l) { try { localStorage.setItem("columbus-lang", l); } catch (e) { /* storage blocked: keep the choice for this page only */ } }
  function setLang(l, save) {
    l = l === "id" ? "id" : "en";
    root.setAttribute("data-lang", l);
    root.setAttribute("lang", l);
    var bs = document.querySelectorAll(".lang button");
    for (var i = 0; i < bs.length; i++) bs[i].setAttribute("aria-pressed", String(bs[i].getAttribute("data-lang") === l));
    var t = document.querySelector("meta[name='title-" + l + "']");
    if (t) document.title = t.getAttribute("content");
    if (save) remember(l);
    var dash = document.querySelector(".topbar .dash");
    if (dash) dash.setAttribute("href", "../dashboard_html/index.html?lang=" + l);
  }
  var q = new URLSearchParams(location.search).get("lang");
  setLang(q || stored() || "en", false);
  var bs = document.querySelectorAll(".lang button");
  for (var i = 0; i < bs.length; i++) bs[i].addEventListener("click", function () { setLang(this.getAttribute("data-lang"), true); });

  /* Case index: mark the chapter being read. */
  var links = document.querySelectorAll(".toc a"), map = {};
  for (var j = 0; j < links.length; j++) map[links[j].getAttribute("href").slice(1)] = links[j];
  if ("IntersectionObserver" in window && links.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        for (var k in map) map[k].removeAttribute("aria-current");
        if (map[e.target.id]) map[e.target.id].setAttribute("aria-current", "true");
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    document.querySelectorAll("section.chap").forEach(function (s) { io.observe(s); });
  }

  /* Background: faint detective, chalk outline and magnifier silhouettes in the side gutters. Decoration only. */
  var SIL = {
    detective: '<g fill="currentColor"><path d="M28 33 Q60 26 94 33 L93 38 Q60 32 29 38Z"/><path d="M42 33 L46 13 Q61 6 76 13 L80 33Z"/><ellipse cx="62" cy="46" rx="12" ry="13"/><path d="M44 58 Q62 51 80 58 L88 122 L98 162 L28 162 L40 122Z"/><path d="M45 160 L35 210 L48 213 L59 163Z"/><path d="M70 160 L88 207 L101 204 L83 160Z"/><path d="M78 66 L104 92 L98 99 L73 78Z"/><path d="M33 211 L52 211 L52 217 L28 217Z"/><path d="M86 205 L106 200 L108 206 L88 211Z"/></g><circle cx="108" cy="102" r="8" fill="none" stroke="currentColor" stroke-width="3"/>',
    chalk: '<g fill="none" stroke="currentColor" stroke-width="3.6" stroke-linejoin="round" stroke-linecap="round"><circle cx="52" cy="46" r="17"/><path d="M66 58 L100 50 L140 22 L152 30 L118 62 L170 70 L222 52 L270 68 L266 80 L224 70 L196 92 L246 128 L238 138 L184 106 L150 100 L118 124 L104 152 L92 148 L102 118 L84 98 L46 108 L42 96 L76 82 Z"/></g>',
    glass: '<g fill="none" stroke="currentColor" stroke-width="7" stroke-linecap="round"><circle cx="42" cy="42" r="28"/><path d="M63 63 L96 96"/></g>'
  };
  function scatter() {
    var box = document.getElementById("bgfx"); if (!box) return;
    var Wd = root.clientWidth, Hd = document.body.scrollHeight, wrapW = Math.min(1240, Wd), gutter = (Wd - wrapW) / 2;
    var kinds = ["detective", "chalk", "detective", "glass", "chalk", "detective"], out = [];
    var n = Math.max(6, Math.round(Hd / (Wd < 760 ? 1600 : 640)));
    for (var i = 0; i < n; i++) {
      var kind = kinds[i % kinds.length];
      var w = kind === "chalk" ? 170 + Math.random() * 90 : kind === "glass" ? 70 + Math.random() * 40 : 90 + Math.random() * 60;
      var vb = kind === "chalk" ? "0 0 300 170" : kind === "glass" ? "0 0 110 110" : "0 0 120 220";
      var left = gutter > w * .6 ? (i % 2 ? Wd - gutter + Math.random() * Math.max(0, gutter - w) : Math.random() * Math.max(0, gutter - w)) : Math.random() * (Wd - w);
      var top = 620 + (i + Math.random() * .8) * (Hd - 800) / n;
      var rot = kind === "chalk" ? Math.random() * 50 - 25 : 0, flip = kind === "detective" && Math.random() < .5 ? -1 : 1;
      out.push('<svg viewBox="' + vb + '" style="left:' + left.toFixed(0) + 'px;top:' + top.toFixed(0) + 'px;width:' + w.toFixed(0) +
        'px;opacity:' + (0.045 + Math.random() * .035).toFixed(3) + ';transform:rotate(' + rot.toFixed(0) + 'deg) scaleX(' + flip + ')">' + SIL[kind] + '</svg>');
    }
    box.innerHTML = out.join("");
  }
  requestAnimationFrame(scatter);
  var rt; addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(scatter, 250); });
})();
</script>
