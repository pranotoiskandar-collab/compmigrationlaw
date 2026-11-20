/* /report/: fills in the page and entry the visitor came from. Submissions go to the Netlify form "data-problem". */
(function () {
  var FT = window.FT, p = new URLSearchParams(location.search);
  var page = p.get('page') || (document.referrer && document.referrer.indexOf(location.origin) === 0 ? document.referrer.slice(location.origin.length) : '');
  if (page) document.getElementById('rp-page').value = 'https://theimr.org' + page.replace(/^https?:\/\/[^/]+/, '');
  if (p.get('entry')) document.getElementById('rp-entry').value = p.get('entry');
  function lang() { document.getElementById('rp-lang').value = FT.L; }
  lang(); FT.onLang(lang);
})();
