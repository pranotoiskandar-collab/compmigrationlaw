/* "Know your rights before you go": draws a one-country, one-job checklist from checklist-data.json.
   The sheet is in Indonesian by default (it is written for people leaving Indonesia); an English copy is
   available for families, NGOs and lawyers. Print styles in the page turn it into an A4 handout. */
(function () {
  var F = window.IMRF, esc = F.esc;
  var GULF = {SA: 1, AE: 1, QA: 1, KW: 1, OM: 1, BH: 1};
  var TREATY = {
    C189: ['Konvensi ILO tentang Pekerja Rumah Tangga (C189)', 'ILO Domestic Workers Convention (C189)'],
    C190: ['Konvensi ILO tentang Kekerasan dan Pelecehan di Dunia Kerja (C190)', 'ILO Violence and Harassment Convention (C190)'],
    C097: ['Konvensi ILO tentang Migrasi untuk Pekerjaan (C97)', 'ILO Migration for Employment Convention (C97)'],
    C143: ['Konvensi ILO tentang Pekerja Migran (C143)', 'ILO Migrant Workers Convention (C143)'],
    ICRMW: ['Konvensi PBB tentang Perlindungan Hak Pekerja Migran dan Keluarganya (ICRMW)', 'UN Migrant Workers Convention (ICRMW)']
  };
  var S = {
    id: {
      title: 'Kenali hak anda sebelum berangkat', info: 'Informasi hukum, bukan nasihat hukum',
      before: 'Sebelum berangkat (di Indonesia)', there: function (c) { return 'Di ' + c + ': apa kata hukumnya'; },
      legend: '✔ dilindungi   ◐ sebagian   ✖ tidak dilindungi   ? belum jelas',
      todo: 'Yang perlu anda lakukan: ', src: 'Dasar hukum: ', star: '*',
      treaties: 'Janji internasional negara ini', yes: 'sudah meratifikasi', wait: 'sudah meratifikasi, belum berlaku', signed: 'baru menandatangani', no: 'belum meratifikasi',
      idnote: 'Indonesia sudah meratifikasi Konvensi PBB tentang Pekerja Migran (ICRMW) pada 2012.',
      help: 'Jika ada masalah, hubungi', home: 'Di Indonesia', abroad: function (c) { return 'Di ' + c; },
      nohelp: 'Kami belum punya kontak yang sudah diperiksa untuk negara ini. Hubungi KBRI/KJRI atau Klinik Hukum IMR.',
      clinic: 'Klinik Hukum IMR (gratis): siapkan pengaduan hak di theimr.org/legal-clinic/',
      foot: function (d, n) { return 'Disusun dari basis data Institute for Migrant Rights (theimr.org), ' + n + '. Data dikodekan per ' + d + '. Hukum dapat berubah; periksa kembali sebelum berangkat. Tanda * berarti belum dicocokkan dengan teks resmi undang-undang. Lembar ini berisi informasi hukum umum, bukan nasihat hukum untuk kasus anda.'; },
      link: 'Lembar ini daring: ', more: 'Rincian (bahasa Inggris)', unclear: 'Belum jelas',
      gulf: 'Perhatian'
    },
    en: {
      title: 'Know your rights before you go', info: 'Legal information, not legal advice',
      before: 'Before you leave (in Indonesia)', there: function (c) { return 'In ' + c + ': what the law says'; },
      legend: '✔ protected   ◐ partly   ✖ not protected   ? unclear',
      todo: 'What to do: ', src: 'Legal basis: ', star: '*',
      treaties: "This country's international commitments", yes: 'has ratified', wait: 'has ratified, not yet in force', signed: 'has only signed', no: 'has not ratified',
      idnote: 'Indonesia ratified the UN Migrant Workers Convention (ICRMW) in 2012.',
      help: 'If something goes wrong, contact', home: 'In Indonesia', abroad: function (c) { return 'In ' + c; },
      nohelp: 'We do not yet have checked contacts for this country. Contact the Indonesian embassy or consulate, or the IMR Legal Clinic.',
      clinic: 'IMR Legal Clinic (free): prepare a rights communication at theimr.org/legal-clinic/',
      foot: function (d, n) { return 'Compiled from the Institute for Migrant Rights databases (theimr.org), ' + n + '. Data coded as of ' + d + '. Laws change; check again before you leave. * means not yet checked against the official text of the law. This sheet is general legal information, not legal advice on your case.'; },
      link: 'This sheet online: ', more: 'Details', unclear: 'Unclear',
      gulf: 'Warning'
    }
  };
  var DBNAME = {'domestic-workers': ['Pekerja Rumah Tangga Migran', 'Migrant Domestic Workers'], 'east-asia': ['Asia Timur', 'East Asia'], 'southeast-asia': ['Asia Tenggara', 'Southeast Asia']};
  var data, cur = {c: null, g: null, l: 'id'};
  var $c = document.getElementById('rc-countries'), $g = document.getElementById('rc-groups'), $s = document.getElementById('rc-sheet'), $tools = document.getElementById('rc-tools');

  function icon(v) { return v === '2' ? ['✔', 'rc-y'] : v === '1' ? ['◐', 'rc-p'] : v === '0' ? ['✖', 'rc-n'] : ['?', 'rc-u']; }
  function dmy(iso, l) { return F.date(iso, l); }

  function countryButtons() {
    var ui = F.lang();
    $c.innerHTML = data.countries.map(function (c) {
      return '<button type="button" class="ft-btn alt rc-pick" data-c="' + c.iso2 + '" aria-pressed="' + (cur.c === c.iso2) + '">' + esc(ui === 'id' ? c.id : c.en) + '</button>';
    }).join('');
  }
  function groupButtons() {
    var c = find(cur.c), ui = F.lang();
    if (!c) { $g.innerHTML = ''; document.getElementById('rc-step2').hidden = true; return; }
    document.getElementById('rc-step2').hidden = false;
    $g.innerHTML = c.groups.map(function (g) {
      return '<button type="button" class="ft-btn alt rc-pick" data-g="' + g.k + '" aria-pressed="' + (cur.g === g.k) + '">' + esc(ui === 'id' ? g.id : g.en) + '</button>';
    }).join('');
  }
  function find(iso) { for (var i = 0; data && i < data.countries.length; i++) if (data.countries[i].iso2 === iso) return data.countries[i]; return null; }

  function contact(p, l) {
    var tel = (p.tel || []).map(function (t) { return '<a href="tel:' + esc(t.replace(/[^+\d]/g, '')) + '">' + esc(t) + '</a>'; }).join(' · ');
    var desc = l === 'id' ? (p.d_id || '') : (p.d || '');
    return '<li><b>' + esc(p.n) + '</b>' + (p.city ? ' (' + esc(l === 'id' && p.city_id ? p.city_id : p.city) + ')' : '') +
      (tel ? '<br>☎ ' + tel : '') + (p.web ? '<br><span class="rc-url">' + esc(p.web.replace(/^https?:\/\//, '').replace(/\/$/, '')) + '</span>' : '') +
      (desc ? '<br><span class="rc-small">' + esc(desc) + '</span>' : '') + '</li>';
  }

  function sheet() {
    var c = find(cur.c), g = c && c.groups.filter(function (x) { return x.k === cur.g; })[0];
    if (!c || !g) { $s.innerHTML = ''; $tools.hidden = true; return; }
    var l = cur.l, t = S[l], li = l === 'id' ? 0 : 1, cname = l === 'id' ? c.id : c.en, gname = l === 'id' ? g.id : g.en;
    var coded = g.items.reduce(function (m, i) { return i.coded > m ? i.coded : m; }, '');
    var h = '<div class="rc-head"><p class="rc-k">' + esc(t.title) + '</p><h2 class="rc-h">' + esc(cname) + '</h2><p class="rc-job">' + esc(gname) + '</p>' +
      '<p class="rc-badge">' + esc(t.info) + '</p></div>';
    // before departure
    var before = data.before.filter(function (b) { return b.f !== 'exit' || (GULF[c.iso2] && g.k === 'PRT'); });
    h += '<h3 class="rc-sec">' + esc(t.before) + '</h3><ul class="rc-boxes">' + before.map(function (b) {
      var warn = b.f === 'exit';
      return '<li' + (warn ? ' class="rc-warn"' : '') + '><span class="rc-box" aria-hidden="true">' + (warn ? '!' : '') + '</span><span>' + (warn ? '<b>' + esc(t.gulf) + ':</b> ' : '') + esc(l === 'id' ? b.id : b.en) +
        (b.src ? ' <span class="rc-small">(' + esc(b.src) + (b.ev === 'S' ? t.star : '') + ')</span>' : '') + '</span></li>';
    }).join('') + '</ul>';
    // destination rules
    h += '<h3 class="rc-sec">' + esc(t.there(cname)) + '</h3><p class="rc-legend">' + esc(t.legend) + '</p><ol class="rc-rules">';
    g.items.forEach(function (i) {
      var ic = icon(i.v), a = i.v === '' ? t.unclear : (l === 'id' ? i.a_id : i.a_en);
      var checked = i.ev === 'P' && (!i.checked || /confirmed/.test(i.checked));
      h += '<li><span class="rc-ic ' + ic[1] + '" aria-hidden="true">' + ic[0] + '</span><div><b>' + esc(l === 'id' ? i.q_id : i.q_en) + '</b><br>' + esc(a) +
        '<br><span class="rc-do">' + esc(t.todo) + esc(l === 'id' ? i.do_id : i.do_en) + '</span>' +
        (i.src ? '<br><span class="rc-small">' + esc(t.src) + esc(i.src.split(' · official text:')[0]) + (checked ? '' : t.star) + '</span>' : '') +
        (i.note_en ? '<details class="rc-more"><summary>' + esc(t.more) + '</summary><span class="rc-small" lang="en">' + esc(i.note_en) + '</span></details>' : '') +
        '</div></li>';
    });
    h += '</ol>';
    // treaties
    h += '<h3 class="rc-sec">' + esc(t.treaties) + '</h3><ul class="rc-list">';
    ['C189', 'C190', 'C097', 'C143', 'ICRMW'].forEach(function (k) {
      var r = c.treaties[k], st;
      if (!r) st = t.no; else if (r.s === 'signed') st = t.signed; else if (r.f === 'no') st = t.wait; else st = t.yes;
      h += '<li>' + esc(cname) + ' <b>' + esc(st) + '</b> ' + esc(TREATY[k][li]) + (r && r.d ? ' (' + r.d.slice(0, 4) + ')' : '') + '</li>';
    });
    h += '<li>' + esc(t.idnote) + '</li></ul>';
    // help
    var home = (data.home_help || []).filter(function (p) { return p.t === 'gov' || /YLBHI|SBMI|Migrant CARE/i.test(p.n); }).slice(0, 4);
    h += '<h3 class="rc-sec">' + esc(t.help) + '</h3><div class="rc-cols"><div><p class="rc-sub">' + esc(t.abroad(cname)) + '</p>' +
      (c.help.length ? '<ul class="rc-list">' + c.help.map(function (p) { return contact(p, l); }).join('') + '</ul>' : '<p class="rc-small">' + esc(t.nohelp) + '</p>') +
      '</div><div><p class="rc-sub">' + esc(t.home) + '</p><ul class="rc-list">' + home.map(function (p) { return contact(p, l); }).join('') +
      '<li><b>' + esc(t.clinic) + '</b></li></ul></div></div>';
    var url = 'theimr.org/rights-checklist/?c=' + c.iso2 + '&g=' + g.k + (l === 'en' ? '&l=en' : '');
    h += '<p class="rc-foot">' + esc(t.foot(dmy(coded, l), (l === 'id' ? 'basis data ' : '') + DBNAME[g.db][li] + (l === 'en' ? ' database' : '') + ', ' + (l === 'id' ? 'pelacak ratifikasi, dan direktori bantuan hukum' : 'ratification tracker and legal help directory'))) +
      '<br>' + esc(t.link) + '<b>' + esc(url) + '</b></p>';
    $s.innerHTML = h;
    $s.setAttribute('lang', l);
    $tools.hidden = false;
    var pdf = document.getElementById('rc-pdf');
    pdf.href = '/rights-checklist/pdf/' + c.iso2.toLowerCase() + '-' + g.k.toLowerCase() + '-' + l + '.pdf';
    pdf.setAttribute('download', 'hak-sebelum-berangkat-' + c.iso2.toLowerCase() + '-' + g.k.toLowerCase() + '-' + l + '.pdf');
    var share = document.getElementById('rc-wa');
    share.href = 'https://wa.me/?text=' + encodeURIComponent((l === 'id' ? 'Kenali hak anda sebelum berangkat ke ' : 'Know your rights before you go to ') + cname + ': https://' + url);
    document.querySelectorAll('#rc-langs [data-l]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.l === l)); });
    try { history.replaceState(null, '', '?c=' + c.iso2 + '&g=' + g.k + (l === 'en' ? '&l=en' : '')); } catch (e) {}
    document.title = (l === 'id' ? 'Hak sebelum berangkat: ' : 'Rights before you go: ') + cname + ' · IMR';
  }

  function drawAll() { countryButtons(); groupButtons(); sheet(); }

  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-c],[data-g],[data-l]');
    if (!b || !b.closest('#rc-app')) return;
    if (b.dataset.c) { cur.c = b.dataset.c; var cc = find(cur.c); cur.g = cc.groups.length === 1 ? cc.groups[0].k : null; drawAll(); if (cur.g) document.getElementById('rc-sheet').scrollIntoView({behavior: 'smooth', block: 'start'}); else document.getElementById('rc-step2').scrollIntoView({behavior: 'smooth', block: 'nearest'}); }
    else if (b.dataset.g) { cur.g = b.dataset.g; drawAll(); document.getElementById('rc-sheet').scrollIntoView({behavior: 'smooth', block: 'start'}); }
    else if (b.dataset.l) { cur.l = b.dataset.l; sheet(); }
  });
  document.getElementById('rc-print').addEventListener('click', function () { window.print(); });
  F.onLang(function () { countryButtons(); groupButtons(); });

  var p = new URLSearchParams(location.search);
  cur.c = p.get('c'); cur.g = p.get('g'); cur.l = p.get('l') === 'en' ? 'en' : 'id';
  fetch('/rights-checklist/checklist-data.json').then(function (r) { return r.json(); }).then(function (d) {
    data = d;
    var c = find(cur.c);
    if (!c) cur.c = cur.g = null;
    else if (!c.groups.some(function (g) { return g.k === cur.g; })) cur.g = c.groups.length === 1 ? c.groups[0].k : null;
    drawAll();
    document.documentElement.setAttribute('data-rc-ready', '1');
  });
})();
