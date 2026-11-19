/* Migrant workers in Southeast Asia: renders the page from window.SEA (sea-data.js) and, for the origin section, window.OC (Countries of Origin data). Engine adapted from ea.js. EN/ID follows the site language switch. */
(function () {
  "use strict";
  var G = window.SEA || {};
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); };
  var ID = function () { return document.documentElement.lang === "id"; };
  var t = function (en, id) { return ID() && id ? id : en; };
  var fmt = function (n) { return n == null ? "" : Number(n).toLocaleString(ID() ? "id-ID" : "en-GB"); };
  var S = G.states || [], GR = G.groups || [], CB = G.codebook || [];
  var stateOf = function (k) { return S.filter(function (x) { return x.k === k; })[0]; };
  var sname = function (k) { if (k === "ASEAN") return t("All ASEAN members", "Semua anggota ASEAN"); var s = stateOf(k); return s ? t(s.n, s.n_id) : k; };
  var CODED = "2026-11-13";
  function ev(id) { return (G.checked && G.checked[id]) ? "P" : "S"; }
  function evText(id) {
    var c = G.checked && G.checked[id];
    if (!c) return t("S · secondary or statutory citation not yet checked against the official text; coded ", "S · sumber sekunder atau rujukan pasal yang belum diperiksa terhadap teks resmi; dikodekan ") + CODED;
    return c === "partly"
      ? t("P · checked against the official text on ", "P · diperiksa terhadap teks resmi pada ") + G.checked_on + t("; part of the note rests on a secondary source, on official ministry or agency guidance, or on our reading", "; sebagian catatan bersandar pada sumber sekunder, panduan resmi kementerian atau lembaga, atau tafsiran kami")
      : t("P · checked against the official text on ", "P · diperiksa terhadap teks resmi pada ") + G.checked_on;
  }

  var LV = {2:["yes", "Full", "Penuh"], 1:["partial", "Partial", "Sebagian"], 0:["no", "None", "Tidak ada"]};
  function vline() { var n = 0, p = 0; GR.forEach(function (g) { CB.forEach(function (d) { n++; if (G.checked && G.checked[g.k + "." + d.k]) p++; }); });
    return p ? t(p + " of " + n + " cells have been checked against the official legal texts (P); the others rest on secondary sources and statutory citations (S). See Method.", p + " dari " + n + " sel telah diperiksa terhadap teks hukum resmi (P); sisanya bersandar pada sumber sekunder dan rujukan pasal (S). Lihat Metode.")
      : t("All " + n + " cells rest on secondary sources and statutory citations (S) until the check against the official legal texts is complete. See Method.", "Seluruh " + n + " sel bersandar pada sumber sekunder dan rujukan pasal (S) sampai pemeriksaan terhadap teks hukum resmi selesai. Lihat Metode."); }
  function pill(v) { var x = LV[v] || ["unclear", "Unclear", "Belum jelas"]; return '<span class="g-pill p-' + x[0] + '">' + esc(t(x[1], x[2])) + "</span>"; }
  function level(d, v) { return t(d["l" + v], d["l" + v + "_id"]); }

  /* ---------- I. at a glance ---------- */
  var sel = null;
  function glance() {
    var h = "<thead><tr><th>" + t("Worker group", "Kelompok pekerja") + "</th>" + CB.map(function (d) { return "<th>" + esc(t(d.en, d.id)) + "</th>"; }).join("") + "</tr></thead><tbody>";
    GR.forEach(function (g) {
      h += "<tr><td><b>" + esc(t(g.n, g.n_id)) + "</b>" + (g.flagship ? ' <span class="g-mono">· ' + t("focus", "fokus") + "</span>" : "") + "</td>" + CB.map(function (d) {
        var c = g.codes[d.k] || [], on = sel && sel[0] === g.k && sel[1] === d.k;
        return '<td class="c"><button type="button" class="g-cell" data-g="' + g.k + '" data-d="' + d.k + '" aria-pressed="' + !!on + '" title="' + esc(c[1] || "") + '">' + pill(c[0]) + "</button></td>";
      }).join("") + "</tr>";
    });
    $("g-glance").innerHTML = h + "</tbody>";
    $("g-glance").onclick = function (e) { var b = e.target.closest("[data-g]"); if (!b) return; sel = [b.getAttribute("data-g"), b.getAttribute("data-d")]; glance(); };
    $("g-legend").innerHTML = [2, 1, 0].map(function (v) { return pill(v); }).join(" ") + ' <span class="g-mono">' + t("Coded on the law as written (de jure). Select any cell for its rule, note and source.", "Dikodekan menurut hukum tertulis (de jure). Pilih sel mana pun untuk melihat aturan, catatan dan sumbernya.") + "</span>";
    var box = $("g-cellnote");
    if (!sel) { box.innerHTML = ""; return; }
    var g = GR.filter(function (x) { return x.k === sel[0]; })[0], d = CB.filter(function (x) { return x.k === sel[1]; })[0], c = g.codes[d.k];
    box.innerHTML = '<div class="g-card"><h3>' + esc(t(g.n, g.n_id)) + " · " + esc(t(d.en, d.id)) + "</h3><dl class=\"g-dl\"><dt>" + t("Value", "Nilai") + "</dt><dd>" + pill(c[0]) + " " + esc(level(d, c[0])) + "</dd><dt>" + t("Note", "Catatan") + "</dt><dd>" + esc(c[1]) + "</dd><dt>" + t("Source", "Sumber") + "</dt><dd>" + esc(c[2]) + "</dd><dt>" + t("Evidence", "Bukti") + "</dt><dd>" + evText(g.k + "." + d.k) + "</dd></dl></div>";
  }

  /* ---------- II. compare ---------- */
  var W = {}; CB.forEach(function (d) { W[d.k] = 0; });
  function score(g, w) { var tot = 0, max = 0; CB.forEach(function (d) { var v = (g.codes[d.k] || [])[0]; tot += w[d.k] * (v == null ? 0 : v); max += w[d.k] * 2; }); return max ? 100 * tot / max : 0; }
  function weights() {
    $("g-weights").innerHTML = CB.map(function (d) {
      return '<label>' + esc(t(d.en, d.id)) + ' <output id="w-' + d.k + '">' + W[d.k] + '</output><input type="range" min="0" max="3" step="1" value="' + W[d.k] + '" data-w="' + d.k + '" aria-label="' + esc(t(d.en, d.id)) + '"></label>';
    }).join("");
  }
  function rank() {
    if (!CB.some(function (d) { return W[d.k] > 0; })) { $("g-rank").innerHTML = '<p class="g-empty">' + t("Set a weight above to see a weighted comparison.", "Atur bobot di atas untuk melihat perbandingan tertimbang.") + "</p>"; $("g-rank-note").textContent = ""; return; }
    var R = GR.map(function (g) { return {g:g, v:score(g, W)}; }).sort(function (a, b) { return b.v - a.v; });
    $("g-rank").innerHTML = R.map(function (r) {
      return '<div class="g-bar"><span>' + esc(t(r.g.n, r.g.n_id)) + '</span><span class="tr"><span class="fl" style="width:' + r.v.toFixed(1) + '%"></span></span><span class="v">' + r.v.toFixed(0) + "/100</span></div>";
    }).join("");
    $("g-rank-note").textContent = t("Score = weighted share of the maximum possible (each feature 0, 1 or 2). It describes the law on paper, not how it is enforced.", "Skor = bagian tertimbang dari nilai maksimum (setiap fitur 0, 1 atau 2). Skor menggambarkan hukum tertulis, bukan penegakannya.");
  }
  var ROB = null;
  function robust() {
    if (!ROB) {
      var N = 10000, seed = 20261031, rnd = function () { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };
      ROB = GR.map(function () { return {first:0, rank:0}; });
      for (var i = 0; i < N; i++) {
        var w = {}; CB.forEach(function (d) { w[d.k] = 3 * rnd(); });
        var sc = GR.map(function (g, j) { return [j, score(g, w)]; }).sort(function (a, b) { return b[1] - a[1]; });
        sc.forEach(function (x, r) { ROB[x[0]].rank += r + 1; }); ROB[sc[0][0]].first++;
      }
      ROB.forEach(function (x) { x.first /= N; x.rank /= N; });
    }
    var o = GR.map(function (g, j) { return [g, ROB[j]]; }).sort(function (a, b) { return a[1].rank - b[1].rank; });
    $("g-robust").innerHTML = "<thead><tr><th>" + t("Worker group", "Kelompok pekerja") + "</th><th>" + t("Highest score in", "Skor tertinggi pada") + "</th><th>" + t("Mean position (1 = highest)", "Posisi rata-rata (1 = tertinggi)") + "</th></tr></thead><tbody>" +
      o.map(function (r) { return "<tr><td>" + esc(t(r[0].n, r[0].n_id)) + '</td><td class="c g-mono">' + (100 * r[1].first).toFixed(1) + '%</td><td class="c g-mono">' + r[1].rank.toFixed(2) + "</td></tr>"; }).join("") + "</tbody>";
  }

  /* ---------- III. profiles ---------- */
  var TV = function (v) {
    if (!v) return pill(0).replace(esc(t("None", "Tidak ada")), esc(t("Not bound", "Tidak terikat")));
    if (v === "?") return '<span class="g-pill p-unclear">' + t("Unclear", "Belum jelas") + "</span>";
    var y = (v.match(/\d{4}/) || [""])[0];
    if (v[0] === "p") return '<span class="g-pill p-yes">' + t("Party ", "Pihak ") + y + "</span>";
    if (v[0] === "a") return '<span class="g-pill p-yes">' + t("Applies", "Berlaku") + (y ? " " + y : "") + "</span>";
    if (v[0] === "d") return '<span class="g-pill p-partial">' + t("Domestic law ", "UU domestik ") + y + "</span>";
    return '<span class="g-pill p-partial">' + t("Partly aligned", "Sebagian selaras") + "</span>";
  };
  function intlTable() {
    var T = G.treaties || [];
    $("g-intl").innerHTML = "<thead><tr><th>" + t("Instrument", "Instrumen") + "</th>" + S.map(function (s) { return "<th>" + esc(t(s.n, s.n_id)) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      T.map(function (x) { return "<tr><td><b>" + esc(x[1]) + '</b><br><span class="g-mono">' + esc(t(x[2], x[3])) + "</span></td>" + S.map(function (s) { return '<td class="c">' + TV((G.intl[s.k] || {})[x[0]]) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody>";
    $("g-intlnote").textContent = t(G.intl_note, G.intl_note_id);
  }
  var curP = (location.hash.match(/^#profile-(\w\w)$/) || [])[1] || "MY";
  function stateBtns(el, cur, cb) {
    el.innerHTML = S.map(function (s) { return '<button type="button" class="g-btn" data-s="' + s.k + '" aria-pressed="' + (s.k === cur) + '">' + esc(t(s.n, s.n_id)) + "</button>"; }).join("");
    el.onclick = function (e) { var b = e.target.closest("[data-s]"); if (b) cb(b.getAttribute("data-s")); };
  }
  function profile() {
    stateBtns($("g-states"), curP, function (k) { curP = k; profile(); });
    var s = stateOf(curP); if (!s) return;
    var A = (G.advocacy || {})[s.k] || {};
    var gs = GR.filter(function (g) { return g.s === s.k; });
    var F = (G.frameworks || []).filter(function (a) { return a.s === s.k || a.s === "ASEAN"; });
    var rows = [
      [t("Focus of this page", "Fokus halaman ini"), esc(t(s.focus, s.focus_id))],
      [t("Main legislation", "Peraturan utama"), esc(s.law)],
      [t("International status", "Status internasional"), esc(t(s.status, s.status_id))],
      [t("Worker groups coded", "Kelompok pekerja yang dikodekan"), gs.map(function (g) { return "<b>" + esc(t(g.n, g.n_id)) + "</b><br>" + esc(t(g.basis, g.basis_id)) + (g.size && g.size[0] ? '<br><span class="g-mono">' + t("About ", "Sekitar ") + fmt(g.size[0]) + " (" + esc(g.size[1]) + "; " + esc(g.size[2]) + ")</span>" : ""); }).join("<br><br>")],
      [t("Where to complain", "Tempat mengadu"), esc(t(s.complaints, s.complaints_id))],
      [t("Instruments on record", "Instrumen tercatat"), fmt(F.length) + ' · <a href="#agreements" data-fs="' + s.k + '">' + t("see the list", "lihat daftar") + "</a>"]
    ];
    var adv = "";
    if (A.args) adv += '<h4 class="g-h4">' + t("Arguments the law opens", "Argumen yang dibuka oleh hukum") + "</h4><ul>" + A.args.map(function (x) { return "<li>" + esc(t(x[0], x[1])) + "</li>"; }).join("") + "</ul>";
    if (A.avenues) adv += '<h4 class="g-h4">' + t("Avenues", "Jalur") + "</h4><ul>" + A.avenues.map(function (x) { return "<li>" + esc(t(x[0], x[1])) + "</li>"; }).join("") + "</ul>";
    $("g-profile").innerHTML = '<div class="g-card" id="profile-' + s.k + '"><h3>' + esc(t(s.n, s.n_id)) + '</h3><dl class="g-dl">' + rows.map(function (r) { return "<dt>" + r[0] + "</dt><dd>" + r[1] + "</dd>"; }).join("") + "</dl>" +
      (adv ? '<div class="g-adv">' + adv + "</div>" : "") +
      '<div class="g-acts"><a href="/legal-help/?country=' + s.k + '">' + t("Free legal help in ", "Bantuan hukum gratis di ") + esc(t(s.n, s.n_id)) + '</a><a href="/legal-clinic/?country=' + s.iso3 + '">' + t("Draft a rights communication", "Susun pengaduan hak") + '</a><a href="#" id="g-print">' + t("Print a one-page brief", "Cetak ringkasan satu halaman") + "</a></div>" +
      '<p class="g-note">' + vline() + "</p></div>";
    var a = $("g-profile").querySelector("[data-fs]"); if (a) a.onclick = function () { AF.s = s.k; AF.level = ""; AF.nature = ""; agreements(); };
    $("g-print").onclick = function (e) { e.preventDefault(); window.print(); };
  }

  /* ---------- IV. people and jobs ---------- */
  var curD = "MY";
  function demog() {
    stateBtns($("g-dstates"), curD, function (k) { curD = k; demog(); });
    var D = (G.demog || {})[curD];
    if (!D) { $("g-demog").innerHTML = '<p class="g-empty">' + t("Figures for this state are being compiled.", "Data negara ini sedang dihimpun.") + "</p>"; return; }
    var mx = Math.max.apply(null, D.rows.map(function (r) { return r[2]; }));
    $("g-demog").innerHTML = '<div class="g-bars">' + D.rows.map(function (r) {
      var hi = /fish|crew|nelayan|awak/i.test(r[0]);
      return '<div class="g-bar"><span>' + esc(t(r[0], r[1])) + ' <span class="g-mono">' + esc(r[3]) + '</span></span><span class="tr"><span class="fl' + (hi ? " hi" : "") + '" style="width:' + Math.max(0.6, 100 * r[2] / mx).toFixed(1) + '%"></span></span><span class="v">' + fmt(r[2]) + "</span></div>";
    }).join("") + '</div><p class="g-note">' + esc(t(D.note, D.note_id)) + "</p>";
  }

  /* ---------- V. frameworks ---------- */
  var LEVELS = [["international", "International", "Internasional"], ["regional", "Regional (ASEAN)", "Regional (ASEAN)"], ["market", "Importing-state measures", "Kebijakan negara pengimpor"], ["bilateral", "Bilateral", "Bilateral"]];
  var NATURES = [["treaty", "Binding treaty", "Traktat mengikat"], ["domestic", "Domestic incorporation", "Penerapan domestik"], ["measure", "Binding measure or regulation", "Ketentuan atau regulasi mengikat"], ["listing", "Listing or trade sanction", "Daftar atau sanksi dagang"], ["agreement", "Agreement or arrangement", "Perjanjian atau pengaturan"], ["mou", "Memorandum of understanding", "Nota kesepahaman"], ["declaration", "Declaration or consensus (non-binding)", "Deklarasi atau konsensus (tidak mengikat)"]];
  var lname = function (arr, k) { var x = arr.filter(function (a) { return a[0] === k; })[0]; return x ? t(x[1], x[2]) : k; };
  var AF = {s:"", level:"", nature:"", q:""};
  function amap() {
    var F = (G.frameworks || []).filter(function (a) { return !AF.s || a.s === AF.s || a.s === "ASEAN"; });
    var h = "<thead><tr><th>" + t("Level ↓ / nature →", "Tingkat ↓ / sifat →") + "</th>" + NATURES.map(function (n) { return "<th>" + esc(t(n[1], n[2])) + "</th>"; }).join("") + "<th>" + t("Total", "Jumlah") + "</th></tr></thead><tbody>";
    LEVELS.forEach(function (l) {
      var row = F.filter(function (a) { return a.level === l[0]; });
      h += "<tr><td><b>" + esc(t(l[1], l[2])) + "</b></td>" + NATURES.map(function (n) {
        var c = row.filter(function (a) { return a.nature === n[0]; }).length, on = AF.level === l[0] && AF.nature === n[0];
        return '<td class="c">' + (c ? '<button type="button" class="g-btn" style="min-height:36px;padding:0 12px" aria-pressed="' + on + '" data-l="' + l[0] + '" data-n="' + n[0] + '">' + c + "</button>" : '<span class="g-mono">0</span>') + "</td>";
      }).join("") + '<td class="c"><button type="button" class="g-btn" style="min-height:36px;padding:0 12px" aria-pressed="' + (AF.level === l[0] && !AF.nature) + '" data-l="' + l[0] + '" data-n="">' + row.length + "</button></td></tr>";
    });
    $("g-amap").innerHTML = h + "</tbody>";
    $("g-amap").onclick = function (e) { var b = e.target.closest("[data-l]"); if (!b) return; var l = b.getAttribute("data-l"), n = b.getAttribute("data-n"); if (AF.level === l && AF.nature === n) { AF.level = ""; AF.nature = ""; } else { AF.level = l; AF.nature = n; } agreements(); };
  }
  function atools() {
    var so = '<option value="">' + t("All four", "Keempatnya") + "</option>" + S.map(function (s) { return '<option value="' + s.k + '"' + (AF.s === s.k ? " selected" : "") + ">" + esc(t(s.n, s.n_id)) + "</option>"; }).join("");
    var lo = '<option value="">' + t("All levels", "Semua tingkat") + "</option>" + LEVELS.map(function (l) { return '<option value="' + l[0] + '"' + (AF.level === l[0] ? " selected" : "") + ">" + esc(t(l[1], l[2])) + "</option>"; }).join("");
    var no = '<option value="">' + t("All kinds", "Semua jenis") + "</option>" + NATURES.map(function (n) { return '<option value="' + n[0] + '"' + (AF.nature === n[0] ? " selected" : "") + ">" + esc(t(n[1], n[2])) + "</option>"; }).join("");
    $("g-atools").innerHTML = '<div><label for="af-s">' + t("Destination", "Negara tujuan") + '</label><select id="af-s">' + so + '</select></div><div><label for="af-l">' + t("Level", "Tingkat") + '</label><select id="af-l">' + lo + '</select></div><div><label for="af-n">' + t("Nature", "Sifat") + '</label><select id="af-n">' + no + '</select></div><div><label for="af-q">' + t("Search", "Cari") + '</label><input id="af-q" type="search" value="' + esc(AF.q) + '" placeholder="' + t("Partner or title", "Mitra atau judul") + '"></div>';
    $("af-s").onchange = function () { AF.s = this.value; agreements(); };
    $("af-l").onchange = function () { AF.level = this.value; agreements(); };
    $("af-n").onchange = function () { AF.nature = this.value; agreements(); };
    $("af-q").oninput = function () { AF.q = this.value; alist(); };
  }
  function alist() {
    var q = AF.q.toLowerCase(), all = G.frameworks || [];
    var R = all.filter(function (a) { return (!AF.s || a.s === AF.s || a.s === "ASEAN") && (!AF.level || a.level === AF.level) && (!AF.nature || a.nature === AF.nature) && (!q || (a.partner + " " + a.title + " " + (a.scope || "")).toLowerCase().indexOf(q) >= 0); });
    $("g-acount").textContent = fmt(R.length) + t(" of ", " dari ") + fmt(all.length) + t(" instruments", " instrumen");
    $("g-atable").innerHTML = "<thead><tr><th>" + t("Destination", "Negara tujuan") + "</th><th>" + t("Partner", "Mitra") + "</th><th>" + t("Instrument", "Instrumen") + "</th><th>" + t("Level", "Tingkat") + "</th><th>" + t("Nature", "Sifat") + "</th><th>" + t("Adopted", "Diadopsi") + "</th><th>" + t("In force / ended", "Berlaku / berakhir") + "</th></tr></thead><tbody>" +
      R.map(function (a) { return '<tr><td class="c">' + esc(sname(a.s)) + "</td><td>" + esc(a.partner) + "</td><td>" + esc(a.title) + (a.scope ? '<br><span class="g-mono">' + esc(a.scope) + "</span>" : "") + '</td><td class="c">' + esc(lname(LEVELS, a.level)) + "</td><td>" + esc(lname(NATURES, a.nature)) + '</td><td class="c g-mono">' + esc(a.signed || "") + '</td><td class="c g-mono">' + esc(a.in_force || "") + "</td></tr>"; }).join("") + "</tbody>";
  }
  function memos() {
    $("g-memos").innerHTML = (G.memos || []).map(function (m) { return "<p><b>" + esc(t(m[0], m[1])) + "</b>: " + esc(t(m[2], m[3])) + "</p>"; }).join("");
  }
  function agreements() { amap(); atools(); alist(); }


  /* ---------- V b. domestic laws ---------- */
  var LTYPE = {constitution:["Constitution","Konstitusi"], statute:["Statute","Undang-undang"], regulation:["Regulation","Peraturan"], contract:["Standard contract","Kontrak standar"], policy:["Policy","Kebijakan"]};
  var LF = {s:"", type:"", q:""};
  function laws() {
    var L = G.laws || [];
    var so = '<option value="">' + t("All four", "Keempatnya") + "</option>" + S.map(function (s) { return '<option value="' + s.k + '"' + (LF.s === s.k ? " selected" : "") + ">" + esc(t(s.n, s.n_id)) + "</option>"; }).join("");
    var to = '<option value="">' + t("All types", "Semua jenis") + "</option>" + Object.keys(LTYPE).map(function (k) { return '<option value="' + k + '"' + (LF.type === k ? " selected" : "") + ">" + esc(t(LTYPE[k][0], LTYPE[k][1])) + "</option>"; }).join("");
    $("g-ltools").innerHTML = '<div><label for="lf-s">' + t("Jurisdiction", "Yurisdiksi") + '</label><select id="lf-s">' + so + '</select></div><div><label for="lf-t">' + t("Type", "Jenis") + '</label><select id="lf-t">' + to + '</select></div><div style="grid-column:span 2"><label for="lf-q">' + t("Search", "Cari") + '</label><input id="lf-q" type="search" value="' + esc(LF.q) + '" placeholder="' + t("Title, topic or original title", "Judul, topik atau judul asli") + '"></div>';
    $("lf-s").onchange = function () { LF.s = this.value; laws(); };
    $("lf-t").onchange = function () { LF.type = this.value; laws(); };
    $("lf-q").oninput = function () { LF.q = this.value; lawList(); };
    lawList();
  }
  function lawList() {
    var L = G.laws || [], q = LF.q.toLowerCase();
    var R = L.filter(function (x) { return (!LF.s || x.s === LF.s) && (!LF.type || x.type === LF.type) && (!q || (x.title + " " + x.orig + " " + x.topic).toLowerCase().indexOf(q) >= 0); });
    $("g-lcount").textContent = fmt(R.length) + t(" of ", " dari ") + fmt(L.length) + t(" laws and instruments", " hukum dan instrumen");
    $("g-ltable").innerHTML = "<thead><tr><th>" + t("Jurisdiction", "Yurisdiksi") + "</th><th>" + t("Title", "Judul") + "</th><th>" + t("Type", "Jenis") + "</th><th>" + t("Adopted", "Diadopsi") + "</th><th>" + t("Last amended", "Perubahan terakhir") + "</th><th>" + t("Relevance", "Relevansi") + "</th><th>" + t("Official text", "Teks resmi") + "</th></tr></thead><tbody>" +
      R.map(function (x) { return '<tr><td class="c">' + esc(sname(x.s)) + "</td><td><b>" + esc(x.title) + "</b>" + (x.orig ? '<br><span class="g-mono" lang="' + ({MY:"ms", BN:"ms", TH:"th", SG:"en"}[x.s] || "und") + '">' + esc(x.orig) + "</span>" : "") + "</td><td>" + esc(t(LTYPE[x.type][0], LTYPE[x.type][1])) + '</td><td class="c g-mono">' + esc(x.year) + '</td><td class="c g-mono">' + esc(x.amended || "") + "</td><td>" + esc(x.topic) + '</td><td class="c"><a href="' + esc(x.url) + '" rel="noopener">' + (x.link === "text" ? t("Read the text", "Baca teks") : t("Official database", "Basis data resmi")) + "</a></td></tr>"; }).join("") + "</tbody>";
  }

  /* ---------- VI. corridors ---------- */
  var curC = "MY";
  function corridors() {
    stateBtns($("g-cstates"), curC, function (k) { curC = k; corridors(); });
    var R = (G.stock || []).filter(function (r) { return r.s === curC; }).sort(function (a, b) { return b.v - a.v; });
    if (!R.length) { $("g-corr").innerHTML = '<p class="g-empty">' + t("Corridor figures are being compiled.", "Data koridor sedang dihimpun.") + "</p>"; return; }
    var mx = R[0].v;
    $("g-corr").innerHTML = '<p class="g-mono" style="margin:0 0 6px">' + esc(R[0].pop) + " · " + esc(R[0].y) + "</p>" + R.map(function (r) {
      var n = (G.frameworks || []).filter(function (a) { return a.s === curC && a.level === "bilateral" && a.partner === r.o; }).length + (curC === "KR" && (G.eps || []).indexOf(r.o) >= 0 ? 1 : 0) + (curC === "JP" && (G.ssw || []).some(function (x) { return x[0] === r.o; }) ? 1 : 0);
      return '<div class="g-bar"><span>' + esc(r.o) + (n ? ' <span class="g-mono">· ' + n + "</span>" : "") + '</span><span class="tr"><span class="fl' + (n ? " hi" : "") + '" style="width:' + (100 * r.v / mx).toFixed(1) + '%"></span></span><span class="v">' + (r.v >= 1e6 ? (r.v / 1e6).toFixed(1) + "M" : r.v >= 1e4 ? Math.round(r.v / 1e3) + "k" : fmt(r.v)) + "</span></div>";
    }).join("") + '<p class="g-note">' + t("Source: ", "Sumber: ") + ((G.stock_src || {})[curC] || []).map(function (x) { return '<a href="' + esc(x[1]) + '">' + esc(x[0]) + "</a>"; }).join("; ") + ". " + t("A red bar and number mark bilateral instruments on record. Each state counts a different population, so compare within a state, not across.", "Batang merah dan angka menandai instrumen bilateral yang tercatat. Setiap negara menghitung populasi yang berbeda, jadi bandingkan di dalam satu negara, bukan antarnegara.") + "</p>";
  }

  /* ---------- VII. explore ---------- */
  var ICRMW = {Philippines:1995, "Sri Lanka":1996, Indonesia:2012, Bangladesh:2011};
  function corrRows() {
    return (G.stock || []).filter(function (r) { return r.o !== "Others"; }).map(function (r) {
      var bil = (G.frameworks || []).some(function (a) { return a.s === r.s && a.level === "bilateral" && a.partner === r.o; }) || (r.s === "KR" && (G.eps || []).indexOf(r.o) >= 0) || (r.s === "JP" && (G.ssw || []).some(function (x) { return x[0] === r.o; }));
      return {id: r.o + " → " + sname(r.s), destination: sname(r.s), origin: r.o, workers: r.v, log_workers: Math.log10(r.v), bilateral: bil ? 1 : 0, origin_icrmw: ICRMW[r.o] ? 1 : 0, population: r.pop, year: r.y};
    });
  }
  function stats() {
    if (!window.IMRStats) return;
    IMRStats.mount($("g-stats"), {
      rows: corrRows(), filename: "imr-southeast-asia-corridors", idLabel: "corridor",
      vars: [
        {key:"workers", type:"num", label:"Workers in the corridor", label_id:"Pekerja di koridor", log:true},
        {key:"bilateral", type:"bin", label:"Bilateral instrument on record", label_id:"Ada instrumen bilateral", yes:"Instrument", no:"None", yes_id:"Ada instrumen", no_id:"Tidak ada"},
        {key:"origin_icrmw", type:"bin", label:"Origin is party to the UN migrant workers convention", label_id:"Negara asal pihak Konvensi Pekerja Migran PBB", yes:"Party", no:"Not party", yes_id:"Pihak", no_id:"Bukan pihak"},
        {key:"destination", type:"cat", label:"Destination", label_id:"Negara tujuan"}
      ],
      presets: [
        {q:"Do corridors with a bilateral instrument carry more workers?", q_id:"Apakah koridor dengan instrumen bilateral membawa lebih banyak pekerja?", mode:0, y:"workers", g:"bilateral"},
        {q:"The same, controlling for the destination", q_id:"Sama, dengan mengontrol negara tujuan", mode:2, ry:"workers", preds:["bilateral", "destination"]},
        {q:"Are origins that ratified the migrant workers convention more often covered by an instrument?", q_id:"Apakah negara asal yang meratifikasi Konvensi Pekerja Migran lebih sering tercakup instrumen?", mode:0, y:"bilateral", g:"origin_icrmw"}
      ],
      defaults: {y:"workers", g:"bilateral", x:"workers", y2:"bilateral", preds:["bilateral", "destination"]},
      note: "Each row is an origin–destination corridor. Destinations count different populations (all workers, helpers, crew), so models should include the destination. Rows within one destination are not independent, and n is small: read every p-value as descriptive.",
      note_id: "Setiap baris adalah satu koridor asal–tujuan. Negara tujuan menghitung populasi yang berbeda, jadi model sebaiknya memasukkan negara tujuan. Baris dalam satu negara tujuan tidak independen dan n kecil: baca setiap nilai p sebagai deskriptif."
    });
  }

  /* ---------- VIII. developments ---------- */
  var RF = "";
  var KIND = {real:["Change in rights", "Perubahan hak"], partial:["Partial or limited", "Sebagian atau terbatas"], law:["New law or ratification", "Hukum atau ratifikasi baru"], market:["Importing-state measure", "Kebijakan negara pengimpor"], origin:["Sending-state or bilateral", "Negara pengirim atau bilateral"], cut:["Reduction in protection", "Pengurangan perlindungan"]};
  function reforms() {
    $("g-rfilter").innerHTML = '<button type="button" class="g-btn" data-r="" aria-pressed="' + (RF === "") + '">' + t("All", "Semua") + "</button>" + S.map(function (s) { return '<button type="button" class="g-btn" data-r="' + s.k + '" aria-pressed="' + (RF === s.k) + '">' + esc(t(s.n, s.n_id)) + "</button>"; }).join("");
    $("g-rfilter").onclick = function (e) { var b = e.target.closest("[data-r]"); if (b) { RF = b.getAttribute("data-r"); reforms(); } };
    var MO = ID() ? ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"] : ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    $("g-tl").innerHTML = (G.reforms || []).filter(function (r) { return !RF || r[1] === RF; }).map(function (r) {
      var d = r[0].split("-"), cls = r[4] === "market" ? "origin" : r[4] === "origin" || r[4] === "cut" ? "" : r[4];
      return '<li class="' + cls + '"><span class="d">' + MO[+d[1] - 1] + " " + d[0] + " · " + esc(sname(r[1])) + " · " + esc(t(KIND[r[4]][0], KIND[r[4]][1])) + "</span><br>" + esc(t(r[2], r[3])) + "</li>";
    }).join("");
    $("g-tlleg").innerHTML = '<span class="g-mono">' + t("Green: change in rights · amber: partial · red: importing-state measure · open: law, ratification or bilateral step. Dates in the future are scheduled.", "Hijau: perubahan hak · kuning: sebagian · merah: kebijakan negara pengimpor · kosong: hukum, ratifikasi atau langkah bilateral. Tanggal di masa depan adalah jadwal.") + "</span>";
  }

  /* ---------- IX. method ---------- */
  function provRows() {
    var out = [];
    GR.forEach(function (g) { CB.forEach(function (d) { var c = g.codes[d.k] || []; out.push({group:g.k, group_name:g.n, state:g.s, feature:d.k, feature_name:d.en, value:c[0], value_label:d["l" + c[0]], note:c[1], source:c[2], evidence:ev(g.k + "." + d.k), coded:CODED, checked_official_text:(G.checked && G.checked[g.k + "." + d.k]) ? G.checked_on + " (" + G.checked[g.k + "." + d.k] + ")" : ""}); }); });
    return out;
  }
  function method() {
    $("g-codebook").innerHTML = "<thead><tr><th>" + t("Feature", "Fitur") + "</th><th>2</th><th>1</th><th>0</th></tr></thead><tbody>" +
      CB.map(function (d) { return "<tr><td><b>" + esc(t(d.en, d.id)) + "</b></td><td>" + esc(level(d, 2)) + "</td><td>" + esc(level(d, 1)) + "</td><td>" + esc(level(d, 0)) + "</td></tr>"; }).join("") + "</tbody>";
    var P = provRows(), nS = P.filter(function (r) { return r.evidence === "S"; }).length;
    $("g-prov").innerHTML = "<thead><tr><th>" + t("Cells coded", "Sel dikodekan") + "</th><th>" + t("Primary text (P)", "Teks primer (P)") + "</th><th>" + t("Secondary (S)", "Sekunder (S)") + "</th><th>" + t("Coded", "Dikodekan") + "</th><th>" + t("Second coding", "Pengodean kedua") + "</th></tr></thead><tbody><tr><td class=\"c g-mono\">" + P.length + '</td><td class="c g-mono">' + (P.length - nS) + '</td><td class="c g-mono">' + nS + '</td><td class="c g-mono">' + CODED + '</td><td class="c g-mono">' + t("planned (Cohen's κ)", "direncanakan (κ Cohen)") + "</td></tr></tbody>";
    var y = "2026", apa = "Institute for Migrant Rights. (" + y + "). Migrant workers in Southeast Asia: Migration and labor laws in comparison (Version " + G.version + ", " + G.updated + ") [Data set and overview]. https://theimr.org/southeast-asia/";
    var bib = "@misc{imr_southeastasia_" + y + ",\n  author = {{Institute for Migrant Rights}},\n  title = {Migrant Workers in Southeast Asia, Migration Jurisprudence from the South},\n  year = {" + y + "},\n  version = {" + G.version + "},\n  note = {Data set and overview, updated " + G.updated + "},\n  url = {https://theimr.org/southeast-asia/}\n}";
    if (!$("g-cite")) return; // the static "How to cite" block (tools/cite_blocks.py) replaced this
    $("g-cite").innerHTML = '<p style="margin:0 0 10px">' + esc(apa) + '</p><pre class="g-mono" style="white-space:pre-wrap;background:#F4F1EE;border:1px solid #C8BCB1;padding:12px;margin:0">' + esc(bib) + '</pre><div class="g-btns" style="margin-top:10px"><button type="button" class="g-btn" id="g-cp1">' + t("Copy citation", "Salin sitasi") + '</button><button type="button" class="g-btn" id="g-cp2">' + t("Copy BibTeX", "Salin BibTeX") + "</button></div>";
    var cp = function (txt, b) { try { navigator.clipboard.writeText(txt); b.textContent = t("Copied", "Tersalin"); } catch (e) {} };
    $("g-cp1").onclick = function () { cp(apa, this); }; $("g-cp2").onclick = function () { cp(bib, this); };
  }

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

  /* ---------- XI. downloads ---------- */
  function csv(rows, cols) { return cols.join(",") + "\n" + rows.map(function (r) { return cols.map(function (c) { var v = r[c] == null ? "" : String(r[c]); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }).join(","); }).join("\n"); }
  function save(name, text, type) { var b = new Blob([text], {type: type}), a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = name; document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500); }
  function sources() {
    var v = "-v" + G.version;
    var D = [["cd", t("Coded cells with sources (CSV)", "Sel terkode dengan sumber (CSV)")], ["cb", t("Codebook (CSV)", "Buku kode (CSV)")], ["it", t("Treaty status (CSV)", "Status traktat (CSV)")], ["fw", t("Instruments (CSV)", "Instrumen (CSV)")], ["lw", t("Domestic laws (CSV)", "Hukum domestik (CSV)")], ["or", t("Origin states (CSV)", "Negara asal (CSV)")], ["rf", t("Legal developments (CSV)", "Perkembangan hukum (CSV)")], ["js", t("Everything (JSON)", "Semua (JSON)")]];
    $("g-dls").innerHTML = D.map(function (d) { return '<button type="button" class="g-btn dl" data-d="' + d[0] + '">' + esc(d[1]) + "</button>"; }).join("");
    $("g-dls").onclick = function (e) {
      var b = e.target.closest("[data-d]"); if (!b) return; var k = b.getAttribute("data-d");
      if (k === "cd") save("imr-southeast-asia-codings" + v + ".csv", csv(provRows(), ["group", "group_name", "state", "feature", "feature_name", "value", "value_label", "note", "source", "evidence", "coded", "checked_official_text"]), "text/csv");
      if (k === "cb") save("imr-southeast-asia-codebook" + v + ".csv", csv(CB, ["k", "en", "l2", "l1", "l0"]), "text/csv");
      if (k === "it") save("imr-southeast-asia-treaties" + v + ".csv", csv((G.treaties || []).map(function (x) { var r = {instrument:x[1]}; S.forEach(function (s) { r[s.k] = (G.intl[s.k] || {})[x[0]]; }); return r; }), ["instrument"].concat(S.map(function (s) { return s.k; }))), "text/csv");
      if (k === "fw") save("imr-southeast-asia-instruments" + v + ".csv", csv(G.frameworks || [], ["s", "partner", "title", "level", "nature", "signed", "in_force", "scope"]), "text/csv");
      if (k === "lw") save("imr-southeast-asia-laws" + v + ".csv", csv(G.laws || [], ["s", "title", "orig", "year", "amended", "type", "topic", "groups", "url", "link"]), "text/csv");
      if (k === "co") save("imr-southeast-asia-corridors" + v + ".csv", csv(corrRows(), ["id", "destination", "origin", "workers", "bilateral", "origin_icrmw", "population", "year"]), "text/csv");
      if (k === "or") save("imr-southeast-asia-origins" + v + ".csv", csv(originRows(), ["country", "feature", "feature_name", "value", "note", "source", "evidence"]), "text/csv");
      if (k === "rf") save("imr-southeast-asia-developments" + v + ".csv", csv((G.reforms || []).map(function (r) { return {date:r[0], state:r[1], change:r[2], kind:r[4]}; }), ["date", "state", "change", "kind"]), "text/csv");
      if (k === "js") save("imr-southeast-asia" + v + ".json", JSON.stringify({source:"Institute for Migrant Rights, Migrant workers in Southeast Asia", version:G.version, updated:G.updated, changelog:G.changelog, codebook:CB, groups:GR, codings:provRows(), states:S, treaties:G.treaties, treaty_status:G.intl, instruments:G.frameworks, domestic_laws:G.laws, origins:originRows(), corridors:corrRows(), developments:G.reforms}, null, 2), "application/json");
    };
    $("g-src").innerHTML = "<ul>" + (G.sources || []).map(function (s) { return '<li><a href="' + esc(s[1]) + '">' + esc(s[0]) + "</a>" + (s[2] ? " · " + esc(t(s[2], s[3])) : "") + "</li>"; }).join("") + "</ul>" +
      '<p class="g-mono">' + t("Version ", "Versi ") + esc(G.version) + " · " + t("updated ", "diperbarui ") + esc(G.updated) + "</p>" +
      "<ul class=\"g-mono\">" + (G.changelog || []).map(function (c) { return "<li>" + esc(c[0]) + " · v" + esc(c[1]) + " · " + esc(t(c[2], c[3])) + "</li>"; }).join("") + "</ul>";
  }

  function all() { glance(); weights(); rank(); if ($("g-robust-d").open) robust(); intlTable(); profile(); origins(); agreements(); memos(); laws(); reforms(); method(); sources(); }
  document.addEventListener("DOMContentLoaded", function () {
    all();
    $("g-weights").addEventListener("input", function (e) { var k = e.target.getAttribute("data-w"); if (!k) return; W[k] = +e.target.value; $("w-" + k).textContent = W[k]; rank(); });
    $("g-robust-d").addEventListener("toggle", function () { if (this.open) robust(); });
    new MutationObserver(function () { all(); }).observe(document.documentElement, {attributes: true, attributeFilter: ["lang"]});
  });
})();
