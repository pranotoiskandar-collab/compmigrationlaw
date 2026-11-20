/* /coverage/: how many of seven kinds of data IMR holds per country (site/features/index.json). Measures our data, not the country. */
(function () {
  var FT = window.FT, $ = function (id) { return document.getElementById(id); };
  var META, BY = {}, LIST, SEL = null;

  function paint() {
    document.querySelectorAll('.ft-map [data-c]').forEach(function (el) {
      var c = BY[el.getAttribute('data-c')], k = c ? c.k : 0;
      el.setAttribute('class', 'k' + k + (SEL === el.getAttribute('data-c') ? ' sel' : ''));
      var t = el.querySelector('title');
      if (t) t.textContent = (c ? FT.name(c) : t.textContent.split(':')[0]) + ': ' + k + '/7';
    });
  }
  function panel(code) {
    SEL = code; paint();
    var c = BY[code], name = c ? FT.name(c) : (document.querySelector('.ft-map [data-c="' + code + '"] title') || {}).textContent;
    if (!c) {
      $('cov-panel').innerHTML = '<h3>' + FT.esc(String(name).split(':')[0]) + '</h3><p>' + FT.t('We hold no data for this country yet. Help would be welcome.', 'Kami belum memiliki data apa pun untuk negara ini. Bantuan sangat kami harapkan.') + '</p>';
      return;
    }
    var li = META.layers.map(function (l) {
      var n = c.L[l[0]] || 0, ck = c.ck[l[0]];
      return '<li class="' + (n ? '' : 'miss') + '">' + FT.esc(FT.t(l[1], l[2])) + ': <b>' + (n || FT.t('none yet', 'belum ada')) + '</b>' +
        (n && ck != null ? ' <span class="ft-small">(' + ck + ' ' + FT.t('checked by an editor', 'sudah diperiksa editor') + ')</span>' : '') + '</li>';
    }).join('');
    var ds = c.ds.filter(function (d) { return META.datasets[d]; }).map(function (d) { return FT.dsLink(META, d); }).join(' · ');
    $('cov-panel').innerHTML = '<h3>' + FT.esc(name) + ' · ' + c.k + '/7</h3><ul>' + li + '</ul>' +
      (ds ? '<p class="ft-small">' + FT.t('Appears in: ', 'Muncul di: ') + ds + '</p>' : '') +
      '<p><a class="ft-btn ghost" href="/compare/?a=' + c.c + '">' + FT.t('Compare', 'Bandingkan') + '</a> <a class="ft-btn ghost" href="/timeline/?c=' + c.c + '">' + FT.t('Timeline', 'Lini masa') + '</a> ' +
      '<a class="ft-btn ghost" href="/follow/?c=' + c.c + '">' + FT.t('Follow', 'Ikuti') + '</a> ' + FT.report(c.c + ' (coverage)') + '</p>';
  }
  function table() {
    var q = ($('cov-q').value || '').toLowerCase(), gaps = $('cov-gaps').checked;
    var rows = FT.sortByName(LIST).filter(function (c) {
      return (!q || (c.en + ' ' + c.id + ' ' + c.c).toLowerCase().indexOf(q) >= 0) && (!gaps || c.k < 7);
    });
    var th = '<thead><tr><th scope="col">' + FT.t('Country', 'Negara') + '</th>' + META.layers.map(function (l) {
      return '<th scope="col" class="n">' + FT.esc(FT.t(l[1], l[2])) + '</th>';
    }).join('') + '<th scope="col" class="n">' + FT.t('Kinds held', 'Jenis data') + '</th></tr></thead>';
    $('cov-t').innerHTML = th + '<tbody>' + rows.map(function (c) {
      return '<tr><th scope="row"><a href="#" data-pick="' + c.c + '">' + FT.esc(FT.name(c)) + '</a></th>' + META.layers.map(function (l) {
        return '<td class="n">' + (c.L[l[0]] || '<span class="ft-small">–</span>') + '</td>';
      }).join('') + '<td class="n">' + c.k + '/7</td></tr>';
    }).join('') + '</tbody>';
  }
  FT.index().then(function (d) {
    META = d.meta; LIST = d.countries; LIST.forEach(function (c) { BY[c.c] = c; });
    paint(); table();
    document.querySelector('.ft-map').addEventListener('click', function (e) {
      var el = e.target.closest('[data-c]'); if (el) panel(el.getAttribute('data-c'));
    });
    $('cov-t').addEventListener('click', function (e) {
      var a = e.target.closest('[data-pick]'); if (!a) return;
      e.preventDefault(); panel(a.getAttribute('data-pick')); $('cov-panel').scrollIntoView({behavior: 'smooth', block: 'center'});
    });
    $('cov-q').addEventListener('input', table); $('cov-gaps').addEventListener('change', table);
    if (FT.param('c')) panel(FT.param('c'));
    FT.onLang(function () { paint(); table(); if (SEL) panel(SEL); });
  });
})();
