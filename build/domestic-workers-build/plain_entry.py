"""Adds the /domestic-workers/ entry to /assets/plain.js (idempotent). Run: python3 plain_entry.py SITE_DIR"""
import sys
SITE = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/theimr-site"
P = SITE + "/assets/plain.js"; s = open(P, encoding="utf-8").read()
if '"domestic-workers": {' in s: print("plain.js already has the entry"); sys.exit()
def box(en, id_): return '{\n        en: %s,\n        id: %s\n      }' % (repr_js(en), repr_js(id_))
import json
def repr_js(x): return json.dumps(x, ensure_ascii=False)
E = {
 "#glance": ("<p><b>What this shows.</b> How each country's law treats domestic workers who come from abroad, on 17 questions taken from the ILO Domestic Workers Convention, such as a weekly day off or keeping one's own passport. A second view shows what countries of origin do before their workers leave.</p><p><b>How to read it.</b> Full means the law meets the international standard, partial means it does so in part, none means the law does not provide for it. Click a cell to see the article of the law it rests on.</p><p><b>Keep in mind.</b> Only the law on paper is coded, not what happens in homes.</p>",
             "<p><b>Apa yang ditunjukkan.</b> Bagaimana hukum tiap negara memperlakukan pekerja rumah tangga dari luar negeri, pada 17 pertanyaan dari Konvensi ILO tentang Pekerja Rumah Tangga, misalnya hari libur mingguan atau memegang paspor sendiri. Tampilan kedua menunjukkan apa yang dilakukan negara asal sebelum pekerjanya berangkat.</p><p><b>Cara membacanya.</b> Penuh berarti hukum memenuhi standar internasional, sebagian berarti hanya sebagian, tidak ada berarti hukum tidak mengaturnya. Klik sel untuk melihat pasal yang menjadi dasarnya.</p><p><b>Perlu diingat.</b> Yang dikodekan hanya hukum di atas kertas, bukan apa yang terjadi di dalam rumah.</p>"),
 "#compare": ("<p><b>What this shows.</b> The rules of up to four countries next to each other, with the article of the law for each answer.</p>",
              "<p><b>Apa yang ditunjukkan.</b> Aturan hingga empat negara berdampingan, dengan pasal hukum untuk setiap jawaban.</p>"),
 "#c189": ("<p><b>What this shows.</b> For each rule in the ILO convention, how many of the 34 countries of destination follow it fully, in part or not at all. Long green bars are rules most countries already have; short ones show where the law is thinnest.</p>",
           "<p><b>Apa yang ditunjukkan.</b> Untuk setiap aturan dalam konvensi ILO, berapa dari 34 negara tujuan yang mengikutinya sepenuhnya, sebagian, atau tidak sama sekali. Batang hijau yang panjang adalah aturan yang sudah dimiliki sebagian besar negara; yang pendek menunjukkan di mana hukumnya paling tipis.</p>"),
 "#corridors": ("<p><b>What this shows.</b> The path of one worker: the rules of the home country before departure, any agreement between the two countries, and the rules in the country where she works.</p>",
                "<p><b>Apa yang ditunjukkan.</b> Jalur seorang pekerja: aturan negara asal sebelum berangkat, perjanjian antara kedua negara bila ada, dan aturan di negara tempat ia bekerja.</p>"),
 "#instruments": ("<p><b>What this shows.</b> Every treaty, agreement and law in the database. Binding means a state that has accepted it must follow it; not binding means it is guidance.</p>",
                  "<p><b>Apa yang ditunjukkan.</b> Semua traktat, perjanjian, dan hukum dalam basis data. Mengikat berarti negara yang menerimanya wajib mengikutinya; tidak mengikat berarti hanya pedoman.</p>"),
 "#timeline": ("<p><b>What this shows.</b> When the instruments were adopted. Most rules specific to domestic workers came after 2011, the year of the ILO convention.</p>",
               "<p><b>Apa yang ditunjukkan.</b> Kapan instrumen diadopsi. Sebagian besar aturan khusus pekerja rumah tangga muncul setelah 2011, tahun konvensi ILO.</p>"),
 "#treaties": ("<p><b>What this shows.</b> Which international treaties each country has joined. Joining a treaty is a promise to bring the law into line with it.</p>",
               "<p><b>Apa yang ditunjukkan.</b> Traktat internasional yang telah diikuti tiap negara. Mengikuti traktat adalah janji untuk menyesuaikan hukum dengannya.</p>"),
}
body = "\n    \"domestic-workers\": {\n" + ",\n".join('      "%s": %s' % (k, box(*v)) for k, v in E.items()) + \
  ',\n      "#score": S.score(["country", "negara"]),\n      "#profiles": S.profiles(["country", "negara"]),\n      "#analyze": S.analyze,\n      "#methods": S.methods(["658 cells are coded (34 destinations × 17 features and 10 origins × 8 features). The UAE cells come from the official text; the others are being checked.", "Ada 658 sel yang dikodekan (34 negara tujuan × 17 fitur dan 10 negara asal × 8 fitur). Sel UEA berasal dari teks resmi; sisanya sedang diperiksa."])\n    },'
anchor = '\n    "countries-of-origin": {'
assert anchor in s
s = s.replace(anchor, body + anchor, 1); open(P, "w", encoding="utf-8").write(s); print("plain.js entry added")
