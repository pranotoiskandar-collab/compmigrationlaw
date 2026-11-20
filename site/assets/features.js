/* Small helpers shared by the feature pages: CSV reading, the page language, and escaping.
   The site language switch (/assets/lang.js) stores its choice in localStorage "imr-lang" and sets <html lang>;
   pages that draw their own content listen for that change through IMRF.onLang. */
(function () {
  function parseCSV(text) {
    var rows = [], row = [], f = '', q = false, i, c;
    text = text.replace(/^﻿/, '');
    for (i = 0; i < text.length; i++) {
      c = text[i];
      if (q) {
        if (c === '"') { if (text[i + 1] === '"') { f += '"'; i++; } else q = false; }
        else f += c;
      } else if (c === '"') q = true;
      else if (c === ',') { row.push(f); f = ''; }
      else if (c === '\n' || c === '\r') {
        if (c === '\r' && text[i + 1] === '\n') i++;
        row.push(f); f = ''; if (row.length > 1 || row[0] !== '') rows.push(row); row = [];
      } else f += c;
    }
    if (f !== '' || row.length) { row.push(f); rows.push(row); }
    var head = rows.shift() || [];
    return rows.map(function (r) { var o = {}; head.forEach(function (h, j) { o[h] = r[j] == null ? '' : r[j]; }); return o; });
  }
  function getCSV(url) {
    return fetch(url).then(function (r) { if (!r.ok) throw new Error(url + ' ' + r.status); return r.text(); }).then(parseCSV);
  }
  function lang() {
    var l = document.documentElement.lang;
    if (l === 'id' || l === 'en') return l;
    try { return localStorage.getItem('imr-lang') === 'id' ? 'id' : 'en'; } catch (e) { return 'en'; }
  }
  var subs = [], last = null;
  function onLang(fn) { subs.push(fn); }
  new MutationObserver(function () {
    var l = lang(); if (l !== last) { last = l; subs.forEach(function (f) { f(l); }); }
  }).observe(document.documentElement, {attributes: true, attributeFilter: ['lang']});
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]; }); }
  function toast(msg) {
    var t = document.createElement('div'); t.className = 'ft-toast'; t.setAttribute('role', 'status'); t.setAttribute('data-noi18n', '');
    t.textContent = msg; document.body.appendChild(t); setTimeout(function () { t.remove(); }, 2600);
  }
  var MON = {en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
             id: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']};
  function date(iso, l) {
    if (!iso) return '';
    var p = iso.split('-'); if (p.length < 3) return iso;
    return (+p[2]) + ' ' + MON[l || lang()][+p[1] - 1] + ' ' + p[0];
  }
  window.IMRF = {parseCSV: parseCSV, getCSV: getCSV, lang: lang, onLang: onLang, esc: esc, toast: toast, date: date};
})();
