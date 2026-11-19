/* Migrant domestic workers database: renders /domestic-workers/ from window.DW (dw-data.js). EN/ID follows the site language switch. */
(function () {
  "use strict";
  var G = window.DW; if (!G) return;
  var $ = function (id) { return document.getElementById(id); };
  var ID = function () { return document.documentElement.lang === "id"; };
  var t = function (en, id) { return ID() && id ? id : en; };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); };
  var S = G.countries, DEST = S.filter(function (s) { return s.role === "dest"; }), ORIG = S.filter(function (s) { return s.role === "origin"; });
  var BY = {}; S.forEach(function (s) { BY[s.k] = s; });
  var DCB = G.dcb, OCB = G.ocb;
  var sname = function (k) { var s = BY[k]; return s ? t(s.n, s.n_id) : k; };
  var rname = function (r) { var x = G.regions[r]; return x ? t(x[0], x[1]) : r; };
  var lab = function (d) { return t(d.en, d.id); };
  var level = function (d, v) { return v == null ? t("Not yet determined", "Belum ditentukan") : t(d["l" + v], d["l" + v + "_id"]); };
  var cell = function (k, f) { var cb = BY[k].role === "dest" ? G.dc : G.oc; return (cb[k] || {})[f] || [null, "", "", "S"]; };
  var cbOf = function (k) { return BY[k].role === "dest" ? DCB : OCB; };
  function pill(v, txt) {
    var cls = v === 2 ? "p-yes" : v === 1 ? "p-partial" : v === 0 ? "p-no" : "p-unclear";
    var tx = txt || (v === 2 ? t("Full", "Penuh") : v === 1 ? t("Partial", "Sebagian") : v === 0 ? t("None", "Tidak ada") : "?");
    return '<span class="g-pill ' + cls + '">' + esc(tx) + "</span>";
  }
  var evTag = function (e) { return e === "P" ? '<span class="g-ev p">P</span>' : '<span class="g-ev s" title="' + esc(t("Secondary source, not yet checked against the official text", "Sumber sekunder, belum dicocokkan dengan teks resmi")) + '">S</span>'; };

  /* ---------- I. at a glance ---------- */
  var VIEW = "dest", SEL = null;
  function glance() {
    var rows = VIEW === "dest" ? DEST : ORIG, cb = VIEW === "dest" ? DCB : OCB;
    $("g-gview").innerHTML = [["dest", t("Countries of destination (" + DEST.length + ")", "Negara tujuan (" + DEST.length + ")")], ["origin", t("Countries of origin (" + ORIG.length + ")", "Negara asal (" + ORIG.length + ")")]].map(function (b) {
      return '<button type="button" class="g-btn" data-v="' + b[0] + '" aria-pressed="' + (VIEW === b[0]) + '">' + esc(b[1]) + "</button>"; }).join("");
    var reg = "", h = "<thead><tr><th>" + t("Country", "Negara") + "</th>" + cb.map(function (d) { return '<th title="' + esc(d.bench) + '">' + esc(lab(d)) + '<br><span class="g-bench">' + esc(d.bench) + "</span></th>"; }).join("") + "</tr></thead><tbody>";
    rows.forEach(function (s) {
      if (s.region !== reg) { reg = s.region; h += '<tr class="g-reg"><td colspan="' + (cb.length + 1) + '">' + esc(rname(reg)) + "</td></tr>"; }
      h += '<tr><th scope="row" class="c">' + esc(sname(s.k)) + "</th>" + cb.map(function (d) {
        var c = cell(s.k, d.k), on = SEL && SEL[0] === s.k && SEL[1] === d.k;
        return '<td class="c"><button type="button" class="g-cell" data-c="' + s.k + "|" + d.k + '" aria-pressed="' + on + '" aria-label="' + esc(sname(s.k) + ": " + lab(d)) + '">' + pill(c[0]) + (c[3] === "P" ? '<span class="g-dot" aria-hidden="true">•</span>' : "") + "</button></td>";
      }).join("") + "</tr>";
    });
    $("g-glance").innerHTML = h + "</tbody>";
    $("g-legend").innerHTML = pill(2) + " " + esc(t("meets the benchmark", "memenuhi tolok ukur")) + " &nbsp; " + pill(1) + " " + esc(t("in part", "sebagian")) + " &nbsp; " + pill(0) + " " + esc(t("not provided", "tidak diatur")) + " &nbsp; " + pill(null) + " " + esc(t("not yet determined", "belum ditentukan")) +
      ' &nbsp; <span class="g-dot">•</span> ' + esc(t("coded from the legal text (P); other cells are from secondary sources (S) and are being checked", "dikodekan dari teks hukum (P); sel lain dari sumber sekunder (S) dan sedang diperiksa"));
    cellNote();
  }
  function cellNote() {
    if (!SEL || !BY[SEL[0]]) { $("g-cellnote").innerHTML = '<p class="g-note">' + esc(t("Select any cell to see the provision, the note and the source.", "Pilih sel mana pun untuk melihat ketentuan, catatan, dan sumbernya.")) + "</p>"; return; }
    var d = cbOf(SEL[0]).filter(function (x) { return x.k === SEL[1]; })[0]; if (!d) return;
    var c = cell(SEL[0], SEL[1]);
    $("g-cellnote").innerHTML = '<div class="g-card"><h3>' + esc(sname(SEL[0])) + " · " + esc(lab(d)) + "</h3><dl class=\"g-dl\"><dt>" + t("Coding", "Kode") + "</dt><dd>" + pill(c[0]) + " " + esc(level(d, c[0])) + "</dd><dt>" + t("Benchmark", "Tolok ukur") + "</dt><dd>" + esc(d.bench) + "</dd><dt>" + t("Note", "Catatan") + "</dt><dd>" + esc(c[1] || "—") + "</dd><dt>" + t("Source", "Sumber") + "</dt><dd>" + esc(c[2] || "—") + "</dd><dt>" + t("Evidence", "Bukti") + "</dt><dd>" + evTag(c[3]) + " " + esc(c[3] === "P" ? t("Coded from the official text", "Dikodekan dari teks resmi") : t("Secondary source; not yet checked against the official text", "Sumber sekunder; belum dicocokkan dengan teks resmi")) + "</dd></dl></div>";
  }

  /* ---------- II. side by side ---------- */
  var CMP = ["AE", "HK", "IT", "PH"].slice();
  function compare() {
    var pool = VIEWC === "dest" ? DEST : ORIG, cb = VIEWC === "dest" ? DCB : OCB;
    CMP = CMP.filter(function (k) { return BY[k].role === VIEWC; });
    $("g-cview").innerHTML = [["dest", t("Destinations", "Tujuan")], ["origin", t("Origins", "Asal")]].map(function (b) { return '<button type="button" class="g-btn" data-cv="' + b[0] + '" aria-pressed="' + (VIEWC === b[0]) + '">' + esc(b[1]) + "</button>"; }).join("");
    $("g-cpick").innerHTML = pool.map(function (s) { var on = CMP.indexOf(s.k) >= 0; return '<button type="button" class="g-btn sm" data-k="' + s.k + '" aria-pressed="' + on + '"' + (!on && CMP.length >= 4 ? " disabled" : "") + ">" + esc(sname(s.k)) + "</button>"; }).join("");
    if (!CMP.length) { $("g-ctable").innerHTML = ""; $("g-cmsg").textContent = t("Choose up to four countries.", "Pilih hingga empat negara."); return; }
    $("g-cmsg").textContent = t("Up to four countries. Notes and sources are shown under each code.", "Hingga empat negara. Catatan dan sumber ditampilkan di bawah tiap kode.");
    $("g-ctable").innerHTML = "<thead><tr><th>" + t("Feature", "Fitur") + "</th>" + CMP.map(function (k) { return "<th>" + esc(sname(k)) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      cb.map(function (d) { return "<tr><th scope=\"row\"><b>" + esc(lab(d)) + '</b><br><span class="g-bench">' + esc(d.bench) + "</span></th>" + CMP.map(function (k) { var c = cell(k, d.k); return "<td>" + pill(c[0]) + " " + evTag(c[3]) + '<div class="g-small">' + esc(c[1]) + '</div><div class="g-src">' + esc(c[2]) + "</div></td>"; }).join("") + "</tr>"; }).join("") +
      "<tr><th scope=\"row\">" + t("Instruments in this database", "Instrumen dalam basis data ini") + "</th>" + CMP.map(function (k) { return '<td class="g-small">' + insFor(k).map(function (x) { return esc(x.title); }).join("<br>") + "</td>"; }).join("") + "</tr></tbody>";
  }
  var VIEWC = "dest";
  function insFor(k) { return G.ins.filter(function (x) { return (x.tier === "nat" || x.tier === "bil") && x.countries.split(",").indexOf(k) >= 0; }); }

  /* ---------- III. weights ---------- */
  var W = {}; DCB.forEach(function (d) { W[d.k] = 0; });
  function score(k, w) { var s = 0, m = 0; DCB.forEach(function (d) { var v = cell(k, d.k)[0]; if (v != null && w[d.k] > 0) { s += w[d.k] * v; m += w[d.k] * 2; } }); return m ? 100 * s / m : null; }
  function weights() {
    $("g-weights").innerHTML = DCB.map(function (d) { return "<label>" + esc(lab(d)) + ' <output id="w-' + d.k + '">' + W[d.k] + '</output><input type="range" min="0" max="3" step="1" value="' + W[d.k] + '" data-w="' + d.k + '" aria-label="' + esc(lab(d)) + '"></label>'; }).join("");
  }
  function rank() {
    var any = DCB.some(function (d) { return W[d.k] > 0; });
    if (!any) { $("g-rank").innerHTML = '<div class="g-empty">' + esc(t("No comparison is shown until you give at least one feature a weight. There is no default ranking.", "Perbandingan baru tampil setelah Anda memberi bobot pada minimal satu fitur. Tidak ada peringkat bawaan.")) + "</div>"; $("g-rank-note").textContent = ""; return; }
    var o = DEST.map(function (s) { return [s, score(s.k, W)]; }).sort(function (a, b) { return (b[1] || 0) - (a[1] || 0); });
    $("g-rank").innerHTML = o.map(function (r) { return '<div class="g-bar"><span>' + esc(sname(r[0].k)) + '</span><span class="tr"><span class="fl" style="width:' + (r[1] || 0).toFixed(1) + '%"></span></span><span class="v">' + (r[1] == null ? "—" : r[1].toFixed(0)) + "</span></div>"; }).join("");
    $("g-rank-note").textContent = t("Score = weighted share of the maximum (0-100) on the features you weighted. Cells not yet determined are left out of that country's maximum. Most cells are from secondary sources and are being checked.", "Skor = bagian tertimbang dari nilai maksimum (0-100) pada fitur yang Anda beri bobot. Sel yang belum ditentukan tidak dihitung dalam maksimum negara itu. Sebagian besar sel berasal dari sumber sekunder dan sedang diperiksa.");
  }
  var ROB = null;
  function robust() {
    if (!ROB) {
      var N = 10000, seed = 20261111, rnd = function () { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };
      ROB = DEST.map(function () { return {first: 0, rank: 0}; });
      for (var i = 0; i < N; i++) {
        var w = {}; DCB.forEach(function (d) { w[d.k] = 3 * rnd(); });
        var sc = DEST.map(function (s, j) { return [j, score(s.k, w)]; }).sort(function (a, b) { return b[1] - a[1]; });
        sc.forEach(function (x, r) { ROB[x[0]].rank += r + 1; }); ROB[sc[0][0]].first++;
      }
      ROB.forEach(function (x) { x.first /= N; x.rank /= N; });
    }
    var o = DEST.map(function (s, j) { return [s, ROB[j]]; }).sort(function (a, b) { return a[1].rank - b[1].rank; });
    $("g-robust").innerHTML = "<thead><tr><th>" + t("Country", "Negara") + "</th><th>" + t("Highest score in", "Skor tertinggi pada") + "</th><th>" + t("Mean position (1 = highest)", "Posisi rata-rata (1 = tertinggi)") + "</th></tr></thead><tbody>" +
      o.map(function (r) { return "<tr><td>" + esc(sname(r[0].k)) + '</td><td class="c g-mono">' + (100 * r[1].first).toFixed(1) + '%</td><td class="c g-mono">' + r[1].rank.toFixed(2) + "</td></tr>"; }).join("") + "</tbody>";
  }

  /* ---------- IV. C189 provision map ---------- */
  function c189() {
    $("g-c189").innerHTML = DCB.map(function (d) {
      var n = [0, 0, 0, 0]; DEST.forEach(function (s) { var v = cell(s.k, d.k)[0]; n[v == null ? 3 : 2 - v]++; });
      var seg = function (i, cls, c) { return n[i] ? '<span class="' + cls + '" style="width:' + (100 * n[i] / DEST.length) + '%" title="' + c + ": " + n[i] + '">' + n[i] + "</span>" : ""; };
      return '<div class="g-c189r"><div><b>' + esc(lab(d)) + '</b> <span class="g-bench">' + esc(d.bench) + '</span></div><div class="g-stack">' + seg(0, "p-yes", t("Full", "Penuh")) + seg(1, "p-partial", t("Partial", "Sebagian")) + seg(2, "p-no", t("None", "Tidak ada")) + seg(3, "p-unclear", "?") + "</div></div>";
    }).join("");
    $("g-c189leg").innerHTML = '<span class="g-pill p-yes">' + t("Full", "Penuh") + '</span> <span class="g-pill p-partial">' + t("Partial", "Sebagian") + '</span> <span class="g-pill" style="background:#fff;border:1px solid #C8BCB1">' + t("None", "Tidak ada") + '</span> <span class="g-pill p-unclear">' + t("Not yet determined", "Belum ditentukan") + "</span>";
    var c189p = DEST.filter(function (s) { return (G.ts[s.k].C189 || [])[0] === "yes"; }).map(function (s) { return sname(s.k); });
    $("g-c189note").textContent = t("Each bar counts the " + DEST.length + " destinations by how their law treats one C189 provision. Parties to C189 among them: " + c189p.join(", ") + ". Non-parties are measured against the same text because it is the agreed international benchmark, not because it binds them.",
      "Setiap batang menghitung " + DEST.length + " negara tujuan menurut cara hukumnya mengatur satu ketentuan C189. Pihak C189 di antaranya: " + c189p.join(", ") + ". Negara bukan pihak diukur dengan teks yang sama karena teks itu tolok ukur internasional yang disepakati, bukan karena mengikat mereka.");
  }

  /* ---------- V. profiles ---------- */
  var PK = "AE";
  function profile() {
    $("g-states").innerHTML = S.map(function (s) { return '<button type="button" class="g-btn sm" data-p="' + s.k + '" aria-pressed="' + (PK === s.k) + '">' + esc(sname(s.k)) + "</button>"; }).join("");
    var s = BY[PK], cb = cbOf(PK), ins = insFor(PK);
    var tr = G.treaties.map(function (x) { return "<li>" + tsPill(G.ts[PK][x[0]]) + " " + esc(x[1]) + "</li>"; }).join("");
    $("g-profile").innerHTML = '<div class="g-grid2"><div class="g-card"><h3>' + esc(sname(PK)) + '</h3><p class="g-mono">' + esc(s.role === "dest" ? t("Country of destination", "Negara tujuan") : t("Country of origin", "Negara asal")) + " · " + esc(rname(s.region)) + " · " + s.iso3 + "</p>" +
      '<h4 class="g-h4">' + t("Instruments", "Instrumen") + "</h4><ul class=\"g-list\">" + ins.map(function (x) { return "<li><b>" + esc(x.title) + "</b> (" + x.year + ") " + evTag(x.evidence) + '<br><span class="g-small">' + esc(t(x.sum, x.sum_id)) + "</span></li>"; }).join("") + "</ul>" +
      '<h4 class="g-h4">' + t("Treaty status", "Status traktat") + '</h4><ul class="g-list">' + tr + "</ul></div>" +
      '<div class="g-card"><h3>' + t("Coded features", "Fitur terkode") + "</h3><dl class=\"g-dl\">" + cb.map(function (d) { var c = cell(PK, d.k); return "<dt>" + esc(lab(d)) + "</dt><dd>" + pill(c[0]) + " " + evTag(c[3]) + " " + esc(c[1]) + (c[2] ? '<br><span class="g-src">' + esc(c[2]) + "</span>" : "") + "</dd>"; }).join("") + "</dl></div></div>";
  }
  function tsPill(x) {
    if (!x) return "";
    var y = (String(x[1]).match(/\d{4}/) || [""])[0];
    var m = {yes: ["p-yes", t("Party", "Pihak") + (y ? " " + y : "")], pending: ["p-partial", t("Ratified " + y + ", not yet in force", "Diratifikasi " + y + ", belum berlaku")], sig: ["p-partial", t("Signed only", "Hanya ditandatangani")], no: ["p-no", t("Not party", "Bukan pihak")], ne: ["p-unclear", t("Not eligible", "Tidak bisa menjadi pihak")], na: ["p-unclear", t("Not coded", "Tidak dikodekan")]}[x[0]];
    return '<span class="g-pill ' + m[0] + '"' + (x[2] ? ' title="' + esc(x[2]) + '"' : "") + ">" + esc(m[1]) + "</span>" + (x[3] === "S" && x[0] !== "ne" && x[0] !== "na" ? '<span class="g-ev s">S</span>' : "");
  }

  /* ---------- VI. corridors ---------- */
  var CO = "ID", CD = "MY";
  /* membership of regional bodies and processes among the 30 jurisdictions (others are matched by region) */
  var MEMB = {"ASEAN": ["ID", "PH", "VN", "MY", "SG"], "Colombo Process": ["ID", "PH", "VN", "LK", "NP", "IN", "BD"],
    "Abu Dhabi Dialogue": ["ID", "PH", "VN", "LK", "NP", "IN", "BD", "AE", "SA", "KW", "QA", "BH", "OM", "MY"],
    "League of Arab States": ["SA", "KW", "QA", "BH", "OM", "AE", "JO", "LB", "MA"], "African Union": ["ET", "KE", "UG", "ZA", "NA", "ZM", "TZ", "MA"], "SADC": ["ZA", "NA", "ZM", "TZ"],
    "European Union": ["IT", "ES"], "Council of Europe": ["IT", "ES", "GB"], "Organization of American States": ["US", "CA", "AR", "BR", "MX", "CR", "BO", "PE", "CL", "PY", "UY"],
    "Inter-American Court of Human Rights": ["AR", "BR", "MX", "CR", "BO", "PE", "CL", "PY", "UY"], "MERCOSUR": ["AR", "BR", "PY", "UY", "BO"]};
  function corridor() {
    var opt = function (arr, sel) { return arr.map(function (s) { return '<option value="' + s.k + '"' + (s.k === sel ? " selected" : "") + ">" + esc(sname(s.k)) + "</option>"; }).join(""); };
    $("g-co").innerHTML = opt(ORIG, CO); $("g-cd").innerHTML = opt(DEST, CD);
    var bil = G.ins.filter(function (x) { if (x.tier !== "bil") return false; var c = x.countries.split(","); return c.indexOf(CO) >= 0 && c.indexOf(CD) >= 0; });
    var reg = G.ins.filter(function (x) { if (x.tier !== "reg") return false; var m = MEMB[x.countries]; if (m) return x.id === "COLOMBO" ? m.indexOf(CO) >= 0 : m.indexOf(CO) >= 0 && m.indexOf(CD) >= 0; return BY[CO].region === x.region && BY[CD].region === x.region; });
    var both = G.treaties.map(function (x) { return "<tr><td>" + esc(x[1]) + "</td><td>" + tsPill(G.ts[CO][x[0]]) + "</td><td>" + tsPill(G.ts[CD][x[0]]) + "</td></tr>"; }).join("");
    $("g-corr").innerHTML = '<div class="g-grid3"><div class="g-card"><h3>' + t("Before departure", "Sebelum berangkat") + " · " + esc(sname(CO)) + '</h3><ul class="g-list">' + OCB.map(function (d) { var c = cell(CO, d.k); return "<li>" + pill(c[0]) + " <b>" + esc(lab(d)) + '</b><br><span class="g-small">' + esc(c[1]) + "</span></li>"; }).join("") + "</ul></div>" +
      '<div class="g-card"><h3>' + t("Between the two", "Di antara keduanya") + '</h3><h4 class="g-h4">' + t("Bilateral instruments", "Instrumen bilateral") + "</h4>" + (bil.length ? '<ul class="g-list">' + bil.map(function (x) { return "<li><b>" + esc(x.title) + "</b> (" + x.year + ')<br><span class="g-small">' + esc(t(x.sum, x.sum_id)) + "</span></li>"; }).join("") + "</ul>" : '<p class="g-small">' + esc(t("None recorded in this database.", "Tidak ada yang tercatat dalam basis data ini.")) + "</p>") +
      (reg.length ? '<h4 class="g-h4">' + t("Regional and interregional", "Kawasan dan antarkawasan") + '</h4><ul class="g-list">' + reg.map(function (x) { return "<li>" + esc(x.title) + " (" + x.year + ")</li>"; }).join("") + "</ul>" : "") +
      '<h4 class="g-h4">' + t("Treaties", "Traktat") + '</h4><div class="g-scroll"><table class="g-t"><thead><tr><th></th><th>' + esc(sname(CO)) + "</th><th>" + esc(sname(CD)) + "</th></tr></thead><tbody>" + both + "</tbody></table></div></div>" +
      '<div class="g-card"><h3>' + t("At work", "Saat bekerja") + " · " + esc(sname(CD)) + '</h3><ul class="g-list">' + DCB.map(function (d) { var c = cell(CD, d.k); return "<li>" + pill(c[0]) + " <b>" + esc(lab(d)) + '</b><br><span class="g-small">' + esc(c[1]) + "</span></li>"; }).join("") + "</ul></div></div>";
  }

  /* ---------- VII. instruments ---------- */
  var F = {tier: "", region: "", type: "", topic: "", bind: "", q: ""};
  var TIER = {intl: ["International", "Internasional"], reg: ["Regional and interregional", "Kawasan dan antarkawasan"], bil: ["Bilateral", "Bilateral"], nat: ["National", "Nasional"]};
  var TYPE = {treaty: ["Treaty", "Traktat"], protocol: ["Protocol", "Protokol"], rec: ["ILO recommendation", "Rekomendasi ILO"], interp: ["Treaty-body interpretation", "Tafsir badan traktat"], soft: ["Declaration, framework or guideline", "Deklarasi, kerangka atau pedoman"], statute: ["Statute or directive", "Undang-undang atau direktif"], reg: ["Regulation or decree", "Peraturan atau keputusan"], contract: ["Standard contract or collective agreement", "Kontrak standar atau perjanjian kerja bersama"], mou: ["Bilateral agreement or MoU", "Perjanjian bilateral atau MoU"], judgment: ["Judgment or advisory opinion", "Putusan atau pendapat nasihat"]};
  var ALLF = DCB.concat(OCB);
  function insList() {
    var sel = function (k, opts, all) { return '<select data-f="' + k + '"><option value="">' + esc(all) + "</option>" + opts.map(function (o) { return '<option value="' + o[0] + '"' + (F[k] === o[0] ? " selected" : "") + ">" + esc(o[1]) + "</option>"; }).join("") + "</select>"; };
    if (!$("g-ftools").dataset.ok || $("g-ftools").dataset.lang !== String(ID())) {
      $("g-ftools").innerHTML =
        "<label>" + t("Level", "Tingkat") + sel("tier", Object.keys(TIER).map(function (k) { return [k, t(TIER[k][0], TIER[k][1])]; }), t("All levels", "Semua tingkat")) + "</label>" +
        "<label>" + t("Region", "Kawasan") + sel("region", Object.keys(G.regions).map(function (k) { return [k, rname(k)]; }), t("All regions", "Semua kawasan")) + "</label>" +
        "<label>" + t("Kind of instrument", "Jenis instrumen") + sel("type", Object.keys(TYPE).map(function (k) { return [k, t(TYPE[k][0], TYPE[k][1])]; }), t("All kinds", "Semua jenis")) + "</label>" +
        "<label>" + t("Topic", "Topik") + sel("topic", ALLF.map(function (d) { return [d.k, lab(d)]; }), t("All topics", "Semua topik")) + "</label>" +
        "<label>" + t("Binding force", "Daya ikat") + sel("bind", [["1", t("Binding", "Mengikat")], ["0", t("Not binding", "Tidak mengikat")]], t("Both", "Keduanya")) + "</label>" +
        '<label class="wide">' + t("Search titles, summaries and coded notes", "Cari judul, ringkasan, dan catatan kode") + '<input type="search" data-f="q" value="' + esc(F.q) + '" placeholder="' + esc(t("e.g. passport, rest day, Kafala, 2017", "mis. paspor, hari istirahat, 2017")) + '"></label>';
      $("g-ftools").dataset.ok = "1"; $("g-ftools").dataset.lang = String(ID());
    }
    var q = F.q.trim().toLowerCase();
    var R = G.ins.filter(function (x) {
      if (F.tier && x.tier !== F.tier) return false;
      if (F.region && x.region !== F.region && !(x.tier === "intl")) return false;
      if (F.region && x.tier === "intl") return false;
      if (F.type && x.type !== F.type) return false;
      if (F.topic && x.topics.indexOf(F.topic) < 0) return false;
      if (F.bind && String(x.binding) !== F.bind) return false;
      if (q && (x.title + " " + x.sum + " " + x.sum_id + " " + x.issuer + " " + x.year).toLowerCase().indexOf(q) < 0) return false;
      return true;
    }).sort(function (a, b) { return ["intl", "reg", "bil", "nat"].indexOf(a.tier) - ["intl", "reg", "bil", "nat"].indexOf(b.tier) || a.year - b.year; });
    $("g-icount").textContent = t(R.length + " of " + G.ins.length + " instruments", R.length + " dari " + G.ins.length + " instrumen");
    $("g-itable").innerHTML = "<thead><tr><th>" + t("Instrument", "Instrumen") + "</th><th>" + t("Level", "Tingkat") + "</th><th>" + t("Kind", "Jenis") + "</th><th>" + t("Adopted", "Diadopsi") + "</th><th>" + t("Covers", "Mencakup") + "</th></tr></thead><tbody>" +
      (R.length ? R.map(function (x) { return "<tr><td><b>" + esc(x.title) + "</b> " + evTag(x.evidence) + '<br><span class="g-small">' + esc(t(x.sum, x.sum_id)) + '</span><br><span class="g-src">' + esc(x.issuer) + "</span></td><td>" + esc(t(TIER[x.tier][0], TIER[x.tier][1])) + (x.tier === "nat" || x.tier === "bil" ? "<br>" + esc(x.countries.split(",").map(sname).join(" · ")) : x.tier === "reg" ? "<br>" + esc(x.countries) : "") + "</td><td>" + esc(t(TYPE[x.type][0], TYPE[x.type][1])) + "<br>" + (x.binding ? '<span class="g-pill p-yes">' + t("Binding", "Mengikat") + "</span>" : '<span class="g-pill p-unclear">' + t("Not binding", "Tidak mengikat") + "</span>") + '</td><td class="c g-mono">' + x.year + (x.in_force && x.in_force != x.year ? "<br>" + t("in force ", "berlaku ") + x.in_force : "") + '</td><td class="g-small">' + x.topics.map(function (k) { var d = ALLF.filter(function (z) { return z.k === k; })[0]; return d ? esc(lab(d)) : ""; }).join(", ") + "</td></tr>"; }).join("") : '<tr><td colspan="5">' + esc(t("No instrument matches these filters.", "Tidak ada instrumen yang cocok.")) + "</td></tr>") + "</tbody>";
    // coded notes that match the search
    if (q.length > 2) {
      var hits = [];
      S.forEach(function (s) { cbOf(s.k).forEach(function (d) { var c = cell(s.k, d.k); if ((c[1] + " " + c[2]).toLowerCase().indexOf(q) >= 0) hits.push([s.k, d, c]); }); });
      $("g-nhits").innerHTML = hits.length ? '<h3 class="g-h4">' + t("Coded provisions that mention “" + esc(F.q) + "” (" + hits.length + ")", "Ketentuan terkode yang menyebut “" + esc(F.q) + "” (" + hits.length + ")") + '</h3><ul class="g-list">' + hits.slice(0, 40).map(function (h) { return "<li>" + pill(h[2][0]) + " <b>" + esc(sname(h[0])) + " · " + esc(lab(h[1])) + "</b>: " + esc(h[2][1]) + ' <span class="g-src">' + esc(h[2][2]) + "</span></li>"; }).join("") + "</ul>" : "";
    } else $("g-nhits").innerHTML = "";
  }

  /* ---------- VIII. timeline ---------- */
  var TF = "";
  function timeline() {
    $("g-tfilter").innerHTML = '<button type="button" class="g-btn sm" data-t="" aria-pressed="' + (TF === "") + '">' + t("All", "Semua") + "</button>" + Object.keys(TIER).map(function (k) { return '<button type="button" class="g-btn sm" data-t="' + k + '" aria-pressed="' + (TF === k) + '">' + esc(t(TIER[k][0], TIER[k][1])) + "</button>"; }).join("");
    var R = G.ins.filter(function (x) { return !TF || x.tier === TF; }).sort(function (a, b) { return a.year - b.year; });
    var y0 = 1945, y1 = 2026, by = {};
    R.forEach(function (x) { var d = Math.floor(x.year / 5) * 5; (by[d] = by[d] || []).push(x); });
    var mx = Math.max.apply(null, Object.keys(by).map(function (k) { return by[k].length; }).concat([1]));
    var h = '<div class="g-hist" role="img" aria-label="' + esc(t("Number of instruments adopted per five-year period", "Jumlah instrumen yang diadopsi per lima tahun")) + '">';
    for (var d = y0; d <= y1; d += 5) { var n = (by[d] || []).length; h += '<div class="g-hcol"><span class="g-hbar" style="height:' + (100 * n / mx) + '%" title="' + d + "-" + (d + 4) + ": " + n + '"></span><span class="g-hlab">' + (d % 10 === 0 ? d : "") + "</span></div>"; }
    $("g-hist").innerHTML = h + "</div>";
    $("g-tl").innerHTML = R.map(function (x) { return '<li class="' + x.tier + '"><span class="d">' + x.year + " · " + esc(t(TIER[x.tier][0], TIER[x.tier][1])) + (x.tier === "nat" || x.tier === "bil" ? " · " + esc(x.countries.split(",").map(sname).join(" · ")) : "") + "</span><br>" + esc(x.title) + "</li>"; }).join("");
  }

  /* ---------- IX. treaty status ---------- */
  function treaties() {
    $("g-ttable").innerHTML = "<thead><tr><th>" + t("Country", "Negara") + "</th>" + G.treaties.map(function (x) { return "<th>" + esc(x[0]) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      S.map(function (s) { return '<tr><th scope="row" class="c">' + esc(sname(s.k)) + "</th>" + G.treaties.map(function (x) { return '<td class="c">' + tsPill(G.ts[s.k][x[0]]) + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody>";
    $("g-tkey").innerHTML = G.treaties.map(function (x) { return "<b>" + esc(x[0]) + "</b> " + esc(x[1]); }).join(" · ");
  }

  /* ---------- X. explore the data ---------- */
  function statRows() {
    return DEST.map(function (s) {
      var r = {id: sname(s.k), region: rname(s.region), gulf: s.region === "gulf" ? 1 : 0};
      var all = {}; DCB.forEach(function (d) { all[d.k] = 1; });
      r.index = score(s.k, all); r.index = r.index == null ? null : +r.index.toFixed(1);
      DCB.forEach(function (d) { r[d.k] = cell(s.k, d.k)[0]; });
      ["C189", "C181", "C190", "P29"].forEach(function (k) { r[k.toLowerCase()] = (G.ts[s.k][k] || [])[0] === "yes" ? 1 : ["ne", "na"].indexOf((G.ts[s.k][k] || [])[0]) >= 0 ? null : 0; });
      r.general = cell(s.k, "cov")[0] === 2 ? 1 : 0;
      var main = insFor(s.k).filter(function (x) { return x.tier === "nat"; }).map(function (x) { return x.year; });
      r.year = main.length ? Math.max.apply(null, main) : null;
      return r;
    });
  }
  function stats() {
    if (!window.IMRStats) return;
    var vars = [
      {key: "index", type: "num", label: "Protection index, all 17 features equally weighted (0-100)", label_id: "Indeks perlindungan, 17 fitur berbobot sama (0-100)", zero: false},
      {key: "c189", type: "bin", label: "Party to ILO C189", label_id: "Pihak ILO C189", yes: "Party", no: "Not party", yes_id: "Pihak", no_id: "Bukan pihak"},
      {key: "c181", type: "bin", label: "Party to ILO C181", label_id: "Pihak ILO C181", yes: "Party", no: "Not party", yes_id: "Pihak", no_id: "Bukan pihak"},
      {key: "c190", type: "bin", label: "Party to ILO C190", label_id: "Pihak ILO C190", yes: "Party", no: "Not party", yes_id: "Pihak", no_id: "Bukan pihak"},
      {key: "general", type: "bin", label: "Covered by the general labor law", label_id: "Dicakup hukum ketenagakerjaan umum", yes: "General law", no: "Dedicated or none", yes_id: "Hukum umum", no_id: "Khusus atau tidak ada"},
      {key: "year", type: "num", label: "Year of the latest national instrument", label_id: "Tahun instrumen nasional terbaru"},
      {key: "region", type: "cat", label: "Region", label_id: "Kawasan"}
    ].concat(DCB.map(function (d) { return {key: d.k, type: "num", label: d.en + " (0-2)", label_id: d.id + " (0-2)"}; }));
    IMRStats.mount($("g-stats"), {
      rows: statRows(), filename: "imr-domestic-workers-destinations", idLabel: "country", vars: vars,
      presets: [
        {q: "Do C189 parties provide more of the coded protections?", q_id: "Apakah pihak C189 memberi lebih banyak perlindungan yang dikodekan?", mode: 0, y: "index", g: "c189"},
        {q: "Is coverage by the general labor law linked to weekly rest?", q_id: "Apakah cakupan hukum ketenagakerjaan umum terkait dengan istirahat mingguan?", mode: 0, y: "rest", g: "general"},
        {q: "Are newer national laws more protective?", q_id: "Apakah hukum nasional yang lebih baru lebih melindungi?", mode: 1, x: "year", y2: "index"},
        {q: "Index by C189 and C190 status together", q_id: "Indeks menurut status C189 dan C190 bersama-sama", mode: 2, ry: "index", preds: ["c189", "c190"]}
      ],
      defaults: {y: "index", g: "c189", x: "year", y2: "index", preds: ["c189", "c190"]},
      note: "Each row is one of the " + DEST.length + " destination jurisdictions. The sample is small and not random, most cells are still from secondary sources, and ratification may follow law reform rather than cause it: read every result as a description of these jurisdictions, not as evidence of an effect.",
      note_id: "Setiap baris adalah satu dari " + DEST.length + " yurisdiksi tujuan. Sampelnya kecil dan tidak acak, sebagian besar sel masih dari sumber sekunder, dan ratifikasi bisa mengikuti reformasi hukum, bukan menyebabkannya: baca setiap hasil sebagai gambaran yurisdiksi ini, bukan bukti adanya pengaruh."
    });
  }

  /* ---------- XI. method ---------- */
  function provRows() {
    var out = [];
    S.forEach(function (s) { cbOf(s.k).forEach(function (d) { var c = cell(s.k, d.k); out.push({country: s.k, country_name: s.n, iso3: s.iso3, role: s.role === "dest" ? "destination" : "origin", feature: d.k, feature_name: d.en, benchmark: d.bench, value: c[0], value_label: c[0] == null ? "" : d["l" + c[0]], note: c[1], source: c[2], evidence: c[3], coded: G.updated}); }); });
    return out;
  }
  function method() {
    var cbt = function (cb) { return "<thead><tr><th>" + t("Feature", "Fitur") + "</th><th>" + t("Benchmark", "Tolok ukur") + "</th><th>2</th><th>1</th><th>0</th></tr></thead><tbody>" + cb.map(function (d) { return "<tr><td><b>" + esc(lab(d)) + '</b></td><td class="g-mono">' + esc(d.bench) + "</td><td>" + esc(level(d, 2)) + "</td><td>" + esc(level(d, 1)) + "</td><td>" + esc(level(d, 0)) + "</td></tr>"; }).join("") + "</tbody>"; };
    $("g-cbd").innerHTML = cbt(DCB); $("g-cbo").innerHTML = cbt(OCB);
    var P = provRows(), nP = P.filter(function (r) { return r.evidence === "P"; }).length, nN = P.filter(function (r) { return r.value == null; }).length;
    $("g-prov").innerHTML = "<thead><tr><th>" + t("Cells coded", "Sel dikodekan") + "</th><th>" + t("From the official text (P)", "Dari teks resmi (P)") + "</th><th>" + t("Secondary (S)", "Sekunder (S)") + "</th><th>" + t("Not yet determined", "Belum ditentukan") + "</th><th>" + t("Instruments", "Instrumen") + "</th></tr></thead><tbody><tr><td class=\"c g-mono\">" + P.length + '</td><td class="c g-mono">' + nP + '</td><td class="c g-mono">' + (P.length - nP) + '</td><td class="c g-mono">' + nN + '</td><td class="c g-mono">' + G.ins.length + "</td></tr></tbody>";
    var apa = "Institute for Migrant Rights. (2026). Migrant domestic workers: International, regional and national law compared (Version " + G.version + ", " + G.updated + ") [Data set]. https://theimr.org/domestic-workers/";
    if ($("g-cite")) $("g-cite").textContent = apa;
  }

  /* ---------- XIII. downloads ---------- */
  function csv(rows, cols) { return cols.join(",") + "\n" + rows.map(function (r) { return cols.map(function (c) { var v = r[c] == null ? "" : Array.isArray(r[c]) ? r[c].join(";") : String(r[c]); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }).join(","); }).join("\n"); }
  function save(name, text, type) { var b = new Blob([text], {type: type}), a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = name; document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500); }
  function sources() {
    var v = "-v" + G.version, P = "imr-domestic-workers";
    var D = [["cd", t("Coded cells with notes and sources (CSV)", "Sel terkode dengan catatan dan sumber (CSV)")], ["cb", t("Codebook (CSV)", "Buku kode (CSV)")], ["in", t("Instruments (CSV)", "Instrumen (CSV)")], ["ts", t("Treaty status (CSV)", "Status traktat (CSV)")], ["js", t("Everything (JSON)", "Semua data (JSON)")]];
    $("g-dls").innerHTML = D.map(function (d) { return '<button type="button" class="g-btn dl" data-d="' + d[0] + '">' + esc(d[1]) + "</button>"; }).join("");
    $("g-dls").onclick = function (e) {
      var b = e.target.closest("[data-d]"); if (!b) return; var k = b.getAttribute("data-d");
      if (k === "cd") save(P + "-codings" + v + ".csv", csv(provRows(), ["country", "country_name", "iso3", "role", "feature", "feature_name", "benchmark", "value", "value_label", "note", "source", "evidence", "coded"]), "text/csv");
      if (k === "cb") save(P + "-codebook" + v + ".csv", csv(DCB.map(function (d) { return Object.assign({role: "destination"}, d); }).concat(OCB.map(function (d) { return Object.assign({role: "origin"}, d); })), ["role", "k", "en", "id", "bench", "l2", "l1", "l0", "l2_id", "l1_id", "l0_id"]), "text/csv");
      if (k === "in") save(P + "-instruments" + v + ".csv", csv(G.ins, ["id", "tier", "region", "countries", "type", "binding", "year", "in_force", "issuer", "title", "sum", "topics", "evidence"]), "text/csv");
      if (k === "ts") save(P + "-treaties" + v + ".csv", csv([].concat.apply([], S.map(function (s) { return G.treaties.map(function (x) { var y = G.ts[s.k][x[0]]; return {country: s.k, country_name: s.n, instrument: x[0], status: y[0], date: y[1], note: y[2], evidence: y[3]}; }); })), ["country", "country_name", "instrument", "status", "date", "note", "evidence"]), "text/csv");
      if (k === "js") save(P + v + ".json", JSON.stringify({source: "Institute for Migrant Rights, Migrant domestic workers database", licence: "CC BY 4.0", version: G.version, updated: G.updated, changelog: G.changelog, codebook: {destination: DCB, origin: OCB}, codings: provRows(), countries: S, instruments: G.ins, treaty_status: G.ts}, null, 1), "application/json");
    };
    $("g-ver").innerHTML = t("Version ", "Versi ") + esc(G.version) + " · " + t("updated ", "diperbarui ") + esc(G.updated) + "<br>" + (G.changelog || []).map(function (c) { return esc(c[0]) + " · v" + esc(c[1]) + " · " + esc(t(c[2], c[3])); }).join("<br>");
  }

  function all() { glance(); compare(); weights(); rank(); if ($("g-robust-d").open) robust(); c189(); profile(); corridor(); insList(); timeline(); treaties(); method(); sources(); }
  document.addEventListener("DOMContentLoaded", function () {
    all(); stats();
    $("g-gview").addEventListener("click", function (e) { var b = e.target.closest("[data-v]"); if (b) { VIEW = b.getAttribute("data-v"); SEL = null; glance(); } });
    $("g-glance").addEventListener("click", function (e) { var b = e.target.closest("[data-c]"); if (b) { SEL = b.getAttribute("data-c").split("|"); glance(); } });
    $("g-cview").addEventListener("click", function (e) { var b = e.target.closest("[data-cv]"); if (b) { VIEWC = b.getAttribute("data-cv"); CMP = VIEWC === "dest" ? ["AE", "HK", "IT"] : ["ID", "PH"]; compare(); } });
    $("g-cpick").addEventListener("click", function (e) { var b = e.target.closest("[data-k]"); if (!b) return; var k = b.getAttribute("data-k"), i = CMP.indexOf(k); if (i >= 0) CMP.splice(i, 1); else if (CMP.length < 4) CMP.push(k); compare(); });
    $("g-weights").addEventListener("input", function (e) { var k = e.target.getAttribute("data-w"); if (!k) return; W[k] = +e.target.value; $("w-" + k).textContent = W[k]; rank(); });
    $("g-wreset").addEventListener("click", function () { DCB.forEach(function (d) { W[d.k] = 0; }); weights(); rank(); });
    $("g-wequal").addEventListener("click", function () { DCB.forEach(function (d) { W[d.k] = 1; }); weights(); rank(); });
    $("g-robust-d").addEventListener("toggle", function () { if (this.open) robust(); });
    $("g-states").addEventListener("click", function (e) { var b = e.target.closest("[data-p]"); if (b) { PK = b.getAttribute("data-p"); profile(); } });
    $("g-co").addEventListener("change", function () { CO = this.value; corridor(); });
    $("g-cd").addEventListener("change", function () { CD = this.value; corridor(); });
    $("g-ftools").addEventListener("change", function (e) { var k = e.target.getAttribute("data-f"); if (k && k !== "q") { F[k] = e.target.value; insList(); } });
    $("g-ftools").addEventListener("input", function (e) { if (e.target.getAttribute("data-f") === "q") { F.q = e.target.value; insList(); } });
    $("g-tfilter").addEventListener("click", function (e) { var b = e.target.closest("[data-t]"); if (b) { TF = b.getAttribute("data-t"); timeline(); } });
    new MutationObserver(function () { all(); }).observe(document.documentElement, {attributes: true, attributeFilter: ["lang"]});
  });
})();
