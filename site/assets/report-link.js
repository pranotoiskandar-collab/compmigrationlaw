/* "Report a problem" link on every page (added at publish time by tools/features/publish.py).
   Footer: a link for the page. Court decision pages: a link for that decision, under its title.
   Reports go to the Netlify form "data-problem" on /report/ and from there to the data-fix tracker. */
(function () {
  if (/^\/report\//.test(location.pathname)) return;
  function L() { try { return localStorage.getItem('imr-lang') === 'id' ? 'id' : 'en'; } catch (e) { return 'en'; } }
  function href(entry) {
    return '/report/?page=' + encodeURIComponent(location.pathname + location.search) + (entry ? '&entry=' + encodeURIComponent(entry) : '');
  }
  var made = [];
  function txt(a) { a.textContent = L() === 'id' ? a.getAttribute('data-l-id') : a.getAttribute('data-l-en'); }
  function link(cls, entry, en, id) {
    var a = document.createElement('a');
    a.href = href(entry); a.rel = 'nofollow'; a.className = cls;
    a.setAttribute('data-noi18n', ''); a.setAttribute('data-l-en', en); a.setAttribute('data-l-id', id);
    txt(a); made.push(a); return a;
  }
  function init() {
    var f = document.querySelector('footer .imr-foot-ai p') || document.querySelector('footer');
    if (f && !document.querySelector('.imr-report-foot')) {
      var s = document.createElement('span'); s.className = 'imr-report-foot'; s.setAttribute('data-noi18n', '');
      s.appendChild(document.createTextNode(' · '));
      var a = link('', '', 'Report a problem with this page', 'Laporkan masalah di halaman ini');
      a.style.color = '#FFFFFF'; s.appendChild(a); f.appendChild(s);
    }
    var m = /^\/court-decisions\/d\/([^/]+)\/?$/.exec(location.pathname);
    var h = m && document.querySelector('main h1, h1');
    if (h && !document.querySelector('.imr-rep-btn')) {
      var p = document.createElement('p'); p.style.margin = '6px 0 0';
      var b = link('imr-rep-btn', decodeURIComponent(m[1]), 'Report a problem with this decision', 'Laporkan masalah pada putusan ini');
      b.style.cssText = 'font:14px/1.4 Figtree,system-ui,sans-serif;color:#8F5E12';
      p.appendChild(b); h.insertAdjacentElement('afterend', p);
    }
  }
  document.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('.imr-lang [data-sl], #langs [data-lang]')) setTimeout(function () { made.forEach(txt); }, 0);
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
