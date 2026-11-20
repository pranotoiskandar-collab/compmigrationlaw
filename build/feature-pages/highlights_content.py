"""Case of the month: the write-ups. One entry per month, newest first. Each entry must point at a decision in
data/court-decisions/decisions.csv (field "id"), say on what it rests ("basis"), and carry a short social post in
English and Indonesian. Facts come only from the decision entry and the official judgment; analysis is ours and is
labelled as such. After adding an entry run:  python3 build/feature-pages/highlights.py
"""

HIGHLIGHTS = [
    {
        "month": "2026-11",
        "id": "mk-127-2023",
        "title_en": "Fishing crew are still migrant workers",
        "title_id": "Awak kapal perikanan tetap pekerja migran",
        "court_en": "Constitutional Court of Indonesia, Decision 127/PUU-XXI/2023, 29 November 2024",
        "court_id": "Mahkamah Konstitusi Republik Indonesia, Putusan Nomor 127/PUU-XXI/2023, 29 November 2024",
        "basis": "S",
        "body_en": [
            ("What the Court decided",
             "A petition asked the Constitutional Court to take ship crew and fishers out of Law 18/2017 on the Protection of "
             "Indonesian Migrant Workers. The Court rejected it. Indonesians who work on foreign fishing and merchant vessels "
             "remain migrant workers under Article 4(1)(c) of the Law, with the protection the Law gives before departure, "
             "while working abroad and after return."),
            ("Why it matters",
             "For many crew the law of their own country is the protection most within reach. Our East Asia data show how thin "
             "the destination side can be: in Taiwan, distant-water fishing crew sit outside the Labor Standards Act, under "
             "fisheries regulations with a separate wage floor well below the national minimum wage. The Court kept in place "
             "the home-state duties that the 2017 Law attaches to every migrant worker, such as a contract signed before "
             "departure, pre-departure orientation and enrolment in social security."),
            ("What to watch",
             "A ruling that keeps a law in force is only the start. Researchers and advocates may ask how the placement and "
             "protection of crew is organised under the Law after the ruling, whether the duties reach crew recruited "
             "outside the official placement system, and how complaints by crew are handled in practice. We will record what "
             "follows in the decision's follow-up field."),
        ],
        "body_id": [
            ("Putusan Mahkamah",
             "Sebuah permohonan meminta Mahkamah Konstitusi mengeluarkan awak kapal dan pelaut perikanan dari Undang-Undang "
             "Nomor 18 Tahun 2017 tentang Pelindungan Pekerja Migran Indonesia. Mahkamah menolak permohonan tersebut. Warga "
             "Indonesia yang bekerja di kapal ikan dan kapal niaga asing tetap merupakan pekerja migran menurut Pasal 4 ayat "
             "(1) huruf c undang-undang tersebut, dengan pelindungan yang diberikannya sebelum bekerja, selama bekerja, dan "
             "setelah bekerja."),
            ("Mengapa penting",
             "Bagi banyak awak kapal, hukum negaranya sendiri merupakan pelindungan yang paling dapat dijangkau. Data Asia Timur "
             "kami menunjukkan betapa tipisnya pelindungan di negara tujuan: di Taiwan, awak kapal perikanan laut lepas berada "
             "di luar Labor Standards Act, yakni di bawah peraturan perikanan dengan batas upah tersendiri yang jauh di bawah "
             "upah minimum nasional. Mahkamah mempertahankan kewajiban negara asal yang dilekatkan UU 2017 pada setiap pekerja "
             "migran, antara lain perjanjian kerja yang ditandatangani sebelum berangkat, orientasi pra pemberangkatan, dan "
             "kepesertaan jaminan sosial."),
            ("Yang perlu dicermati",
             "Putusan yang mempertahankan suatu undang-undang barulah permulaan. Peneliti dan pendamping dapat menelaah "
             "bagaimana penempatan dan pelindungan awak kapal diatur menurut undang-undang tersebut setelah putusan ini, "
             "apakah kewajiban itu menjangkau awak kapal yang direkrut di luar jalur penempatan resmi, dan bagaimana pengaduan "
             "awak kapal ditangani dalam praktik. Kami akan mencatat perkembangannya pada kolom tindak lanjut putusan ini."),
        ],
        "links": [
            ("/court-decisions/d/mk-127-2023/", "The decision in our database", "Putusan ini dalam basis data kami"),
            ("/east-asia/", "East Asia: rules for fishing crew in Taiwan and Korea", "Asia Timur: aturan bagi awak kapal di Taiwan dan Korea"),
            ("/rights-checklist/?c=TW&g=TW-DWF", "Rights checklist: distant-water crew, Taiwan", "Daftar periksa hak: awak kapal laut lepas, Taiwan"),
        ],
        "post_en": "Case of the month: Indonesia's Constitutional Court refused to take ship crew and fishers out of the migrant "
                   "worker protection law (Decision 127/PUU-XXI/2023). Crew on foreign vessels stay protected. "
                   "theimr.org/court-decisions/highlights/2026-11/",
        "post_id": "Putusan bulan ini: MK menolak mengeluarkan awak kapal dan pelaut perikanan dari UU Pelindungan Pekerja Migran "
                   "Indonesia (Putusan 127/PUU-XXI/2023). Awak kapal di kapal asing tetap dilindungi. "
                   "theimr.org/court-decisions/highlights/2026-11/",
    },
]
