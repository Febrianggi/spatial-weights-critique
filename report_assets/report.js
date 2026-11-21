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
    var home = document.querySelector(".topbar .brand");
    if (home) home.setAttribute("href", "../index.html?lang=" + l);
    var dash = document.querySelector(".topbar .dash");
    if (dash) dash.setAttribute("href", "../dashboard_html/index.html?lang=" + l);
  }
  var q = new URLSearchParams(location.search).get("lang");
  setLang(q || stored() || "en", false);
  var bs = document.querySelectorAll(".lang button");
  for (var i = 0; i < bs.length; i++) bs[i].addEventListener("click", function () { setLang(this.getAttribute("data-lang"), true); });

  /* Contents: mark the chapter being read. */
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

})();
</script>
