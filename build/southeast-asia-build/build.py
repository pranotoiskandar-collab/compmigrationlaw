#!/usr/bin/env python3
"""Build theimr.org /southeast-asia/ from the East Asia page (shell + engine) and sea-data.js.

Usage: python3 build.py <site-root>
- southeast-asia/index.html  shell from east-asia/index.html with SEA text and sections
- southeast-asia/sea.js      engine from east-asia/ea.js, reading window.SEA, plus an origins section from window.OC
- southeast-asia/sea-data.js, sea-i18n.js, data/*.csv
- countries-of-origin/oc-sea.js (+ script tag), Thailand and Singapore in the bilateral matrix
Idempotent. Afterwards run deploy.py (menu, lang.js, plain.js, sitemap, llms.txt), then ai_use.py and analytics.py.
"""
import os, re, sys, shutil, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1]
EA = os.path.join(ROOT, "east-asia")
OUT = os.path.join(ROOT, "southeast-asia")
os.makedirs(os.path.join(OUT, "data"), exist_ok=True)


def rep(s, old, new, count=1, need=True):
    if old not in s:
        if need:
            raise SystemExit("not found: " + old[:90])
        return s
    return s.replace(old, new) if count == 0 else s.replace(old, new, count)


# ---------------------------------------------------------------- engine
js = open(os.path.join(EA, "ea.js"), encoding="utf-8").read()
js = rep(js, "/* Migrant workers in East Asia: renders the page from window.EA (ea-data.js).",
         "/* Migrant workers in Southeast Asia: renders the page from window.SEA (sea-data.js) and, for the origin section, window.OC (Countries of Origin data). Engine adapted from ea.js.")
js = rep(js, "window.EA", "window.SEA", 0)
js = rep(js, 'var CODED = "2026-10-31";', 'var CODED = "2026-11-13";')
js = re.sub(r'\|\| "TW";', '|| "MY";', js)
js = rep(js, 'var curD = "TW";', 'var curD = "MY";', need=False)
js = rep(js, 'var curC = "TW";', 'var curC = "MY";', need=False)
# ASEAN-wide instruments: show them under every state and name them
js = rep(js, "var sname = function (k) { var s = stateOf(k); return s ? t(s.n, s.n_id) : k; };",
         'var sname = function (k) { if (k === "ASEAN") return t("All ASEAN members", "Semua anggota ASEAN"); var s = stateOf(k); return s ? t(s.n, s.n_id) : k; };')
js = rep(js, "var F = (G.frameworks || []).filter(function (a) { return a.s === s.k; });",
         'var F = (G.frameworks || []).filter(function (a) { return a.s === s.k || a.s === "ASEAN"; });')
js = rep(js, "var F = (G.frameworks || []).filter(function (a) { return !AF.s || a.s === AF.s; });",
         'var F = (G.frameworks || []).filter(function (a) { return !AF.s || a.s === AF.s || a.s === "ASEAN"; });')
js = rep(js, "return (!AF.s || a.s === AF.s) &&", 'return (!AF.s || a.s === AF.s || a.s === "ASEAN") &&')
js = rep(js, '["regional", "Regional (fisheries bodies)", "Kawasan (badan perikanan)"]', '["regional", "Regional (ASEAN)", "Regional (ASEAN)"]')
js = rep(js, '["mou", "Memorandum of understanding", "Nota kesepahaman"]]',
         '["mou", "Memorandum of understanding", "Nota kesepahaman"], ["declaration", "Declaration or consensus (non-binding)", "Deklarasi atau konsensus (tidak mengikat)"]]')
# original-language titles
js = rep(js, '(x.s === "KR" ? "ko" : x.s === "JP" ? "ja" : "zh-Hant")', '({MY:"ms", BN:"ms", TH:"th", SG:"en"}[x.s] || "und")', 0)
# verification line computed from the data
js = re.sub(r"'<p class=\"g-note\">' \+ t\(\"30 of 70 cells have been checked.*?\"\) \+ \"</p></div>\";",
            "'<p class=\"g-note\">' + vline() + \"</p></div>\";", js, flags=re.S)
assert "vline()" in js, "verification line not patched"
js = rep(js, "  function pill(v) {",
         '  function vline() { var n = 0, p = 0; GR.forEach(function (g) { CB.forEach(function (d) { n++; if (G.checked && G.checked[g.k + "." + d.k]) p++; }); });\n'
         '    return p ? t(p + " of " + n + " cells have been checked against the official legal texts (P); the others rest on secondary sources and statutory citations (S). See Method.", p + " dari " + n + " sel telah diperiksa terhadap teks hukum resmi (P); sisanya bersandar pada sumber sekunder dan rujukan pasal (S). Lihat Metode.")\n'
         '      : t("All " + n + " cells rest on secondary sources and statutory citations (S) until the check against the official legal texts is complete. See Method.", "Seluruh " + n + " sel bersandar pada sumber sekunder dan rujukan pasal (S) sampai pemeriksaan terhadap teks hukum resmi selesai. Lihat Metode."); }\n'
         "  function pill(v) {")
# memoranda paragraph: generic
js = re.sub(r"  function memos\(\) \{.*?\n  \}\n", "  function memos() {\n    $(\"g-memos\").innerHTML = (G.memos || []).map(function (m) { return \"<p><b>\" + esc(t(m[0], m[1])) + \"</b>: \" + esc(t(m[2], m[3])) + \"</p>\"; }).join(\"\");\n  }\n", js, count=1, flags=re.S)
# citation and downloads
js = rep(js, "Migrant workers in East Asia: Migration and labor laws in comparison", "Migrant workers in Southeast Asia: Migration and labor laws in comparison")
js = rep(js, "https://theimr.org/east-asia/", "https://theimr.org/southeast-asia/", 0)
js = rep(js, "imr_eastasia_", "imr_southeastasia_")
js = js.replace("Migrant Workers in East Asia", "Migrant Workers in Southeast Asia")
js = rep(js, '"imr-east-asia', '"imr-southeast-asia', 0)
js = js.replace("Institute for Migrant Rights, Migrant workers in East Asia", "Institute for Migrant Rights, Migrant workers in Southeast Asia")
js = rep(js, "eps_memoranda:G.eps, ssw_memoranda:G.ssw, ", "origins:originRows(), ")
# sections this release does not show (people, corridors, corridor statistics)
js = rep(js, "intlTable(); profile(); demog(); agreements(); memos(); laws(); corridors(); reforms(); method(); sources(); }",
         "intlTable(); profile(); origins(); agreements(); memos(); laws(); reforms(); method(); sources(); }")
js = rep(js, "    all(); stats();", "    all();")
# drop the corridors CSV button (no corridor data yet)
js = rep(js, '["co", t("Corridors (CSV)", "Koridor (CSV)")], ', '["or", t("Origin states (CSV)", "Negara asal (CSV)")], ')
js = rep(js, '      if (k === "rf")', '      if (k === "or") save("imr-southeast-asia-origins" + v + ".csv", csv(originRows(), ["country", "feature", "feature_name", "value", "note", "source", "evidence"]), "text/csv");\n      if (k === "rf")')

ORIG = r'''
  /* ---------- V. countries of origin (from window.OC) ---------- */
  var OK = ["ID", "PH", "VN", "MM", "KH", "LA", "TL"], osel = null;
  function OCd() { return window.OC || {}; }
  function ostates() { var O = OCd(); return (O.states || []).filter(function (s) { return OK.indexOf(s.k) >= 0; }).sort(function (a, b) { return OK.indexOf(a.k) - OK.indexOf(b.k); }); }
  function originRows() {
    var O = OCd(), out = [];
    ostates().forEach(function (s) { (O.codebook || []).forEach(function (d) { var c = ((O.codes || {})[s.k] || {})[d.k] || []; out.push({country:s.k, feature:d.k, feature_name:d.en, value:c[0], note:c[1], source:c[2], evidence:(O.checked && O.checked[s.k + "." + d.k]) ? "P" : "S"}); }); });
    return out;
  }
  function origins() {
    var O = OCd(), OB = O.codebook || [], OS = ostates();
    if (!OS.length) { $("g-orig").innerHTML = '<p class="g-empty">' + t("The origin data could not be loaded.", "Data negara asal tidak bisa dimuat.") + "</p>"; return; }
    var h = "<thead><tr><th>" + t("Country of origin", "Negara asal") + "</th>" + OB.map(function (d) { return "<th>" + esc(t(d.en, d.id)) + "</th>"; }).join("") + "<th>" + t("Profile", "Profil") + "</th></tr></thead><tbody>";
    OS.forEach(function (s) {
      h += "<tr><td><b>" + esc(t(s.n, s.n_id)) + "</b>" + (s.sea ? ' <span class="g-mono">· ' + t("new", "baru") + "</span>" : "") + "</td>" + OB.map(function (d) {
        var c = ((O.codes || {})[s.k] || {})[d.k] || [], on = osel && osel[0] === s.k && osel[1] === d.k;
        return '<td class="c"><button type="button" class="g-cell" data-o="' + s.k + '" data-f="' + d.k + '" aria-pressed="' + !!on + '">' + pill(c[0]) + "</button></td>";
      }).join("") + '<td class="c"><a href="/countries-of-origin/#profile-' + s.k + '">' + t("Open", "Buka") + "</a></td></tr>";
    });
    $("g-orig").innerHTML = h + "</tbody>";
    $("g-orig").onclick = function (e) { var b = e.target.closest("[data-o]"); if (!b) return; osel = [b.getAttribute("data-o"), b.getAttribute("data-f")]; origins(); };
    var n = "";
    if (osel) {
      var s = OS.filter(function (x) { return x.k === osel[0]; })[0], d = OB.filter(function (x) { return x.k === osel[1]; })[0], c = ((O.codes || {})[osel[0]] || {})[osel[1]] || [];
      if (s && d) n = '<div class="g-card"><h3>' + esc(t(s.n, s.n_id)) + " · " + esc(t(d.en, d.id)) + "</h3><p>" + pill(c[0]) + " " + esc(c[0] == null ? t("Could not be established from the sources so far.", "Belum bisa dipastikan dari sumber yang ada.") : t(d["l" + c[0]], d["l" + c[0] + "_id"])) + "</p><p>" + esc(c[1] || "") + '</p><p class="g-mono">' + t("Source: ", "Sumber: ") + esc(c[2] || "") + " · " + ((O.checked && O.checked[osel[0] + "." + osel[1]]) ? t("P · checked against the official text on ", "P · diperiksa terhadap teks resmi pada ") + O.checked_on + (O.checked[osel[0] + "." + osel[1]] === "partly" ? t(" (partly)", " (sebagian)") : "") : t("S · not yet checked against the official text", "S · belum diperiksa terhadap teks resmi")) + "</p></div>";
    }
    $("g-orignote").innerHTML = n;
    var I = O.intl || {}, T = (O.treaties || []).filter(function (x) { return ["icrmw", "cedaw", "palermo", "c97", "c143", "c181", "c189", "c190"].indexOf(x[0]) >= 0; });
    $("g-origintl").innerHTML = "<thead><tr><th>" + t("Instrument", "Instrumen") + "</th>" + OS.map(function (s) { return "<th>" + esc(t(s.n, s.n_id)) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      T.map(function (x) { return "<tr><td><b>" + esc(x[1]) + '</b><br><span class="g-mono">' + esc(t(x[2], x[3])) + "</span></td>" + OS.map(function (s) { return '<td class="c">' + TV((I[s.k] || {})[x[0]]) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody>";
  }
'''
js = rep(js, "\n  /* ---------- XI. downloads ---------- */", ORIG + "\n  /* ---------- XI. downloads ---------- */")
open(os.path.join(OUT, "sea.js"), "w", encoding="utf-8").write(js)

# ---------------------------------------------------------------- data
shutil.copy(os.path.join(HERE, "sea-data.js"), os.path.join(OUT, "sea-data.js"))
shutil.copy(os.path.join(HERE, "sea-i18n.js"), os.path.join(OUT, "sea-i18n.js"))
shutil.copy(os.path.join(HERE, "sea-check.js"), os.path.join(OUT, "sea-check.js"))
COO = os.path.join(ROOT, "countries-of-origin")
shutil.copy(os.path.join(HERE, "oc-sea.js"), os.path.join(COO, "oc-sea.js"))

# Countries of Origin page: load the extension and widen the bilateral matrix
ci = open(os.path.join(COO, "index.html"), encoding="utf-8").read()
if "oc-sea.js" not in ci:
    ci = rep(ci, '<script src="oc-data.js" defer></script>', '<script src="oc-data.js" defer></script>\n<script src="oc-sea.js" defer></script>')
if "sea-check.js" not in ci:
    ci = rep(ci, '<script src="oc-sea.js" defer></script>', '<script src="oc-sea.js" defer></script>\n<script src="/southeast-asia/sea-check.js" defer></script>')
ci = rep(ci, "in eight countries of origin (Indonesia, the Philippines, Vietnam, Nepal, Bangladesh, India, Sri Lanka and Pakistan)",
         "in twelve countries of origin (Indonesia, the Philippines, Vietnam, Myanmar, Cambodia, Laos, Timor-Leste, Nepal, Bangladesh, India, Sri Lanka and Pakistan)", 0, need=False)
open(os.path.join(COO, "index.html"), "w", encoding="utf-8").write(ci)
oj = open(os.path.join(COO, "oc.js"), encoding="utf-8").read()
oj = rep(oj, '"Malaysia", "Japan", "South Korea", "Taiwan", "Hong Kong"];', '"Malaysia", "Thailand", "Singapore", "Japan", "South Korea", "Taiwan", "Hong Kong"];', need=False)
oj = rep(oj, '"South Korea":"Korea Selatan"};', '"South Korea":"Korea Selatan", "Singapore":"Singapura"};', need=False)
OLD_EV = 'esc(c[2]) + "</dd><dt>" + t("Evidence", "Bukti") + "</dt><dd>" + t("S · secondary or statutory citation not yet checked against the official text; coded ", "S · sumber sekunder atau rujukan pasal yang belum diperiksa terhadap teks resmi; dikodekan ") + CODED + "</dd></dl></div>";'
NEW_EV = 'esc(c[2]) + "</dd><dt>" + t("Evidence", "Bukti") + "</dt><dd>" + ocEv(s.k + "." + d.k) + "</dd></dl></div>";'
if "function ocEv" not in oj:
    oj = oj.replace(OLD_EV, NEW_EV, 1)
    oj = oj.replace('  var LV = {', '  function ocEv(id) { var c = G.checked && G.checked[id]; if (!c) return t("S · secondary or statutory citation not yet checked against the official text; coded ", "S · sumber sekunder atau rujukan pasal yang belum diperiksa terhadap teks resmi; dikodekan ") + CODED; return t("P · checked against the official text on ", "P · diperiksa terhadap teks resmi pada ") + G.checked_on + (c === "partly" ? t("; part of the note rests on official guidance, a secondary source or our reading", "; sebagian catatan bersandar pada panduan resmi, sumber sekunder atau tafsiran kami") : ""); }\n  var LV = {', 1)
    oj = oj.replace('evidence:"S", coded:CODED, checked_official_text:""}', 'evidence:(G.checked && G.checked[s.k + "." + d.k]) ? "P" : "S", coded:CODED, checked_official_text:(G.checked && G.checked[s.k + "." + d.k]) ? G.checked_on + " (" + G.checked[s.k + "." + d.k] + ")" : ""}', 1)
    assert "function ocEv" in oj and "ocEv(s.k" in oj
open(os.path.join(COO, "oc.js"), "w", encoding="utf-8").write(oj)

# ---------------------------------------------------------------- shell
h = open(os.path.join(EA, "index.html"), encoding="utf-8").read()
head, rest = h.split("<main", 1)
_, tail = rest.split("</main>", 1)
main = open(os.path.join(HERE, "main.html"), encoding="utf-8").read()
DESC = "Labor law, ASEAN and bilateral instruments for migrant workers in Malaysia, Singapore, Thailand and Brunei, with the emigration law of Indonesia, the Philippines, Vietnam, Myanmar, Cambodia, Laos and Timor-Leste: a codebook, downloadable data and tools to compare."
head = rep(head, "<title>Migrant workers in East Asia · Institute for Migrant Rights</title>", "<title>Migrant workers in Southeast Asia · Institute for Migrant Rights</title>")
head = re.sub(r'<meta name="keywords" content="[^"]*">', '<meta name="keywords" content="Southeast Asia, ASEAN, Malaysia, Singapore, Thailand, Brunei, Indonesia, Philippines, Vietnam, Myanmar, Cambodia, Laos, Timor-Leste, Cebu Declaration, ASEAN Consensus on migrant workers, temporary labor migration programs, plantation workers, farm workers, migrant fishers, domestic workers, empirical legal studies, comparative law, socio-legal studies, legal pluralism, migration law, labor migration, migrant workers’ rights, human rights law, access to justice, Global South, open data, replication data">', head)
head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + DESC + '">', head)
head = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="' + DESC + '">', head)
head = rep(head, '<meta property="og:title" content="Migrant workers in East Asia · Institute for Migrant Rights">', '<meta property="og:title" content="Migrant workers in Southeast Asia · Institute for Migrant Rights">')
head = rep(head, "https://theimr.org/east-asia/", "https://theimr.org/southeast-asia/", 0)
ld = {"@context": "https://schema.org", "@type": "Dataset",
      "name": "Migrant workers in Southeast Asia: migration and labor laws in comparison",
      "alternateName": "IMR Southeast Asia comparative labor dataset",
      "description": "Comparative legal data on migrant workers in Southeast Asia. Destination side: eight worker groups in Malaysia, Singapore, Thailand and Brunei (plantation and farm workers, domestic workers, Work Permit holders, workers under bilateral memoranda, sea fishers) coded on the ten de jure features of the IMR East Asia codebook, with notes, sources and verification status; treaty status; ASEAN, international, importing-state and bilateral instruments; domestic laws with links to official legislation databases; dated legal developments. Origin side: emigration and protection law of Indonesia, the Philippines, Vietnam, Myanmar, Cambodia, Laos and Timor-Leste on the nine features of the IMR Countries of Origin codebook.",
      "url": "https://theimr.org/southeast-asia/", "version": "1.0", "dateModified": "2026-11-13", "inLanguage": ["en", "id"],
      "keywords": ["migrant workers", "Southeast Asia", "ASEAN", "Cebu Declaration", "ASEAN Consensus", "labor law", "plantation workers", "farm workers", "migrant fishers", "ILO C188", "domestic workers", "bilateral labor agreements", "MOU system", "comparative law", "empirical legal studies", "Malaysia", "Singapore", "Thailand", "Brunei", "Indonesia", "Philippines", "Vietnam", "Myanmar", "Cambodia", "Laos", "Timor-Leste", "open data", "replication data"],
      "creator": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": "https://theimr.org/"},
      "publisher": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": "https://theimr.org/"},
      "license": "https://creativecommons.org/licenses/by/4.0/", "isAccessibleForFree": True,
      "spatialCoverage": [{"@type": "Place", "name": n} for n in ["Malaysia", "Singapore", "Thailand", "Brunei", "Indonesia", "Philippines", "Vietnam", "Myanmar", "Cambodia", "Laos", "Timor-Leste"]],
      "temporalCoverage": "1955/2027",
      "variableMeasured": ["coverage by labor statute", "minimum wage", "working time and rest", "changing employer", "freedom of association", "recruitment fees", "social insurance", "complaint channel", "route to long-term residence", "family accompaniment", "treaty status", "ASEAN instruments", "bilateral instruments", "emigration and protection law"],
      "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "name": nm, "contentUrl": "https://theimr.org/southeast-asia/data/" + f} for nm, f in [("Coded cells with notes and sources", "codings.csv"), ("Codebook", "codebook.csv"), ("Treaty status", "treaty-status.csv"), ("Instruments", "instruments.csv"), ("Domestic laws", "domestic-laws.csv"), ("Origin states", "origins.csv"), ("Legal developments", "developments.csv")]]}
head = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>", head, count=1, flags=re.S)
head = head.replace(' aria-current="page"', '')
tail = rep(tail, '<script src="ea-data.js" defer></script>\n<script src="ea.js" defer></script>\n<script src="ea-i18n.js" defer></script>',
           '<script src="/countries-of-origin/oc-data.js" defer></script>\n<script src="/countries-of-origin/oc-sea.js" defer></script>\n<script src="sea-data.js" defer></script>\n<script src="sea-check.js" defer></script>\n<script src="sea.js" defer></script>\n<script src="sea-i18n.js" defer></script>')
tail = rep(tail, '<script src="/assets/stats.js" defer></script>\n', "")
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(head + "<main" + main + "</main>" + tail)

# ---------------------------------------------------------------- static CSVs
subprocess.run(["node", os.path.join(HERE, "gen_csv.js"), ROOT], check=True)
print("built", OUT)
