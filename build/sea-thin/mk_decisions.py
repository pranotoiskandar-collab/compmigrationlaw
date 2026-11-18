"""Indonesian Constitutional Court decisions on the migrant worker laws, plus one Myanmar ruling.

Source list: imrdata repo, decisions/tables/mk_decisions.csv (MK list, 17 Nov 2026).
Texts: the official PDFs on s.mkri.id, downloaded on oto's Mac on 18 Nov 2026
(OneDrive IMR-data/sea-courts-2026-11-18/mk/, with summary.csv of verbatim holdings
and reasoning sentences with page numbers). Summaries below are written from those
texts. Myanmar: Myanmar Law Reports (Rulings) 2021, Union Supreme Court site.

Usage: python3 build/sea-thin/mk_decisions.py OUT.json
Writes {"new": [...], "links": {...}} for build/merge-incoming/patch_site_decisions.py.
Also prints the field update for the older stub c-id-mk-019-2005 (applied by update_stub.py).
"""
import json, sys

PDF = "https://s.mkri.id/public/content/persidangan/putusan/"
MKC = "Constitutional Court of Indonesia"


def mk(i, no, name, date, sector, issues, sit, stages, outcome, follow, q, q_id, held, plain, plain_id, args, tools, pdf, after_en, after_id):
    return {"id": i, "name": f"Decision {no} ({name})", "court": MKC, "cc": "ID", "region": "asia", "forum": "origin",
            "tier": "national", "level": "apex", "date": date, "cite": f"Putusan Nomor {no}", "sector": sector,
            "issues": issues, "situations": sit, "stages": stages, "outcome": outcome, "follow": follow, "status": "S",
            "q": q, "q_id": q_id, "held": held, "plain": plain, "plain_id": plain_id, "branch": "constitutional",
            "tools": tools, "args": args,
            "after": [{"d": date, "en": after_en, "id": after_id}],
            "src": [{"t": "Judgment (MKRI)", "u": PDF + pdf.replace(" ", "%20")}]}


NEW = [
    mk("mk-028-029-2006", "028-029/PUU-IV/2006", "minimum age of 21 for work with private employers abroad", "2007-04-12",
       "domestic work", ["equality", "work"], ["fees"], [1, 2], "lost", "none",
       "Does the rule that workers placed with individual (household) employers abroad must be at least 21 breach the right to work and equal treatment?",
       "Apakah ketentuan bahwa TKI yang dipekerjakan pada pengguna perseorangan sekurang-kurangnya berusia 21 tahun melanggar hak atas pekerjaan dan perlakuan yang sama?",
       "Rejected (5 to 4). The age limit in Art. 35(a) of Law 39/2004 pursues a legitimate aim, the personal and emotional maturity needed for work in private homes, is objectively and reasonably justified and is not discriminatory.",
       "Women aged 18 to 20 were refused departure because they were under 21, the minimum age for working in a private household abroad. They asked the Constitutional Court to strike the rule down. A narrow majority refused: the Court said the age limit protects workers and does not stop anyone from working.",
       "Sejumlah perempuan berusia 18 sampai 20 tahun ditolak berangkat karena belum berusia 21 tahun, batas usia minimum untuk bekerja pada pengguna perseorangan di luar negeri. Mereka meminta Mahkamah Konstitusi membatalkan ketentuan tersebut. Mayoritas tipis hakim menolak: menurut Mahkamah, batas usia tersebut melindungi pekerja dan tidak menghalangi hak seseorang untuk bekerja.",
       [{"a": "worktoright", "ok": False}, {"a": "equality", "ok": False}], ["standard"],
       "putusan_sidang_PutusanNomor028-029PUUIV2006tgl120407ttgPJTKI.pdf",
       "Petition rejected; the age limit of 21 stays.", "Permohonan ditolak; batas usia 21 tahun tetap berlaku."),
    mk("mk-005-2013", "5/PUU-XI/2013", "challenge to Law 39/2004, Art. 60, by a former worker's brother", "2013-08-27",
       "", ["access"], [], [4], "lost", "none",
       "Could the brother of a former migrant worker challenge Art. 60 of Law 39/2004 on her behalf?",
       "Apakah saudara laki-laki seorang mantan TKI dapat menguji Pasal 60 UU 39/2004 atas nama saudaranya?",
       "Not accepted. The petitioner gave no proof that he was the guardian of the worker concerned, so he lacked legal standing.",
       "A man asked the Court to review a rule of the 2004 migrant worker law on behalf of his sister, a former migrant worker. The Court did not look at the rule itself, because he could not show he had the right to act for her.",
       "Seorang laki-laki meminta Mahkamah menguji salah satu ketentuan UU 39/2004 atas nama saudara perempuannya, seorang mantan TKI. Mahkamah tidak memeriksa pokok perkara karena Pemohon tidak dapat membuktikan bahwa ia berhak bertindak atas nama saudaranya.",
       [], ["procedure"], "putusan_sidang_5 PUU 2013 - telah ucap 27 Agustus 2013.pdf",
       "Petition not accepted for lack of standing.", "Permohonan tidak dapat diterima karena Pemohon tidak memiliki kedudukan hukum."),
    mk("mk-050-2013", "50/PUU-XI/2013", "renewing a contract without first going home", "2014-10-16",
       "domestic work", ["employment", "equality"], ["employer"], [4], "won", "unknown",
       "May the law require a worker employed by an individual employer abroad to return to Indonesia before renewing the contract (Law 39/2004, Art. 59)?",
       "Bolehkah undang-undang mewajibkan TKI yang bekerja pada pengguna perseorangan pulang ke Indonesia sebelum memperpanjang perjanjian kerja (Pasal 59 UU 39/2004)?",
       "Granted in part. Art. 59 was struck down: it removed or threatened the worker's chance to extend a contract with an employer of the worker's choice, breaching equal treatment and the right to work and a decent living. The other challenged articles (Arts. 10(b), 58(2), 60) were upheld; who may place workers abroad is a matter of legislative policy.",
       "Women domestic workers from Cianjur challenged a rule forcing workers with household employers to come home before they could renew their contract. The Court struck the rule down: a protection law should not take away a worker's chance to stay with an employer she wants to keep working for.",
       "Para pekerja rumah tangga migran perempuan dari Cianjur menguji ketentuan yang mewajibkan TKI pada pengguna perseorangan pulang terlebih dahulu sebelum memperpanjang perjanjian kerja. Mahkamah membatalkan ketentuan tersebut: undang-undang perlindungan tidak boleh menghilangkan kesempatan pekerja untuk tetap bekerja pada majikan yang dikehendakinya.",
       [{"a": "worktoright", "ok": True}, {"a": "equality", "ok": True}, {"a": "recruiter", "ok": False}], ["rule", "policy"],
       "putusan_sidang_2064_50 PUU 2013-UU_39_th_2004-PenempatanDanPerlindungan-TKI-telahucap-16Okt2014- wmActionWiz.pdf",
       "Art. 59 of Law 39/2004 struck down; the other articles stay. Law 39/2004 was later replaced by Law 18/2017.",
       "Pasal 59 UU 39/2004 dinyatakan bertentangan dengan UUD 1945; pasal lainnya tetap berlaku. UU 39/2004 kemudian diganti dengan UU 18/2017."),
    mk("mk-061-2015", "61/PUU-XIII/2015", "placement rules behind the Middle East moratorium", "2015-10-20",
       "domestic work", ["recruitment", "equality"], ["fees"], [1, 2], "lost", "none",
       "Do the placement rules of Law 39/2004 (Arts. 11(1), 27(1), 81(1), 94 and 95), relied on to stop placements in the Middle East, discriminate against workers and placement companies?",
       "Apakah ketentuan penempatan dalam UU 39/2004 (Pasal 11 ayat (1), 27 ayat (1), 81 ayat (1), 94 dan 95), yang menjadi dasar penghentian penempatan ke Timur Tengah, mendiskriminasi pekerja dan perusahaan penempatan?",
       "Rejected. Different treatment serves to uphold citizens' rights to work and a decent living rather than to discriminate; requiring employers to be legal entities makes them easier to hold liable; the placement agency BNP2TKI is an open legal policy choice of the legislature.",
       "A placement company, a former worker in Riyadh and a woman who could not leave because of the halt on placements to the Middle East challenged the rules behind it. The Court upheld them, saying the rules aim to protect workers.",
       "Sebuah perusahaan penempatan, seorang mantan TKI di Riyadh, dan seorang calon TKI yang tidak dapat berangkat karena penghentian penempatan ke Timur Tengah menguji ketentuan yang menjadi dasarnya. Mahkamah menolak permohonan tersebut karena ketentuan itu bertujuan melindungi pekerja.",
       [{"a": "equality", "ok": False}, {"a": "worktoright", "ok": False}], ["policy"], "61_PUU-XIII_2015.pdf",
       "Petition rejected.", "Permohonan ditolak."),
    mk("mk-006-2015", "6/PUU-XIII/2015", "overseas worker card (KTKLN) for seafarers", "2016-08-04",
       "seafarers", ["coverage", "registration"], ["coverage"], [2], "lost", "none",
       "Is it unconstitutional to require Indonesian seafarers, like other workers going abroad, to hold the overseas worker card (KTKLN) (Law 39/2004, Arts. 26(2)(f) and 28)?",
       "Apakah kewajiban pelaut Indonesia, seperti TKI lainnya, untuk memiliki Kartu Tenaga Kerja Luar Negeri (KTKLN) (Pasal 26 ayat (2) huruf f dan Pasal 28 UU 39/2004) bertentangan dengan UUD 1945?",
       "Rejected. The KTKLN is a form of state protection at every stage of placement abroad: before, during and after placement.",
       "Six seafarers argued that the card required of workers going abroad was a burden that did not fit their work. The Court disagreed: the card is one of the ways the state protects workers before, during and after work abroad.",
       "Enam orang pelaut berpendapat bahwa kartu yang diwajibkan bagi TKI merupakan beban yang tidak sesuai dengan pekerjaan mereka. Mahkamah tidak sependapat: kartu tersebut merupakan salah satu bentuk perlindungan negara sebelum, selama, dan sesudah bekerja di luar negeri.",
       [{"a": "coverage", "ok": False}], ["policy"], "6_PUU-XIII_2015.pdf",
       "Petition rejected; the KTKLN rule stays.", "Permohonan ditolak; ketentuan KTKLN tetap berlaku."),
    mk("mk-012-2016", "12/PUU-XIV/2016", "settling disputes between workers and placement companies", "2017-05-30",
       "", ["access", "recruitment"], ["fees"], [5], "lost", "none",
       "Does Art. 85(2) of Law 39/2004 on settling disputes between a worker and the placement company deny workers access to justice because it does not list every remedy?",
       "Apakah Pasal 85 ayat (2) UU 39/2004 tentang penyelesaian perselisihan antara TKI dan PPTKIS menghalangi akses pekerja terhadap keadilan karena tidak menyebutkan semua upaya hukum?",
       "Rejected. Leaving a remedy out of Art. 85(2) does not make it unconstitutional; if workers do not get access to justice, that is a problem of implementation, not of the norm.",
       "The head of a union of Indonesian overseas workers said the law's dispute rules left workers without a way to court against their placement company. The Court said the rule itself is valid and that any failure lies in how it is applied.",
       "Ketua serikat pekerja Indonesia luar negeri berpendapat bahwa ketentuan penyelesaian perselisihan dalam undang-undang membuat pekerja tidak memiliki jalan ke pengadilan untuk menggugat perusahaan penempatan. Mahkamah menyatakan ketentuan tersebut sah dan bahwa kekurangannya terletak pada pelaksanaannya.",
       [], ["text"], "12_PUU-XIV_2016.pdf", "Petition rejected.", "Permohonan ditolak."),
    mk("mk-032-2017", "32/PUU-XV/2017", "meaning of 'exploitation' in the trafficking law", "2017-10-19",
       "", ["trafficking", "criminal"], ["forced"], [1], "lost", "none",
       "Is the trafficking offence in Art. 2(1) of Law 21/2007 unclear because it does not require proof that the victim was actually exploited?",
       "Apakah tindak pidana perdagangan orang dalam Pasal 2 ayat (1) UU 21/2007 tidak jelas karena tidak mensyaratkan bukti bahwa korban benar-benar dieksploitasi?",
       "Rejected. Art. 2(1) defines a formal offence, clear on its face; the petitioner's case concerns the application of the law and proof, not its constitutionality.",
       "A man prosecuted under the anti-trafficking law argued that it was unfair to convict without proof of actual exploitation. The Court said the law is clear: the crime is complete when the acts are done for the purpose of exploitation, and his complaint was about the evidence in his own case.",
       "Seorang laki-laki yang dituntut berdasarkan UU TPPO berpendapat bahwa tidak adil menghukum seseorang tanpa bukti eksploitasi yang nyata. Mahkamah menyatakan undang-undang tersebut jelas: tindak pidana telah selesai ketika perbuatan dilakukan dengan tujuan eksploitasi, dan keberatan Pemohon menyangkut pembuktian dalam perkaranya sendiri.",
       [], ["text"], "32_PUU-XV_2017.pdf", "Petition rejected; Art. 2(1) stays.", "Permohonan ditolak; Pasal 2 ayat (1) tetap berlaku."),
    mk("mk-083-2019", "83/PUU-XVII/2019", "capital and deposit rules for placement companies", "2020-11-25",
       "", ["recruitment"], ["fees"], [1], "won", "none",
       "Do the minimum paid-up capital (Rp5 billion) and bank deposit (Rp1.5 billion) required of placement companies under Law 18/2017, with criminal penalties, breach the Constitution?",
       "Apakah kewajiban modal disetor (Rp5 miliar) dan deposito (Rp1,5 miliar) bagi P3MI dalam UU 18/2017, beserta ketentuan pidananya, bertentangan dengan UUD 1945?",
       "Rejected (5 to 4). Raising the capital and deposit is part of ensuring the qualifications and credibility of placement companies; the criminal provisions apply to anyone who breaches the rules.",
       "The association of placement companies said the high capital and deposit rules of the 2017 law shut small agencies out. A narrow majority upheld the rules, which help make sure agencies can answer for what happens to the workers they send.",
       "Asosiasi perusahaan penempatan berpendapat bahwa kewajiban modal dan deposito yang tinggi dalam UU 18/2017 menyingkirkan perusahaan kecil. Mayoritas tipis hakim mempertahankan ketentuan tersebut, yang membantu memastikan perusahaan penempatan dapat bertanggung jawab atas pekerja yang dikirimnya.",
       [{"a": "recruiter", "ok": True}], ["policy"], "putusan_mkri_7238.pdf",
       "Petition rejected; the capital and deposit rules stay.", "Permohonan ditolak; ketentuan modal dan deposito tetap berlaku."),
    mk("mk-020-2020", "20/PUU-XVIII/2020", "bank deposit required of placement companies", "2020-11-25",
       "", ["recruitment"], ["fees"], [1], "won", "none",
       "Does the Rp1.5 billion deposit in a state bank required of placement companies (Law 18/2017, Art. 54(1)(b)) breach the Constitution?",
       "Apakah kewajiban deposito Rp1,5 miliar di bank pemerintah bagi P3MI (Pasal 54 ayat (1) huruf b UU 18/2017) bertentangan dengan UUD 1945?",
       "Rejected as to Art. 54(1)(b), following decision 83/PUU-XVII/2019; not accepted as to Art. 5(d), which sets duties of migrant workers, not of companies, so the company directors lacked standing.",
       "Directors of two placement companies challenged the bank deposit rule. The Court kept it, as it had in a decision the same day.",
       "Direktur dua perusahaan penempatan menguji ketentuan deposito di bank. Mahkamah mempertahankannya, sebagaimana dalam putusan yang diucapkan pada hari yang sama.",
       [{"a": "recruiter", "ok": True}], ["precedent"], "putusan_mkri_7246.pdf",
       "Petition rejected in part and not accepted in part.", "Permohonan ditolak sebagian dan tidak dapat diterima sebagian."),
    mk("mk-040-2011", "40/PUU-IX/2011", "exit ban during a preliminary investigation", "2012-02-08",
       "", ["exit"], ["arrest"], [2], "won", "unknown",
       "May the immigration law let officials stop a person from leaving Indonesia while a matter is only at the preliminary investigation stage (Law 6/2011, Art. 16(1)(b))?",
       "Bolehkah UU Keimigrasian memungkinkan pejabat mencegah seseorang keluar wilayah Indonesia ketika perkara masih dalam tahap penyelidikan (Pasal 16 ayat (1) huruf b UU 6/2011)?",
       "Granted. The words 'penyelidikan dan' were struck down: refusing exit when a person is not yet even a suspect can easily be used to block travel abroad and breaches legal certainty and equal treatment (Art. 28D(1)).",
       "Six advocates challenged the power to stop people leaving the country before they are even suspects. The Court agreed and removed it, so a ban on leaving now needs at least a formal criminal investigation.",
       "Enam advokat menguji kewenangan mencegah orang keluar negeri sebelum ia ditetapkan sebagai tersangka. Mahkamah mengabulkan permohonan tersebut sehingga pencegahan ke luar negeri kini sekurang-kurangnya memerlukan tahap penyidikan.",
       [{"a": "exitban", "ok": True}], ["rule"], "putusan_sidang_40 PUU 2011-TELAH BACA.pdf",
       "Words 'penyelidikan dan' in Art. 16(1)(b) struck down.", "Kata “penyelidikan dan” dalam Pasal 16 ayat (1) huruf b dinyatakan bertentangan dengan UUD 1945."),
    mk("mk-064-2011", "64/PUU-IX/2011", "repeated extension of exit bans", "2012-06-20",
       "", ["exit"], ["arrest"], [2], "won", "unknown",
       "May an exit ban under the immigration law be extended by six months 'each time' without limit (Law 6/2011, Art. 97(1))?",
       "Bolehkah pencegahan ke luar negeri berdasarkan UU Keimigrasian diperpanjang enam bulan “setiap kali” tanpa batas (Pasal 97 ayat (1) UU 6/2011)?",
       "Granted in part. The phrase 'setiap kali' (each time) is unconstitutional; extensions are acceptable only if limited and based on justice and legal certainty.",
       "A law professor under a travel ban challenged the rule that let the ban be renewed again and again. The Court removed the words 'each time', so renewals now have a limit.",
       "Seorang guru besar yang dicegah ke luar negeri menguji ketentuan yang memungkinkan pencegahan diperpanjang berkali-kali. Mahkamah membatalkan frasa “setiap kali” sehingga perpanjangan kini dibatasi.",
       [{"a": "exitban", "ok": True}], ["rule"], "putusan_sidang_64 PUU 2011-TELAH BACA 20-06-2012.pdf",
       "Phrase 'setiap kali' in Art. 97(1) struck down.", "Frasa “setiap kali” dalam Pasal 97 ayat (1) dinyatakan bertentangan dengan UUD 1945."),
]

NEW.append({
    "id": "c-mm-usc-82b-2020", "name": "Ma Thida v. Union of Myanmar (overseas employment charge or trafficking charge)",
    "court": "Supreme Court of the Union (Myanmar)", "cc": "MM", "region": "asia", "forum": "origin", "tier": "national",
    "level": "apex", "date": "2021-02-10", "cite": "Criminal Revision No. 82(b) of 2020 and No. 1(ka) of 2020, Myanmar Law Reports (Rulings) 2021, pp. 50-53",
    "sector": "", "issues": ["recruitment", "trafficking", "criminal"], "situations": ["fees", "forced"], "stages": [1],
    "outcome": "unknown", "follow": "unknown", "status": "C",
    "q": "Should a charge under the Overseas Employment Law (s. 26) be replaced by a heavier charge under the Anti Trafficking in Persons Law?",
    "q_id": "Apakah dakwaan berdasarkan Undang-Undang Pekerjaan di Luar Negeri (Pasal 26) harus diganti dengan dakwaan yang lebih berat berdasarkan Undang-Undang Anti Perdagangan Orang?",
    "held": "",
    "plain": "The High Court ordered a recruitment case to be re-charged under the anti-trafficking law, which carries heavier penalties. On revision, the Supreme Court held that a charge properly framed by the trial court should not be set aside just to frame a heavier one. Read from the Burmese report; to be confirmed by a Burmese reader.",
    "plain_id": "Pengadilan Tinggi memerintahkan agar perkara perekrutan didakwa ulang berdasarkan undang-undang anti perdagangan orang yang ancaman pidananya lebih berat. Dalam pemeriksaan revisi, Mahkamah Agung menyatakan bahwa dakwaan yang telah disusun dengan benar oleh pengadilan tingkat pertama tidak boleh dikesampingkan hanya untuk menyusun dakwaan yang lebih berat. Dibaca dari laporan berbahasa Myanmar; perlu dikonfirmasi oleh pembaca bahasa Myanmar.",
    "branch": "criminal", "tools": [], "args": [],
    "after": [{"d": "2021-02-10", "en": "Supreme Court decision on revision.", "id": "Putusan Mahkamah Agung atas revisi."}],
    "src": [{"t": "Union Supreme Court, Myanmar Law Reports (Rulings) 2021",
             "u": "https://www.unionsupremecourt.gov.mm/uploads/projects/17415822672021%20%E1%80%85%E1%80%AE%E1%80%9B%E1%80%84%E1%80%BA%E1%80%91%E1%80%AF%E1%80%B6%E1%80%B8.pdf"}],
    "title_local": "မသီတာ နှင့် ပြည်ထောင်စုသမ္မတမြန်မာနိုင်ငံတော်",
})

# The older stub for 019-020/PUU-III/2005, now coded from the judgment.
STUB = {
    "name": "Decision 019-020/PUU-III/2005 (education requirement for workers going abroad)",
    "date": "2006-03-28", "cite": "Putusan Nomor 019-020/PUU-III/2005", "issues": ["work", "recruitment"],
    "situations": ["fees"], "stages": [1, 2], "outcome": "won", "follow": "unknown", "status": "S",
    "q": "May Law 39/2004 require every worker going abroad to have at least a junior high school education (Art. 35(d)), and do its rules on placement companies breach the Constitution?",
    "q_id": "Bolehkah UU 39/2004 mewajibkan setiap calon TKI berpendidikan sekurang-kurangnya SLTP (Pasal 35 huruf d), dan apakah ketentuan tentang pelaksana penempatan TKI swasta bertentangan dengan UUD 1945?",
    "held": "Petition 019 granted in part: Art. 35(d) (junior high school minimum) struck down, as an education limit is justified only where the job needs it and otherwise breaches the right to work (Arts. 27(2), 28A, 28H); the challenges to the rules on placement companies were rejected. Petition 020 (Indonesia Manpower Watch) not accepted for lack of standing.",
    "plain": "Associations of placement companies and an NGO challenged parts of the 2004 law on sending workers abroad. The Court struck down the rule that every worker must have finished junior high school, because schooling can only be required when the job needs it. The other challenges failed.",
    "plain_id": "Asosiasi perusahaan penempatan dan sebuah yayasan menguji sejumlah ketentuan UU 39/2004. Mahkamah membatalkan ketentuan bahwa setiap calon TKI wajib berpendidikan sekurang-kurangnya SLTP, karena syarat pendidikan hanya dapat dibenarkan apabila pekerjaan memang memerlukannya. Permohonan lainnya ditolak.",
    "tools": ["standard"], "args": [{"a": "worktoright", "ok": True}],
    "after": [{"d": "2006-03-28", "en": "Art. 35(d) of Law 39/2004 struck down.", "id": "Pasal 35 huruf d UU 39/2004 dinyatakan bertentangan dengan UUD 1945."}],
}
LINKS = {"c-id-mk-019-2005": [{"t": "Judgment (MKRI)", "u": PDF + "putusan_sidang_putusan%20019_PUU-III_2005.pdf"}]}

if __name__ == "__main__":
    json.dump({"new": NEW, "links": LINKS, "stub": {"c-id-mk-019-2005": STUB}}, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(NEW), "new;", len(LINKS), "link updates")
