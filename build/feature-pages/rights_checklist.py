"""Build site/rights-checklist/index.html. The sheets are drawn by site/rights-checklist/rc.js from
checklist-data.json (see rights_checklist_data.py); the PDFs in site/rights-checklist/pdf/ are printed from the
same page by rights_checklist_pdfs.js. Rebuild order: rights_checklist_data.py, rights_checklist.py, then the PDFs."""
from shell import page

CSS = r"""<link rel="stylesheet" href="/assets/features.css">
<style>
.rc-picks{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 0}
.rc-pick{font-size:17px;padding:12px 16px}
.rc-step{margin:34px 0 0;font-weight:600;font-size:21px}
.rc-step b{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;background:#1E6B4A;color:#FFF;font-size:16px;margin-right:8px}
#rc-sheet{margin:26px 0 0;background:#FFFFFF;border:1px solid #B2C7BC;padding:28px 30px;color:#172D24;font-size:17px;line-height:1.5}
#rc-sheet:empty{display:none}
.rc-head{border-bottom:3px solid #1E6B4A;padding-bottom:12px}
.rc-k{margin:0;font:600 13px/1.3 'Figtree',sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#1E6B4A}
.rc-h{margin:4px 0 0;font-size:34px;font-weight:600;line-height:1.1}
.rc-job{margin:4px 0 0;font-size:19px}
.rc-badge{display:inline-block;margin:10px 0 0;padding:4px 10px;background:#FFF6E0;border:1px solid #D9B25C;font-size:14px;font-weight:600}
.rc-sec{margin:24px 0 8px;font-size:21px;font-weight:600;border-bottom:1px solid #DCE8E1;padding-bottom:4px}
.rc-boxes,.rc-rules,.rc-list{list-style:none;margin:0;padding:0}
.rc-boxes li{display:flex;gap:12px;align-items:flex-start;margin:8px 0}
.rc-box{flex:0 0 22px;height:22px;border:2px solid #172D24;border-radius:3px;margin-top:2px;text-align:center;font-weight:700;line-height:20px}
.rc-warn{background:#FFF6E0;padding:8px;border-left:4px solid #A86B00}
.rc-warn .rc-box{border-color:#A86B00;color:#A86B00}
.rc-rules li{display:flex;gap:12px;align-items:flex-start;padding:10px 0;border-bottom:1px solid #EEF3EF;break-inside:avoid}
.rc-ic{flex:0 0 34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700}
.rc-y{background:#CFE6D8;color:#0F4A30}.rc-p{background:#FBEBC5;color:#6B4A00}.rc-n{background:#F3D9D3;color:#7A1F0E}.rc-u{background:#ECEDEA;color:#4A4F4C}
.rc-do{color:#1E6B4A;font-weight:500}
.rc-small{font-size:13.5px;color:#4A5A52}
.rc-legend{margin:0 0 6px;font-size:14px;color:#4A5A52;white-space:pre-wrap}
.rc-more summary{cursor:pointer;font-size:13.5px;color:#1E6B4A}
.rc-list li{margin:6px 0}
.rc-cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:16px}
.rc-sub{margin:4px 0;font-weight:600}
.rc-url{font-size:14px}
.rc-foot{margin:22px 0 0;padding-top:10px;border-top:1px solid #B2C7BC;font-size:13px;color:#4A5A52}
@media (max-width:640px){#rc-sheet{padding:18px 16px}.rc-h{font-size:28px}}
@media print{
  @page{size:A4;margin:12mm}
  body,body>div{background:#FFF!important}
  .imr-bentham,header.ed-mast,.imr-ridge,footer,#rc-intro,#rc-app>.rc-step,#rc-app>.rc-picks,#rc-step2,#rc-tools,.imr-lang,.rc-more,.imr-skip,[data-imr-skip]{display:none!important}
  main section{padding:0!important}
  .ft-wrap,.ft-narrow{max-width:none;padding:0}
  #rc-sheet{margin:0;border:0;padding:0;font-size:9pt;line-height:1.28}
  #rc-app>.ft-note{display:none!important}
  .rc-h{font-size:20pt}.rc-job{font-size:11pt}.rc-sec{margin:9pt 0 4pt;font-size:12pt}
  .rc-boxes li{margin:3pt 0}.rc-box{flex-basis:12pt;height:12pt;line-height:11pt}
  .rc-rules{columns:2;column-gap:7mm}
  .rc-rules li{display:flex;padding:3pt 0;break-inside:avoid;page-break-inside:avoid}
  .rc-ic{flex:0 0 18pt;height:18pt;font-size:11pt}
  .rc-small{font-size:7.6pt}
  .rc-list .rc-small{display:none}
  .rc-list li{margin:2pt 0}
  .rc-foot{font-size:7.6pt;margin-top:8pt}
  .rc-ic{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  .rc-badge,.rc-warn{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  a{color:#172D24;text-decoration:none}
}
</style>"""

MAIN = r"""<main id="rights-checklist">
<section style="padding:56px 0 8px" id="rc-intro"><div class="ft-narrow">
<p class="ft-eye">Legal Clinic · Before you go</p>
<h1 class="ft-h1">Know your rights before you go</h1>
<p class="ft-lede">Choose the country and the job. You get a one-page checklist in Indonesian, built from our databases: what to do before leaving Indonesia, what the destination's law says about your work, and who to call if something goes wrong. Print it, save it as PDF, or send it by WhatsApp.</p>
<div class="ft-warn">This is legal information, not legal advice. Laws change, and your contract may give you more. For help with your own case, use the <a href="/legal-clinic/">Legal Clinic</a> or <a href="/legal-help/">find free legal help</a>.</div>
</div></section>
<section><div class="ft-narrow" id="rc-app">
<p class="rc-step"><b>1</b>Where are you going?</p>
<div class="rc-picks" id="rc-countries" data-noi18n></div>
<div id="rc-step2" hidden>
<p class="rc-step"><b>2</b>What work will you do?</p>
<div class="rc-picks" id="rc-groups" data-noi18n></div>
</div>
<div id="rc-tools" class="ft-row" hidden style="margin-top:30px">
<span class="ft-note" style="margin:0">Sheet language</span>
<span id="rc-langs" data-noi18n><button type="button" class="ft-btn alt" data-l="id" aria-pressed="true">Bahasa Indonesia</button> <button type="button" class="ft-btn alt" data-l="en" aria-pressed="false">English</button></span>
<button type="button" class="ft-btn" id="rc-print">Print</button>
<a class="ft-btn alt" id="rc-pdf" href="#" data-imr-download>Download PDF</a>
<a class="ft-btn alt" id="rc-wa" href="#" target="_blank" rel="noopener">Share on WhatsApp</a>
</div>
<article id="rc-sheet" data-noi18n aria-live="polite"></article>
<p class="ft-note" style="margin-top:28px">Countries and jobs shown are those our databases code today: domestic work in the Gulf States, Malaysia, Singapore, Hong Kong and Taiwan (Migrant Domestic Workers database), and the worker groups of the East Asia and Southeast Asia pages. Factory and care work in Taiwan, and other jobs, will follow as the databases grow.</p>
<p class="ft-note">To keep these sheets on your phone for use without signal, see <a href="/app/">Use IMR without signal</a>.</p>
</div></section>
</main>"""

I18N = {
    "Legal Clinic · Before you go": "Klinik Hukum · Sebelum berangkat",
    "Know your rights before you go": "Kenali hak anda sebelum berangkat",
    "Choose the country and the job. You get a one-page checklist in Indonesian, built from our databases: what to do before leaving Indonesia, what the destination's law says about your work, and who to call if something goes wrong. Print it, save it as PDF, or send it by WhatsApp.":
        "Pilih negara dan pekerjaan. Anda akan mendapat daftar periksa satu halaman dalam bahasa Indonesia yang kami susun dari basis data kami, yakni apa yang perlu dilakukan sebelum meninggalkan Indonesia, apa kata hukum negara tujuan tentang pekerjaan anda, dan siapa yang dapat dihubungi bila terjadi masalah. Anda dapat mencetaknya, menyimpannya sebagai PDF, atau mengirimkannya melalui WhatsApp.",
    "This is legal information, not legal advice. Laws change, and your contract may give you more. For help with your own case, use the ": "Ini merupakan informasi hukum, bukan nasihat hukum. Hukum dapat berubah, dan kontrak anda mungkin memberi hak lebih. Untuk bantuan atas kasus anda sendiri, gunakan ",
    "Legal Clinic": "Klinik Hukum", " or ": " atau ", "find free legal help": "cari bantuan hukum gratis",
    "Where are you going?": "Ke mana anda akan pergi?",
    "What work will you do?": "Pekerjaan apa yang akan anda lakukan?",
    "Sheet language": "Bahasa lembar",
    "To keep these sheets on your phone for use without signal, see ": "Untuk menyimpan lembar ini di ponsel agar bisa dipakai tanpa sinyal, lihat ",
    "Use IMR without signal": "Pakai IMR tanpa sinyal",
    "Print": "Cetak", "Download PDF": "Unduh PDF", "Share on WhatsApp": "Bagikan lewat WhatsApp",
    "Countries and jobs shown are those our databases code today: domestic work in the Gulf States, Malaysia, Singapore, Hong Kong and Taiwan (Migrant Domestic Workers database), and the worker groups of the East Asia and Southeast Asia pages. Factory and care work in Taiwan, and other jobs, will follow as the databases grow.":
        "Negara dan pekerjaan yang tersedia merupakan yang saat ini dikodekan dalam basis data kami, yakni pekerjaan rumah tangga di negara-negara Teluk, Malaysia, Singapura, Hong Kong, dan Taiwan (basis data Pekerja Rumah Tangga Migran), serta kelompok pekerja pada halaman Asia Timur dan Asia Tenggara. Pekerjaan pabrik dan perawatan di Taiwan, serta pekerjaan lain, akan menyusul seiring bertambahnya basis data.",
}

page("/rights-checklist/", "Know your rights before you go",
     "A printable checklist in Indonesian for each main destination country and job: what to do before leaving, what the destination's law says, and where to get help. Built from the IMR databases; legal information, not legal advice.",
     MAIN, head=CSS,
     scripts='<script src="/assets/features.js" defer></script>\n<script src="/rights-checklist/rc.js" defer></script>', i18n=I18N)
print("ok")
