/* IMR country widget for partner sites (iframe). Shows IMR data for one country with the
   "Data from IMR" badge, which is part of the widget and links back to theimr.org.
   Reads the same files as Ask IMR (/legal-clinic/ask/). No cookies, no tracking beyond a
   GoatCounter page count of the widget URL. Legal information, not legal advice. */
(function () {
  var P = new URLSearchParams(location.search);
  var C = (P.get('c') || 'MY').toUpperCase().replace(/[^A-Z]/g, '').slice(0, 2);
  var L = P.get('lang') === 'id' ? 'id' : 'en';
  var TOPIC = (P.get('topic') || '').replace(/[^a-z]/g, '');
  document.documentElement.lang = L;
  var T = {
    en: {title: 'Migrant worker law in', rules: 'What the law says', laws: 'Laws', decisions: 'Court decisions', help: 'Free legal help',
      more: 'More on theimr.org', ask: 'Ask IMR a question', note: 'Legal information, not legal advice. Check the official source.',
      checked: 'checked against the official text', notChecked: 'not yet checked against the official text', official: 'Official text', call: 'Call',
      won: 'Worker won', lost: 'Worker lost', counts: function (n) { return n[0] + ' coded rules · ' + n[1] + ' laws · ' + n[2] + ' court decisions'; },
      none: 'IMR has no records for this country yet.', err: 'The data could not be loaded.', lic: 'Data CC BY 4.0'},
    id: {title: 'Hukum pekerja migran di', rules: 'Apa kata aturannya', laws: 'Undang-undang', decisions: 'Putusan pengadilan', help: 'Bantuan hukum gratis',
      more: 'Selengkapnya di theimr.org', ask: 'Tanya IMR', note: 'Informasi hukum, bukan nasihat hukum. Periksa sumber resminya.',
      checked: 'sudah diperiksa pada teks resmi', notChecked: 'belum diperiksa pada teks resmi', official: 'Teks resmi', call: 'Telepon',
      won: 'Pekerja menang', lost: 'Pekerja kalah', counts: function (n) { return n[0] + ' aturan terkode · ' + n[1] + ' undang-undang · ' + n[2] + ' putusan pengadilan'; },
      none: 'IMR belum memiliki catatan untuk negara ini.', err: 'Data tidak dapat dimuat.', lic: 'Data CC BY 4.0'}
  }[L];
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]; }); }
  var root = document.getElementById('w');
  var BASE = '/legal-clinic/ask/';
  function pick(list, n, pref) {
    var l = list.slice();
    if (TOPIC) { var hit = l.filter(function (r) { return (r.t || []).indexOf(TOPIC) >= 0; }); if (hit.length) l = hit; }
    if (pref) l.sort(pref);
    return l.slice(0, n);
  }
  Promise.all([fetch(BASE + 'ask-index.json').then(function (r) { return r.json(); }), fetch(BASE + 'c/' + C + '.json').then(function (r) { if (!r.ok) throw r; return r.json(); })])
    .then(function (x) {
      var idx = x[0], d = x[1], co = idx.countries[C];
      var h = '<h1>' + esc(T.title) + ' ' + esc(co[L]) + '</h1><p class="n">' + esc(T.counts(co.n)) + '</p>';
      var rules = pick(d.rules, 3, function (a, b) { return (b.e === 'P') - (a.e === 'P'); });
      if (rules.length) h += '<h2>' + esc(T.rules) + '</h2>' + rules.map(function (r) {
        var f = L === 'id' && r.fi ? r.fi : r.f, v = L === 'id' && r.vi ? r.vi : r.v, g = L === 'id' && r.gi ? r.gi : r.g;
        return '<div class="i"><small>' + esc(g) + '</small><p><b>' + esc(f) + ':</b> ' + esc(v) + ' <i>(' + esc(r.e === 'P' ? T.checked : T.notChecked) + ')</i></p></div>';
      }).join('');
      var laws = pick(d.laws, 3);
      if (laws.length) h += '<h2>' + esc(T.laws) + '</h2>' + laws.map(function (r) {
        return '<div class="i"><p><b>' + esc(r.ti) + '</b>' + (r.y ? ' (' + esc(r.y) + ')' : '') + (r.u ? ' · <a href="' + esc(r.u) + '" target="_blank" rel="noopener">' + esc(T.official) + ' ↗</a>' : '') + '</p></div>';
      }).join('');
      var decs = pick(d.decisions, 3, function (a, b) { return ((b.oc === 'won' || b.oc === 'lost') - (a.oc === 'won' || a.oc === 'lost')) || ((b.d || '') > (a.d || '') ? 1 : -1); });
      if (decs.length) h += '<h2>' + esc(T.decisions) + '</h2>' + decs.map(function (r) {
        var txt = L === 'id' ? (r.pi || r.pe) : (r.pe || r.pi);
        return '<div class="i"><p><a href="https://theimr.org/court-decisions/d/' + esc(r.id) + '/" target="_blank" rel="noopener"><b>' + esc(r.nm) + '</b></a> (' + esc(r.d) + ')' +
          (T[r.oc] ? ' · ' + esc(T[r.oc]) : '') + '</p>' + (txt ? '<p class="s">' + esc(txt) + '</p>' : '') + '</div>';
      }).join('');
      var help = d.help.slice(0, 2);
      if (help.length) h += '<h2>' + esc(T.help) + '</h2>' + help.map(function (r) {
        return '<div class="i"><p><b>' + esc(r.nm) + '</b>' + (r.city ? ', ' + esc(r.city) : '') + '</p><p>' + (r.tel || []).slice(0, 1).map(function (t) { return '<a class="tel" href="tel:' + esc(t.replace(/[^+0-9]/g, '')) + '">' + esc(T.call) + ' ' + esc(t) + '</a>'; }).join('') +
          (r.web ? ' <a href="' + esc(r.web) + '" target="_blank" rel="noopener">' + esc(r.web.replace(/^https?:\/\/(www\.)?/, '').replace(/\/.*$/, '')) + ' ↗</a>' : '') + '</p></div>';
      }).join('');
      if (!rules.length && !laws.length && !decs.length) h += '<p>' + esc(T.none) + '</p>';
      h += '<p class="more"><a href="https://theimr.org/legal-clinic/?lang=' + L + '#ask-imr" target="_blank" rel="noopener">' + esc(T.ask) + ' →</a> <a href="https://theimr.org/databases/?lang=' + L + '" target="_blank" rel="noopener">' + esc(T.more) + ' →</a></p>';
      root.innerHTML = h;
    }).catch(function () { root.innerHTML = '<p>' + esc(T.err) + '</p>'; });
  document.getElementById('badge').innerHTML = '<a href="https://theimr.org/?ref=widget" target="_blank" rel="noopener"><img src="/partners/badge/' + (L === 'id' ? 'data-dari-imr' : 'data-from-imr') + '.svg" width="198" height="42" alt="' + (L === 'id' ? 'Data dari IMR, Institute for Migrant Rights' : 'Data from IMR, Institute for Migrant Rights') + '"></a><small>' + esc(T.note) + ' ' + esc(T.lic) + '</small>';
})();
