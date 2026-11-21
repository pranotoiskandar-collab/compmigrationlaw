/* Countries of origin: renders the page from window.OC (oc-data.js). EN/ID follows the site language switch. */
(function () {
  "use strict";
  var G = window.OC || {};
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); };
  var ID = function () { return document.documentElement.lang === "id"; };
  var t = function (en, id) { return ID() && id ? id : en; };
  var fmt = function (n) { return n == null ? "" : Number(n).toLocaleString(ID() ? "id-ID" : "en-GB"); };
  var S = G.states || [], CB = G.codebook || [], C = G.codes || {};
  var stateOf = function (k) { return S.filter(function (x) { return x.k === k; })[0]; };
  var sname = function (k) { var s = stateOf(k); return s ? t(s.n, s.n_id) : k; };
  var covers = function (a, k) { return a.s === "all" || a.s.split(",").indexOf(k) >= 0; };
  var snames = function (a) { return a.s === "all" ? t("All eight", "Kedelapannya") : a.s.split(",").map(sname).join(", "); };
  var CODED = "2026-10-31";
  var HELP = {ID:1, PH:1, NP:0, BD:1, IN:1, LK:1, PK:1, VN:0};

  function ocEv(id) { var c = G.checked && G.checked[id]; if (!c) return t("S · secondary or statutory citation not yet checked against the official text; coded ", "S · sumber sekunder atau rujukan pasal yang belum diperiksa terhadap teks resmi; dikodekan ") + CODED; return t("P · checked against the official text on ", "P · diperiksa terhadap teks resmi pada ") + G.checked_on + (c === "partly" ? t("; part of the note rests on official guidance, a secondary source or our reading", "; sebagian catatan bersandar pada panduan resmi, sumber sekunder atau tafsiran kami") : ""); }
  var LV = {2:["yes", "Full", "Penuh"], 1:["partial", "Partial", "Sebagian"], 0:["no", "None", "Tidak ada"]};
  function pill(v) { var x = LV[v] || ["unclear", "Unclear", "Belum jelas"]; return '<span class="g-pill p-' + x[0] + '">' + esc(t(x[1], x[2])) + "</span>"; }
  function level(d, v) { return t(d["l" + v], d["l" + v + "_id"]); }

  /* ---------- I. at a glance ---------- */
  var sel = null;
  function glance() {
    var h = "<thead><tr><th>" + t("Country of origin", "Negara asal") + "</th>" + CB.map(function (d) { return "<th>" + esc(t(d.en, d.id)) + "</th>"; }).join("") + "</tr></thead><tbody>";
    S.forEach(function (s) {
      h += "<tr><td><b>" + esc(t(s.n, s.n_id)) + "</b></td>" + CB.map(function (d) {
        var c = (C[s.k] || {})[d.k] || [], on = sel && sel[0] === s.k && sel[1] === d.k;
        return '<td class="c"><button type="button" class="g-cell" data-g="' + s.k + '" data-d="' + d.k + '" aria-pressed="' + !!on + '" title="' + esc(c[1] || "") + '">' + pill(c[0]) + "</button></td>";
      }).join("") + "</tr>";
    });
    $("g-glance").innerHTML = h + "</tbody>";
    $("g-glance").onclick = function (e) { var b = e.target.closest("[data-g]"); if (!b) return; sel = [b.getAttribute("data-g"), b.getAttribute("data-d")]; glance(); };
    $("g-legend").innerHTML = [2, 1, 0].map(function (v) { return pill(v); }).join(" ") + ' <span class="g-mono">' + t("Coded on the law and binding policy as written (de jure). Select any cell for its rule, note and source.", "Dikodekan menurut hukum dan kebijakan mengikat yang tertulis (de jure). Pilih sel mana pun untuk melihat aturan, catatan dan sumbernya.") + "</span>";
    var box = $("g-cellnote");
    if (!sel) { box.innerHTML = ""; return; }
    var s = stateOf(sel[0]), d = CB.filter(function (x) { return x.k === sel[1]; })[0], c = C[s.k][d.k];
    box.innerHTML = '<div class="g-card"><h3>' + esc(t(s.n, s.n_id)) + " · " + esc(t(d.en, d.id)) + "</h3><dl class=\"g-dl\"><dt>" + t("Value", "Nilai") + "</dt><dd>" + pill(c[0]) + " " + esc(level(d, c[0])) + "</dd><dt>" + t("Note", "Catatan") + "</dt><dd>" + esc(c[1]) + "</dd><dt>" + t("Source", "Sumber") + "</dt><dd>" + esc(c[2]) + "</dd><dt>" + t("Evidence", "Bukti") + "</dt><dd>" + ocEv(s.k + "." + d.k) + "</dd></dl></div>";
  }

  /* ---------- II. compare ---------- */
  var W = {}; CB.forEach(function (d) { W[d.k] = 0; });
  function score(k, w) { var tot = 0, max = 0; CB.forEach(function (d) { var v = ((C[k] || {})[d.k] || [])[0]; tot += w[d.k] * (v == null ? 0 : v); max += w[d.k] * 2; }); return max ? 100 * tot / max : 0; }
  function weights() {
    $("g-weights").innerHTML = CB.map(function (d) {
      return '<label>' + esc(t(d.en, d.id)) + ' <output id="w-' + d.k + '">' + W[d.k] + '</output><input type="range" min="0" max="3" step="1" value="' + W[d.k] + '" data-w="' + d.k + '" aria-label="' + esc(t(d.en, d.id)) + '"></label>';
    }).join("");
  }
  function rank() {
    if (!CB.some(function (d) { return W[d.k] > 0; })) { $("g-rank").innerHTML = '<p class="g-empty">' + t("Set a weight above to see a weighted comparison.", "Atur bobot di atas untuk melihat perbandingan tertimbang.") + "</p>"; $("g-rank-note").textContent = ""; return; }
    var R = S.map(function (s) { return {s:s, v:score(s.k, W)}; }).sort(function (a, b) { return b.v - a.v; });
    $("g-rank").innerHTML = R.map(function (r) {
      return '<div class="g-bar"><span>' + esc(t(r.s.n, r.s.n_id)) + '</span><span class="tr"><span class="fl" style="width:' + r.v.toFixed(1) + '%"></span></span><span class="v">' + r.v.toFixed(0) + "/100</span></div>";
    }).join("");
    $("g-rank-note").textContent = t("Score = weighted share of the maximum possible (each feature 0, 1 or 2). It describes the law and policy on paper, not how they are applied.", "Skor = bagian tertimbang dari nilai maksimum (setiap fitur 0, 1 atau 2). Skor menggambarkan hukum dan kebijakan tertulis, bukan penerapannya.");
  }
  var ROB = null;
  function robust() {
    if (!ROB) {
      var N = 10000, seed = 20261031, rnd = function () { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };
      ROB = S.map(function () { return {first:0, rank:0}; });
      for (var i = 0; i < N; i++) {
        var w = {}; CB.forEach(function (d) { w[d.k] = 3 * rnd(); });
        var sc = S.map(function (s, j) { return [j, score(s.k, w)]; }).sort(function (a, b) { return b[1] - a[1]; });
        sc.forEach(function (x, r) { ROB[x[0]].rank += r + 1; }); ROB[sc[0][0]].first++;
      }
      ROB.forEach(function (x) { x.first /= N; x.rank /= N; });
    }
    var o = S.map(function (s, j) { return [s, ROB[j]]; }).sort(function (a, b) { return a[1].rank - b[1].rank; });
    $("g-robust").innerHTML = "<thead><tr><th>" + t("Country", "Negara") + "</th><th>" + t("Highest score in", "Skor tertinggi pada") + "</th><th>" + t("Mean position (1 = highest)", "Posisi rata-rata (1 = tertinggi)") + "</th></tr></thead><tbody>" +
      o.map(function (r) { return "<tr><td>" + esc(t(r[0].n, r[0].n_id)) + '</td><td class="c g-mono">' + (100 * r[1].first).toFixed(1) + '%</td><td class="c g-mono">' + r[1].rank.toFixed(2) + "</td></tr>"; }).join("") + "</tbody>";
  }

  /* ---------- III. international layer ---------- */
  var TV = function (v) {
    if (!v) return pill(0).replace(esc(t("None", "Tidak ada")), esc(t("Not party", "Bukan pihak")));
    if (v === "?") return '<span class="g-pill p-unclear">' + t("Unclear", "Belum jelas") + "</span>";
    if (/^r /.test(v)) return '<span class="g-pill p-partial">' + t("Ratified ", "Diratifikasi ") + v.slice(2) + t(", not in force", ", belum berlaku") + "</span>";
    var y = (v.match(/\d{4}/) || [""])[0];
    return '<span class="g-pill p-yes">' + t("Party ", "Pihak ") + y + "</span>";
  };
  function intlTable() {
    var T = G.treaties || [];
    $("g-intl").innerHTML = "<thead><tr><th>" + t("Instrument", "Instrumen") + "</th>" + S.map(function (s) { return "<th>" + esc(t(s.n, s.n_id)) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      T.map(function (x) { return "<tr><td><b>" + esc(x[1]) + '</b><br><span class="g-mono">' + esc(t(x[2], x[3])) + "</span></td>" + S.map(function (s) { return '<td class="c">' + TV((G.intl[s.k] || {})[x[0]]) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody>";
    $("g-intlnote").textContent = t(G.intl_note, G.intl_note_id);
  }

  /* ---------- IV. profiles ---------- */
  var curP = (location.hash.match(/^#profile-(\w\w)$/) || [])[1] || "ID";
  function stateBtns(el, cur, cb) {
    el.innerHTML = S.map(function (s) { return '<button type="button" class="g-btn" data-s="' + s.k + '" aria-pressed="' + (s.k === cur) + '">' + esc(t(s.n, s.n_id)) + "</button>"; }).join("");
    el.onclick = function (e) { var b = e.target.closest("[data-s]"); if (b) cb(b.getAttribute("data-s")); };
  }
  function profile() {
    stateBtns($("g-states"), curP, function (k) { curP = k; profile(); });
    var s = stateOf(curP); if (!s) return;
    var A = (G.advocacy || {})[s.k] || {};
    var F = (G.frameworks || []).filter(function (a) { return covers(a, s.k); });
    var L = (G.laws || []).filter(function (x) { return x.s === s.k; });
    var rows = [
      [t("Main legislation", "Peraturan utama"), esc(s.law)],
      [t("Policy", "Kebijakan"), esc(t(s.policy, s.policy_id))],
      [t("Institutions", "Lembaga"), esc(t(s.inst, s.inst_id))],
      [t("International status", "Status internasional"), esc(t(s.status, s.status_id))],
      [t("Where to complain", "Tempat mengadu"), esc(t(s.complaints, s.complaints_id))],
      [t("On record", "Tercatat"), fmt(F.length) + t(" instruments", " instrumen") + ' · <a href="#agreements" data-fs="' + s.k + '">' + t("see the list", "lihat daftar") + "</a> · " + fmt(L.length) + t(" laws and policies", " hukum dan kebijakan") + ' · <a href="#laws" data-ls="' + s.k + '">' + t("see the list", "lihat daftar") + "</a>"]
    ];
    var adv = "";
    if (A.args) adv += '<h4 class="g-h4">' + t("Arguments the law opens", "Argumen yang dibuka oleh hukum") + "</h4><ul>" + A.args.map(function (x) { return "<li>" + esc(t(x[0], x[1])) + "</li>"; }).join("") + "</ul>";
    if (A.avenues) adv += '<h4 class="g-h4">' + t("Avenues", "Jalur") + "</h4><ul>" + A.avenues.map(function (x) { return "<li>" + esc(t(x[0], x[1])) + "</li>"; }).join("") + "</ul>";
    $("g-profile").innerHTML = '<div class="g-card" id="profile-' + s.k + '"><h3>' + esc(t(s.n, s.n_id)) + '</h3><dl class="g-dl">' + rows.map(function (r) { return "<dt>" + r[0] + "</dt><dd>" + r[1] + "</dd>"; }).join("") + "</dl>" +
      (adv ? '<div class="g-adv">' + adv + "</div>" : "") +
      '<div class="g-acts"><a href="/legal-help/' + (HELP[s.k] ? "?country=" + s.k : "") + '">' + t("Free legal help in ", "Bantuan hukum gratis di ") + esc(t(s.n, s.n_id)) + '</a><a href="/legal-clinic/">' + t("Draft a rights communication", "Susun pengaduan hak") + '</a><a href="#" id="g-print">' + t("Print a one-page brief", "Cetak ringkasan satu halaman") + "</a></div>" +
      '<p class="g-note">' + t("Coded from secondary sources and statutory citations; the official texts have not yet been checked cell by cell. See Method.", "Dikodekan dari sumber sekunder dan rujukan pasal; teks resmi belum diperiksa sel demi sel. Lihat Metode.") + "</p></div>";
    var a = $("g-profile").querySelector("[data-fs]"); if (a) a.onclick = function () { AF.s = s.k; AF.level = ""; AF.nature = ""; agreements(); };
    var b = $("g-profile").querySelector("[data-ls]"); if (b) b.onclick = function () { LF.s = s.k; LF.type = ""; laws(); };
    $("g-print").onclick = function (e) { e.preventDefault(); window.print(); };
  }

  /* ---------- V. outflows ---------- */
  function outflow() {
    var O = G.outflow || {}, mx = Math.max.apply(null, S.map(function (s) { return (O[s.k] || {}).v || 0; }));
    $("g-out").innerHTML = '<div class="g-bars">' + S.map(function (s) {
      var o = O[s.k]; if (!o) return "";
      return '<div class="g-bar"><span>' + esc(t(s.n, s.n_id)) + ' <span class="g-mono">' + esc(o.y) + '</span></span><span class="tr"><span class="fl' + (s.k === "ID" ? " hi" : "") + '" style="width:' + Math.max(0.6, 100 * o.v / mx).toFixed(1) + '%"></span></span><span class="v">' + (o.v >= 1e6 ? (o.v / 1e6).toFixed(2) + "M" : Math.round(o.v / 1e3) + "k") + "</span></div>";
    }).join("") + "</div>";
    $("g-outt").innerHTML = "<thead><tr><th>" + t("Country", "Negara") + "</th><th>" + t("Figure", "Angka") + "</th><th>" + t("Period", "Periode") + "</th><th>" + t("What it counts", "Yang dihitung") + "</th><th>" + t("Women", "Perempuan") + "</th><th>" + t("Note and source", "Catatan dan sumber") + "</th></tr></thead><tbody>" +
      S.map(function (s) { var o = O[s.k]; if (!o) return ""; return "<tr><td><b>" + esc(t(s.n, s.n_id)) + '</b></td><td class="c g-mono">' + fmt(o.v) + '</td><td class="c g-mono">' + esc(o.y) + "</td><td>" + esc(t(o.pop, o.pop_id)) + '</td><td class="c g-mono">' + (o.women ? fmt(o.women) + " (" + Math.round(100 * o.women / o.v) + "%)" : "—") + "</td><td>" + esc(t(o.note, o.note_id)) + ' <a href="' + esc(o.src[1]) + '" rel="noopener">' + esc(o.src[0]) + "</a></td></tr>"; }).join("") + "</tbody>";
  }

  /* ---------- VI. frameworks ---------- */
  var LEVELS = [["international", "International", "Internasional"], ["regional", "Regional", "Kawasan"], ["interregional", "Interregional", "Antarkawasan"], ["bilateral", "Bilateral", "Bilateral"]];
  var NATURES = [["treaty", "Treaty", "Traktat"], ["agreement", "Agreement or arrangement", "Perjanjian atau pengaturan"], ["mou", "Memorandum of understanding", "Nota kesepahaman"], ["declaration", "Declaration or guidelines", "Deklarasi atau pedoman"], ["process", "Consultative process", "Proses konsultatif"]];
  var lname = function (arr, k) { var x = arr.filter(function (a) { return a[0] === k; })[0]; return x ? t(x[1], x[2]) : k; };
  var AF = {s:"", level:"", nature:"", q:""};
  function amap() {
    var F = (G.frameworks || []).filter(function (a) { return !AF.s || covers(a, AF.s); });
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
  var DEST = ["Saudi Arabia", "United Arab Emirates", "Qatar", "Kuwait", "Malaysia", "Thailand", "Singapore", "Japan", "South Korea", "Taiwan", "Hong Kong"];
  var DEST_ID = {"Saudi Arabia":"Arab Saudi", "United Arab Emirates":"Uni Emirat Arab", "Japan":"Jepang", "South Korea":"Korea Selatan", "Singapore":"Singapura"};
  var dname = function (d) { return t(d, DEST_ID[d]); };
  function bmatrix() {
    var F = (G.frameworks || []).filter(function (a) { return a.level === "bilateral"; });
    $("g-bmat").innerHTML = "<thead><tr><th>" + t("Origin ↓ / destination →", "Asal ↓ / tujuan →") + "</th>" + DEST.map(function (d) { return "<th>" + esc(dname(d)) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      S.map(function (s) { return "<tr><td><b>" + esc(t(s.n, s.n_id)) + "</b></td>" + DEST.map(function (d) {
        var R = F.filter(function (a) { return a.s === s.k && a.partner === d; });
        return '<td class="c">' + (R.length ? '<span class="g-pill p-yes" title="' + esc(R.map(function (a) { return a.title + " (" + a.signed + ")"; }).join("; ")) + '">' + esc(R.map(function (a) { return a.signed.slice(0, 4); }).join(", ")) + "</span>" : '<span class="g-mono">·</span>') + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody>";
  }
  var REG = {"@SA": [["South Asia", "Asia Selatan"], ["BD", "IN", "LK", "NP", "PK"]], "@SEA": [["Southeast Asia", "Asia Tenggara"], ["ID", "PH", "VN", "MM", "KH", "LA", "TL"]]};
  var inSel = function (v, k) { return !v || (REG[v] ? REG[v][1].indexOf(k) >= 0 : v === k); };
  var regOpts = function (v) { return Object.keys(REG).map(function (r) { return '<option value="' + r + '"' + (v === r ? " selected" : "") + ">" + esc(t(REG[r][0][0], REG[r][0][1])) + "</option>"; }).join(""); };
  function atools() {
    var so = '<option value="">' + t("All countries", "Semua negara") + "</option>" + regOpts(AF.s) + S.map(function (s) { return '<option value="' + s.k + '"' + (AF.s === s.k ? " selected" : "") + ">" + esc(t(s.n, s.n_id)) + "</option>"; }).join("");
    var lo = '<option value="">' + t("All levels", "Semua tingkat") + "</option>" + LEVELS.map(function (l) { return '<option value="' + l[0] + '"' + (AF.level === l[0] ? " selected" : "") + ">" + esc(t(l[1], l[2])) + "</option>"; }).join("");
    var no = '<option value="">' + t("All kinds", "Semua jenis") + "</option>" + NATURES.map(function (n) { return '<option value="' + n[0] + '"' + (AF.nature === n[0] ? " selected" : "") + ">" + esc(t(n[1], n[2])) + "</option>"; }).join("");
    $("g-atools").innerHTML = '<div><label for="af-s">' + t("Country of origin", "Negara asal") + '</label><select id="af-s">' + so + '</select></div><div><label for="af-l">' + t("Level", "Tingkat") + '</label><select id="af-l">' + lo + '</select></div><div><label for="af-n">' + t("Nature", "Sifat") + '</label><select id="af-n">' + no + '</select></div><div><label for="af-q">' + t("Search", "Cari") + '</label><input id="af-q" type="search" value="' + esc(AF.q) + '" placeholder="' + t("Partner or title", "Mitra atau judul") + '"></div>';
    $("af-s").onchange = function () { AF.s = this.value; agreements(); };
    $("af-l").onchange = function () { AF.level = this.value; agreements(); };
    $("af-n").onchange = function () { AF.nature = this.value; agreements(); };
    $("af-q").oninput = function () { AF.q = this.value; alist(); };
  }
  function alist() {
    var q = AF.q.toLowerCase(), all = G.frameworks || [];
    var R = all.filter(function (a) { return (!AF.s || (REG[AF.s] ? REG[AF.s][1].some(function (k) { return covers(a, k); }) : covers(a, AF.s))) && (!AF.level || a.level === AF.level) && (!AF.nature || a.nature === AF.nature) && (!q || (a.partner + " " + a.title + " " + (a.scope || "")).toLowerCase().indexOf(q) >= 0); });
    $("g-acount").textContent = fmt(R.length) + t(" of ", " dari ") + fmt(all.length) + t(" instruments", " instrumen");
    $("g-atable").innerHTML = "<thead><tr><th>" + t("Country of origin", "Negara asal") + "</th><th>" + t("Partner", "Mitra") + "</th><th>" + t("Instrument", "Instrumen") + "</th><th>" + t("Level", "Tingkat") + "</th><th>" + t("Nature", "Sifat") + "</th><th>" + t("Adopted", "Diadopsi") + "</th><th>" + t("In force", "Berlaku") + "</th></tr></thead><tbody>" +
      R.map(function (a) { return "<tr><td>" + esc(snames(a)) + "</td><td>" + esc(a.level === "bilateral" ? dname(a.partner) : a.partner) + "</td><td>" + esc(a.title) + (a.scope ? '<br><span class="g-mono">' + esc(a.scope) + "</span>" : "") + '</td><td class="c">' + esc(lname(LEVELS, a.level)) + "</td><td>" + esc(lname(NATURES, a.nature)) + '</td><td class="c g-mono">' + esc(a.signed || "") + '</td><td class="c g-mono">' + esc(a.in_force || "") + "</td></tr>"; }).join("") + "</tbody>";
  }
  function agreements() { amap(); atools(); alist(); }

  /* ---------- VII. domestic laws and policies ---------- */
  var LTYPE = {constitution:["Constitution","Konstitusi"], statute:["Statute","Undang-undang"], regulation:["Regulation","Peraturan"], policy:["Policy","Kebijakan"], draft:["Draft law","Rancangan undang-undang"]};
  var LANG = {ID:"id", VN:"vi", NP:"ne", BD:"bn"};
  var LF = {s:"", type:"", q:""};
  function laws() {
    var so = '<option value="">' + t("All countries", "Semua negara") + "</option>" + regOpts(LF.s) + S.map(function (s) { return '<option value="' + s.k + '"' + (LF.s === s.k ? " selected" : "") + ">" + esc(t(s.n, s.n_id)) + "</option>"; }).join("");
    var to = '<option value="">' + t("All types", "Semua jenis") + "</option>" + Object.keys(LTYPE).map(function (k) { return '<option value="' + k + '"' + (LF.type === k ? " selected" : "") + ">" + esc(t(LTYPE[k][0], LTYPE[k][1])) + "</option>"; }).join("");
    $("g-ltools").innerHTML = '<div><label for="lf-s">' + t("Country", "Negara") + '</label><select id="lf-s">' + so + '</select></div><div><label for="lf-t">' + t("Type", "Jenis") + '</label><select id="lf-t">' + to + '</select></div><div style="grid-column:span 2"><label for="lf-q">' + t("Search", "Cari") + '</label><input id="lf-q" type="search" value="' + esc(LF.q) + '" placeholder="' + t("Title, topic or original title", "Judul, topik atau judul asli") + '"></div>';
    $("lf-s").onchange = function () { LF.s = this.value; laws(); };
    $("lf-t").onchange = function () { LF.type = this.value; laws(); };
    $("lf-q").oninput = function () { LF.q = this.value; lawList(); };
    lawList();
  }
  function lawList() {
    var L = G.laws || [], q = LF.q.toLowerCase();
    var R = L.filter(function (x) { return inSel(LF.s, x.s) && (!LF.type || x.type === LF.type) && (!q || (x.title + " " + x.orig + " " + x.topic).toLowerCase().indexOf(q) >= 0); });
    $("g-lcount").textContent = fmt(R.length) + t(" of ", " dari ") + fmt(L.length) + t(" laws and policies", " hukum dan kebijakan");
    $("g-ltable").innerHTML = "<thead><tr><th>" + t("Country", "Negara") + "</th><th>" + t("Title", "Judul") + "</th><th>" + t("Type", "Jenis") + "</th><th>" + t("Adopted", "Diadopsi") + "</th><th>" + t("Last amended", "Perubahan terakhir") + "</th><th>" + t("Relevance", "Relevansi") + "</th><th>" + t("Official source", "Sumber resmi") + "</th></tr></thead><tbody>" +
      R.map(function (x) { return '<tr><td class="c">' + esc(sname(x.s)) + "</td><td><b>" + esc(x.title) + "</b>" + (x.orig ? '<br><span class="g-mono"' + (LANG[x.s] ? ' lang="' + LANG[x.s] + '"' : "") + ">" + esc(x.orig) + "</span>" : "") + "</td><td>" + esc(t(LTYPE[x.type][0], LTYPE[x.type][1])) + '</td><td class="c g-mono">' + esc(x.year) + '</td><td class="c g-mono">' + esc(x.amended || "") + "</td><td>" + esc(x.topic) + '</td><td class="c"><a href="' + esc(x.url) + '" rel="noopener">' + (x.link === "text" ? t("Read the text", "Baca teks") : x.link === "secondary" ? t("Secondary copy", "Salinan sekunder") : x.link === "un" ? t("UN-hosted copy", "Salinan di situs PBB") : x.link === "guidance" ? t("Official guidance", "Panduan resmi") : t("Official database", "Basis data resmi")) + "</a></td></tr>"; }).join("") + "</tbody>";
  }

  /* ---------- VIII. protection from violence ---------- */
  var VB = G.vcodebook || [], VC = G.vcodes || {}, vsel = null;
  function violence() {
    var h = "<thead><tr><th>" + t("Country of origin", "Negara asal") + "</th>" + VB.map(function (d) { return "<th>" + esc(t(d.en, d.id)) + "</th>"; }).join("") + "</tr></thead><tbody>";
    S.forEach(function (s) {
      h += "<tr><td><b>" + esc(t(s.n, s.n_id)) + "</b></td>" + VB.map(function (d) {
        var c = (VC[s.k] || {})[d.k] || [], on = vsel && vsel[0] === s.k && vsel[1] === d.k;
        return '<td class="c"><button type="button" class="g-cell" data-g="' + s.k + '" data-d="' + d.k + '" aria-pressed="' + !!on + '" title="' + esc(c[1] || "") + '">' + pill(c[0]) + "</button></td>";
      }).join("") + "</tr>";
    });
    $("g-vglance").innerHTML = h + "</tbody>";
    $("g-vglance").onclick = function (e) { var b = e.target.closest("[data-g]"); if (!b) return; vsel = [b.getAttribute("data-g"), b.getAttribute("data-d")]; violence(); };
    var box = $("g-vnote");
    if (vsel) {
      var s = stateOf(vsel[0]), d = VB.filter(function (x) { return x.k === vsel[1]; })[0], c = VC[s.k][d.k];
      box.innerHTML = '<div class="g-card"><h3>' + esc(t(s.n, s.n_id)) + " · " + esc(t(d.en, d.id)) + "</h3><dl class=\"g-dl\"><dt>" + t("Value", "Nilai") + "</dt><dd>" + pill(c[0]) + " " + esc(level(d, c[0])) + "</dd><dt>" + t("Note", "Catatan") + "</dt><dd>" + esc(c[1]) + "</dd><dt>" + t("Source", "Sumber") + "</dt><dd>" + esc(c[2]) + "</dd><dt>" + t("Evidence", "Bukti") + "</dt><dd>" + t("S · secondary or statutory citation not yet checked against the official text; coded ", "S · sumber sekunder atau rujukan pasal yang belum diperiksa terhadap teks resmi; dikodekan ") + CODED + "</dd></dl></div>";
    } else box.innerHTML = "";
    $("g-vcodebook").innerHTML = "<thead><tr><th>" + t("Feature", "Fitur") + "</th><th>2</th><th>1</th><th>0</th></tr></thead><tbody>" +
      VB.map(function (d) { return "<tr><td><b>" + esc(t(d.en, d.id)) + "</b></td><td>" + esc(level(d, 2)) + "</td><td>" + esc(level(d, 1)) + "</td><td>" + esc(level(d, 0)) + "</td></tr>"; }).join("") + "</tbody>";
    $("g-deaths").innerHTML = "<thead><tr><th>" + t("Country", "Negara") + "</th><th>" + t("Recorded", "Tercatat") + "</th><th>" + t("Period", "Periode") + "</th><th>" + t("What it counts", "Yang dihitung") + "</th><th>" + t("Note and source", "Catatan dan sumber") + "</th></tr></thead><tbody>" +
      (G.deaths || []).map(function (r) { return "<tr><td><b>" + esc(sname(r.s)) + '</b></td><td class="c g-mono">' + fmt(r.v) + '</td><td class="c g-mono">' + esc(r.y) + "</td><td>" + esc(t(r.what, r.what_id)) + "</td><td>" + esc(t(r.note, r.note_id)) + ' <a href="' + esc(r.src[1]) + '" rel="noopener">' + esc(r.src[0]) + "</a></td></tr>"; }).join("") + "</tbody>";
  }
  function vRows() {
    var out = [];
    S.forEach(function (s) { VB.forEach(function (d) { var c = (VC[s.k] || {})[d.k] || []; out.push({country:s.k, country_name:s.n, iso3:s.iso3, feature:d.k, feature_name:d.en, value:c[0], value_label:d["l" + c[0]], note:c[1], source:c[2], evidence:"S", coded:CODED}); }); });
    return out;
  }

  /* ---------- VIII. corridors ---------- */
  var withStock = S.filter(function (s) { return (G.stock || []).some(function (r) { return r.s === s.k; }); });
  var curC = withStock.length ? withStock[0].k : "BD";
  var hasBil = function (o, d) { return (G.frameworks || []).some(function (a) { return a.level === "bilateral" && a.s === o && a.partner === d; }); };
  function corridors() {
    var el = $("g-cstates");
    el.innerHTML = withStock.map(function (s) { return '<button type="button" class="g-btn" data-s="' + s.k + '" aria-pressed="' + (s.k === curC) + '">' + esc(t(s.n, s.n_id)) + "</button>"; }).join("");
    el.onclick = function (e) { var b = e.target.closest("[data-s]"); if (b) { curC = b.getAttribute("data-s"); corridors(); } };
    var R = (G.stock || []).filter(function (r) { return r.s === curC; }).sort(function (a, b) { return b.v - a.v; }), o = (G.outflow || {})[curC] || {};
    var mx = o.v || R[0].v;
    $("g-corr").innerHTML = '<p class="g-mono" style="margin:0 0 6px">' + esc(t(o.pop, o.pop_id)) + " · " + esc(R[0].y) + " · " + t("bars scaled to the national total of ", "batang diskalakan ke total nasional ") + fmt(o.v) + "</p>" + R.map(function (r) {
      var b = hasBil(curC, r.d);
      return '<div class="g-bar"><span>' + esc(dname(r.d)) + (b ? ' <span class="g-mono">· ' + t("instrument", "instrumen") + "</span>" : "") + (r.derived ? ' <span class="g-mono">≈</span>' : "") + '</span><span class="tr"><span class="fl' + (b ? " hi" : "") + '" style="width:' + (100 * r.v / mx).toFixed(1) + '%"></span></span><span class="v">' + (r.v >= 1e4 ? Math.round(r.v / 1e3) + "k" : fmt(r.v)) + "</span></div>";
    }).join("") + '<p class="g-note">' + t("Source: ", "Sumber: ") + ((G.stock_src || {})[curC] || []).map(function (x) { return '<a href="' + esc(x[1]) + '">' + esc(x[0]) + "</a>"; }).join("; ") + ". " + t("A red bar marks a corridor with a bilateral instrument on record. Each country counts outflows differently, so compare within a country, not across.", "Batang merah menandai koridor dengan instrumen bilateral yang tercatat. Setiap negara menghitung arus keluar secara berbeda, jadi bandingkan di dalam satu negara, bukan antarnegara.") + "</p>";
  }

  /* ---------- IX. explore ---------- */
  var GULF = ["Saudi Arabia", "United Arab Emirates", "Qatar", "Kuwait", "Oman", "Bahrain"];
  function corrRows() {
    var O = G.outflow || {};
    return (G.stock || []).map(function (r) {
      var o = O[r.s] || {}, x = (G.intl[r.s] || {});
      return {id: sname(r.s) + " → " + r.d, origin: sname(r.s), destination: r.d, region: GULF.indexOf(r.d) >= 0 ? "Gulf" : "Other", workers: r.v, share: o.v ? +(100 * r.v / o.v).toFixed(2) : null, bilateral: hasBil(r.s, r.d) ? 1 : 0, origin_icrmw: x.icrmw ? 1 : 0, year: r.y, derived: r.derived ? 1 : 0};
    });
  }
  function stats() {
    if (!window.IMRStats) return;
    IMRStats.mount($("g-stats"), {
      rows: corrRows(), filename: "imr-countries-of-origin-corridors", idLabel: "corridor",
      vars: [
        {key:"share", type:"num", label:"Share of the origin's outflow (%)", label_id:"Bagian dari arus keluar negara asal (%)"},
        {key:"workers", type:"num", label:"Workers in the corridor", label_id:"Pekerja di koridor", log:true},
        {key:"bilateral", type:"bin", label:"Bilateral instrument on record", label_id:"Ada instrumen bilateral", yes:"Instrument", no:"None", yes_id:"Ada instrumen", no_id:"Tidak ada"},
        {key:"origin_icrmw", type:"bin", label:"Origin is party to the UN migrant workers convention", label_id:"Negara asal pihak Konvensi Pekerja Migran PBB", yes:"Party", no:"Not party", yes_id:"Pihak", no_id:"Bukan pihak"},
        {key:"region", type:"cat", label:"Destination region", label_id:"Kawasan tujuan"},
        {key:"origin", type:"cat", label:"Country of origin", label_id:"Negara asal"}
      ],
      presets: [
        {q:"Do corridors with a bilateral instrument take a larger share of the origin's workers?", q_id:"Apakah koridor dengan instrumen bilateral menerima bagian lebih besar dari pekerja negara asal?", mode:0, y:"share", g:"bilateral"},
        {q:"The same, controlling for whether the destination is in the Gulf", q_id:"Sama, dengan mengontrol apakah tujuan berada di kawasan Teluk", mode:2, ry:"share", preds:["bilateral", "region"]},
        {q:"Are Gulf corridors more often covered by an instrument?", q_id:"Apakah koridor Teluk lebih sering tercakup instrumen?", mode:0, y:"bilateral", g:"region"}
      ],
      defaults: {y:"share", g:"bilateral", x:"workers", y2:"share", preds:["bilateral", "region"]},
      note: "Each row is an origin–destination corridor with an official outflow figure. Only 17 corridors have a reported breakdown, origins count outflows differently and corridors from one origin are not independent: read every p-value as descriptive.",
      note_id: "Setiap baris adalah satu koridor asal–tujuan dengan angka arus keluar resmi. Hanya 17 koridor yang memiliki rincian, negara asal menghitung arus keluar secara berbeda dan koridor dari satu negara asal tidak independen: baca setiap nilai p sebagai deskriptif."
    });
  }

  /* ---------- X. developments ---------- */
  var RF = "";
  var KIND = {real:["Wider protection", "Pelindungan lebih luas"], partial:["Partial or limited", "Sebagian atau terbatas"], law:["New law, institution or ratification", "Hukum, lembaga atau ratifikasi baru"], bilateral:["Bilateral or regional", "Bilateral atau kawasan"], restrict:["Restriction on departure", "Pembatasan keberangkatan"]};
  function reforms() {
    $("g-rfilter").innerHTML = '<button type="button" class="g-btn" data-r="" aria-pressed="' + (RF === "") + '">' + t("All", "Semua") + "</button>" + S.map(function (s) { return '<button type="button" class="g-btn" data-r="' + s.k + '" aria-pressed="' + (RF === s.k) + '">' + esc(t(s.n, s.n_id)) + "</button>"; }).join("");
    $("g-rfilter").onclick = function (e) { var b = e.target.closest("[data-r]"); if (b) { RF = b.getAttribute("data-r"); reforms(); } };
    var MO = ID() ? ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"] : ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    $("g-tl").innerHTML = (G.reforms || []).filter(function (r) { return !RF || r[1] === RF; }).map(function (r) {
      var d = r[0].split("-"), cls = r[4] === "restrict" ? "origin" : r[4] === "bilateral" || r[4] === "law" ? "" : r[4];
      return '<li class="' + cls + '"><span class="d">' + MO[+d[1] - 1] + " " + d[0] + " · " + esc(sname(r[1])) + " · " + esc(t(KIND[r[4]][0], KIND[r[4]][1])) + "</span><br>" + esc(t(r[2], r[3])) + "</li>";
    }).join("");
    $("g-tlleg").innerHTML = '<span class="g-mono">' + t("Green: wider protection · amber: partial · red: restriction on departure · open: law, institution, ratification or bilateral step.", "Hijau: pelindungan lebih luas · kuning: sebagian · merah: pembatasan keberangkatan · kosong: hukum, lembaga, ratifikasi atau langkah bilateral.") + "</span>";
  }

  /* ---------- XI. method ---------- */
  function provRows() {
    var out = [];
    S.forEach(function (s) { CB.forEach(function (d) { var c = (C[s.k] || {})[d.k] || []; out.push({country:s.k, country_name:s.n, iso3:s.iso3, feature:d.k, feature_name:d.en, value:c[0], value_label:d["l" + c[0]], note:c[1], source:c[2], evidence:(G.checked && G.checked[s.k + "." + d.k]) ? "P" : "S", coded:CODED, checked_official_text:(G.checked && G.checked[s.k + "." + d.k]) ? G.checked_on + " (" + G.checked[s.k + "." + d.k] + ")" : ""}); }); });
    return out;
  }
  function method() {
    $("g-codebook").innerHTML = "<thead><tr><th>" + t("Feature", "Fitur") + "</th><th>2</th><th>1</th><th>0</th></tr></thead><tbody>" +
      CB.map(function (d) { return "<tr><td><b>" + esc(t(d.en, d.id)) + "</b></td><td>" + esc(level(d, 2)) + "</td><td>" + esc(level(d, 1)) + "</td><td>" + esc(level(d, 0)) + "</td></tr>"; }).join("") + "</tbody>";
    var P = provRows(), nS = P.filter(function (r) { return r.evidence === "S"; }).length;
    $("g-prov").innerHTML = "<thead><tr><th>" + t("Cells coded", "Sel dikodekan") + "</th><th>" + t("Primary text (P)", "Teks primer (P)") + "</th><th>" + t("Secondary (S)", "Sekunder (S)") + "</th><th>" + t("Coded", "Dikodekan") + "</th><th>" + t("Second coding", "Pengodean kedua") + "</th></tr></thead><tbody><tr><td class=\"c g-mono\">" + P.length + '</td><td class="c g-mono">' + (P.length - nS) + '</td><td class="c g-mono">' + nS + '</td><td class="c g-mono">' + CODED + '</td><td class="c g-mono">' + t("planned (Cohen's κ)", "direncanakan (κ Cohen)") + "</td></tr></tbody>";
    var y = "2026", apa = "Institute for Migrant Rights. (" + y + "). Countries of origin: Emigration and protection law and policy compared (Version " + G.version + ", " + G.updated + ") [Data set and overview]. https://theimr.org/countries-of-origin/";
    var bib = "@misc{imr_origin_" + y + ",\n  author = {{Institute for Migrant Rights}},\n  title = {Countries of Origin: Emigration and Protection Law and Policy Compared},\n  year = {" + y + "},\n  version = {" + G.version + "},\n  note = {Data set and overview, updated " + G.updated + "},\n  url = {https://theimr.org/countries-of-origin/}\n}";
    if (!$("g-cite")) return; // the static "How to cite" block (tools/cite_blocks.py) replaced this
    $("g-cite").innerHTML = '<p style="margin:0 0 10px">' + esc(apa) + '</p><pre class="g-mono" style="white-space:pre-wrap;background:#EEF4F0;border:1px solid #B2C7BC;padding:12px;margin:0">' + esc(bib) + '</pre><div class="g-btns" style="margin-top:10px"><button type="button" class="g-btn" id="g-cp1">' + t("Copy citation", "Salin sitasi") + '</button><button type="button" class="g-btn" id="g-cp2">' + t("Copy BibTeX", "Salin BibTeX") + "</button></div>";
    var cp = function (txt, b) { try { navigator.clipboard.writeText(txt); b.textContent = t("Copied", "Tersalin"); } catch (e) {} };
    $("g-cp1").onclick = function () { cp(apa, this); }; $("g-cp2").onclick = function () { cp(bib, this); };
  }

  /* ---------- XIII. downloads ---------- */
  function csv(rows, cols) { return cols.join(",") + "\n" + rows.map(function (r) { return cols.map(function (c) { var v = r[c] == null ? "" : String(r[c]); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }).join(","); }).join("\n"); }
  function save(name, text, type) { var b = new Blob([text], {type: type}), a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = name; document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500); }
  function sources() {
    var v = "-v" + G.version, P = "imr-countries-of-origin";
    var D = [["cd", t("Coded cells with sources (CSV)", "Sel terkode dengan sumber (CSV)")], ["cb", t("Codebook (CSV)", "Buku kode (CSV)")], ["it", t("Treaty status (CSV)", "Status traktat (CSV)")], ["fw", t("Instruments (CSV)", "Instrumen (CSV)")], ["lw", t("Laws and policies (CSV)", "Hukum dan kebijakan (CSV)")], ["of", t("Outflows (CSV)", "Arus keluar (CSV)")], ["co", t("Corridors (CSV)", "Koridor (CSV)")], ["vp", t("Protection from violence (CSV)", "Pelindungan dari kekerasan (CSV)")], ["rf", t("Legal developments (CSV)", "Perkembangan hukum (CSV)")], ["js", t("Everything (JSON)", "Semua (JSON)")]];
    $("g-dls").innerHTML = D.map(function (d) { return '<button type="button" class="g-btn dl" data-d="' + d[0] + '">' + esc(d[1]) + "</button>"; }).join("");
    $("g-dls").onclick = function (e) {
      var b = e.target.closest("[data-d]"); if (!b) return; var k = b.getAttribute("data-d");
      if (k === "cd") save(P + "-codings" + v + ".csv", csv(provRows(), ["country", "country_name", "iso3", "feature", "feature_name", "value", "value_label", "note", "source", "evidence", "coded", "checked_official_text"]), "text/csv");
      if (k === "cb") save(P + "-codebook" + v + ".csv", csv(CB, ["k", "en", "l2", "l1", "l0"]), "text/csv");
      if (k === "it") save(P + "-treaties" + v + ".csv", csv((G.treaties || []).map(function (x) { var r = {instrument:x[1]}; S.forEach(function (s) { r[s.k] = (G.intl[s.k] || {})[x[0]]; }); return r; }), ["instrument"].concat(S.map(function (s) { return s.k; }))), "text/csv");
      if (k === "fw") save(P + "-instruments" + v + ".csv", csv(G.frameworks || [], ["s", "partner", "title", "level", "nature", "signed", "in_force", "scope"]), "text/csv");
      if (k === "lw") save(P + "-laws" + v + ".csv", csv(G.laws || [], ["s", "title", "orig", "year", "amended", "type", "topic", "url", "link"]), "text/csv");
      if (k === "of") save(P + "-outflows" + v + ".csv", csv(S.map(function (s) { var o = (G.outflow || {})[s.k] || {}; return {country:s.k, value:o.v, period:o.y, counts:o.pop, women:o.women, note:o.note, source:(o.src || [])[0], url:(o.src || [])[1]}; }), ["country", "value", "period", "counts", "women", "note", "source", "url"]), "text/csv");
      if (k === "co") save(P + "-corridors" + v + ".csv", csv(corrRows(), ["id", "origin", "destination", "region", "workers", "share", "bilateral", "origin_icrmw", "year", "derived"]), "text/csv");
      if (k === "vp") save(P + "-protection" + v + ".csv", csv(vRows(), ["country", "country_name", "iso3", "feature", "feature_name", "value", "value_label", "note", "source", "evidence", "coded"]), "text/csv");
      if (k === "rf") save(P + "-developments" + v + ".csv", csv((G.reforms || []).map(function (r) { return {date:r[0], country:r[1], change:r[2], kind:r[4]}; }), ["date", "country", "change", "kind"]), "text/csv");
      if (k === "js") save(P + v + ".json", JSON.stringify({source:"Institute for Migrant Rights, Countries of origin", version:G.version, updated:G.updated, changelog:G.changelog, codebook:CB, codings:provRows(), countries:S, treaties:G.treaties, treaty_status:G.intl, instruments:G.frameworks, laws_and_policies:G.laws, outflows:G.outflow, corridors:corrRows(), protection_codebook:VB, protection_codings:vRows(), deaths_recorded:G.deaths, developments:G.reforms}, null, 2), "application/json");
    };
    $("g-src").innerHTML = "<ul>" + (G.sources || []).map(function (s) { return '<li><a href="' + esc(s[1]) + '">' + esc(s[0]) + "</a>" + (s[2] ? " · " + esc(t(s[2], s[3])) : "") + "</li>"; }).join("") + "</ul>" +
      '<p class="g-mono">' + t("Version ", "Versi ") + esc(G.version) + " · " + t("updated ", "diperbarui ") + esc(G.updated) + "</p>" +
      "<ul class=\"g-mono\">" + (G.changelog || []).map(function (c) { return "<li>" + esc(c[0]) + " · v" + esc(c[1]) + " · " + esc(t(c[2], c[3])) + "</li>"; }).join("") + "</ul>";
  }

  function all() { glance(); weights(); rank(); if ($("g-robust-d").open) robust(); intlTable(); profile(); outflow(); agreements(); bmatrix(); laws(); violence(); corridors(); reforms(); method(); sources(); }
  document.addEventListener("DOMContentLoaded", function () {
    all(); stats();
    $("g-weights").addEventListener("input", function (e) { var k = e.target.getAttribute("data-w"); if (!k) return; W[k] = +e.target.value; $("w-" + k).textContent = W[k]; rank(); });
    $("g-robust-d").addEventListener("toggle", function () { if (this.open) robust(); });
    new MutationObserver(function () { all(); }).observe(document.documentElement, {attributes: true, attributeFilter: ["lang"]});
  });
})();
