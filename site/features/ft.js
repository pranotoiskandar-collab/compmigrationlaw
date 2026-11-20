/* Shared helpers for the compare, timeline, coverage, laws, follow and report pages.
   Language: follows the site EN/ID switch (assets/lang.js, localStorage "imr-lang"). Static text carries its Indonesian in
   data-id; dynamic text is written with FT.t(en, id). Our own content is marked data-noi18n so lang.js leaves it alone. */
(function () {
  var KEY = 'imr-lang', subs = [];
  function lang() {
    var q = new URLSearchParams(location.search).get('lang');
    if (q === 'id' || q === 'en') return q;
    try { return localStorage.getItem(KEY) === 'id' ? 'id' : 'en'; } catch (e) { return 'en'; }
  }
  var FT = window.FT = {
    L: lang(),
    t: function (en, id) { return FT.L === 'id' && id ? id : en; },
    esc: function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]; }); },
    onLang: function (f) { subs.push(f); },
    json: function (u) {
      FT._c = FT._c || {};
      if (!FT._c[u]) FT._c[u] = fetch(u).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
      return FT._c[u];
    },
    index: function () { return FT.json('/features/index.json'); },
    country: function (c) { return FT.json('/features/c/' + c + '.json'); },
    name: function (c) { return c ? FT.t(c.en, c.id) : ''; },
    sortByName: function (list) { return list.slice().sort(function (a, b) { return FT.name(a).localeCompare(FT.name(b), FT.L); }); },
    report: function (entry, label) {
      var u = '/report/?page=' + encodeURIComponent(location.pathname + location.search) + '&entry=' + encodeURIComponent(entry);
      return '<a class="ft-rep" href="' + u + '" rel="nofollow">' + FT.esc(label || FT.t('Report a problem', 'Laporkan masalah')) + '</a>';
    },
    status: function (st) {
      var m = {'ratified': 'diratifikasi', 'in force': 'berlaku', 'accession': 'aksesi', 'party': 'pihak', 'Party': 'pihak', 'signed': 'ditandatangani',
        'ratified, not yet in force': 'diratifikasi, belum berlaku', 'denounced': 'dicabut (denunsiasi)', 'applied (declared)': 'diterapkan (deklarasi)',
        'Party: accession': 'pihak: aksesi', 'Party: ratification': 'pihak: ratifikasi', 'yes': 'ya', 'in_force_pending': 'belum berlaku'};
      return FT.L === 'id' && m[st] ? m[st] : st;
    },
    param: function (k) { return new URLSearchParams(location.search).get(k); },
    setParams: function (o) {
      var p = new URLSearchParams(location.search);
      Object.keys(o).forEach(function (k) { if (o[k]) p.set(k, o[k]); else p.delete(k); });
      history.replaceState(null, '', location.pathname + (p.toString() ? '?' + p : '') + location.hash);
    },
    dsName: function (meta, ds) { var d = meta.datasets[ds]; return d ? FT.t(d[0], d[1]) : ds; },
    dsLink: function (meta, ds) { var d = meta.datasets[ds]; return d ? '<a href="' + d[2] + '">' + FT.esc(FT.t(d[0], d[1])) + '</a>' : FT.esc(ds); },
    fmtDate: function (d) {
      if (!d) return '';
      var m = /^(\d{4})-(\d{2})(?:-(\d{2}))?/.exec(d);
      if (!m) return d;
      var mon = FT.L === 'id' ? ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'] : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      return (m[3] ? +m[3] + ' ' : '') + mon[+m[2] - 1] + ' ' + m[1];
    }
  };
  function swap() {
    document.querySelectorAll('[data-id]').forEach(function (el) {
      if (el._en == null) el._en = el.innerHTML;
      el.innerHTML = FT.L === 'id' ? FT.esc(el.getAttribute('data-id')) : el._en;
    });
    var aria = {'Find a country': 'Cari negara', 'Coverage table': 'Tabel cakupan data'};
    document.querySelectorAll('.ft [aria-label]').forEach(function (el) {
      if (el._al == null) el._al = el.getAttribute('aria-label');
      el.setAttribute('aria-label', FT.L === 'id' && aria[el._al] ? aria[el._al] : el._al);
    });
  }
  function apply() {
    document.querySelectorAll('main.ft').forEach(function (m) { m.setAttribute('data-noi18n', ''); });
    swap();
    var h = document.querySelector('main.ft h1');
    if (h) document.title = h.textContent + ' · Institute for Migrant Rights';
    subs.forEach(function (f) { f(FT.L); });
  }
  // the site switch is built by lang.js; react after it has run
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.imr-lang [data-sl]');
    if (!b) return;
    var l = b.getAttribute('data-sl') === 'id' ? 'id' : 'en';
    if (l !== FT.L) { FT.L = l; setTimeout(apply, 0); }
  });
  FT.start = function (f) { if (f) subs.push(f); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', apply); else setTimeout(apply, 0);
})();
