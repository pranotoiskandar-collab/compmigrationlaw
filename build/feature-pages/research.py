"""Build site/research/index.html: reading list and saved searches (no accounts; see /assets/research.js)."""
from shell import page

CSS = """<link rel="stylesheet" href="/assets/features.css">
<style>
.rs-list{margin:14px 0 0;padding-left:22px}
.rs-list li{margin:0 0 16px;padding:12px 14px;background:#FFFFFF;border:1px solid #B2C7BC}
.rs-note{display:block;margin:8px 0}
.rs-note span{display:block;font-size:13px;color:#2E493D}
.rs-note textarea{width:100%;box-sizing:border-box;font:15px 'Figtree',system-ui,sans-serif;padding:6px 8px;border:1px solid #B2C7BC}
</style>"""

MAIN = """<main id="research"><section style="padding:56px 0 24px"><div class="ft-narrow">
<p class="ft-eye">Migration Jurisprudence from the South · Tools</p>
<h1 class="ft-h1">Saved searches and reading list</h1>
<p class="ft-lede">For students, researchers and lawyers. Save court decisions to a reading list with your own notes, save searches with their filters, and export the list to Zotero, Mendeley, EndNote or a spreadsheet.</p>
<div class="ft-box">No account and no sign-in. Your lists stay in this browser on this device; IMR does not receive them. To move them to another device, download the list file and open it there, or send yourself the share link.</div>
<p class="ft-note" id="rs-count" data-noi18n></p>

<div class="ft-card" id="rs-incoming" hidden><p id="rs-incoming-text" style="margin:0" data-noi18n></p><div class="ft-row"><button type="button" class="ft-btn" id="rs-add-in">Add them to my list</button></div></div>

<h2 class="ft-h2">Reading list</h2>
<div id="rs-items" data-noi18n></div>
<div class="ft-row">
<button type="button" class="ft-btn" id="rs-bib">BibTeX</button>
<button type="button" class="ft-btn alt" id="rs-ris">RIS (Zotero, Mendeley, EndNote)</button>
<button type="button" class="ft-btn alt" id="rs-csv">CSV (spreadsheet)</button>
</div>

<h2 class="ft-h2">Saved searches</h2>
<div id="rs-searches" data-noi18n></div>

<h2 class="ft-h2">Move or share your lists</h2>
<div class="ft-row">
<button type="button" class="ft-btn alt" id="rs-json">Download list file</button>
<label class="ft-btn alt" for="rs-file" style="cursor:pointer">Open a list file</label><input type="file" id="rs-file" accept="application/json,.json" hidden>
<button type="button" class="ft-btn alt" id="rs-share">Copy share link</button>
<button type="button" class="ft-btn alt" id="rs-clear">Clear both lists</button>
</div>
<p class="ft-note">A share link carries the whole list inside the address, so a teacher can send a class one link. Long lists make long links; for more than about fifty entries, send the list file instead.</p>
</div></section></main>"""

I18N = {
    "Migration Jurisprudence from the South · Tools": "Pandangan Hukum Migrasi dari Dunia Berkembang · Alat",
    "Saved searches and reading list": "Pencarian tersimpan dan daftar bacaan",
    "For students, researchers and lawyers. Save court decisions to a reading list with your own notes, save searches with their filters, and export the list to Zotero, Mendeley, EndNote or a spreadsheet.":
        "Untuk mahasiswa, peneliti, dan advokat. Simpan putusan pengadilan ke daftar bacaan beserta catatan anda, simpan pencarian beserta filternya, lalu ekspor daftar tersebut ke Zotero, Mendeley, EndNote, atau lembar kerja.",
    "No account and no sign-in. Your lists stay in this browser on this device; IMR does not receive them. To move them to another device, download the list file and open it there, or send yourself the share link.":
        "Tanpa akun dan tanpa masuk. Daftar anda tetap berada di peramban pada perangkat ini; IMR tidak menerimanya. Untuk memindahkannya ke perangkat lain, unduh berkas daftar lalu buka di sana, atau kirim tautan berbagi kepada diri anda sendiri.",
    "Add them to my list": "Tambahkan ke daftar saya",
    "Reading list": "Daftar bacaan", "Saved searches": "Pencarian tersimpan",
    "RIS (Zotero, Mendeley, EndNote)": "RIS (Zotero, Mendeley, EndNote)", "CSV (spreadsheet)": "CSV (lembar kerja)",
    "Move or share your lists": "Pindahkan atau bagikan daftar anda",
    "Download list file": "Unduh berkas daftar", "Open a list file": "Buka berkas daftar", "Copy share link": "Salin tautan berbagi", "Clear both lists": "Kosongkan kedua daftar",
    "A share link carries the whole list inside the address, so a teacher can send a class one link. Long lists make long links; for more than about fifty entries, send the list file instead.":
        "Tautan berbagi memuat seluruh daftar di dalam alamatnya, sehingga seorang pengajar dapat mengirim satu tautan kepada kelasnya. Daftar yang panjang menghasilkan tautan yang panjang; untuk lebih dari sekitar lima puluh entri, kirimkan berkas daftar sebagai gantinya.",
}

page("/research/", "Saved searches and reading list",
     "Save court decisions and database searches without an account, add notes, and export to BibTeX, RIS (Zotero, Mendeley, EndNote) or CSV. Lists stay in your browser.",
     MAIN, head=CSS + '<meta name="robots" content="noindex">',
     scripts='<script src="/assets/features.js" defer></script>\n<script src="/assets/research.js" defer></script>\n<script src="/research/rs.js" defer></script>', i18n=I18N)
print("ok")
