/* Court decisions on migration: renders three views of window.CD (cd-data.js) and one decision panel.
   Views: by situation, by argument, along the journey, compare (groups with Fisher/chi-square tests, or decisions side by side). EN/ID follows the site language switch. */
(function () {
  "use strict";
  var CD = window.CD || {decisions: [], args: [], codebook: []};
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); };
  var ID = function () { return document.documentElement.lang === "id"; };
  var t = function (en, id) { return ID() && id ? id : en; };

  var COUNTRY = {ID: ["Indonesia", "Indonesia"], PH: ["Philippines", "Filipina"], HK: ["Hong Kong", "Hong Kong"], MM: ["Myanmar", "Myanmar"], EG: ["Egypt", "Mesir"], UG: ["Uganda", "Uganda"], GH: ["Ghana", "Ghana"], MO: ["Macau", "Makau"], KR: ["South Korea", "Korea Selatan"], IN: ["India", "India"], IL: ["Israel", "Israel"], ZA: ["South Africa", "Afrika Selatan"], GR: ["Greece", "Yunani"], CY: ["Cyprus and Russia", "Siprus dan Rusia"], FR: ["France", "Prancis"], GB: ["United Kingdom", "Inggris"], US: ["United States", "Amerika Serikat"], MX: ["Mexico", "Meksiko"], XM: ["Americas (requested by Mexico)", "Amerika (atas permintaan Meksiko)"], XA: ["Americas (requested by Argentina, Brazil, Paraguay and Uruguay)", "Amerika (atas permintaan Argentina, Brasil, Paraguay dan Uruguay)"], ES: ["Spain", "Spanyol"], PA: ["Panama", "Panama"], DO: ["Dominican Republic", "Republik Dominika"], AR: ["Argentina", "Argentina"], CO: ["Colombia", "Kolombia"], NP: ["Nepal", "Nepal"], LK: ["Sri Lanka", "Sri Lanka"], MY: ["Malaysia", "Malaysia"], SG: ["Singapore", "Singapura"], TH: ["Thailand", "Thailand"], KW: ["Kuwait", "Kuwait"], TW: ["Taiwan", "Taiwan"], JP: ["Japan", "Jepang"], PK: ["Pakistan", "Pakistan"], LB: ["Lebanon", "Lebanon"], KE: ["Kenya", "Kenya"], ZM: ["Zambia", "Zambia"], NA: ["Namibia", "Namibia"], NG: ["Nigeria", "Nigeria"], AO: ["Angola", "Angola"], RW: ["Rwanda", "Rwanda"], GN: ["Guinea", "Guinea"], BW: ["Botswana", "Botswana"], TZ: ["Tanzania", "Tanzania"], ZW: ["Zimbabwe", "Zimbabwe"], BR: ["Brazil", "Brasil"], BO: ["Bolivia", "Bolivia"], NI: ["Nicaragua", "Nikaragua"], PE: ["Peru", "Peru"], EC: ["Americas (requested by Ecuador)", "Amerika (atas permintaan Ekuador)"], BD: ["Bangladesh", "Bangladesh"], CD: ["Guinea and DR Congo", "Guinea dan RD Kongo"], QA: ["Qatar", "Qatar"], CA: ["Canada", "Kanada"], MR: ["Mauritania", "Mauritania"], SA: ["Saudi Arabia", "Arab Saudi"], AE: ["United Arab Emirates", "Uni Emirat Arab"], OM: ["Oman", "Oman"], BH: ["Bahrain", "Bahrain"], AT: ["Austria", "Austria"], LV: ["Latvia", "Latvia"], BG: ["Bulgaria", "Bulgaria"], DK: ["Denmark", "Denmark"], IT: ["Italy", "Italia"], BE: ["Belgium", "Belgia"], SI: ["Slovenia", "Slovenia"], NL: ["Netherlands", "Belanda"], AZ: ["Azerbaijan", "Azerbaijan"], NE: ["Niger", "Niger"], PG: ["Papua New Guinea", "Papua Nugini"], AU: ["Australia", "Australia"], NZ: ["New Zealand", "Selandia Baru"], CH: ["Switzerland", "Swiss"], SR: ["Suriname", "Suriname"], CL: ["Chile", "Cile"], CI: ["Côte d’Ivoire", "Pantai Gading"], HR: ["Croatia", "Kroasia"], HU: ["Hungary", "Hongaria"], KZ: ["Kazakhstan", "Kazakhstan"], LS: ["Lesotho", "Lesotho"], MA: ["Morocco", "Maroko"], MW: ["Malawi", "Malawi"], SE: ["Sweden", "Swedia"], TJ: ["Tajikistan", "Tajikistan"]};
  var BR = {criminal: ["Criminal", "Pidana"], "private": ["Private (labor, contract, tort)", "Perdata (ketenagakerjaan, kontrak, perbuatan melawan hukum)"], administrative: ["Administrative", "Administrasi"], constitutional: ["Constitutional and human rights", "Konstitusi dan hak asasi manusia"]};
  /* National legislation linked from decisions of the same country (also listed in the Migration Law Atlas). */
  var LAWS = {AO: [{en: "Law on the Legal Regime of Foreign Citizens (2007; replaced Law 3/94)", id: "Undang-Undang tentang Rezim Hukum Warga Negara Asing (2007; menggantikan UU 3/94)", u: "https://www.saflii.org/ao/legis/num_act/lotlrofc356.pdf"}]};
  function lawsBlock(d) {
    var L = LAWS[d.cc]; if (!L) return "";
    return '<p class="cd-flab">' + esc(t("Related legislation", "Peraturan terkait")) + '</p><ul class="cd-srcl">' + L.map(function (x) { return '<li><a href="' + esc(x.u) + '" rel="noopener">' + esc(t(x.en, x.id)) + '</a> · <a href="/migration-law/">' + esc(t("in the Migration Law Atlas", "di Atlas Hukum Migrasi")) + "</a></li>"; }).join("") + "</ul>";
  }
  var TIER = {national: ["National court", "Pengadilan nasional"], regional: ["Regional court", "Pengadilan kawasan"], international: ["International body", "Badan internasional"]};
  var FORUM = {destination: ["in the destination country", "di negara tujuan"], origin: ["in the country of origin", "di negara asal"]};
  var isC = function (d) { return d.status === "C"; };
  var OUT = {unknown: ["Outcome to be checked", "Hasil perlu diperiksa"], won: ["Worker side won", "Pihak pekerja menang"], lost: ["Worker side lost", "Pihak pekerja kalah"], advisory: ["Advisory: rights affirmed", "Nasihat: hak ditegaskan"]};
  var FOL = {carried: ["Carried out", "Dilaksanakan"], partly: ["Partly carried out", "Sebagian dilaksanakan"], not: ["Not carried out", "Tidak dilaksanakan"], unknown: ["Not yet known", "Belum diketahui"], none: ["Nothing to carry out", "Tidak ada yang perlu dilaksanakan"]};
  var FOLC = {carried: "#134A33", partly: "#6F8A7D", not: "#B2C7BC", unknown: "#FFFFFF", none: "#DCE8E1"};
  var SIT = [
    ["wages", "Wages not paid", "Upah tidak dibayar"], ["passport", "Passport kept by employer", "Paspor ditahan majikan"],
    ["employer", "Could not change employer", "Tidak bisa pindah majikan"], ["dismissed", "Dismissed or sent home", "Dipecat atau dipulangkan"],
    ["forced", "Forced labour or trafficking", "Kerja paksa atau perdagangan orang"], ["injury", "Hurt or injured at work", "Terluka saat bekerja"],
    ["fees", "Recruitment and the agency", "Perekrutan dan agen"], ["union", "Joining a union", "Bergabung dengan serikat"],
    ["discrimination", "Treated worse as a foreigner", "Diperlakukan lebih buruk sebagai orang asing"], ["housing", "Living in the employer’s home", "Tinggal di rumah majikan"],
    ["residence", "Residence and staying on", "Izin tinggal dan menetap"], ["arrest", "Arrested, detained or expelled", "Ditangkap, ditahan atau diusir"], ["health", "Health care", "Layanan kesehatan"],
    ["coverage", "Who the law protects", "Siapa yang dilindungi hukum"], ["welfare", "Food and support in a crisis", "Pangan dan bantuan saat krisis"]
  ];
  var STAGE = [
    [1, "Recruitment at home", "Perekrutan di dalam negeri", "Fees, agencies, false promises", "Biaya, agen, janji palsu"],
    [2, "Leaving the country", "Berangkat ke luar negeri", "Exit rules, visas, documents", "Aturan keberangkatan, visa, dokumen"],
    [3, "Working abroad", "Bekerja di luar negeri", "Wages, hours, passport, abuse, unions", "Upah, jam kerja, paspor, kekerasan, serikat"],
    [4, "Changing or losing the job", "Pindah atau kehilangan pekerjaan", "Changing employer, dismissal", "Pindah majikan, pemecatan"],
    [5, "Return and after", "Pulang dan sesudahnya", "Claims from home, residence", "Tuntutan dari rumah, izin tinggal"]
  ];
  var PRI = {asia: 0, africa: 0, mideast: 0, latam: 0, gulf: 0, pacific: 0, intl: 1, americas: 2, europe: 2};

  var S = {view: "situation", tier: "all", forum: "all", br: "all", tool: "all", sit: "all", stage: 3, open: null, argOpen: null};
  var all = (CD.decisions || []).slice().sort(function (a, b) {
    return (PRI[a.region] - PRI[b.region]) || ((a.status === "C") - (b.status === "C")) || (a.date < b.date ? 1 : a.date > b.date ? -1 : 0);
  });
  var byId = {}; all.forEach(function (d) { byId[d.id] = d; });
  var argOf = {}; (CD.args || []).forEach(function (a) { argOf[a.k] = a; });
  var toolOf = {}; (CD.tools || []).forEach(function (a) { toolOf[a.k] = a; });

  function cname(d) { var c = COUNTRY[d.cc]; return c ? t(c[0], c[1]) : d.cc; }
  function year(d) { return String(d.date).slice(0, 4); }
  function fdate(s) {
    if (!/^\d{4}-\d{2}(-\d{2})?$/.test(s)) return s;
    var p = s.split("-"), dt = new Date(Date.UTC(+p[0], +p[1] - 1, p[2] ? +p[2] : 1));
    var o = p[2] ? {day: "numeric", month: "long", year: "numeric", timeZone: "UTC"} : {month: "long", year: "numeric", timeZone: "UTC"};
    return dt.toLocaleDateString(ID() ? "id-ID" : "en-GB", o);
  }
  function visible() {
    return all.filter(function (d) {
      return (S.tier === "all" || d.tier === S.tier) && (S.forum === "all" || d.forum === S.forum) && (S.br === "all" || d.branch === S.br) && (S.tool === "all" || (d.tools || []).indexOf(S.tool) >= 0);
    });
  }
  function pill(txt, cls) { return '<span class="cd-pill ' + (cls || "") + '">' + esc(txt) + "</span>"; }
  function aipill(txt, cls) { return '<a class="cd-pill ' + (cls || "") + '" href="/ai-use/#composition">' + esc(txt) + "</a>"; }
  function meta(d) {
    var tier = t(TIER[d.tier][0], TIER[d.tier][1]);
    var where = d.tier === "national" && FORUM[d.forum] ? " " + t(FORUM[d.forum][0], FORUM[d.forum][1]) : "";
    return esc(tier + where) + " · " + esc(t(BR[d.branch][0], BR[d.branch][1])) + " · " + esc(cname(d)) + " · " + esc(year(d));
  }
  var isRef = function (d) { return d.region === "europe" || d.region === "americas"; };
  var isEchr = function (d) { return /European Court of Human Rights/.test(d.court); };
  var LIB = ["CA", "US", "GB", "AU", "NZ", "FR", "ES", "IE", "DE", "NL", "BE", "IT"];
  var isLib = function (d) { return d.tier === "national" && LIB.indexOf(d.cc) >= 0; };
  function closest(d, pool, k) {
    var ak = d.args.map(function (x) { return x.a; });
    var score = function (e) { return 3 * e.args.filter(function (x) { return ak.indexOf(x.a) >= 0; }).length + e.situations.filter(function (x) { return d.situations.indexOf(x) >= 0; }).length + e.stages.filter(function (x) { return d.stages.indexOf(x) >= 0; }).length * 0.5; };
    return all.filter(pool).filter(function (e) { return e.id !== d.id && !isC(e); }).map(function (e) { return {e: e, s: score(e)}; }).filter(function (x) { return x.s >= 1; }).sort(function (a, b) { return b.s - a.s; }).slice(0, k).map(function (x) { return x.e; });
  }
  function comparators(d) {
    if (isEchr(d) || isLib(d)) return [];
    var out = [];
    closest(d, isEchr, 1).forEach(function (e) { out.push([t("European Court of Human Rights", "Mahkamah HAM Eropa"), e]); });
    closest(d, isLib, 1).forEach(function (e) { out.push([t("National court of a liberal democracy", "Pengadilan nasional negara demokrasi liberal") + " (" + cname(e) + ")", e]); });
    return out;
  }
  /* Decisions are listed as compact rows; each row opens in place to show the summary, holding and sources. */
  S.limit = 25;
  function cards(list) {
    var main = list.filter(function (d) { return !isRef(d); }), ref = list.filter(isRef);
    var shown = main.slice(0, S.limit), rest = main.length - shown.length;
    return (main.length ? '<div class="cd-rows">' + shown.map(card).join("") + "</div>" : "") +
      (rest > 0 ? '<div class="g-acts"><button type="button" class="g-btn" data-more>' + esc(t("Show " + Math.min(rest, 25) + " more (" + rest + " not shown)", "Tampilkan " + Math.min(rest, 25) + " lagi (" + rest + " belum ditampilkan)")) + "</button></div>" : "") +
      (ref.length ? '<details class="cd-refs"><summary>' + esc(t("For comparison: European Court of Human Rights and courts of Canada, the US and Europe", "Sebagai pembanding: Mahkamah HAM Eropa dan pengadilan Kanada, AS dan Eropa")) + " (" + ref.length + ')</summary><div class="cd-rows">' + ref.map(card).join("") + "</div></details>" : "");
  }
  function card(d) {
    var c = isC(d);
    var status = c ? pill(t("Unchecked candidate", "Kandidat belum diperiksa"), "s-C") : pill(t(OUT[d.outcome][0], OUT[d.outcome][1]), "o-" + d.outcome);
    var body = '<p class="cd-meta">' + meta(d) + (isRef(d) ? " " + pill(t("Comparison", "Pembanding"), "ref") : "") + "</p>" +
      '<p class="cd-court">' + esc(d.court) + (d.cite ? " · " + esc(d.cite) : "") + "</p>" +
      "<p>" + esc(t(d.plain, d.plain_id)) + "</p>" +
      (c ? '<p class="cd-pills">' + aipill(t("Unchecked candidate: not yet verified", "Kandidat belum diperiksa: belum diverifikasi"), "s-C") + "</p>" :
        (d.q ? '<p><b>' + esc(t("Question", "Pertanyaan")) + ".</b> " + esc(t(d.q, d.q_id)) + "</p>" : "") +
        (d.held ? '<p><b>' + esc(t("Decided", "Diputuskan")) + ".</b> " + esc(d.held) + "</p>" : "") +
        '<p class="cd-pills">' + pill(t(OUT[d.outcome][0], OUT[d.outcome][1]), "o-" + d.outcome) + pill(t("After: ", "Sesudahnya: ") + t(FOL[d.follow][0], FOL[d.follow][1]), "f-" + d.follow) + aipill(t("Unverified: being checked", "Belum diverifikasi: sedang diperiksa"), "s-S") + "</p>") +
      '<p class="cd-flab">' + esc(t("Sources", "Sumber")) + '</p><ul class="cd-srcl">' + d.src.map(function (s) { return '<li><a href="' + esc(s.u) + '" rel="noopener">' + esc(s.t) + "</a></li>"; }).join("") + "</ul>" + lawsBlock(d) +
      '<p class="cd-ract"><a href="#d/' + esc(d.id) + '" data-open="' + esc(d.id) + '">' + esc(t("Open the full page", "Buka halaman lengkap")) + "</a>" +
      (c ? "" : ' <button type="button" class="cd-link" data-addcmp="' + esc(d.id) + '">' + esc(t("Compare", "Bandingkan")) + "</button>") + "</p>";
    return '<details class="cd-row' + (c ? " cd-cand" : "") + '"><summary><span class="cd-rn">' + esc(d.name) + '</span><span class="cd-rm">' + esc(cname(d)) + " · " + esc(year(d)) + " · " + esc(t(BR[d.branch][0], BR[d.branch][1])) + '</span><span class="cd-rp">' + status + '</span></summary><div class="cd-rb">' + body + "</div></details>";
  }

  /* ---------- filters (shared by all views) ---------- */
  function filters() {
    var tiers = [["all", "All levels", "Semua tingkat"], ["national", "National", "Nasional"], ["regional", "Regional", "Kawasan"], ["international", "International", "Internasional"]];
    var fora = [["all", "Destination and origin", "Tujuan dan asal"], ["destination", "Destination country", "Negara tujuan"], ["origin", "Country of origin", "Negara asal"]];
    var v = all;
    var cnt = function (k) { return k === "all" ? v.length : v.filter(function (d) { return d.tier === k; }).length; };
    var h = '<div class="cd-frow"><span class="cd-flab">' + esc(t("Level of court", "Tingkat pengadilan")) + '</span><div class="g-btns" role="group" aria-label="' + esc(t("Level of court", "Tingkat pengadilan")) + '">' +
      tiers.map(function (x) { return '<button type="button" class="g-btn" data-tier="' + x[0] + '" aria-pressed="' + (S.tier === x[0]) + '">' + esc(t(x[1], x[2])) + " (" + cnt(x[0]) + ")</button>"; }).join("") + "</div></div>";
    if (S.tier === "all" || S.tier === "national") {
      h += '<div class="cd-frow"><span class="cd-flab">' + esc(t("National courts", "Pengadilan nasional")) + '</span><div class="g-btns" role="group" aria-label="' + esc(t("Where the national court sits", "Letak pengadilan nasional")) + '">' +
        fora.map(function (x) { return '<button type="button" class="g-btn" data-forum="' + x[0] + '" aria-pressed="' + (S.forum === x[0]) + '">' + esc(t(x[1], x[2])) + "</button>"; }).join("") + "</div></div>";
    }
    var brs = [["all", "All types", "Semua jenis"]].concat(["criminal", "private", "administrative", "constitutional"].map(function (k) { return [k, BR[k][0], BR[k][1]]; }));
    var bc = function (k) { return k === "all" ? v.length : v.filter(function (d) { return d.branch === k; }).length; };
    h += '<div class="cd-frow"><span class="cd-flab">' + esc(t("Type of case", "Jenis perkara")) + '</span><div class="g-btns" role="group" aria-label="' + esc(t("Type of case", "Jenis perkara")) + '">' +
      brs.map(function (x) { return '<button type="button" class="g-btn" data-br="' + x[0] + '" aria-pressed="' + (S.br === x[0]) + '">' + esc(t(x[1], x[2])) + " (" + bc(x[0]) + ")</button>"; }).join("") + "</div></div>";
    var tc = function (k) { return v.filter(function (d) { return (d.tools || []).indexOf(k) >= 0; }).length; };
    h += '<div class="cd-frow"><span class="cd-flab">' + esc(t("Reasoning tool", "Alat penalaran")) + '</span><select id="cd-tool" aria-label="' + esc(t("Reasoning tool", "Alat penalaran")) + '"><option value="all">' + esc(t("All reasoning tools", "Semua alat penalaran")) + "</option>" +
      (CD.tools || []).map(function (x) { return '<option value="' + x.k + '"' + (S.tool === x.k ? " selected" : "") + ">" + esc(t(x.en, x.id)) + " (" + tc(x.k) + ")</option>"; }).join("") + '</select> <a class="g-note" href="#cd-reasoning" style="margin:0">' + esc(t("What these are", "Apa artinya")) + "</a></div>";
    $("cd-filters").innerHTML = h;
  }

  /* ---------- view 1: by situation ---------- */
  function vSituation() {
    var v = visible();
    var n = function (k) { return k === "all" ? v.length : v.filter(function (d) { return d.situations.indexOf(k) >= 0; }).length; };
    var h = '<h2 class="cd-vh">' + esc(t("Start from what happened", "Mulai dari apa yang terjadi")) + "</h2>" +
      '<p class="g-note" style="margin-top:0">' + esc(t("Pick the situation closest to yours. The focus is on courts in Asia, Africa, the Middle East and Latin America; European and United States decisions follow as comparison points.", "Pilih situasi yang paling mirip dengan anda. Fokusnya pengadilan di Asia, Afrika, Timur Tengah dan Amerika Latin; putusan Eropa dan Amerika Serikat menyusul sebagai pembanding.")) + "</p>" +
      '<div class="cd-chips" role="group" aria-label="' + esc(t("Situation", "Situasi")) + '"><button type="button" class="cd-chip" data-sit="all" aria-pressed="' + (S.sit === "all") + '">' + esc(t("All situations", "Semua situasi")) + " (" + n("all") + ")</button>" +
      SIT.map(function (s) { return '<button type="button" class="cd-chip" data-sit="' + s[0] + '" aria-pressed="' + (S.sit === s[0]) + '">' + esc(t(s[1], s[2])) + " (" + n(s[0]) + ")</button>"; }).join("") + "</div>";
    var list = S.sit === "all" ? v : v.filter(function (d) { return d.situations.indexOf(S.sit) >= 0; });
    h += list.length ? cards(list) :
      empty("No decision in this collection yet for this situation and level of court. That gap is worth knowing.", "Belum ada putusan dalam koleksi ini untuk situasi dan tingkat pengadilan ini. Kekosongan itu penting diketahui.");
    return h;
  }

  /* ---------- view 2: by argument ---------- */
  function vArgument() {
    var v = visible();
    var rows = (CD.args || []).map(function (a) {
      var used = v.filter(function (d) { return d.args.some(function (x) { return x.a === a.k; }); });
      var ok = used.filter(function (d) { return d.args.some(function (x) { return x.a === a.k && x.ok; }); });
      return {a: a, used: used, ok: ok};
    }).filter(function (r) { return r.used.length; }).sort(function (x, y) { return y.used.length - x.used.length; });
    var h = '<h2 class="cd-vh">' + esc(t("Which arguments persuade courts?", "Argumen mana yang meyakinkan pengadilan?")) + "</h2>" +
      '<p class="g-note" style="margin-top:0">' + esc(t("Each row is a legal argument made for migrant workers, with how often the decisions here accepted it. Counts describe this collection only, not all litigation, so they are not success rates.", "Setiap baris adalah argumen hukum yang diajukan untuk pekerja migran, dengan berapa kali putusan di sini menerimanya. Angka hanya menggambarkan koleksi ini, bukan seluruh perkara, jadi bukan tingkat keberhasilan.")) + "</p>";
    if (!rows.length) return h + empty("No argument recorded for this level of court yet.", "Belum ada argumen untuk tingkat pengadilan ini.");
    h += '<div class="g-scroll"><table class="g-t cd-at"><thead><tr><th scope="col">' + esc(t("Argument", "Argumen")) + '</th><th scope="col">' + esc(t("Accepted / tried", "Diterima / diajukan")) + '</th><th scope="col">' + esc(t("Where tried", "Di mana diajukan")) + '</th><th scope="col">' + esc(t("Decisions", "Putusan")) + "</th></tr></thead><tbody>";
    rows.forEach(function (r) {
      var pct = Math.round(100 * r.ok.length / r.used.length);
      var where = r.used.map(function (d) { return cname(d); }).filter(function (x, i, A) { return A.indexOf(x) === i; }).join(", ");
      var open = S.argOpen === r.a.k;
      h += "<tr><td><b>" + esc(t(r.a.en, r.a.id)) + '</b><br><span class="g-mono">' + esc(r.a.law) + "</span></td>" +
        '<td class="c"><span class="cd-bar" role="img" aria-label="' + r.ok.length + " / " + r.used.length + '"><span style="width:' + pct + '%"></span></span><span class="g-mono">' + r.ok.length + " / " + r.used.length + "</span></td>" +
        "<td>" + esc(where) + '</td><td><button type="button" class="cd-link" data-arg="' + esc(r.a.k) + '" aria-expanded="' + open + '">' + esc(open ? t("Hide", "Tutup") : t("Show", "Lihat")) + " (" + r.used.length + ")</button></td></tr>";
      if (open) {
        var li = function (d) { return '<li><a href="#d/' + esc(d.id) + '" data-open="' + esc(d.id) + '">' + esc(d.name) + "</a> <span class=\"g-mono\">" + esc(cname(d)) + ", " + esc(year(d)) + "</span></li>"; };
        var rej = r.used.filter(function (d) { return r.ok.indexOf(d) < 0; });
        h += '<tr class="cd-sub"><td colspan="4"><div class="g-grid2"><div><p class="cd-flab">' + esc(t("Accepted in", "Diterima dalam")) + "</p><ul>" + (r.ok.map(li).join("") || "<li>—</li>") + '</ul></div><div><p class="cd-flab">' + esc(t("Rejected in", "Ditolak dalam")) + "</p><ul>" + (rej.map(li).join("") || "<li>—</li>") + "</ul></div></div></td></tr>";
      }
    });
    return h + "</tbody></table></div>";
  }

  /* ---------- view 3: along the journey ---------- */
  function vJourney() {
    var v = visible();
    var at = function (s) { return v.filter(function (d) { return d.stages.indexOf(s) >= 0; }); };
    var h = '<h2 class="cd-vh">' + esc(t("From recruitment to return", "Dari perekrutan sampai pulang")) + "</h2>" +
      '<p class="g-note" style="margin-top:0">' + esc(t("Decisions placed on the stage of migration where the problem began, with the kind of court that decided them. Empty stages show where courts have not yet been asked.", "Putusan ditempatkan pada tahap migrasi tempat masalah bermula, dengan jenis pengadilan yang memutusnya. Tahap kosong menunjukkan di mana pengadilan belum pernah diminta memutus.")) + "</p>" +
      '<ol class="cd-stages">' + STAGE.map(function (s) {
        var L = at(s[0]);
        var c = function (f) { return L.filter(f).length; };
        return '<li><button type="button" class="cd-stage" data-stage="' + s[0] + '" aria-pressed="' + (S.stage === s[0]) + '"><span class="g-mono">' + s[0] + "</span><b>" + esc(t(s[1], s[2])) + "</b><span class=\"cd-sd\">" + esc(t(s[3], s[4])) + '</span><span class="cd-sn">' +
          esc(t("Courts at home", "Pengadilan di negara asal")) + " " + c(function (d) { return d.forum === "origin"; }) + "<br>" +
          esc(t("Courts abroad", "Pengadilan di negara tujuan")) + " " + c(function (d) { return d.forum === "destination"; }) + "<br>" +
          esc(t("Regional and international", "Kawasan dan internasional")) + " " + c(function (d) { return d.tier !== "national"; }) + "</span></button></li>";
      }).join("") + "</ol>";
    var st = STAGE[S.stage - 1], L = at(S.stage);
    h += '<h3 class="cd-vh3">' + esc(t(st[1], st[2])) + "</h3>";
    h += L.length ? cards(L) :
      empty("No decision in this collection yet at this stage. That gap is worth knowing.", "Belum ada putusan dalam koleksi ini pada tahap ini. Kekosongan itu penting diketahui.");
    return h;
  }

  /* ---------- view 4: compare ---------- */
  var DIMS = {
    region: {en: "Region", id: "Kawasan", key: function (d) { return isEchr(d) ? "echr" : isRef(d) ? "ref" : d.region; },
      groups: [["asia", "Asia", "Asia"], ["africa", "Africa", "Afrika"], ["latam", "Latin America", "Amerika Latin"], ["mideast", "Middle East", "Timur Tengah"], ["gulf", "Gulf States", "Negara Teluk"], ["pacific", "Pacific", "Pasifik"], ["intl", "International bodies", "Badan internasional"], ["echr", "European Court of Human Rights (comparator)", "Mahkamah HAM Eropa (pembanding)"], ["ref", "Canada, US and European national courts (comparison)", "Pengadilan nasional Kanada, AS dan Eropa (pembanding)"]]},
    tier: {en: "Level of court", id: "Tingkat pengadilan", key: function (d) { return d.tier; },
      groups: [["national", "National", "Nasional"], ["regional", "Regional", "Kawasan"], ["international", "International", "Internasional"]]},
    branch: {en: "Type of case", id: "Jenis perkara", key: function (d) { return d.branch; },
      groups: [["criminal", "Criminal", "Pidana"], ["private", "Private (labor, contract, tort)", "Perdata"], ["administrative", "Administrative", "Administrasi"], ["constitutional", "Constitutional and human rights", "Konstitusi dan HAM"]]},
    forum: {en: "Home or abroad (national courts)", id: "Negara asal atau tujuan (pengadilan nasional)", key: function (d) { return d.tier === "national" ? d.forum : null; },
      groups: [["destination", "Courts of destination countries", "Pengadilan negara tujuan"], ["origin", "Courts of origin countries", "Pengadilan negara asal"]]},
    period: {en: "Period", id: "Periode", key: function (d) { var y = +year(d); return y < 2000 ? "p0" : y < 2010 ? "p1" : y < 2020 ? "p2" : "p3"; },
      groups: [["p0", "Before 2000", "Sebelum 2000"], ["p1", "2000–2009", "2000–2009"], ["p2", "2010–2019", "2010–2019"], ["p3", "2020 onward", "2020 dan sesudahnya"]]},
    country: {en: "Country", id: "Negara", key: function (d) { return d.cc; }, groups: null}
  };
  function dimGroups(k) {
    if (k !== "country") return DIMS[k].groups;
    var n = {}; all.forEach(function (d) { if (!isC(d)) n[d.cc] = (n[d.cc] || 0) + 1; });
    return Object.keys(n).filter(function (c) { return n[c] >= 3; }).sort(function (a, b) { return n[b] - n[a]; })
      .map(function (c) { var x = COUNTRY[c] || [c, c]; return [c, x[0], x[1]]; });
  }
  var CDEF = {region: ["asia", "africa", "latam", "echr"], tier: ["national", "regional", "international"], branch: ["private", "administrative", "constitutional"], forum: ["destination", "origin"], period: ["p1", "p2", "p3"], country: ["HK", "ZA", "PH", "IN"]};
  S.cby = "region"; S.cg = CDEF.region.slice(); S.cfocus = "all"; S.cmode = "groups"; S.cpick = [];

  /* statistics (all computed in the browser; seeded so results are reproducible) */
  function lf(n) { var s = 0; for (var i = 2; i <= n; i++) s += Math.log(i); return s; }
  function fisher(a, b, c, d) {
    var r1 = a + b, r2 = c + d, c1 = a + c, n = r1 + r2;
    var p = function (x) { return Math.exp(lf(r1) + lf(r2) + lf(c1) + lf(n - c1) - lf(n) - lf(x) - lf(r1 - x) - lf(c1 - x) - lf(r2 - c1 + x)); };
    var p0 = p(a), s = 0, lo = Math.max(0, c1 - r2), hi = Math.min(r1, c1);
    for (var x = lo; x <= hi; x++) { var q = p(x); if (q <= p0 * (1 + 1e-7)) s += q; }
    return Math.min(1, s);
  }
  function gammq(a, x) {
    if (x <= 0) return 1;
    var gln = (function (z) { var c = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5], y = z, tmp = z + 5.5; tmp -= (z + 0.5) * Math.log(tmp); var ser = 1.000000000190015; for (var j = 0; j < 6; j++) ser += c[j] / ++y; return -tmp + Math.log(2.5066282746310005 * ser / z); })(a);
    if (x < a + 1) { var ap = a, sum = 1 / a, del = sum; for (var n = 0; n < 500; n++) { ap++; del *= x / ap; sum += del; if (Math.abs(del) < Math.abs(sum) * 1e-12) break; } return 1 - sum * Math.exp(-x + a * Math.log(x) - gln); }
    var b = x + 1 - a, cc = 1e300, dd = 1 / b, h = dd;
    for (var i = 1; i < 500; i++) { var an = -i * (i - a); b += 2; dd = an * dd + b; if (Math.abs(dd) < 1e-300) dd = 1e-300; cc = b + an / cc; if (Math.abs(cc) < 1e-300) cc = 1e-300; dd = 1 / dd; var de = dd * cc; h *= de; if (Math.abs(de - 1) < 1e-12) break; }
    return Math.exp(-x + a * Math.log(x) - gln) * h;
  }
  function chi2(tab) {
    var R = tab.length, C = tab[0].length, rs = tab.map(function (r) { return r.reduce(function (s, v) { return s + v; }, 0); }), cs = [], n = 0, x = 0, small = 0;
    for (var j = 0; j < C; j++) { cs[j] = 0; for (var i = 0; i < R; i++) cs[j] += tab[i][j]; n += cs[j]; }
    for (i = 0; i < R; i++) for (j = 0; j < C; j++) { var e = rs[i] * cs[j] / n; if (e > 0) x += (tab[i][j] - e) * (tab[i][j] - e) / e; if (e < 5) small++; }
    return {x: x, df: (R - 1) * (C - 1), n: n, small: small, cells: R * C};
  }
  function permP(groupsOf, labels, obs) {
    var seed = 20261101, rnd = function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; var z = Math.imul(seed ^ seed >>> 15, 1 | seed); z = z + Math.imul(z ^ z >>> 7, 61 | z) ^ z; return ((z ^ z >>> 14) >>> 0) / 4294967296; };
    var L = labels.slice(), G = groupsOf.length ? Math.max.apply(null, groupsOf) + 1 : 0, K = 2, hits = 0, N = 5000;
    for (var r = 0; r < N; r++) {
      for (var i = L.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)), tmp = L[i]; L[i] = L[j]; L[j] = tmp; }
      var tab = []; for (var g = 0; g < G; g++) tab.push([0, 0]);
      for (i = 0; i < L.length; i++) tab[groupsOf[i]][L[i]]++;
      if (chi2(tab).x >= obs - 1e-9) hits++;
    }
    return (hits + 1) / (N + 1);
  }
  function wilson(k, n) { if (!n) return null; var z = 1.96, p = k / n, d = 1 + z * z / n, c = (p + z * z / (2 * n)) / d, h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return [Math.max(0, c - h), Math.min(1, c + h)]; }
  function pct(k, n) { return n ? Math.round(100 * k / n) + "%" : "—"; }
  function fp(p) { return p < 0.001 ? "< 0.001" : p.toFixed(3); }

  function cmpGroups() {
    var dim = DIMS[S.cby], lab = {}; dimGroups(S.cby).forEach(function (g) { lab[g[0]] = t(g[1], g[2]); });
    var base = all.filter(function (d) { return !isC(d) && (S.cfocus === "all" || d.situations.indexOf(S.cfocus) >= 0); });
    return S.cg.filter(function (k) { return lab[k]; }).map(function (k) {
      var L = base.filter(function (d) { return dim.key(d) === k; });
      var won = L.filter(function (d) { return d.outcome === "won"; }).length, lost = L.filter(function (d) { return d.outcome === "lost"; }).length;
      var fy = L.filter(function (d) { return d.follow === "carried" || d.follow === "partly"; }).length, fn = L.filter(function (d) { return d.follow === "not"; }).length, fu = L.filter(function (d) { return d.follow === "unknown"; }).length;
      return {k: k, label: lab[k], L: L, won: won, lost: lost, adv: L.filter(function (d) { return d.outcome === "advisory"; }).length, fy: fy, fn: fn, fu: fu};
    });
  }
  function testBlock(G, yes, no, en, id, what) {
    var use = G.filter(function (g) { return g[yes] + g[no] > 0; });
    if (use.length < 2) return '<p class="g-note">' + esc(t("Not enough decisions in at least two groups to test " + en + ".", "Putusan di sekurang-kurangnya dua kelompok tidak cukup untuk menguji " + id + ".")) + "</p>";
    var tab = use.map(function (g) { return [g[yes], g[no]]; }), c = chi2(tab), h, p;
    if (use.length === 2) {
      p = fisher(tab[0][0], tab[0][1], tab[1][0], tab[1][1]);
      h = t("Fisher’s exact test (two-sided), comparing " + use[0].label + " with " + use[1].label + ": p = " + fp(p) + ".", "Uji eksak Fisher (dua sisi), membandingkan " + use[0].label + " dengan " + use[1].label + ": p = " + fp(p) + ".");
    } else {
      var gi = [], lb = []; use.forEach(function (g, i) { for (var a = 0; a < g[yes]; a++) { gi.push(i); lb.push(0); } for (a = 0; a < g[no]; a++) { gi.push(i); lb.push(1); } });
      p = permP(gi, lb, c.x); var pa = gammq(c.df / 2, c.x / 2), V = Math.sqrt(c.x / c.n);
      h = t("Chi-square test of independence: χ² = " + c.x.toFixed(2) + ", df = " + c.df + ", n = " + c.n + ", asymptotic p = " + fp(pa) + "; permutation p (5,000 shuffles) = " + fp(p) + "; Cramér’s V = " + V.toFixed(2) + ".",
        "Uji chi-kuadrat independensi: χ² = " + c.x.toFixed(2) + ", df = " + c.df + ", n = " + c.n + ", p asimtotik = " + fp(pa) + "; p permutasi (5.000 acakan) = " + fp(p) + "; V Cramér = " + V.toFixed(2) + ".") +
        (c.small ? " " + t(c.small + " of " + c.cells + " expected counts are below 5, so rely on the permutation p.", c.small + " dari " + c.cells + " frekuensi harapan di bawah 5, jadi gunakan p permutasi.") : "");
    }
    var plain = p < 0.05 ?
      t("In plain language: the groups differ more than chance alone would usually produce in a collection of this size. That is a pattern in this collection, not proof about courts in general.", "Dalam bahasa sederhana: perbedaan antarkelompok lebih besar daripada yang biasanya muncul karena kebetulan pada koleksi sebesar ini. Itu pola dalam koleksi ini, bukan bukti tentang pengadilan pada umumnya.") :
      t("In plain language: the differences between the groups could easily be due to chance, given how few decisions each group has.", "Dalam bahasa sederhana: perbedaan antarkelompok bisa saja karena kebetulan, mengingat sedikitnya putusan di tiap kelompok.");
    return '<div class="cd-test"><p class="cd-flab">' + esc(t(what[0], what[1])) + "</p><p>" + esc(h) + '</p><p class="g-note">' + esc(plain) + "</p></div>";
  }
  function cell(k, n) { var w = wilson(k, n); return n ? '<span class="g-mono">' + pct(k, n) + "</span> <span class=\"cd-n\">(" + k + "/" + n + (w ? "; 95% CI " + Math.round(100 * w[0]) + "–" + Math.round(100 * w[1]) + "%" : "") + ")</span>" : "—"; }
  function top(L, f, map, k) {
    var c = {}; L.forEach(function (d) { f(d).forEach(function (x) { c[x] = (c[x] || 0) + 1; }); });
    return Object.keys(c).sort(function (a, b) { return c[b] - c[a]; }).slice(0, k).map(function (x) { return esc(map(x)) + " (" + c[x] + ")"; }).join("<br>") || "—";
  }
  var sitName = function (k) { var s = SIT.filter(function (x) { return x[0] === k; })[0]; return s ? t(s[1], s[2]) : k; };
  var stName = function (k) { var s = STAGE[+k - 1]; return s ? t(s[1], s[2]) : k; };
  function cmpCSV(G) {
    var q = function (v) { v = String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
    var rows = [["group", "decisions", "worker_won", "worker_lost", "advisory", "followup_carried_or_partly", "followup_not", "followup_unknown", "decision_ids"]];
    G.forEach(function (g) { rows.push([g.label, g.L.length, g.won, g.lost, g.adv, g.fy, g.fn, g.fu, g.L.map(function (d) { return d.id; }).join(" ")]); });
    return "data:text/csv;charset=utf-8," + encodeURIComponent("﻿" + rows.map(function (r) { return r.map(q).join(","); }).join("\n"));
  }
  function vCompare() {
    var h = '<h2 class="cd-vh">' + esc(t("Compare groups of decisions", "Bandingkan kelompok putusan")) + "</h2>" +
      '<p class="g-note" style="margin-top:0">' + esc(t("Choose what to compare, then pick two to four groups. The table shows how the decisions in each group came out, what happened afterwards, and which arguments courts accepted. Tests are computed in your browser.", "Pilih apa yang dibandingkan, lalu pilih dua sampai empat kelompok. Tabel menunjukkan hasil putusan di tiap kelompok, apa yang terjadi sesudahnya, dan argumen mana yang diterima pengadilan. Uji dihitung di peramban anda.")) + "</p>" +
      '<div class="g-btns" role="group" aria-label="' + esc(t("Comparison mode", "Mode perbandingan")) + '"><button type="button" class="g-btn" data-cmode="groups" aria-pressed="' + (S.cmode === "groups") + '">' + esc(t("Groups of decisions", "Kelompok putusan")) + '</button><button type="button" class="g-btn" data-cmode="cases" aria-pressed="' + (S.cmode === "cases") + '">' + esc(t("Decisions side by side", "Putusan berdampingan")) + "</button></div>";
    if (S.cmode === "cases") return h + vCases();
    h += '<div class="cd-frow"><span class="cd-flab">' + esc(t("Compare by", "Bandingkan menurut")) + '</span><div class="g-btns" role="group">' +
      Object.keys(DIMS).map(function (k) { return '<button type="button" class="g-btn" data-cby="' + k + '" aria-pressed="' + (S.cby === k) + '">' + esc(t(DIMS[k].en, DIMS[k].id)) + "</button>"; }).join("") + "</div></div>";
    var dimN = function (k) { return all.filter(function (d) { return !isC(d) && DIMS[S.cby].key(d) === k; }).length; };
    h += '<div class="cd-frow"><span class="cd-flab">' + esc(t("Groups (2 to 4)", "Kelompok (2 sampai 4)")) + '</span><div class="cd-chips" role="group">' +
      dimGroups(S.cby).map(function (g) { return '<button type="button" class="cd-chip" data-cg="' + esc(g[0]) + '" aria-pressed="' + (S.cg.indexOf(g[0]) >= 0) + '">' + esc(t(g[1], g[2])) + " (" + dimN(g[0]) + ")</button>"; }).join("") + "</div></div>";
    h += '<div class="cd-frow"><label class="cd-flab" for="cd-cfocus">' + esc(t("Limit to one situation", "Batasi pada satu situasi")) + '</label><select id="cd-cfocus" class="cd-sel"><option value="all">' + esc(t("All situations", "Semua situasi")) + "</option>" +
      SIT.map(function (s) { return '<option value="' + s[0] + '"' + (S.cfocus === s[0] ? " selected" : "") + ">" + esc(t(s[1], s[2])) + "</option>"; }).join("") + "</select></div>";
    var G = cmpGroups();
    if (G.length < 2) return h + empty("Pick at least two groups to compare.", "Pilih sekurang-kurangnya dua kelompok untuk dibandingkan.");
    var th = G.map(function (g) { return '<th scope="col">' + esc(g.label) + "</th>"; }).join("");
    var row = function (lab, f) { return '<tr><th scope="row">' + lab + "</th>" + G.map(function (g) { return "<td>" + f(g) + "</td>"; }).join("") + "</tr>"; };
    var xl = function (L) { return '<ul class="cd-xl">' + L.map(function (d) { return '<li><a href="#d/' + esc(d.id) + '" data-open="' + esc(d.id) + '">' + esc(d.name) + '</a> <span class="g-mono">' + esc(cname(d)) + ", " + esc(year(d)) + "</span></li>"; }).join("") + "</ul>"; };
    var ex = function (inner, L) { return L.length ? '<details class="cd-x"><summary>' + inner + '</summary>' + xl(L) + "</details>" : inner; };
    var by = function (g, f) { return g.L.filter(f); };
    var fo = function (k) { return function (d) { return d.outcome === k; }; };
    h += '<p class="g-note">' + esc(t("Tap any number to see the decisions behind it.", "Ketuk angka mana pun untuk melihat putusan di baliknya.")) + "</p>";
    h += '<div class="g-scroll"><table class="g-t cd-cmp"><thead><tr><th scope="col"></th>' + th + "</tr></thead><tbody>" +
      row(esc(t("Decisions", "Putusan")), function (g) { return ex('<b class="g-mono">' + g.L.length + "</b>", g.L); }) +
      row(esc(t("Worker side won (of decisions with a winner)", "Pihak pekerja menang (dari putusan yang ada pemenangnya)")), function (g) { return ex(cell(g.won, g.won + g.lost), by(g, fo("won")).concat(by(g, fo("lost")))); }) +
      row(esc(t("Advisory opinions", "Pendapat nasihat")), function (g) { return ex('<span class="g-mono">' + g.adv + "</span>", by(g, fo("advisory"))); }) +
      row(esc(t("Carried out fully or partly (of decisions with something to carry out and a known result)", "Dilaksanakan seluruhnya atau sebagian (dari putusan yang perlu dilaksanakan dan hasilnya diketahui)")), function (g) { return ex(cell(g.fy, g.fy + g.fn), by(g, function (d) { return d.follow === "carried" || d.follow === "partly" || d.follow === "not"; })); }) +
      row(esc(t("Follow-up not yet known", "Tindak lanjut belum diketahui")), function (g) { return ex('<span class="g-mono">' + g.fu + "</span>", by(g, function (d) { return d.follow === "unknown"; })); }) +
      row(esc(t("Most frequent situations", "Situasi paling sering")), function (g) { return top(g.L, function (d) { return d.situations; }, sitName, 3); }) +
      row(esc(t("Most frequent stages", "Tahap paling sering")), function (g) { return top(g.L, function (d) { return d.stages.map(String); }, stName, 2); }) +
      row(esc(t("Years covered", "Tahun yang dicakup")), function (g) { var y = g.L.map(year).sort(); return y.length ? '<span class="g-mono">' + y[0] + "–" + y[y.length - 1] + "</span>" : "—"; }) +
      "</tbody></table></div>";
    h += '<h3 class="cd-vh3">' + esc(t("Is the difference more than chance?", "Apakah perbedaannya lebih dari kebetulan?")) + "</h3>" +
      testBlock(G, "won", "lost", "outcomes", "hasil putusan", ["Outcome: worker side won or lost", "Hasil: pihak pekerja menang atau kalah"]) +
      testBlock(G, "fy", "fn", "follow-up", "tindak lanjut", ["Follow-up: carried out (fully or partly) or not", "Tindak lanjut: dilaksanakan (seluruhnya atau sebagian) atau tidak"]) +
      '<p class="g-note">' + esc(t("Read with care: this is a curated collection of reported decisions, not a random sample of all cases. Courts and cases that are published, translated or reported in the news are over-represented, and many entries are still being checked. A small p-value describes a pattern in this collection; it does not show that courts in one region decide differently from courts elsewhere.", "Baca dengan hati-hati: ini koleksi putusan terpilih yang dilaporkan, bukan sampel acak dari semua perkara. Pengadilan dan perkara yang diterbitkan, diterjemahkan, atau diberitakan lebih banyak terwakili, dan banyak entri masih diperiksa. Nilai p yang kecil menggambarkan pola dalam koleksi ini; itu tidak menunjukkan bahwa pengadilan di satu kawasan memutus secara berbeda dari pengadilan di tempat lain.")) + "</p>";
    var args = (CD.args || []).map(function (a) {
      var per = G.map(function (g) { var u = g.L.filter(function (d) { return d.args.some(function (x) { return x.a === a.k; }); }); return {u: u.length, L: u, ok: u.filter(function (d) { return d.args.some(function (x) { return x.a === a.k && x.ok; }); }).length}; });
      return {a: a, per: per, tot: per.reduce(function (s, p) { return s + p.u; }, 0), groups: per.filter(function (p) { return p.u; }).length};
    }).filter(function (r) { return r.groups >= 2; }).sort(function (x, y) { return y.tot - x.tot; });
    h += '<h3 class="cd-vh3">' + esc(t("Arguments raised in more than one group", "Argumen yang diajukan di lebih dari satu kelompok")) + "</h3>";
    h += args.length ? '<div class="g-scroll"><table class="g-t cd-cmp"><thead><tr><th scope="col">' + esc(t("Argument (accepted / tried)", "Argumen (diterima / diajukan)")) + "</th>" + th + "</tr></thead><tbody>" +
      args.map(function (r) { return '<tr><th scope="row">' + esc(t(r.a.en, r.a.id)) + "</th>" + r.per.map(function (p) { return '<td class="g-mono">' + (p.u ? ex(p.ok + " / " + p.u, p.L) : "—") + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div>" :
      '<p class="g-note">' + esc(t("No argument appears in more than one of the chosen groups.", "Tidak ada argumen yang muncul di lebih dari satu kelompok yang dipilih.")) + "</p>";
    h += '<details class="cd-coded"><summary>' + esc(t("Decisions in each group", "Putusan di tiap kelompok")) + '</summary><div class="g-grid2">' +
      G.map(function (g) { return '<div><p class="cd-flab">' + esc(g.label) + "</p><ul>" + g.L.map(function (d) { return '<li><a href="#d/' + esc(d.id) + '" data-open="' + esc(d.id) + '">' + esc(d.name) + '</a> <span class="g-mono">' + esc(cname(d)) + ", " + esc(year(d)) + "</span></li>"; }).join("") + "</ul></div>"; }).join("") + "</div></details>";
    h += '<div class="g-acts"><a class="g-btn dl" href="' + cmpCSV(G) + '" download="court-decisions-comparison.csv">' + esc(t("Download this comparison (CSV)", "Unduh perbandingan ini (CSV)")) + "</a></div>";
    return h;
  }
  function vCases() {
    var opts = function (sel) { return '<option value="">' + esc(t("Choose a decision", "Pilih putusan")) + "</option>" + all.filter(function (d) { return !isC(d); }).sort(function (a, b) { return cname(a).localeCompare(cname(b)) || (a.date < b.date ? -1 : 1); }).map(function (d) { return '<option value="' + esc(d.id) + '"' + (sel === d.id ? " selected" : "") + ">" + esc(cname(d) + ", " + year(d) + ": " + d.name) + "</option>"; }).join(""); };
    var h = '<p class="g-note">' + esc(t("Choose up to three decisions to read side by side.", "Pilih sampai tiga putusan untuk dibaca berdampingan.")) + '</p><div class="cd-pick">';
    for (var i = 0; i < 3; i++) h += '<select class="cd-sel" data-cpick="' + i + '" aria-label="' + esc(t("Decision " + (i + 1), "Putusan " + (i + 1))) + '">' + opts(S.cpick[i]) + "</select>";
    h += "</div>";
    var P = S.cpick.filter(function (x) { return x && byId[x]; }).map(function (x) { return byId[x]; });
    if (!P.length) return h;
    var row = function (lab, f) { return '<tr><th scope="row">' + esc(lab) + "</th>" + P.map(function (d) { return "<td>" + f(d) + "</td>"; }).join("") + "</tr>"; };
    return h + '<div class="g-scroll"><table class="g-t cd-cmp cd-side"><thead><tr><th scope="col"></th>' + P.map(function (d) { return '<th scope="col"><a href="#d/' + esc(d.id) + '" data-open="' + esc(d.id) + '">' + esc(d.name) + "</a></th>"; }).join("") + "</tr></thead><tbody>" +
      row(t("Court", "Pengadilan"), function (d) { return esc(d.court); }) +
      row(t("Level and place", "Tingkat dan tempat"), function (d) { return meta(d); }) +
      row(t("Date and citation", "Tanggal dan sitasi"), function (d) { return esc(fdate(d.date)) + "<br>" + esc(d.cite); }) +
      row(t("Sector", "Sektor"), function (d) { return esc(d.sector); }) +
      row(t("Question", "Pertanyaan"), function (d) { return esc(t(d.q, d.q_id)); }) +
      row(t("What the court decided", "Apa yang diputuskan"), function (d) { return esc(d.held); }) +
      row(t("Outcome", "Hasil"), function (d) { return pill(t(OUT[d.outcome][0], OUT[d.outcome][1]), "o-" + d.outcome); }) +
      row(t("What happened next", "Apa yang terjadi sesudahnya"), function (d) { return pill(t(FOL[d.follow][0], FOL[d.follow][1]), "f-" + d.follow); }) +
      row(t("Arguments", "Argumen"), function (d) { return d.args.map(function (x) { var a = argOf[x.a]; return esc(t(a.en, a.id)) + " — <b>" + esc(x.ok ? t("accepted", "diterima") : t("rejected", "ditolak")) + "</b>"; }).join("<br>") || "—"; }) +
      row(t("Situations", "Situasi"), function (d) { return d.situations.map(sitName).map(esc).join("<br>"); }) +
      row(t("Stages", "Tahap"), function (d) { return d.stages.map(stName).map(esc).join("<br>"); }) +
      "</tbody></table></div>";
  }

  /* ---------- follow-up summary ---------- */
  function summary() {
    var v = visible().filter(function (d) { return !isC(d); }), keys = ["carried", "partly", "not", "unknown", "none"];
    var n = function (k) { return v.filter(function (d) { return d.follow === k; }).length; };
    $("cd-sum").innerHTML = '<div class="g-stack" role="img" aria-label="' + esc(t("Decisions by what happened afterwards", "Putusan menurut apa yang terjadi sesudahnya")) + '">' +
      keys.map(function (k) { return n(k) ? '<span style="flex:' + n(k) + ";background:" + FOLC[k] + '" title="' + esc(t(FOL[k][0], FOL[k][1])) + '"></span>' : ""; }).join("") + "</div>" +
      '<div class="g-legend">' + keys.map(function (k) { return '<span><span class="cd-sw" style="background:' + FOLC[k] + '"></span>' + esc(t(FOL[k][0], FOL[k][1])) + " " + n(k) + "</span>"; }).join("") + "</div>";
  }

  /* ---------- one decision ---------- */
  function detail() {
    var box = $("cd-detail"), d = S.open && byId[S.open];
    if (!d) { box.hidden = true; box.innerHTML = ""; return; }
    if (isC(d)) {
      box.hidden = false;
      box.innerHTML = '<div class="cd-dhead"><p class="cd-meta">' + meta(d) + '</p><span class="g-btns"><button type="button" class="g-btn" data-close>' + esc(t("Back to the list", "Kembali ke daftar")) + "</button></span></div>" +
        '<h2 id="cd-dtitle">' + esc(d.name) + "</h2>" + '<p class="cd-court">' + esc(d.court) + " · " + esc(fdate(d.date)) + " · " + esc(d.cite) + "</p>" +
        '<p class="cd-pills">' + aipill(t("Unchecked candidate: not yet verified", "Kandidat belum diperiksa: belum diverifikasi"), "s-C") + "</p>" +
        '<div class="cd-warn" style="margin-top:12px"><p>' + esc(t("This is a lead for researchers, not a checked entry. The name, court, year and citation may be wrong, and no summary of the decision has been written yet. Do not rely on it.", "Ini petunjuk untuk peneliti, bukan entri yang sudah diperiksa. Nama, pengadilan, tahun, dan sitasi bisa saja keliru, dan ringkasan putusan belum ditulis. Jangan dijadikan pegangan.")) + "</p></div>" +
        '<h3 class="g-h4">' + esc(t("Topic", "Topik")) + "</h3><p>" + esc(t(d.plain, d.plain_id)) + "</p>" +
        '<h3 class="g-h4">' + esc(t("Where to check", "Tempat memeriksa")) + "</h3><ul>" + d.src.map(function (s) { return '<li><a href="' + esc(s.u) + '" rel="noopener">' + esc(s.t) + "</a></li>"; }).join("") + "</ul>" +
        '<p class="g-note">' + esc(t("Know this case? Send the judgment or a correction to secretariat@theimr.org.", "Mengenal perkara ini? Kirim putusan atau koreksi ke secretariat@theimr.org.")) + "</p>";
      return;
    }
    var argl = d.args.map(function (x) { var a = argOf[x.a]; return "<li>" + esc(t(a.en, a.id)) + " — <b>" + esc(x.ok ? t("accepted", "diterima") : t("rejected", "ditolak")) + "</b></li>"; }).join("");
    var tl = d.after.map(function (x) { return '<li><span class="d">' + esc(x.d === "later" ? t("Later", "Kemudian") : fdate(x.d)) + "</span><br>" + esc(t(x.en, x.id)) + "</li>"; }).join("");
    var rows = [["tier", t(TIER[d.tier][0], TIER[d.tier][1])], ["type_of_case", t(BR[d.branch][0], BR[d.branch][1])], ["forum", d.forum], ["level", d.level], ["country", d.cc], ["date", d.date], ["citation", d.cite], ["sector", d.sector], ["issues", d.issues.join("; ")], ["stages", d.stages.join("; ")], ["outcome", d.outcome], ["follow_up", d.follow], ["status", d.status]];
    box.hidden = false;
    box.innerHTML = '<div class="cd-dhead"><p class="cd-meta">' + meta(d) + '</p><span class="g-btns"><button type="button" class="g-btn" data-addcmp="' + esc(d.id) + '">' + esc(t("Compare with other decisions", "Bandingkan dengan putusan lain")) + '</button><button type="button" class="g-btn" data-close>' + esc(t("Back to the list", "Kembali ke daftar")) + "</button></span></div>" +
      '<h2 id="cd-dtitle">' + esc(d.name) + "</h2>" +
      '<p class="cd-court">' + esc(d.court) + " · " + esc(fdate(d.date)) + " · " + esc(d.cite) + "</p>" +
      '<p class="cd-pills">' + pill(t(OUT[d.outcome][0], OUT[d.outcome][1]), "o-" + d.outcome) + pill(t("After: ", "Sesudahnya: ") + t(FOL[d.follow][0], FOL[d.follow][1]), "f-" + d.follow) + (d.status === "P" ? pill(t("Checked against the judgment", "Diperiksa dengan teks putusan"), "s-P") : aipill(t("Unverified: summary pre-written by AI from secondary sources, being checked against the judgment", "Belum diverifikasi: ringkasan ditulis lebih dahulu oleh AI dari sumber sekunder, sedang diperiksa dengan teks putusan"), "s-" + d.status)) + "</p>" +
      '<div class="cd-plain"><h3>' + esc(t("In plain language", "Dalam bahasa sederhana")) + "</h3><p>" + esc(t(d.plain, d.plain_id)) + "</p></div>" +
      '<div class="g-grid2"><div><h3 class="g-h4">' + esc(t("Question", "Pertanyaan")) + "</h3><p>" + esc(t(d.q, d.q_id)) + '</p><h3 class="g-h4">' + esc(t("What the court decided", "Apa yang diputuskan")) + "</h3><p>" + esc(d.held) + "</p>" +
      (ID() ? '<p class="g-note">Ringkasan putusan ini dalam bahasa Inggris.</p>' : "") +
      '<h3 class="g-h4">' + esc(t("Arguments made for the worker side", "Argumen untuk pihak pekerja")) + "</h3><ul>" + argl + "</ul>" +
      ((d.tools || []).length ? '<h3 class="g-h4">' + esc(t("Reasoning tools", "Alat penalaran")) + '</h3><ul>' + d.tools.map(function (k) { var x = toolOf[k]; return x ? "<li><b>" + esc(t(x.en, x.id)) + "</b>: " + esc(t(x.def, x.def_id)) + ' <span class="g-mono">(' + esc(x.ch) + ")</span></li>" : ""; }).join("") + '</ul><p class="g-note" style="margin-top:0">' + esc(t("Coded by rule from the arguments and the wording of the holding, with AI assistance; to be confirmed against the judgment.", "Dikodekan menurut aturan dari argumen dan rumusan putusan, dengan bantuan AI; perlu dikonfirmasi dengan teks putusan.")) + "</p>" : "") +
      (function () { var C = comparators(d); return C.length ? '<h3 class="g-h4">' + esc(t("Comparators from liberal jurisdictions", "Pembanding dari yurisdiksi liberal")) + '</h3><p class="g-note" style="margin-top:0">' + esc(t("The closest decisions on the same question from the European Court of Human Rights and from national courts of liberal democracies such as Canada, the UK, the US, Australia and New Zealand, for comparison.", "Putusan terdekat untuk pertanyaan yang sama dari Mahkamah HAM Eropa dan dari pengadilan nasional negara demokrasi liberal seperti Kanada, Inggris, AS, Australia, dan Selandia Baru, sebagai pembanding.")) + "</p><ul>" + C.map(function (c) { var e = c[1]; return '<li><span class="cd-flab">' + esc(c[0]) + '</span><br><a href="#d/' + esc(e.id) + '" data-open="' + esc(e.id) + '">' + esc(e.name) + "</a> (" + esc(year(e)) + "): " + pill(t(OUT[e.outcome][0], OUT[e.outcome][1]), "o-" + e.outcome) + ' <button type="button" class="cd-link" data-addcmp2="' + esc(d.id) + "|" + esc(e.id) + '">' + esc(t("Compare side by side", "Bandingkan berdampingan")) + "</button></li>"; }).join("") + "</ul>" : ""; })() + "</div>" +
      '<div><h3 class="g-h4">' + esc(t("What happened next", "Apa yang terjadi sesudahnya")) + '</h3><ul class="g-tl">' + tl + "</ul>" +
      '<h3 class="g-h4">' + esc(t("Sources", "Sumber")) + "</h3><ul>" + d.src.map(function (s) { return '<li><a href="' + esc(s.u) + '" rel="noopener">' + esc(s.t) + "</a></li>"; }).join("") + "</ul>" + lawsBlock(d) + "</div></div>" +
      '<details class="cd-coded"><summary>' + esc(t("Coded variables", "Variabel kode")) + '</summary><div class="g-scroll"><table class="g-t"><tbody>' +
      rows.map(function (r) { return '<tr><th scope="row" class="g-mono">' + esc(r[0]) + "</th><td>" + esc(r[1]) + "</td></tr>"; }).join("") + "</tbody></table></div></details>" +
      '<p class="g-note">' + esc(t("Cite this entry: Institute for Migrant Rights, Migration Jurisprudence from the South: Court Decisions, version ", "Kutip entri ini: Institute for Migrant Rights, Pandangan Hukum Migrasi dari Dunia Berkembang: Putusan Pengadilan, versi ")) + esc(CD.version) + ", " + esc(t("entry", "entri")) + " " + esc(d.id) + ", https://theimr.org/court-decisions/#d/" + esc(d.id) + "</p>" +
      '<div class="g-acts"><a href="/legal-clinic/">' + esc(t("Something similar happened to you? Tell the Legal Clinic", "Mengalami hal serupa? Hubungi Klinik Hukum")) + "</a></div>";
  }

  function codebook() {
    $("cd-codebook").innerHTML = "<thead><tr><th>" + esc(t("Variable", "Variabel")) + "</th><th>" + esc(t("Definition", "Definisi")) + "</th><th>" + esc(t("Values", "Nilai")) + "</th></tr></thead><tbody>" +
      (CD.codebook || []).map(function (c) { return '<tr><td class="c g-mono">' + esc(c.v) + "</td><td>" + esc(c.def) + '</td><td class="g-mono">' + esc(c.vals) + "</td></tr>"; }).join("") + "</tbody>";
  }

  function render() {
    document.querySelectorAll("[data-view]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-view") === S.view)); });
    filters();
    var cmpv = S.view === "compare"; $("cd-filters").hidden = cmpv; $("cd-count").hidden = cmpv;
    $("cd-view").innerHTML = S.view === "argument" ? vArgument() : S.view === "journey" ? vJourney() : cmpv ? vCompare() : vSituation();
    var nc = visible().filter(isC).length; $("cd-count").textContent = t(visible().length + " of " + all.length + " decisions shown, including " + nc + " unchecked candidates", visible().length + " dari " + all.length + " putusan ditampilkan, termasuk " + nc + " kandidat belum diperiksa");
    summary(); detail(); codebook();
  }

  function fromHash() {
    var h = location.hash.replace(/^#/, "");
    if (h.indexOf("d/") === 0) { S.open = h.slice(2); return true; }
    S.open = null;
    if (h === "situation" || h === "argument" || h === "journey" || h === "compare") S.view = h;
    return false;
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-more],[data-view],[data-tier],[data-br],[data-forum],[data-sit],[data-stage],[data-arg],[data-open],[data-close],[data-cmode],[data-cby],[data-cg],[data-addcmp],[data-addcmp2]");
    if (!b || !b.closest("#court-decisions")) return;
    if (b.hasAttribute("data-open")) { e.preventDefault(); S.open = b.getAttribute("data-open"); history.pushState(null, "", "#d/" + S.open); render(); $("cd-detail").scrollIntoView({behavior: "smooth", block: "start"}); var ti = $("cd-dtitle"); if (ti) { ti.setAttribute("tabindex", "-1"); ti.focus({preventScroll: true}); } return; }
    if (b.hasAttribute("data-close")) { S.open = null; history.pushState(null, "", "#" + S.view); render(); $("cd-views").scrollIntoView({behavior: "smooth"}); return; }
    if (b.hasAttribute("data-view")) { S.view = b.getAttribute("data-view"); S.open = null; history.replaceState(null, "", "#" + S.view); }
    if (b.hasAttribute("data-more")) { S.limit += 25; render(); return; }
    if (!b.hasAttribute("data-open") && !b.hasAttribute("data-addcmp")) S.limit = 25;
    if (b.hasAttribute("data-br")) S.br = b.getAttribute("data-br");
    if (b.hasAttribute("data-tier")) { S.tier = b.getAttribute("data-tier"); if (S.tier !== "all" && S.tier !== "national") S.forum = "all"; }
    if (b.hasAttribute("data-forum")) S.forum = b.getAttribute("data-forum");
    if (b.hasAttribute("data-sit")) S.sit = b.getAttribute("data-sit");
    if (b.hasAttribute("data-stage")) S.stage = +b.getAttribute("data-stage");
    if (b.hasAttribute("data-cmode")) S.cmode = b.getAttribute("data-cmode");
    if (b.hasAttribute("data-cby")) { S.cby = b.getAttribute("data-cby"); S.cg = CDEF[S.cby].slice(); }
    if (b.hasAttribute("data-cg")) { var g = b.getAttribute("data-cg"), i = S.cg.indexOf(g); if (i >= 0) S.cg.splice(i, 1); else if (S.cg.length < 4) S.cg.push(g); }
    if (b.hasAttribute("data-addcmp2")) { S.cpick = b.getAttribute("data-addcmp2").split("|"); S.view = "compare"; S.cmode = "cases"; S.open = null; history.pushState(null, "", "#compare"); render(); $("cd-views").scrollIntoView({behavior: "smooth"}); return; }
    if (b.hasAttribute("data-addcmp")) { var id = b.getAttribute("data-addcmp"); if (S.cpick.indexOf(id) < 0) { S.cpick = S.cpick.filter(Boolean).concat([id]).slice(-3); } S.view = "compare"; S.cmode = "cases"; S.open = null; history.pushState(null, "", "#compare"); render(); $("cd-views").scrollIntoView({behavior: "smooth"}); return; }
    if (b.hasAttribute("data-arg")) S.argOpen = S.argOpen === b.getAttribute("data-arg") ? null : b.getAttribute("data-arg");
    render();
  });
  document.addEventListener("change", function (e) {
    var x = e.target; if (!x.closest || !x.closest("#court-decisions")) return;
    if (x.id === "cd-cfocus") { S.cfocus = x.value; render(); }
    if (x.hasAttribute("data-cpick")) { S.cpick[+x.getAttribute("data-cpick")] = x.value; render(); }
  });
  window.addEventListener("popstate", function () { fromHash(); render(); });
  var startOpen = fromHash();
  render();
  if (startOpen) setTimeout(function () { var x = $("cd-detail"); if (x && !x.hidden) x.scrollIntoView(); }, 50);
  new MutationObserver(function () { render(); }).observe(document.documentElement, {attributes: true, attributeFilter: ["lang"]});

  document.addEventListener("change", function (e) {
    if (e.target && e.target.id === "cd-tool") { S.tool = e.target.value; S.limit = 25; S.open = null; render(); }
  });
  /* reasoning lens (method section) */
  var rz = $("cd-reasoning");
  if (rz) {
    var nS = all.filter(function (d) { return d.status !== "C"; }).length;
    rz.innerHTML = '<h3 class="g-h4">' + esc(t("Reasoning tools", "Alat penalaran")) + '</h3><p style="max-width:820px">' + esc(t(
      "Besides the arguments, each full entry is tagged with the patterns of legal reasoning it shows, drawn from works on legal reasoning: Ward Farnsworth, The Legal Analyst (University of Chicago Press, 2007); Joel P. Trachtman, The Tools of Argument (2013); Pierre Schlag and David Skover, Tactics of Legal Reasoning (Carolina Academic Press, 1986); Frederick Schauer, Thinking Like a Lawyer (Harvard University Press, 2009); Janet Giltrow and others (eds), Legal Meanings (De Gruyter); Scott Brewer (ed.), Precedents, Statutes, and Analysis of Legal Concepts (1998); Suvi Sankari, European Court of Justice Legal Reasoning in Context (Europa Law Publishing, 2013); and Richard K. Neumann, Ellie Margolis and Kathryn M. Stanchi, Legal Reasoning and Legal Writing (Aspen Publishing) The tags are coded by rule from the argument codes and the wording of the question and holding, with AI assistance, and are still to be confirmed against each judgment. The method, rules applied to coded factors and to the text of each summary, is a simple form of the legal text analytics surveyed in Kevin D. Ashley, Artificial Intelligence and Legal Analytics (Cambridge University Press, 2017); like those tools, it can miss reasoning that is not stated in the summary. They describe how the reasoning can be read, not the court's own vocabulary, and one decision can carry several. Use the Reasoning tool filter above to list the decisions for each.",
      "Selain argumen, setiap entri lengkap ditandai dengan pola penalaran hukum yang ditunjukkannya, diambil dari karya tentang penalaran hukum: Ward Farnsworth, The Legal Analyst (University of Chicago Press, 2007); Joel P. Trachtman, The Tools of Argument (2013); Pierre Schlag dan David Skover, Tactics of Legal Reasoning (Carolina Academic Press, 1986); Frederick Schauer, Thinking Like a Lawyer (Harvard University Press, 2009); Janet Giltrow dan lainnya (ed.), Legal Meanings (De Gruyter); Scott Brewer (ed.), Precedents, Statutes, and Analysis of Legal Concepts (1998); Suvi Sankari, European Court of Justice Legal Reasoning in Context (Europa Law Publishing, 2013); serta Richard K. Neumann, Ellie Margolis dan Kathryn M. Stanchi, Legal Reasoning and Legal Writing (Aspen Publishing) Tanda ini dikodekan menurut aturan dari kode argumen dan rumusan pertanyaan serta putusan, dengan bantuan AI, dan masih perlu dikonfirmasi dengan teks setiap putusan. Metodenya, yaitu aturan yang diterapkan pada faktor yang dikodekan dan pada teks setiap ringkasan, adalah bentuk sederhana analitik teks hukum yang diulas dalam Kevin D. Ashley, Artificial Intelligence and Legal Analytics (Cambridge University Press, 2017); seperti alat-alat itu, metode ini bisa melewatkan penalaran yang tidak tertulis dalam ringkasan. Tanda ini menggambarkan cara penalaran bisa dibaca, bukan istilah pengadilan sendiri, dan satu putusan bisa memiliki beberapa tanda. Gunakan filter Alat penalaran di atas untuk melihat putusan untuk masing-masing.")) + "</p>" +
      '<div class="g-scroll"><table class="g-table"><thead><tr><th>' + esc(t("Tool", "Alat")) + "</th><th>" + esc(t("What it means here", "Artinya di sini")) + "</th><th>" + esc(t("Further reading", "Bacaan lanjut")) + "</th><th>" + esc(t("Decisions", "Putusan")) + " (" + nS + ")</th></tr></thead><tbody>" +
      (CD.tools || []).map(function (x) { var n = all.filter(function (d) { return (d.tools || []).indexOf(x.k) >= 0; }).length; return "<tr><td><b>" + esc(t(x.en, x.id)) + "</b></td><td>" + esc(t(x.def, x.def_id)) + '</td><td class="g-mono">' + esc(x.ch) + '</td><td class="c">' + n + "</td></tr>"; }).join("") + "</tbody></table></div>";
  }
  /* downloads list */
  var dl = $("cd-dls");
  if (dl) dl.innerHTML = [["data/decisions.csv", "Decisions (CSV)", "Putusan (CSV)"], ["data/arguments.csv", "Arguments per decision (CSV)", "Argumen per putusan (CSV)"], ["data/reasoning.csv", "Reasoning tools per decision (CSV)", "Alat penalaran per putusan (CSV)"], ["data/reasoning-tools.csv", "Reasoning tool codes (CSV)", "Kode alat penalaran (CSV)"], ["data/argument-codes.csv", "Argument codes (CSV)", "Kode argumen (CSV)"], ["data/sources.csv", "Sources (CSV)", "Sumber (CSV)"], ["data/timeline.csv", "What happened next (CSV)", "Apa yang terjadi sesudahnya (CSV)"], ["data/codebook.csv", "Codebook (CSV)", "Buku kode (CSV)"], ["data/decisions.json", "All data (JSON)", "Semua data (JSON)"]]
    .map(function (x) { return '<a class="g-btn dl" href="' + x[0] + '" download>' + esc(t(x[1], x[2])) + "</a>"; }).join("");
})();
