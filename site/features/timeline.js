/* /timeline/: how one country's law changed, from /features/c/<ISO2>.json (tools/features/build_data.py). */
(function () {
  var FT = window.FT, $ = function (id) { return document.getElementById(id); };
  var META, LIST, KIND = {
    law: ['Law', 'Undang-undang'], change: ['Reform', 'Reformasi'], treaty: ['Treaty', 'Perjanjian internasional'],
    agreement: ['Agreement', 'Perjanjian bilateral'], court: ['Court decision', 'Putusan pengadilan']
  };

  function iso(d) {
    d = String(d || '');
    var m = /^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?/.exec(d);
    if (m) return m[1] + '-' + (m[2] || '00') + '-' + (m[3] || '00');
    m = /(\d{1,2}) (\w{3})\w* (\d{4})/.exec(d);
    var mon = {Jan: '01', Feb: '02', Mar: '03', Apr: '04', May: '05', Jun: '06', Jul: '07', Aug: '08', Sep: '09', Oct: '10', Nov: '11', Dec: '12'};
    if (m && mon[m[2]]) return m[3] + '-' + mon[m[2]] + '-' + ('0' + m[1]).slice(-2);
    m = /(1[89]\d\d|20\d\d)/.exec(d);
    return m ? m[1] + '-00-00' : '';
  }
  function show(s) {
    var p = s.split('-');
    if (p[1] === '00') return p[0];
    return FT.fmtDate(p[0] + '-' + p[1] + (p[2] !== '00' ? '-' + p[2] : ''));
  }

  function events(C) {
    var ev = [];
    C.laws.forEach(function (l) {
      if (l.y) ev.push({k: 'law', d: iso(String(l.y)), h: (l.u ? '<a href="' + FT.esc(l.u) + '" rel="noopener">' + FT.esc(l.t) + '</a>' : FT.esc(l.t)) + ' ' + FT.t('adopted', 'disahkan'),
        x: l.s2 ? '<span lang="id">' + FT.esc(l.s1 + ' ' + l.s2) + '</span>' : FT.esc(l.tp || ''), r: l.k});
      String(l.am || '').replace(/(1[89]\d\d|20\d\d)/g, function (y) {
        ev.push({k: 'law', d: iso(y), h: FT.esc(l.t) + ' ' + FT.t('amended', 'diubah'), x: FT.esc(l.am), r: l.k});
      });
    });
    C.changes.forEach(function (c) { ev.push({k: 'change', d: iso(c.d), h: FT.esc(FT.L === 'id' && c.id ? c.id : c.en), x: FT.dsLink(META, c.ds)}); });
    C.treaties.forEach(function (t) {
      var d = iso(t.d); if (!d) return;
      ev.push({k: 'treaty', d: d, h: FT.esc(META.treaties[t.i] || t.i) + ': ' + FT.esc(FT.status(t.st || '')), x: ''});
    });
    C.agreements.forEach(function (a) {
      var d = iso(a.sg || a['if']); if (!d) return;
      ev.push({k: 'agreement', d: d, h: FT.esc(a.t), x: FT.esc([a.p, a.lv].filter(Boolean).join(' · '))});
    });
    C.dec.forEach(function (d) {
      ev.push({k: 'court', d: iso(d.d), h: '<a href="/court-decisions/d/' + encodeURIComponent(d.id) + '/">' + FT.esc(d.n) + '</a>',
        x: FT.esc(d.ct) + (FT.L === 'id' ? (d.pi ? '<br>' + FT.esc(d.pi) : '') : (d.pe ? '<br>' + FT.esc(d.pe) : ''))});
    });
    C.decC.forEach(function (y) {
      ev.push({k: 'court', d: y[0] + '-00-00', h: y[1] + ' ' + (y[1] === 1 ? FT.t('other decision recorded, not yet checked by an editor', 'putusan lain tercatat, belum diperiksa editor') : FT.t('other decisions recorded, not yet checked by an editor', 'putusan lain tercatat, belum diperiksa editor')),
        x: '<a href="/court-decisions/">' + FT.t('Search them on Court Decisions', 'Cari di Putusan Pengadilan') + '</a>'});
    });
    return ev.filter(function (e) { return e.d; }).sort(function (a, b) { return a.d < b.d ? -1 : a.d > b.d ? 1 : 0; });
  }

  function fill() {
    var cur = $('tl-c').value || FT.param('c') || 'ID';
    $('tl-c').innerHTML = FT.sortByName(LIST.filter(function (c) { return c.L.laws || c.L.changes || c.L.decisions || c.L.treaties; }))
      .map(function (c) { return '<option value="' + c.c + '">' + FT.esc(FT.name(c)) + '</option>'; }).join('');
    $('tl-c').value = cur; if (!$('tl-c').value) $('tl-c').value = 'ID';
  }
  function render() {
    var c = $('tl-c').value; FT.setParams({c: c});
    var on = [].slice.call(document.querySelectorAll('.ft-kinds input:checked')).map(function (i) { return i.value; });
    FT.country(c).then(function (C) {
      var ev = events(C).filter(function (e) { return on.indexOf(e.k) >= 0; });
      if (!ev.length) { $('tl-out').innerHTML = '<p class="ft-empty">' + FT.t('No dated entries for this country yet.', 'Belum ada entri bertanggal untuk negara ini.') + '</p>'; return; }
      var html = '<p class="ft-note">' + ev.length + ' ' + FT.t('entries', 'entri') + ' · <a href="/compare/?a=' + c + '">' + FT.t('Compare with another country', 'Bandingkan dengan negara lain') + '</a></p><ol class="ft-tl">', dec = '';
      ev.forEach(function (e) {
        var d10 = e.d.slice(0, 3) + '0s';
        if (d10 !== dec) { dec = d10; html += '<li class="decade" aria-hidden="true"><b>' + d10 + '</b></li>'; }
        html += '<li class="' + e.k + '"><span class="d">' + show(e.d) + '</span><span class="k">' + FT.esc(FT.t(KIND[e.k][0], KIND[e.k][1])) + '</span><div>' + e.h + '</div>' +
          (e.x ? '<div class="ft-small">' + e.x + '</div>' : '') + (e.r ? FT.report(e.r) : '') + '</li>';
      });
      $('tl-out').innerHTML = html + '</ol>';
    });
  }
  FT.index().then(function (d) {
    META = d.meta; LIST = d.countries; fill(); render();
    $('tl-c').addEventListener('change', render);
    document.querySelectorAll('.ft-kinds input').forEach(function (i) { i.addEventListener('change', render); });
    FT.onLang(function () { fill(); render(); });
  });
})();
