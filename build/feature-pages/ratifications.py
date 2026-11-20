"""Build site/ratifications/index.html (the ratification tracker). The table itself is drawn in the browser by
site/ratifications/rt.js from /ratifications/data/ratifications.csv, which the weekly workflow keeps current,
so this page needs rebuilding only when its text changes."""
from shell import page

MAIN = r"""<main id="ratifications">
<section style="padding:64px 0 8px"><div class="ft-narrow">
<p class="ft-eye">Migration Jurisprudence from the South · Tools</p>
<h1 class="ft-h1">Ratification tracker</h1>
<p class="ft-lede">Which states have joined the five treaties written for migrant workers: the ILO Migration for Employment Convention (C97), the ILO Migrant Workers Convention (C143), the ILO Domestic Workers Convention (C189), the ILO Violence and Harassment Convention (C190), and the UN Migrant Workers Convention (ICRMW).</p>
<div class="ft-box">The table is refreshed every week from the official records: ILO NORMLEX for the four ILO conventions and the UN Treaty Collection for the ICRMW. The date each record was last checked is shown below the table.</div>
</div></section>

<section><div class="ft-wrap">
<div class="ft-stats" id="rt-stats" data-noi18n aria-live="polite"></div>

<h2 class="ft-h2">Country by country</h2>
<div class="ft-row">
<label for="rt-q" class="ft-note" style="margin:0">Find a country</label>
<input id="rt-q" class="ft-input" type="search" autocomplete="off" placeholder="e.g. Indonesia">
<label for="rt-f" class="ft-note" style="margin:0">Show</label>
<select id="rt-f" class="ft-sel">
<option value="any">States party to at least one</option>
<option value="all">All states</option>
<option value="C097">Parties to C97</option>
<option value="C143">Parties to C143</option>
<option value="C189">Parties to C189</option>
<option value="C190">Parties to C190</option>
<option value="ICRMW">Parties to the ICRMW</option>
<option value="none">States party to none</option>
</select>
<span id="rt-save-slot"></span>
</div>
<div class="ft-scroll" tabindex="0" role="region" aria-label="Ratification table"><table class="ft-t" id="rt-table" data-noi18n></table></div>
<p class="ft-note" id="rt-legend" data-noi18n></p>
<p class="ft-note" id="rt-checked" data-noi18n></p>

<h2 class="ft-h2">Latest changes</h2>
<p class="ft-note">New ratifications, signatures and denunciations that the weekly check has found, newest first.</p>
<div id="rt-changes" data-noi18n></div>

<h2 class="ft-h2">The five treaties</h2>
<div class="ft-scroll"><table class="ft-t">
<thead><tr><th>Treaty</th><th>What it does for migrant workers</th><th>Official record</th></tr></thead>
<tbody>
<tr><td><b>C97</b> (1949)</td><td>Equal treatment with nationals on pay, union rights, housing, social security and access to courts for migrants who are lawfully in the country.</td><td><a href="https://normlex.ilo.org/dyn/nrmlx_en/f?p=NORMLEXPUB:11300:0::NO::P11300_INSTRUMENT_ID:312242">NORMLEX</a></td></tr>
<tr><td><b>C143</b> (1975)</td><td>Basic human rights for all migrant workers, including those without papers; action against clandestine movements and illegal employment; equal opportunity.</td><td><a href="https://normlex.ilo.org/dyn/nrmlx_en/f?p=NORMLEXPUB:11300:0::NO::P11300_INSTRUMENT_ID:312288">NORMLEX</a></td></tr>
<tr><td><b>C189</b> (2011)</td><td>Domestic workers get the labor rights other workers have: a written contract, rest days, a minimum wage, and the right to keep their own documents.</td><td><a href="https://normlex.ilo.org/dyn/nrmlx_en/f?p=NORMLEXPUB:11300:0::NO::P11300_INSTRUMENT_ID:2551460">NORMLEX</a></td></tr>
<tr><td><b>C190</b> (2019)</td><td>The right to a world of work free from violence and harassment, for everyone who works, whatever their contract or status.</td><td><a href="https://normlex.ilo.org/dyn/nrmlx_en/f?p=NORMLEXPUB:11300:0::NO::P11300_INSTRUMENT_ID:3999810">NORMLEX</a></td></tr>
<tr><td><b>ICRMW</b> (1990)</td><td>The UN treaty on the rights of all migrant workers and their families, with or without papers, from recruitment to return.</td><td><a href="https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&amp;mtdsg_no=IV-13&amp;chapter=4&amp;clang=_en">UN Treaty Collection</a></td></tr>
</tbody></table></div>

<h2 class="ft-h2">How to read and cite this</h2>
<div class="ft-en"><p class="ft-note">An ILO convention binds a state twelve months after the ILO registers its ratification; until then it is shown as "ratified, not yet in force". The ICRMW has been in force since 1 July 2003, so it binds each party from the date it ratified or acceded. A signature alone creates no obligation to apply the treaty, only an obligation not to defeat its purpose. Where an official record and this table differ, the official record is right; please tell us at <a href="mailto:secretariat@theimr.org">secretariat@theimr.org</a>.</p>
<p class="ft-note">Cite as: Institute for Migrant Rights, <i>Ratification tracker</i> (theimr.org/ratifications/, accessed [date]), compiled from ILO NORMLEX and the UN Treaty Collection.</p></div>
<div class="ft-id" data-noi18n><p class="ft-note">Konvensi ILO mengikat suatu negara dua belas bulan setelah ILO mendaftarkan ratifikasinya; sebelum itu, kami tampilkan sebagai "diratifikasi, belum berlaku". ICRMW telah berlaku sejak 1 Juli 2003, sehingga mengikat setiap negara pihak sejak tanggal ratifikasi atau aksesinya. Penandatanganan saja tidak menimbulkan kewajiban untuk menerapkan perjanjian tersebut, melainkan hanya kewajiban untuk tidak menggagalkan tujuannya. Apabila catatan resmi dan tabel ini berbeda, catatan resmi yang benar; mohon beri tahu kami melalui <a href="mailto:secretariat@theimr.org">secretariat@theimr.org</a>.</p>
<p class="ft-note">Kutip sebagai: Institute for Migrant Rights, <i>Pelacak ratifikasi</i> (theimr.org/ratifications/, diakses [tanggal]), dihimpun dari NORMLEX ILO dan UN Treaty Collection.</p></div>
<div class="ft-row">
<a class="ft-btn" href="/ratifications/data/ratifications.csv" data-imr-download>Download the table (CSV)</a>
<a class="ft-btn alt" href="/ratifications/data/changes.csv" data-imr-download>Change log (CSV)</a>
<a class="ft-btn alt" href="/ratifications/data/codebook.csv" data-imr-download>Codebook (CSV)</a>
</div>
</div></section>
</main>"""

I18N = {
    "Ratification table": "Tabel ratifikasi",
    "e.g. Indonesia": "misalnya Indonesia",
    "Migration Jurisprudence from the South · Tools": "Pandangan Hukum Migrasi dari Dunia Berkembang · Alat",
    "Ratification tracker": "Pelacak ratifikasi",
    "Which states have joined the five treaties written for migrant workers: the ILO Migration for Employment Convention (C97), the ILO Migrant Workers Convention (C143), the ILO Domestic Workers Convention (C189), the ILO Violence and Harassment Convention (C190), and the UN Migrant Workers Convention (ICRMW).":
        "Negara mana saja yang telah menjadi pihak pada lima perjanjian internasional yang disusun bagi pekerja migran, yakni Konvensi ILO tentang Migrasi untuk Pekerjaan (C97), Konvensi ILO tentang Pekerja Migran (C143), Konvensi ILO tentang Pekerja Rumah Tangga (C189), Konvensi ILO tentang Kekerasan dan Pelecehan (C190), serta Konvensi PBB tentang Pekerja Migran (ICRMW).",
    "The table is refreshed every week from the official records: ILO NORMLEX for the four ILO conventions and the UN Treaty Collection for the ICRMW. The date each record was last checked is shown below the table.":
        "Tabel ini kami perbarui setiap minggu dari catatan resmi, yakni NORMLEX ILO untuk keempat konvensi ILO dan UN Treaty Collection untuk ICRMW. Tanggal pemeriksaan terakhir setiap catatan tercantum di bawah tabel.",
    "Country by country": "Per negara",
    "Find a country": "Cari negara",
    "Show": "Tampilkan",
    "States party to at least one": "Negara pihak pada sekurang-kurangnya satu",
    "All states": "Semua negara",
    "Parties to C97": "Pihak pada C97", "Parties to C143": "Pihak pada C143", "Parties to C189": "Pihak pada C189",
    "Parties to C190": "Pihak pada C190", "Parties to the ICRMW": "Pihak pada ICRMW",
    "States party to none": "Negara yang belum menjadi pihak pada satu pun",
    "Latest changes": "Perubahan terbaru",
    "New ratifications, signatures and denunciations that the weekly check has found, newest first.":
        "Ratifikasi, penandatanganan, dan pengakhiran (denunciation) baru yang ditemukan pemeriksaan mingguan, dimulai dari yang terbaru.",
    "The five treaties": "Kelima perjanjian tersebut",
    "Treaty": "Perjanjian", "What it does for migrant workers": "Apa artinya bagi pekerja migran", "Official record": "Catatan resmi",
    "Equal treatment with nationals on pay, union rights, housing, social security and access to courts for migrants who are lawfully in the country.":
        "Perlakuan yang sama dengan warga negara dalam hal upah, hak berserikat, perumahan, jaminan sosial, dan akses ke pengadilan bagi migran yang berada secara sah di negara tersebut.",
    "Basic human rights for all migrant workers, including those without papers; action against clandestine movements and illegal employment; equal opportunity.":
        "Hak asasi dasar bagi semua pekerja migran, termasuk yang tidak berdokumen; tindakan terhadap perpindahan gelap dan pekerjaan ilegal; serta kesempatan yang sama.",
    "Domestic workers get the labor rights other workers have: a written contract, rest days, a minimum wage, and the right to keep their own documents.":
        "Pekerja rumah tangga memperoleh hak ketenagakerjaan yang sama dengan pekerja lain, yakni kontrak tertulis, hari istirahat, upah minimum, dan hak menyimpan dokumen sendiri.",
    "The right to a world of work free from violence and harassment, for everyone who works, whatever their contract or status.":
        "Hak atas dunia kerja yang bebas dari kekerasan dan pelecehan bagi setiap orang yang bekerja, apa pun kontrak atau statusnya.",
    "The UN treaty on the rights of all migrant workers and their families, with or without papers, from recruitment to return.":
        "Perjanjian PBB tentang hak semua pekerja migran dan keluarganya, berdokumen maupun tidak, sejak perekrutan hingga kepulangan.",
    "How to read and cite this": "Cara membaca dan mengutip",
    "Download the table (CSV)": "Unduh tabel (CSV)", "Change log (CSV)": "Catatan perubahan (CSV)", "Codebook (CSV)": "Buku kode (CSV)",
}

page("/ratifications/", "Ratification tracker",
     "Which states have ratified the ILO C97, C143, C189 and C190 conventions and the UN Migrant Workers Convention (ICRMW), refreshed weekly from ILO NORMLEX and the UN Treaty Collection.",
     MAIN, head='<link rel="stylesheet" href="/assets/features.css">',
     scripts='<script src="/assets/features.js" defer></script>\n<script src="/assets/research.js" defer></script>\n<script src="/ratifications/rt.js" defer></script>', i18n=I18N)
print("ok")
