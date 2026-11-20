# Plain-language wording for the country sheets, English and Indonesian.
# Each answer restates one level of the Countries of Origin codebook
# (data/countries-of-origin/codebook.csv and protection-codebook.csv) in short, everyday words.
# If the codebook changes, change the matching answer here.

COUNTRY_NAMES = {
    'ID': ('Indonesia', 'Indonesia'), 'PH': ('the Philippines', 'Filipina'),
    'NP': ('Nepal', 'Nepal'), 'BD': ('Bangladesh', 'Bangladesh'), 'VN': ('Viet Nam', 'Vietnam'),
    'IN': ('India', 'India'), 'LK': ('Sri Lanka', 'Sri Lanka'), 'PK': ('Pakistan', 'Pakistan'),
}
# Short form used in headings ("the Philippines" reads badly in "Philippines's law").
SHORT = {'PH': ('the Philippines', 'Filipina')}

LEVEL = {
    2: ('Strong', 'Kuat'),
    1: ('Partial', 'Sebagian'),
    0: ('None', 'Tidak ada'),
}

# key, icon, (EN label, ID label), {level: (EN answer, ID answer)}
FEATURES = [
    ('fees', 'coin', ('Agency fees', 'Biaya agensi'), {
        2: ('By law, workers do not pay recruitment fees.',
            'Menurut hukum, pekerja tidak membayar biaya rekrutmen.'),
        1: ('The law limits fees, or bans them only for some jobs or countries.',
            'Hukum membatasi biaya tersebut, atau melarangnya hanya untuk pekerjaan atau negara tujuan tertentu.'),
        0: ('The law sets no limit on fees.',
            'Hukum tidak membatasi biaya yang dibebankan kepada pekerja.')}),
    ('contract', 'doc', ('Written contract', 'Kontrak tertulis'), {
        2: ('You must get a written contract, checked by the government, before you leave.',
            'Anda wajib menerima kontrak kerja tertulis yang diperiksa pemerintah sebelum berangkat.'),
        1: ('A contract is required, but not for every worker, or the government does not check it.',
            'Kontrak diwajibkan, tetapi tidak untuk semua pekerja, atau pemerintah tidak memeriksanya.'),
        0: ('The law does not require a contract.',
            'Hukum tidak mewajibkan kontrak.')}),
    ('predep', 'class', ('Training before you go', 'Pembekalan sebelum berangkat'), {
        2: ('Training on your rights is required and free.',
            'Pembekalan tentang hak anda bersifat wajib dan gratis.'),
        1: ('Training is required, but you may have to pay, or it is only for some workers.',
            'Pembekalan diwajibkan, tetapi anda mungkin harus membayar, atau pembekalan hanya berlaku bagi sebagian pekerja.'),
        0: ('No training is required.',
            'Tidak ada pembekalan wajib.')}),
    ('welfare', 'shield', ('Insurance or welfare fund', 'Asuransi atau dana perlindungan'), {
        2: ('A government fund or insurance covers death, injury and the trip home.',
            'Dana pemerintah atau asuransi wajib menanggung kematian, cacat, dan kepulangan.'),
        1: ('A fund or insurance exists, but it covers only some workers or some risks.',
            'Dana atau asuransi tersedia, tetapi hanya menanggung sebagian pekerja atau sebagian risiko.'),
        0: ('There is no government fund or insurance.',
            'Tidak ada dana pemerintah atau asuransi wajib.')}),
    ('hotline', 'phone', ('Help line', 'Saluran bantuan'), {
        2: ('There is an official help line, open 24 hours.',
            'Tersedia saluran bantuan resmi yang buka 24 jam.'),
        1: ('There is an official help line, but not 24 hours, or not in every country.',
            'Tersedia saluran bantuan resmi, tetapi tidak 24 jam atau tidak di semua negara.'),
        0: ('We found no official help line.',
            'Kami tidak menemukan saluran bantuan resmi.')}),
    ('legalaid', 'scale', ('A lawyer abroad', 'Pengacara di luar negeri'), {
        2: ('By law, the government pays for legal help abroad, also in court.',
            'Menurut undang-undang, pemerintah membiayai bantuan hukum di luar negeri, termasuk di pengadilan.'),
        1: ('The government may pay for legal help abroad, case by case.',
            'Pemerintah dapat membiayai bantuan hukum di luar negeri, kasus demi kasus.'),
        0: ('We found no legal help paid by the government.',
            'Kami tidak menemukan bantuan hukum yang dibiayai pemerintah.')}),
    ('shelter', 'house', ('Safe place to stay', 'Tempat penampungan'), {
        2: ('By law, embassies in the main countries must have a safe place to stay.',
            'Menurut undang-undang, perwakilan di negara tujuan utama wajib menyediakan tempat penampungan.'),
        1: ('Some embassies have a safe place to stay.',
            'Sebagian perwakilan menyediakan tempat penampungan.'),
        0: ('We found no safe place to stay at embassies.',
            'Kami tidak menemukan tempat penampungan di perwakilan.')}),
    ('redress', 'flag', ('Complaint at home', 'Pengaduan di dalam negeri'), {
        2: ('A special office at home can order the agency or employer to pay you.',
            'Lembaga khusus di dalam negeri dapat memerintahkan agensi atau majikan membayar ganti rugi kepada anda.'),
        1: ('A complaint can punish the agency or get your fees back. For other money owed, you go to court.',
            'Pengaduan dapat berujung sanksi bagi agensi atau pengembalian biaya. Untuk tuntutan uang lainnya, anda harus ke pengadilan.'),
        0: ('Only the ordinary courts can help.',
            'Hanya pengadilan biasa yang dapat membantu.')}),
]

T = {
    'title': ('Working abroad from {c}', 'Bekerja di luar negeri dari {c}'),
    'sub': ('Your rights under the law of {c}, and where to get free help',
            'Hak anda menurut hukum {c}, dan tempat mencari bantuan gratis'),
    'law_h': ('What the law of {c} says', 'Isi hukum {c}'),
    'law_note': ('This is what the law says. What happens in practice can be different.',
                 'Inilah isi hukumnya. Kenyataan di lapangan dapat berbeda.'),
    'laws_h': ('Main laws', 'Undang-undang utama'),
    'help_h': ('Free help', 'Bantuan gratis'),
    'help_note': ('We list a phone number only when we have checked it.',
                  'Kami hanya mencantumkan nomor telepon yang telah kami periksa.'),
    'help_none': ('We have no checked phone number for {c} yet. Use the link below to find help.',
                  'Kami belum memiliki nomor telepon yang telah diperiksa untuk {c}. Gunakan tautan di bawah untuk mencari bantuan.'),
    'tips_h': ('Before you go', 'Sebelum berangkat'),
    'tips': [
        ('Keep a photo of your passport, visa and contract on your phone. Give copies to your family.',
         'Simpan foto paspor, visa, dan kontrak di ponsel anda. Titipkan salinannya kepada keluarga.'),
        ('Ask for a receipt for every payment to an agency.',
         'Mintalah kuitansi untuk setiap pembayaran kepada agensi.'),
        ('Save the numbers on this page before you leave.',
         'Simpan nomor-nomor di halaman ini sebelum berangkat.'),
    ],
    'cases_h': ('Court decisions that helped workers', 'Putusan pengadilan yang membantu pekerja'),
    'cases_note': ('Short summaries, not yet checked line by line against the full judgment.',
                   'Ringkasan singkat yang belum dicocokkan baris demi baris dengan naskah putusan.'),
    'cases_none': ('We are still collecting court decisions from {c}.',
                   'Kami masih menghimpun putusan pengadilan dari {c}.'),
    'qr_help': ('Help in the country where you work', 'Bantuan di negara tempat anda bekerja'),
    'qr_updates': ('New court decisions and laws, once a month, free',
                   'Putusan dan undang-undang baru, sebulan sekali, gratis'),
    'qr_more': ('More detail and sources', 'Rincian dan sumber'),
    'disclaimer': ('General information, not legal advice.', 'Informasi umum, bukan nasihat hukum.'),
    'made': ('Made on {d} from the open data of the Institute for Migrant Rights. Free to copy and share (CC BY 4.0).',
             'Dibuat pada {d} dari data terbuka Institute for Migrant Rights. Bebas disalin dan dibagikan (CC BY 4.0).'),
    'level_word': ('Protection', 'Perlindungan'),
}

MONTHS = {
    'en': 'January February March April May June July August September October November December'.split(),
    'id': 'Januari Februari Maret April Mei Juni Juli Agustus September Oktober November Desember'.split(),
}
