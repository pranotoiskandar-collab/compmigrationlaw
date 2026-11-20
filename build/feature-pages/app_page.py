"""Build site/app/index.html: install theimr.org as an app and save the essentials for use without signal."""
from shell import page

MAIN = """<main id="app"><section style="padding:56px 0 24px"><div class="ft-narrow">
<p class="ft-eye">For phones</p>
<h1 class="ft-h1">Use IMR on your phone, even without signal</h1>
<p class="ft-lede">Put IMR on your home screen like an app. Then save the Legal Clinic, the rights checklists and the list of free legal help on your phone, so they open at sea, in a dormitory or anywhere the signal is weak.</p>

<h2 class="ft-h2">1. Install</h2>
<div class="ft-row" id="ap-install-row" hidden><button type="button" class="ft-btn" id="ap-install">Install the IMR app</button></div>
<p class="ft-note" id="ap-installed" hidden data-noi18n></p>
<div class="ft-card">
<p style="margin:0"><b>Android (Chrome):</b> open the menu (three dots), then choose <b>Install app</b> or <b>Add to Home screen</b>.</p>
<p style="margin:10px 0 0"><b>iPhone (Safari):</b> press the <b>Share</b> button, then <b>Add to Home Screen</b>.</p>
</div>

<h2 class="ft-h2">2. Save for use without signal</h2>
<p class="ft-note">Saves about 1 MB: the Legal Clinic, the rights checklists for all countries, the free legal help directory and the trafficking self-check. Do this once on Wi-Fi. Pages you open later are saved too.</p>
<div class="ft-row"><button type="button" class="ft-btn" id="ap-save">Save now</button></div>
<p class="ft-note" id="ap-status" role="status" data-noi18n></p>

<div class="ft-box">Saved pages stay only on your phone. A rights communication written in the Legal Clinic without signal waits on the phone and is sent when the phone is online again. Nothing is sent anywhere else.</div>
</div></section></main>"""

JS = """<script>
(function(){
var L=function(){return document.documentElement.lang==='id'?'id':'en'};
var T={en:{saving:'Saving…',done:'Saved. These pages now open without signal.',nosw:'This browser cannot save pages for offline use. Try Chrome on Android or Safari on iPhone.',already:'IMR is installed on this device.',fail:'Could not save right now. Try again on Wi-Fi.'},
id:{saving:'Menyimpan…',done:'Tersimpan. Halaman-halaman ini kini bisa dibuka tanpa sinyal.',nosw:'Peramban ini tidak dapat menyimpan halaman untuk dipakai tanpa sinyal. Coba Chrome di Android atau Safari di iPhone.',already:'IMR sudah terpasang di perangkat ini.',fail:'Belum bisa menyimpan. Coba lagi saat tersambung Wi-Fi.'}};
var ev=null,row=document.getElementById('ap-install-row');
addEventListener('beforeinstallprompt',function(e){e.preventDefault();ev=e;row.hidden=false;});
document.getElementById('ap-install').addEventListener('click',function(){if(!ev)return;ev.prompt();ev.userChoice.then(function(){ev=null;row.hidden=true;});});
if(matchMedia('(display-mode: standalone)').matches||navigator.standalone){var i=document.getElementById('ap-installed');i.hidden=false;i.textContent=T[L()].already;}
var st=document.getElementById('ap-status'),timer;
document.getElementById('ap-save').addEventListener('click',function(){
 if(!('serviceWorker' in navigator)){st.textContent=T[L()].nosw;return;}
 st.textContent=T[L()].saving;
 clearTimeout(timer);timer=setTimeout(function(){st.textContent=T[L()].fail;},60000);
 navigator.serviceWorker.ready.then(function(r){var lite=navigator.connection&&navigator.connection.saveData;(r.active||navigator.serviceWorker.controller).postMessage({type:'save-essentials',lite:!!lite});});
});
if('serviceWorker' in navigator)navigator.serviceWorker.addEventListener('message',function(e){if(e.data&&e.data.type==='essentials-saved'){clearTimeout(timer);st.textContent=T[L()].done;}});
})();
</script>"""

I18N = {
    "For phones": "Untuk ponsel",
    "Use IMR on your phone, even without signal": "Pakai IMR di ponsel, bahkan tanpa sinyal",
    "Put IMR on your home screen like an app. Then save the Legal Clinic, the rights checklists and the list of free legal help on your phone, so they open at sea, in a dormitory or anywhere the signal is weak.":
        "Pasang IMR di layar utama ponsel seperti aplikasi. Lalu simpan Klinik Hukum, daftar periksa hak, dan daftar bantuan hukum gratis di ponsel anda, sehingga semuanya tetap bisa dibuka di laut, di asrama, atau di mana pun sinyalnya lemah.",
    "1. Install": "1. Pasang", "Install the IMR app": "Pasang aplikasi IMR",
    "Android (Chrome):": "Android (Chrome):", " open the menu (three dots), then choose ": " buka menu (tiga titik), lalu pilih ",
    "Install app": "Instal aplikasi", " or ": " atau ", "Add to Home screen": "Tambahkan ke layar utama", ".": ".",
    "iPhone (Safari):": "iPhone (Safari):", " press the ": " tekan tombol ", "Share": "Bagikan", " button, then ": ", lalu ",
    "Add to Home Screen": "Tambahkan ke Layar Utama",
    "2. Save for use without signal": "2. Simpan untuk dipakai tanpa sinyal",
    "Saves about 1 MB: the Legal Clinic, the rights checklists for all countries, the free legal help directory and the trafficking self-check. Do this once on Wi-Fi. Pages you open later are saved too.":
        "Menyimpan sekitar 1 MB, yakni Klinik Hukum, daftar periksa hak untuk semua negara, direktori bantuan hukum gratis, dan cek mandiri perdagangan orang. Lakukan sekali saat tersambung Wi-Fi. Halaman yang anda buka kemudian juga akan tersimpan.",
    "Save now": "Simpan sekarang",
    "Saved pages stay only on your phone. A rights communication written in the Legal Clinic without signal waits on the phone and is sent when the phone is online again. Nothing is sent anywhere else.":
        "Halaman yang tersimpan hanya berada di ponsel anda. Pengaduan hak yang ditulis di Klinik Hukum tanpa sinyal akan menunggu di ponsel dan terkirim begitu ponsel kembali tersambung. Tidak ada yang dikirim ke tempat lain.",
}

page("/app/", "Use IMR on your phone",
     "Install theimr.org as an app on Android or iPhone and save the Legal Clinic, rights checklists and free legal help directory for use without signal.",
     MAIN, head='<link rel="stylesheet" href="/assets/features.css">', scripts='<script src="/assets/features.js" defer></script>\n' + JS, i18n=I18N)
print("ok")
