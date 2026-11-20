/* Ask IMR (Tanya IMR): a question box on the Legal Clinic page.
   It does not use an AI model and sends nothing to any outside service. It reads the visitor's
   question in the browser, picks out a country and a topic, and shows the matching records from
   the IMR databases with their sources (index built by build/growth-pages/build_ask_index.py).
   Only the country code and topic are counted in GoatCounter, never the question itself.
   Everything shown is legal information from the databases, not legal advice. */
(function () {
  var box = document.getElementById('ask-imr');
  if (!box) return;
  var BASE = '/legal-clinic/ask/';
  var INDEX = null, CACHE = {}, LAST = null;

  var T = {
    en: {
      eyebrow: 'Ask IMR', title: 'Ask a question about your rights',
      sub: 'Write in your own words, for example the country where you work and what happened. The answer comes from the IMR databases, with links to the sources.',
      ph: 'Example: my salary has not been paid in Malaysia', ask: 'Ask', tryq: 'Try:',
      examples: ['What are my rights in Malaysia?', 'My wages are not paid in Hong Kong', 'My employer keeps my passport in Saudi Arabia', 'Can I change employer in Taiwan?', 'Agency fees for work in South Korea'],
      note: 'This is general legal information from our databases, not legal advice. Laws change: check the official source. For your own case, contact free legal help below or prepare a rights communication.',
      which: 'Which country do you mean? Tap one:', more: 'More countries', understood: 'Your question is about', anyTopic: 'all topics',
      changeTopic: 'Narrow it down:', loading: 'Looking in the databases…', failed: 'The databases could not be loaded. Check your connection and try again.',
      rules: 'What the law says', laws: 'Laws and regulations', decisions: 'Court decisions', help: 'Free legal help', next: 'What you can do next',
      showAll: 'Show all', details: 'Details (in English)', source: 'Source', official: 'Official text', page: 'See the database page',
      checked: 'Checked against the official text', notChecked: 'Not yet checked against the official text',
      won: 'The worker won', lost: 'The worker lost', advisory: 'Advisory opinion', unknown: 'Outcome not yet coded',
      unverified: 'Summary not yet verified', readDecision: 'Read the decision summary',
      none: 'We have no records on this topic for this country yet. Here is what we have for the country in general.',
      noneAtAll: 'We do not have records for this country yet. Free legal help that works across borders:',
      wiz: 'Prepare a rights communication with the Clinic', finder: 'All free legal help on the map', works: 'What works where (arguments courts accepted)',
      call: 'Call', site: 'Website', origin: 'country of origin',
      topics: {wage: 'Wages', hours: 'Hours and rest', passport: 'Passport and documents', fees: 'Recruitment and fees', employer: 'Changing or losing a job',
        violence: 'Violence and abuse', trafficking: 'Trafficking and forced labor', status: 'Visa, arrest and deportation', union: 'Unions', health: 'Injury, sickness and insurance',
        complain: 'Complaints and legal help', family: 'Family', housing: 'Housing', domestic: 'Domestic work', farm: 'Farm and plantation work', fishing: 'Fishing and sea work',
        'return': 'Going home', equality: 'Equal treatment', coverage: 'Coverage by labor law'}
    },
    id: {
      eyebrow: 'Tanya IMR', title: 'Tanyakan hak anda',
      sub: 'Tulis dengan kata-kata anda sendiri, misalnya negara tempat anda bekerja dan apa yang terjadi. Jawaban diambil dari basis data IMR, lengkap dengan tautan ke sumbernya.',
      ph: 'Contoh: gaji saya tidak dibayar di Malaysia', ask: 'Tanya', tryq: 'Coba:',
      examples: ['Apa hak saya di Malaysia?', 'Gaji saya tidak dibayar di Hong Kong', 'Paspor saya ditahan majikan di Arab Saudi', 'Bolehkah saya pindah majikan di Taiwan?', 'Biaya agen untuk kerja di Korea Selatan'],
      note: 'Ini merupakan informasi hukum umum dari basis data kami, bukan nasihat hukum. Hukum dapat berubah, sehingga periksalah sumber resminya. Untuk kasus anda sendiri, hubungi bantuan hukum gratis di bawah atau siapkan pengaduan hak.',
      which: 'Negara mana yang anda maksud? Pilih salah satu:', more: 'Negara lain', understood: 'Pertanyaan anda tentang', anyTopic: 'semua topik',
      changeTopic: 'Persempit topiknya:', loading: 'Sedang mencari di basis data…', failed: 'Basis data tidak dapat dimuat. Periksa sambungan internet anda lalu coba lagi.',
      rules: 'Apa kata aturannya', laws: 'Undang-undang dan peraturan', decisions: 'Putusan pengadilan', help: 'Bantuan hukum gratis', next: 'Langkah yang dapat anda ambil',
      showAll: 'Tampilkan semua', details: 'Rincian (bahasa Inggris)', source: 'Sumber', official: 'Teks resmi', page: 'Lihat halaman basis datanya',
      checked: 'Sudah diperiksa pada teks resmi', notChecked: 'Belum diperiksa pada teks resmi',
      won: 'Pekerja menang', lost: 'Pekerja kalah', advisory: 'Pendapat hukum (advisory)', unknown: 'Hasil putusan belum dikodekan',
      unverified: 'Ringkasan belum diverifikasi', readDecision: 'Baca ringkasan putusannya',
      none: 'Kami belum memiliki catatan tentang topik ini untuk negara tersebut. Berikut catatan umum yang kami miliki untuk negara itu.',
      noneAtAll: 'Kami belum memiliki catatan untuk negara ini. Bantuan hukum gratis yang bekerja lintas negara:',
      wiz: 'Siapkan pengaduan hak bersama Klinik', finder: 'Semua bantuan hukum gratis di peta', works: 'Apa yang berhasil di mana (argumen yang diterima pengadilan)',
      call: 'Telepon', site: 'Situs web', origin: 'negara asal',
      topics: {wage: 'Gaji dan upah', hours: 'Jam kerja dan libur', passport: 'Paspor dan dokumen', fees: 'Perekrutan dan biaya', employer: 'Pindah atau kehilangan pekerjaan',
        violence: 'Kekerasan dan penganiayaan', trafficking: 'Perdagangan orang dan kerja paksa', status: 'Visa, penangkapan dan deportasi', union: 'Serikat pekerja', health: 'Kecelakaan, sakit dan asuransi',
        complain: 'Pengaduan dan bantuan hukum', family: 'Keluarga', housing: 'Tempat tinggal', domestic: 'Pekerja rumah tangga', farm: 'Pertanian dan perkebunan', fishing: 'Perikanan dan kerja di kapal',
        'return': 'Pulang ke tanah air', equality: 'Perlakuan yang setara', coverage: 'Cakupan hukum ketenagakerjaan'}
    }
  };

  // Words people use for each topic, in Indonesian and English (lower case, matched as word starts).
  var TOPIC_WORDS = {
    wage: 'gaji upah dibayar bayaran digaji gajian lembur potong potongan salary wage wages pay paid unpaid overtime',
    hours: 'jam libur istirahat cuti hari minggu hours rest day off leave holiday',
    passport: 'paspor dokumen ktp identitas passport document documents',
    fees: 'biaya agen agensi calo sponsor pt p3mi utang hutang perekrut perekrutan penempatan kontrak fee fees agent agency recruiter recruitment debt contract broker',
    employer: 'pindah ganti majikan kabur dipecat phk berhenti putus change employer abscond runaway fired dismissed terminated quit',
    violence: 'kekerasan dipukul pukul disiksa siksa pelecehan diperkosa perkosaan dianiaya aniaya ancam diancam violence abuse abused beaten harassment rape assault threat',
    trafficking: 'perdagangan tppo trafficking trafficked dijual kerja paksa paksa forced',
    status: 'visa izin ditangkap tangkap razia deportasi dideportasi dipenjara penjara ilegal overstay imigrasi tahanan detention detained arrest arrested deport deported deportation immigration permit undocumented illegal jail prison',
    union: 'serikat organisasi union unions organize',
    health: 'sakit kecelakaan cedera luka asuransi bpjs jaminan meninggal wafat kematian hamil sick injury injured accident insurance died death pregnant medical',
    complain: 'mengadu adu pengaduan lapor melapor laporan pengadilan hakim pengacara advokat gugat gugatan complain complaint report court lawyer judge sue claim',
    family: 'keluarga anak istri suami family child children spouse wife husband',
    housing: 'tempat tinggal asrama mes kamar housing dormitory accommodation room',
    domestic: 'prt pembantu art pekerja rumah tangga majikan perempuan domestic maid helper housemaid',
    farm: 'kebun perkebunan sawit pertanian ladang tani petani farm plantation agriculture palm',
    fishing: 'nelayan kapal abk ikan laut pelaut fishing fisher fishermen vessel ship crew seafarer',
    'return': 'pulang kepulangan purna kembali return returned home',
    equality: 'diskriminasi setara sama rata discrimination equal equality'
  };
  // Some topics only make sense together, for example "pindah majikan" should not also mean domestic work.
  var PHRASES = [[/pindah majikan|ganti majikan|change (my )?employer/, 'employer'], [/rumah tangga|domestic work/, 'domestic'], [/kerja paksa|forced labou?r/, 'trafficking'], [/tempat tinggal/, 'housing']];

  function lang() {
    var l = (document.documentElement.lang || 'en').slice(0, 2);
    return l === 'id' ? 'id' : 'en';
  }
  function t(k) { return T[lang()][k]; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]; }); }
  function norm(s) { return ' ' + String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, ' ').trim() + ' '; }
  function count(path) { try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({path: path, title: path, event: true}); } catch (e) {} }

  function loadIndex() {
    if (INDEX) return Promise.resolve(INDEX);
    return fetch(BASE + 'ask-index.json').then(function (r) { if (!r.ok) throw r; return r.json(); }).then(function (j) { INDEX = j; return j; });
  }
  function loadCountry(c) {
    if (CACHE[c]) return Promise.resolve(CACHE[c]);
    return fetch(BASE + 'c/' + c + '.json').then(function (r) { if (!r.ok) throw r; return r.json(); }).then(function (j) { CACHE[c] = j; return j; });
  }

  function findCountry(q) {
    var n = norm(q), hits = [];
    Object.keys(INDEX.countries).forEach(function (c) {
      var co = INDEX.countries[c];
      var names = (co.a + ' ' + co.en + ' ' + co.id).toLowerCase().split(/\s{2,}|,/).join(' ');
      // aliases are space-separated; multi-word names are tried whole first
      var cand = [co.en.toLowerCase(), co.id.toLowerCase()].concat(co.a.split(' '));
      cand.forEach(function (w) {
        w = norm(w).trim(); if (w.length < 2) return;
        var i = n.indexOf(' ' + w + ' ');
        if (i >= 0) hits.push({c: c, i: i, len: w.length});
      });
    });
    if (!hits.length) return null;
    // Prefer a destination over Indonesia when both are named ("orang Indonesia di Malaysia").
    var other = hits.filter(function (h) { return h.c !== 'ID'; });
    var pool = other.length ? other : hits;
    pool.sort(function (a, b) { return a.i - b.i || b.len - a.len; });
    return pool[0].c;
  }
  function findTopics(q) {
    var n = norm(q), found = {};
    PHRASES.forEach(function (p) { if (p[0].test(n)) found[p[1]] = 3; });
    Object.keys(TOPIC_WORDS).forEach(function (k) {
      TOPIC_WORDS[k].split(' ').forEach(function (w) { if (w && n.indexOf(' ' + w) >= 0) found[k] = (found[k] || 0) + 1; });
    });
    if (found.employer && /majikan/.test(n) && !/rumah tangga|prt|pembantu/.test(n)) delete found.domestic;
    return Object.keys(found).sort(function (a, b) { return found[b] - found[a]; });
  }
  function words(q) { return norm(q).trim().split(' ').filter(function (w) { return w.length > 3; }); }
  function score(rec, topics, ws, text) {
    var s = 0, tg = rec.t || [];
    topics.forEach(function (tp, i) { if (tg.indexOf(tp) >= 0) s += i === 0 ? 10 : 5; });
    var low = norm(text);
    ws.forEach(function (w) { if (low.indexOf(' ' + w) >= 0) s += 1; });
    return s;
  }

  // ---------- rendering ----------
  function chip(label, attrs, on) { return '<button type="button" class="ai-chip' + (on ? ' on' : '') + '" ' + attrs + '>' + esc(label) + '</button>'; }
  function list(id, items, render, limit) {
    if (!items.length) return '';
    var head = items.slice(0, limit).map(render).join('');
    var rest = items.length > limit ? '<div class="ai-rest" hidden>' + items.slice(limit).map(render).join('') + '</div><button type="button" class="ai-all" data-all>' + esc(t('showAll')) + ' (' + items.length + ')</button>' : '';
    return '<h4 class="ai-h">' + esc(t(id)) + ' <span>' + items.length + '</span></h4><div class="ai-list">' + head + rest + '</div>';
  }
  function linkify(s) {
    return esc(s).replace(/https?:\/\/[^\s;,)]+/g, function (u) { return '<a href="' + u + '" target="_blank" rel="noopener">' + esc(t('official')) + ' ↗</a>'; });
  }
  function rRule(r) {
    var L = lang(), g = L === 'id' && r.gi ? r.gi : r.g;
    var f = L === 'id' && r.fi ? r.fi : r.f, v = L === 'id' && r.vi ? r.vi : r.v;
    var ev = r.e === 'P' ? '<span class="ai-ok">' + esc(t('checked')) + '</span>' : '<span class="ai-warn">' + esc(t('notChecked')) + '</span>';
    return '<article class="ai-card"><p class="ai-k">' + esc(g) + '</p><p class="ai-t"><b>' + esc(f) + ':</b> ' + esc(v) + '</p>' +
      '<details><summary>' + esc(t('details')) + '</summary><p>' + esc(r.n) + '</p><p class="ai-src">' + esc(t('source')) + ': ' + linkify(r.s) + '</p></details>' +
      '<p class="ai-m">' + ev + ' · <a href="' + esc(r.p) + '">' + esc(t('page')) + ' →</a></p></article>';
  }
  function rLaw(r) {
    var u = r.u ? '<a href="' + esc(r.u) + '" target="_blank" rel="noopener">' + esc(t('official')) + ' ↗</a> · ' : '';
    return '<article class="ai-card"><p class="ai-t"><b>' + esc(r.ti) + '</b>' + (r.y ? ' (' + esc(r.y) + ')' : '') + '</p>' +
      (r.or_ && r.or_ !== r.ti ? '<p class="ai-k">' + esc(r.or_) + '</p>' : '') + (r.tp ? '<p class="ai-d">' + esc(r.tp) + '</p>' : '') +
      '<p class="ai-m">' + u + '<a href="' + esc(r.p) + '">' + esc(t('page')) + ' →</a></p></article>';
  }
  function rDec(r) {
    var L = lang(), txt = L === 'id' ? (r.pi || r.pe) : (r.pe || r.pi);
    var oc = '<span class="ai-oc ai-' + esc(r.oc) + '">' + esc(t(r.oc) || r.oc) + '</span>';
    return '<article class="ai-card"><p class="ai-t"><b>' + esc(r.nm) + '</b></p><p class="ai-k">' + esc(r.ct) + (r.d ? ', ' + esc(r.d) : '') + '</p>' +
      (txt ? '<p class="ai-d">' + esc(txt) + '</p>' : '') +
      '<p class="ai-m">' + oc + (r.st !== 'P' ? ' · <span class="ai-warn">' + esc(t('unverified')) + '</span>' : '') +
      ' · <a href="/court-decisions/d/' + esc(r.id) + '/">' + esc(t('readDecision')) + ' →</a></p></article>';
  }
  function rHelp(r) {
    var L = lang(), d = L === 'id' ? (r.di || r.de) : (r.de || r.di);
    var tel = (r.tel || []).map(function (x) { return '<a class="ai-tel" href="tel:' + esc(x.replace(/[^+0-9]/g, '')) + '">' + esc(t('call')) + ' ' + esc(x) + '</a>'; }).join(' ');
    return '<article class="ai-card"><p class="ai-t"><b>' + esc(r.nm) + '</b></p>' + (r.city ? '<p class="ai-k">' + esc(r.city) + '</p>' : '') +
      (d ? '<p class="ai-d">' + esc(d) + '</p>' : '') + '<p class="ai-m">' + tel + (r.web ? ' <a href="' + esc(r.web) + '" target="_blank" rel="noopener">' + esc(t('site')) + ' ↗</a>' : '') + '</p></article>';
  }
  function nextSteps() {
    return '<h4 class="ai-h">' + esc(t('next')) + '</h4><p class="ai-next"><a href="#wiz">' + esc(t('wiz')) + ' →</a><a href="/legal-help/">' + esc(t('finder')) + ' →</a><a href="/legal-clinic/what-works/">' + esc(t('works')) + ' →</a></p>';
  }

  function rank(items, topics, ws, textOf, extra) {
    return items.map(function (r) { return {r: r, s: score(r, topics, ws, textOf(r)) + (extra ? extra(r) : 0)}; })
      .filter(function (x) { return !topics.length || x.s >= 5; })
      .sort(function (a, b) { return b.s - a.s; }).map(function (x) { return x.r; });
  }

  function answer(q, forceCountry, forceTopic) {
    var out = box.querySelector('.ai-out');
    out.innerHTML = '<p class="ai-wait">' + esc(t('loading')) + '</p>';
    loadIndex().then(function () {
      var c = forceCountry || findCountry(q);
      var topics = forceTopic === '' ? [] : forceTopic ? [forceTopic] : findTopics(q);
      LAST = {q: q, c: c, topic: forceTopic};
      if (!c) { return showCountryPicker(out, topics); }
      count('event/ask/' + c + '/' + (topics[0] || 'general'));
      return loadCountry(c).then(function (data) { render(out, q, c, topics, data); });
    }).catch(function () { out.innerHTML = '<p class="ai-wait">' + esc(t('failed')) + '</p>'; });
  }

  function showCountryPicker(out, topics) {
    var main = ['MY', 'SG', 'HK', 'TW', 'KR', 'JP', 'SA', 'AE', 'QA', 'KW', 'BN', 'TH', 'ID'];
    var L = lang(), cs = INDEX.countries;
    var btn = function (c) { return cs[c] ? chip(cs[c][L], 'data-c="' + c + '"') : ''; };
    var others = Object.keys(cs).filter(function (c) { return main.indexOf(c) < 0; }).sort(function (a, b) { return cs[a][L].localeCompare(cs[b][L]); });
    out.innerHTML = '<p class="ai-q">' + esc(t('which')) + '</p><div class="ai-chips">' + main.map(btn).join('') + '</div>' +
      '<details class="ai-more"><summary>' + esc(t('more')) + '</summary><div class="ai-chips">' + others.map(btn).join('') + '</div></details>';
    out.dataset.topics = topics.join(',');
  }

  function render(out, q, c, topics, data) {
    var L = lang(), co = INDEX.countries[c], ws = words(q);
    var cname = norm(co.en + ' ' + co.id + ' ' + co.a).trim().split(' ');
    ws = ws.filter(function (w) { return cname.indexOf(w) < 0; });
    var rules = rank(data.rules, topics, ws, function (r) { return r.g + ' ' + r.f + ' ' + r.fi + ' ' + r.n; }, function (r) { return r.e === 'P' ? 0.5 : 0; });
    var laws = rank(data.laws, topics, ws, function (r) { return r.ti + ' ' + r.tp; });
    var decs = rank(data.decisions, topics, ws, function (r) { return r.nm + ' ' + r.pe + ' ' + r.pi; },
      function (r) { return (r.oc === 'won' || r.oc === 'lost' ? 1 : 0) + (r.pe ? 0.5 : 0) + (parseInt(r.d, 10) || 0) / 10000; });
    var help = data.help.concat(INDEX.cross || []);
    var narrowed = topics.length > 0;
    var empty = narrowed && !rules.length && !laws.length && !decs.length;
    if (empty) {
      rules = rank(data.rules, [], ws, function (r) { return r.f; });
      laws = data.laws.slice(); decs = rank(data.decisions, [], [], function () { return ''; }, function (r) { return (r.pe ? 1 : 0) + (r.oc === 'won' ? 1 : 0); });
    }
    // topic chips available for this country
    var avail = {};
    data.rules.concat(data.laws, data.decisions).forEach(function (r) { (r.t || []).forEach(function (x) { avail[x] = (avail[x] || 0) + 1; }); });
    var tchips = chip(t('anyTopic'), 'data-t=""', !narrowed) + Object.keys(T[L].topics).filter(function (k) { return avail[k]; })
      .map(function (k) { return chip(T[L].topics[k], 'data-t="' + k + '"', topics[0] === k); }).join('');
    var head = '<p class="ai-q">' + esc(t('understood')) + ' <b>' + esc(co[L]) + '</b> · <b>' + esc(narrowed ? T[L].topics[topics[0]] || topics[0] : t('anyTopic')) + '</b></p>' +
      '<details class="ai-more"' + (narrowed ? '' : ' open') + '><summary>' + esc(t('changeTopic')) + '</summary><div class="ai-chips" data-for="' + c + '">' + tchips + '</div></details>';
    var body = '';
    if (!data.rules.length && !data.laws.length && !data.decisions.length) body = '<p class="ai-none">' + esc(t('noneAtAll')) + '</p>';
    else if (empty) body = '<p class="ai-none">' + esc(t('none')) + '</p>';
    body += list('rules', rules, rRule, 3) + list('laws', laws, rLaw, 3) + list('decisions', decs, rDec, 3) + list('help', help, rHelp, 3) + nextSteps();
    out.innerHTML = head + body;
    out.dataset.c = c;
  }

  // ---------- page shell ----------
  function shell() {
    var L = lang();
    box.innerHTML =
      '<div class="ai-in"><p class="ai-eb">' + esc(t('eyebrow')) + '</p><h2 id="ai-h2">' + esc(t('title')) + '</h2><p class="ai-sub">' + esc(t('sub')) + '</p>' +
      '<form class="ai-form" role="search"><label class="ai-sr" for="ai-q">' + esc(t('title')) + '</label><input id="ai-q" type="search" autocomplete="off" enterkeyhint="search" placeholder="' + esc(t('ph')) + '">' +
      '<button type="submit">' + esc(t('ask')) + '</button></form>' +
      '<p class="ai-try">' + esc(t('tryq')) + '</p><div class="ai-chips ai-ex">' + T[L].examples.map(function (e) { return chip(e, 'data-q="' + esc(e) + '"'); }).join('') + '</div>' +
      '<p class="ai-note">' + esc(t('note')) + '</p><div class="ai-out" aria-live="polite"></div></div>';
  }
  shell();
  box.addEventListener('submit', function (e) {
    e.preventDefault();
    var q = box.querySelector('#ai-q').value.trim(); if (q) answer(q);
  });
  box.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    if (b.hasAttribute('data-q')) { box.querySelector('#ai-q').value = b.dataset.q; answer(b.dataset.q); }
    else if (b.hasAttribute('data-c')) { var out = box.querySelector('.ai-out'); var tp = (out.dataset.topics || '').split(',')[0]; answer(LAST ? LAST.q : '', b.dataset.c, tp || ''); }
    else if (b.hasAttribute('data-t')) { answer(LAST ? LAST.q : '', b.closest('[data-for]').dataset.for, b.dataset.t); }
    else if (b.hasAttribute('data-all')) { var r = b.previousElementSibling; r.hidden = false; b.remove(); }
  });
  // Follow the page language (the Clinic's own buttons or the site switch change <html lang>).
  var cur = lang();
  new MutationObserver(function () {
    if (lang() === cur) return; cur = lang();
    var q = box.querySelector('#ai-q').value; shell(); box.querySelector('#ai-q').value = q;
    if (LAST) answer(LAST.q, LAST.c, LAST.topic);
  }).observe(document.documentElement, {attributes: true, attributeFilter: ['lang']});
})();
