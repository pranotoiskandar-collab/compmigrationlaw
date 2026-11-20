/* /follow/: choose countries and sign up for alerts. Opt-in only.
   While Buttondown is not set up, the form is the Netlify form "follow-country". Once /features/alerts-config.json carries
   a Buttondown username (tools/features/publish.py copies it from tools/digest/config.json), the form posts to Buttondown with
   one tag per country (country-ID, country-MY, ...), and Buttondown sends the confirmation email (double opt-in). */
(function () {
  var FT = window.FT, $ = function (id) { return document.getElementById(id); };
  var LIST, picked = {};
  (FT.param('c') || '').split(',').forEach(function (c) { if (/^[A-Z]{2}$/.test(c)) picked[c] = 1; });

  function draw() {
    var q = ($('fl-q').value || '').toLowerCase();
    $('fl-q').placeholder = FT.t('Find a country', 'Cari negara');
    $('fl-list').innerHTML = FT.sortByName(LIST).filter(function (c) {
      return picked[c.c] || !q || (c.en + ' ' + c.id).toLowerCase().indexOf(q) >= 0;
    }).map(function (c) {
      return '<label class="ft-chk"><input type="checkbox" value="' + c.c + '"' + (picked[c.c] ? ' checked' : '') + '> ' + FT.esc(FT.name(c)) + '</label>';
    }).join('');
    sync();
  }
  function sync() { $('fl-countries').value = Object.keys(picked).sort().join(','); }

  FT.index().then(function (d) {
    LIST = d.countries.filter(function (c) { return c.k > 0; });
    draw();
    $('fl-q').addEventListener('input', draw);
    $('fl-list').addEventListener('change', function (e) {
      if (e.target.checked) picked[e.target.value] = 1; else delete picked[e.target.value];
      sync();
    });
    FT.onLang(draw);
  });

  // RSS: one feed per country (tools/features/feeds.py writes the list of countries that have one)
  Promise.all([FT.index(), FT.json('/feeds/countries.json')]).then(function (r) {
    var have = {}; r[1].forEach(function (c) { have[c] = 1; });
    function fill() {
      var cur = $('fd-c').value || 'ID';
      $('fd-c').innerHTML = FT.sortByName(r[0].countries.filter(function (c) { return have[c.c]; }))
        .map(function (c) { return '<option value="' + c.c + '">' + FT.esc(FT.name(c)) + '</option>'; }).join('');
      $('fd-c').value = cur; link();
    }
    function link() { var u = '/feeds/c/' + $('fd-c').value + '.xml'; $('fd-link').href = u; $('fd-link').textContent = 'https://theimr.org' + u; }
    fill(); $('fd-c').addEventListener('change', link); FT.onLang(fill);
  }).catch(function () {});

  var form = $('follow-form');
  form.addEventListener('submit', function (e) {
    if (!Object.keys(picked).length) {
      e.preventDefault();
      alertBox(FT.t('Please choose at least one country.', 'Silakan pilih paling sedikit satu negara.'));
      return;
    }
    if (!form.dataset.bd) return; // Netlify form
    // Buttondown: one tag per country plus the language
    form.querySelectorAll('input[name=tag]').forEach(function (i) { i.remove(); });
    Object.keys(picked).concat(['lang-' + form.language.value]).forEach(function (t) {
      var i = document.createElement('input'); i.type = 'hidden'; i.name = 'tag';
      i.value = t.indexOf('lang-') === 0 ? t : 'country-' + t; form.appendChild(i);
    });
  });
  function alertBox(msg) {
    var p = form.querySelector('.ft-flag') || document.createElement('p');
    p.className = 'ft-flag'; p.setAttribute('role', 'alert'); p.textContent = msg;
    form.insertBefore(p, form.firstChild); p.scrollIntoView({block: 'center'});
  }
  fetch('/features/alerts-config.json').then(function (r) { return r.ok ? r.json() : {}; }).then(function (c) {
    if (!c || !c.buttondown_username) return;
    form.dataset.bd = '1';
    form.action = 'https://buttondown.com/api/emails/embed-subscribe/' + encodeURIComponent(c.buttondown_username);
    form.removeAttribute('data-netlify');
    ['form-name', 'website', 'countries', 'consent'].forEach(function (n) { var i = form.querySelector('[name="' + n + '"]'); if (i && n !== 'consent') i.disabled = true; });
  }).catch(function () {});
})();
