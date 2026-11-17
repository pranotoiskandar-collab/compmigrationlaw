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
      h += '<tr><td colspan="' + (CB.length + 3) + '" style="background:#E6E9E2;font-family:\'JetBrains Mono\',monospace;font-size:12.5px">' + esc(t(GRP[g][0], GRP[g][1])).toUpperCase() + "</td></tr>";
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
    var h = "<thead><tr><th>" + t("Country", "Negara") + "</th><th>" + t("Hate crime aggravation", "Pemberatan kejahatan kebencian") + "</th><th>" + t("Access to justice", "Akses keadilan") + "</th><th>" + t("Equal protection across groups", "Perlindungan setara antarkelompok") + "</th><th>" + t("Rule of law", "Negara hukum") + "</th><th>" + t("OSCE attrition", "Atrisi OSCE") + "</th></tr></thead><tbody>";
    ["W", "N"].forEach(function (g) {
      h += '<tr><td colspan="6" style="background:#E6E9E2;font-family:\'JetBrains Mono\',monospace;font-size:12.5px">' + esc(t(GRP[g][0], GRP[g][1])).toUpperCase() + "</td></tr>";
      S.filter(function (s) { return s.g === g; }).forEach(function (s) {
        var r = row(s.k), c = HC[s.k] || [], o = (G.osce || {})[s.k];
        h += "<tr><td><b>" + esc(t(s.n, s.n_id)) + '</b></td><td class="c"><button type="button" class="g-cell" data-h="' + s.k + '" aria-pressed="' + (impSel === s.k) + '" title="' + esc(c[1] || "") + '">' + pill(c[0]) + '</button></td><td class="c g-mono">' + fn(r.acjst) + '</td><td class="c g-mono">' + fn(r.eqprotec) + '</td><td class="c g-mono">' + fn(r.rule) + '</td><td class="c g-mono">' + (o ? esc(o) : (g === "W" && s.k !== "AUS" && s.k !== "NZL" ? t("pending", "menunggu") : t("not covered", "tidak dicakup"))) + "</td></tr>";
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
    FT.forEach(function (f) { h += '<label style="display:flex;gap:10px;align-items:center;min-height:40px;font-size:16px"><input type="checkbox" data-bf="' + f[0] + '"' + (BD.feat[f[0]] ? " checked" : "") + ' style="width:20px;height:20px;accent-color:#B3261E"> ' + esc(ftName(f)) + "</label>"; });
    h += '<label style="display:block;margin-top:8px;font-size:15px">' + t("At least this many ticked features must be explicit: ", "Setidaknya sebanyak ini fitur yang dicentang harus eksplisit: ") + '<select data-bmin style="min-height:40px;font:inherit;border:1px solid #1B1F1A;background:#fff">' + [1, 2, 3, 4, 5].filter(function (n) { return n <= Math.max(nf, 1); }).map(function (n) { return '<option' + (n === BD.min ? " selected" : "") + ">" + n + "</option>"; }).join("") + "</select></label>";
    h += '<p class="g-h4" style="margin-top:22px">' + t("2. Which countries?", "2. Negara mana?") + "</p>";
    [["W", t("Western democracies", "Demokrasi Barat")], ["N", t("Non-Western democracies", "Demokrasi non-Barat")], ["aut", t("Countries V-Dem classifies as electoral autocracies (India, Indonesia, Mexico, Philippines)", "Negara yang diklasifikasikan V-Dem sebagai otokrasi elektoral (India, Indonesia, Meksiko, Filipina)")], ["lka", t("Sri Lanka (outlier on the vote measures)", "Sri Lanka (pencilan pada ukuran suara)")]].forEach(function (c) {
      h += '<label style="display:flex;gap:10px;align-items:center;min-height:40px;font-size:16px"><input type="checkbox" data-bi="' + c[0] + '"' + (BD.inc[c[0]] ? " checked" : "") + ' style="width:20px;height:20px;accent-color:#B3261E"> ' + esc(c[1]) + "</label>";
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
    if (G.osce) vars.push(N("osce_xeno_pm", "Police-recorded racist and xenophobic hate crimes per million (OSCE ODIHR)", "Kejahatan kebencian rasis dan xenofobik tercatat polisi per juta (OSCE ODIHR)"));
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
        {q: "Do Western and non-Western democracies differ in party hate speech?", q_id: "Apakah demokrasi Barat dan non-Barat berbeda dalam ucapan kebencian partai?", mode: 0, y: "polhate", g: "western"}
      ],
      defaults: {y: "polhate", g: "explicit", x: "polhate_elec", y2: "stance", preds: ["expl_index", "libdem", "western"]},
      note: "Each row is one country included under your settings above (all 34 by default; vote measures cover 33). Countries are not independent draws from a population, legal codes are secondary and pending checks, and the vote data come from elections held 2015–2019: read every p-value as descriptive, and every association as compatible with several causal stories.",
      note_id: "Setiap baris adalah satu negara yang disertakan menurut pengaturan Anda di atas (34 secara bawaan; ukuran suara mencakup 33). Negara bukan sampel acak dari suatu populasi, kode hukum bersifat sekunder dan menunggu pengecekan, dan data suara berasal dari pemilu 2015–2019: baca setiap nilai p sebagai deskriptif, dan setiap hubungan sebagai sesuai dengan beberapa penjelasan kausal."
    });
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

  function all() { glance(); outcomes(); findings(); impunity(); builder(); profile(); method(); sources(); }
  document.addEventListener("DOMContentLoaded", function () {
    builderEvents(); all();
    $("g-glance").addEventListener("click", function (e) { var b = e.target.closest("[data-g]"); if (!b) return; var k = [b.getAttribute("data-g"), b.getAttribute("data-d")]; sel = sel && sel[0] === k[0] && sel[1] === k[1] ? null : k; glance(); });
    $("g-out").addEventListener("click", function (e) { var b = e.target.closest("[data-s]"); if (!b) return; var k = b.getAttribute("data-s"); if (sortK === k) sortD = -sortD; else { sortK = k; sortD = -1; } outcomes(); });
    $("g-sortnote").addEventListener("click", function (e) { if (e.target.id === "g-unsort") { sortK = ""; outcomes(); } });
    $("g-imp").addEventListener("click", function (e) { var b = e.target.closest("[data-h]"); if (!b) return; var k = b.getAttribute("data-h"); impSel = impSel === k ? null : k; impunity(); });
    $("g-states").addEventListener("click", function (e) { var b = e.target.closest("[data-c]"); if (b) { cur = b.getAttribute("data-c"); profile(); } });
    new MutationObserver(function () { all(); }).observe(document.documentElement, {attributes: true, attributeFilter: ["lang"]});
  });
})();
