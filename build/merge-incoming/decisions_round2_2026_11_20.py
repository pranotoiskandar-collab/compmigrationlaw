"""Turn the second round of incoming court decisions into Court Decisions entries (status C, unverified).

Usage: python3 build/merge-incoming/decisions_round2_2026_11_20.py SITE OUT.json
Reads   data/pacific/incoming/court-decisions-2026-11-20.csv                          (163 Pacific decisions)
        data/court-decisions/incoming/latin-america/cl-supreme-court-migration-2026-11-18.csv  (162 Chile)
        data/court-decisions/incoming/other-asia/unpaid-wages-ph-2026-11-18.csv       (32 Philippines)
        data/court-decisions/incoming/regional-intl/un-treaty-bodies-and-eacj-2026-11-18.csv (16 UN + EACJ)
        data/east-asia/incoming/judgments-jp-kr-2026-11-17.csv                         (case numbers for 3 decisions on the site)
Writes  OUT.json with {"new": [...], "links": {}, "cites": {existing_id: extra citation}} for patch_site_decisions.py.

Pranoto asked on 20 November 2026 to put every incoming row on the site. Every new entry has status C, which
the pages show as "Unverified: unchecked candidate". Sources that are not government sites (PacLII) carry
"(secondary source)" in their label. Rows already on the site (same citation, or the same per-decision link)
are skipped, so the script is safe to rerun. Topic lines come from the incoming files; Indonesian lines are
AI-drafted from those topic lines and are as unverified as the English.
"""
import csv, json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = Path(sys.argv[1])
FALLBACK_ID = "Ringkasan bahasa Indonesia sedang disiapkan. Perkara ini baru ditemukan dan belum dibaca."
SHARED_LINKS = {"https://juris.pjud.cl/busqueda?Compendio_Extranjer%C3%ADa"}  # one address for many decisions

src = (SITE / "court-decisions/cd-data.js").read_text(encoding="utf-8")
existing = json.loads(src.split("window.CD=", 1)[1].rstrip().rstrip(";"))["decisions"]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def cite_keys(cite):
    return {norm(p) for p in re.split(r"[;/]", cite) if len(norm(p)) > 5}


seen, ids = set(), {d["id"] for d in existing}
for d in existing:
    seen |= cite_keys(d.get("cite", ""))
    seen |= {s["u"].rstrip("/") for s in d.get("src", [])}


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def rows(rel):
    return list(csv.DictReader(open(ROOT / rel, encoding="utf-8")))


# ---------- coding rules ----------
SIT = {"refugee status": "residence", "asylum": "residence", "offshore processing": "residence", "residence": "residence",
       "visa": "residence", "nationality": "residence", "regularisation": "residence", "expulsion": "residence",
       "refoulement": "residence", "extradition": "residence", "entry": "residence", "free movement": "residence",
       "work permit": "residence", "detention": "arrest", "wages": "wages", "wage deductions": "wages",
       "underpayment": "wages", "dismissed": "dismissed", "trafficking": "forced", "sexual exploitation": "forced",
       "labour exploitation": "forced", "recruitment": "fees", "recruitment fraud": "fees", "fees": "fees",
       "discrimination": "discrimination", "health": "health"}
ISS = {"refugee status": "asylum", "asylum": "asylum", "offshore processing": "detention", "residence": "residence",
       "visa": "residence", "regularisation": "residence", "nationality": "nationality", "expulsion": "expulsion",
       "refoulement": "nonrefoulement", "extradition": "extradition", "entry": "mobility", "free movement": "mobility",
       "work permit": "work permission", "wages": "wages", "wage deductions": "wages", "underpayment": "wages",
       "dismissed": "dismissal", "trafficking": "trafficking", "sexual exploitation": "trafficking",
       "labour exploitation": "trafficking", "recruitment": "recruitment", "recruitment fraud": "recruitment",
       "fees": "fees", "discrimination": "discrimination", "health": "health"}
STAGE = {"fees": 1, "residence": 3, "arrest": 4, "wages": 3, "dismissed": 4, "forced": 3, "discrimination": 3, "health": 3}


def code(toks, expel_stage=4):
    toks = [t.strip() for t in toks.split(";") if t.strip()]
    sits = list(dict.fromkeys(SIT[t] for t in toks if t in SIT))
    iss = list(dict.fromkeys(ISS[t] for t in toks if t in ISS))
    st = {STAGE[s] for s in sits}
    if {"expulsion", "extradition", "refoulement"} & set(toks):
        st.add(expel_stage)
    if {"entry", "free movement"} & set(toks):
        st.add(2)
    return sits, iss, sorted(st)


def entry(**kw):
    base = dict(region="asia", forum="destination", tier="national", sector="", issues=[], situations=[], stages=[],
                outcome="unknown", follow="unknown", status="C", q="", q_id="", held="", plain_id=FALLBACK_ID,
                harvest=True, tools=[], args=[], after=[])
    base.update(kw)
    return base


new, skipped = [], []


def add(e, origin, keys=None):
    keys = keys or cite_keys(e["cite"])
    u = e["src"][0]["u"].rstrip("/")
    if keys & seen or (u in seen and u not in SHARED_LINKS) or e["id"] in ids:
        skipped.append((origin, e["id"], e["cite"]))
        return
    seen.update(keys); seen.add(u); ids.add(e["id"])
    new.append(e)


# ---------- Indonesian lines (AI-drafted from the English topic lines; unverified like them) ----------
ID_PACIFIC = {
    "Appeal under s 43 Refugees Convention Act 2012 against a refugee status decision of the Refugee Status Review Tribunal (asylum seeker transferred from Australia).":
        "Banding berdasarkan Pasal 43 Undang-Undang Konvensi Pengungsi 2012 terhadap putusan Tribunal Peninjauan Status Pengungsi (pencari suaka yang dipindahkan dari Australia).",
    "Refugee appeal: whether the Tribunal failed to consider an integer of the claim; procedural fairness (ss 34(4), 37 Refugees Convention Act 2012).":
        "Banding pengungsi: apakah Tribunal lalai menimbang satu unsur permohonan; keadilan prosedural (Pasal 34(4) dan 37 Undang-Undang Konvensi Pengungsi 2012).",
    "Appeal to the Court of Appeal from a Supreme Court decision on refugee status / complementary protection under the Refugees Convention Act 2012.":
        "Banding ke Pengadilan Banding atas putusan Mahkamah Agung Nauru tentang status pengungsi atau perlindungan pelengkap berdasarkan Undang-Undang Konvensi Pengungsi 2012.",
    "Appeal to the High Court of Australia from the Supreme Court of Nauru on refugee status (the HCA heard Nauru appeals until 2018).":
        "Banding ke High Court Australia atas putusan Mahkamah Agung Nauru tentang status pengungsi (High Court Australia memeriksa banding dari Nauru sampai 2018).",
    "Sentence for trafficking in persons and seven counts of obtaining property by deception; the court notes this is Fiji's first trafficking conviction.":
        "Hukuman atas perdagangan orang dan tujuh dakwaan memperoleh harta dengan tipu daya; pengadilan mencatat ini vonis perdagangan orang pertama di Fiji.",
    "Aggravated trafficking charges (Crimes Decree 2009 ss 112(5), 113) over three young Thai women brought to Fiji to work.":
        "Dakwaan perdagangan orang dengan pemberatan (Dekret Pidana 2009 Pasal 112(5) dan 113) atas tiga perempuan muda Thailand yang dibawa ke Fiji untuk bekerja.",
    "Sentence for trafficking in persons: three Thai women arrived at Nadi in September 2012 to work in massage parlours.":
        "Hukuman atas perdagangan orang: tiga perempuan Thailand tiba di Nadi pada September 2012 untuk bekerja di panti pijat.",
    "Appeal against trafficking conviction: two young women from Thailand recruited to work as masseuses in Fiji.":
        "Banding atas vonis perdagangan orang: dua perempuan muda dari Thailand direkrut untuk bekerja sebagai terapis pijat di Fiji.",
    "Trial judgment on a charge of trafficking in persons contrary to s 112(3) Crimes Act 2009 (offence between January and March 2015, Nadi).":
        "Putusan tingkat pertama atas dakwaan perdagangan orang berdasarkan Pasal 112(3) Undang-Undang Pidana 2009 (perbuatan antara Januari dan Maret 2015, di Nadi).",
    "Trial judgment on one count of trafficking in persons contrary to s 112(4) Crimes Act 2009.":
        "Putusan tingkat pertama atas satu dakwaan perdagangan orang berdasarkan Pasal 112(4) Undang-Undang Pidana 2009.",
    "Judicial review of an Immigration Department decision to deport a foreign national living in Fiji.":
        "Uji yudisial atas keputusan Departemen Imigrasi untuk mendeportasi warga negara asing yang tinggal di Fiji.",
    "Judicial review of a September 2018 decision of the Minister for Immigration (prohibited immigrant / removal).":
        "Uji yudisial atas keputusan Menteri Imigrasi bulan September 2018 (penetapan sebagai imigran terlarang dan pengusiran).",
    "Leave for judicial review refused: a university Vice-Chancellor on an employment-linked work and residence permit was declared a prohibited immigrant while abroad.":
        "Izin uji yudisial ditolak: seorang rektor universitas dengan izin kerja dan izin tinggal yang terkait pekerjaannya ditetapkan sebagai imigran terlarang ketika sedang di luar negeri.",
    "Appeal from refusal of leave for judicial review of the cancellation of a work permit and a prohibited-immigrant declaration (Immigration Act 2003 s 13(2)(g)).":
        "Banding atas penolakan izin uji yudisial terhadap pencabutan izin kerja dan penetapan sebagai imigran terlarang (Undang-Undang Imigrasi 2003 Pasal 13(2)(g)).",
    "Supreme Court on judicial review of declarations that foreign nationals were prohibited immigrants under s 13(2)(g) Immigration Act 2003 (after Interpol Red Notices).":
        "Mahkamah Agung Fiji tentang uji yudisial atas penetapan warga negara asing sebagai imigran terlarang berdasarkan Pasal 13(2)(g) Undang-Undang Imigrasi 2003 (setelah Red Notice Interpol).",
    "High Court judicial review of prohibited-immigrant declarations (Immigration Act, Citizenship of Fiji Act).":
        "Uji yudisial di High Court atas penetapan sebagai imigran terlarang (Undang-Undang Imigrasi dan Undang-Undang Kewarganegaraan Fiji).",
    "Sentence of several defendants found guilty of trafficking-related charges (Chief Justice Lunabek).":
        "Hukuman bagi beberapa terdakwa yang dinyatakan bersalah atas dakwaan terkait perdagangan orang (Ketua Mahkamah Agung Lunabek).",
    "Deductions from RSE workers' wages for accommodation and other costs breached the Wages Protection Act 1983 and Minimum Wage Act 1983; arrears ordered.":
        "Potongan upah pekerja musiman RSE untuk biaya penginapan dan biaya lain melanggar Undang-Undang Perlindungan Upah 1983 dan Undang-Undang Upah Minimum 1983; kekurangan upah wajib dibayar.",
    "Interlocutory judgment in the RSE deductions case (the Court agreed to hear the matter directly).":
        "Putusan sela dalam perkara potongan upah pekerja RSE (pengadilan setuju memeriksa perkara itu secara langsung).",
    "Penalties ($43,000 company, $5,500 director) for fining PALM workers under an alcohol policy and other unlawful deductions (Fair Work Act).":
        "Denda (43.000 dolar untuk perusahaan, 5.500 dolar untuk direktur) karena mendenda pekerja PALM berdasarkan aturan alkohol dan potongan upah lain yang melanggar hukum (Fair Work Act).",
    "Court-ordered penalty of about $106,000 against a labour-hire company that underpaid 87 visa holders engaged under the Pacific Labour Scheme and Seasonal Worker Programme.":
        "Pengadilan menjatuhkan denda sekitar 106.000 dolar kepada perusahaan penyalur tenaga kerja yang kurang membayar 87 pemegang visa dalam Pacific Labour Scheme dan Seasonal Worker Programme.",
    "Penalties against a Queensland labour-hire operator for 'appalling' treatment of 22 Vanuatu workers under the Seasonal Worker Programme (underpaid $77,649).":
        "Denda bagi penyalur tenaga kerja di Queensland karena perlakuan yang “sangat buruk” terhadap 22 pekerja Vanuatu dalam Seasonal Worker Programme (kurang bayar 77.649 dolar).",
}

ID_PH = [
    "Arsitek yang dipecat di Arab Saudi; gaji untuk sisa masa kontrak, selisih gaji, dan pengembalian potongan biaya telepon dikuatkan.",
    "Pekerja konstruksi di luar negeri; NLRC menambahkan gaji untuk sisa masa kontrak pada gaji yang belum dibayar; permohonan agen ditolak.",
    "Tuntutan sopir di luar negeri atas kekurangan upah, lembur yang tidak dibayar, dan bonus kontrak; apakah POEA atau arbiter ketenagakerjaan yang berwenang.",
    "Pelaut yang diberhentikan sebelum kontrak berakhir mendapat gaji untuk sisa masa kontrak; uang lembur tetap dihapus.",
    "Tuntutan pelaut atas gaji sisa masa kontrak dan selisih gaji; pembatalan oleh NLRC dikesampingkan dan pekerja dimenangkan.",
    "Pelaut mendapat gaji untuk sisa masa kontrak; lembur tetap sebesar 2.250 dolar AS dihapus karena kerja lembur tidak terbukti.",
    "Tuntutan pelaut berdasarkan kontrak yang disetujui POEA atas gaji yang belum dibayar, lembur tetap, dan uang cuti; putusan NLRC dikuatkan.",
    "Pekerja di Hong Kong diberhentikan sebelum kontrak berakhir; gaji sisa masa kontrak sebesar 55.000 dolar Hong Kong dikuatkan terhadap agen.",
    "Tuntutan pekerja yang dipecat atas gaji yang belum dibayar, ongkos pesawat yang dipotong dari upah, uang cuti, dan gaji sisa masa kontrak.",
    "Pelaut dipecat tanpa proses yang layak; putusan gaji termasuk lembur tetap untuk sisa masa kontrak dikuatkan.",
    "Tuntutan pekerja di luar negeri atas gaji sisa masa kontrak dan lembur; tanggung jawab dibagi antara dua agen perekrutan.",
    "Gaji, lembur, cuti, dan tunjangan pelaut untuk sisa masa kontrak; putusan POEA dipulihkan.",
    "Pengaduan pekerja kapal pesiar atas upah sisa masa kontrak dan lembur; agen dan pemberi kerja di luar negeri bertanggung jawab bersama.",
    "Cara menghitung gaji yang terutang untuk sisa masa kontrak di Arab Saudi (tiga bulan atau seluruh sisa masa kontrak).",
    "Pramusaji perempuan di Arab Saudi; gaji yang belum dibayar, selisih gaji, dan gaji sisa masa kontrak setelah dipecat karena sakit.",
    "Pekerja di Angola; tuntutan selisih gaji, potongan upah untuk kerusakan kendaraan, dan uang lembur.",
    "Pelaut dipulangkan sebelum kontrak berakhir; gaji sisa masa kontrak dan biaya pengacara dikuatkan.",
    "Tuntutan pelaut atas gaji sisa masa kontrak, potongan tanpa izin, dan diskriminasi karena berkebangsaan Filipina; putusan POEA dipulihkan.",
    "Pekerja rumah tangga di Taiwan dipecat tanpa alasan; gaji sisa masa kontrak sebesar 151.996 dolar Taiwan dikuatkan.",
    "Tuntutan pelaut atas gaji sisa masa kontrak, lembur yang tidak dibayar, uang cuti, dan selisih gaji; jumlah putusan dibatasi oleh Mahkamah.",
    "Pengaduan pelaut atas pemecatan tidak sah serta gaji dan tunjangan yang belum dibayar untuk sisa masa kontrak; putusan dikuatkan.",
    "Gaji pelaut yang belum dibayar, lembur tetap, tunjangan, uang cuti, dan pesangon; putusan NLRC dipulihkan.",
    "Upah pelaut yang belum dibayar dipakai untuk biaya pemulangannya; tuntutan atas upah, tunjangan sakit, dan biaya pengobatan dikabulkan.",
    "Hukum mana yang berlaku bagi kontrak kerja di luar negeri; gaji sisa masa kontrak berdasarkan Republic Act 8042.",
    "Pelaut yang mengadukan perlakuan buruk terhadap awak kapal Filipina; pemecatan dinyatakan tidak sah dan gaji wajib dibayar berdasarkan RA 8042.",
    "Pekerja di Uni Emirat Arab dipecat secara tidak sah; tiga bulan gaji berdasarkan Pasal 10 RA 8042; uang lembur dan uang hari libur ditolak.",
    "Gaji dan tunjangan perwira kapal yang belum dibayar serta lembur yang dijamin; putusan Pengadilan Banding dibatalkan.",
    "Awak kapal dipulangkan sebelum kontrak berakhir; upah yang belum dibayar dan gaji sisa masa kontrak beserta ganti rugi dikuatkan.",
    "Pekerja konstruksi di luar negeri mendapat gaji untuk seluruh sisa masa kontraknya.",
    "Pekerja yang dipecat mendapat pengembalian biaya penempatan dan gaji sisa masa kontrak; lembur dan uang hari libur yang dijamin dihapus.",
    "Tuntutan pelaut atas gaji sisa masa kontrak, lembur tetap, dan tunjangan; putusan dikuatkan dengan perubahan.",
    "Pekerja di Taiwan mendapat tiga bulan gaji yang belum dibayar berdasarkan Pasal 10 RA 8042; putusan bantuan keuangan diubah.",
]

ID_UN = [
    "Warga Ekuador diserahkan kepada aparat Amerika Serikat tanpa prosedur ekstradisi; Komite meninjau pengusiran tanpa proses hukum yang layak.",
    "Libya menyita paspor seorang pria yang tinggal di luar negeri sehingga keluarganya tidak bisa pergi menyusulnya; kebebasan meninggalkan negara dan hak atas kehidupan keluarga.",
    "Kazakhstan mengekstradisi warga Kirgizstan ke Kirgizstan meski ada risiko penyiksaan; larangan pemulangan paksa (non-refoulement).",
    "Migran dari Afrika Tengah diusir oleh Maroko ke perbatasan gurun Aljazair; larangan pemulangan paksa dan pengusiran massal.",
    "Maroko memerintahkan ekstradisi seorang perempuan ke Arab Saudi; risiko penyiksaan setelah dipulangkan.",
    "Ekstradisi dari Maroko ke Tunisia; risiko penyiksaan.",
    "Uzbekistan dan pengusiran warga negara asing; larangan pemulangan paksa (fakta perlu dicek).",
    "Maroko mengekstradisi warga Turki ke Turki; risiko penyiksaan.",
    "Maroko mengekstradisi warga Turki ke Turki; risiko penyiksaan.",
    "Maroko mengekstradisi warga Turki ke Turki; risiko penyiksaan.",
    "Ekstradisi dari Maroko ke Mesir; risiko penyiksaan.",
    "Pengusiran warga Turki dari Maroko; larangan pemulangan paksa.",
    "Angola dan pengusiran warga negara asing; larangan pemulangan paksa (fakta perlu dicek).",
    "Azerbaijan memulangkan dua orang ke negara tempat mereka berisiko disiksa; larangan pemulangan paksa (fakta perlu dicek).",
    "Maroko dan pengusiran seseorang yang berisiko disiksa di luar negeri; larangan pemulangan paksa (fakta perlu dicek).",
    "Advokat Kenya ditolak masuk ke Uganda, ditahan, lalu dipulangkan; penolakan masuk terhadap warga negara anggota Komunitas Afrika Timur tanpa proses yang layak melanggar Traktat EAC dan Protokol Pasar Bersama; Pasal 52 Undang-Undang Kewarganegaraan dan Pengawasan Imigrasi Uganda tidak berlaku bagi warga EAC.",
]

CL_SUBJ = {"permanent residence (permanencia definitiva)": ("permanent residence", "izin tinggal tetap (permanencia definitiva)"),
           "temporary visa (visa temporal)": ("temporary visa", "visa sementara (visa temporal)"),
           "migration regularisation (regularización migratoria)": ("regularisation", "regularisasi status migrasi (regularización migratoria)"),
           "naturalisation (nacionalización)": ("naturalisation", "naturalisasi (nacionalización)")}
CL_RES = {"Supreme Court reversed the appeals court ruling.": "Mahkamah Agung membatalkan putusan pengadilan banding.",
          "Supreme Court confirmed the appeals court ruling.": "Mahkamah Agung menguatkan putusan pengadilan banding.",
          "Supreme Court rejected the protection appeal.": "Mahkamah Agung menolak permohonan perlindungan."}
NAT_ID = {"Venezuela": "Venezuela", "Colombia": "Kolombia", "Peru": "Peru", "Haiti": "Haiti", "Bolivia": "Bolivia",
          "Ecuador": "Ekuador", "Dominican Republic": "Republik Dominika", "Cuba": "Kuba", "Argentina": "Argentina",
          "China": "Tiongkok", "Spain": "Spanyol", "Brazil": "Brasil", "Paraguay": "Paraguay", "Mexico": "Meksiko"}


def cl_id(topic):
    m = re.match(r"Protection appeal against the migration service on (.+?)\. (Supreme Court .+?\.) Applicant nationality as listed: (.*)\.?$", topic)
    if not m:
        return FALLBACK_ID
    subj = CL_SUBJ.get(m.group(1), (None, m.group(1)))[1]
    nat = m.group(3).rstrip(".").strip()
    nat_id = " ".join(NAT_ID.get(w, w) for w in nat.split()) if nat else ""
    s = f"Permohonan perlindungan (recurso de protección) terhadap dinas migrasi tentang {subj}. {CL_RES.get(m.group(2), '')}"
    return s + (f" Kewarganegaraan pemohon menurut daftar: {nat_id}." if nat_id else "")


# ---------- 1. Pacific ----------
def pac_level(court):
    c = court.lower()
    if "high court of australia" in c or "supreme court of fiji" in c:
        return "apex"
    if "court of appeal" in c or "full court" in c:
        return "appeal"
    return "first"


def pac_branch(toks, court):
    t = toks.lower()
    if "trafficking" in t:
        return "criminal"
    if "wage" in t or "underpayment" in t:
        return "private"
    return "administrative"


for r in rows("data/pacific/incoming/court-decisions-2026-11-20.csv"):
    cite = r["case_no"]
    first = cite.split(";")[0]
    if "[citation to be added]" in cite:
        first = r["name"]
        cite = cite.replace("[citation to be added]", "").strip() or f"{r['name']} (citation to be added)"
    yr = r["date"][:4]
    eid = f"c-l-{r['country'].lower()}-{slug(first)}"
    if yr and yr not in eid:
        eid += f"-{yr}"
    sits, iss, st = code(r["situations"])
    tier = r["source_tier"]
    if tier.startswith("PacLII"):
        label = "PacLII (Pacific Islands Legal Information Institute) (secondary source)"
    elif "Fair Work Ombudsman" in tier:
        label = "Fair Work Ombudsman, Australia: media release (official guidance)"
    elif "Employment Court" in tier:
        label = "Employment Court of New Zealand"
    else:
        label = tier
    sector = r["sector"]
    if r["country"] == "NR":
        sector = "asylum seekers and refugees"
    elif sector == "agriculture":
        sector = "agriculture (seasonal workers)"
    court = r["court"]
    if r["country"] == "NR" and "Nauru" not in court:
        court = court  # "High Court of Australia (appeals from Nauru)" already says so
    e = entry(id=eid, name=r["name"], court=court, cc=r["country"], region="pacific", level=pac_level(court),
              date=r["date"], cite=cite, branch=pac_branch(r["situations"], court), sector=sector,
              issues=iss, situations=sits, stages=st, plain=r["topic_first_read"],
              plain_id=ID_PACIFIC.get(r["topic_first_read"], FALLBACK_ID), src=[{"t": label, "u": r["official_link"]}])
    # Fiji judgment and sentence share one file number (HAC...), so only the report citation counts there.
    add(e, "pacific", cite_keys(cite.split(";")[0]) if r["country"] == "FJ" else None)

# ---------- 2. Chile ----------
for r in rows("data/court-decisions/incoming/latin-america/cl-supreme-court-migration-2026-11-18.csv"):
    rol = r["case_no"].replace("Rol N° ", "")
    sits, iss, st = code(r["situations"])
    e = entry(id=f"c-l-cl-cs-rol-{slug(rol)}", name=r["name"], court="Supreme Court of Chile (Third Chamber)", cc="CL",
              region="latam", level="apex", date=r["date"], cite=r["case_no"], branch="constitutional",
              issues=iss, situations=sits, stages=st, plain=r["topic_first_read"], plain_id=cl_id(r["topic_first_read"]),
              src=[{"t": f"Poder Judicial de Chile, Compendio Extranjería (search Rol {rol})", "u": r["official_link"]}])
    add(e, "chile")

# ---------- 3. Philippines, unpaid wages ----------
SECTOR_PH = {"seafaring": "seafarers"}
for i, r in enumerate(rows("data/court-decisions/incoming/other-asia/unpaid-wages-ph-2026-11-18.csv")):
    gr = r["case_no"].replace("G.R. No. ", "")
    sits, iss, st = code(r["situations"])
    sector = SECTOR_PH.get(r["sector"], r["sector"])
    if sector.startswith("domestic work"):
        sector = "domestic work"
    e = entry(id=f"c-l-ph-gr-{slug(gr)}-{r['date'][:4]}", name=r["name"], court=r["court"], cc="PH", region="asia",
              forum="origin", level="apex", date=r["date"], cite=r["case_no"], branch="private", sector=sector,
              issues=iss, situations=sits, stages=st, plain=r["topic_first_read"], plain_id=ID_PH[i],
              src=[{"t": "Supreme Court E-Library", "u": r["official_link"]}])
    add(e, "ph-wages")

# ---------- 4. UN treaty bodies and the EACJ ----------
for i, r in enumerate(rows("data/court-decisions/incoming/regional-intl/un-treaty-bodies-and-eacj-2026-11-18.csv")):
    sits, iss, st = code(r["situations"])
    eacj = "East African Court" in r["court"]
    body = "cat" if "Torture" in r["court"] else ("eacj" if eacj else "ccpr")
    num = r["case_no"] or r["name"]
    cite = r["case_no"] or f"{r['name']} (communication number to be added)"
    if eacj:
        sits = ["residence", "arrest"]; st = [2, 4]
    e = entry(id=f"c-l-{r['country'].lower()}-{body}-{slug(num.replace('Communication No. ', '').replace('Reference No. ', 'ref-'))}",
              name=r["name"], court=r["court"], cc=r["country"],
              region="africa" if eacj else "intl", tier="regional" if eacj else "international",
              forum="regional" if eacj else "international", level="regional" if eacj else "international",
              date=r["date"], cite=cite, branch="constitutional", issues=iss, situations=sits, stages=st,
              plain=r["topic_first_read"], plain_id=ID_UN[i],
              src=[{"t": "East African Court of Justice" if eacj else "OHCHR jurisprudence database", "u": r["official_link"]}])
    add(e, "un-eacj")

# ---------- 5. Japan and Korea: case numbers for decisions already on the site ----------
cites = {}
byname = {d["name"]: d for d in existing}
for r in rows("data/east-asia/incoming/judgments-jp-kr-2026-11-17.csv"):
    if not r["site_status"].startswith("ON SITE"):
        continue
    hit = None
    m = re.search(r"ON SITE as '([^']+?)(?:\.\.\.)?'", r["site_status"])
    if m:
        hit = next((d for d in existing if d["name"].startswith(m.group(1)) and d["cc"] == r["country"]), None)
    m2 = re.search(r"ON SITE \(Supreme Court (\S+)\)", r["site_status"])
    if m2:
        hit = next((d for d in existing if m2.group(1) in d.get("cite", "")), None)
    if hit and not (cite_keys(r["case_no"].replace(" / ", "; ")) & cite_keys(hit.get("cite", ""))):
        cites[hit["id"]] = {"cite": r["case_no"].replace(" / ", "; "), "src": {"t": "Courts in Japan (courts.go.jp)" if r["country"] == "JP"
                            else "law.go.kr (National Law Information Center)", "u": r["official_link"]}}
    elif not hit:
        skipped.append(("jp-kr on-site", r["case_no"], "decision not found"))

json.dump({"new": new, "links": {}, "cites": cites}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("new entries:", len(new), Counter(e["cc"] for e in new))
print("case numbers added to existing entries:", len(cites), list(cites))
print("skipped as duplicates or already on the site:", len(skipped))
for s in skipped:
    print("  ", *s)
dup_ids = [k for k, v in Counter(e["id"] for e in new).items() if v > 1]
assert not dup_ids, dup_ids
