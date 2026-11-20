/* Hate speech, voting and non-citizen protection: renders the page from window.HV (hv-data.js). EN/ID follows the site language switch. */
(function () {
  "use strict";
  var G = window.HV || {};
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); };
  var ID = function () { return document.documentElement.lang === "id"; };
  var t = function (en, id) { return ID() && id ? id : en; };
  var fn = function (v, d) { if (v == null || !isFinite(v)) return "–"; return Number(v).toLocaleString(ID() ? "id-ID" : "en-US", {minimumFractionDigits: d == null ? 2 : d, maximumFractionDigits: d == null ? 2 : d}); };
  var fp = function (p) { return p == null || !isFinite(p) ? "–" : p < 0.001 ? "< 0.001" : fn(p, 3); };
  var S = G.countries || [], CB = G.codebook || [], C = G.codes || {}, R = G.rows || [];
  var row = function (k) { return R.filter(function (r) { return r.iso3 === k; })[0] || {}; };
  var cty = function (k) { return S.filter(function (x) { return x.k === k; })[0] || {}; };
  var cname = function (k) { var s = cty(k); return t(s.n, s.n_id) || k; };
  var GRP = {W: ["Western", "Barat"], N: ["Non-Western", "Non-Barat"]};

  var LV = {2: ["yes", "Explicit", "Eksplisit"], 1: ["partial", "General", "Umum"], 0: ["no", "None", "Tidak ada"]};
  function pill(v) { var x = LV[v] || ["unclear", "Unclear", "Belum jelas"]; return '<span class="g-pill p-' + x[0] + '">' + esc(t(x[1], x[2])) + "</span>"; }
  function level(d, v) { return t(d["l" + v], d["l" + v + "_id"]); }

  /* ---------- II. at a glance ---------- */
  var sel = null;
  function glance() {
    var h = "<thead><tr><th>" + t("Country", "Negara") + "</th>" + CB.map(function (d) { return "<th>" + esc(t(d.en, d.id)) + "</th>"; }).join("") + "<th>" + t("Index (0–8)", "Indeks (0–8)") + "</th><th>" + t("Comparison group", "Kelompok pembanding") + "</th></tr></thead><tbody>";
    ["W", "N"].forEach(function (g) {
      h += '<tr><td colspan="' + (CB.length + 3) + '" style="background:#DCE8E1;font-family:\'Figtree\',monospace;font-size:12.5px">' + esc(t(GRP[g][0], GRP[g][1])).toUpperCase() + "</td></tr>";
      S.filter(function (s) { return s.g === g; }).forEach(function (s) {
        var r = row(s.k);
        h += "<tr><td><b>" + esc(t(s.n, s.n_id)) + "</b></td>" + CB.map(function (d) {
          var c = (C[s.k] || {})[d.k] || [], on = sel && sel[0] === s.k && sel[1] === d.k;
          return '<td class="c"><button type="button" class="g-cell" data-g="' + s.k + '" data-d="' + d.k + '" aria-pressed="' + !!on + '" title="' + esc(c[1] || "") + '">' + pill(c[0]) + "</button></td>";
        }).join("") + '<td class="c g-mono">' + r.expl_index + '</td><td class="c">' + (r.explicit ? t("Explicit", "Eksplisit") : t("Conventional", "Konvensional")) + "</td></tr>";
      });
    });
    $("g-glance").innerHTML = h + "</tbody>";
    $("g-legend").innerHTML = [2, 1, 0].map(function (v) { return pill(v); }).join(" ") + ' <span class="g-mono">' + t("Click a cell for the provision, a note and the source.", "Klik sel untuk ketentuan, catatan dan sumbernya.") + "</span>";
    cellnote();
  }
  function cellnote() {
    if (!sel) { $("g-cellnote").innerHTML = ""; return; }
    var d = CB.filter(function (x) { return x.k === sel[1]; })[0], c = (C[sel[0]] || {})[sel[1]] || [];
    $("g-cellnote").innerHTML = '<div class="g-card"><h3>' + esc(cname(sel[0])) + " · " + esc(t(d.en, d.id)) + "</h3>" +
      "<p>" + pill(c[0]) + " " + esc(level(d, c[0])) + "</p><p>" + esc(c[1]) + "</p>" +
      '<p class="g-mono">' + t("Source: ", "Sumber: ") + esc(c[2] || "–") + (c[3] ? " · " + t("in force since ", "berlaku sejak ") + c[3] : "") + (c[4] != null ? " · " + t("earlier value ", "nilai sebelumnya ") + c[4] : "") + " · " + t("evidence S (secondary; not yet checked against the official text)", "bukti S (sekunder; belum dicek dengan teks resmi)") + "</p></div>";
  }

  /* ---------- III. outcomes ---------- */
  var OC = [
    ["polhate", "Party hate speech, 2025", "Ucapan kebencian partai, 2025", 2],
    ["polhate_elec", "Party hate speech, election year", "Ucapan kebencian partai, tahun pemilu", 2],
    ["elec_year", "Election", "Pemilu", 0],
    ["nativist_vote", "Nativist vote (%)", "Suara pro-pribumi (%)", 1],
    ["restrict_vote", "Restrictive vote (%)", "Suara restriktif (%)", 1],
    ["stance", "Electorate stance (0–4)", "Sikap pemilih (0–4)", 2],
    ["migstock", "Migrants (% of population)", "Migran (% penduduk)", 1]
  ];
  var sortK = "", sortD = -1;
  function outcomes() {
    var rs = S.map(function (s) { return row(s.k); });
    if (sortK) rs.sort(function (a, b) { var x = a[sortK], y = b[sortK]; if (x == null) return 1; if (y == null) return -1; return sortD * (x - y); });
    var h = "<thead><tr><th>" + t("Country", "Negara") + "</th><th>" + t("Group", "Kelompok") + "</th>" + OC.map(function (o) { return '<th><button type="button" class="g-cell" data-s="' + o[0] + '" style="font:inherit;text-decoration:underline">' + esc(t(o[1], o[2])) + (sortK === o[0] ? (sortD < 0 ? " ▼" : " ▲") : "") + "</button></th>"; }).join("") + "</tr></thead><tbody>";
    rs.forEach(function (r) {
      h += "<tr><td><b>" + esc(cname(r.iso3)) + "</b></td><td>" + esc(t(GRP[r.western ? "W" : "N"][0], GRP[r.western ? "W" : "N"][1])) + (r.explicit ? " · " + t("explicit", "eksplisit") : "") + "</td>" + OC.map(function (o) { return '<td class="c g-mono">' + (o[0] === "elec_year" ? (r.elec_year || "–") : fn(r[o[0]], o[3])) + "</td>"; }).join("") + "</tr>";
    });
    $("g-out").innerHTML = h + "</tbody>";
    $("g-sortnote").innerHTML = sortK ? '<button type="button" class="g-btn" id="g-unsort">' + t("Back to the regional order", "Kembali ke urutan kawasan") + "</button>" : "";
  }

  /* ---------- IV. findings ---------- */
  function vals(rs, k) { return rs.map(function (r) { return r[k]; }).filter(function (v) { return v != null && isFinite(v); }); }
  function mean(a) { return a.reduce(function (s, v) { return s + v; }, 0) / a.length; }
  var H = [
    ["polhate", "Party hate speech, 2025 (V-Dem)", "Ucapan kebencian partai, 2025 (V-Dem)", "H1"],
    ["polhate_elec", "Party hate speech in the election year", "Ucapan kebencian partai pada tahun pemilu", "H1"],
    ["nativist_vote", "Vote for nativist parties (%)", "Suara partai pro-pribumi (%)", "H2"],
    ["restrict_vote", "Vote for restrictive parties (%)", "Suara partai restriktif (%)", "H2"],
    ["stance", "Vote-weighted immigration stance (0–4)", "Sikap imigrasi berbobot suara (0–4)", "H2"]
  ];
  function groupTests(rows, key, tabId, readId) {
    var T = IMRStats.tests;
    var ex = rows.filter(function (r) { return r[key]; }), co = rows.filter(function (r) { return !r[key]; });
    if (ex.length < 3 || co.length < 3) { $(tabId).innerHTML = ""; $(readId).innerHTML = '<p class="g-empty">' + t("Each group needs at least three countries. Widen the definition or include more countries.", "Setiap kelompok memerlukan setidaknya tiga negara. Perluas definisi atau sertakan lebih banyak negara.") + "</p>"; return; }
    var res = H.map(function (h) { var a = vals(ex, h[0]), b = vals(co, h[0]), w = T.welch(a, b), pm = T.permDiff(a, b, "two"); return {h: h, a: a, b: b, w: w, pm: pm}; });
    var adj = T.holm(res.map(function (x) { return x.pm.p; }));
    var tb = "<thead><tr><th>" + t("Hypothesis", "Hipotesis") + "</th><th>" + t("Outcome", "Hasil") + "</th><th>" + t("Explicit: mean (n)", "Eksplisit: rata-rata (n)") + "</th><th>" + t("Conventional: mean (n)", "Konvensional: rata-rata (n)") + "</th><th>" + t("Difference [95% CI]", "Selisih [IK 95%]") + "</th><th>" + t("p, Welch", "p, Welch") + "</th><th>" + t("p, permutation", "p, permutasi") + "</th><th>" + t("p, Holm", "p, Holm") + "</th></tr></thead><tbody>";
    res.forEach(function (x, i) {
      tb += "<tr><td class=\"g-mono\">" + x.h[3] + "</td><td>" + esc(t(x.h[1], x.h[2])) + '</td><td class="c g-mono">' + fn(mean(x.a)) + " (" + x.a.length + ')</td><td class="c g-mono">' + fn(mean(x.b)) + " (" + x.b.length + ')</td><td class="c g-mono">' + fn(x.w.d) + " [" + fn(x.w.lo) + ", " + fn(x.w.hi) + ']</td><td class="c g-mono">' + fp(x.w.p) + '</td><td class="c g-mono">' + fp(x.pm.p) + '</td><td class="c g-mono">' + fp(adj[i]) + "</td></tr>";
    });
    $(tabId).innerHTML = tb + "</tbody>";
    var sig = res.filter(function (x, i) { return adj[i] < 0.05; });
    var lower = res.filter(function (x) { return x.w.d < 0; }).length;
    $(readId).innerHTML = "<p>" + (ID()
      ? "Pada " + lower + " dari " + res.length + " ukuran, negara dengan perlindungan eksplisit bagi orang yang bukan warga negara memiliki nilai rata-rata lebih rendah daripada negara dengan hukum konvensional. " + (sig.length ? sig.length + " selisih tetap signifikan setelah koreksi Holm." : "Tidak ada selisih yang signifikan setelah koreksi Holm atas lima uji, sehingga data ini tidak cukup untuk menolak hipotesis nol bahwa kedua kelompok sama.")
      : "On " + lower + " of " + res.length + " measures, countries whose law explicitly protects non-citizens have lower average values than countries with conventional law. " + (sig.length ? sig.length + " difference" + (sig.length > 1 ? "s remain" : " remains") + " significant after Holm correction." : "No difference survives Holm correction across the five tests, so the data do not allow rejecting the null hypothesis that the two groups are alike.")) + "</p>";

  }

  function findings() {
    var T = window.IMRStats && IMRStats.tests; if (!T) { $("g-find").innerHTML = '<p class="g-empty">' + t("The statistics engine did not load.", "Mesin statistik tidak termuat.") + "</p>"; return; }
    groupTests(R, "explicit", "g-ftab", "g-fread");
    var ex = R.filter(function (r) { return r.explicit; }), co = R.filter(function (r) { return !r.explicit; });
    /* link between hate speech and voting, by group */
    var lk = [["nativist_vote", "Nativist vote", "Suara pro-pribumi"], ["stance", "Electorate stance", "Sikap pemilih"]];
    var grp = [["all", t("All countries", "Semua negara"), R], ["ex", t("Explicit protection", "Perlindungan eksplisit"), ex], ["co", t("Conventional law", "Hukum konvensional"), co], ["w", t("Western", "Barat"), R.filter(function (r) { return r.western; })], ["n", t("Non-Western", "Non-Barat"), R.filter(function (r) { return !r.western; })]];
    var lt = "<thead><tr><th>" + t("Countries", "Negara") + "</th>" + lk.map(function (l) { return "<th>" + esc(t("Party hate speech × ", "Ucapan kebencian partai × ") + t(l[1], l[2])) + ": r [95% CI] · ρ · n</th>"; }).join("") + "</tr></thead><tbody>";
    var cors = {};
    grp.forEach(function (g) {
      lt += "<tr><td>" + esc(g[1]) + "</td>" + lk.map(function (l) {
        var pr = g[2].filter(function (r) { return r.polhate_elec != null && r[l[0]] != null; });
        if (pr.length < 5) return '<td class="c">–</td>';
        var x = pr.map(function (r) { return r.polhate_elec; }), y = pr.map(function (r) { return r[l[0]]; }), p = T.pearson(x, y), s = T.spearman(x, y);
        cors[g[0] + l[0]] = p;
        return '<td class="c g-mono">' + fn(p.r) + " [" + fn(p.lo) + ", " + fn(p.hi) + "] · " + fn(s.r) + " · " + pr.length + "</td>";
      }).join("") + "</tr>";
    });
    $("g-ltab").innerHTML = lt + "</tbody>";

    /* H3: interaction */
    var D = R.filter(function (r) { return r.polhate_elec != null && r.stance != null; });
    var X = D.map(function (r) { return [1, r.polhate_elec, r.explicit, r.polhate_elec * r.explicit, r.libdem, r.western]; }), y = D.map(function (r) { return r.stance; });
    var m = T.ols(X, y), it = "";
    if (m) {
      var nm = [t("Intercept", "Konstanta"), t("Party hate speech, election year", "Ucapan kebencian partai, tahun pemilu"), t("Explicit protection", "Perlindungan eksplisit"), t("Hate speech × explicit protection", "Ucapan kebencian × perlindungan eksplisit"), t("Liberal democracy index", "Indeks demokrasi liberal"), t("Western", "Barat")];
      it = "<thead><tr><th>" + t("Term", "Suku") + "</th><th>b</th><th>" + t("95% CI", "IK 95%") + "</th><th>p</th></tr></thead><tbody>" + nm.map(function (n, i) { return "<tr><td>" + esc(n) + '</td><td class="c g-mono">' + fn(m.b[i]) + '</td><td class="c g-mono">[' + fn(m.lo[i]) + ", " + fn(m.hi[i]) + ']</td><td class="c g-mono">' + fp(m.p[i]) + "</td></tr>"; }).join("") + "</tbody>";
      $("g-itab").innerHTML = it;
      var ce = cors.exstance, cc = cors.costance;
      $("g-iread").innerHTML = "<p>" + (ID()
        ? "Di antara negara dengan hukum konvensional, ucapan kebencian partai dan sikap pemilih terhadap imigrasi berkorelasi r = " + fn(cc && cc.r) + "; di antara negara dengan perlindungan eksplisit r = " + fn(ce && ce.r) + ". Suku interaksi dalam model (n = " + m.n + ", R² = " + fn(m.r2) + ") adalah b = " + fn(m.b[3]) + " (p " + fp(m.p[3]) + "): " + (m.p[3] < 0.05 ? (m.b[3] < 0 ? "hubungan lebih lemah" : "hubungan lebih kuat") + " di negara dengan perlindungan eksplisit, dengan demokrasi dan kawasan dikendalikan." : "data tidak menunjukkan bahwa hubungan tersebut berbeda secara jelas antara kedua kelompok.")
        : "Among countries with conventional law, party hate speech and the electorate's immigration stance correlate at r = " + fn(cc && cc.r) + "; among countries with explicit protection, r = " + fn(ce && ce.r) + ". The interaction term in the model (n = " + m.n + ", R² = " + fn(m.r2) + ") is b = " + fn(m.b[3]) + " (p " + fp(m.p[3]) + "): " + (m.p[3] < 0.05 ? "the link is " + (m.b[3] < 0 ? "weaker" : "stronger") + " where protection is explicit, holding democracy and region constant." : "the data do not show the link to differ clearly between the two groups.")) + "</p>";
    }
  }

  /* ---------- V. impunity ---------- */
  var HC = G.hca || {}, impSel = null;
  function impunity() {
    var h = "<thead><tr><th>" + t("Country", "Negara") + "</th><th>" + t("Hate crime aggravation", "Pemberatan kejahatan kebencian") + "</th><th>" + t("Access to justice", "Akses keadilan") + "</th><th>" + t("Equal protection across groups", "Perlindungan setara antarkelompok") + "</th><th>" + t("Rule of law", "Negara hukum") + "</th><th>" + t("Prosecuted · sentenced, % of recorded (OSCE)", "Dituntut · divonis, % dari yang tercatat (OSCE)") + "</th></tr></thead><tbody>";
    ["W", "N"].forEach(function (g) {
      h += '<tr><td colspan="6" style="background:#DCE8E1;font-family:\'Figtree\',monospace;font-size:12.5px">' + esc(t(GRP[g][0], GRP[g][1])).toUpperCase() + "</td></tr>";
      S.filter(function (s) { return s.g === g; }).forEach(function (s) {
        var r = row(s.k), c = HC[s.k] || [];
        h += "<tr><td><b>" + esc(t(s.n, s.n_id)) + '</b></td><td class="c"><button type="button" class="g-cell" data-h="' + s.k + '" aria-pressed="' + (impSel === s.k) + '" title="' + esc(c[1] || "") + '">' + pill(c[0]) + '</button></td><td class="c g-mono">' + fn(r.acjst) + '</td><td class="c g-mono">' + fn(r.eqprotec) + '</td><td class="c g-mono">' + fn(r.rule) + '</td><td class="c g-mono">' + (r.osce_total_pm != null ? (r.osce_pros_rate == null && r.osce_sent_rate == null ? t("not reported", "tidak dilaporkan") : fn(r.osce_pros_rate, 1) + " · " + fn(r.osce_sent_rate, 1)) : t("not covered", "tidak dicakup")) + "</td></tr>";
      });
    });
    $("g-imp").innerHTML = h + "</tbody>";
    var c = impSel && HC[impSel];
    $("g-impnote").innerHTML = c ? '<div class="g-card" style="margin-top:18px"><h3>' + esc(cname(impSel)) + " · " + t("Hate crime aggravation", "Pemberatan kejahatan kebencian") + "</h3><p>" + pill(c[0]) + " " + esc(c[1]) + '</p><p class="g-mono">' + t("Source: ", "Sumber: ") + esc(c[2]) + (c[3] ? " · " + t("in force since ", "berlaku sejak ") + c[3] : "") + " · " + t("evidence S", "bukti S") + "</p></div>" : '<p class="g-mono" style="margin-top:12px">' + t("Explicit: names nationality, nation, xenophobia or migrant status · General: race, ethnicity, colour, religion or national origin only · None: no general provision. Click a cell for the provision.", "Eksplisit: menyebut kewarganegaraan, bangsa, xenofobia atau status migran · Umum: hanya ras, etnis, warna kulit, agama atau asal kebangsaan · Tidak ada: tidak ada ketentuan umum. Klik sel untuk ketentuannya.") + "</p>";
  }

  /* ---------- VI. build your own definition ---------- */
  var FT = [["const"], ["adl"], ["hsl"], ["mig"], ["hca", "Hate crime aggravation", "Pemberatan kejahatan kebencian"]];
  var BD0 = {feat: {const: 1, adl: 0, hsl: 0, mig: 1, hca: 0}, min: 1, w: {const: 1, adl: 1, hsl: 1, mig: 1, hca: 0}, inc: {W: 1, N: 1, aut: 1, lka: 1}};
  var BD = JSON.parse(JSON.stringify(BD0));
  var ftName = function (f) { var d = CB.filter(function (x) { return x.k === f[0]; })[0]; return d ? t(d.en, d.id) : t(f[1], f[2]); };
  var codeOf = function (r, k) { return k === "hca" ? r.hca : r[k]; };
  function myRows() {
    var ks = FT.map(function (f) { return f[0]; });
    return R.filter(function (r) {
      if (!BD.inc[r.western ? "W" : "N"]) return false;
      if (!BD.inc.aut && !r.democracy) return false;
      if (!BD.inc.lka && r.iso3 === "LKA") return false;
      return true;
    }).map(function (r) {
      var o = {}; for (var k in r) o[k] = r[k];
      var n2 = ks.filter(function (k) { return BD.feat[k] && codeOf(r, k) === 2; }).length;
      o.my_explicit = n2 >= BD.min ? 1 : 0;
      o.my_index = ks.reduce(function (s, k) { return s + BD.w[k] * codeOf(r, k); }, 0);
      return o;
    });
  }
  function builder() {
    var nf = FT.filter(function (f) { return BD.feat[f[0]]; }).length;
    if (BD.min > Math.max(nf, 1)) BD.min = Math.max(nf, 1);
    var h = '<div class="g-grid2"><div><p class="g-h4">' + t("1. What counts as explicit protection?", "1. Apa yang dihitung sebagai perlindungan eksplisit?") + "</p><p class=\"g-note\" style=\"margin:0 0 8px\">" + t("A country is in your explicit group when enough of the ticked features name non-citizens or nationality (score 2).", "Suatu negara masuk kelompok eksplisit Anda bila cukup banyak fitur yang dicentang menyebut orang yang bukan warga negara atau kewarganegaraan (nilai 2).") + "</p>";
    FT.forEach(function (f) { h += '<label style="display:flex;gap:10px;align-items:center;min-height:40px;font-size:16px"><input type="checkbox" data-bf="' + f[0] + '"' + (BD.feat[f[0]] ? " checked" : "") + ' style="width:20px;height:20px;accent-color:#1E6B4A"> ' + esc(ftName(f)) + "</label>"; });
    h += '<label style="display:block;margin-top:8px;font-size:15px">' + t("At least this many ticked features must be explicit: ", "Setidaknya sebanyak ini fitur yang dicentang harus eksplisit: ") + '<select data-bmin style="min-height:40px;font:inherit;border:1px solid #172D24;background:#fff">' + [1, 2, 3, 4, 5].filter(function (n) { return n <= Math.max(nf, 1); }).map(function (n) { return '<option' + (n === BD.min ? " selected" : "") + ">" + n + "</option>"; }).join("") + "</select></label>";
    h += '<p class="g-h4" style="margin-top:22px">' + t("2. Which countries?", "2. Negara mana?") + "</p>";
    [["W", t("Western democracies", "Demokrasi Barat")], ["N", t("Non-Western democracies", "Demokrasi non-Barat")], ["aut", t("Countries V-Dem classifies as electoral autocracies (India, Indonesia, Mexico, Philippines)", "Negara yang diklasifikasikan V-Dem sebagai otokrasi elektoral (India, Indonesia, Meksiko, Filipina)")], ["lka", t("Sri Lanka (outlier on the vote measures)", "Sri Lanka (pencilan pada ukuran suara)")]].forEach(function (c) {
      h += '<label style="display:flex;gap:10px;align-items:center;min-height:40px;font-size:16px"><input type="checkbox" data-bi="' + c[0] + '"' + (BD.inc[c[0]] ? " checked" : "") + ' style="width:20px;height:20px;accent-color:#1E6B4A"> ' + esc(c[1]) + "</label>";
    });
    h += '</div><div><p class="g-h4">' + t("3. Weights for your own index", "3. Bobot untuk indeks Anda sendiri") + '</p><p class="g-note" style="margin:0 0 8px">' + t("Your index adds each feature's score (0, 1 or 2) times its weight. It appears in the tools below as \u201cYour index\u201d.", "Indeks Anda menjumlahkan nilai setiap fitur (0, 1 atau 2) dikali bobotnya. Indeks ini muncul di alat di bawah sebagai \u201cIndeks Anda\u201d.") + '</p><div class="g-w" style="grid-template-columns:1fr">';
    FT.forEach(function (f) { h += "<label>" + esc(ftName(f)) + ' <output id="bw-' + f[0] + '">' + BD.w[f[0]] + '</output><input type="range" min="0" max="3" step="1" value="' + BD.w[f[0]] + '" data-bw="' + f[0] + '"></label>'; });
    h += '</div><div class="g-btns"><button type="button" class="g-btn" data-breset>' + t("Reset", "Atur ulang") + '</button><button type="button" class="g-btn dl" data-bdl>' + t("Download your dataset (CSV)", "Unduh dataset Anda (CSV)") + "</button></div></div></div>";
    $("g-build").innerHTML = h;
    rebuild();
  }
  function rebuild() {
    var rs = myRows(), ex = rs.filter(function (r) { return r.my_explicit; });
    $("g-bcount").innerHTML = '<p class="g-mono">' + rs.length + t(" countries included · ", " negara disertakan · ") + ex.length + t(" in your explicit group: ", " dalam kelompok eksplisit Anda: ") + esc(ex.map(function (r) { return cname(r.iso3); }).join(", ") || "–") + "</p>";
    if (window.IMRStats) groupTests(rs, "my_explicit", "g-mytab", "g-myread");
    stats(rs);
  }
  function builderEvents() {
    var el = $("g-build");
    el.addEventListener("change", function (e) {
      var x = e.target;
      if (x.hasAttribute("data-bf")) { BD.feat[x.getAttribute("data-bf")] = x.checked ? 1 : 0; builder(); return; }
      if (x.hasAttribute("data-bmin")) BD.min = +x.value;
      if (x.hasAttribute("data-bi")) BD.inc[x.getAttribute("data-bi")] = x.checked ? 1 : 0;
      if (x.hasAttribute("data-bw")) BD.w[x.getAttribute("data-bw")] = +x.value;
      rebuild();
    });
    el.addEventListener("input", function (e) { var k = e.target.getAttribute("data-bw"); if (k) $("bw-" + k).textContent = e.target.value; });
    el.addEventListener("click", function (e) {
      if (e.target.closest("[data-breset]")) { BD = JSON.parse(JSON.stringify(BD0)); builder(); }
      if (e.target.closest("[data-bdl]")) { var rs = myRows(); save("imr-hate-speech-voting-my-dataset-v" + G.version + ".csv", csv(rs, Object.keys(rs[0])), "text/csv"); }
    });
  }

  /* ---------- V. explore ---------- */
  function stats(base) {
    if (!window.IMRStats) return;
    var rows = (base || myRows()).map(function (r) { var o = {}; for (var k in r) o[k] = r[k]; o.id = cname(r.iso3); o.group = r.western ? "Western" : "Non-Western"; o.protection = r.explicit ? "Explicit" : "Conventional"; return o; });
    var B = function (k, en, id, yes, no, yi, ni) { return {key: k, type: "bin", label: en, label_id: id, yes: yes, no: no, yes_id: yi, no_id: ni}; };
    var N = function (k, en, id, log) { return {key: k, type: "num", label: en, label_id: id, log: !!log}; };
    var vars = [
      N("polhate", "Party hate speech, 2025 (V-Dem, higher = more often)", "Ucapan kebencian partai, 2025 (V-Dem, makin tinggi = makin sering)"),
      N("polhate_elec", "Party hate speech in the election year (V-Dem)", "Ucapan kebencian partai pada tahun pemilu (V-Dem)"),
      N("polhate_chg", "Change in party hate speech, 2015–2025", "Perubahan ucapan kebencian partai, 2015–2025"),
      N("nativist_vote", "Vote for nativist parties (%, V-Party)", "Suara partai pro-pribumi (%, V-Party)"),
      N("restrict_vote", "Vote for restrictive parties (%, V-Party)", "Suara partai restriktif (%, V-Party)"),
      N("stance", "Vote-weighted immigration stance (0–4, higher = more restrictive)", "Sikap imigrasi berbobot suara (0–4, makin tinggi = makin restriktif)"),
      B("my_explicit", "Your definition of explicit protection", "Definisi perlindungan eksplisit Anda", "Explicit (yours)", "Not explicit (yours)", "Eksplisit (Anda)", "Tidak eksplisit (Anda)"),
      N("my_index", "Your index (your weights)", "Indeks Anda (bobot Anda)"),
      N("expl_index", "Explicitness index (0–8)", "Indeks eksplisit (0–8)"),
      N("expl_index_el", "Explicitness index in the election year (0–8)", "Indeks eksplisit pada tahun pemilu (0–8)"),
      N("tgt_relig", "Online hate targets religious groups (share of V-Dem experts)", "Ucapan kebencian daring menyasar kelompok agama (bagian pakar V-Dem)"),
      N("tgt_ethnic", "Online hate targets ethnic groups (share of experts)", "Ucapan kebencian daring menyasar kelompok etnis (bagian pakar)"),
      N("socgrp_ineq", "Unequal civil liberties across social groups (V-Dem, reversed)", "Ketimpangan kebebasan sipil antarkelompok sosial (V-Dem, dibalik)"),
      N("polar", "Political polarization (V-Dem)", "Polarisasi politik (V-Dem)"),
      N("libdem", "Liberal democracy index (V-Dem)", "Indeks demokrasi liberal (V-Dem)"),
      N("migstock", "International migrants (% of population)", "Migran internasional (% penduduk)"),
      N("gdppc", "GDP per capita (US$)", "PDB per kapita (US$)", true),
      B("explicit", "Law explicitly protects non-citizens (constitution or migrant statute)", "Hukum secara eksplisit melindungi orang yang bukan warga negara (konstitusi atau UU migran)", "Explicit", "Conventional", "Eksplisit", "Konvensional"),
      B("hsl_nat", "Hate speech law names nationality or foreigners", "Hukum ucapan kebencian menyebut kewarganegaraan atau orang asing", "Names them", "Does not", "Menyebut", "Tidak"),
      B("adl_nat", "Anti-discrimination law names nationality or citizenship", "Hukum antidiskriminasi menyebut kewarganegaraan", "Names them", "Does not", "Menyebut", "Tidak"),
      B("western", "Western democracy", "Demokrasi Barat", "Western", "Non-Western", "Barat", "Non-Barat"),
      B("majoritarian", "Majoritarian electoral system", "Sistem pemilu mayoritarian", "Majoritarian", "Proportional or mixed", "Mayoritarian", "Proporsional atau campuran"),
      B("democracy", "Democracy in 2025 (V-Dem Regimes of the World)", "Demokrasi pada 2025 (V-Dem Regimes of the World)", "Democracy", "Electoral autocracy", "Demokrasi", "Otokrasi elektoral"),
      N("acjst", "Access to justice (V-Dem, 0–1)", "Akses keadilan (V-Dem, 0–1)"),
      N("eqprotec", "Equal protection across social groups (V-Dem, 0–1)", "Perlindungan setara antarkelompok sosial (V-Dem, 0–1)"),
      N("rule", "Rule of law (V-Dem, 0–1)", "Negara hukum (V-Dem, 0–1)"),
      N("hca", "Hate crime aggravation (0–2)", "Pemberatan kejahatan kebencian (0–2)"),
      B("hca_nat", "Hate crime aggravation names nationality or xenophobia", "Pemberatan kejahatan kebencian menyebut kewarganegaraan atau xenofobia", "Names them", "Does not", "Menyebut", "Tidak"),
      B("icrmw", "Party to the UN migrant workers convention", "Pihak Konvensi Pekerja Migran PBB", "Party", "Not party", "Pihak", "Bukan pihak"),
      {key: "system", type: "cat", label: "Electoral system", label_id: "Sistem pemilu"}
    ];
    vars.push(N("shi", "Social hostilities involving religion (Pew SHI, 0–10)", "Permusuhan sosial terkait agama (Pew SHI, 0–10)"),
      N("pew_mob_yrs", "Years with religious mob violence, 2013–2022 (Pew)", "Tahun dengan kekerasan massa terkait agama, 2013–2022 (Pew)"),
      N("pew_comm_yrs", "Years with communal violence, 2013–2022 (Pew)", "Tahun dengan kekerasan komunal, 2013–2022 (Pew)"),
      N("acled_mob", "Mob violence per million a year, 2021–2025 (ACLED)", "Kekerasan massa per sejuta per tahun, 2021–2025 (ACLED)"));
    if (G.osce_ready) vars.push(N("osce_xeno_pm", "Racist and xenophobic hate crimes recorded by police per million (OSCE ODIHR)", "Kejahatan kebencian rasis dan xenofobik tercatat polisi per juta (OSCE ODIHR)", true),
      N("osce_total_pm", "All hate crimes recorded by police per million (OSCE ODIHR)", "Semua kejahatan kebencian tercatat polisi per juta (OSCE ODIHR)", true),
      N("osce_pros_rate", "Recorded hate crimes prosecuted (%, OSCE ODIHR)", "Kejahatan kebencian tercatat yang dituntut (%, OSCE ODIHR)"),
      N("osce_sent_rate", "Recorded hate crimes ending in a sentence (%, OSCE ODIHR)", "Kejahatan kebencian tercatat yang berujung vonis (%, OSCE ODIHR)"));
    IMRStats.mount($("g-stats"), {
      rows: rows, filename: "imr-hate-speech-voting", idLabel: "country", vars: vars,
      presets: [
        {q: "Under your definition, do nativist parties win less of the vote?", q_id: "Menurut definisi Anda, apakah partai pro-pribumi meraih suara lebih sedikit?", mode: 0, y: "nativist_vote", g: "my_explicit"},
        {q: "Does your index move with party hate speech?", q_id: "Apakah indeks Anda bergerak bersama ucapan kebencian partai?", mode: 1, x: "my_index", y2: "polhate"},
        {q: "Is party hate speech lower where the law explicitly protects non-citizens?", q_id: "Apakah ucapan kebencian partai lebih rendah di negara yang hukumnya secara eksplisit melindungi orang yang bukan warga negara?", mode: 0, y: "polhate", g: "explicit"},
        {q: "Do nativist parties win a smaller share of the vote there?", q_id: "Apakah partai pro-pribumi meraih suara lebih kecil di sana?", mode: 0, y: "nativist_vote", g: "explicit"},
        {q: "Does party hate speech move with the electorate's immigration stance?", q_id: "Apakah ucapan kebencian partai bergerak bersama sikap imigrasi pemilih?", mode: 1, x: "polhate_elec", y2: "stance"},
        {q: "Does a hate speech law that names nationality go with less party hate speech?", q_id: "Apakah hukum ucapan kebencian yang menyebut kewarganegaraan disertai ucapan kebencian partai yang lebih sedikit?", mode: 0, y: "polhate", g: "hsl_nat"},
        {q: "Holding democracy, region, migrant share and electoral system constant, is the explicitness index associated with party hate speech?", q_id: "Dengan demokrasi, kawasan, porsi migran dan sistem pemilu dikendalikan, apakah indeks eksplisit berhubungan dengan ucapan kebencian partai?", mode: 2, ry: "polhate", preds: ["expl_index", "libdem", "western", "migstock"]},
        {q: "Is equal protection across social groups higher where the law explicitly protects non-citizens?", q_id: "Apakah perlindungan setara antarkelompok sosial lebih tinggi di negara yang hukumnya secara eksplisit melindungi orang yang bukan warga negara?", mode: 0, y: "eqprotec", g: "explicit"},
        {q: "Do countries with more party hate speech offer less access to justice?", q_id: "Apakah negara dengan lebih banyak ucapan kebencian partai menawarkan akses keadilan yang lebih rendah?", mode: 1, x: "polhate", y2: "acjst"},
        {q: "Do countries with a larger nativist vote record more racist and xenophobic hate crime (OSCE countries)?", q_id: "Apakah negara dengan suara pro-pribumi lebih besar mencatat lebih banyak kejahatan kebencian rasis dan xenofobik (negara OSCE)?", mode: 1, x: "nativist_vote", y2: "osce_xeno_pm"},
        {q: "Is the nativist vote higher where social hostilities are higher?", q_id: "Apakah suara pro-pribumi lebih tinggi di negara dengan permusuhan sosial yang lebih tinggi?", mode: 1, x: "nativist_vote", y2: "shi"},
        {q: "Do Western and non-Western democracies differ in party hate speech?", q_id: "Apakah demokrasi Barat dan non-Barat berbeda dalam ucapan kebencian partai?", mode: 0, y: "polhate", g: "western"}
      ],
      defaults: {y: "polhate", g: "explicit", x: "polhate_elec", y2: "stance", preds: ["expl_index", "libdem", "western"]},
      note: "Each row is one country included under your settings above (all 34 by default; vote measures cover 33). Countries are not independent draws from a population, legal codes are secondary and pending checks, and the vote data come from elections held 2015–2019: read every p-value as descriptive, and every association as compatible with several causal stories.",
      note_id: "Setiap baris adalah satu negara yang disertakan menurut pengaturan Anda di atas (34 secara bawaan; ukuran suara mencakup 33). Negara bukan sampel acak dari suatu populasi, kode hukum bersifat sekunder dan menunggu pengecekan, dan data suara berasal dari pemilu 2015–2019: baca setiap nilai p sebagai deskriptif, dan setiap hubungan sebagai sesuai dengan beberapa penjelasan kausal."
    });
  }

  /* ---------- VI b. popularity and hate crime ---------- */
  var PCX = [["nativist_vote", "Vote for nativist parties (%)", "Suara partai pro-pribumi (%)"], ["restrict_vote", "Vote for restrictive parties (%)", "Suara partai restriktif (%)"], ["stance", "Electorate's immigration stance (0–4)", "Sikap imigrasi pemilih (0–4)"]];
  function pcY() {
    var y = [["shi", "Social hostilities involving religion (Pew SHI, 0–10, 2023)", "Permusuhan sosial terkait agama (Pew SHI, 0–10, 2023)"],
      ["pew_mob_yrs", "Years with religious mob violence, 2013–2022 (Pew, 0–10)", "Tahun dengan kekerasan massa terkait agama, 2013–2022 (Pew, 0–10)"],
      ["pew_comm_yrs", "Years with communal violence, 2013–2022 (Pew, 0–10)", "Tahun dengan kekerasan komunal, 2013–2022 (Pew, 0–10)"],
      ["acled_mob", "Mob violence events per million people a year, 2021–2025 (ACLED)", "Peristiwa kekerasan massa per sejuta penduduk per tahun, 2021–2025 (ACLED)"]];
    if (G.osce_ready) y.unshift(["osce_xeno_pm", "Police-recorded racist and xenophobic hate crimes per million, median 2019–2024 (OSCE ODIHR)", "Kejahatan kebencian rasis dan xenofobik tercatat polisi per juta, median 2019–2024 (OSCE ODIHR)"],
      ["osce_total_pm", "All police-recorded hate crimes per million, median 2019–2024 (OSCE ODIHR)", "Semua kejahatan kebencian tercatat polisi per juta, median 2019–2024 (OSCE ODIHR)"],
      ["osce_pros_rate", "Recorded hate crimes prosecuted (%, median year, OSCE ODIHR)", "Kejahatan kebencian tercatat yang dituntut (%, tahun median, OSCE ODIHR)"],
      ["osce_sent_rate", "Recorded hate crimes ending in a sentence (%, median year, OSCE ODIHR)", "Kejahatan kebencian tercatat yang berujung vonis (%, tahun median, OSCE ODIHR)"]);
    return y;
  }
  var PCS = [["all", "All countries", "Semua negara"], ["W", "Western", "Barat"], ["N", "Non-Western", "Non-Barat"], ["ex", "Explicit protection", "Perlindungan eksplisit"], ["co", "Conventional law", "Hukum konvensional"], ["dem", "Democracies only (V-Dem 2025)", "Hanya demokrasi (V-Dem 2025)"]];
  var PCC = [["none", "No controls", "Tanpa kontrol"], ["libdem", "Liberal democracy", "Demokrasi liberal"], ["full", "Liberal democracy, Western, migrant share, GDP per capita (log)", "Demokrasi liberal, Barat, porsi migran, PDB per kapita (log)"]];
  var PC = {x: "nativist_vote", y: "shi", s: "all", c: "none", drop: "", rank: 0};
  function pcRows(xk, yk, s, drop) {
    return R.filter(function (r) {
      if (r[xk] == null || r[yk] == null || r.iso3 === drop) return false;
      return s === "all" || (s === "W" && r.western) || (s === "N" && !r.western) || (s === "ex" && r.explicit) || (s === "co" && !r.explicit) || (s === "dem" && r.democracy);
    });
  }
  function pcSel(k, opts, v) { return '<select data-pc="' + k + '" style="min-height:40px;font:inherit;border:1px solid #172D24;background:#fff;max-width:100%">' + opts.map(function (o) { return '<option value="' + o[0] + '"' + (o[0] === v ? " selected" : "") + ">" + esc(t(o[1], o[2])) + "</option>"; }).join("") + "</select>"; }
  function lab(L, k) { var o = L.filter(function (x) { return x[0] === k; })[0]; return o ? t(o[1], o[2]) : k; }
  function popcrime() {
    var el = $("g-pc"); if (!el) return;
    var T = window.IMRStats && IMRStats.tests; if (!T) { el.innerHTML = '<p class="g-empty">' + t("The statistics engine did not load.", "Mesin statistik tidak termuat.") + "</p>"; return; }
    var Y = pcY(); if (!Y.some(function (y) { return y[0] === PC.y; })) PC.y = Y[0][0];
    var cs = S.map(function (s) { return [s.k, s.n, s.n_id]; });
    var h = '<div class="g-grid2"><label style="display:block">' + t("Popularity of anti-immigrant parties", "Popularitas partai anti-imigran") + "<br>" + pcSel("x", PCX, PC.x) + "</label>" +
      '<label style="display:block">' + t("Hate crime or group violence measure", "Ukuran kejahatan kebencian atau kekerasan kelompok") + "<br>" + pcSel("y", Y, PC.y) + "</label>" +
      '<label style="display:block">' + t("Countries", "Negara") + "<br>" + pcSel("s", PCS, PC.s) + "</label>" +
      '<label style="display:block">' + t("Hold constant", "Kendalikan") + "<br>" + pcSel("c", PCC, PC.c) + "</label>" +
      '<label style="display:block">' + t("Leave one country out", "Keluarkan satu negara") + "<br>" + pcSel("drop", [["", "None", "Tidak ada"]].concat(cs), PC.drop) + "</label>" +
      '<label style="display:flex;gap:8px;align-items:center;margin-top:22px"><input type="checkbox" data-pc="rank"' + (PC.rank ? " checked" : "") + "> " + t("Plot ranks instead of values", "Tampilkan peringkat, bukan nilai") + "</label></div>";
    var D = pcRows(PC.x, PC.y, PC.s, PC.drop);
    if (D.length < 6) { el.innerHTML = h + '<p class="g-empty">' + t("Fewer than six countries have both measures under these settings.", "Kurang dari enam negara memiliki kedua ukuran dengan pengaturan ini.") + "</p>"; return; }
    var x = D.map(function (r) { return r[PC.x]; }), y = D.map(function (r) { return r[PC.y]; });
    var pr = T.pearson(x, y), sp = T.spearman(x, y), pm = T.permCor(x, y, "two", 5000);
    var ctl = null;
    if (PC.c !== "none") {
      var DD = D.filter(function (r) { return r.libdem != null && (PC.c !== "full" || (r.migstock != null && r.gdppc != null)); });
      var XX = DD.map(function (r) { return PC.c === "full" ? [1, r[PC.x], r.libdem, r.western, r.migstock, Math.log(r.gdppc)] : [1, r[PC.x], r.libdem]; });
      ctl = T.ols(XX, DD.map(function (r) { return r[PC.y]; }));
    }
    /* scatter */
    var rk = function (a) { var o = a.map(function (v, i) { return [v, i]; }).sort(function (p, q) { return p[0] - q[0]; }), r = new Array(a.length); o.forEach(function (p, j) { r[p[1]] = j + 1; }); return r; };
    var px = PC.rank ? rk(x) : x, py = PC.rank ? rk(y) : y;
    var W = 640, H = 360, L = 52, B = 44, mn = function (a) { return Math.min.apply(null, a); }, mx = function (a) { return Math.max.apply(null, a); };
    var x0 = mn(px), x1 = mx(px), y0 = mn(py), y1 = mx(py); if (x1 === x0) x1 = x0 + 1; if (y1 === y0) y1 = y0 + 1;
    var sx = function (v) { return L + (v - x0) / (x1 - x0) * (W - L - 48); }, sy = function (v) { return H - B - (v - y0) / (y1 - y0) * (H - B - 16); };
    var fit = T.ols(px.map(function (v) { return [1, v]; }), py);
    var svg = '<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="' + esc(t("Scatter plot", "Diagram sebar")) + '" style="width:100%;height:auto;max-width:720px;display:block;margin:16px 0 4px;font-family:\'Figtree\',monospace;font-size:11px">' +
      '<line x1="' + L + '" y1="' + (H - B) + '" x2="' + (W - 20) + '" y2="' + (H - B) + '" stroke="#B2C7BC"/><line x1="' + L + '" y1="16" x2="' + L + '" y2="' + (H - B) + '" stroke="#B2C7BC"/>' +
      '<text x="' + L + '" y="' + (H - B + 16) + '" fill="#3D5A4D">' + fn(x0, 1) + '</text><text x="' + (W - 20) + '" y="' + (H - B + 16) + '" text-anchor="end" fill="#3D5A4D">' + fn(x1, 1) + "</text>" +
      '<text x="' + (L - 6) + '" y="' + (H - B) + '" text-anchor="end" fill="#3D5A4D">' + fn(y0, 1) + '</text><text x="' + (L - 6) + '" y="22" text-anchor="end" fill="#3D5A4D">' + fn(y1, 1) + "</text>" +
      '<text x="' + ((W + L) / 2) + '" y="' + (H - 8) + '" text-anchor="middle" fill="#172D24">' + esc((PC.rank ? t("Rank: ", "Peringkat: ") : "") + lab(PCX, PC.x)) + "</text>";
    if (fit) svg += '<line x1="' + sx(x0) + '" y1="' + sy(fit.b[0] + fit.b[1] * x0) + '" x2="' + sx(x1) + '" y2="' + sy(fit.b[0] + fit.b[1] * x1) + '" stroke="#1E6B4A" stroke-width="2" stroke-dasharray="6 4"/>';
    D.forEach(function (r, i) { svg += '<g><title>' + esc(cname(r.iso3) + ": " + fn(x[i], 1) + " · " + fn(y[i], 2)) + '</title><circle cx="' + sx(px[i]) + '" cy="' + sy(py[i]) + '" r="5" fill="' + (r.explicit ? "#172D24" : "#FFFFFF") + '" stroke="#172D24" stroke-width="1.5"/><text x="' + (sx(px[i]) + 7) + '" y="' + (sy(py[i]) + 4) + '" fill="#2E493D">' + esc(r.iso3) + "</text></g>"; });
    svg += "</svg>";
    h += svg + '<p class="g-note" style="margin:0">' + esc(t("Vertical axis: ", "Sumbu tegak: ") + (PC.rank ? t("rank of ", "peringkat ") : "") + lab(Y, PC.y)) + t(". Filled dots: explicit protection; open dots: conventional law. Dashed line: least-squares fit. Hover for values.", ". Titik penuh: perlindungan eksplisit; titik kosong: hukum konvensional. Garis putus-putus: garis kuadrat terkecil. Arahkan kursor untuk melihat nilai.") + "</p>";
    /* results */
    h += '<div class="g-scroll" style="margin-top:14px"><table class="g-t"><thead><tr><th>' + t("Test", "Uji") + "</th><th>" + t("Estimate", "Estimasi") + "</th><th>" + t("95% CI", "IK 95%") + "</th><th>p</th><th>n</th></tr></thead><tbody>" +
      "<tr><td>" + t("Pearson correlation", "Korelasi Pearson") + '</td><td class="c g-mono">r = ' + fn(pr.r) + '</td><td class="c g-mono">[' + fn(pr.lo) + ", " + fn(pr.hi) + ']</td><td class="c g-mono">' + fp(pr.p) + '</td><td class="c g-mono">' + pr.n + "</td></tr>" +
      "<tr><td>" + t("Spearman rank correlation", "Korelasi peringkat Spearman") + '</td><td class="c g-mono">ρ = ' + fn(sp.r) + '</td><td class="c g-mono">–</td><td class="c g-mono">' + fp(sp.p) + '</td><td class="c g-mono">' + D.length + "</td></tr>" +
      "<tr><td>" + t("Permutation test (5,000 reshuffles, Pearson r)", "Uji permutasi (5.000 pengacakan, r Pearson)") + '</td><td class="c g-mono">–</td><td class="c g-mono">–</td><td class="c g-mono">' + fp(pm.p) + '</td><td class="c g-mono">' + D.length + "</td></tr>" +
      (ctl ? "<tr><td>" + t("Regression slope with controls: ", "Kemiringan regresi dengan kontrol: ") + esc(lab(PCC, PC.c)) + '</td><td class="c g-mono">b = ' + fn(ctl.b[1], 3) + '</td><td class="c g-mono">[' + fn(ctl.lo[1], 3) + ", " + fn(ctl.hi[1], 3) + ']</td><td class="c g-mono">' + fp(ctl.p[1]) + '</td><td class="c g-mono">' + ctl.n + "</td></tr>" : "") +
      "</tbody></table></div>";
    var r = pr.r, sz = Math.abs(r) < 0.1 ? t("almost no", "hampir tidak ada") : Math.abs(r) < 0.3 ? t("a weak", "lemah") : Math.abs(r) < 0.5 ? t("a moderate", "sedang") : t("a strong", "kuat");
    var dir = r > 0 ? t("positive", "positif") : t("negative", "negatif"), sig = pm.p < 0.05;
    h += '<div class="g-card" style="margin-top:14px"><p style="margin:0">' + (ID()
      ? "Di " + D.length + " negara, hubungan antara " + lab(PCX, PC.x).toLowerCase() + " dan " + lab(Y, PC.y).charAt(0).toLowerCase() + lab(Y, PC.y).slice(1) + " " + (Math.abs(r) < 0.1 ? "hampir tidak ada" : "bersifat " + dir + " dan " + sz) + " (r = " + fn(r) + ", ρ = " + fn(sp.r) + "). " + (sig ? "Hubungan sebesar ini jarang muncul jika negara diacak (p permutasi " + fp(pm.p) + ")." : "Hubungan sebesar ini sering muncul secara kebetulan dengan jumlah negara sebanyak ini (p permutasi " + fp(pm.p) + ").") + (ctl ? " Dengan kontrol, kemiringannya b = " + fn(ctl.b[1], 3) + " (p " + fp(ctl.p[1]) + ")." : "")
      : "Across " + D.length + " countries, the association between " + lab(PCX, PC.x).replace(/^Vote/, "the vote").replace(/^Electorate/, "the electorate") + " and " + lab(Y, PC.y).charAt(0).toLowerCase() + lab(Y, PC.y).slice(1) + " is " + (Math.abs(r) < 0.1 ? "close to zero" : sz + " " + dir + " one") + " (r = " + fn(r) + ", ρ = " + fn(sp.r) + "). " + (sig ? "An association this large rarely arises when the countries are reshuffled (permutation p " + fp(pm.p) + ")." : "With this many countries, an association this large often arises by chance (permutation p " + fp(pm.p) + ").") + (ctl ? " With controls, the slope is b = " + fn(ctl.b[1], 3) + " (p " + fp(ctl.p[1]) + ")." : "")) +
      '</p><p class="g-note">' + t("This is a cross-country association, not evidence that votes cause hate crime or the reverse. Vote shares come from elections held 2015–2019; the hate crime measures cover 2013–2025. Pew and ACLED are not specific to migrants, and police-recorded figures partly measure how much the police record. Try leaving out one country to see whether a single case drives the result.", "Ini adalah hubungan antarnegara, bukan bukti bahwa suara menyebabkan kejahatan kebencian atau sebaliknya. Porsi suara berasal dari pemilu 2015–2019; ukuran kejahatan kebencian mencakup 2013–2025. Pew dan ACLED tidak khusus migran, dan angka tercatat polisi sebagian mengukur seberapa banyak polisi mencatat. Coba keluarkan satu negara untuk melihat apakah satu kasus saja yang mendorong hasilnya.") + "</p></div>";
    /* all pairs */
    var ps = [], cells = [];
    PCX.forEach(function (a) { Y.forEach(function (b) { var d = pcRows(a[0], b[0], PC.s, PC.drop); if (d.length < 6) { cells.push(null); return; } var s2 = T.spearman(d.map(function (r) { return r[a[0]]; }), d.map(function (r) { return r[b[0]]; })); cells.push({r: s2.r, p: s2.p, n: d.length}); ps.push(s2.p); }); });
    var hp = T.holm(ps), j = 0; cells.forEach(function (c) { if (c) c.h = hp[j++]; });
    h += '<h4 class="g-h4" style="margin-top:22px">' + t("Every pairing at once (Spearman ρ, Holm-adjusted p, n)", "Semua pasangan sekaligus (ρ Spearman, p disesuaikan Holm, n)") + '</h4><div class="g-scroll"><table class="g-t"><thead><tr><th></th>' + Y.map(function (b) { return "<th>" + esc(t(b[1], b[2])) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      PCX.map(function (a, i) { return "<tr><td>" + esc(t(a[1], a[2])) + "</td>" + Y.map(function (b, k) { var c = cells[i * Y.length + k]; return '<td class="c g-mono"' + (c && c.h < 0.05 ? ' style="font-weight:700"' : "") + ">" + (c ? fn(c.r) + " · " + fp(c.h) + " · " + c.n : "–") + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table></div>" +
      '<p class="g-note">' + t("Holm's adjustment accounts for running all these tests together. Bold cells stay below 0.05 after adjustment. The Countries and Leave one out settings above apply here too.", "Penyesuaian Holm memperhitungkan bahwa semua uji ini dijalankan bersama. Sel tebal tetap di bawah 0,05 setelah penyesuaian. Pengaturan Negara dan Keluarkan satu negara di atas juga berlaku di sini.") + (G.osce_ready ? t(" The OSCE ODIHR measures cover 16 countries, and recording practices differ widely between them (the United Kingdom records far more than any other): rank-based results are the safer guide.", " Ukuran OSCE ODIHR mencakup 16 negara, dan praktik pencatatan sangat berbeda antarnegara (Inggris mencatat jauh lebih banyak daripada negara lain): hasil berbasis peringkat adalah panduan yang lebih aman.") : "") + "</p>";
    el.innerHTML = h;
  }
  function pcEvents() {
    var el = $("g-pc"); if (!el) return;
    el.addEventListener("change", function (e) { var k = e.target.getAttribute("data-pc"); if (!k) return; PC[k] = k === "rank" ? (e.target.checked ? 1 : 0) : e.target.value; popcrime(); });
  }

  /* ---------- VI. profiles ---------- */
  var cur = S.length ? S[0].k : null;
  function profile() {
    $("g-states").innerHTML = S.map(function (s) { return '<button type="button" class="g-btn" data-c="' + s.k + '" aria-pressed="' + (s.k === cur) + '">' + esc(t(s.n, s.n_id)) + "</button>"; }).join("");
    var r = row(cur), ic = (G.intl || {})[cur] || [], yn = function (v) { return v == null ? t("Not applicable", "Tidak berlaku") : v ? t("Yes", "Ya") : t("No", "Tidak"); };
    var h = '<div class="g-grid2"><div class="g-card"><h3>' + t("Domestic law", "Hukum nasional") + "</h3>";
    CB.forEach(function (d) { var c = (C[cur] || {})[d.k] || []; h += '<p class="g-h4">' + esc(t(d.en, d.id)) + " " + pill(c[0]) + "</p><p style=\"margin:0\">" + esc(c[1]) + '</p><p class="g-mono" style="margin:4px 0 0">' + esc(c[2] || "–") + "</p>"; });
    h += '</div><div class="g-card"><h3>' + t("International layer and outcomes", "Lapisan internasional dan hasil") + '</h3><dl class="g-dl">' +
      "<dt>" + t("ICERD party", "Pihak ICERD") + "</dt><dd>" + yn(ic[0]) + "</dd>" +
      "<dt>" + t("ICERD Art. 14 complaints", "Pengaduan Pasal 14 ICERD") + "</dt><dd>" + (ic[1] === null && ic[0] !== null ? t("To check", "Perlu dicek") : yn(ic[1])) + "</dd>" +
      "<dt>" + t("UN migrant workers convention", "Konvensi Pekerja Migran PBB") + "</dt><dd>" + yn(ic[2]) + "</dd>" +
      "<dt>" + t("Regime, 2025 (V-Dem)", "Rezim, 2025 (V-Dem)") + "</dt><dd>" + [t("Closed autocracy", "Otokrasi tertutup"), t("Electoral autocracy", "Otokrasi elektoral"), t("Electoral democracy", "Demokrasi elektoral"), t("Liberal democracy", "Demokrasi liberal")][r.regime] + "</dd>" +
      "<dt>" + t("Party hate speech, 2025", "Ucapan kebencian partai, 2025") + "</dt><dd>" + fn(r.polhate) + " (" + t("change since 2015: ", "perubahan sejak 2015: ") + fn(r.polhate_chg) + ")</dd>" +
      "<dt>" + t("Hate crime aggravation", "Pemberatan kejahatan kebencian") + "</dt><dd>" + pill((HC[cur] || [])[0]) + " " + esc((HC[cur] || [])[1] || "") + "</dd>" +
      "<dt>" + t("Access to justice (V-Dem)", "Akses keadilan (V-Dem)") + "</dt><dd>" + fn(r.acjst) + "</dd>" +
      "<dt>" + t("Electoral system", "Sistem pemilu") + "</dt><dd>" + esc(r.system) + "</dd>" +
      "<dt>" + t("Migrants (% of population)", "Migran (% penduduk)") + "</dt><dd>" + fn(r.migstock, 1) + "</dd></dl>";
    var P = (G.parties || []).filter(function (p) { return p.iso3 === cur; });
    if (P.length) {
      h += '<p class="g-h4">' + t("Parties in the ", "Partai pada pemilu ") + P[0].year + t(" election (V-Party)", " (V-Party)") + '</p><div class="g-scroll"><table class="g-t"><thead><tr><th>' + t("Party", "Partai") + "</th><th>" + t("Vote %", "Suara %") + "</th><th>" + t("Immigration (0–4)", "Imigrasi (0–4)") + "</th><th>" + t("People-centrism (0–4)", "Kerakyatan (0–4)") + "</th><th>" + t("Class", "Kelas") + "</th></tr></thead><tbody>" +
        P.map(function (p) { return "<tr><td>" + esc(p.party) + (p.mapped_from ? ' <span class="g-mono">(' + t("scores of ", "skor ") + esc(p.mapped_from) + ")</span>" : "") + '</td><td class="c g-mono">' + fn(p.vote, 1) + '</td><td class="c g-mono">' + fn(p.immig_osp) + '</td><td class="c g-mono">' + fn(p.people_osp) + '</td><td class="c">' + (p.nativist === 1 ? t("Nativist", "Pro-pribumi") : p.restrictive === 1 ? t("Restrictive", "Restriktif") : p.restrictive === 0 ? "–" : t("No score", "Tanpa skor")) + "</td></tr>"; }).join("") + "</tbody></table></div>";
    } else h += '<p class="g-note">' + t("No usable V-Party election for 2015–2019.", "Tidak ada pemilu V-Party 2015–2019 yang bisa dipakai.") + "</p>";
    $("g-profile").innerHTML = h + "</div></div>";
  }

  /* ---------- VII. codebook ---------- */
  function method() {
    $("g-cb").innerHTML = "<thead><tr><th>" + t("Feature", "Fitur") + "</th><th>" + t("Explicit (2)", "Eksplisit (2)") + "</th><th>" + t("General (1)", "Umum (1)") + "</th><th>" + t("None (0)", "Tidak ada (0)") + "</th></tr></thead><tbody>" +
      CB.map(function (d) { return "<tr><td><b>" + esc(t(d.en, d.id)) + "</b></td><td>" + esc(level(d, 2)) + "</td><td>" + esc(level(d, 1)) + "</td><td>" + esc(level(d, 0)) + "</td></tr>"; }).join("") + "</tbody>";
  }

  /* ---------- IX. downloads ---------- */
  function csv(rows, cols) { var q = function (v) { v = v == null ? "" : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }; return "﻿" + cols.join(",") + "\n" + rows.map(function (r) { return cols.map(function (c) { return q(r[c]); }).join(","); }).join("\n"); }
  function save(name, text, type) { var b = new Blob([text], {type: type}), a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = name; document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500); }
  function sources() {
    var v = "-v" + G.version, P = "imr-hate-speech-voting";
    var D = [["cd", t("Country data (CSV)", "Data negara (CSV)")], ["lc", t("Legal codings with sources (CSV)", "Kode hukum dengan sumber (CSV)")], ["pa", t("Parties (CSV)", "Partai (CSV)")], ["js", t("Everything (JSON)", "Semua (JSON)")]];
    $("g-dls").innerHTML = D.map(function (d) { return '<button type="button" class="g-btn dl" data-d="' + d[0] + '">' + esc(d[1]) + "</button>"; }).join("");
    $("g-dls").onclick = function (e) {
      var b = e.target.closest("[data-d]"); if (!b) return; var k = b.getAttribute("data-d");
      if (k === "cd") save(P + "-countries" + v + ".csv", csv(R, Object.keys(R[0])), "text/csv");
      if (k === "lc") { var L = []; S.forEach(function (s) { CB.forEach(function (d) { var c = C[s.k][d.k]; L.push({iso3: s.k, country: s.n, feature: d.k, value: c[0], note: c[1], source: c[2], in_force_since: c[3], prior_value: c[4], evidence: "S"}); }); }); save(P + "-codings" + v + ".csv", csv(L, ["iso3", "country", "feature", "value", "note", "source", "in_force_since", "prior_value", "evidence"]), "text/csv"); }
      if (k === "pa") save(P + "-parties" + v + ".csv", csv(G.parties, ["iso3", "year", "party", "abbr", "vote", "immig_osp", "people_osp", "restrictive", "nativist", "mapped_from"]), "text/csv");
      if (k === "js") save(P + v + ".json", JSON.stringify(G, null, 1), "application/json");
    };
    $("g-src").innerHTML = "<ul>" + (G.lit || []).map(function (s) { return "<li>" + (s[1] ? '<a href="' + esc(s[1]) + '">' + esc(s[0]) + "</a>" : esc(s[0])) + "</li>"; }).join("") + "</ul>" +
      '<p class="g-mono">' + t("Version ", "Versi ") + esc(G.version) + " · " + t("updated ", "diperbarui ") + esc(G.updated) + "</p><ul class=\"g-mono\">" + (G.changelog || []).map(function (c) { return "<li>" + esc(c[0]) + " · v" + esc(c[1]) + " · " + esc(t(c[2], c[3])) + "</li>"; }).join("") + "</ul>";
  }

  function all() { glance(); outcomes(); findings(); impunity(); builder(); popcrime(); profile(); method(); sources(); }
  document.addEventListener("DOMContentLoaded", function () {
    builderEvents(); pcEvents(); all();
    $("g-glance").addEventListener("click", function (e) { var b = e.target.closest("[data-g]"); if (!b) return; var k = [b.getAttribute("data-g"), b.getAttribute("data-d")]; sel = sel && sel[0] === k[0] && sel[1] === k[1] ? null : k; glance(); });
    $("g-out").addEventListener("click", function (e) { var b = e.target.closest("[data-s]"); if (!b) return; var k = b.getAttribute("data-s"); if (sortK === k) sortD = -sortD; else { sortK = k; sortD = -1; } outcomes(); });
    $("g-sortnote").addEventListener("click", function (e) { if (e.target.id === "g-unsort") { sortK = ""; outcomes(); } });
    $("g-imp").addEventListener("click", function (e) { var b = e.target.closest("[data-h]"); if (!b) return; var k = b.getAttribute("data-h"); impSel = impSel === k ? null : k; impunity(); });
    $("g-states").addEventListener("click", function (e) { var b = e.target.closest("[data-c]"); if (b) { cur = b.getAttribute("data-c"); profile(); } });
    new MutationObserver(function () { all(); }).observe(document.documentElement, {attributes: true, attributeFilter: ["lang"]});
  });
})();
