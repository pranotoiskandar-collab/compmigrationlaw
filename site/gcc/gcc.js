/* Gulf States migration and labor laws in comparison page: renders the page from window.GCC (gcc-data.js). EN/ID follows the site language switch. */
(function () {
  "use strict";
  var G = window.GCC || {};
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); };
  var ID = function () { return document.documentElement.lang === "id"; };
  var t = function (en, id) { return ID() && id ? id : en; };
  var sname = function (k) { var s = (G.states || []).filter(function (x) { return x.k === k; })[0]; return s ? t(s.n, s.n_id) : k; };
  var fmt = function (n) { return n == null ? "" : Number(n).toLocaleString(ID() ? "id-ID" : "en-GB"); };
  var ISO3 = {SA:"SAU",AE:"ARE",QA:"QAT",KW:"KWT",BH:"BHR",OM:"OMN"};

  /* ---------- I. at a glance ---------- */
  var LVL = {yes:["In place","Ada"], partial:["Partial","Sebagian"], no:["Absent","Tidak ada"], unclear:["Unclear","Belum jelas"]};
  var FARM = {covered:"yes", excluded:"no", domestic:"partial", separate:"partial", unclear:"unclear"};
  var FARM_L = {covered:["Covered","Tercakup"], excluded:["Excluded","Dikecualikan"], domestic:["Domestic-worker rules","Aturan pekerja rumah tangga"], separate:["Separate regulation","Peraturan tersendiri"], unclear:["Unclear","Belum jelas"]};
  function pill(cls, en, id) { return '<span class="g-pill p-' + cls + '">' + esc(t(en, id)) + "</span>"; }
  function lv(v) { var c = v === "yes" || /^(party|in force)/.test(v) ? "yes" : v === "no" ? "no" : v === "unclear" ? "unclear" : "partial"; return c; }
  function treatyPill(v) {
    if (!v || v === "no") return pill("no", "Not a party", "Bukan pihak");
    var m = String(v).match(/(\d{4})/), y = m ? m[1] : "";
    if (/^ratified/.test(v)) return pill("partial", "Ratified " + y + ", not yet in force", "Diratifikasi " + y + ", belum berlaku");
    return pill("yes", "Party since " + y, "Pihak sejak " + y);
  }
  function glance() {
    var S = G.states || [];
    var h = "<thead><tr><th>" + t("State", "Negara") + "</th><th>" + t("Farmworkers under labor law", "Buruh tani dalam UU ketenagakerjaan") + "</th><th>" + t("Change jobs without consent", "Pindah kerja tanpa izin") + "</th><th>" + t("Minimum wage for migrants", "Upah minimum bagi migran") + "</th><th>" + t("Wage protection", "Perlindungan upah") + "</th><th>" + t("Unions allowed", "Serikat pekerja") + "</th><th>ICESCR</th><th>" + t("ILO forced labor protocol", "Protokol kerja paksa ILO") + "</th><th>" + t("Summer midday ban", "Larangan siang musim panas") + "</th></tr></thead><tbody>";
    S.forEach(function (s) {
      h += "<tr><td><b>" + esc(t(s.n, s.n_id)) + "</b></td><td>" + pill(FARM[s.farm], FARM_L[s.farm][0], FARM_L[s.farm][1]) + "</td>";
      ["mobility", "minwage", "wps", "union"].forEach(function (k) { var v = s[k], c = lv(v); h += "<td>" + pill(c, LVL[c][0], LVL[c][1]) + "</td>"; });
      h += "<td>" + treatyPill(s.icescr) + "</td><td>" + treatyPill(s.p29 === "in force 2021" ? "party 2021" : s.p29) + '</td><td class="c g-mono">' + esc(s.heat) + "</td></tr>";
    });
    $("g-glance").innerHTML = h + "</tbody>";
    $("g-legend").innerHTML = ["yes", "partial", "no", "unclear"].map(function (k) { return pill(k, LVL[k][0], LVL[k][1]); }).join(" ") +
      ' <span class="g-mono">' + t("The UAE, Saudi and Qatari labor-law rows are checked against official texts; Kuwait, Bahrain and Oman still rest on secondary sources.", "Baris UU ketenagakerjaan UEA, Arab Saudi dan Qatar sudah diperiksa terhadap teks resmi; Kuwait, Bahrain dan Oman masih bersandar pada sumber sekunder.") + "</span>";
  }

  /* ---------- II. scorecard ---------- */
  var DIMS = [
    {k:"farm", en:"Farmworkers covered by labor law", id:"Buruh tani dicakup UU ketenagakerjaan", f:function (s) { return {covered:2, domestic:1, separate:1, excluded:0, unclear:0}[s.farm]; }},
    {k:"mobility", en:"Change jobs without employer consent", id:"Pindah kerja tanpa izin majikan", f:function (s) { return sc(s.mobility); }},
    {k:"minwage", en:"Minimum wage for migrants", id:"Upah minimum bagi migran", f:function (s) { return sc(s.minwage); }},
    {k:"wps", en:"Wage protection system", id:"Sistem perlindungan upah", f:function (s) { return sc(s.wps); }},
    {k:"union", en:"Workers may form unions", id:"Pekerja boleh berserikat", f:function (s) { return sc(s.union); }},
    {k:"icescr", en:"Party to ICESCR", id:"Pihak ICESCR", f:function (s) { return /^party/.test(s.icescr) ? 2 : 0; }},
    {k:"p29", en:"ILO forced labor protocol", id:"Protokol kerja paksa ILO", f:function (s) { return /in force/.test(s.p29) ? 2 : /ratified/.test(s.p29) ? 1 : 0; }},
    {k:"heat", en:"Length of the midday heat ban", id:"Lama larangan kerja siang", f:function (s) { return heatScore(s.heat); }},
    {k:"agr", en:"Bilateral agreements on record", id:"Perjanjian bilateral tercatat", f:function (s) { var n = bilatCount(s.k), mx = Math.max.apply(null, (G.states || []).map(function (x) { return bilatCount(x.k); }).concat([1])); return 2 * n / mx; }}
  ];
  function sc(v) { return v === "yes" ? 2 : v === "partial" ? 1 : 0; }
  function heatScore(h) { // hours × days, scaled so the longest ban scores 2
    var all = (G.states || []).map(function (s) { return heatLoad(s.heat); }), mx = Math.max.apply(null, all.concat([1]));
    return 2 * heatLoad(h) / mx;
  }
  function heatLoad(h) {
    var M = {Jan:0,Feb:31,Mar:59,Apr:90,May:120,Jun:151,Jul:181,Aug:212,Sep:243,Oct:273,Nov:304,Dec:334};
    var d = String(h).match(/(\d+) (\w{3}) to (\d+) (\w{3})/), hr = String(h).match(/(\d+):(\d+) to (\d+):(\d+)/);
    if (!d || !hr) return 0;
    var days = (M[d[4]] + +d[3]) - (M[d[2]] + +d[1]) + 1, hours = (+hr[3] + hr[4] / 60) - (+hr[1] + hr[2] / 60);
    return days * hours;
  }
  var W = {}; DIMS.forEach(function (d) { W[d.k] = 0; });
  function weights() {
    $("g-weights").innerHTML = DIMS.map(function (d) {
      return '<label>' + esc(t(d.en, d.id)) + ' <output id="w-' + d.k + '">' + W[d.k] + '</output><input type="range" min="0" max="3" step="1" value="' + W[d.k] + '" data-w="' + d.k + '" aria-label="' + esc(t(d.en, d.id)) + '"></label>';
    }).join("");
  }
  function rank() {
    if (!DIMS.some(function (d) { return W[d.k] > 0; })) { $("g-rank").innerHTML = '<p class="g-empty">' + t("Set a weight above to see a weighted comparison.", "Atur bobot di atas untuk melihat perbandingan tertimbang.") + "</p>"; $("g-rank-note").textContent = ""; return; }
    var S = (G.states || []).map(function (s) {
      var tot = 0, max = 0;
      DIMS.forEach(function (d) { tot += W[d.k] * d.f(s); max += W[d.k] * 2; });
      return {s:s, v:max ? 100 * tot / max : 0};
    }).sort(function (a, b) { return b.v - a.v; });
    $("g-rank").innerHTML = S.map(function (r, i) {
      return '<div class="g-bar"><span>' + (i + 1) + ". " + esc(t(r.s.n, r.s.n_id)) + '</span><span class="tr"><span class="fl' + (i === 0 ? " hi" : "") + '" style="width:' + r.v.toFixed(1) + '%"></span></span><span class="v">' + r.v.toFixed(0) + "/100</span></div>";
    }).join("");
    $("g-rank-note").textContent = t("Score = weighted share of the maximum possible. Heat bans score by days × hours, relative to the longest ban; agreements score relative to the state with the most.", "Skor = bagian tertimbang dari nilai maksimum. Larangan panas dinilai menurut hari × jam, relatif terhadap larangan terpanjang; perjanjian dinilai relatif terhadap negara dengan jumlah terbanyak.");
  }

  /* ---------- III. profiles ---------- */
  var curP = (location.hash.match(/^#profile-(\w\w)$/) || [])[1] || "SA";
  function stateBtns(el, cur, cb) {
    el.innerHTML = (G.states || []).map(function (s) { return '<button type="button" class="g-btn" data-s="' + s.k + '" aria-pressed="' + (s.k === cur) + '">' + esc(t(s.n, s.n_id)) + "</button>"; }).join("");
    el.onclick = function (e) { var b = e.target.closest("[data-s]"); if (b) cb(b.getAttribute("data-s")); };
  }
  function profile() {
    stateBtns($("g-states"), curP, function (k) { curP = k; profile(); });
    var s = (G.states || []).filter(function (x) { return x.k === curP; })[0]; if (!s) return;
    var F = (G.frameworks || []).filter(function (a) { return a.s === s.k; });
    var nb = F.filter(function (a) { return a.level === "bilateral"; }).length;
    var rows = [
      [t("General labor law", "UU ketenagakerjaan umum"), esc(s.law)],
      [t("Farmworkers", "Buruh tani"), pill(FARM[s.farm], FARM_L[s.farm][0], FARM_L[s.farm][1]) + " " + esc(t(s.farm_t, s.farm_t_id))],
      [t("Domestic workers", "Pekerja rumah tangga"), esc(t(s.dw, s.dw_id))],
      [t("Domestic workers in 2017 (ITUC baseline)", "Pekerja rumah tangga pada 2017 (garis dasar ITUC)"), esc(t(s.dw2017 || "", s.dw2017_id || ""))],
      [t("Changing jobs and leaving", "Pindah kerja dan keluar negeri"), esc(t(s.mob_t, s.mob_t_id))],
      [t("ILO conventions not ratified", "Konvensi ILO yang belum diratifikasi"), esc(s.ilo_not || "—") + ' <span class="g-mono">(' + t("of C029/P029, C087, C097, C098, C100, C105, C111, C138, C143, C182, C188, C189; NORMLEX, 31 Oct 2026", "dari C029/P029, C087, C097, C098, C100, C105, C111, C138, C143, C182, C188, C189; NORMLEX, 31 Okt 2026") + ")</span>"],
      [t("UN treaties on trafficking and migrant workers", "Perjanjian PBB tentang perdagangan orang dan pekerja migran"), t("Party to the Palermo Trafficking Protocol; not a party to the Migrant Workers Convention (UN Treaty Collection, 30 Oct 2026).", "Pihak Protokol Palermo tentang perdagangan orang; bukan pihak Konvensi Pekerja Migran (UN Treaty Collection, 30 Okt 2026).")],
      [t("Remittances paid abroad", "Remitansi yang dikirim ke luar negeri"), s.remit != null ? "US$ " + s.remit.toFixed(1) + t(" billion in ", " miliar pada ") + s.remit_y + " <span class=\"g-mono\">(World Bank)</span>" : "—"],
      [t("Minimum wage", "Upah minimum"), esc(t(s.mw_t, s.mw_t_id))],
      [t("Wage protection", "Perlindungan upah"), esc(t(s.wps_t, s.wps_t_id))],
      [t("Summer midday ban", "Larangan kerja siang"), esc(s.heat)],
      [t("Where to complain", "Tempat mengadu"), esc(t(s.complaints, s.complaints_id))],
      [t("Instruments on record", "Instrumen tercatat"), F.length ? fmt(F.length) + " " + t("in total, of which " + nb + " bilateral", "total, " + nb + " di antaranya bilateral") + ' · <a href="#agreements" data-fs="' + s.k + '">' + t("see the list", "lihat daftar") + "</a>" : t("Being compiled", "Sedang dihimpun")]
    ];
    var av = avenues(s);
    rows.push([t("Arguments and avenues", "Argumen dan jalur"), "<ol style=\"margin:0;padding-left:20px\">" + av.map(function (a) { return "<li>" + a + "</li>"; }).join("") + "</ol>"]);
    $("g-profile").innerHTML = '<div class="g-card" id="profile-' + s.k + '"><h3>' + esc(t(s.n, s.n_id)) + '</h3><dl class="g-dl">' + rows.map(function (r) { return "<dt>" + r[0] + "</dt><dd>" + r[1] + "</dd>"; }).join("") + "</dl>" +
      '<div class="g-acts"><a href="/legal-help/?country=' + s.k + '">' + t("Free legal help in ", "Bantuan hukum gratis di ") + esc(t(s.n, s.n_id)) + '</a><a href="/legal-clinic/?country=' + ISO3[s.k] + '">' + t("Draft a rights communication", "Susun pengaduan hak") + '</a><a href="#" id="g-print">' + t("Print this country brief", "Cetak ringkasan negara ini") + "</a></div>" +
      (s.checked ? "" : '<p class="g-note">' + t("Based on secondary sources; the official text has not yet been checked.", "Berdasarkan sumber sekunder; teks resmi belum diperiksa.") + "</p>") + "</div>";
    var pb = $("g-print"); if (pb) pb.onclick = function (e) { e.preventDefault(); window.print(); };
    var a = $("g-profile").querySelector("[data-fs]"); if (a) a.onclick = function () { AF.s = s.k; AF.level = ""; AF.nature = ""; agreements(); };
  }


  function avenues(s) {
    var A = [], party = /^party/.test(s.icescr);
    if (s.farm !== "covered") {
      if (party) A.push(t("ICESCR Art. 7, read with CESCR General Comment No. 23 (2016), extends just and favorable conditions of work to agricultural and domestic workers. A shadow report to the state's next CESCR review can raise the farm exclusion.", "Pasal 7 ICESCR, dibaca bersama Komentar Umum CESCR No. 23 (2016), memperluas kondisi kerja yang adil dan layak kepada buruh tani dan rumah tangga. Laporan bayangan pada peninjauan CESCR berikutnya bisa mengangkat pengecualian pertanian."));
      else A.push(t("The state is not a party to ICESCR. The farm exclusion can be raised through Universal Periodic Review stakeholder submissions and with UN Special Rapporteurs.", "Negara ini bukan pihak ICESCR. Pengecualian pertanian bisa diangkat melalui masukan pemangku kepentingan dalam Tinjauan Periodik Universal dan kepada Pelapor Khusus PBB."));
    }
    A.push(t("All six states are parties to the Convention on the Elimination of Racial Discrimination. CERD General Recommendation No. 30 (2004) on non-citizens supports arguments on equal pay and working conditions in reports to CERD.", "Keenam negara adalah pihak Konvensi Penghapusan Diskriminasi Rasial. Rekomendasi Umum CERD No. 30 (2004) tentang bukan warga negara mendukung argumen kesetaraan upah dan kondisi kerja dalam laporan kepada CERD."));
    if (/in force/.test(s.p29)) A.push(t("The ILO forced labor protocol (P29) is in force: the state must prevent forced labor, protect victims and give access to remedies. A workers' organization can prompt ILO supervisory comments.", "Protokol kerja paksa ILO (P29) berlaku: negara wajib mencegah kerja paksa, melindungi korban dan memberi akses pemulihan. Organisasi pekerja bisa mendorong komentar pengawasan ILO."));
    else if (/ratified/.test(s.p29)) A.push(t("The ILO forced labor protocol (P29) was ratified in 2026 and enters into force a year later; the first report to the ILO is an early chance to raise sponsorship and recruitment-fee issues.", "Protokol kerja paksa ILO (P29) diratifikasi pada 2026 dan berlaku setahun kemudian; laporan pertama kepada ILO adalah kesempatan awal mengangkat isu sponsor dan biaya rekrutmen."));
    if (s.mobility !== "yes") A.push(t("Limits on changing employer can be raised with the UN Special Rapporteur on the human rights of migrants and in ILO forced-labor supervision.", "Pembatasan pindah majikan bisa diangkat kepada Pelapor Khusus PBB tentang hak asasi migran dan dalam pengawasan kerja paksa ILO."));
    if (s.minwage !== "yes") A.push(t("Without a minimum wage for migrants, bilateral agreements and standard contracts with countries of origin are the main lever on pay; see the agreements on record below.", "Tanpa upah minimum bagi migran, perjanjian bilateral dan kontrak standar dengan negara asal menjadi pengungkit utama soal upah; lihat perjanjian yang tercatat di bawah."));
    return A;
  }
  function codebook() {
    var C = [
      [t("Farmworkers under labor law", "Buruh tani dalam UU ketenagakerjaan"), t("Covered = no exclusion of agricultural workers employed by firms; domestic-worker rules = farm work placed under the domestic-worker regime; separate regulation = farm workers excluded from the labor code but covered by a dedicated regulation; excluded = excluded from the labor code; unclear = no provision found.", "Tercakup = tidak ada pengecualian buruh tani di perusahaan; aturan pekerja rumah tangga = pekerjaan pertanian ditempatkan di rezim pekerja rumah tangga; peraturan tersendiri = buruh tani dikecualikan dari UU tetapi diatur peraturan khusus; dikecualikan = dikecualikan dari UU; belum jelas = tidak ditemukan ketentuan."), t("Scope article of the labor law", "Pasal ruang lingkup UU ketenagakerjaan")],
      [t("Change jobs without consent", "Pindah kerja tanpa izin"), t("In place = all workers may change employer without consent; partial = some workers or conditions; absent = consent required.", "Ada = semua pekerja boleh pindah majikan tanpa izin; sebagian = sebagian pekerja atau dengan syarat; tidak ada = perlu izin."), t("Labor and residence regulations", "Peraturan ketenagakerjaan dan izin tinggal")],
      [t("Minimum wage for migrants", "Upah minimum bagi migran"), t("In place = a statutory minimum that applies to non-nationals; partial = sectoral or by decision; absent = none or nationals only.", "Ada = upah minimum menurut undang-undang yang berlaku bagi bukan warga; sebagian = sektoral atau melalui keputusan; tidak ada = tidak ada atau hanya bagi warga."), t("Wage legislation", "Peraturan upah")],
      [t("Wage protection", "Perlindungan upah"), t("In place = electronic wage protection system for most workers; partial = major groups excluded.", "Ada = sistem perlindungan upah elektronik bagi sebagian besar pekerja; sebagian = kelompok besar dikecualikan."), t("Ministry rules", "Aturan kementerian")],
      [t("Unions allowed", "Serikat pekerja"), t("In place = migrant workers may join or form trade unions; partial = workers' committees or restricted unions; absent = not permitted.", "Ada = pekerja migran boleh bergabung atau membentuk serikat; sebagian = komite pekerja atau serikat terbatas; tidak ada = tidak diizinkan."), t("Labor law; ILO reports", "UU ketenagakerjaan; laporan ILO")],
      ["ICESCR · P29", t("Party or ratified, with year; not yet in force where the ILO's twelve-month rule applies.", "Pihak atau diratifikasi, dengan tahun; belum berlaku bila aturan dua belas bulan ILO berlaku."), "UN Treaty Collection; NORMLEX (30 Oct 2026)"],
      [t("Summer midday ban", "Larangan siang musim panas"), t("Dates and hours of the ban on outdoor work in direct sun, as announced.", "Tanggal dan jam larangan kerja di luar ruangan di bawah sinar matahari langsung, sebagaimana diumumkan."), t("Ministry announcements; law-firm guides (2026)", "Pengumuman kementerian; panduan firma hukum (2026)")],
      [t("Instruments", "Instrumen"), t("Level: international, regional, interregional or bilateral. Nature: binding treaty, agreement, memorandum of understanding, protocol or annex, standard contract, declaration or dialogue.", "Tingkat: internasional, kawasan, antarkawasan atau bilateral. Sifat: traktat mengikat, perjanjian, nota kesepahaman, protokol atau lampiran, kontrak standar, deklarasi atau dialog."), "GLMM; Chilton, Posner & Woda; NORMLEX; UNTC"]
    ];
    $("g-codebook").innerHTML = "<thead><tr><th>" + t("Feature", "Fitur") + "</th><th>" + t("Coding rule", "Aturan pengodean") + "</th><th>" + t("Primary source", "Sumber utama") + "</th></tr></thead><tbody>" + C.map(function (r) { return "<tr><td><b>" + esc(r[0]) + "</b></td><td>" + esc(r[1]) + "</td><td>" + esc(r[2]) + "</td></tr>"; }).join("") + "</tbody>";
    var y = (G.updated || "2026").slice(0, 4), apa = "Institute for Migrant Rights. (" + y + "). Migrant workers in the Gulf states: Migration and labor laws in comparison (Version " + G.version + ", " + (G.updated || "") + ") [Data set and overview]. https://theimr.org/gcc/";
    var bib = "@misc{imr_gulf_" + y + ",\n  author = {{Institute for Migrant Rights}},\n  title = {Migrant Workers in the Gulf States, Migration Jurisprudence from the South},\n  year = {" + y + "},\n  version = {" + G.version + "},\n  note = {Data set and overview, updated " + (G.updated || "") + "},\n  url = {https://theimr.org/gcc/}\n}";
    if (!$("g-cite")) return; // the static "How to cite" block (tools/cite_blocks.py) replaced this
    $("g-cite").innerHTML = '<p style="margin:0 0 10px">' + esc(apa) + '</p><pre class="g-mono" style="white-space:pre-wrap;background:#F4F1EE;border:1px solid #C8BCB1;padding:12px;margin:0">' + esc(bib) + '</pre><div class="g-btns" style="margin-top:10px"><button type="button" class="g-btn" id="g-cp1">' + t("Copy citation", "Salin sitasi") + '</button><button type="button" class="g-btn" id="g-cp2">' + t("Copy BibTeX", "Salin BibTeX") + "</button></div>";
    var cp = function (txt, b) { try { navigator.clipboard.writeText(txt); b.textContent = t("Copied", "Tersalin"); } catch (e) {} };
    $("g-cp1").onclick = function () { cp(apa, this); }; $("g-cp2").onclick = function () { cp(bib.replace(/\\n/g, "\n"), this); };
  }


  var FEAT = {farm:["Farmworkers under labor law","Buruh tani dalam UU ketenagakerjaan"], mobility:["Change jobs without consent","Pindah kerja tanpa izin"], minwage:["Minimum wage for migrants","Upah minimum bagi migran"], wps:["Wage protection","Perlindungan upah"], union:["Unions allowed","Serikat pekerja"], icescr:["ICESCR","ICESCR"], p29:["ILO forced labor protocol","Protokol kerja paksa ILO"], heat:["Summer midday ban","Larangan siang musim panas"]};
  function cellVal(st, f) {
    if (f === "farm") return t(FARM_L[st.farm][0], FARM_L[st.farm][1]);
    if (f === "heat") return st.heat;
    if (f === "icescr" || f === "p29") return st[f];
    var c = lv(st[f]); return t(LVL[c][0], LVL[c][1]);
  }
  function prov() {
    var S = {}; (G.states || []).forEach(function (x) { S[x.k] = x; });
    var P = (G.prov || []).filter(function (r) { return S[r[0]]; });
    var np = P.filter(function (r) { return r[2] === "P"; }).length;
    $("g-prov").innerHTML = "<thead><tr><th>" + t("State", "Negara") + "</th><th>" + t("Feature", "Fitur") + "</th><th>" + t("Coding", "Kode") + "</th><th>" + t("Basis", "Dasar") + "</th><th>" + t("Source", "Sumber") + "</th><th>" + t("Checked", "Diperiksa") + "</th></tr></thead><tbody>" +
      P.map(function (r) { return '<tr><td class="c">' + esc(sname(r[0])) + "</td><td>" + esc(t(FEAT[r[1]][0], FEAT[r[1]][1])) + "</td><td>" + esc(cellVal(S[r[0]], r[1])) + '</td><td class="c"><span class="g-pill ' + (r[2] === "P" ? "p-yes" : "p-unclear") + '">' + r[2] + "</span></td><td>" + esc(r[3]) + '</td><td class="c g-mono">' + esc(r[4]) + "</td></tr>"; }).join("") + "</tbody>";
    $("g-prov").insertAdjacentHTML("beforebegin", "");
    var cap = $("g-prov-cap"); if (!cap) { cap = document.createElement("p"); cap.id = "g-prov-cap"; cap.className = "g-mono"; $("g-prov").parentNode.parentNode.insertBefore(cap, $("g-prov").parentNode); }
    cap.textContent = np + t(" of ", " dari ") + P.length + t(" coded cells rest on primary text (P); the rest on secondary sources (S).", " sel berkode bersandar pada teks primer (P); sisanya pada sumber sekunder (S).");
  }
  function robust() {
    var S = G.states || [], N = 10000, seed = 20261031;
    var rnd = function () { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };
    var first = {}, ranks = {}; S.forEach(function (s) { first[s.k] = 0; ranks[s.k] = []; });
    var F = S.map(function (s) { return DIMS.map(function (d) { return d.f(s); }); });
    for (var i = 0; i < N; i++) {
      var w = DIMS.map(function () { return rnd() * 3; });
      var sc = F.map(function (f, j) { var v = 0; for (var k = 0; k < f.length; k++) v += w[k] * f[k]; return [S[j].k, v + rnd() * 1e-9]; }).sort(function (a, b) { return b[1] - a[1]; });
      first[sc[0][0]]++; sc.forEach(function (x, r) { ranks[x[0]].push(r + 1); });
    }
    var med = function (a) { a = a.slice().sort(function (x, y) { return x - y; }); return a[Math.floor(a.length / 2)]; };
    var R = S.map(function (s) { var a = ranks[s.k].slice().sort(function (x, y) { return x - y; }); return {s:s, p1:first[s.k] / N, md:med(a), lo:a[Math.floor(a.length * 0.05)], hi:a[Math.floor(a.length * 0.95)]}; }).sort(function (a, b) { return a.md - b.md || b.p1 - a.p1; });
    $("g-robust").innerHTML = "<thead><tr><th>" + t("State", "Negara") + "</th><th>" + t("Ranks first", "Peringkat pertama") + "</th><th>" + t("Median rank", "Peringkat median") + "</th><th>" + t("90% of weightings", "90% pembobotan") + "</th></tr></thead><tbody>" +
      R.map(function (r) { return "<tr><td>" + esc(t(r.s.n, r.s.n_id)) + '</td><td class="c g-mono">' + (100 * r.p1).toFixed(1) + '%</td><td class="c g-mono">' + r.md + '</td><td class="c g-mono">' + r.lo + "–" + r.hi + "</td></tr>"; }).join("") + "</tbody>";
  }

  /* ---------- IV. people and jobs ---------- */
  var curD = "SA";
  var COL = ["#2E2116", "#8F5E12", "#6B7A63", "#C79A16", "#2F3657", "#8A9285", "#D98C7F", "#5B4A3C"];
  function demog() {
    stateBtns($("g-dstates"), curD, function (k) { curD = k; demog(); });
    var D = (G.demog || {})[curD];
    if (!D) { $("g-demog").innerHTML = '<p class="g-empty">' + t("Figures for this state are being compiled.", "Data negara ini sedang dihimpun.") + "</p>"; return; }
    var h = "";
    if (D.pop) {
      var tot = D.pop.nat + D.pop.non, sh = 100 * D.pop.non / tot;
      h += '<h3 style="font-weight:500;font-size:22px;margin:6px 0 0">' + t("Population", "Penduduk") + ' <span class="g-mono">' + esc(D.pop.year) + "</span></h3>" +
        '<div class="g-stack" role="img" aria-label="' + sh.toFixed(0) + '%"><span style="width:' + (100 - sh) + '%;background:#6B7A63"></span><span style="width:' + sh + '%;background:#8F5E12"></span></div>' +
        '<p class="g-mono" style="margin:0">' + t("Nationals", "Warga negara") + " " + fmt(D.pop.nat) + " · " + t("Non-nationals", "Bukan warga negara") + " " + fmt(D.pop.non) + " (" + sh.toFixed(0) + "%)</p>";
    }
    if (D.sex) {
      var fs = 100 * D.sex.f / (D.sex.m + D.sex.f);
      h += '<h3 style="font-weight:500;font-size:22px;margin:22px 0 0">' + esc(t(D.sex.base, D.sex.base_id)) + ' <span class="g-mono">' + esc(D.sex.year) + "</span></h3>" +
        '<div class="g-stack"><span style="width:' + (100 - fs) + '%;background:#2E2116"></span><span style="width:' + fs + '%;background:#C79A16"></span></div>' +
        '<p class="g-mono" style="margin:0">' + t("Men", "Laki-laki") + " " + (100 - fs).toFixed(0) + "% · " + t("Women", "Perempuan") + " " + fs.toFixed(0) + "%</p>";
    }
    if (D.sectors && D.sectors.length) {
      var mx = Math.max.apply(null, D.sectors.map(function (x) { return x[1]; })), sum = D.sectors.reduce(function (a, x) { return a + x[1]; }, 0);
      h += '<h3 style="font-weight:500;font-size:22px;margin:22px 0 8px">' + esc(t(D.sec_title || "Employed non-nationals by sector", D.sec_title_id || "Pekerja bukan warga negara menurut sektor")) + ' <span class="g-mono">' + esc(D.sec_year || "") + '</span></h3><div class="g-bars">' +
        D.sectors.map(function (x) { var hi = /agri|farm|fish|pertanian/i.test(x[0]); return '<div class="g-bar"><span>' + esc(t(x[0], x[2])) + '</span><span class="tr"><span class="fl' + (hi ? " hi" : "") + '" style="width:' + (100 * x[1] / mx).toFixed(1) + '%"></span></span><span class="v">' + (100 * x[1] / sum).toFixed(0) + "%</span></div>"; }).join("") + "</div>";
    }
    if (D.origins && D.origins.length) {
      h += '<p class="g-note">' + t("Largest nationalities: ", "Kewarganegaraan terbanyak: ") + esc(D.origins.join(", ")) + "</p>";
    }
    h += '<p class="g-note">' + t("Source: ", "Sumber: ") + (D.src || []).map(function (x) { return '<a href="' + esc(x[1]) + '">' + esc(x[0]) + "</a>"; }).join("; ") + "</p>";
    $("g-demog").innerHTML = h;
  }

  /* ---------- V. frameworks and agreements ---------- */
  var LEVELS = [["international", "International", "Internasional"], ["regional", "Regional", "Kawasan"], ["interregional", "Interregional", "Antarkawasan"], ["bilateral", "Bilateral", "Bilateral"]];
  var NATURES = [["treaty", "Binding treaty or convention", "Traktat atau konvensi mengikat"], ["agreement", "Agreement", "Perjanjian"], ["mou", "Memorandum of understanding", "Nota kesepahaman"], ["protocol", "Protocol or annex", "Protokol atau lampiran"], ["contract", "Standard contract", "Kontrak standar"], ["declaration", "Declaration or dialogue", "Deklarasi atau dialog"], ["uncoded", "Listed, type not coded", "Tercatat, jenis belum dikodekan"]];
  var lname = function (arr, k) { var x = arr.filter(function (a) { return a[0] === k; })[0]; return x ? t(x[1], x[2]) : k; };
  var AF = {s:"", level:"", nature:"", q:""};
  function bilatCount(k) { return (G.frameworks || []).filter(function (a) { return a.s === k && a.level === "bilateral"; }).length; }
  function amap() {
    var F = (G.frameworks || []).filter(function (a) { return !AF.s || a.s === AF.s; });
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
    var so = '<option value="">' + t("All six states", "Keenam negara") + "</option>" + (G.states || []).map(function (s) { return '<option value="' + s.k + '"' + (AF.s === s.k ? " selected" : "") + ">" + esc(t(s.n, s.n_id)) + "</option>"; }).join("");
    var lo = '<option value="">' + t("All levels", "Semua tingkat") + "</option>" + LEVELS.map(function (l) { return '<option value="' + l[0] + '"' + (AF.level === l[0] ? " selected" : "") + ">" + esc(t(l[1], l[2])) + "</option>"; }).join("");
    var no = '<option value="">' + t("All kinds", "Semua jenis") + "</option>" + NATURES.map(function (n) { return '<option value="' + n[0] + '"' + (AF.nature === n[0] ? " selected" : "") + ">" + esc(t(n[1], n[2])) + "</option>"; }).join("");
    $("g-atools").innerHTML = '<div><label for="af-s">' + t("Gulf state", "Negara Teluk") + '</label><select id="af-s">' + so + '</select></div><div><label for="af-l">' + t("Level", "Tingkat") + '</label><select id="af-l">' + lo + '</select></div><div><label for="af-n">' + t("Nature", "Sifat") + '</label><select id="af-n">' + no + '</select></div><div><label for="af-q">' + t("Search", "Cari") + '</label><input id="af-q" type="search" value="' + esc(AF.q) + '" placeholder="' + t("Partner or title", "Mitra atau judul") + '"></div>';
    $("af-s").onchange = function () { AF.s = this.value; agreements(); };
    $("af-l").onchange = function () { AF.level = this.value; agreements(); };
    $("af-n").onchange = function () { AF.nature = this.value; agreements(); };
    $("af-q").oninput = function () { AF.q = this.value; alist(); };
  }
  function afilter() {
    var q = AF.q.toLowerCase();
    return (G.frameworks || []).filter(function (a) {
      return (!AF.s || a.s === AF.s) && (!AF.level || a.level === AF.level) && (!AF.nature || a.nature === AF.nature) &&
        (!q || (a.partner + " " + a.title + " " + (a.scope || "")).toLowerCase().indexOf(q) >= 0);
    });
  }
  function alist() {
    var R = afilter();
    if (!(G.frameworks || []).length) { $("g-atable").innerHTML = '<tbody><tr><td class="g-empty">' + t("The list of agreements is being compiled.", "Daftar perjanjian sedang dihimpun.") + "</td></tr></tbody>"; $("g-acount").textContent = ""; return; }
    $("g-acount").textContent = fmt(R.length) + t(" of ", " dari ") + fmt(G.frameworks.length) + t(" instruments", " instrumen");
    $("g-atable").innerHTML = "<thead><tr><th>" + t("Gulf state", "Negara Teluk") + "</th><th>" + t("Partner", "Mitra") + "</th><th>" + t("Instrument", "Instrumen") + "</th><th>" + t("Level", "Tingkat") + "</th><th>" + t("Nature", "Sifat") + "</th><th>" + t("Signed / ratified", "Ditandatangani / diratifikasi") + "</th><th>" + t("In force", "Berlaku") + "</th></tr></thead><tbody>" +
      R.map(function (a) {
        return "<tr><td class=\"c\">" + esc(sname(a.s)) + "</td><td>" + esc(a.partner) + "</td><td>" + (a.url ? '<a href="' + esc(a.url) + '">' + esc(a.title) + "</a>" : esc(a.title)) + (a.scope ? '<br><span class="g-mono">' + esc(a.scope) + "</span>" : "") + '</td><td class="c">' + esc(lname(LEVELS, a.level)) + "</td><td>" + esc(lname(NATURES, a.nature)) + '</td><td class="c g-mono">' + esc(a.signed || "") + '</td><td class="c g-mono">' + esc(a.in_force || "") + "</td></tr>";
      }).join("") + "</tbody>";
  }
  function agreements() { amap(); atools(); alist(); }


  /* ---------- V-b. national laws ---------- */
  var LTOP = [["labor","Labor","Ketenagakerjaan"],["domestic work","Domestic work","Kerja rumah tangga"],["residence/sponsorship","Residence and sponsorship","Izin tinggal dan sponsor"],["wages","Wages","Upah"],["OSH/heat","Safety and heat","Keselamatan dan panas"],["trafficking","Trafficking","Perdagangan orang"],["social security","Social security","Jaminan sosial"],["disputes","Disputes","Sengketa"],["recruitment","Recruitment","Rekrutmen"],["equality","Constitution and equality","Konstitusi dan kesetaraan"]];
  var LTYP = [["constitution","Constitution","Konstitusi"],["statute","Statute","Undang-undang"],["regulation","Regulation","Peraturan"],["decision","Decision","Keputusan"],["policy","Policy","Kebijakan"]];
  var LF = {s:"", topic:"", type:"", q:""};
  function laws() {
    var L = G.laws || []; if (!$("g-ltools")) return;
    var so = '<option value="">' + t("All six states", "Keenam negara") + "</option>" + (G.states || []).map(function (s) { return '<option value="' + s.k + '"' + (LF.s === s.k ? " selected" : "") + ">" + esc(t(s.n, s.n_id)) + "</option>"; }).join("");
    var to = '<option value="">' + t("All topics", "Semua topik") + "</option>" + LTOP.map(function (x) { return '<option value="' + x[0] + '"' + (LF.topic === x[0] ? " selected" : "") + ">" + esc(t(x[1], x[2])) + "</option>"; }).join("");
    var ty = '<option value="">' + t("All types", "Semua jenis") + "</option>" + LTYP.map(function (x) { return '<option value="' + x[0] + '"' + (LF.type === x[0] ? " selected" : "") + ">" + esc(t(x[1], x[2])) + "</option>"; }).join("");
    $("g-ltools").innerHTML = '<div><label for="lf-s">' + t("Gulf state", "Negara Teluk") + '</label><select id="lf-s">' + so + '</select></div><div><label for="lf-t">' + t("Topic", "Topik") + '</label><select id="lf-t">' + to + '</select></div><div><label for="lf-y">' + t("Type", "Jenis") + '</label><select id="lf-y">' + ty + '</select></div><div><label for="lf-q">' + t("Search", "Cari") + '</label><input id="lf-q" type="search" value="' + esc(LF.q) + '" placeholder="' + t("Title, number or group", "Judul, nomor atau kelompok") + '"></div>';
    $("lf-s").onchange = function () { LF.s = this.value; laws(); };
    $("lf-t").onchange = function () { LF.topic = this.value; laws(); };
    $("lf-y").onchange = function () { LF.type = this.value; laws(); };
    $("lf-q").oninput = function () { LF.q = this.value; ltable(); };
    ltable();
  }
  function ltable() {
    var L = G.laws || [], q = LF.q.toLowerCase();
    var R = L.filter(function (r) { return (!LF.s || r.s === LF.s) && (!LF.topic || r.topic === LF.topic) && (!LF.type || r.type === LF.type) && (!q || (r.title + " " + r.orig + " " + r.no + " " + r.groups).toLowerCase().indexOf(q) >= 0); });
    $("g-lcount").textContent = fmt(R.length) + t(" of ", " dari ") + fmt(L.length) + t(" instruments", " instrumen");
    var LK = {text: t("text", "teks"), db: t("database", "basis data"), glmm: "GLMM (secondary)", guidance: t("official guidance", "panduan resmi")};
    $("g-ltable").innerHTML = "<thead><tr><th>" + t("Gulf state", "Negara Teluk") + "</th><th>" + t("Instrument", "Instrumen") + "</th><th>" + t("Year", "Tahun") + "</th><th>" + t("Type", "Jenis") + "</th><th>" + t("Topic", "Topik") + "</th><th>" + t("Who it covers", "Siapa yang dicakup") + "</th><th>" + t("Link", "Tautan") + "</th></tr></thead><tbody>" +
      R.map(function (r) {
        return '<tr><td class="c">' + esc(sname(r.s)) + "</td><td>" + esc(r.title) + (r.no ? '<br><span class="g-mono">' + esc(r.no) + "</span>" : "") + (r.orig ? '<br><span dir="rtl" lang="ar">' + esc(r.orig) + "</span>" : "") + '</td><td class="c g-mono">' + esc(r.year) + (r.amended ? "<br>" + t("amended ", "diubah ") + esc(r.amended) : "") + "</td><td>" + esc(lname(LTYP, r.type)) + "</td><td>" + esc(lname(LTOP, r.topic)) + "</td><td>" + esc(r.groups) + '</td><td class="c">' + (r.url ? '<a href="' + esc(r.url) + '">' + esc(LK[r.link] || r.link) + "</a>" : "") + (r.checked === "yes" ? "" : '<br><span class="g-mono">' + t("unchecked", "belum dicek") + "</span>") + "</td></tr>";
      }).join("") + "</tbody>";
  }

  /* ---------- VI. corridors ---------- */
  var curC = "SA";
  function corridors() {
    stateBtns($("g-cstates"), curC, function (k) { curC = k; corridors(); });
    var R = (G.stock || []).filter(function (r) { return r.s === curC; }).sort(function (a, b) { return b.v - a.v; }).slice(0, 15);
    if (!R.length) { $("g-corr").innerHTML = '<p class="g-empty">' + t("Corridor figures are being compiled.", "Data koridor sedang dihimpun.") + "</p>"; return; }
    var mx = R[0].v;
    $("g-corr").innerHTML = R.map(function (r) {
      var n = (G.frameworks || []).filter(function (a) { return a.s === curC && a.level === "bilateral" && a.partner === r.o; }).length;
      return '<div class="g-bar"><span>' + esc(r.o) + (n ? ' <span class="g-mono" title="' + t("bilateral instruments", "instrumen bilateral") + '">· ' + n + "</span>" : "") + '</span><span class="tr"><span class="fl' + (n ? " hi" : "") + '" style="width:' + (100 * r.v / mx).toFixed(1) + '%"></span></span><span class="v">' + (r.v >= 1e6 ? (r.v / 1e6).toFixed(1) + "M" : Math.round(r.v / 1e3) + "k") + "</span></div>";
    }).join("") + '<p class="g-note">' + t("The number after a country is how many bilateral instruments are on record.", "Angka setelah nama negara adalah jumlah instrumen bilateral yang tercatat.") + (function () { var s = (G.states || []).filter(function (x) { return x.k === curC; })[0]; return s && s.remit != null ? " " + t("Remittances paid from this state in ", "Remitansi yang dikirim dari negara ini pada ") + s.remit_y + ": US$ " + s.remit.toFixed(1) + t(" billion (World Bank). Income gaps and origin conditions per corridor are in the corridor tests below.", " miliar (World Bank). Kesenjangan pendapatan dan kondisi negara asal per koridor ada di uji koridor di bawah.") : ""; })() + "</p>";
  }

  /* ---------- VII. statistics ---------- */
  function stats() {
    if (!window.IMRStats || !(G.corr || []).length) return;
    var SN = {}; (G.states || []).forEach(function (s) { SN[s.n] = s.n_id; });
    IMRStats.mount($("g-stats"), {
      rows: G.corr, filename: "gcc-corridors", idLabel: "corridor",
      vars: G.corr_vars || [], presets: G.corr_presets || [], defaults: G.corr_defaults || {},
      note: G.corr_note, note_id: G.corr_note_id
    });
  }

  /* ---------- VIII. reforms ---------- */
  var RF = "";
  var KIND = {real:["Real change","Perubahan nyata"], partial:["Partial or limited","Sebagian atau terbatas"], law:["New law or rules","Hukum atau aturan baru"], origin:["Sending-country measure","Kebijakan negara pengirim"]};
  function reforms() {
    var ks = ["SA", "AE", "QA", "KW", "BH", "OM", "ID"];
    $("g-rfilter").innerHTML = '<button type="button" class="g-btn" data-r="" aria-pressed="' + (RF === "") + '">' + t("All", "Semua") + "</button>" + ks.map(function (k) { return '<button type="button" class="g-btn" data-r="' + k + '" aria-pressed="' + (RF === k) + '">' + esc(k === "ID" ? "Indonesia" : sname(k)) + "</button>"; }).join("");
    $("g-rfilter").onclick = function (e) { var b = e.target.closest("[data-r]"); if (b) { RF = b.getAttribute("data-r"); reforms(); } };
    var MO = ID() ? ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"] : ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    $("g-tl").innerHTML = (G.reforms || []).filter(function (r) { return !RF || r[1] === RF; }).map(function (r) {
      var d = r[0].split("-");
      return '<li class="' + r[4] + '"><span class="d">' + MO[+d[1] - 1] + " " + d[0] + " · " + esc(r[1] === "ID" ? "Indonesia" : sname(r[1])) + " · " + esc(t(KIND[r[4]][0], KIND[r[4]][1])) + "</span><br>" + esc(t(r[2], r[3])) + "</li>";
    }).join("");
    $("g-tlleg").innerHTML = '<span class="g-mono">' + esc(t(G.reform_src || "", "Ringkasan IMR dari hukum dan sumber sekunder di bagian Sumber; bulan bersifat perkiraan bila laporan berbeda.")) + "</span>";
  }

  /* ---------- X. sources and downloads ---------- */
  function csv(rows, cols) { return cols.join(",") + "\n" + rows.map(function (r) { return cols.map(function (c) { var v = r[c] == null ? "" : String(r[c]); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }).join(","); }).join("\n"); }
  function save(name, text, type) { var b = new Blob([text], {type: type}), a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = name; document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500); }
  function sources() {
    var D = [["fw", t("Frameworks and agreements (CSV)", "Kerangka dan perjanjian (CSV)")], ["lw", t("National laws (CSV)", "Hukum nasional (CSV)")], ["st", t("Country profiles (CSV)", "Profil negara (CSV)")], ["co", t("Corridors (CSV)", "Koridor (CSV)")], ["rf", t("Reform tracker (CSV)", "Pelacak reformasi (CSV)")], ["pv", t("Coded cells with sources (CSV)", "Sel berkode dengan sumber (CSV)")], ["cbc", t("Codebook (CSV)", "Buku kode (CSV)")], ["cb", t("Codebook and change log (TXT)", "Buku kode dan log perubahan (TXT)")], ["js", t("Everything (JSON)", "Semua (JSON)")]];
    $("g-dls").innerHTML = D.map(function (d) { return '<button type="button" class="g-btn dl" data-d="' + d[0] + '">' + esc(d[1]) + "</button>"; }).join("");
    $("g-dls").onclick = function (e) {
      var b = e.target.closest("[data-d]"); if (!b) return; var k = b.getAttribute("data-d");
      if (k === "fw") save("imr-gcc-frameworks.csv", csv(G.frameworks || [], ["s", "partner", "title", "level", "nature", "signed", "in_force", "scope", "src", "url"]), "text/csv");
      if (k === "lw") save("imr-gcc-national-laws.csv", csv(G.laws || [], ["s", "title", "orig", "no", "year", "amended", "type", "topic", "groups", "url", "link", "checked"]), "text/csv");
      if (k === "st") save("imr-gcc-profiles.csv", csv(G.states || [], ["k", "n", "law", "farm", "farm_t", "dw", "dw2017", "mobility", "mob_t", "minwage", "mw_t", "wps", "union", "heat", "icescr", "p29", "complaints", "ilo_not", "remit", "remit_y"]), "text/csv");
      if (k === "co") save("imr-gcc-corridors.csv", csv(G.corr || [], Object.keys((G.corr || [{}])[0] || {})), "text/csv");
      if (k === "rf") save("imr-gcc-reforms.csv", csv((G.reforms || []).map(function (r) { return {date:r[0], state:r[1], change:r[2], kind:r[4]}; }), ["date", "state", "change", "kind"]), "text/csv");
      if (k === "pv") save("imr-gulf-coded-cells.csv", csv((G.prov || []).map(function (r) { var st = (G.states || []).filter(function (x) { return x.k === r[0]; })[0] || {}; return {state:r[0], feature:r[1], coding:st[r[1]], basis:r[2], source:r[3], checked:r[4]}; }), ["state", "feature", "coding", "basis", "source", "checked"]), "text/csv");
      if (k === "cbc") { var c = document.createElement("a"); c.href = "/gcc/data/codebook.csv"; c.download = "imr-gulf-codebook.csv"; document.body.appendChild(c); c.click(); c.remove(); }
      if (k === "cb") save("imr-gulf-codebook.txt", "Migrant workers in the Gulf states: migration and labor laws in comparison. Version " + G.version + ", " + G.updated + "\nInstitute for Migrant Rights. https://theimr.org/gcc/\n\nUNIT OF ANALYSIS: the legal framework of each state on paper (de jure).\n\nCODEBOOK\n" + [].slice.call(document.querySelectorAll("#g-codebook tbody tr")).map(function (tr) { return [].slice.call(tr.cells).map(function (c) { return c.textContent; }).join(" | "); }).join("\n") + "\n\nBASIS: P = primary legal text; S = secondary source.\n\nCHANGE LOG\n" + (G.changelog || []).map(function (c) { return c.join(" | "); }).join("\n") + "\n", "text/plain");
      if (k === "js") save("imr-gulf-states.json", JSON.stringify({source: "Institute for Migrant Rights, Gulf States migration and labor laws in comparison", version: G.version, updated: G.updated, provenance: G.prov, states: G.states, frameworks: G.frameworks, laws: G.laws, stock: G.stock, demography: G.demog, corridors: G.corr, reforms: G.reforms}, null, 2), "application/json");
    };
    $("g-src").innerHTML = "<ul>" + (G.sources || []).map(function (s) { return '<li><a href="' + esc(s[1]) + '">' + esc(s[0]) + "</a>" + (s[2] ? " · " + esc(t(s[2], s[3])) : "") + "</li>"; }).join("") + "</ul>" +
      '<p class="g-mono">' + t("Updated ", "Diperbarui ") + esc(G.updated || "") + "</p>";
  }

  function all() { glance(); weights(); rank(); profile(); demog(); agreements(); laws(); corridors(); reforms(); codebook(); prov(); if ($("g-robust-d").open) robust(); sources(); }
  document.addEventListener("DOMContentLoaded", function () {
    all(); stats();
    $("g-robust-d").addEventListener("toggle", function () { if (this.open) robust(); });
    $("g-weights").addEventListener("input", function (e) { var k = e.target.getAttribute("data-w"); if (!k) return; W[k] = +e.target.value; $("w-" + k).textContent = W[k]; rank(); });
    new MutationObserver(function () { all(); }).observe(document.documentElement, {attributes: true, attributeFilter: ["lang"]});
  });
})();
