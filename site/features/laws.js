/* /laws/: every law with its two-line plain Indonesian summary (site/features/laws.json, data/plain-summaries/laws-id.csv). */
(function () {
  var FT = window.FT, $ = function (id) { return document.getElementById(id); };
  var D, GROUPS = {global: ['Global instruments', 'Instrumen global'], regional: ['Regional instruments', 'Instrumen kawasan'], all: ['International instruments on domestic work', 'Instrumen internasional tentang kerja rumah tangga'],
    national: ['National laws in the Migration Law Atlas', 'Hukum nasional di Atlas Hukum Migrasi'], P: ['Data sources and reports', 'Sumber data dan laporan'],
    'Organization of American States': ['Organization of American States', 'Organisasi Negara-Negara Amerika'], 'Council of Europe': ['Council of Europe', 'Dewan Eropa'],
    'African Union': ['African Union', 'Uni Afrika'], 'European Union': ['European Union', 'Uni Eropa'], 'League of Arab States': ['League of Arab States', 'Liga Arab'],
    'Inter-American Court of Human Rights': ['Inter-American Court of Human Rights', 'Pengadilan HAM Antar-Amerika']};

  function gname(c) {
    if (D.names[c]) return FT.t(D.names[c][0], D.names[c][1]);
    if (GROUPS[c]) return FT.t(GROUPS[c][0], GROUPS[c][1]);
    return c;
  }
  function fill() {
    var cur = $('lw-c').value || FT.param('c') || '';
    var cs = {};
    D.laws.forEach(function (l) { cs[l.c] = (cs[l.c] || 0) + 1; });
    var keys = Object.keys(cs).sort(function (a, b) {
      var ga = D.names[a] ? 1 : 0, gb = D.names[b] ? 1 : 0;
      return ga - gb || gname(a).localeCompare(gname(b), FT.L);
    });
    $('lw-c').innerHTML = '<option value="">' + FT.t('All', 'Semua') + ' (' + D.laws.length + ')</option>' +
      keys.map(function (k) { return '<option value="' + FT.esc(k) + '">' + FT.esc(gname(k)) + ' (' + cs[k] + ')</option>'; }).join('');
    $('lw-c').value = cur;
  }
  function render() {
    var c = $('lw-c').value, q = ($('lw-q').value || '').toLowerCase(), chk = $('lw-chk').checked;
    FT.setParams({c: c});
    var l = D.laws.filter(function (x) {
      return (!c || x.c === c) && (!chk || x.chk === 'yes') &&
        (!q || [x.t, x.o, x.tp, x.s1, x.s2, gname(x.c)].join(' ').toLowerCase().indexOf(q) >= 0);
    });
    var nchk = l.filter(function (x) { return x.chk === 'yes'; }).length;
    $('lw-count').textContent = l.length + ' ' + FT.t('entries', 'entri') + ' · ' + nchk + ' ' + FT.t('summaries still to be checked', 'ringkasan masih perlu dicek');
    $('lw-out').innerHTML = l.slice(0, 400).map(function (x) {
      var t = x.u ? '<a href="' + FT.esc(x.u) + '" rel="noopener">' + FT.esc(x.t) + '</a>' : FT.esc(x.t);
      return '<article class="ft-law"><h3>' + t + '</h3>' +
        (x.s2 ? '<p class="s" lang="id"><span>' + FT.esc(x.s1) + '</span><span>' + FT.esc(x.s2) + '</span></p>'
          : '<p class="s ft-small">' + FT.t('No plain summary yet.', 'Belum ada ringkasan sederhana.') + '</p>') +
        '<p class="m">' + FT.esc(gname(x.c)) + (x.y ? ' · ' + x.y : '') + ' · ' + FT.dsLink(D.meta, x.ds) +
        (x.chk === 'yes' ? ' · <span class="ft-pill part" title="' + FT.esc(x.why || '') + '">' + FT.t('Summary to be checked', 'Ringkasan perlu dicek') + '</span>' +
          (x.why ? ' <span class="ft-small">' + FT.esc(x.why) + '</span>' : '') : x.s2 ? ' · <span class="ft-pill">' + FT.t('Summary, not legal advice', 'Ringkasan, bukan nasihat hukum') + '</span>' : '') +
        ' · ' + FT.report(x.k) + '</p></article>';
    }).join('') + (l.length > 400 ? '<p class="ft-note">' + FT.t('Showing the first 400. Choose a country or search to see the rest.', 'Menampilkan 400 entri pertama. Pilih negara atau gunakan pencarian untuk melihat sisanya.') + '</p>' : '');
  }
  FT.json('/features/laws.json').then(function (d) {
    D = d; fill(); render();
    $('lw-c').addEventListener('change', render); $('lw-q').addEventListener('input', render); $('lw-chk').addEventListener('change', render);
    FT.onLang(function () { fill(); render(); });
  });
})();
