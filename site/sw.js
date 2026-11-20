/* theimr.org service worker.

   What it does, in plain words:
   - Pages: try the network first. On a slow connection, if a saved copy exists and the
     network has not answered within a few seconds, show the saved copy. With no
     connection at all, show the saved copy, or a short "you are offline" page.
   - Scripts, styles, fonts and pictures from this site: show the saved copy at once and
     refresh it in the background. Files whose address carries ?v=... never change, so a
     saved copy is always right.
   - Legal Clinic: when someone opens the Clinic, the files it needs are saved, so it
     still opens and works without internet. A rights communication sent without
     internet waits on the phone (in IndexedDB, see /legal-clinic/outbox.js) and is
     sent here as soon as the phone is online again. Nothing is sent anywhere else.
   - Other websites (GoatCounter, map tiles, court portals) are never touched.

   BUILD is replaced at publish time by tools/optimize_site.py, so each publish
   installs a fresh copy and old saved files are dropped. */
var BUILD = 'dev';
var PAGES = 'imr-pages-' + BUILD;
var FILES = 'imr-files-' + BUILD;
var MARKS = 'clinic-outbox';
var MAX_PAGES = 80;
var MAX_FILES = 160;
var SLOW_MS = 4000;

var CORE = ['/offline.html'];
// The Legal Clinic is saved for offline use only once someone opens it (see 'message' below).
// Files the open Clinic page already loaded are saved as they load; this list adds the rest.
var CLINIC = ['/legal-clinic/', '/legal-clinic/i18n.js', '/legal-clinic/procedures.js', '/legal-clinic/outbox.js',
  '/legal-clinic/thanks.html', '/assets/lang.js', '/assets/editorial.css', '/assets/notebook.css', '/assets/fonts/figtree-latin.woff2'];
// Skipped when the phone asks to save data.
var CLINIC_MORE = ['/legal-clinic/how-we-work/', '/legal-clinic/after-return.html', '/assets/fonts/figtree-italic-latin.woff2'];
// Never kept: staff pages, form posts, downloads.
var NEVER = /^\/(legal-clinic\/review\.html|admin|\.netlify)|\/data\/|\.(csv|zip|pdf|bib|docx?|xlsx?)$/i;

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(FILES).then(function (c) { return c.addAll(CORE); }).catch(function () {}).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return /^imr-/.test(k) && k !== PAGES && k !== FILES; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }).then(flushOutbox));
});

self.addEventListener('message', function (e) {
  var d = e.data || {};
  if (d.type === 'save-clinic') e.waitUntil(saveList(CLINIC.concat(d.lite ? [] : CLINIC_MORE)));
  if (d.type === 'flush-outbox') e.waitUntil(flushOutbox());
});

self.addEventListener('sync', function (e) {
  if (e.tag === 'imr-clinic-outbox') e.waitUntil(flushOutbox());
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== location.origin || NEVER.test(url.pathname) || url.pathname === '/sw.js') return;
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').indexOf('text/html') >= 0) { e.respondWith(page(e, req)); return; }
  if (/\.(js|css|woff2|svg|png|jpe?g|webp|gif|ico|json)$/i.test(url.pathname)) e.respondWith(file(e, req, url));
});

// Pages: network first; saved copy if the network is down or too slow.
function page(e, req) {
  var key = pageKey(req.url);
  var net = fetch(req).then(function (res) {
    if (res && res.ok && res.type === 'basic') {
      var copy = res.clone();
      e.waitUntil(caches.open(PAGES).then(function (c) { return c.put(key, copy).then(function () { return trim(PAGES, MAX_PAGES); }); }));
      e.waitUntil(flushOutbox());
    }
    return res;
  });
  return caches.match(key, {ignoreSearch: true}).then(function (saved) {
    if (!saved) return net.catch(offline);
    var slow = new Promise(function (resolve) { setTimeout(function () { resolve(saved); }, SLOW_MS); });
    return Promise.race([net.catch(function () { return saved; }), slow]);
  });
}
function offline() {
  return caches.match('/offline.html').then(function (r) {
    return r || new Response('<!doctype html><meta charset="utf-8"><title>Offline</title><p>You are offline. / Anda sedang luring.</p>', {headers: {'Content-Type': 'text/html; charset=utf-8'}});
  });
}
// /legal-clinic/index.html, /legal-clinic/ and /legal-clinic/?lang=id are the same page.
function pageKey(u) {
  var url = new URL(u); url.search = ''; url.hash = '';
  url.pathname = url.pathname.replace(/\/index\.html$/, '/');
  return url.href;
}

// Files: versioned (?v=) ones are cache-first; others are shown from cache and refreshed.
function file(e, req, url) {
  return caches.open(FILES).then(function (c) {
    return c.match(req).then(function (saved) {
      var net = fetch(req).then(function (res) {
        if (res && res.ok && res.type === 'basic') {
          var copy = res.clone();
          e.waitUntil(c.put(req, copy).then(function () { return trim(FILES, MAX_FILES); }));
        }
        return res;
      });
      if (saved) {
        if (!url.searchParams.has('v')) e.waitUntil(net.catch(function () {}));
        return saved;
      }
      // A versioned file not saved yet: an older saved version still beats nothing when offline.
      return net.catch(function () { return c.match(req, {ignoreSearch: true}).then(function (old) { return old || Response.error(); }); });
    });
  });
}

function saveList(list) {
  return caches.open(FILES).then(function (files) {
    return caches.open(PAGES).then(function (pages) {
      return Promise.all(list.map(function (u) {
        var isPage = /\/$|\.html$/.test(new URL(u, location.origin).pathname);
        var key = isPage ? pageKey(new URL(u, location.origin).href) : u;
        // Already saved (any version)? Then do not download it again.
        return (isPage ? pages : files).match(key, {ignoreSearch: true}).then(function (have) {
          if (have) return;
          return fetch(u, {credentials: 'same-origin'}).then(function (res) {
            if (res.ok) return (isPage ? pages : files).put(key, res);
          });
        }).catch(function () {});
      }));
    });
  });
}

// Oldest saved copies go first, but the Clinic and the files it needs are always kept.
var KEEP = /\/legal-clinic\/|\/offline\.html|\/assets\/(lang\.js|editorial\.css|notebook\.css|fonts\/)/;
function trim(name, max) {
  return caches.open(name).then(function (c) {
    return c.keys().then(function (keys) {
      var old = keys.filter(function (k) { return !KEEP.test(k.url); });
      var extra = keys.length - max;
      if (extra <= 0) return;
      return Promise.all(old.slice(0, extra).map(function (k) { return c.delete(k); }));
    });
  });
}

// ---------- Legal Clinic outbox (same database as /legal-clinic/outbox.js) ----------
var sending = null;
var MARK = '/__imr-outbox-waiting';  // set by outbox.js; kept in its own cache so a new publish does not drop it
function db() {
  return new Promise(function (resolve, reject) {
    var r = indexedDB.open('imr-clinic', 1);
    r.onupgradeneeded = function () {
      var d = r.result;
      if (!d.objectStoreNames.contains('outbox')) d.createObjectStore('outbox', {keyPath: 'ref'});
      if (!d.objectStoreNames.contains('sent')) d.createObjectStore('sent', {keyPath: 'ref'});
    };
    r.onsuccess = function () { resolve(r.result); };
    r.onerror = function () { reject(r.error); };
  });
}
function all(d, store) {
  return new Promise(function (resolve) {
    var q = d.transaction(store).objectStore(store).getAll();
    q.onsuccess = function () { resolve(q.result || []); };
    q.onerror = function () { resolve([]); };
  });
}
function markSent(d, ref) {
  return new Promise(function (resolve) {
    var t = d.transaction(['outbox', 'sent'], 'readwrite');
    t.objectStore('outbox').delete(ref);
    t.objectStore('sent').put({ref: ref, sentAt: Date.now()});
    t.oncomplete = t.onerror = function () { resolve(); };
  });
}
function flushOutbox() {
  if (sending) return sending;
  if (typeof indexedDB === 'undefined') return Promise.resolve();
  // Only open the database on phones where the Clinic has left something waiting.
  sending = caches.open(MARKS).then(function (c) { return c.match(MARK); }).then(function (m) { if (!m) return; return db().then(function (d) {
    return all(d, 'outbox').then(function (items) {
      return items.reduce(function (p, item) {
        return p.then(function () {
          var fd = new FormData();
          item.fields.forEach(function (f) { if (f[2]) fd.append(f[0], f[1], f[2]); else fd.append(f[0], f[1]); });
          return fetch('/', {method: 'POST', body: fd}).then(function (res) {
            if (!res.ok) return;
            return markSent(d, item.ref).then(function () { return tell({type: 'clinic-sent', ref: item.ref}); });
          }).catch(function () {});
        });
      }, Promise.resolve()).then(function () {
        return all(d, 'outbox').then(function (left) { if (!left.length) return caches.open(MARKS).then(function (c) { return c.delete(MARK); }); });
      });
    });
  }); }).catch(function () {}).then(function () { sending = null; });
  return sending;
}
function tell(msg) {
  return self.clients.matchAll({type: 'window'}).then(function (cs) { cs.forEach(function (c) { c.postMessage(msg); }); });
}
