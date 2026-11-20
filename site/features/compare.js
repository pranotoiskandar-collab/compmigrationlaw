/* /compare/: two countries side by side, from /features/c/<ISO2>.json (tools/features/build_data.py). */
(function () {
  var FT = window.FT, $ = function (id) { return document.getElementById(id); };
  var TOPICS = [
    ['', 'All topics', 'Semua topik', null],
    ['fees', 'Recruitment fees and agencies', 'Biaya rekrutmen dan agen', /fee|recruit|agen|placement|broker|cost|licen/i],
    ['dw', 'Domestic workers', 'Pekerja rumah tangga', /domestic|household|C189|maid/i],
    ['wage', 'Wages, hours and contracts', 'Upah, jam kerja, dan kontrak', /wage|pay|salar|hour|rest|leave|contract|minimum/i],
    ['move', 'Changing employer and leaving', 'Pindah majikan dan keluar negeri', /employer|mobility|transfer|exit|sponsor|kafala|leav|runaway|abscond/i],
    ['justice', 'Complaints, courts and help', 'Pengaduan, pengadilan, dan bantuan', /complain|court|tribunal|dispute|remed|justice|legal aid|lawyer|labou?r office|inspect|grievance|help/i],
    ['docs', 'Passports and documents', 'Paspor dan dokumen', /passport|document|identity|visa|permit|status|irregular|undocumented/i],
    ['social', 'Insurance, health and social security', 'Asuransi, kesehatan, dan jaminan sosial', /insur|health|medical|social security|welfare|injur|compens|pension/i],
    ['union', 'Unions and association', 'Serikat pekerja dan berserikat', /union|associat|organi[sz]|collective|strike/i],
    ['traffic', 'Forced labor and trafficking', 'Kerja paksa dan perdagangan orang', /forced|traffick|slavery|servitude|exploit/i]
  ];
  var SIT_TOPIC = {fees: ['fees'], wage: ['wages', 'dismissed'], move: ['employer', 'residence', 'dismissed'], justice: null,
    docs: ['passport', 'residence', 'arrest'], social: ['injury', 'health', 'welfare'], union: ['union'], traffic: ['forced'], dw: null};
  var META, LIST;

  function topic() { var k = $('cmp-topic').value; return TOPICS.filter(function (t) { return t[0] === k; })[0]; }
  function hit(txt) { var t = topic(); return !t[3] || t[3].test(txt || ''); }

  function fillSelects() {
    var a = $('cmp-a').value || FT.param('a') || 'ID', b = $('cmp-b').value || FT.param('b') || 'MY', tp = $('cmp-topic').value || FT.param('topic') || '';
    var opts = FT.sortByName(LIST).map(function (c) {
      return '<option value="' + c.c + '">' + FT.esc(FT.name(c)) + ' (' + c.k + '/7)</option>';
    }).join('');
    $('cmp-a').innerHTML = opts; $('cmp-b').innerHTML = opts;
    $('cmp-a').value = a; $('cmp-b').value = b;
    if (!$('cmp-a').value) $('cmp-a').value = 'ID';
    if (!$('cmp-b').value) $('cmp-b').value = 'MY';
    $('cmp-topic').innerHTML = TOPICS.map(function (t) { return '<option value="' + t[0] + '">' + FT.esc(FT.t(t[1], t[2])) + '</option>'; }).join('');
    $('cmp-topic').value = tp;
  }

  function cell(html) { return '<td>' + (html || '<span class="ft-small">' + FT.t('Nothing recorded', 'Belum ada catatan') + '</span>') + '</td>'; }
  function head(A, B, first) {
    return '<thead><tr><th scope="col">' + FT.esc(first) + '</th><th scope="col">' + FT.esc(FT.name(A)) + '</th><th scope="col">' + FT.esc(FT.name(B)) + '</th></tr></thead>';
  }
  function table(A, B, first, body) {
    return '<div class="ft-scroll" tabindex="0" role="region" aria-label="' + FT.esc(first) + '"><table class="ft-t ft-cmp">' + head(A, B, first) + '<tbody>' + body + '</tbody></table></div>';
  }
  function pill(v, label) {
    var n = parseFloat(v), cls = isNaN(n) ? '' : (n >= 2 ? 'ok' : n >= 1 ? 'part' : 'no');
    return '<span class="ft-pill ' + cls + '">' + FT.esc(label || v) + '</span>';
  }

  function render() {
    var a = $('cmp-a').value, b = $('cmp-b').value;
    FT.setParams({a: a, b: b, topic: $('cmp-topic').value});
    $('cmp-share').innerHTML = FT.t('Link to this comparison: ', 'Tautan ke perbandingan ini: ') + '<a href="' + FT.esc(location.href) + '">' + FT.esc(location.href) + '</a>';
    $('cmp-out').innerHTML = '<p class="ft-note">' + FT.t('Loading…', 'Memuat…') + '</p>';
    Promise.all([FT.country(a), FT.country(b)]).then(function (r) { draw(r[0], r[1]); }).catch(function () {
      $('cmp-out').innerHTML = '<p class="ft-empty">' + FT.t('Could not load the data. Please try again.', 'Data tidak dapat dimuat. Silakan coba lagi.') + '</p>';
    });
  }

  function draw(A, B) {
    var out = '', tp = topic();
    // 1. What we hold
    var rows = META.layers.map(function (l) {
      return '<tr><th scope="row">' + FT.esc(FT.t(l[1], l[2])) + '</th><td class="n">' + (A.L[l[0]] || 0) + '</td><td class="n">' + (B.L[l[0]] || 0) + '</td></tr>';
    }).join('');
    out += sec(FT.t('What the databases hold', 'Isi basis data'), table(A, B, FT.t('Kind of data', 'Jenis data'), rows) +
      '<p class="ft-note">' + FT.t('Numbers of entries. A low number can mean we have not collected the material yet; see the ', 'Jumlah entri. Angka yang kecil bisa berarti kami belum menghimpun bahannya; lihat ') +
      '<a href="/coverage/">' + FT.t('coverage map', 'peta cakupan data') + '</a>.</p>');

    // 2. Coded features, lined up when the same database codes both
    var keyed = {}, order = [];
    [[A, 0], [B, 1]].forEach(function (x) {
      x[0].coded.forEach(function (f) {
        if (!hit(f.fn + ' ' + f.n + ' ' + f.g) && !(tp[0] === 'dw' && f.ds === 'domestic-workers')) return;
        var k = f.ds + '|' + f.f;
        if (!keyed[k]) { keyed[k] = {ds: f.ds, fn: f.fn, v: [[], []]}; order.push(k); }
        keyed[k].v[x[1]].push(f);
      });
    });
    if (tp[0] === 'dw') order = order.filter(function (k) { return keyed[k].ds === 'domestic-workers'; });
    var byDs = {};
    order.forEach(function (k) { (byDs[keyed[k].ds] = byDs[keyed[k].ds] || []).push(keyed[k]); });
    function one(f) {
      return (f.g && f.ds !== 'domestic-workers' ? '<div class="ft-small">' + FT.esc(f.g) + '</div>' : '') + pill(f.v, FT.t(f.vl || f.v, f.vi || f.vl || f.v)) +
        (f.n ? '<details><summary class="ft-small">' + FT.t('Details and source', 'Rincian dan sumber') + '</summary><p class="ft-small">' + FT.esc(f.n) +
          (f.src ? '<br><i>' + FT.esc(f.src) + '</i>' : '') + '</p></details>' : '') +
        (f.ok ? '<div class="ft-small">' + FT.t('Checked against official text: ', 'Dicek dengan teks resmi: ') + FT.esc(f.ok) + '</div>' : '');
    }
    var cbody = '', solo = '';
    Object.keys(byDs).forEach(function (ds) {
      var rs = byDs[ds];
      var shared = rs.filter(function (r) { return r.v[0].length && r.v[1].length; });
      if (shared.length) {
        cbody += '<tr class="sub"><th colspan="3">' + FT.dsLink(META, ds) + '</th></tr>';
        shared.forEach(function (r) {
          var f0 = r.v[0][0];
          cbody += '<tr><th scope="row">' + FT.esc(FT.t(r.fn, f0.fi || r.fn)) + '</th>' + r.v.map(function (fs) {
            return cell(fs.map(one).join('<hr style="border:0;border-top:1px dotted #B2C7BC">'));
          }).join('') + '</tr>';
        });
      }
      [A, B].forEach(function (who, i) {
        var only = rs.filter(function (r) { return r.v[i].length && !r.v[1 - i].length; });
        if (!only.length) return;
        solo += '<details class="ft-sec"><summary><b>' + FT.esc(FT.dsName(META, ds)) + '</b>: ' + FT.t('features coded for ', 'fitur yang dikodekan hanya untuk ') + FT.esc(FT.name(who)) +
          FT.t(' only', '') + ' (' + only.length + ')</summary><div class="ft-scroll"><table class="ft-t"><tbody>' + only.map(function (r) {
            return '<tr><th scope="row">' + FT.esc(FT.t(r.fn, r.v[i][0].fi || r.fn)) + '</th><td>' + r.v[i].map(one).join('<hr style="border:0;border-top:1px dotted #B2C7BC">') + '</td></tr>';
          }).join('') + '</tbody></table></div></details>';
      });
    });
    out += sec(FT.t('Coded legal features', 'Fitur hukum yang dikodekan'),
      (cbody ? table(A, B, FT.t('Feature', 'Fitur'), cbody) + '<p class="ft-note">' + FT.t('Each database uses its own codebook, so values are compared only within the same database. Green = strong, yellow = partial, red = none, as defined in that codebook.', 'Setiap basis data memakai buku kodenya sendiri, sehingga nilai hanya dibandingkan di dalam basis data yang sama. Hijau = kuat, kuning = sebagian, merah = tidak ada, sesuai definisi buku kode tersebut.') + '</p>'
        : (solo ? '<p class="ft-note">' + FT.t('No feature is coded for both countries on this topic. What each one has:', 'Tidak ada fitur yang dikodekan untuk kedua negara pada topik ini. Yang dimiliki masing-masing:') + '</p>' : empty())) + solo);

    // 3. Treaties
    var ins = {};
    [A, B].forEach(function (C, i) { C.treaties.forEach(function (t) { (ins[t.i] = ins[t.i] || [null, null])[i] = t; }); });
    var tk = Object.keys(ins).filter(function (k) { return hit((META.treaties[k] || k) + ' ' + k); }).sort();
    var tbody = tk.map(function (k) {
      return '<tr><th scope="row">' + FT.esc(META.treaties[k] || k) + '</th>' + ins[k].map(function (t) {
        return t ? cell(pill(2, FT.status(t.st) || FT.t('party', 'pihak')) + ' <span class="ft-small">' + FT.esc(FT.fmtDate(String(t.d || ''))) + '</span>')
          : cell('<span class="ft-small">' + FT.t('No record of ratification', 'Tidak ada catatan ratifikasi') + '</span>');
      }).join('') + '</tr>';
    }).join('');
    out += sec(FT.t('Treaties (ILO and UN)', 'Perjanjian internasional (ILO dan PBB)'), tbody ? table(A, B, FT.t('Treaty', 'Perjanjian'), tbody) +
      '<p class="ft-note">' + FT.t('Treaty records come from NORMLEX and the UN Treaty Collection as copied into the databases. “No record” is not proof that a state is not a party: check the official status page.', 'Catatan perjanjian berasal dari NORMLEX dan UN Treaty Collection sebagaimana disalin ke basis data. “Tidak ada catatan” bukan bukti bahwa negara tersebut bukan pihak; periksalah halaman status resminya.') + '</p>' : empty());

    // 4. Laws
    function laws(C) {
      var l = C.laws.filter(function (x) { return hit(x.t + ' ' + (x.tp || '') + ' ' + (x.ty || '')) || (tp[0] === 'dw' && x.ds === 'domestic-workers'); });
      if (!l.length) return '';
      return '<ul style="margin:0;padding-left:18px">' + l.map(function (x) {
        var t = x.u ? '<a href="' + FT.esc(x.u) + '" rel="noopener">' + FT.esc(x.t) + '</a>' : FT.esc(x.t);
        return '<li style="margin-bottom:10px">' + t + (x.y ? ' <span class="ft-small">(' + x.y + (x.am ? '; ' + FT.t('amended ', 'diubah ') + FT.esc(x.am) : '') + ')</span>' : '') +
          (x.s2 ? '<div class="ft-small" lang="id">' + FT.esc(x.s1 + ' ' + x.s2) + (x.chk === 'yes' ? ' <span class="ft-pill part">' + FT.t('summary to be checked', 'ringkasan perlu dicek') + '</span>' : '') + '</div>' : '') +
          ' ' + FT.report(x.k) + '</li>';
      }).join('') + '</ul>';
    }
    out += sec(FT.t('National laws and instruments', 'Undang-undang dan instrumen nasional'),
      table(A, B, '', '<tr><th scope="row">' + FT.t('Listed in the databases', 'Tercatat di basis data') + '</th>' + cell(laws(A)) + cell(laws(B)) + '</tr>') +
      '<p class="ft-note">' + FT.t('The short Indonesian lines are plain summaries, not legal advice. ', 'Kalimat pendek berbahasa Indonesia adalah ringkasan sederhana, bukan nasihat hukum. ') + '<a href="/laws/">' + FT.t('All laws in plain words', 'Semua hukum dalam bahasa sederhana') + '</a></p>');

    // 5. Agreements
    function agr(C) {
      var l = C.agreements.filter(function (x) { return hit(x.t + ' ' + x.sc + ' ' + x.p); });
      if (!l.length) return '';
      return '<ul style="margin:0;padding-left:18px">' + l.map(function (x) {
        return '<li style="margin-bottom:8px">' + FT.esc(x.t) + ' <span class="ft-small">(' + FT.esc([x.p, x.lv, x.sg || x['if']].filter(Boolean).join(' · ')) + ')</span></li>';
      }).join('') + '</ul>';
    }
    out += sec(FT.t('Bilateral and regional agreements', 'Perjanjian bilateral dan kawasan'),
      table(A, B, '', '<tr><th scope="row">' + FT.t('Agreements recorded', 'Perjanjian yang tercatat') + '</th>' + cell(agr(A)) + cell(agr(B)) + '</tr>'));

    // 6. Court decisions by situation
    var sitKeys = Object.keys(META.situations).filter(function (k) {
      var s = SIT_TOPIC[tp[0]]; return !tp[0] || s === null || (s && s.indexOf(k) >= 0);
    });
    var sa = {}, sb = {};
    A.sit.forEach(function (x) { sa[x[0]] = x[1]; }); B.sit.forEach(function (x) { sb[x[0]] = x[1]; });
    var dbody = sitKeys.filter(function (k) { return sa[k] || sb[k]; }).map(function (k) {
      return '<tr><th scope="row">' + FT.esc(FT.t(META.situations[k][0], META.situations[k][1])) + '</th><td class="n">' + (sa[k] || 0) + '</td><td class="n">' + (sb[k] || 0) + '</td></tr>';
    }).join('');
    dbody += '<tr><th scope="row">' + FT.t('All decisions', 'Semua putusan') + '</th><td class="n">' + A.L.decisions + '</td><td class="n">' + B.L.decisions + '</td></tr>';
    out += sec(FT.t('Court decisions, by situation', 'Putusan pengadilan, menurut situasi'), table(A, B, FT.t('Situation', 'Situasi'), dbody) +
      '<p class="ft-note">' + FT.t('Counts include decisions not yet checked by an editor. Read them on ', 'Jumlah ini termasuk putusan yang belum diperiksa editor. Bacalah di halaman ') +
      '<a href="/court-decisions/">' + FT.t('Court Decisions', 'Putusan Pengadilan') + '</a>. ' + FT.t('See how each country’s law changed on the ', 'Lihat bagaimana hukum tiap negara berubah di ') +
      '<a href="/timeline/?c=' + A.c + '">' + FT.t('timeline', 'lini masa') + '</a>.</p>');
    $('cmp-out').innerHTML = out;
  }
  function sec(h, body) { return '<section class="ft-sec"><h2>' + FT.esc(h) + '</h2>' + body + '</section>'; }
  function empty() { return '<p class="ft-empty">' + FT.t('Nothing recorded for this topic in either country yet.', 'Belum ada catatan untuk topik ini di kedua negara.') + '</p>'; }

  FT.index().then(function (d) {
    META = d.meta; LIST = d.countries;
    fillSelects(); render();
    ['cmp-a', 'cmp-b', 'cmp-topic'].forEach(function (id) { $(id).addEventListener('change', render); });
    FT.onLang(function () { fillSelects(); render(); });
  });
})();
