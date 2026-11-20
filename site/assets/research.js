/* Research tools without accounts: saved searches and a reading list, kept only in this browser (localStorage).
   Nothing is sent to IMR or anyone else. People move their list between devices with a file or a link.

   On a court decision page (/court-decisions/d/<id>/) it adds an "Add to reading list" button under the title.
   On the database pages it adds a small "Save this search" bar that stores the page address with its filters.
   /research/ shows both lists and exports them (BibTeX, RIS, CSV, JSON).
   window.IMRResearch is the small API the /research/ page uses. */
(function () {
  var KEY = 'imr-research-v1';
  var DB_PAGES = /^\/(court-decisions|migration-law|gcc|east-asia|southeast-asia|countries-of-origin|domestic-workers|government-hate-speech|ratifications|legal-clinic\/what-works)\//;

  function load() {
    try { var d = JSON.parse(localStorage.getItem(KEY) || '{}'); return {searches: d.searches || [], items: d.items || []}; }
    catch (e) { return {searches: [], items: []}; }
  }
  function save(d) {
    try { localStorage.setItem(KEY, JSON.stringify(d)); return true; } catch (e) { return false; }
  }
  function available() { try { localStorage.setItem(KEY + '-t', '1'); localStorage.removeItem(KEY + '-t'); return true; } catch (e) { return false; } }
  function id() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 6); }
  function L() { var l = document.documentElement.lang; if (l === 'id') return 'id'; try { return localStorage.getItem('imr-lang') === 'id' ? 'id' : 'en'; } catch (e) { return 'en'; } }
  var T = {
    en: {add: '+ Add to reading list', added: '✓ In your reading list', saveS: '☆ Save this search', savedS: '★ Search saved', open: 'My reading list',
      toastAdd: 'Added to your reading list (kept in this browser only)', toastS: 'Search saved (kept in this browser only)', full: 'Could not save: this browser blocks storage.'},
    id: {add: '+ Tambahkan ke daftar bacaan', added: '✓ Ada di daftar bacaan anda', saveS: '☆ Simpan pencarian ini', savedS: '★ Pencarian tersimpan', open: 'Daftar bacaan saya',
      toastAdd: 'Ditambahkan ke daftar bacaan (hanya tersimpan di peramban ini)', toastS: 'Pencarian tersimpan (hanya di peramban ini)', full: 'Tidak bisa menyimpan: peramban ini memblokir penyimpanan.'}
  };
  function toast(m) {
    var t = document.createElement('div'); t.setAttribute('role', 'status'); t.setAttribute('data-noi18n', '');
    t.style.cssText = 'position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:#172D24;color:#fff;padding:10px 16px;border-radius:4px;font:15px/1.4 Figtree,system-ui,sans-serif;z-index:90;max-width:90vw';
    t.textContent = m; document.body.appendChild(t); setTimeout(function () { t.remove(); }, 2800);
  }

  var API = {
    data: load,
    hasItem: function (key) { return load().items.some(function (i) { return i.key === key; }); },
    addItem: function (it) { var d = load(); if (d.items.some(function (i) { return i.key === it.key; })) return true; it.added = new Date().toISOString().slice(0, 10); d.items.push(it); return save(d); },
    removeItem: function (key) { var d = load(); d.items = d.items.filter(function (i) { return i.key !== key; }); return save(d); },
    setNote: function (key, note) { var d = load(); d.items.forEach(function (i) { if (i.key === key) i.note = note; }); return save(d); },
    hasSearch: function (url) { return load().searches.some(function (s) { return s.url === url; }); },
    addSearch: function (title, url) { var d = load(); if (d.searches.some(function (s) { return s.url === url; })) return true; d.searches.push({id: id(), title: title, url: url, saved: new Date().toISOString().slice(0, 10)}); return save(d); },
    renameSearch: function (sid, title) { var d = load(); d.searches.forEach(function (s) { if (s.id === sid) s.title = title; }); return save(d); },
    removeSearch: function (sid) { var d = load(); d.searches = d.searches.filter(function (s) { return s.id !== sid; }); return save(d); },
    replace: function (d) { return save({searches: d.searches || [], items: d.items || []}); },
    merge: function (d) {
      var cur = load();
      (d.items || []).forEach(function (i) { if (i && i.key && !cur.items.some(function (x) { return x.key === i.key; })) cur.items.push(i); });
      (d.searches || []).forEach(function (s) { if (s && s.url && !cur.searches.some(function (x) { return x.url === s.url; })) { s.id = s.id || id(); cur.searches.push(s); } });
      return save(cur);
    },
    available: available
  };
  window.IMRResearch = API;

  function decisionFromPage() {
    var m = location.pathname.match(/^\/court-decisions\/d\/([^\/]+)\/?$/); if (!m) return null;
    var h1 = document.querySelector('main h1'); if (!h1) return null;
    var p = h1.nextElementSibling, court = '', country = '', date = '', cite = '';
    if (p && p.tagName === 'P') {
      var parts = p.textContent.split('·').map(function (s) { return s.trim(); });
      court = parts[0] || ''; country = parts[1] || ''; date = parts[2] || '';
      var q = p.nextElementSibling; var cm = q && q.textContent.match(/Citation:\s*([^\n]+?)(?:Type of case:|$)/);
      if (cm) cite = cm[1].trim();
    }
    return {key: 'decision:' + m[1], type: 'decision', id: m[1], title: h1.textContent.trim(), court: court, country: country,
      date: date, citation: cite, url: 'https://theimr.org/court-decisions/d/' + m[1] + '/'};
  }

  function button(label, on) {
    var b = document.createElement('button'); b.type = 'button'; b.setAttribute('data-noi18n', '');
    b.style.cssText = 'cursor:pointer;font:600 15px/1.2 Figtree,system-ui,sans-serif;padding:8px 12px;border:1px solid #1E6B4A;border-radius:2px;margin:6px 8px 0 0;' +
      (on ? 'background:#1E6B4A;color:#fff' : 'background:#fff;color:#1E6B4A');
    b.textContent = label; return b;
  }
  function link(text) {
    var a = document.createElement('a'); a.href = '/research/'; a.textContent = text; a.setAttribute('data-noi18n', '');
    a.style.cssText = 'font:500 15px Figtree,system-ui,sans-serif;margin-left:4px'; return a;
  }

  function decisionButton() {
    var d = decisionFromPage(); if (!d) return;
    var box = document.createElement('div'); box.className = 'imr-research'; box.style.cssText = 'margin:10px 0 0';
    function draw() {
      var on = API.hasItem(d.key), t = T[L()]; box.innerHTML = '';
      var b = button(on ? t.added : t.add, on);
      b.addEventListener('click', function () {
        if (API.hasItem(d.key)) { API.removeItem(d.key); } else if (API.addItem(d)) toast(T[L()].toastAdd); else toast(T[L()].full);
        draw();
      });
      box.appendChild(b); box.appendChild(link(t.open));
    }
    draw(); document.querySelector('main h1').insertAdjacentElement('afterend', box);
    langWatch(draw);
  }

  function searchBar() {
    if (!DB_PAGES.test(location.pathname) || /^\/court-decisions\/(d|highlights)\//.test(location.pathname)) return;
    var bar = document.createElement('div'); bar.className = 'imr-research';
    bar.style.cssText = 'position:fixed;left:12px;bottom:12px;z-index:70;background:#F4F8F5;border:1px solid #B2C7BC;border-radius:4px;padding:2px 8px 8px;box-shadow:0 2px 8px rgba(0,0,0,.12);max-width:calc(100vw - 24px)';
    function title() {
      var h = (document.querySelector('main h1') || {}).textContent || document.title;
      var q = decodeURIComponent((location.search + ' ' + location.hash).replace(/[?#&=+_\/]/g, ' ')).replace(/\s+/g, ' ').trim();
      return h.trim() + (q ? ' · ' + q.slice(0, 80) : '');
    }
    function draw() {
      var t = T[L()], url = location.pathname + location.search + location.hash, on = API.hasSearch(url); bar.innerHTML = '';
      var b = button(on ? t.savedS : t.saveS, on);
      b.addEventListener('click', function () {
        var u = location.pathname + location.search + location.hash;
        if (API.hasSearch(u)) return;
        if (API.addSearch(title(), u)) toast(T[L()].toastS); else toast(T[L()].full);
        draw();
      });
      bar.appendChild(b); bar.appendChild(link(t.open));
    }
    draw(); document.body.appendChild(bar);
    window.addEventListener('hashchange', draw); window.addEventListener('popstate', draw);
    var last = location.href; setInterval(function () { if (location.href !== last) { last = location.href; draw(); } }, 1000);
    langWatch(draw);
    // Keep the bar out of the way when printing.
    var st = document.createElement('style'); st.textContent = '@media print{.imr-research{display:none!important}}'; document.head.appendChild(st);
  }
  function langWatch(fn) { new MutationObserver(fn).observe(document.documentElement, {attributes: true, attributeFilter: ['lang']}); }

  function init() { if (!available()) return; decisionButton(); searchBar(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
