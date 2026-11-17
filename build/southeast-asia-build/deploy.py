#!/usr/bin/env python3
"""Site-wide hooks for /southeast-asia/ (idempotent): plain-language notes, nav label in lang.js, sitemap, llms.txt.
Usage: python3 deploy.py <site-root>
Menus and the /databases/ card come from restructure-build/restructure.py; run it afterwards, then ai_use.py and analytics.py."""
import os, sys, re

ROOT = sys.argv[1]
p = lambda *a: os.path.join(ROOT, *a)

# plain-language notes
pj = open(p("assets", "plain.js"), encoding="utf-8").read()
if '"southeast-asia": {' not in pj:
    entry = '''    "southeast-asia": {
      "#glance": {
        en: "<p><b>What this shows.</b> How the law treats eight groups of migrant workers in Malaysia, Singapore, Thailand and Brunei, on ten features such as minimum wage, changing employer and bringing family.</p><p><b>How to read it.</b> The comparison is by worker group, not by country, because one country can treat groups very differently. In Singapore, for example, the main labor law covers construction workers but not domestic workers.</p><p><b>Keep in mind.</b> Most cells have been checked against the official law texts; the few that could not be checked are marked S.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Bagaimana hukum memperlakukan delapan kelompok pekerja migran di Malaysia, Singapura, Thailand, dan Brunei, pada sepuluh fitur seperti upah minimum, pindah majikan, dan membawa keluarga.</p><p><b>Cara membacanya.</b> Perbandingan dilakukan per kelompok pekerja, bukan per negara, karena satu negara bisa memperlakukan kelompok secara sangat berbeda. Di Singapura, misalnya, undang-undang ketenagakerjaan utama mencakup pekerja konstruksi tetapi tidak pekerja rumah tangga.</p><p><b>Perlu diingat.</b> Sebagian besar sel sudah diperiksa terhadap teks hukum resmi; beberapa yang belum bisa diperiksa ditandai S.</p>"
      },
      "#score": S.score(["group", "kelompok"]),
      "#intl": {
        en: "<p><b>What this shows.</b> Which international treaties each destination state has joined, and the ASEAN commitments that all members share. The ASEAN declarations are promises, not binding law.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Traktat internasional mana yang diikuti tiap negara tujuan, dan komitmen ASEAN yang dimiliki semua anggota. Deklarasi ASEAN adalah janji, bukan hukum yang mengikat.</p>"
      },
      "#profiles": S.profiles(["state", "negara"]),
      "#origins": {
        en: "<p><b>What this shows.</b> What the home countries do for their workers before and after they leave: licensing recruiters, limiting fees, contracts, training, insurance, officers at embassies and help on return.</p><p><b>How to read it.</b> These rows are the same records as on the Countries of Origin page. Unclear means we could not yet establish the rule.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Apa yang dilakukan negara asal bagi pekerjanya sebelum dan sesudah berangkat: perizinan perekrut, pembatasan biaya, kontrak, pelatihan, asuransi, petugas di kedutaan, dan bantuan saat pulang.</p><p><b>Cara membacanya.</b> Baris ini adalah catatan yang sama dengan halaman Negara Asal. Belum jelas berarti aturannya belum bisa kami pastikan.</p>"
      },
      "#agreements": S.agreements,
      "#laws": S.laws,
      "#reforms": S.reforms,
      "#methods": S.methods(["80 cells are coded (8 groups × 10 features); 63 have been checked against the official texts.", "Ada 80 sel yang dikodekan (8 kelompok × 10 fitur); 63 di antaranya sudah dicocokkan dengan teks resmi."])
    },
'''
    pj = pj.replace('    "countries-of-origin": {', entry + '    "countries-of-origin": {', 1)
    open(p("assets", "plain.js"), "w", encoding="utf-8").write(pj)

# nav label
lj = open(p("assets", "lang.js"), encoding="utf-8").read()
if '"Southeast Asia"' not in lj:
    lj = lj.replace('window.SITE_I18N={"id":{', 'window.SITE_I18N={"id":{"Southeast Asia": "Asia Tenggara", ', 1)
    open(p("assets", "lang.js"), "w", encoding="utf-8").write(lj)

# sitemap
sm = open(p("sitemap.xml"), encoding="utf-8").read()
if "/southeast-asia/" not in sm:
    sm = sm.replace("</urlset>", "  <url><loc>https://theimr.org/southeast-asia/</loc><lastmod>2026-11-13</lastmod></url>\n</urlset>")
    open(p("sitemap.xml"), "w", encoding="utf-8").write(sm)

# llms.txt
lt = open(p("llms.txt"), encoding="utf-8").read()
if "/southeast-asia/" not in lt:
    line = "- [Migrant workers in Southeast Asia](https://theimr.org/southeast-asia/): labor law for eight migrant worker groups in Malaysia, Singapore, Thailand and Brunei (ten de jure features), ASEAN and bilateral instruments, and emigration law of seven origin states; CSV downloads.\n"
    m = re.search(r"^- \[[^\]]*East Asia[^\n]*\n", lt, flags=re.M)
    lt = lt[:m.end()] + line + lt[m.end():] if m else lt.rstrip("\n") + "\n" + line
    open(p("llms.txt"), "w", encoding="utf-8").write(lt)
print("deploy ok")
