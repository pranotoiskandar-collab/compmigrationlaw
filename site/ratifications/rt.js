/* Ratification tracker: draws the table, the counts and the change log from /ratifications/data/*.csv. */
(function () {
  var F = window.IMRF, esc = F.esc;
  var INS = ['C097', 'C143', 'C189', 'C190', 'ICRMW'];
  var LABEL = {C097: 'C97', C143: 'C143', C189: 'C189', C190: 'C190', ICRMW: 'ICRMW'};
  var NAME = {
    en: {C097: 'Migration for Employment', C143: 'Migrant Workers', C189: 'Domestic Workers', C190: 'Violence and Harassment', ICRMW: 'UN Migrant Workers Convention'},
    id: {C097: 'Migrasi untuk Pekerjaan', C143: 'Pekerja Migran', C189: 'Pekerja Rumah Tangga', C190: 'Kekerasan dan Pelecehan', ICRMW: 'Konvensi PBB tentang Pekerja Migran'}
  };
  var T = {
    en: {country: 'Country', total: 'Parties', inforce: 'in force', wait: 'not yet in force', signed: 'signed', den: 'denounced',
      parties: 'parties', none: 'No state matches.', shown: 'states shown', checked: 'Last checked against the official records: ',
      legend: 'Year shown is the year of ratification or signature. Green: binding. Light green: ratified, not yet in force (ILO twelve-month rule). Beige: signed only. Red: denounced. Blank: not a party.',
      nochanges: 'No changes found since the tracker started on 19 November 2026. The first weekly check runs on Monday.',
      blocked: 'Last attempt could not reach the source: ', loadfail: 'The table could not be loaded. Download the CSV below instead.',
      new: 'new', updated: 'updated', gone: 'no longer listed'},
    id: {country: 'Negara', total: 'Jumlah', inforce: 'berlaku', wait: 'belum berlaku', signed: 'ditandatangani', den: 'diakhiri',
      parties: 'negara pihak', none: 'Tidak ada negara yang cocok.', shown: 'negara ditampilkan', checked: 'Terakhir dicocokkan dengan catatan resmi: ',
      legend: 'Tahun yang tercantum adalah tahun ratifikasi atau penandatanganan. Hijau: mengikat. Hijau muda: diratifikasi, belum berlaku (aturan dua belas bulan ILO). Krem: baru ditandatangani. Merah: diakhiri. Kosong: bukan pihak.',
      nochanges: 'Belum ada perubahan sejak pelacak ini dimulai pada 19 November 2026. Pemeriksaan mingguan pertama berjalan hari Senin.',
      blocked: 'Upaya terakhir tidak bisa menjangkau sumber: ', loadfail: 'Tabel tidak bisa dimuat. Silakan unduh CSV di bawah.',
      new: 'baru', updated: 'diperbarui', gone: 'tidak lagi tercantum'}
  };
  var rows = [], changes = [], status = [], byCountry = {}, sortKey = 'country', sortDir = 1;
  var q = document.getElementById('rt-q'), f = document.getElementById('rt-f');

  function cell(r, l) {
    if (!r) return '<td></td>';
    var y = (r.date_ratified || r.date_signed || '').slice(0, 4), cls, tip;
    if (r.status === 'denounced') { cls = 'ft-den'; tip = T[l].den; }
    else if (r.status === 'signed') { cls = 'ft-sig'; tip = T[l].signed; }
    else if (r.binding_now === 'yes') { cls = 'ft-yes'; tip = T[l].inforce; }
    else { cls = 'ft-wait'; tip = T[l].wait; }
    var d = F.date(r.date_ratified || r.date_signed, l);
    return '<td><span class="ft-pill ' + cls + '" title="' + esc(tip + ' · ' + d) + '">' + esc(y) + '<span class="visually-hidden" style="position:absolute;left:-9999px"> ' + esc(tip) + '</span></span></td>';
  }
  function party(r) { return r && r.status === 'ratified'; }

  function draw() {
    var l = F.lang(), t = T[l], term = (q.value || '').trim().toLowerCase(), mode = f.value;
    var list = Object.keys(byCountry).map(function (k) { return byCountry[k]; });
    list = list.filter(function (c) {
      if (term && c.name.toLowerCase().indexOf(term) < 0 && c.iso2.toLowerCase() !== term) return false;
      if (mode === 'any') return c.n > 0;
      if (mode === 'none') return c.n === 0;
      if (mode === 'all') return true;
      return party(c.r[mode]);
    });
    list.sort(function (a, b) {
      var x, y;
      if (sortKey === 'country') { x = a.name; y = b.name; return sortDir * x.localeCompare(y); }
      if (sortKey === 'n') { x = a.n; y = b.n; }
      else { x = a.r[sortKey] ? (a.r[sortKey].date_ratified || a.r[sortKey].date_signed || '9') : '~'; y = b.r[sortKey] ? (b.r[sortKey].date_ratified || b.r[sortKey].date_signed || '9') : '~'; }
      return x < y ? -sortDir : x > y ? sortDir : a.name.localeCompare(b.name);
    });
    var head = '<thead><tr><th scope="col"><button class="sort" data-k="country">' + t.country + '</button></th>' +
      INS.map(function (i) { return '<th scope="col" title="' + esc(NAME[l][i]) + '"><button class="sort" data-k="' + i + '">' + LABEL[i] + '</button></th>'; }).join('') +
      '<th scope="col"><button class="sort" data-k="n">' + t.total + '</button></th></tr></thead>';
    var body = list.length ? list.map(function (c) {
      return '<tr><th scope="row" style="font-weight:500">' + esc(c.name) + '</th>' + INS.map(function (i) { return cell(c.r[i], l); }).join('') + '<td>' + c.n + '</td></tr>';
    }).join('') : '<tr><td colspan="7">' + t.none + '</td></tr>';
    document.getElementById('rt-table').innerHTML = head + '<tbody>' + body + '</tbody>';
    document.getElementById('rt-legend').textContent = list.length + ' ' + t.shown + '. ' + t.legend;
    var stats = INS.map(function (i) {
      var n = rows.filter(function (r) { return r.instrument === i && r.status === 'ratified'; }).length;
      return '<div class="ft-stat"><b>' + n + '</b><span>' + LABEL[i] + ' · ' + esc(NAME[l][i]) + ' (' + t.parties + ')</span></div>';
    });
    document.getElementById('rt-stats').innerHTML = stats.join('');
    var last = rows.reduce(function (m, r) { return r.last_checked > m ? r.last_checked : m; }, '');
    var probs = status.filter(function (s) { return s.result && s.result !== 'ok' && s.result.indexOf('not') === 0; });
    document.getElementById('rt-checked').textContent = t.checked + F.date(last, l) + '.' +
      (probs.length ? ' ' + t.blocked + probs.map(function (s) { return LABEL[s.instrument] + ' (' + F.date(s.last_attempt, l) + ')'; }).join(', ') + '.' : '');
    var ch = changes.slice().reverse().slice(0, 25);
    document.getElementById('rt-changes').innerHTML = ch.length ? '<ul style="margin:12px 0 0;padding-left:20px;font-size:16px">' + ch.map(function (c) {
      var kind = c.change === 'new' ? t.new : c.change === 'updated' ? t.updated : t.gone;
      return '<li>' + F.date(c.date_seen, l) + ': <b>' + esc(c.country) + '</b>, ' + LABEL[c.instrument] + ' (' + kind + (c.after ? ': ' + esc(c.after) : '') + ')</li>';
    }).join('') + '</ul>' : '<p class="ft-note">' + t.nochanges + '</p>';
    try { history.replaceState(null, '', location.pathname + (term || mode !== 'any' ? '?' + new URLSearchParams({q: term, show: mode}).toString().replace(/q=&/, '') : '')); } catch (e) {}
  }

  document.getElementById('rt-table').addEventListener('click', function (e) {
    var b = e.target.closest('button.sort'); if (!b) return;
    var k = b.dataset.k; if (sortKey === k) sortDir = -sortDir; else { sortKey = k; sortDir = k === 'country' ? 1 : (k === 'n' ? -1 : 1); }
    draw();
  });
  q.addEventListener('input', draw); f.addEventListener('change', draw);
  F.onLang(draw);

  var p = new URLSearchParams(location.search);
  if (p.get('q')) q.value = p.get('q');
  if (p.get('show')) f.value = p.get('show');

  var base = '/ratifications/data/';
  Promise.all([F.getCSV(base + 'ratifications.csv'), F.getCSV(base + 'changes.csv').catch(function () { return []; }),
    F.getCSV(base + 'sources-status.csv').catch(function () { return []; }),
    fetch('/ratifications/countries.json').then(function (r) { return r.json(); }).catch(function () { return {}; })])
    .then(function (res) {
      rows = res[0]; changes = res[1]; status = res[2];
      var names = res[3];
      Object.keys(names).forEach(function (iso) { byCountry[iso] = {iso2: iso, name: names[iso], r: {}, n: 0}; });
      rows.forEach(function (r) {
        var c = byCountry[r.iso2] || (byCountry[r.iso2] = {iso2: r.iso2, name: r.country, r: {}, n: 0});
        c.r[r.instrument] = r; if (r.status === 'ratified') c.n++;
      });
      draw();
    })
    .catch(function () { document.getElementById('rt-table').innerHTML = '<tbody><tr><td>' + T[F.lang()].loadfail + '</td></tr></tbody>'; });
})();
