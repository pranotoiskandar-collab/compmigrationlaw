/* Trafficking self-check: the rule engine and the screens. Data in tc-data.js (window.TC).
   Nothing is stored or sent: answers live in this page's memory and vanish when it closes.
   Only anonymous counts go to GoatCounter (started, finished + result level, sheet printed/downloaded). */
(function () {
  'use strict';
  var TC = window.TC, $ = function (s, r) { return (r || document).querySelector(s); };
  var root = $('#tc-app');
  var A = {}, pos = 0;

  /* ---------- helpers ---------- */
  function lang() { return document.documentElement.lang === 'id' ? 'id' : 'en'; }
  function T(o) { if (!o) return ''; if (typeof o === 'string') return o; return '<span class="en">' + o.en + '</span><span class="id">' + o.id + '</span>'; }
  function L(en, id) { return T({ en: en, id: id }); }
  function count(p, t) { try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: 'event/trafficking-check/' + p, title: t || p, event: true }); } catch (e) {} }
  function has(list, k) { return (A[list] || []).indexOf(k) >= 0; }
  function uniq(a) { var s = {}, r = []; a.forEach(function (x) { if (x && !s[x]) { s[x] = 1; r.push(x); } }); return r; }

  /* ---------- icons (24px line drawings) ---------- */
  var P = {
    child: '<circle cx="12" cy="7" r="3"/><path d="M8 21v-6l-2-3 3-1h6l3 1-2 3v6"/>',
    adult: '<circle cx="12" cy="5" r="3"/><path d="M7 22v-8l-1-4h12l-1 4v8M12 14v8"/>',
    q: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .9-1 1.7M12 17h.01"/>',
    woman: '<circle cx="12" cy="6" r="3"/><path d="M12 9l-4 8h8l-4-8zM10 17v5M14 17v5"/>',
    man: '<circle cx="12" cy="5" r="3"/><path d="M8 10h8v6h-2v6h-4v-6H8z"/>',
    dash: '<circle cx="12" cy="12" r="9"/><path d="M8 12h8"/>',
    home: '<path d="M3 11l9-7 9 7M5 10v10h14V10"/><path d="M10 20v-5h4v5"/>',
    globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    plane: '<path d="M2 16l20-8-4 10-6-3-3 4v-5l9-6-11 5z"/>',
    house: '<path d="M4 21V10l8-6 8 6v11z"/><path d="M9 21v-6h6v6"/>',
    leaf: '<path d="M5 19c0-9 6-14 15-14 0 9-5 15-14 15"/><path d="M5 19l8-8"/>',
    boat: '<path d="M3 15h18l-3 5H6zM12 3v12M12 4l6 8h-6"/>',
    factory: '<path d="M3 21V11l6 3V11l6 3V6h4v15z"/>',
    music: '<path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>',
    phone: '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M11 18h2"/>',
    dots: '<circle cx="6" cy="12" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="18" cy="12" r="1.5"/>',
    hand: '<path d="M7 11V5a1.5 1.5 0 0 1 3 0v5M10 10V4a1.5 1.5 0 0 1 3 0v6M13 10V5a1.5 1.5 0 0 1 3 0v7M16 12v-2a1.5 1.5 0 0 1 3 0v4a8 8 0 0 1-8 8 6 6 0 0 1-5-3l-3-5a1.5 1.5 0 0 1 2.5-1.5L7 14"/>',
    bus: '<rect x="4" y="3" width="16" height="15" rx="2"/><path d="M4 11h16M7 21v-3M17 21v-3"/>',
    swap: '<path d="M4 8h14l-3-3M20 16H6l3 3"/>',
    fist: '<path d="M6 11V8a2 2 0 0 1 4 0v-1a2 2 0 0 1 4 0v1a2 2 0 0 1 4 0v6a6 6 0 0 1-6 6H10a4 4 0 0 1-4-4z"/>',
    warn: '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',
    badge: '<path d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6z"/>',
    lock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    nophone: '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M3 3l18 18"/>',
    grab: '<path d="M4 14l6-6 4 4 6-6M14 6h6v6"/>',
    passport: '<rect x="5" y="2" width="14" height="20" rx="2"/><circle cx="12" cy="10" r="3"/><path d="M9 17h6"/>',
    coin: '<circle cx="12" cy="12" r="9"/><path d="M15 9h-4a2 2 0 0 0 0 4h2a2 2 0 0 1 0 4H9M12 6v2M12 16v2"/>',
    chain: '<path d="M10 14a4 4 0 0 1 0-5.6l2.8-2.8a4 4 0 0 1 5.6 5.6L17 12.6M14 10a4 4 0 0 1 0 5.6l-2.8 2.8a4 4 0 0 1-5.6-5.6L7 11.4"/>',
    doc: '<path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6M9 13h8M9 17h6"/>',
    cash: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/>',
    mask: '<path d="M3 8c3-2 15-2 18 0 0 6-3 10-9 10S3 14 3 8z"/><circle cx="8.5" cy="11" r="1.5"/><circle cx="15.5" cy="11" r="1.5"/>',
    hole: '<ellipse cx="12" cy="16" rx="9" ry="4"/><path d="M12 3v8M9 8l3 3 3-3"/>',
    crown: '<path d="M3 18h18L19 8l-4 4-3-6-3 6-4-4z"/>',
    door: '<path d="M5 21V3h11v18M16 21h3M12 12h.01"/>',
    tool: '<path d="M14 6a4 4 0 0 0 5 5l-9 9a2 2 0 0 1-3-3l9-9a4 4 0 0 0-2-2z"/>',
    bed: '<path d="M3 18V8M3 14h18v4M21 14v-2a3 3 0 0 0-3-3h-7v5"/><circle cx="7" cy="11" r="2"/>',
    ring: '<circle cx="12" cy="14" r="7"/><path d="M9 3h6l-3 4z"/>',
    heart: '<path d="M12 20s-8-5-8-11a4.5 4.5 0 0 1 8-2.5A4.5 4.5 0 0 1 20 9c0 6-8 11-8 11z"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    tent: '<path d="M2 20L12 4l10 16zM12 4v16"/>',
    check: '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
    x: '<circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/>',
    flag: '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
    speak: '<path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/>'
  };
  function ico(k) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (P[k] || P.q) + '</svg>'; }

  /* ---------- read aloud ---------- */
  var CAN = 'speechSynthesis' in window;
  function speak(text) {
    if (!CAN) return;
    if (speechSynthesis.speaking) { speechSynthesis.cancel(); return; }
    var u = new SpeechSynthesisUtterance(text); u.lang = lang() === 'id' ? 'id-ID' : 'en-US'; u.rate = 0.9; speechSynthesis.speak(u);
  }
  function visibleText(node) {
    var parts = [];
    node.querySelectorAll('.tc-say').forEach(function (n) {
      var c = n.cloneNode(true); c.querySelectorAll(lang() === 'id' ? '.en' : '.id').forEach(function (x) { x.remove(); });
      parts.push(c.textContent.trim());
    });
    return parts.join('. ');
  }

  /* ---------- steps ---------- */
  function steps() {
    return TC.STEPS.filter(function (s) {
      if (s.abroad) return A.where === 'abroad' || A.where === 'both';
      return true;
    });
  }
  function opts(s) {
    var child = A.age === 'u18' || A.age === 'unsure';
    return s.o.filter(function (o) { return !o.child || child; });
  }
  function answered(s) { var v = A[s.id]; return s.kind === 'one' ? !!v : !!(v && v.length); }

  function intro() {
    root.innerHTML =
      '<div class="tc-card tc-intro">' +
      '<p class="tc-big tc-say">' + L('Answer a few short questions about what happened. At the end you get a result sheet that explains, in plain words, whether the situation may be human trafficking or forced labor under international law, Indonesian law and the law of the country where it happened.',
        'Jawab beberapa pertanyaan singkat tentang apa yang terjadi. Di akhir Anda mendapat lembar hasil yang menjelaskan, dengan kata-kata sederhana, apakah keadaan itu mungkin perdagangan orang atau kerja paksa menurut hukum internasional, hukum Indonesia, dan hukum negara tempat kejadiannya.') + '</p>' +
      '<ul class="tc-ticks">' +
      '<li class="tc-say">' + ico('lock') + L('Private. Your answers stay on this device and disappear when you close the page. Nothing is saved or sent.', 'Rahasia. Jawaban Anda tetap di perangkat ini dan hilang saat halaman ditutup. Tidak ada yang disimpan atau dikirim.') + '</li>' +
      '<li class="tc-say">' + ico('clock') + L('About 5 minutes, 13 questions or fewer. You can go back at any time.', 'Sekitar 5 menit, paling banyak 13 pertanyaan. Anda bisa kembali kapan saja.') + '</li>' +
      '<li class="tc-say">' + ico('adult') + L('If you are asking for someone else, answer for them.', 'Bila Anda bertanya untuk orang lain, jawablah untuk orang itu.') + '</li>' +
      '<li class="tc-say">' + ico('warn') + L('This is not legal advice. It shows what the law looks for, so that you can talk to a lawyer or a legal helper.', 'Ini bukan nasihat hukum. Ini menunjukkan apa yang dicari hukum, agar Anda bisa berbicara dengan pengacara atau pendamping hukum.') + '</li>' +
      '</ul>' +
      '<p class="tc-danger tc-say">' + L('<b>In danger now?</b> Call the local police, or the nearest Indonesian embassy or consulate if you are abroad. <a href="/legal-help/">Find free legal help</a>.',
        '<b>Dalam bahaya sekarang?</b> Hubungi polisi setempat, atau KBRI/KJRI terdekat bila Anda di luar negeri. <a href="/legal-help/">Cari bantuan hukum gratis</a>.') + '</p>' +
      '<div class="tc-nav"><button type="button" class="tc-go" id="tc-start">' + L('Start', 'Mulai') + ' →</button>' +
      (CAN ? '<button type="button" class="tc-listen" data-say="card">' + ico('speak') + L('Listen', 'Dengarkan') + '</button>' : '') + '</div></div>';
    $('#tc-start').onclick = function () { A = {}; pos = 0; count('start', 'Trafficking check started'); show(); };
  }

  function show() {
    var S = steps(), s = S[pos];
    var many = s.kind === 'many';
    var h = '<div class="tc-card" id="tc-step" data-step="' + s.id + '"><div class="tc-prog" aria-hidden="true"><i style="width:' + Math.round(100 * pos / S.length) + '%"></i></div>' +
      '<p class="tc-count">' + L('Question ' + (pos + 1) + ' of ' + S.length, 'Pertanyaan ' + (pos + 1) + ' dari ' + S.length) + '</p>' +
      '<fieldset><legend class="tc-q tc-say">' + T(s.q) + '</legend>' + (s.h ? '<p class="tc-hint tc-say">' + T(s.h) + '</p>' : '') +
      '<div class="tc-opts' + (s.id === 'dest' ? ' tc-small' : '') + '">';
    opts(s).forEach(function (o) {
      var on = many ? has(s.id, o.k) : A[s.id] === o.k;
      h += '<button type="button" class="tc-opt" data-k="' + o.k + '" aria-pressed="' + on + '">' + ico(o.i) + '<span class="tc-say">' + T(o) + '</span>' + (many ? '<b class="tc-box" aria-hidden="true"></b>' : '') + '</button>';
    });
    h += '</div></fieldset><div class="tc-nav">' +
      (pos > 0 ? '<button type="button" class="tc-back">← ' + L('Back', 'Kembali') + '</button>' : '<button type="button" class="tc-back" data-home="1">← ' + L('Back', 'Kembali') + '</button>') +
      '<button type="button" class="tc-go"' + (answered(s) ? '' : ' disabled') + '>' + (pos === S.length - 1 ? L('See my result sheet', 'Lihat lembar hasil') : L('Next', 'Lanjut')) + ' →</button>' +
      (CAN ? '<button type="button" class="tc-listen" data-say="card">' + ico('speak') + L('Listen', 'Dengarkan') + '</button>' : '') + '</div></div>';
    root.innerHTML = h;
    root.querySelectorAll('.tc-opt').forEach(function (b) {
      b.onclick = function () {
        var k = b.dataset.k;
        if (!many) { A[s.id] = k; if (s.id === 'where' && k === 'in') delete A.dest; show(); return; }
        var v = A[s.id] || [];
        if (k === 'none' || k === 'unsure') v = v.indexOf(k) >= 0 ? [] : [k];
        else { v = v.filter(function (x) { return x !== 'none' && x !== 'unsure'; }); v = v.indexOf(k) >= 0 ? v.filter(function (x) { return x !== k; }) : v.concat(k); }
        A[s.id] = v; show();
      };
    });
    $('.tc-back', root).onclick = function (e) { if (e.currentTarget.dataset.home) { intro(); return; } pos--; show(); };
    $('.tc-go', root).onclick = function () { if (pos < steps().length - 1) { pos++; show(); } else result(); };
    var f = $('.tc-q', root); if (f) { f.setAttribute('tabindex', '-1'); f.focus({ preventScroll: true }); }
    root.scrollIntoView({ block: 'start', behavior: 'smooth' });
  }

  /* ---------- the rule engine ---------- */
  function analyse() {
    var R = { refs: [], co: [], inv: [], ilo: [] };
    var ref = function (a) { R.refs = R.refs.concat(a); };
    R.child = A.age === 'u18'; R.maybeChild = A.age === 'unsure';
    R.woman = A.sex === 'f'; R.abroad = A.where !== 'in'; R.dest = A.dest && A.dest !== 'other' ? A.dest : null;
    R.sector = A.sector;
    // Element 1: act
    R.act = (A.act || []).filter(function (k) { return TC.MAP.act[k]; });
    R.actSt = R.act.length ? 'yes' : has('act', 'unsure') ? 'unk' : 'no';
    R.act.forEach(function (k) { ref(TC.MAP.act[k].ref); });
    // Element 2: means
    var mk = [].concat(A.force || [], A.money || [], A.trick || []);
    R.means = mk.filter(function (k) { return TC.MAP.means[k]; });
    R.meansSt = R.means.length ? 'yes' : (has('force', 'unsure') || has('money', 'unsure') || has('trick', 'unsure')) ? 'unk' : 'no';
    R.means.forEach(function (k) { var m = TC.MAP.means[k]; ref(m.ref); if (m.ilo) R.ilo.push(m.ilo); if (m.co) R.co.push(k); if (m.inv) R.inv.push(k); });
    if (has('trick', 'noquit')) R.inv.push('noquit');
    // Element 3: purpose
    R.purpose = (A.purpose || []).filter(function (k) { return TC.MAP.purpose[k]; });
    R.purpose.forEach(function (k) { var p = TC.MAP.purpose[k]; ref(p.ref); if (p.inv) R.inv.push(k); });
    (A.cond || []).forEach(function (k) { var c = TC.MAP.cond[k]; if (c) { R.ilo.push(c.ilo); R.inv.push(k); } });
    if (R.child || R.maybeChild) { if (has('act', 'move') || has('act', 'send') || has('act', 'receive')) R.ilo.push('vuln'); }
    if (R.child) R.ilo.push('vuln');
    R.ilo = uniq(R.ilo); R.co = uniq(R.co); R.inv = uniq(R.inv);
    // Forced labor, ICLS 2018 test: involuntary work AND coercion
    R.fl = R.co.length > 0 && R.inv.length > 0;
    R.purpSt = R.purpose.length ? 'yes' : has('purpose', 'unsure') ? 'unk' : 'no';
    R.purpInferred = false;
    if (R.fl && R.purpSt !== 'yes') { R.purpSt = 'yes'; R.purpInferred = true; ref(['c29', 'uu21_7']); }
    // Combine
    var meansOk = R.meansSt === 'yes';
    var childTest = R.actSt === 'yes' && R.purpSt === 'yes';
    var adultTest = childTest && meansOk;
    R.childOnly = R.maybeChild && childTest && !adultTest;
    var present = (R.actSt === 'yes') + ((R.child || meansOk) ? 1 : 0) + (R.purpSt === 'yes');
    var unk = (R.actSt === 'unk') + (R.meansSt === 'unk') + (R.purpSt === 'unk');
    var labor = has('money', 'wages') || has('money', 'docs') || has('money', 'debt') || has('trick', 'lied') || (A.cond || []).some(function (k) { return k !== 'none'; });
    if ((R.child && childTest) || adultTest) R.level = 'T';
    else if (R.childOnly) R.level = 'P';
    else if (R.fl) R.level = 'F';
    else if (A.smug === 'yes' && R.purpSt !== 'yes' && !R.co.length) R.level = 'S';
    else if (present >= 2 || (present >= 1 && unk >= 1)) R.level = 'P';
    else if (A.smug === 'yes') R.level = 'S';
    else if (labor) R.level = 'L';
    else R.level = 'N';
    R.present = present; R.unk = unk; R.labor = labor;
    // Fixed references by situation
    if (R.level === 'T' || R.level === 'P') ref(['pal3a', 'actip', 'uu21_1', 'uu21_2', 'kuhp']);
    if (R.level === 'F') ref(['c29', 'icls', 'ilo11', 'iccpr8', 'cmw']);
    if (R.ilo.length) ref(['ilo11', 'icls']);
    if (R.child || R.maybeChild) ref(['pal3c', 'crc', 'opsc', 'c182', 'uu21_6', 'uu35_76f', 'uu35_76i', 'uu35_59', 'jgc']);
    if (R.woman) ref(['cedaw6', 'gr38']);
    if (has('purpose', 'sex') || has('purpose', 'marriage') || has('force', 'violence')) ref(['tpks4', 'tpksv']);
    if (has('purpose', 'marriage') && (R.child || R.maybeChild)) ref(['uu16']);
    if (A.consent === 'yes') ref(['pal3b', 'uu21_18']);
    if (A.smug === 'yes') ref(['smug']);
    if (R.sector === 'domestic') ref(['c189', 'cmwgc1']);
    if (R.abroad && (R.level === 'T' || R.level === 'P')) ref(['uu21_4']);
    if (has('act', 'recruit') || has('act', 'send') || has('money', 'debt')) ref(['uu18_30', 'uu18_69']);
    if (R.level !== 'N') ref(['pal6', 'uu21_vict', 'lpsk', 'ohchr', 'p29', 'srtip']);
    if (labor && !R.abroad) ref(['uu2']);
    R.refs = uniq(R.refs).filter(function (k) { return TC.REF[k]; });
    return R;
  }

  /* ---------- result sheet ---------- */
  var EL = {
    yes: { c: 'ok', en: 'Present', id: 'Ada' }, unk: { c: 'unk', en: 'Not clear', id: 'Belum jelas' },
    no: { c: 'no', en: 'Not found', id: 'Tidak ditemukan' }, na: { c: 'na', en: 'Not needed for a child', id: 'Tidak diperlukan untuk anak' }
  };
  function tile(num, name, st, items, map, extra) {
    var e = EL[st];
    var li = items.map(function (k) { var m = map[k]; return '<li>' + T(m) + '</li>'; }).join('');
    return '<div class="tc-el tc-' + e.c + '"><p class="tc-eln">' + num + '</p><h4>' + T(name) + '</h4><p class="tc-st">' + T(e) + '</p>' +
      (li ? '<ul>' + li + '</ul>' : '') + (extra || '') + '</div>';
  }
  function refLine(k) {
    var r = TC.REF[k];
    return '<li><b>' + (r.u ? '<a href="' + r.u + '" rel="noopener">' + T(r.t) + '</a>' : T(r.t)) + '</b>' + (r.chk ? ' <span class="tc-chk">' + L('being checked', 'sedang diperiksa') + '</span>' : '') +
      '<br>' + T(r.d) + (r.ri ? ' <i>' + T(r.ri) + '</i>' : '') + '</li>';
  }
  function trStat(v) {
    if (!v) return L('unknown', 'tidak diketahui');
    var s = v[0], y = v[1] ? ' (' + v[1] + ')' : '', c = v[2] ? ' *' : '';
    if (s === 'p') return '<b class="tc-yes">' + L('Party', 'Negara pihak') + y + c + '</b>';
    if (s === 's') return L('Signed only', 'Hanya menandatangani');
    if (s === '?') return L('Being checked', 'Sedang diperiksa');
    return '<span class="tc-nop">' + L('Not a party', 'Bukan negara pihak') + '</span>';
  }
  function pickCases(R) {
    var tags = [];
    var secMap = { domestic: 'domestic', farm: 'farm', fishing: 'fishing', factory: 'factory', ent: 'sex', scam: 'crime' };
    if (secMap[R.sector]) tags.push(secMap[R.sector]);
    R.purpose.forEach(function (k) { if (TC.CASES[k]) tags.push(k); });
    if (R.child || R.maybeChild) tags.push('child');
    if (has('money', 'debt')) tags.push('debt');
    if (R.fl || has('purpose', 'forcedwork')) tags.push('forced');
    if (R.abroad) tags.push('abroad');
    if (has('money', 'debt') || has('act', 'recruit')) tags.push('fees');
    if (R.level === 'T') tags.push('victim');
    tags.push('general');
    var score = {};
    tags.forEach(function (t, i) {
      (TC.CASES[t] || []).forEach(function (id, j) { score[id] = (score[id] || 0) + 10 / (i + 1) - j * 0.2; });
    });
    var south = { asia: 1, africa: 1, latam: 1, mideast: 1, gulf: 1, pacific: 1 };
    var list = Object.keys(score).filter(function (id) { return TC.CD[id]; }).map(function (id) {
      var d = TC.CD[id]; var s = score[id] + (south[d.reg] ? 3 : 0) + (d.st === 'C' ? -4 : 0); return [s, id];
    }).sort(function (a, b) { return b[0] - a[0]; });
    // keep variety: at most 4 from the first (most specific) tag, then the best of the rest
    var first = TC.CASES[tags[0]] || [], out = [], nFirst = 0;
    list.forEach(function (x) { if (out.length < 7 && (first.indexOf(x[1]) < 0 || nFirst++ < 4)) out.push(x[1]); });
    return out;
  }
  var TIER = { national: { en: 'National court', id: 'Pengadilan nasional' }, regional: { en: 'Regional body', id: 'Badan kawasan' }, international: { en: 'International body', id: 'Badan internasional' } };
  var OUT = { won: { en: 'Worker or victim won', id: 'Pekerja atau korban menang' }, lost: { en: 'Worker or victim lost', id: 'Pekerja atau korban kalah' }, partly: { en: 'Partly won', id: 'Menang sebagian' }, advisory: { en: 'Advisory', id: 'Nasihat' }, unknown: { en: 'Outcome being coded', id: 'Hasil sedang dikodekan' } };

  function result() {
    var R = analyse(), LV = TC.LEVEL[R.level];
    count('finish/' + R.level + '/' + (R.abroad ? 'abroad' : 'indonesia'), 'Trafficking check finished: ' + R.level);
    var today = new Date().toISOString().slice(0, 10);
    var h = '<article class="tc-sheet" id="tc-sheet">';
    h += '<header class="tc-sh"><p class="tc-eye">' + L('Institute for Migrant Rights · Legal Clinic', 'Institute for Migrant Rights · Klinik Hukum') + '</p>' +
      '<h2>' + L('Result sheet: could this be human trafficking?', 'Lembar hasil: apakah ini perdagangan orang?') + '</h2>' +
      '<p class="tc-meta">' + L('Made on ' + today + ' in your browser. Not saved or sent anywhere. Keep it safe: it shows your answers.', 'Dibuat pada ' + today + ' di peramban Anda. Tidak disimpan atau dikirim ke mana pun. Simpan baik-baik: lembar ini memuat jawaban Anda.') + '</p></header>';

    // 1. Verdict
    h += '<section class="tc-verdict tc-v-' + LV.c + '"><p class="tc-eye">' + L('1 · Result', '1 · Hasil') + '</p><h3>' + T(LV) + '</h3><p>' + T(LV.s) + '</p>';
    if (R.childOnly) h += '<p>' + L('If the person was under 18 when it started, the answers already meet the definition of child trafficking, because no “means” is needed for a child.', 'Bila orang itu berusia di bawah 18 tahun ketika semua ini dimulai, jawaban ini sudah memenuhi definisi perdagangan anak, karena untuk anak tidak diperlukan “cara”.') + '</p>';
    if (R.level === 'T' && R.fl) h += '<p>' + L('The answers also show forced labor.', 'Jawaban ini juga menunjukkan kerja paksa.') + '</p>';
    if (R.dest && TC.DEST[R.dest]) {
      var DD = TC.DEST[R.dest];
      if (DD.narrow === 'sexcross' && (R.level === 'T' || R.level === 'P') && !has('purpose', 'sex'))
        h += '<p class="tc-local"><b>' + T(DD.n) + ':</b> ' + L('the local trafficking offense covers only moving people into or out of Hong Kong for prostitution, so this situation would be handled under other offenses there. International standards and Indonesian law still apply as shown below.', 'tindak pidana perdagangan orang di sana hanya mencakup membawa orang masuk atau keluar Hong Kong untuk pelacuran, sehingga keadaan ini akan ditangani dengan tindak pidana lain di sana. Standar internasional dan hukum Indonesia tetap berlaku seperti di bawah.') + '</p>';
      else if (R.level === 'F') h += '<p class="tc-local"><b>' + T(DD.n) + ':</b> ' + T(DD.fl) + '</p>';
    }
    h += '<p class="tc-small">' + L('This is an indication from your answers, not a legal finding. Only a court can decide. Facts you did not mention can change the result.', 'Ini petunjuk dari jawaban Anda, bukan putusan hukum. Hanya pengadilan yang bisa memutuskan. Fakta yang tidak Anda sebutkan bisa mengubah hasilnya.') + '</p></section>';

    // 2. Three elements
    var needM = !(R.child);
    h += '<section><p class="tc-eye">' + L('2 · The three parts of trafficking', '2 · Tiga unsur perdagangan orang') + '</p>' +
      '<p class="tc-lead">' + L('International law (Palermo Protocol, Art. 3) and Indonesian law (UU 21/2007, Art. 1(1)) both look for three parts. For a child, only the first and the third are needed.', 'Hukum internasional (Protokol Palermo, Pasal 3) dan hukum Indonesia (UU 21/2007, Pasal 1 angka 1) sama-sama mencari tiga unsur. Untuk anak, cukup unsur pertama dan ketiga.') + '</p><div class="tc-els">' +
      tile('1', { en: 'Act: what was done', id: 'Perbuatan: apa yang dilakukan' }, R.actSt, R.act, TC.MAP.act) +
      tile('2', { en: 'Means: how it was done', id: 'Cara: bagaimana dilakukan' }, needM ? R.meansSt : 'na', R.means, TC.MAP.means,
        R.maybeChild ? '<p class="tc-small">' + L('If the person was under 18, this part is not needed.', 'Bila orang itu di bawah 18 tahun, unsur ini tidak diperlukan.') + '</p>' : '') +
      tile('3', { en: 'Purpose: exploitation', id: 'Tujuan: eksploitasi' }, R.purpSt, R.purpose, TC.MAP.purpose,
        R.purpInferred ? '<p class="tc-small">' + L('Inferred: the forced labor signs below show a purpose of forced labor.', 'Disimpulkan: tanda kerja paksa di bawah menunjukkan tujuan kerja paksa.') + '</p>' : '') +
      '</div>';
    if (A.consent === 'yes') h += '<p class="tc-note">' + L('<b>Agreeing at first does not matter.</b> Once any of the means was used, the person’s consent is irrelevant (Palermo Protocol, Art. 3(b); UU 21/2007, Art. 26). A child cannot consent to exploitation at all.', '<b>Setuju di awal tidak berarti apa-apa.</b> Begitu salah satu cara dipakai, persetujuan orang itu tidak relevan (Protokol Palermo, Pasal 3(b); UU 21/2007, Pasal 26). Anak sama sekali tidak bisa menyetujui eksploitasi.') + '</p>';
    h += '<p class="tc-note">' + L('<b>Where Indonesian law is wider.</b> UU 21/2007 adds “sending” to the acts and confinement, falsification and debt bondage to the means. It also covers conduct that <i>results</i> in exploitation, not only conduct done for that purpose.', '<b>Di mana hukum Indonesia lebih luas.</b> UU 21/2007 menambahkan “pengiriman” pada perbuatan serta penyekapan, pemalsuan, dan penjeratan utang pada cara. UU ini juga mencakup perbuatan yang <i>mengakibatkan</i> orang tereksploitasi, bukan hanya yang bertujuan eksploitasi.') + '</p></section>';

    // 3. Forced labor
    h += '<section><p class="tc-eye">' + L('3 · Forced labor test', '3 · Uji kerja paksa') + '</p>' +
      '<p class="tc-lead">' + L('Forced labor is work taken under the threat of a penalty that the person did not offer freely (ILO Convention 29, Art. 2). Following the ILO statistical guidelines (2018), this check finds forced labor when the work was <b>not free</b> and was kept in place by <b>coercion</b>.', 'Kerja paksa adalah pekerjaan yang diambil di bawah ancaman hukuman dan tidak ditawarkan dengan sukarela (Konvensi ILO 29, Pasal 2). Mengikuti pedoman statistik ILO (2018), pemeriksaan ini menemukan kerja paksa bila pekerjaan itu <b>tidak sukarela</b> dan dipertahankan dengan <b>paksaan</b>.') + '</p>' +
      '<p><b>' + (R.fl ? L('Result: signs of forced labor found.', 'Hasil: ditemukan tanda kerja paksa.') : L('Result: the two-part test is not met by your answers.', 'Hasil: uji dua bagian tidak terpenuhi oleh jawaban Anda.')) + '</b> ' +
      L('Not free: ' + R.inv.length + ' sign(s). Coercion: ' + R.co.length + ' sign(s).', 'Tidak sukarela: ' + R.inv.length + ' tanda. Paksaan: ' + R.co.length + ' tanda.') + '</p><ul class="tc-ilo">';
    TC.ILO.forEach(function (x) { var on = R.ilo.indexOf(x[0]) >= 0; h += '<li class="' + (on ? 'on' : '') + '">' + ico(on ? 'check' : 'dash') + T(x[1]) + '</li>'; });
    h += '</ul><p class="tc-small">' + L('The eleven ILO indicators of forced labor (2012). Ticked = found in your answers.', 'Sebelas indikator kerja paksa ILO (2012). Dicentang = ditemukan dalam jawaban Anda.') + '</p></section>';

    // 4. Women and children
    var n = 4;
    if (R.child || R.maybeChild || R.woman) {
      h += '<section class="tc-wc"><p class="tc-eye">' + L(n + ' · Extra protection', n + ' · Pelindungan tambahan') + '</p>';
      if (R.child || R.maybeChild) h += '<h4>' + L('Children (under 18)', 'Anak (di bawah 18 tahun)') + '</h4><ul>' +
        '<li>' + L('No “means” is needed: moving or receiving a child for exploitation is trafficking (Palermo Protocol, Art. 3(c)–(d); UU 21/2007, Arts. 5–6).', 'Tidak diperlukan “cara”: memindahkan atau menerima anak untuk dieksploitasi adalah perdagangan orang (Protokol Palermo, Pasal 3(c)–(d); UU 21/2007, Pasal 5–6).') + '</li>' +
        '<li>' + L('Penalties are one third higher when the victim is a child (UU 21/2007, Art. 17). Selling or trafficking a child, and exploiting a child economically or sexually, are also crimes under the Child Protection Law (UU 35/2014, Arts. 76F, 76I, 83, 88).', 'Pidana ditambah sepertiga bila korbannya anak (UU 21/2007, Pasal 17). Menjual atau memperdagangkan anak, serta mengeksploitasi anak secara ekonomi atau seksual, juga tindak pidana menurut UU Perlindungan Anak (UU 35/2014, Pasal 76F, 76I, 83, 88).') + '</li>' +
        '<li>' + L('A child’s real age counts, even if papers were faked to show an adult. Child victims have a right to special protection and restitution (UU 35/2014, Arts. 59, 71D) and to child-friendly procedures (CRC Optional Protocol, Art. 8).', 'Usia sebenarnya anak yang dihitung, meskipun dokumennya dipalsukan agar tampak dewasa. Anak korban berhak atas perlindungan khusus dan restitusi (UU 35/2014, Pasal 59, 71D) serta proses yang ramah anak (Protokol Opsional KHA, Pasal 8).') + '</li>' +
        (has('purpose', 'marriage') ? '<li>' + L('Marriage under 19 is not allowed in Indonesia (UU 16/2019), and child marriage is a form of forced marriage under UU TPKS, Art. 10.', 'Perkawinan di bawah 19 tahun tidak diperbolehkan di Indonesia (UU 16/2019), dan perkawinan anak merupakan bentuk pemaksaan perkawinan menurut UU TPKS, Pasal 10.') + '</li>' : '') +
        '</ul>';
      if (R.woman) h += '<h4>' + L('Women and girls', 'Perempuan dan anak perempuan') + '</h4><ul>' +
        '<li>' + L('States must stop all forms of traffic in women (CEDAW, Art. 6). The CEDAW Committee’s General Recommendation No. 38 (2020) explains the special risks for migrating women and girls, including in domestic work.', 'Negara wajib menghentikan segala bentuk perdagangan perempuan (CEDAW, Pasal 6). Rekomendasi Umum Komite CEDAW No. 38 (2020) menjelaskan risiko khusus bagi perempuan dan anak perempuan yang bermigrasi, termasuk di kerja rumah tangga.') + '</li>' +
        '<li>' + L('Sexual exploitation, sexual slavery and forced marriage are crimes under UU TPKS (Arts. 4, 10, 12–13), which gives victims rights to handling, protection, recovery and restitution.', 'Eksploitasi seksual, perbudakan seksual, dan pemaksaan perkawinan adalah tindak pidana menurut UU TPKS (Pasal 4, 10, 12–13), yang memberi korban hak atas penanganan, pelindungan, pemulihan, dan restitusi.') + '</li>' +
        (R.sector === 'domestic' ? '<li>' + L('Domestic workers have the right to keep their own documents and to leave the house in their free time (ILO C189, Art. 9; CMW General Comment No. 1). Indonesia has not ratified C189.', 'Pekerja rumah tangga berhak memegang dokumennya sendiri dan keluar rumah pada waktu luang (ILO C189, Pasal 9; Komentar Umum CMW No. 1). Indonesia belum meratifikasi C189.') + '</li>' : '') +
        '<li>' + L('Pregnancy or loss of reproductive function caused by trafficking makes the penalty heavier (UU 21/2007, Art. 7).', 'Kehamilan atau hilangnya fungsi reproduksi akibat perdagangan orang memperberat pidana (UU 21/2007, Pasal 7).') + '</li></ul>';
      h += '</section>'; n++;
    }

    // 5. Indonesian law: possible charges
    var ch = [];
    if (R.level === 'T' || R.level === 'P' || R.level === 'F') {
      ch.push(L('<b>Trafficking in persons</b>, UU 21/2007, Art. 2: 3 to 15 years in prison and a fine of Rp120–600 million. Attempting or helping is punished the same way (Art. 10).', '<b>Tindak pidana perdagangan orang</b>, UU 21/2007, Pasal 2: penjara 3 sampai 15 tahun dan denda Rp120–600 juta. Percobaan atau pembantuan dipidana sama (Pasal 10).'));
      if (R.abroad) ch.push(L('<b>Taking an Indonesian abroad for exploitation</b>, UU 21/2007, Art. 4: same penalty. Indonesian courts can try recruiters and agents in Indonesia even when the exploitation happened abroad.', '<b>Membawa WNI ke luar negeri untuk dieksploitasi</b>, UU 21/2007, Pasal 4: pidana yang sama. Pengadilan Indonesia bisa mengadili perekrut dan agen di Indonesia meskipun eksploitasinya terjadi di luar negeri.'));
      if (R.child || R.maybeChild) ch.push(L('<b>Child victim</b>: penalties one third higher (UU 21/2007, Art. 17); trafficking or exploiting a child under UU 35/2014, Arts. 76F/83 and 76I/88.', '<b>Korban anak</b>: pidana ditambah sepertiga (UU 21/2007, Pasal 17); memperdagangkan atau mengeksploitasi anak menurut UU 35/2014, Pasal 76F/83 dan 76I/88.'));
      if (has('trick', 'power')) ch.push(L('<b>Official who abused power</b>: one third higher (UU 21/2007, Art. 8).', '<b>Pejabat yang menyalahgunakan kekuasaan</b>: ditambah sepertiga (UU 21/2007, Pasal 8).'));
      if (has('money', 'forged')) ch.push(L('<b>False information in documents</b> to make trafficking easier (UU 21/2007, Art. 19).', '<b>Keterangan palsu dalam dokumen</b> untuk mempermudah perdagangan orang (UU 21/2007, Pasal 19).'));
      if (has('force', 'violence')) ch.push(L('<b>Serious injury or death</b> makes the penalty heavier (UU 21/2007, Art. 7).', '<b>Luka berat atau kematian</b> memperberat pidana (UU 21/2007, Pasal 7).'));
      ch.push(L('The new Criminal Code (KUHP 2023, in force since 2 January 2026) also has a chapter on trafficking; UU 21/2007 still applies as a special law.', 'KUHP baru (KUHP 2023, berlaku sejak 2 Januari 2026) juga memuat bab tentang perdagangan orang; UU 21/2007 tetap berlaku sebagai undang-undang khusus.'));
    }
    if (has('purpose', 'sex')) ch.push(L('<b>Sexual exploitation or sexual slavery</b>, UU TPKS, Arts. 12–13: up to 15 years.', '<b>Eksploitasi seksual atau perbudakan seksual</b>, UU TPKS, Pasal 12–13: paling lama 15 tahun.'));
    if (has('purpose', 'marriage')) ch.push(L('<b>Forced marriage</b>, including child marriage, UU TPKS, Art. 10: up to 9 years.', '<b>Pemaksaan perkawinan</b>, termasuk perkawinan anak, UU TPKS, Pasal 10: paling lama 9 tahun.'));
    if (has('act', 'recruit') || has('act', 'send')) ch.push(L('<b>Unlawful placement of migrant workers</b>: only licensed placement companies may place workers abroad (UU 18/2017, Art. 69), and placement costs may not be charged to the worker (Art. 30).', '<b>Penempatan pekerja migran secara melawan hukum</b>: hanya perusahaan penempatan berizin yang boleh menempatkan pekerja ke luar negeri (UU 18/2017, Pasal 69), dan biaya penempatan tidak boleh dibebankan kepada pekerja (Pasal 30).'));
    if (R.level === 'F') ch.push(L('Where the trafficking act is not proved, the conduct may still be charged under the Criminal Code (for example deprivation of liberty, threats or assault).', 'Bila unsur perbuatan perdagangan orang tidak terbukti, perbuatan itu tetap bisa didakwakan menurut KUHP (misalnya perampasan kemerdekaan, pengancaman, atau penganiayaan).'));
    if (R.level === 'L' || R.level === 'N' || R.level === 'S') {
      if (R.labor) ch.push(L('Unpaid wages and broken contracts are labor claims: in Indonesia through bipartite talks, mediation and the Industrial Relations Court (UU 2/2004); for work abroad, through KP2MI and the Indonesian embassy.', 'Upah yang tidak dibayar dan kontrak yang dilanggar adalah tuntutan ketenagakerjaan: di Indonesia melalui perundingan bipartit, mediasi, dan Pengadilan Hubungan Industrial (UU 2/2004); untuk kerja di luar negeri, melalui KP2MI dan KBRI.'));
      if (A.smug === 'yes') ch.push(L('A smuggled migrant should not be prosecuted for having been smuggled (Smuggling Protocol, Art. 5). Smuggling turns into trafficking if the person is later exploited.', 'Migran yang diselundupkan tidak boleh dituntut karena telah diselundupkan (Protokol Penyelundupan, Pasal 5). Penyelundupan berubah menjadi perdagangan orang bila orang itu kemudian dieksploitasi.'));
    }
    if (ch.length) {
      h += '<section><p class="tc-eye">' + L(n + ' · Under Indonesian law: what could be charged', n + ' · Menurut hukum Indonesia: apa yang bisa didakwakan') + '</p><ul class="tc-list">' + ch.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>' +
        '<p class="tc-small">' + L('Penalties as written in the statutes; article references are being checked against the official texts (JDIH BPK, peraturan.go.id). Prosecutors choose the charges.', 'Pidana sebagaimana tertulis dalam undang-undang; rujukan pasal sedang diperiksa terhadap naskah resmi (JDIH BPK, peraturan.go.id). Jaksa yang memilih dakwaan.') + '</p></section>';
      n++;
    }

    // 6. Destination country
    if (R.abroad) {
      h += '<section class="tc-dest"><p class="tc-eye">' + L(n + ' · The country where it happened', n + ' · Negara tempat kejadian') + '</p>';
      if (R.dest && TC.DEST[R.dest]) {
        var De = TC.DEST[R.dest], Dd = TC.D[R.dest] || {};
        h += '<h3>' + T(De.n) + '</h3><p class="tc-note"><b>' + L('How its law differs:', 'Perbedaan hukumnya:') + '</b> ' + T(De.pec) + ' <span class="tc-chk">' + L('being checked', 'sedang diperiksa') + '</span></p>';
        if (R.level === 'F' || R.fl) h += '<p><b>' + L('Forced labor there:', 'Kerja paksa di sana:') + '</b> ' + T(De.fl) + '</p>';
        var laws = (Dd.laws || []).filter(function (l) { return /traffick/i.test(l.topic + ' ' + l.t) || (R.sector === 'domestic' && /domestic/i.test(l.topic + ' ' + l.t)); });
        if (laws.length) h += '<h4>' + L('Main laws', 'Undang-undang utama') + '</h4><ul class="tc-list">' + laws.map(function (l) {
          return '<li>' + (l.u ? '<a href="' + l.u + '" rel="noopener">' + l.t + '</a>' : l.t) + (l.no ? ', ' + l.no : '') + ' (' + l.y + (l.am ? L(', amended ' + l.am, ', diubah ' + l.am) : '') + ')</li>';
        }).join('') + '</ul>';
        var tr = Dd.tr || {};
        h += '<h4>' + L('Its international obligations', 'Kewajiban internasionalnya') + '</h4><table class="tc-tr"><tbody>' +
          [['palermo', 'UN Trafficking Protocol (Palermo)', 'Protokol Perdagangan Orang PBB (Palermo)'], ['c29', 'ILO Forced Labour Convention (C29)', 'Konvensi Kerja Paksa ILO (C29)'], ['p29', 'ILO Forced Labor Protocol (P29)', 'Protokol Kerja Paksa ILO (P29)'],
           ['c105', 'ILO Abolition of Forced Labour (C105)', 'Penghapusan Kerja Paksa ILO (C105)'], ['c189', 'ILO Domestic Workers (C189)', 'Pekerja Rumah Tangga ILO (C189)'], ['icrmw', 'UN Migrant Workers Convention', 'Konvensi Pekerja Migran PBB']]
            .map(function (r) { return '<tr><th>' + L(r[1], r[2]) + '</th><td>' + trStat(tr[r[0]]) + '</td></tr>'; }).join('') +
          (De.asean ? '<tr><th>' + L('ASEAN Convention against Trafficking (ACTIP)', 'Konvensi ASEAN Menentang Perdagangan Orang (ACTIP)') + '</th><td><b class="tc-yes">' + L('Party', 'Negara pihak') + '</b></td></tr>' : '') +
          '</tbody></table>' + (tr.palermo && tr.palermo[2] ? '<p class="tc-small">* ' + L('From the UN Treaty Collection; being checked.', 'Dari UN Treaty Collection; sedang diperiksa.') + '</p>' : '') +
          (R.dest === 'HK' ? '<p class="tc-small">' + L('Hong Kong treaty status shows treaties applied to Hong Kong by China.', 'Status traktat Hong Kong menunjukkan traktat yang diberlakukan Tiongkok untuk Hong Kong.') + '</p>' : '');
        var mob = (Dd.mob || {})[R.sector] || (Dd.mob || {})._;
        var rules = [];
        if (mob) rules.push('<b>' + L('Changing employer', 'Pindah majikan') + (mob.grp ? ' (' + T(mob.grp) + ')' : '') + ':</b> ' + (mob.id ? T(mob) : mob.en));
        if (mob && mob.fee) rules.push('<b>' + L('Recruitment fees', 'Biaya rekrutmen') + ':</b> ' + mob.fee);
        if (Dd.dw && R.sector === 'domestic') {
          if (Dd.dw.cov) rules.push('<b>' + L('Domestic workers and labor law', 'Pekerja rumah tangga dan hukum ketenagakerjaan') + ':</b> ' + Dd.dw.cov);
          if (Dd.dw.doc) rules.push('<b>' + L('Keeping your documents', 'Memegang dokumen sendiri') + ':</b> ' + Dd.dw.doc);
          if (Dd.dw.viol) rules.push('<b>' + L('Violence and trafficking', 'Kekerasan dan perdagangan orang') + ':</b> ' + Dd.dw.viol);
        }
        if (Dd.comp) rules.push('<b>' + L('Where to complain', 'Tempat mengadu') + ':</b> ' + T(Dd.comp));
        if (rules.length) h += '<h4>' + L('Rules that matter for this situation', 'Aturan yang penting untuk keadaan ini') + '</h4><ul class="tc-list">' + rules.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>' +
          '<p class="tc-small"><span class="id">Catatan data di atas dalam bahasa Inggris. </span>' + L('From the IMR comparison data; see the source on ', 'Dari data perbandingan IMR; lihat sumbernya di ') + '<a href="' + De.page + '">' + L('the comparison page', 'halaman perbandingan') + '</a>' + (R.sector === 'domestic' ? L(' and <a href="/domestic-workers/">Migrant Domestic Workers</a>', ' dan <a href="/domestic-workers/">Pekerja Rumah Tangga Migran</a>') : '') + '.</p>';
      } else {
        h += '<p>' + L('We do not yet have a profile for that country. Check whether it is a party to the <a href="https://treaties.un.org/" rel="noopener">UN Trafficking Protocol</a> and to <a href="https://normlex.ilo.org/" rel="noopener">ILO Conventions 29 and 189</a>, and look for its anti-trafficking law. The <a href="/migration-law/">Migration Law Atlas</a> shows many countries’ treaty status.', 'Kami belum memiliki profil negara itu. Periksa apakah negara itu pihak pada <a href="https://treaties.un.org/" rel="noopener">Protokol Perdagangan Orang PBB</a> dan <a href="https://normlex.ilo.org/" rel="noopener">Konvensi ILO 29 dan 189</a>, dan cari undang-undang anti-perdagangan orangnya. <a href="/migration-law/">Atlas Hukum Migrasi</a> menunjukkan status traktat banyak negara.') + '</p>';
      }
      h += '<p>' + L('Indonesian law keeps protecting you abroad: the Indonesian government must protect victims abroad and bring them home (UU 21/2007, Art. 54), and Indonesian migrant workers have rights under UU 18/2017. Contact the nearest Indonesian embassy or consulate.', 'Hukum Indonesia tetap melindungi Anda di luar negeri: Pemerintah Indonesia wajib melindungi korban di luar negeri dan memulangkannya (UU 21/2007, Pasal 54), dan Pekerja Migran Indonesia memiliki hak menurut UU 18/2017. Hubungi KBRI atau KJRI terdekat.') + '</p></section>';
      n++;
    }

    // 7. Victims' rights
    if (R.level !== 'N') {
      h += '<section><p class="tc-eye">' + L(n + ' · Rights of victims and possible remedies', n + ' · Hak korban dan kemungkinan pemulihan') + '</p><ul class="tc-list">' +
        '<li>' + L('<b>Not punished</b> for crimes the trafficker forced you to commit (UU 21/2007, Art. 18) or, under international standards, for immigration offenses linked to the trafficking (OHCHR Principle 7; ACTIP, Art. 14; ILO P29, Art. 4(2)).', '<b>Tidak dipidana</b> atas kejahatan yang dipaksakan pelaku (UU 21/2007, Pasal 18) atau, menurut standar internasional, atas pelanggaran keimigrasian yang terkait dengan perdagangan itu (Prinsip OHCHR 7; ACTIP, Pasal 14; ILO P29, Pasal 4(2)).') + '</li>' +
        '<li>' + L('<b>Restitution</b> from the trafficker for lost income, suffering, medical and other costs (UU 21/2007, Art. 48). LPSK can help you claim it and can protect you and witnesses (UU 31/2014).', '<b>Restitusi</b> dari pelaku atas kehilangan penghasilan, penderitaan, biaya pengobatan, dan biaya lain (UU 21/2007, Pasal 48). LPSK bisa membantu mengajukannya dan bisa melindungi Anda serta saksi (UU 31/2014).') + '</li>' +
        '<li>' + L('<b>Health and social rehabilitation, return and reintegration</b> (UU 21/2007, Art. 51), <b>a confidential identity</b> (Art. 44) and <b>police protection</b> against threats (Art. 47).', '<b>Rehabilitasi kesehatan dan sosial, pemulangan, dan reintegrasi</b> (UU 21/2007, Pasal 51), <b>kerahasiaan identitas</b> (Pasal 44), dan <b>pelindungan polisi</b> dari ancaman (Pasal 47).') + '</li>' +
        (R.abroad ? '<li>' + L('<b>In the destination country</b>: housing, medical and legal help, a chance to stay, and a safe return (Palermo Protocol, Arts. 6–8). Unpaid wages can usually still be claimed.', '<b>Di negara tujuan</b>: tempat tinggal, bantuan medis dan hukum, kesempatan untuk tinggal, dan pemulangan yang aman (Protokol Palermo, Pasal 6–8). Upah yang tidak dibayar biasanya tetap bisa dituntut.') + '</li>' : '') +
        (R.woman || has('purpose', 'sex') || has('purpose', 'marriage') ? '<li>' + L('<b>TPKS rights</b>: handling, protection, recovery and restitution for victims of sexual violence (UU 12/2022).', '<b>Hak menurut UU TPKS</b>: penanganan, pelindungan, pemulihan, dan restitusi bagi korban kekerasan seksual (UU 12/2022).') + '</li>' : '') +
        '<li>' + L('<b>Beyond national courts</b>: some cases can go to UN treaty bodies or other international procedures. The Legal Clinic shows which ones are open.', '<b>Di luar pengadilan nasional</b>: sebagian perkara bisa dibawa ke badan traktat PBB atau prosedur internasional lain. Klinik Hukum menunjukkan mana yang terbuka.') + '</li></ul></section>';
      n++;
    }

    // 8. Similar decisions
    var cs = pickCases(R);
    if (cs.length) {
      h += '<section><p class="tc-eye">' + L(n + ' · Similar decisions', n + ' · Putusan serupa') + '</p><p class="tc-lead">' + L('Decisions from the Court Decisions collection that dealt with similar facts. Asia, Africa, the Middle East and Latin America come first. A decision in another country does not bind courts in Indonesia, but it shows how judges have reasoned.', 'Putusan dari koleksi Putusan Pengadilan yang menangani fakta serupa. Asia, Afrika, Timur Tengah, dan Amerika Latin didahulukan. Putusan di negara lain tidak mengikat pengadilan di Indonesia, tetapi menunjukkan cara hakim bernalar.') + '</p><ol class="tc-cases">';
      cs.forEach(function (id) {
        var d = TC.CD[id];
        h += '<li><a href="/court-decisions/d/' + id + '/"><b>' + d.n + '</b></a><br><span class="tc-small">' + d.c + ', ' + d.y + ' · ' + T(TIER[d.tier] || TIER.national) + ' · ' + T(OUT[d.out] || OUT.unknown) +
          (d.st === 'C' ? ' · ' + L('candidate, not yet summarized', 'kandidat, belum diringkas') : ' · <a href="/ai-use/#composition">' + L('summary unverified', 'ringkasan belum diverifikasi') + '</a>') + '</span>' +
          (d.p ? '<br>' + T({ en: d.p, id: d.pi || d.p }) : '') + '</li>';
      });
      h += '</ol><p class="tc-small">' + L('No Indonesian trafficking conviction is in the collection yet; we are adding them.', 'Belum ada putusan pemidanaan perdagangan orang dari Indonesia dalam koleksi; kami sedang menambahkannya.') + ' <a href="/court-decisions/">' + L('Open Court Decisions', 'Buka Putusan Pengadilan') + '</a></p></section>';
      n++;
    }

    // 9. Standards cited
    var groups = [['intl', 'International law and UN bodies', 'Hukum internasional dan badan PBB'], ['asean', 'ASEAN', 'ASEAN'], ['id', 'Indonesian law', 'Hukum Indonesia']];
    h += '<section><p class="tc-eye">' + L(n + ' · Legal standards behind this sheet', n + ' · Standar hukum di balik lembar ini') + '</p>';
    groups.forEach(function (g) {
      var ks = R.refs.filter(function (k) { return TC.REF[k].g === g[0]; });
      if (ks.length) h += '<h4>' + L(g[1], g[2]) + '</h4><ul class="tc-refs">' + ks.map(refLine).join('') + '</ul>';
    });
    h += '<p class="tc-small">' + L('“Being checked”: the article reference is still being compared with the official text.', '“Sedang diperiksa”: rujukan pasal masih dibandingkan dengan naskah resmi.') + '</p></section>'; n++;

    // 10. Next steps
    h += '<section class="tc-next"><p class="tc-eye">' + L(n + ' · What you can do now', n + ' · Apa yang bisa Anda lakukan sekarang') + '</p><ol class="tc-list">' +
      '<li>' + L('If you or someone else is in danger, contact the local police or the nearest Indonesian embassy or consulate.', 'Bila Anda atau orang lain dalam bahaya, hubungi polisi setempat atau KBRI/KJRI terdekat.') + '</li>' +
      '<li>' + L('Keep any proof safely: contracts, messages, photos of documents, pay slips, names and addresses of the agent and employer.', 'Simpan bukti dengan aman: kontrak, pesan, foto dokumen, slip gaji, nama dan alamat agen serta majikan.') + '</li>' +
      '<li>' + L('Show this sheet to a lawyer or a legal aid group. <a href="/legal-help/">Find free legal help</a> near you.', 'Tunjukkan lembar ini kepada pengacara atau lembaga bantuan hukum. <a href="/legal-help/">Cari bantuan hukum gratis</a> di dekat Anda.') + '</li>' +
      '<li>' + L('To take the case to an international body, <a href="/legal-clinic/">prepare a rights communication</a> with the Legal Clinic.', 'Untuk membawa perkara ke badan internasional, <a href="/legal-clinic/">siapkan pengaduan hak</a> bersama Klinik Hukum.') + '</li>' +
      '</ol></section>';

    // 11. Answers
    h += '<section><p class="tc-eye">' + L((n + 1) + ' · Your answers', (n + 1) + ' · Jawaban Anda') + '</p><dl class="tc-ans">';
    steps().forEach(function (s) {
      var v = A[s.id]; if (!v) return; v = [].concat(v);
      h += '<dt>' + T(s.q) + '</dt><dd>' + v.map(function (k) { var o = s.o.filter(function (x) { return x.k === k; })[0]; return o ? T(o) : k; }).join('; ') + '</dd>';
    });
    h += '</dl></section>';
    h += '<footer class="tc-sf"><p>' + L('How this works: a fixed set of rules applies the Palermo Protocol test (act, means, purpose; no means for a child) and the ILO forced-labor test to your answers, then adds Indonesian law and the law of the destination country. It is not artificial intelligence and does not guess. <a href="#method">Read the method</a>. Not legal advice.',
      'Cara kerjanya: seperangkat aturan tetap menerapkan uji Protokol Palermo (perbuatan, cara, tujuan; tanpa cara untuk anak) dan uji kerja paksa ILO pada jawaban Anda, lalu menambahkan hukum Indonesia dan hukum negara tujuan. Ini bukan kecerdasan buatan dan tidak menebak. <a href="#method">Baca metodenya</a>. Bukan nasihat hukum.') +
      '<br>theimr.org/legal-clinic/trafficking-check/ · ' + L('Court Decisions data ', 'Data Putusan Pengadilan ') + TC.CDV + '</p></footer>';
    h += '</article><div class="tc-nav tc-sheetnav">' +
      '<button type="button" class="tc-go" id="tc-print">' + ico('doc') + L('Print or save as PDF', 'Cetak atau simpan sebagai PDF') + '</button>' +
      '<button type="button" class="tc-back" id="tc-dl">' + ico('passport') + L('Download the sheet', 'Unduh lembar hasil') + '</button>' +
      '<button type="button" class="tc-back" id="tc-edit">← ' + L('Change answers', 'Ubah jawaban') + '</button>' +
      '<button type="button" class="tc-back" id="tc-new">' + L('Start again', 'Mulai lagi') + '</button></div>';
    root.innerHTML = h;
    $('#tc-print').onclick = function () { count('print', 'Result sheet printed'); window.print(); };
    $('#tc-dl').onclick = function () { count('download', 'Result sheet downloaded'); download(); };
    $('#tc-edit').onclick = function () { pos = steps().length - 1; show(); };
    $('#tc-new').onclick = function () { A = {}; intro(); };
    root.scrollIntoView({ block: 'start', behavior: 'smooth' });
  }

  function download() {
    var c = $('#tc-sheet').cloneNode(true), l = lang();
    c.querySelectorAll(l === 'id' ? '.en' : '.id').forEach(function (x) { x.remove(); });
    c.querySelectorAll('a[href^="/"]').forEach(function (a) { a.href = 'https://theimr.org' + a.getAttribute('href'); });
    c.querySelectorAll('a[href^="#"]').forEach(function (a) { a.href = 'https://theimr.org/legal-clinic/trafficking-check/' + a.getAttribute('href'); });
    var css = $('#tc-css').textContent;
    var html = '<!doctype html><html lang="' + l + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>' +
      (l === 'id' ? 'Lembar hasil' : 'Result sheet') + ' · IMR</title><style>body{margin:0;padding:24px;background:#fff;color:#172D24;font:17px/1.6 system-ui,sans-serif}' + css + '</style></head><body>' + c.outerHTML + '</body></html>';
    var b = new Blob([html], { type: 'text/html' }), a = document.createElement('a');
    a.href = URL.createObjectURL(b); a.download = 'imr-trafficking-check-' + new Date().toISOString().slice(0, 10) + '.html';
    document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-say]'); if (b) speak(visibleText(b.closest('.tc-card')));
    if (e.target.closest('#tc-exit')) { try { speechSynthesis.cancel(); } catch (x) {} A = {}; root.innerHTML = ''; location.replace('https://www.google.com/'); }
  });
  intro();
})();
