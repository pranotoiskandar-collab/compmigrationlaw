"""Build site/rights-checklist/checklist-data.json, the data behind the "know your rights before you go" sheets.

Everything on a sheet comes from the databases; nothing is coded here:
  * destination rules for domestic workers   data/domestic-workers/codings.csv (17 features, labels in EN and ID)
  * destination rules for other jobs          data/east-asia/codings.csv and data/southeast-asia/codings.csv
                                              (10 features of the East Asia codebook; the Indonesian labels below
                                              are translations of data/east-asia/codebook.csv)
  * Indonesia's duties before departure       data/domestic-workers/codings.csv, role = origin, country = ID
  * treaties                                  data/ratifications/ratifications.csv
  * where to get help                         site/legal-help/places.js (phones verified there)

What this file adds is wording only: a plain question and a plain "what to do" line for each feature, in
Indonesian and English. Rerun after any of the sources change:
    python3 build/feature-pages/rights_checklist_data.py
"""
import csv
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "site", "rights-checklist", "checklist-data.json")


def rows(path):
    with open(os.path.join(DATA, path), newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


# Main destinations of Indonesian migrant workers, with the groups the databases code for each.
COUNTRIES = [
    ("MY", "Malaysia", "Malaysia", ["PRT", "MY-PLT"]),
    ("SG", "Singapura", "Singapore", ["PRT", "SG-WP"]),
    ("HK", "Hong Kong", "Hong Kong", ["PRT"]),
    ("TW", "Taiwan", "Taiwan", ["PRT", "TW-C", "TW-DWF"]),
    ("KR", "Korea Selatan", "South Korea", ["KR-E9", "KR-E10"]),
    ("JP", "Jepang", "Japan", ["JP-SSW", "JP-TITP"]),
    ("BN", "Brunei Darussalam", "Brunei", ["BN-FW"]),
    ("SA", "Arab Saudi", "Saudi Arabia", ["PRT"]),
    ("AE", "Uni Emirat Arab", "United Arab Emirates", ["PRT"]),
    ("QA", "Qatar", "Qatar", ["PRT"]),
    ("KW", "Kuwait", "Kuwait", ["PRT"]),
    ("OM", "Oman", "Oman", ["PRT"]),
    ("BH", "Bahrain", "Bahrain", ["PRT"]),
]

GROUP_ID = {
    "PRT": ("Pekerja rumah tangga (PRT), termasuk pengasuh di rumah", "Domestic workers, including carers in the home"),
    "MY-PLT": ("Pekerja perkebunan dan pertanian", "Plantation and farm workers"),
    "SG-WP": ("Pemegang Work Permit (konstruksi, pabrik, galangan kapal, jasa)", "Work Permit holders (construction, manufacturing, shipyards, services)"),
    "TW-C": ("Nelayan kapal pantai dan lepas pantai", "Coastal and offshore fishers"),
    "TW-DWF": ("Awak kapal ikan jarak jauh (laut lepas)", "Distant-water fishing crew"),
    "KR-E9": ("Pekerja perikanan pantai dan budidaya (visa E-9)", "Coastal fishing and aquaculture workers (E-9 visa)"),
    "KR-E10": ("Awak kapal 20 ton ke atas (visa E-10)", "Crew of vessels of 20 tons and over (E-10 visa)"),
    "JP-SSW": ("Pekerja berketerampilan khusus (Tokutei Ginou / SSW)", "Specified skilled workers (SSW)"),
    "JP-TITP": ("Peserta magang teknis (Ginou Jisshu / TITP)", "Technical intern trainees (TITP)"),
    "BN-FW": ("Pekerja konstruksi dan pertanian", "Construction and farm workers"),
}

# Plain questions and actions, per feature. Keys: domestic-workers codebook (destination role) and East Asia codebook.
FEATURES = {
    # domestic-workers codebook
    "cov": ("Apakah hukum ketenagakerjaan melindungi anda?", "Does labor law protect you?",
            "Tanyakan undang-undang mana yang mengatur pekerjaan anda, dan simpan namanya.", "Ask which law covers your job and keep its name."),
    "con": ("Apakah anda harus mendapat kontrak tertulis dalam bahasa yang anda pahami?", "Must you get a written contract in a language you understand?",
            "Minta kontrak dalam bahasa Indonesia. Baca sebelum tanda tangan. Simpan fotonya di HP.", "Ask for the contract in your language. Read it before signing. Keep a photo on your phone."),
    "wage": ("Apakah upah minimum berlaku bagi anda?", "Does a minimum wage apply to you?",
             "Pastikan jumlah upah tertulis di kontrak.", "Make sure the wage is written in the contract."),
    "pay": ("Apakah upah harus dibayar rutin dan tercatat?", "Must your wage be paid regularly and on record?",
            "Catat setiap pembayaran upah: tanggal, jumlah, dan potongan.", "Write down every payment: date, amount and deductions."),
    "hrs": ("Apakah jam kerja anda dibatasi?", "Are your working hours limited?",
            "Catat jam mulai dan selesai kerja setiap hari.", "Write down when you start and stop work each day."),
    "rest": ("Apakah anda berhak libur mingguan?", "Do you have a right to a weekly day off?",
             "Pastikan hari libur tertulis di kontrak.", "Make sure your day off is written in the contract."),
    "leave": ("Apakah anda berhak cuti tahunan dibayar?", "Do you have a right to paid annual leave?",
              "Tanyakan berapa hari cuti anda per tahun.", "Ask how many days of leave you get each year."),
    "doc": ("Apakah anda boleh menyimpan paspor sendiri?", "May you keep your own passport?",
            "Simpan foto paspor, visa, dan kontrak di HP dan kirim ke keluarga.", "Keep photos of your passport, visa and contract on your phone and send them to your family."),
    "live": ("Apakah ada aturan tentang tempat tinggal dan privasi anda?", "Are there rules on your living conditions and privacy?",
             "Tanyakan di mana anda akan tidur dan apakah ada kamar sendiri.", "Ask where you will sleep and whether you get your own room."),
    "mob": ("Bisakah anda pindah majikan?", "Can you change employer?",
            "Jika tidak bisa pindah tanpa izin majikan, pastikan majikan dan pekerjaan sesuai janji sebelum berangkat.", "If you cannot change without the employer's consent, check the employer and the job before you leave."),
    "fee": ("Apakah biaya perekrutan dilarang di negara tujuan?", "Are recruitment fees banned in the destination?",
            "Jangan membayar agen di luar ketentuan. Minta kuitansi untuk setiap pembayaran.", "Do not pay agents more than the rules allow. Get a receipt for every payment."),
    "agen": ("Apakah agen harus berizin dan bertanggung jawab?", "Must agencies be licensed and liable?",
             "Catat nama dan nomor izin agen di Indonesia dan di negara tujuan.", "Write down the name and licence number of the agency at home and abroad."),
    "insp": ("Apakah ada pengawasan ketenagakerjaan untuk pekerjaan anda?", "Is there labor inspection for your job?",
             "Simpan nomor kantor ketenagakerjaan setempat.", "Keep the number of the local labor office."),
    "disp": ("Ke mana anda bisa mengadu jika ada sengketa?", "Where can you complain if there is a dispute?",
             "Simpan nomor pengaduan di bawah. Bukti tertulis membantu pengaduan anda.", "Keep the complaint numbers below. Written evidence helps your complaint."),
    "soc": ("Apakah anda mendapat jaminan sosial dan perlindungan kehamilan?", "Do you get social security and maternity protection?",
            "Tanyakan asuransi apa yang dibayar majikan.", "Ask which insurance the employer pays for."),
    "viol": ("Apakah hukum melindungi anda dari kekerasan dan pelecehan?", "Does the law protect you from abuse and harassment?",
             "Jika terjadi kekerasan, cari tempat aman dan hubungi nomor di bawah.", "If there is violence, get to a safe place and call a number below."),
    "org": ("Bolehkah anda bergabung dengan serikat atau perkumpulan pekerja?", "May you join a union or workers' association?",
            "Cari perkumpulan pekerja Indonesia di kota tujuan.", "Look for an Indonesian workers' association in the city you go to."),
    # East Asia codebook (also used on the Southeast Asia page)
    "lab": ("Apakah undang-undang ketenagakerjaan berlaku bagi anda?", "Does the labor statute apply to you?",
            "Tanyakan undang-undang mana yang mengatur pekerjaan anda, dan simpan namanya.", "Ask which law covers your job and keep its name."),
    "hours": ("Apakah jam kerja dan waktu istirahat anda dibatasi?", "Are your working hours and rest protected?",
              "Catat jam mulai dan selesai kerja setiap hari.", "Write down when you start and stop work each day."),
    "union": ("Bolehkah anda bergabung dengan serikat pekerja?", "May you join a union?",
              "Cari perkumpulan pekerja Indonesia di kota tujuan.", "Look for an Indonesian workers' association in the city you go to."),
    "fees": ("Apakah biaya perekrutan dilarang di negara tujuan?", "Are recruitment fees banned in the destination?",
             "Jangan membayar agen di luar ketentuan. Minta kuitansi untuk setiap pembayaran.", "Do not pay agents more than the rules allow. Get a receipt for every payment."),
    "ins": ("Apakah anda didaftarkan dalam asuransi sosial?", "Are you enrolled in social insurance?",
            "Tanyakan asuransi apa yang dibayar majikan, dan minta nomor kepesertaannya.", "Ask which insurance the employer pays for and get the member number."),
    "comp": ("Adakah saluran pengaduan khusus dalam bahasa anda?", "Is there a complaint channel in your language?",
             "Simpan nomor pengaduan di bawah sebelum berangkat.", "Save the complaint numbers below before you leave."),
    "res": ("Apakah masa kerja anda dihitung untuk izin tinggal tetap?", "Does your time count toward permanent residence?",
            "Tanyakan berapa lama anda boleh tinggal dan apakah bisa diperpanjang.", "Ask how long you may stay and whether it can be extended."),
    "fam": ("Bolehkah keluarga ikut?", "May your family come with you?",
            "Rencanakan komunikasi rutin dengan keluarga di rumah.", "Plan regular contact with your family at home."),
}

# Indonesian level labels for the East Asia codebook (English is in data/east-asia/codebook.csv).
EA_ID = {
    "lab": ("UU ketenagakerjaan umum berlaku penuh", "UU ketenagakerjaan berlaku dengan pengecualian, atau ada UU khusus sektor", "Hanya peraturan administratif di luar UU ketenagakerjaan"),
    "wage": ("Upah minimum nasional berlaku", "Ada batas upah tersendiri yang lebih rendah atau tidak terkait upah minimum nasional", "Tidak ada batas upah"),
    "hours": ("Batas jam kerja menurut undang-undang berlaku", "Hanya waktu istirahat minimum, atau batas jam kerja dengan pengecualian sektor", "Dikecualikan dari aturan jam kerja"),
    "mob": ("Boleh pindah majikan tanpa izin majikan", "Boleh pindah hanya dengan alasan tertentu, terbatas, atau dengan persetujuan pemerintah", "Tidak bisa pindah tanpa izin majikan"),
    "union": ("Boleh membentuk dan bergabung dengan serikat dengan syarat yang sama", "Boleh bergabung tetapi ada batasan hukum, atau status tinggal membuatnya sulit", "Dilarang"),
    "fees": ("Biaya yang dibebankan kepada pekerja dilarang oleh hukum negara tujuan", "Biaya yang dibebankan kepada pekerja dibatasi atau diatur", "Biaya tidak diatur"),
    "ins": ("Didaftarkan dalam asuransi ketenagakerjaan atau kesehatan nasional", "Hanya asuransi swasta atau kecelakaan yang dibeli majikan", "Tidak ada kewajiban asuransi"),
    "comp": ("Ada saluran pengaduan publik khusus pekerja migran dalam bahasa mereka", "Hanya saluran umum, atau saluran yang sulit dijangkau dari tempat kerja (misalnya di laut)", "Tidak ada saluran yang dapat dijangkau"),
    "res": ("Masa kerja dihitung untuk izin tinggal tetap", "Bisa pindah ke status lain yang dapat mengarah ke izin tinggal tetap, dengan syarat", "Tidak ada jalur: masa tinggal maksimum tetap, atau masa kerja tidak dihitung"),
    "fam": ("Pasangan dan anak boleh ikut atau menyusul", "Hanya pada status berikutnya atau dengan syarat", "Dilarang"),
}

# Before departure: Indonesia's own rules (origin codings for ID), in plain words.
ORIGIN = {
    "ocon": ("Tanda tangani perjanjian kerja sebelum berangkat, di depan petugas. Baca isinya dan minta salinannya.",
             "Sign the employment contract before you leave, in front of an official. Read it and ask for a copy."),
    "ofee": ("Untuk 10 jabatan, termasuk pekerja rumah tangga, anda tidak boleh dibebani biaya penempatan. Tanyakan apakah pekerjaan anda termasuk.",
             "For 10 occupations, including domestic work, you must not be charged placement costs. Ask whether your job is one of them."),
    "pdo": ("Ikuti Orientasi Pra Pemberangkatan (OPP). Ini wajib dan gratis.", "Attend the pre-departure orientation. It is compulsory and free."),
    "wel": ("Pastikan anda terdaftar di BPJS Ketenagakerjaan sebelum berangkat, dan simpan nomor kartunya.",
            "Make sure you are registered with BPJS Ketenagakerjaan before you leave, and keep the card number."),
    "att": ("Catat alamat KBRI atau KJRI di negara tujuan. Nomor resminya ada di aplikasi Safe Travel Kementerian Luar Negeri.",
            "Write down the address of the Indonesian embassy or consulate. Its official numbers are in the Foreign Ministry's Safe Travel app."),
    "exit": ("Penempatan PRT pada majikan perseorangan di 19 negara Timur Tengah dihentikan sejak 2015, kecuali jalur resmi uji coba ke Arab Saudi. Tawaran di luar jalur resmi berisiko tinggi.",
             "Placement of domestic workers with private employers in 19 Middle East countries has been suspended since 2015, except a pilot official channel to Saudi Arabia. Offers outside official channels are high-risk."),
}
ALWAYS = [
    ("Berangkat lewat jalur resmi. Periksa izin perusahaan penempatan (P3MI) di situs KP2MI (dulu BP2MI) sebelum menyerahkan dokumen atau uang.",
     "Leave through official channels. Check the placement company's licence on the KP2MI (formerly BP2MI) website before handing over documents or money."),
    ("Simpan foto paspor, visa, kontrak, dan kuitansi di HP, dan kirim salinannya ke keluarga.",
     "Keep photos of your passport, visa, contract and receipts on your phone, and send copies to your family."),
]


def help_places():
    js = "global.window={};require(%r);process.stdout.write(JSON.stringify(window.LEGAL_HELP.places));" % os.path.join(ROOT, "site", "legal-help", "places.js")
    places = json.loads(subprocess.check_output(["node", "-e", js]))
    out = {}
    for p in places:
        if not p.get("tel") and not p.get("web"):
            continue
        out.setdefault(p["c"], []).append({k: p.get(k) for k in ("t", "n", "city", "city_id", "tel", "web", "d", "d_id", "hours", "hours_id", "checked") if p.get(k)})
    return out


def main():
    dw = rows("domestic-workers/codings.csv")
    dw_book = {r["feature"]: r for r in rows("domestic-workers/codebook.csv") if r["role"] == "destination"}
    ea_book = {r["k"]: r for r in rows("east-asia/codebook.csv")}
    ea = rows("east-asia/codings.csv") + rows("southeast-asia/codings.csv")
    rat = rows("ratifications/ratifications.csv")
    places = help_places()

    def item(feat, value, lab_id, lab_en, note, source, evidence, coded, checked=""):
        q = FEATURES[feat]
        return {"f": feat, "v": value, "q_id": q[0], "q_en": q[1], "do_id": q[2], "do_en": q[3],
                "a_id": lab_id, "a_en": lab_en, "note_en": note, "src": source, "ev": evidence,
                "coded": coded, "checked": checked}

    out = {"built": "", "countries": []}
    for iso, name_id, name_en, groups in COUNTRIES:
        c = {"iso2": iso, "id": name_id, "en": name_en, "groups": [], "treaties": {}, "help": places.get(iso, [])}
        for g in groups:
            items = []
            if g == "PRT":
                for r in dw:
                    if r["country"] == iso and r["role"] == "destination":
                        b = dw_book[r["feature"]]
                        v = r["value"]
                        lab_id = b.get(v + "_id", "") if v in ("0", "1", "2") else "Belum jelas"
                        items.append(item(r["feature"], v, lab_id, r["value_label"], r["note"], r["source"], r["evidence"], r["coded"]))
                db = "domestic-workers"
            else:
                for r in ea:
                    if r["group"] == g:
                        v = r["value"]
                        lab_id = EA_ID[r["feature"]][2 - int(v)] if v in ("0", "1", "2") else "Belum jelas"
                        items.append(item(r["feature"], v, lab_id, r["value_label"], r["note"], r["source"], r["evidence"], r["coded"],
                                          r.get("checked_official_text", "")))
                db = "east-asia" if iso in ("TW", "KR", "JP", "HK") else "southeast-asia"
            if items:
                c["groups"].append({"k": g, "id": GROUP_ID[g][0], "en": GROUP_ID[g][1], "db": db, "items": items})
        for r in rat:
            if r["iso2"] == iso:
                c["treaties"][r["instrument"]] = {"s": r["status"], "d": r["date_ratified"] or r["date_signed"], "f": r["binding_now"]}
        out["countries"].append(c)

    origin = []
    for r in dw:
        if r["country"] == "ID" and r["role"] == "origin" and r["feature"] in ORIGIN:
            t = ORIGIN[r["feature"]]
            origin.append({"f": r["feature"], "id": t[0], "en": t[1], "src": r["source"], "ev": r["evidence"], "v": r["value"]})
    order = ["ocon", "ofee", "pdo", "wel", "att", "exit"]
    origin.sort(key=lambda o: order.index(o["f"]))
    out["before"] = [{"id": a, "en": b, "src": "", "ev": ""} for a, b in ALWAYS] + origin
    out["home_help"] = places.get("ID", [])
    out["id_treaties"] = {r["instrument"]: {"s": r["status"], "d": r["date_ratified"] or r["date_signed"]} for r in rat if r["iso2"] == "ID"}
    import datetime
    out["built"] = datetime.date.today().isoformat()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print("%d countries, %d sheets -> %s" % (len(out["countries"]), sum(len(c["groups"]) for c in out["countries"]), OUT))


if __name__ == "__main__":
    main()
