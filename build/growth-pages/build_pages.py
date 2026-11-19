"""Build /partners/ (badge, widget, reuse terms), /impact/ and /materials/, plus /assets/lang-growth.js.

Run from the repository root:  python3 build/growth-pages/build_pages.py
Numbers about the data are counted from data/ when the script runs. Numbers about use
(visitors, citations, partners, stories) come only from impact-figures.json; when a value is
missing the page says it is being collected. Nothing is estimated.
"""
import collections
import json
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from common import DATA, ROOT, SITE, esc, page, rows, tr, write_lang  # noqa: E402

HERE = pathlib.Path(__file__).parent
PROJECT = pathlib.Path("/mnt/project-files")


def fmt(n):
    return f"{n:,}"


# ---------------------------------------------------------------- data counts
def counts():
    dec = rows("court-decisions/decisions.csv")
    laws = sum(len(rows(p)) for p in ("southeast-asia/domestic-laws.csv", "east-asia/domestic-laws.csv",
                                      "gcc/domestic-laws.csv", "countries-of-origin/laws-policies.csv"))
    norms = len(rows("migration-law/migration-norms.csv"))
    dw = rows("domestic-workers/instruments.csv")
    idx = json.loads((SITE / "legal-clinic" / "ask" / "ask-index.json").read_text(encoding="utf-8"))
    help_n = idx["totals"][3]
    return dict(decisions=len(dec), dec_countries=len({r["country"] for r in dec if len(r["country"]) == 2 and not r["country"].startswith("X")}),
                coded=sum(1 for r in dec if r["status"] in ("S", "P")), laws=laws, norms=norms, dw=len(dw), help=help_n,
                rules=idx["totals"][0])


# ---------------------------------------------------------------- partners
def partners():
    countries = json.loads((SITE / "legal-clinic" / "ask" / "ask-index.json").read_text(encoding="utf-8"))["countries"]
    order = sorted(countries, key=lambda c: countries[c]["en"])
    opts = "".join(f'<option value="{c}"{" selected" if c == "MY" else ""}>{esc(countries[c]["en"])}</option>' for c in order)
    badge_code = ('<a href="https://theimr.org/?ref=badge" title="Data from the Institute for Migrant Rights (IMR)">'
                  '<img src="https://theimr.org/partners/badge/data-from-imr.svg" width="198" height="42" '
                  'alt="Data from IMR, Institute for Migrant Rights"></a>')
    badge_code_id = badge_code.replace("data-from-imr", "data-dari-imr").replace("Data from IMR", "Data dari IMR").replace(
        "Data from the Institute", "Data dari Institute")
    m = f"""
<section class="gp gp-hero"><p class="gp-eb">{tr("Partners", "Mitra")}</p>
<h1>{tr("Show and share IMR data", "Tampilkan dan bagikan data IMR")}</h1>
<p>{tr("Legal aid offices, NGOs, unions, universities and journalists may show IMR data on their own sites. We ask one thing in return: show the “Data from IMR” badge with a link to theimr.org.", "Kantor bantuan hukum, LSM, serikat pekerja, universitas dan jurnalis dapat menampilkan data IMR di situs mereka sendiri. Kami hanya meminta satu hal sebagai gantinya, yakni memasang lencana “Data dari IMR” beserta tautan ke theimr.org.")}</p></section>
<div class="gp">
<section class="gp-sec" id="badge"><p class="gp-num">I</p><h2>{tr("The badge", "Lencananya")}</h2>
<p>{tr("The badge tells your readers where the information comes from and that it can be checked. Each link back also helps people find IMR in search engines.", "Lencana ini memberi tahu pembaca anda dari mana informasinya berasal dan bahwa informasi tersebut dapat diperiksa. Setiap tautan balik juga membantu orang menemukan IMR melalui mesin pencari.")}</p>
<div class="gp-badges"><img src="/partners/badge/data-from-imr.svg" width="264" height="56" alt="Data from IMR badge, light"><span class="dark"><img src="/partners/badge/data-from-imr-dark.svg" width="264" height="56" alt="Data from IMR badge, dark"></span>
<img src="/partners/badge/data-dari-imr.svg" width="264" height="56" alt="Data dari IMR badge, light"><span class="dark"><img src="/partners/badge/data-dari-imr-dark.svg" width="264" height="56" alt="Data dari IMR badge, dark"></span></div>
<h3>{tr("Copy this code into your page (English)", "Salin kode ini ke halaman anda (bahasa Inggris)")}</h3>
<div class="gp-code" data-noi18n><textarea readonly aria-label="Badge code, English" rows="3">{esc(badge_code)}</textarea><button type="button" class="gp-copy" data-copy>Copy</button></div>
<h3>{tr("Copy this code into your page (Indonesian)", "Salin kode ini ke halaman anda (bahasa Indonesia)")}</h3>
<div class="gp-code" data-noi18n><textarea readonly aria-label="Badge code, Indonesian" rows="3">{esc(badge_code_id)}</textarea><button type="button" class="gp-copy" data-copy>Copy</button></div>
<p>{tr("Download the badge files:", "Unduh berkas lencananya:")}</p>
<p class="gp-noprint"><a class="gp-btn ghost" href="/partners/badge/data-from-imr.svg" download>SVG EN</a><a class="gp-btn ghost" href="/partners/badge/data-from-imr.png" download>PNG EN</a><a class="gp-btn ghost" href="/partners/badge/data-from-imr-dark.png" download>PNG EN dark</a><a class="gp-btn ghost" href="/partners/badge/data-dari-imr.svg" download>SVG ID</a><a class="gp-btn ghost" href="/partners/badge/data-dari-imr.png" download>PNG ID</a><a class="gp-btn ghost" href="/partners/badge/data-dari-imr-dark.png" download>PNG ID dark</a></p>
</section>

<section class="gp-sec" id="widget"><p class="gp-num">II</p><h2>{tr("Put a country box on your site", "Pasang kotak negara di situs anda")}</h2>
<p>{tr("The country box shows what IMR has for one country: the main rules, laws with links to the official texts, court decisions and free legal help. It updates itself whenever IMR updates its data. The badge is built into the box.", "Kotak negara menampilkan apa yang dimiliki IMR untuk satu negara, yakni aturan pokok, undang-undang dengan tautan ke teks resminya, putusan pengadilan, dan bantuan hukum gratis. Kotak ini diperbarui dengan sendirinya setiap kali IMR memperbarui datanya. Lencananya sudah terpasang di dalam kotak tersebut.")}</p>
<form class="gp-form gp-noprint" id="wform" onsubmit="return false">
<label>{tr("Country", "Negara")}<select id="wc">{opts}</select></label>
<label>{tr("Language", "Bahasa")}<select id="wl"><option value="id">Bahasa Indonesia</option><option value="en">English</option></select></label>
<label>{tr("Topic", "Topik")}<select id="wt"><option value="">{tr("All topics", "Semua topik")}</option><option value="wage">{tr("Wages", "Gaji dan upah")}</option><option value="fees">{tr("Recruitment and fees", "Perekrutan dan biaya")}</option><option value="passport">{tr("Passport and documents", "Paspor dan dokumen")}</option><option value="employer">{tr("Changing or losing a job", "Pindah atau kehilangan pekerjaan")}</option><option value="violence">{tr("Violence and abuse", "Kekerasan dan penganiayaan")}</option><option value="status">{tr("Visa, arrest and deportation", "Visa, penangkapan dan deportasi")}</option><option value="domestic">{tr("Domestic work", "Pekerja rumah tangga")}</option></select></label>
</form>
<div class="gp-code" data-noi18n><textarea readonly id="wcode" aria-label="Country box code" rows="4"></textarea><button type="button" class="gp-copy" data-copy>Copy</button></div>
<iframe class="gp-frame" id="wprev" title="Preview of the IMR country box" loading="lazy"></iframe>
</section>

<section class="gp-sec" id="connect"><p class="gp-num">III</p><h2>{tr("Connect to the data", "Sambungkan ke datanya")}</h2>
<p>{tr("Developers and researchers can take the data directly. Every database has CSV downloads, and the open data files give one country at a time in JSON.", "Pengembang dan peneliti dapat mengambil datanya secara langsung. Setiap basis data memiliki unduhan CSV, dan berkas data terbuka menyediakan data per negara dalam format JSON.")}</p>
<ul class="gp-list">
<li><a href="/databases/">{tr("All databases and their CSV downloads", "Semua basis data dan unduhan CSV-nya")}</a></li>
<li><span data-noi18n><code>https://theimr.org/api/v1/index.json</code></span> · <span data-noi18n><code>https://theimr.org/api/v1/countries/MY.json</code></span> <span>{tr("(open data files, one per country, ISO two-letter code)", "(berkas data terbuka, satu per negara, kode ISO dua huruf)")}</span></li>
<li><a href="https://github.com/pranotoiskandar-collab/compmigrationlaw">{tr("The full data and site source on GitHub", "Seluruh data dan kode sumber situs di GitHub")}</a></li>
</ul>
<p class="gp-note">{tr("If you show IMR data on a website or in an app, put the badge next to it. In a report, article or book, use the credit line below.", "Jika anda menampilkan data IMR di situs web atau aplikasi, pasanglah lencananya di dekat data tersebut. Dalam laporan, artikel atau buku, gunakan kalimat sumber di bawah ini.")}</p>
</section>

<section class="gp-sec" id="terms"><p class="gp-num">IV</p><h2>{tr("Terms of reuse", "Ketentuan penggunaan ulang")}</h2>
<ol class="gp-list">
<li>{tr("The data and the text of this site are under the Creative Commons Attribution 4.0 licence (CC BY 4.0). You may copy, share and adapt them for any purpose, if you give credit, link to the licence and say if you changed anything.", "Data dan teks situs ini berada di bawah lisensi Creative Commons Atribusi 4.0 (CC BY 4.0). Anda boleh menyalin, membagikan dan mengadaptasinya untuk tujuan apa pun, asalkan anda menyebutkan sumbernya, menautkan lisensinya, dan menyatakan jika anda mengubah sesuatu.")}</li>
<li>{tr("On websites and apps, the badge is how we ask you to give credit. It meets the credit requirement of the licence. The country box and the badge must stay as they are: please do not hide, crop or recolor them.", "Di situs web dan aplikasi, lencana inilah cara yang kami minta untuk menyebutkan sumber. Lencana tersebut memenuhi syarat penyebutan sumber dalam lisensi. Kotak negara dan lencananya harus tetap utuh, sehingga mohon jangan disembunyikan, dipotong, atau diubah warnanya.")}</li>
<li>{tr("In print and research, use this credit line:", "Dalam terbitan cetak dan penelitian, gunakan kalimat sumber berikut:")} <span data-noi18n><i>Institute for Migrant Rights, Migration Jurisprudence from the South (theimr.org), CC BY 4.0.</i></span></li>
<li>{tr("The IMR name, logo and badge are not covered by the licence. You may use the badge only to link to theimr.org as the source of the data, and not in a way that suggests IMR endorses you or your work.", "Nama, logo dan lencana IMR tidak termasuk dalam lisensi tersebut. Anda hanya boleh memakai lencana untuk menautkan theimr.org sebagai sumber data, dan tidak dengan cara yang mengesankan bahwa IMR mendukung anda atau karya anda.")}</li>
<li>{tr("The data is legal information, not legal advice. Laws change, so link to the official source when you can. Court judgments and laws belong to their publishers.", "Data ini merupakan informasi hukum, bukan nasihat hukum. Hukum dapat berubah, sehingga tautkanlah sumber resminya jika memungkinkan. Putusan pengadilan dan undang-undang merupakan milik penerbitnya masing-masing.")}</li>
</ol>
<p><a href="https://creativecommons.org/licenses/by/4.0/">{tr("Read the CC BY 4.0 licence", "Baca lisensi CC BY 4.0")}</a></p>
</section>

<section class="gp-sec" id="list"><p class="gp-num">V</p><h2>{tr("Tell us you use it", "Beri tahu kami bahwa anda memakainya")}</h2>
<p>{tr("Write to secretariat@theimr.org with the address of your page. With your permission we will list your organization on our impact page, and tell you when the data for your country changes.", "Kirimkan surel ke secretariat@theimr.org dengan alamat halaman anda. Dengan izin anda, kami akan mencantumkan organisasi anda di halaman dampak kami dan memberi tahu anda bila data negara anda berubah.")}</p>
<p><a class="gp-btn" href="mailto:secretariat@theimr.org?subject=Partner%20badge">secretariat@theimr.org</a> <a class="gp-btn ghost" href="/impact/">{tr("Our impact", "Dampak kami")}</a> <a class="gp-btn ghost" href="/materials/">{tr("Materials to download", "Bahan untuk diunduh")}</a></p>
</section>
</div>
<script>
(function(){{
  document.addEventListener('click',function(e){{var b=e.target.closest('[data-copy]');if(!b)return;var t=b.previousElementSibling;t.select();
    var done=function(){{var o=b.textContent;b.textContent='✓';setTimeout(function(){{b.textContent=o}},1500)}};
    if(navigator.clipboard)navigator.clipboard.writeText(t.value).then(done,function(){{document.execCommand('copy');done()}});else{{document.execCommand('copy');done()}}}});
  var c=document.getElementById('wc'),l=document.getElementById('wl'),tp=document.getElementById('wt'),code=document.getElementById('wcode'),prev=document.getElementById('wprev');
  try{{if(localStorage.getItem('imr-lang')==='en')l.value='en'}}catch(e){{}}
  function upd(){{var q='c='+c.value+'&lang='+l.value+(tp.value?'&topic='+tp.value:'');
    var alt=l.value==='id'?'Data dari IMR':'Data from IMR';
    code.value='<iframe src="https://theimr.org/embed/country/?'+q+'" title="'+alt+': '+c.options[c.selectedIndex].text+'" width="100%" height="560" style="max-width:420px;border:1px solid #B2C7BC;border-radius:6px" loading="lazy"></iframe>';
    prev.src='/embed/country/?'+q;}}
  [c,l,tp].forEach(function(x){{x.addEventListener('change',upd)}});upd();
}})();
</script>"""
    page("partners", "Partner badge and country box",
         "Show IMR data on your own site: the 'Data from IMR' badge, an embeddable country box, open data files and the terms of reuse (CC BY 4.0).", m)


# ---------------------------------------------------------------- impact
def impact(n):
    fig = json.loads((HERE / "impact-figures.json").read_text(encoding="utf-8"))
    pending = tr("Being collected", "Sedang dihimpun")

    def stat(value, label, note, src=None):
        if value is None:
            return (f'<div class="gp-stat pending"><b>{pending}</b><span>{label}</span>'
                    f'<small>{note}</small></div>')
        return f'<div class="gp-stat"><b>{fmt(value) if isinstance(value, int) else esc(value)}</b><span>{label}</span><small>{note}</small></div>'

    period = fig.get("period")
    use = "".join([
        stat(fig["visitors"]["value"], tr("people visited the site", "orang mengunjungi situs ini"), tr("Unique visitors, counted without cookies.", "Pengunjung unik, dihitung tanpa kuki.")),
        stat(fig["visitor_countries"]["value"], tr("countries they came from", "negara asal pengunjung"), tr("Countries with at least one visit.", "Negara dengan sedikitnya satu kunjungan.")),
        stat(fig["downloads"]["value"], tr("data downloads", "unduhan data"), tr("CSV, PDF and other files downloaded.", "Berkas CSV, PDF dan lainnya yang diunduh.")),
        stat(fig["ask_questions"]["value"], tr("questions asked to Ask IMR", "pertanyaan kepada Tanya IMR"), tr("Only the country and topic are counted, never the question.", "Hanya negara dan topiknya yang dihitung, bukan pertanyaannya.")),
        stat(fig["clinic_drafts"]["value"], tr("rights communications prepared with the Clinic", "pengaduan hak yang disiapkan bersama Klinik"), tr("Drafts sent to the Clinic for review.", "Draf yang dikirim ke Klinik untuk ditinjau.")),
        stat(fig["widget_views"]["value"], tr("views of the IMR country box on partner sites", "tayangan kotak negara IMR di situs mitra"), tr("Counted on the box itself.", "Dihitung pada kotak itu sendiri.")),
    ])
    data = "".join([
        stat(n["decisions"], tr("court decisions", "putusan pengadilan"), tr(f"From courts in {n['dec_countries']} countries, and from regional and international bodies.", f"Dari pengadilan di {n['dec_countries']} negara, serta dari badan kawasan dan internasional.")),
        stat(n["coded"], tr("decisions fully coded", "putusan yang dikodekan penuh"), tr("The rest are listed and waiting to be checked.", "Sisanya telah didaftar dan menunggu diperiksa.")),
        stat(n["laws"], tr("national laws and regulations with official links", "undang-undang dan peraturan nasional dengan tautan resmi"), tr("Gulf States, East Asia, Southeast Asia and countries of origin.", "Negara Teluk, Asia Timur, Asia Tenggara dan negara asal.")),
        stat(n["rules"], tr("coded rules, country by country", "aturan terkode, per negara"), tr("Wages, hours, fees, changing employer and more.", "Upah, jam kerja, biaya, pindah majikan dan lainnya.")),
        stat(n["norms"], tr("global, regional and national norms in the Atlas", "norma global, kawasan dan nasional dalam Atlas"), tr("With ratifications by country.", "Beserta ratifikasinya per negara.")),
        stat(n["help"], tr("free legal help contacts", "kontak bantuan hukum gratis"), tr("Phone numbers only where checked.", "Nomor telepon hanya yang sudah diperiksa.")),
    ])

    def items(lst, render, empty):
        if not lst:
            return f'<p class="gp-note">{empty}</p>'
        return '<ul class="gp-list">' + "".join(render(x) for x in lst) + "</ul>"

    cites = items(fig["citations"], lambda c: f'<li><a href="{esc(c.get("url", ""))}">{esc(c["title"])}</a> <span class="gp-tag">{esc(c.get("type", ""))}</span></li>',
                  tr("We are collecting the places where IMR data is cited: scholarship, policy papers, court filings and the press. If you have cited IMR, please tell us.", "Kami sedang menghimpun tempat-tempat yang mengutip data IMR, yakni karya ilmiah, kertas kebijakan, berkas perkara dan pers. Jika anda pernah mengutip IMR, mohon beri tahu kami."))
    partners_l = items(fig["partners"], lambda p: f'<li><a href="{esc(p.get("url", ""))}">{esc(p["name"])}</a> <span class="gp-tag">{esc(p.get("uses", ""))}</span></li>',
                       tr("No partner sites are listed yet. Organizations that show the IMR badge or country box will appear here with their permission.", "Belum ada situs mitra yang tercantum. Organisasi yang memasang lencana atau kotak negara IMR akan tampil di sini dengan izin mereka."))
    stories = items(fig["stories"], lambda s: f'<li><b>{esc(s["title"])}</b>. {esc(s["text"])}</li>',
                    tr("Stories will be published only with the written consent of the people involved, and without names or details that could identify them.", "Kisah hanya akan diterbitkan dengan persetujuan tertulis dari orang-orang yang terlibat, tanpa nama atau rincian yang dapat mengenali mereka."))
    per = f" ({esc(period)})" if period else ""
    m = f"""
<section class="gp gp-hero"><p class="gp-eb">{tr("Impact", "Dampak")}</p>
<h1>{tr("What IMR has built, and who uses it", "Apa yang telah dibangun IMR, dan siapa yang memakainya")}</h1>
<p>{tr("This page reports what we can count. Where a figure has not yet been counted, it says so. We do not estimate.", "Halaman ini melaporkan apa yang dapat kami hitung. Jika suatu angka belum dihitung, halaman ini menyatakannya. Kami tidak membuat perkiraan.")}</p></section>
<div class="gp">
<section class="gp-sec" id="data"><p class="gp-num">I</p><h2>{tr("What we have built", "Apa yang telah kami bangun")}</h2>
<p>{tr("Counted directly from the open data on the day this page was built.", "Dihitung langsung dari data terbuka pada hari halaman ini dibangun.")}</p><div class="gp-grid">{data}</div></section>
<section class="gp-sec" id="use"><p class="gp-num">II</p><h2>{tr("Who uses it", "Siapa yang memakainya")}{per}</h2>
<p>{tr("Counted with GoatCounter, which uses no cookies and keeps no personal data.", "Dihitung dengan GoatCounter, yang tidak memakai kuki dan tidak menyimpan data pribadi.")}</p><div class="gp-grid">{use}</div></section>
<section class="gp-sec" id="citations"><p class="gp-num">III</p><h2>{tr("Where IMR data is cited", "Di mana data IMR dikutip")}</h2>{cites}</section>
<section class="gp-sec" id="partners"><p class="gp-num">IV</p><h2>{tr("Partner sites", "Situs mitra")}</h2>{partners_l}<p><a href="/partners/">{tr("How to show IMR data on your site", "Cara menampilkan data IMR di situs anda")}</a></p></section>
<section class="gp-sec" id="stories"><p class="gp-num">V</p><h2>{tr("Stories", "Kisah")}</h2>{stories}</section>
<section class="gp-sec" id="method"><p class="gp-num">VI</p><h2>{tr("How we count", "Cara kami menghitung")}</h2>
<ul class="gp-list">
<li>{tr("Data figures are counted from the CSV files in the public repository each time the page is built.", "Angka data dihitung dari berkas CSV di repositori publik setiap kali halaman ini dibangun.")}</li>
<li>{tr("Use figures come from GoatCounter, a privacy-friendly counter without cookies. Ask IMR counts only the country and the topic of a question.", "Angka pemakaian berasal dari GoatCounter, penghitung yang ramah privasi tanpa kuki. Tanya IMR hanya menghitung negara dan topik suatu pertanyaan.")}</li>
<li>{tr("Citations, partners and stories are listed only after we have seen them, with a link where one exists.", "Kutipan, mitra dan kisah hanya dicantumkan setelah kami melihatnya sendiri, dengan tautan bila tersedia.")}</li>
</ul>
<p class="gp-noprint"><button type="button" class="gp-copy" onclick="window.print()">{tr("Print or save as PDF", "Cetak atau simpan sebagai PDF")}</button> <a class="gp-btn ghost" href="mailto:secretariat@theimr.org?subject=IMR%20impact">secretariat@theimr.org</a></p>
</section>
</div>"""
    page("impact", "Impact", "What the Institute for Migrant Rights has built and who uses it: data counted from the open databases, use counted without cookies, citations, partner sites and stories.", m)


# ---------------------------------------------------------------- materials
MATERIALS = [
    # (source under /mnt/project-files, file name on the site, unused). The main flyer is layout B, Puncak green (site look).
    ("flyer/alt-layouts/alt-b-puncak-green.pdf", "imr-flyer-en.pdf", "flyer/preview/imr-flyer-en-p1.png"),
    ("flyer/alt-layouts/alt-b-puncak-green-id.pdf", "imr-flyer-id.pdf", "flyer/preview/imr-flyer-id-p1.png"),
    ("volunteer-brief/imr-volunteer-brief-us.pdf", "imr-volunteer-brief-en.pdf", "volunteer-brief/preview/imr-volunteer-brief-us-p1.png"),
    ("volunteer-brief/imr-relawan-mahasiswa-hukum-id.pdf", "imr-relawan-mahasiswa-hukum-id.pdf", "volunteer-brief/preview/imr-relawan-mahasiswa-hukum-id-p1.png"),
]


# Teaching packs: (file stem in site/materials/files/teaching/, title EN, title ID, text EN, text ID, citation)
TEACHING = [
    ("paket-ajar-hukum-migrasi-tenaga-kerja-id",
     "Teaching pack on migrant labor law: five court-decision case studies (in Indonesian)",
     "Paket Ajar Hukum Migrasi Tenaga Kerja: lima studi kasus putusan pengadilan",
     "Five modules on decisions of the Indonesian Constitutional Court and foreign courts about Indonesian migrant workers. 13 pages, A4.",
     "Lima modul tentang putusan Mahkamah Konstitusi dan pengadilan negara lain mengenai pekerja migran Indonesia. 13 halaman, A4.",
     "Institute for Migrant Rights (2026). Paket Ajar Hukum Migrasi Tenaga Kerja: lima studi kasus dari putusan pengadilan, versi 1.0."),
]


def copy_materials():
    """Copy the public outreach files into site/materials/files/ (only when the project folder is there)."""
    out = SITE / "materials" / "files"
    out.mkdir(parents=True, exist_ok=True)
    if not PROJECT.exists():
        print("project folder not mounted; keeping the files already in site/materials/files/")
        return
    from PIL import Image
    for src, name, thumb in MATERIALS:
        shutil.copy2(PROJECT / src, out / name)
        # Thumbnail from page 1 of the PDF itself, so it always shows the current version.
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-r", "60", "-png", str(PROJECT / src), f"{tmp}/p"], check=True)
            im = Image.open(next(pathlib.Path(tmp).glob("p*.png"))).convert("RGB")
        im.thumbnail((480, 680))
        im.save(out / name.replace(".pdf", ".jpg"), quality=82, optimize=True)
    teach = out / "teaching"
    teach.mkdir(exist_ok=True)
    for stem, *_ in TEACHING:
        for ext in (".pdf", ".docx"):
            if (PROJECT / "teaching-packs" / (stem + ext)).exists():
                shutil.copy2(PROJECT / "teaching-packs" / (stem + ext), teach / (stem + ext))
        if (teach / (stem + ".pdf")).exists():
            import subprocess
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-r", "60", "-png", str(teach / (stem + ".pdf")), f"{tmp}/p"], check=True)
                im = Image.open(next(pathlib.Path(tmp).glob("p*.png"))).convert("RGB")
            im.thumbnail((480, 680))
            im.save(teach / (stem + ".jpg"), quality=82, optimize=True)


def size(name):
    p = SITE / "materials" / "files" / name
    return f"PDF, {p.stat().st_size / 1e6:.1f} MB" if p.exists() else "PDF"


def materials():
    teaching = SITE / "materials" / "files" / "teaching"
    packs = [t for t in TEACHING if (teaching / (t[0] + ".pdf")).exists()]
    if packs:
        cards = []
        for stem, title_en, title_id, text_en, text_id, cite in packs:
            pdf, docx, jpg = (teaching / (stem + ext) for ext in (".pdf", ".docx", ".jpg"))
            thumb = ""
            if jpg.exists():
                from PIL import Image
                w, h = Image.open(jpg).size
                thumb = f'<a href="/materials/files/teaching/{pdf.name}"><img class="gp-thumb" src="/materials/files/teaching/{jpg.name}" alt="" width="{w}" height="{h}" loading="lazy"></a>'
            word = f'<a class="gp-btn ghost" href="/materials/files/teaching/{docx.name}" download>Word</a>' if docx.exists() else ""
            cards.append(f'<div class="gp-card">{thumb}<h3>{tr(title_en, title_id)}</h3><p>{tr(text_en, text_id)}</p>'
                         f'<p class="gp-meta">Bahasa Indonesia · PDF, {pdf.stat().st_size / 1e6:.1f} MB · CC BY 4.0</p>'
                         f'<p class="gp-meta"><span>{tr("Cite as:", "Kutip sebagai:")}</span> <span data-noi18n>{esc(cite)}</span></p>'
                         f'<a class="gp-btn" href="/materials/files/teaching/{pdf.name}" download>PDF</a>{word}</div>')
        packs_html = (f'<p>{tr("Ready-made case studies for law faculties, built on court decisions in the IMR databases, with questions for class. Lecturers may copy and adapt them.", "Studi kasus siap pakai bagi fakultas hukum, yang disusun dari putusan pengadilan dalam basis data IMR, lengkap dengan pertanyaan untuk diskusi kelas. Para dosen boleh menyalin dan menyesuaikannya.")}</p>'
                      '<div class="gp-grid">' + "".join(cards) + "</div>")
    else:
        packs_html = f'<p class="gp-note">{tr("Teaching packs for law faculties are being prepared: case studies built on IMR court decisions and laws, with questions for class. They will appear here for download.", "Bahan ajar untuk fakultas hukum sedang disiapkan, berupa studi kasus yang disusun dari putusan pengadilan dan undang-undang dalam basis data IMR, lengkap dengan pertanyaan untuk diskusi kelas. Bahan tersebut akan tersedia untuk diunduh di sini.")}</p>'

    def card(name, title, text, lang_label):
        w, h = 480, 679
        jpg = SITE / "materials" / "files" / name.replace(".pdf", ".jpg")
        if jpg.exists():
            from PIL import Image
            w, h = Image.open(jpg).size
        return (f'<div class="gp-card"><a href="/materials/files/{name}"><img class="gp-thumb" src="/materials/files/{name.replace(".pdf", ".jpg")}" alt="" width="{w}" height="{h}" loading="lazy"></a>'
                f'<h3>{title}</h3><p>{text}</p><p class="gp-meta">{lang_label} · {size(name)}</p>'
                f'<a class="gp-btn" href="/materials/files/{name}" download>{tr("Download", "Unduh")}</a></div>')

    m = f"""
<section class="gp gp-hero"><p class="gp-eb">{tr("Materials", "Bahan")}</p>
<h1>{tr("Materials to download and share", "Bahan untuk diunduh dan dibagikan")}</h1>
<p>{tr("Flyers, country sheets, volunteer briefs and teaching packs. Print them, send them on WhatsApp or put them on your notice board. Everything here is free to share under CC BY 4.0.", "Selebaran, lembar negara, panduan relawan dan bahan ajar. Cetaklah, kirimkan lewat WhatsApp, atau tempelkan di papan pengumuman anda. Semua bahan di sini bebas dibagikan di bawah lisensi CC BY 4.0.")}</p></section>
<div class="gp">
<section class="gp-sec" id="flyers"><p class="gp-num">I</p><h2>{tr("About IMR: two-page flyer", "Tentang IMR: selebaran dua halaman")}</h2>
<div class="gp-grid">{card("imr-flyer-en.pdf", tr("IMR flyer (English)", "Selebaran IMR (bahasa Inggris)"), tr("What IMR does, the databases and the Legal Clinic, on two A4 pages.", "Apa yang dikerjakan IMR, basis data dan Klinik Hukum, dalam dua halaman A4."), "English")}
{card("imr-flyer-id.pdf", tr("IMR flyer (Indonesian)", "Selebaran IMR (bahasa Indonesia)"), tr("The same flyer in Indonesian.", "Selebaran yang sama dalam bahasa Indonesia."), "Bahasa Indonesia")}</div></section>
<section class="gp-sec" id="country-sheets"><p class="gp-num">II</p><h2>{tr("Country sheets", "Lembar negara")}</h2>
<p>{tr("One page for each of eight countries of origin, in English and Indonesian, as a PDF to print and as an image for phones.", "Satu halaman untuk masing-masing dari delapan negara asal, dalam bahasa Inggris dan Indonesia, sebagai PDF untuk dicetak dan sebagai gambar untuk ponsel.")}</p>
<p><a class="gp-btn" href="/country-sheets/">{tr("Open the country sheets", "Buka lembar negara")}</a></p></section>
<section class="gp-sec" id="volunteers"><p class="gp-num">III</p><h2>{tr("Volunteer briefs", "Panduan relawan")}</h2>
<div class="gp-grid">{card("imr-volunteer-brief-en.pdf", tr("Volunteer with IMR (English)", "Menjadi relawan IMR (bahasa Inggris)"), tr("Tasks from sharing and translating to research, data and code.", "Tugas mulai dari menyebarkan dan menerjemahkan hingga penelitian, data dan pemrograman."), "English")}
{card("imr-relawan-mahasiswa-hukum-id.pdf", tr("Volunteer brief for law students (Indonesian)", "Panduan relawan untuk mahasiswa hukum (bahasa Indonesia)"), tr("Tasks for Indonesian law students and campus legal clinics.", "Tugas bagi mahasiswa hukum Indonesia dan klinik hukum kampus."), "Bahasa Indonesia")}</div></section>
<section class="gp-sec" id="teaching"><p class="gp-num">IV</p><h2>{tr("Teaching packs", "Bahan ajar")}</h2>{packs_html}</section>
<section class="gp-sec" id="badge"><p class="gp-num">V</p><h2>{tr("Partner badge", "Lencana mitra")}</h2>
<p>{tr("If you use IMR data on your site, show the badge with a link to theimr.org.", "Jika anda memakai data IMR di situs anda, pasanglah lencananya dengan tautan ke theimr.org.")}</p>
<div class="gp-badges"><img src="/partners/badge/data-from-imr.svg" width="264" height="56" alt="Data from IMR badge"><img src="/partners/badge/data-dari-imr.svg" width="264" height="56" alt="Data dari IMR badge"></div>
<p><a class="gp-btn" href="/partners/#badge">{tr("Get the badge code", "Ambil kode lencananya")}</a></p></section>
<section class="gp-sec" id="connect"><p class="gp-num">VI</p><h2>{tr("Connect and embed", "Sambungkan dan sematkan")}</h2>
<p>{tr("Put an IMR country box on your own site, or take the data directly as CSV or JSON. The badge comes with it.", "Pasang kotak negara IMR di situs anda sendiri, atau ambil datanya langsung dalam format CSV atau JSON. Lencananya sudah termasuk.")}</p>
<p><a class="gp-btn" href="/partners/#widget">{tr("Embed a country box", "Sematkan kotak negara")}</a><a class="gp-btn ghost" href="/partners/#connect">{tr("Open data files", "Berkas data terbuka")}</a><a class="gp-btn ghost" href="/partners/#terms">{tr("Terms of reuse", "Ketentuan penggunaan ulang")}</a></p></section>
</div>"""
    page("materials", "Materials", "Free IMR materials to download and share: flyers in English and Indonesian, country sheets, volunteer briefs, teaching packs and the partner badge.", m)


def main():
    copy_materials()
    n = counts()
    partners()
    impact(n)
    materials()
    tr("Our impact", "Dampak kami")
    tr("Materials", "Bahan")
    tr("Partner badge", "Lencana mitra")
    tr("Copy", "Salin")
    write_lang()


if __name__ == "__main__":
    main()
