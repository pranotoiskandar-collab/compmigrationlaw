/* Indonesian strings for the annual report card on /materials/. Loaded after the site language scripts. */
(function () {
  var X = {"IMR Annual Report 2026": "Laporan Tahunan IMR 2026",
    "What we did in 2026, the databases in numbers, the team, and plans for 2027, on eight A4 pages.": "Kegiatan kami pada 2026, basis data dalam angka, tim kami, serta rencana untuk 2027, dalam delapan halaman A4.",
    "IMR Annual Report 2026 (Indonesian)": "Laporan Tahunan IMR 2026 (bahasa Indonesia)",
    "The same report in Indonesian.": "Laporan yang sama dalam bahasa Indonesia."};
  var D = window.SITE_I18N = window.SITE_I18N || {}; D.id = D.id || {};
  for (var k in X) if (!Object.prototype.hasOwnProperty.call(D.id, k)) D.id[k] = X[k];
  var b = document.querySelector('.imr-lang button[aria-pressed="true"]');
  if (b && b.getAttribute('data-sl') !== 'en') b.click();
})();
