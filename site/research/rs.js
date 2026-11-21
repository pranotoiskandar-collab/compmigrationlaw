/* /research/: the reading list and saved searches kept by /assets/research.js, with export and import. */
(function () {
  var R = window.IMRResearch, F = window.IMRF, esc = F.esc;
  var T = {
    en: {noitems: 'Your reading list is empty. Open any court decision and press "Add to reading list".', nosearch: 'No saved searches yet. On a database page, set the filters you want and press "Save this search".',
      remove: 'Remove', note: 'Your note', open: 'Open', added: 'added', saved: 'saved', rename: 'Rename', storage: 'This browser does not allow the site to store anything (private mode or blocked site data), so lists cannot be kept here.',
      imported: function (n) { return n + ' entries added.'; }, shareok: 'Link copied. Anyone who opens it can add your list to theirs.', incoming: function (n) { return 'This link carries a reading list with ' + n + ' entries.'; },
      addThem: 'Add them to my list', badfile: 'That file is not an IMR reading list.', cleared: 'Lists cleared.', confirmClear: 'Press again to clear both lists from this browser.',
      count: function (a, b) { return a + ' in the reading list, ' + b + ' saved searches'; }},
    id: {noitems: 'Daftar bacaan anda masih kosong. Buka putusan pengadilan mana pun lalu tekan "Tambahkan ke daftar bacaan".', nosearch: 'Belum ada pencarian tersimpan. Di halaman basis data, atur filter yang anda inginkan lalu tekan "Simpan pencarian ini".',
      remove: 'Hapus', note: 'Catatan anda', open: 'Buka', added: 'ditambahkan', saved: 'disimpan', rename: 'Ganti nama', storage: 'Peramban ini tidak mengizinkan situs menyimpan apa pun (mode pribadi atau data situs diblokir), sehingga daftar tidak bisa disimpan di sini.',
      imported: function (n) { return n + ' entri ditambahkan.'; }, shareok: 'Tautan disalin. Siapa pun yang membukanya bisa menambahkan daftar anda ke daftarnya.', incoming: function (n) { return 'Tautan ini membawa daftar bacaan berisi ' + n + ' entri.'; },
      addThem: 'Tambahkan ke daftar saya', badfile: 'Berkas itu bukan daftar bacaan IMR.', cleared: 'Daftar dikosongkan.', confirmClear: 'Tekan sekali lagi untuk mengosongkan kedua daftar dari peramban ini.',
      count: function (a, b) { return a + ' di daftar bacaan, ' + b + ' pencarian tersimpan'; }}
  };
  function t() { return T[F.lang()]; }
  var pending = null, clearArmed = false;

  function draw() {
    var d = R.data(), l = t();
    if (!R.available()) { document.getElementById('rs-items').innerHTML = '<p class="ft-warn">' + l.storage + '</p>'; return; }
    document.getElementById('rs-count').textContent = l.count(d.items.length, d.searches.length);
    document.getElementById('rs-items').innerHTML = d.items.length ? '<ol class="rs-list">' + d.items.map(function (i) {
      return '<li><a href="' + esc(i.url) + '"><b>' + esc(i.title) + '</b></a><br><span class="ft-note" style="margin:0">' +
        esc([i.court, i.country, i.date, i.citation].filter(Boolean).join(' · ')) + ' · ' + l.added + ' ' + esc(F.date(i.added)) + '</span>' +
        '<label class="rs-note"><span>' + l.note + '</span><textarea rows="2" data-key="' + esc(i.key) + '">' + esc(i.note || '') + '</textarea></label>' +
        '<button type="button" class="ft-save" data-rm="' + esc(i.key) + '">' + l.remove + '</button></li>';
    }).join('') + '</ol>' : '<p class="ft-note">' + l.noitems + '</p>';
    document.getElementById('rs-searches').innerHTML = d.searches.length ? '<ol class="rs-list">' + d.searches.map(function (s) {
      return '<li><a href="' + esc(s.url) + '"><b>' + esc(s.title) + '</b></a><br><span class="ft-note" style="margin:0">' + esc(s.url) + ' · ' + l.saved + ' ' + esc(F.date(s.saved)) + '</span><br>' +
        '<button type="button" class="ft-save" data-ren="' + esc(s.id) + '">' + l.rename + '</button> <button type="button" class="ft-save" data-rms="' + esc(s.id) + '">' + l.remove + '</button></li>';
    }).join('') + '</ol>' : '<p class="ft-note">' + l.nosearch + '</p>';
    if (pending) {
      document.getElementById('rs-incoming').hidden = false;
      document.getElementById('rs-incoming-text').textContent = l.incoming((pending.items || []).length + (pending.searches || []).length);
    }
  }

  // ---- export formats
  function year(i) { var m = (i.date || '').match(/\d{4}/); return m ? m[0] : ''; }
  function bibKey(i) { return (i.id || i.key || 'imr').replace(/[^A-Za-z0-9]/g, '') ; }
  function bibEsc(s) { return String(s || '').replace(/([{}%&$#_])/g, '\\$1'); }
  function bibtex(d) {
    var today = new Date().toISOString().slice(0, 10);
    return d.items.map(function (i) {
      return '@misc{' + bibKey(i) + ',\n  title = {{' + bibEsc(i.title) + '}},\n' + (i.court ? '  howpublished = {' + bibEsc(i.court) + (i.citation ? ', ' + bibEsc(i.citation) : '') + '},\n' : '') +
        (year(i) ? '  year = {' + year(i) + '},\n' : '') + (i.date ? '  date = {' + bibEsc(i.date) + '},\n' : '') +
        '  note = {Institute for Migrant Rights, Court Decisions database' + (i.note ? '. ' + bibEsc(i.note) : '') + '},\n  url = {' + i.url + '},\n  urldate = {' + today + '}\n}\n';
    }).join('\n');
  }
  function ris(d) {
    var today = new Date().toISOString().slice(0, 10).replace(/-/g, '/');
    return d.items.map(function (i) {
      var lines = ['TY  - ' + (i.type === 'decision' ? 'CASE' : 'ELEC'), 'TI  - ' + i.title];
      if (i.court) lines.push('PB  - ' + i.court);
      if (i.date) lines.push('DA  - ' + i.date.replace(/-/g, '/'));
      if (year(i)) lines.push('PY  - ' + year(i));
      if (i.citation) lines.push('M1  - ' + i.citation);
      if (i.country) lines.push('CY  - ' + i.country);
      lines.push('UR  - ' + i.url, 'Y2  - ' + today, 'DB  - Institute for Migrant Rights, Court Decisions');
      if (i.note) lines.push('N1  - ' + i.note);
      lines.push('ER  - ');
      return lines.join('\r\n');
    }).join('\r\n\r\n') + '\r\n';
  }
  function csvq(s) { s = String(s == null ? '' : s); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }
  function csv(d) {
    var head = ['kind', 'title', 'court', 'country', 'date', 'citation', 'url', 'note', 'added'];
    var rows = d.items.map(function (i) { return ['reading list', i.title, i.court, i.country, i.date, i.citation, i.url, i.note, i.added]; })
      .concat(d.searches.map(function (s) { return ['saved search', s.title, '', '', '', '', 'https://theimr.org' + s.url, '', s.saved]; }));
    return '﻿' + [head].concat(rows).map(function (r) { return r.map(csvq).join(','); }).join('\r\n') + '\r\n';
  }
  function download(name, text, type) {
    var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], {type: type}));
    a.download = name; document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }
  function b64e(s) { return btoa(unescape(encodeURIComponent(s))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); }
  function b64d(s) { s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '='; return decodeURIComponent(escape(atob(s))); }
  function valid(d) { return d && (Array.isArray(d.items) || Array.isArray(d.searches)); }
  function slim(d) { return {v: 1, items: d.items.map(function (i) { var o = {}; ['key', 'type', 'id', 'title', 'court', 'country', 'date', 'citation', 'url', 'note', 'added'].forEach(function (k) { if (i[k]) o[k] = i[k]; }); return o; }), searches: d.searches}; }

  document.addEventListener('click', function (e) {
    var b = e.target.closest('button,[data-x]'); if (!b) return;
    var d = R.data(), stamp = new Date().toISOString().slice(0, 10);
    if (b.dataset.rm) { R.removeItem(b.dataset.rm); draw(); }
    else if (b.dataset.rms) { R.removeSearch(b.dataset.rms); draw(); }
    else if (b.dataset.ren) { var s = d.searches.filter(function (x) { return x.id === b.dataset.ren; })[0]; var n = s && prompt(t().rename, s.title); if (n) { R.renameSearch(s.id, n); draw(); } }
    else if (b.id === 'rs-bib') download('imr-reading-list-' + stamp + '.bib', bibtex(d), 'application/x-bibtex');
    else if (b.id === 'rs-ris') download('imr-reading-list-' + stamp + '.ris', ris(d), 'application/x-research-info-systems');
    else if (b.id === 'rs-csv') download('imr-reading-list-' + stamp + '.csv', csv(d), 'text/csv');
    else if (b.id === 'rs-json') download('imr-reading-list-' + stamp + '.json', JSON.stringify(slim(d), null, 1), 'application/json');
    else if (b.id === 'rs-share') {
      var url = location.origin + '/research/#import=' + b64e(JSON.stringify(slim(d)));
      (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(function () { F.toast(t().shareok); }, function () { prompt('', url); });
    }
    else if (b.id === 'rs-add-in') { R.merge(pending); F.toast(t().imported((pending.items || []).length + (pending.searches || []).length)); pending = null; document.getElementById('rs-incoming').hidden = true; history.replaceState(null, '', '/research/'); draw(); }
    else if (b.id === 'rs-clear') { if (!clearArmed) { clearArmed = true; F.toast(t().confirmClear); setTimeout(function () { clearArmed = false; }, 4000); } else { R.replace({}); clearArmed = false; F.toast(t().cleared); draw(); } }
  });
  document.addEventListener('change', function (e) {
    if (e.target.matches('textarea[data-key]')) R.setNote(e.target.dataset.key, e.target.value);
    if (e.target.id === 'rs-file' && e.target.files[0]) {
      e.target.files[0].text().then(function (txt) { var d = JSON.parse(txt); if (!valid(d)) throw 0; R.merge(d); F.toast(t().imported((d.items || []).length + (d.searches || []).length)); draw(); })
        .catch(function () { F.toast(t().badfile); });
      e.target.value = '';
    }
  });
  var m = location.hash.match(/^#import=(.+)$/);
  if (m) { try { var d = JSON.parse(b64d(m[1])); if (valid(d)) pending = d; } catch (err) {} }
  F.onLang(draw);
  draw();
})();
