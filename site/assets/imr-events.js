/* IMR usage events for GoatCounter (cookie-free, no personal data). Counts database downloads and use of the main tools.
   Events appear in the GoatCounter dashboard under paths starting with "event/". */
(function () {
  function send(path, title) {
    try {
      if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({path: path, title: title || path, event: true});
    } catch (e) {}
  }
  var page = location.pathname.replace(/index\.html$/, "") || "/";
  var lang = function () { try { return (localStorage.getItem("imr-lang") || document.documentElement.lang || "en").slice(0, 2); } catch (e) { return "en"; } };
  document.addEventListener("click", function (e) {
    var el = e.target.closest && e.target.closest("a[download], a[href$='.csv'], a[href$='.json'], a[href$='.bib'], a[href$='.pdf'], a[href$='.docx'], button[id^='dl-'], .dl, [data-dl]");
    if (!el) return;
    var name = (el.getAttribute("href") || el.id || el.textContent || "").trim().replace(/\s+/g, " ").slice(0, 80);
    send("event/download" + page + name, "Download: " + name + " (" + page + ")");
  }, true);
  document.addEventListener("change", function (e) {
    var t = e.target; if (!t || !t.id) return;
    if (t.id === "migconv") send("event/tool" + page + "migrant-conventions-" + (t.checked ? "on" : "off"), "Score switch C97/C143/C189 " + (t.checked ? "on" : "off"));
    else if (t.id === "cd-tool") send("event/tool" + page + "reasoning-" + t.value, "Reasoning tool filter: " + t.value);
  }, true);
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-view], [data-cmode], [data-lens], [data-lang], .lang-switch button, #gocmp");
    if (!b) return;
    var v = b.getAttribute("data-view") || b.getAttribute("data-cmode") || b.getAttribute("data-lens") || b.getAttribute("data-lang") || b.id || "";
    if (v) send("event/tool" + page + "view-" + v, "View or option: " + v + " (" + page + ")");
  }, true);
  window.addEventListener("load", function () { setTimeout(function () { send("event/lang/" + lang() + page, "Language " + lang()); }, 1500); });
})();
