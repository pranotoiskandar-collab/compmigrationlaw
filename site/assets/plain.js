/* IMR plain-language layer: adds an optional "In plain language" note to each section of the data pages,
   with a page-wide switch (remembered per browser). English and Indonesian; follows the site language switch.
   Content lives in TXT below, keyed by page and section selector. Include with
   <script src="/assets/plain.js" defer></script> on any page listed in PAGES. */
(function () {
  "use strict";
  var KEY = "imr-plain";

  /* ---------- shared explanations ---------- */
  var S = {
    score: function (what, en_id) {
      return {
        en: "<p><b>What this shows.</b> Each " + what[0] + " gets 2 points for a protection that is fully in place, 1 if it is partial and 0 if it is missing. You decide how much each feature matters by moving the sliders, and the page adds up the points.</p>" +
          "<p><b>How to read it.</b> There is no official ranking, because the order depends on what you value. The stability check tries 10,000 random sets of weights. If the same " + what[0] + " comes first almost every time, it leads whatever one values. If the wins are split, nobody can fairly call one " + what[0] + " the best.</p>" +
          "<p><b>Keep in mind.</b> The points describe the law on paper, not how it is enforced.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Setiap " + what[1] + " mendapat 2 poin bila suatu perlindungan berlaku penuh, 1 bila sebagian, dan 0 bila tidak ada. Anda menentukan seberapa penting tiap fitur dengan menggeser penggeser, lalu halaman menjumlahkan poinnya.</p>" +
          "<p><b>Cara membacanya.</b> Tidak ada peringkat resmi, karena urutannya bergantung pada apa yang Anda anggap penting. Uji stabilitas mencoba 10.000 kombinasi bobot acak. Bila " + what[1] + " yang sama hampir selalu di urutan pertama, ia unggul apa pun yang dianggap penting. Bila hasilnya terbagi, tidak ada yang bisa disebut terbaik secara adil.</p>" +
          "<p><b>Perlu diingat.</b> Poin menggambarkan hukum di atas kertas, bukan pelaksanaannya.</p>"
      };
    },
    analyze: {
      en: "<p><b>What this shows.</b> Each row is a corridor: a country workers come from and the place they go to. You can ask, for example, whether corridors covered by an agreement carry more workers.</p>" +
        "<p><b>How to read it.</b> Every answer gives a <i>p-value</i>: how often a pattern this strong would appear by pure chance if there were no real link. Below 0.05 (one in twenty) is called \"significant\". A higher p-value does not prove there is no link; it means these few corridors cannot show one.</p>" +
        "<p><b>Keep in mind.</b> These are associations, not causes. Big corridors may attract agreements rather than agreements creating big corridors. Corridors to the same destination share its laws and statistics, so the results are more uncertain than the numbers suggest.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Setiap baris adalah satu koridor: negara asal pekerja dan tempat tujuan mereka. Anda bisa bertanya, misalnya, apakah koridor yang tercakup perjanjian membawa lebih banyak pekerja.</p>" +
        "<p><b>Cara membacanya.</b> Setiap jawaban memberi <i>nilai p</i>: seberapa sering pola sekuat ini muncul hanya karena kebetulan seandainya tidak ada hubungan nyata. Di bawah 0,05 (satu banding dua puluh) disebut \"signifikan\". Nilai p yang lebih tinggi tidak membuktikan tidak ada hubungan; artinya koridor yang sedikit ini belum bisa menunjukkannya.</p>" +
        "<p><b>Perlu diingat.</b> Ini keterkaitan, bukan sebab-akibat. Koridor besar mungkin menarik perjanjian, bukan perjanjian yang menciptakan koridor besar. Koridor ke tujuan yang sama berbagi hukum dan statistik yang sama, sehingga hasilnya lebih tidak pasti daripada yang tampak.</p>"
    },
    agreements: {
      en: "<p><b>What this shows.</b> Every agreement and instrument we could trace, sorted by level (worldwide, regional, between regions, between two countries) and by type (treaty, agreement, memorandum of understanding, standard contract, declaration).</p>" +
        "<p><b>How to read it.</b> A treaty or agreement binds once it is in force. A memorandum of understanding usually does not create legal obligations; it records a shared intention. A long list therefore does not always mean strong protection.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Semua perjanjian dan instrumen yang bisa kami telusuri, dikelompokkan menurut tingkat (global, kawasan, antarkawasan, antara dua negara) dan jenis (traktat, perjanjian, nota kesepahaman, kontrak standar, deklarasi).</p>" +
        "<p><b>Cara membacanya.</b> Traktat atau perjanjian mengikat setelah berlaku. Nota kesepahaman biasanya tidak menimbulkan kewajiban hukum; ia mencatat niat bersama. Jadi daftar yang panjang tidak selalu berarti perlindungan yang kuat.</p>"
    },
    laws: {
      en: "<p><b>What this shows.</b> The national laws, regulations and standard contracts behind the coding, with links to the official texts and a note on whom each one covers and whom it leaves out.</p>" +
        "<p><b>Keep in mind.</b> English translations are for reference; the original-language text is the law.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Undang-undang, peraturan, dan kontrak standar nasional yang menjadi dasar pengodean, dengan tautan ke teks resmi dan catatan tentang siapa yang dicakup dan siapa yang tidak.</p>" +
        "<p><b>Perlu diingat.</b> Terjemahan bahasa Inggris hanya rujukan; teks dalam bahasa aslinyalah yang berlaku sebagai hukum.</p>"
    },
    reforms: {
      en: "<p><b>What this shows.</b> A dated list of changes in the law, so you can see what is new and what the coding reflects.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Daftar perubahan hukum menurut tanggal, sehingga Anda bisa melihat apa yang baru dan apa yang sudah tercermin dalam pengodean.</p>"
    },
    methods: function (n) {
      return {
        en: "<p><b>What this shows.</b> How the data were built. Each feature of the law is \"coded\": a reader applies a written rule (the codebook) and gives it 2, 1 or 0, like a teacher marking with a rubric. " + n[0] + "</p>" +
          "<p><b>How to read it.</b> A cell marked <b>P</b> was checked against the official legal text. A cell marked <b>S</b> rests on a reliable secondary source and is provisional until checked. The codebook and every cell can be downloaded, so anyone can check our work.</p>" +
          "<p><b>Keep in mind.</b> Only the law on paper is coded, not what happens in practice.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Cara data disusun. Setiap fitur hukum \"dikodekan\": pembaca menerapkan aturan tertulis (buku kode) dan memberi nilai 2, 1, atau 0, seperti guru yang menilai dengan rubrik. " + n[1] + "</p>" +
          "<p><b>Cara membacanya.</b> Sel bertanda <b>P</b> sudah dicocokkan dengan teks hukum resmi. Sel bertanda <b>S</b> bersandar pada sumber sekunder yang tepercaya dan bersifat sementara sampai diperiksa. Buku kode dan setiap sel bisa diunduh, sehingga siapa pun bisa memeriksa pekerjaan kami.</p>" +
          "<p><b>Perlu diingat.</b> Yang dikodekan hanya hukum di atas kertas, bukan apa yang terjadi dalam praktik.</p>"
      };
    },
    profiles: function (w) {
      return {
        en: "<p><b>What this shows.</b> Everything on this page for one " + w[0] + " at a time: how its law scores on each feature, with the reason and the source, plus the arguments and avenues that the gaps open for advocates.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Semua isi halaman ini untuk satu " + w[1] + " sekaligus: nilai hukumnya pada tiap fitur, beserta alasan dan sumbernya, serta argumen dan jalur yang dibuka oleh celah-celahnya bagi advokat.</p>"
      };
    }
  };

  /* ---------- Atlas (shared by /migration-law/?lens=farm and /migration-law/) ---------- */
  var ATLAS = {
    'section[data-view="map"]': {
      en: "<p><b>What this shows.</b> A map of how far each country has committed to the key treaties. By default, darker means a higher ratification score: the country has joined more of the treaties, and sooner (see Country ranking for how the score is made). You can also shade the map by a single treaty.</p><p><b>Keep in mind.</b> Joining a treaty is a promise. It does not show whether workers are protected in practice; see Implementation for that.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Peta tentang sejauh mana tiap negara terikat pada perjanjian internasional utama. Secara bawaan, warna lebih gelap berarti skor ratifikasi lebih tinggi: negara itu mengikuti lebih banyak perjanjian, dan lebih cepat (lihat Peringkat negara untuk cara skor dihitung). Anda juga bisa mewarnai peta menurut satu perjanjian saja.</p><p><b>Perlu diingat.</b> Ikut serta dalam perjanjian adalah janji. Itu tidak menunjukkan apakah pekerja terlindungi dalam praktik; lihat bagian Implementasi.</p>"
    },
    'section[data-view="norms"]': {
      en: "<p><b>What this shows.</b> Every rule in the Atlas, ranked. Each gets two marks from 1 to 5: how binding it is (5 = a treaty in force, 1 = a voluntary standard) and how relevant it is to the topic (5 = entirely about it). The two marks are multiplied, so the top score is 25.</p><p><b>Example.</b> A binding convention entirely about farm work scores 5 × 5 = 25. A binding general human rights treaty scores 5 × 2 = 10. A voluntary farm guideline scores 1 × 5 = 5. Multiplying rewards rules that are strong on both counts.</p><p><b>Keep in mind.</b> The marks are IMR's judgment, applied through written rules. National laws are ranked separately because they bind only one country.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Semua aturan dalam Atlas, diurutkan. Masing-masing mendapat dua nilai dari 1 sampai 5: seberapa mengikat (5 = perjanjian yang berlaku, 1 = standar sukarela) dan seberapa relevan dengan topiknya (5 = sepenuhnya tentang topik itu). Kedua nilai dikalikan, jadi nilai tertinggi 25.</p><p><b>Contoh.</b> Konvensi mengikat yang sepenuhnya tentang kerja pertanian bernilai 5 × 5 = 25. Perjanjian HAM umum yang mengikat bernilai 5 × 2 = 10. Pedoman pertanian sukarela bernilai 1 × 5 = 5. Perkalian memberi nilai tinggi pada aturan yang kuat di kedua sisi.</p><p><b>Perlu diingat.</b> Nilai ini adalah penilaian IMR berdasarkan aturan tertulis. Hukum nasional diurutkan terpisah karena hanya mengikat satu negara.</p>"
    },
    'section[data-view="timeline"]': {
      en: "<p><b>What this shows.</b> When each rule was adopted (the dot) and when it came into force (the end of the line). A long line means states took a long time to bring it into effect. Color shows how binding the rule is.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Kapan tiap aturan diadopsi (titik) dan kapan mulai berlaku (ujung garis). Garis panjang berarti negara-negara butuh waktu lama untuk memberlakukannya. Warna menunjukkan seberapa mengikat aturan itu.</p>"
    },
    'section[data-view="countries"]': {
      en: "<p><b>What this shows.</b> A score from 0 to 100 for each of 187 countries, based on 13 treaties. It mixes two things. <b>Breadth</b> (60%): how much of the list the country has joined, with the six farm conventions counting double. <b>Enthusiasm</b> (40%): how many of the seven newer treaties (since 1989) it joined, with a bonus for joining quickly.</p><p><b>Example.</b> The Philippines has joined three farm conventions (6 points) and three others (3 points): 9 of 19, so breadth is 47.4. It joined two newer treaties within about five years: enthusiasm 24.2. Score: 0.6 × 47.4 + 0.4 × 24.2 = 38.1.</p><p><b>Keep in mind.</b> The 60/40 split is a choice, not a fact; you can download both parts and combine them your way.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Skor 0 sampai 100 untuk tiap 187 negara, berdasarkan 13 perjanjian. Skor ini menggabungkan dua hal. <b>Keluasan</b> (60%): seberapa banyak dari daftar itu yang telah diikuti, dengan enam konvensi pertanian dihitung dua kali. <b>Antusiasme</b> (40%): berapa dari tujuh perjanjian yang lebih baru (sejak 1989) yang diikuti, dengan bonus bila cepat.</p><p><b>Contoh.</b> Filipina mengikuti tiga konvensi pertanian (6 poin) dan tiga lainnya (3 poin): 9 dari 19, jadi keluasannya 47,4. Ia mengikuti dua perjanjian baru dalam sekitar lima tahun: antusiasme 24,2. Skor: 0,6 × 47,4 + 0,4 × 24,2 = 38,1.</p><p><b>Perlu diingat.</b> Pembagian 60/40 adalah pilihan, bukan fakta; Anda bisa mengunduh kedua bagian dan menggabungkannya dengan cara Anda sendiri.</p>"
    },
    'section[data-view="implementation"]': {
      en: "<p><b>What this shows.</b> Whether countries carry out the treaties they joined. Each treaty is checked with four questions: is there a national law, does it cover everyone (including farmworkers, domestic workers and undocumented migrants), is it enforced, and have UN or ILO experts asked for changes that are still open?</p><p><b>How to read it.</b> <i>Implemented</i> = yes to the first three. <i>Partly</i> = a law exists but falls short. <i>Gap</i> = the law is missing, leaves a group out, or is ignored in practice.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Apakah negara melaksanakan perjanjian yang telah diikutinya. Tiap perjanjian diperiksa dengan empat pertanyaan: adakah undang-undang nasionalnya, apakah mencakup semua orang (termasuk buruh tani, pekerja rumah tangga, dan migran tidak berdokumen), apakah ditegakkan, dan apakah pakar PBB atau ILO masih meminta perubahan yang belum dipenuhi?</p><p><b>Cara membacanya.</b> <i>Dilaksanakan</i> = ya untuk tiga pertanyaan pertama. <i>Sebagian</i> = ada undang-undang tetapi kurang. <i>Celah</i> = undang-undang tidak ada, mengecualikan suatu kelompok, atau diabaikan dalam praktik.</p>"
    },
    'section[data-view="cases"]': {
      en: "<p><b>What this shows.</b> Decisions in which courts and UN or ILO committees applied these rules to real cases. They show what the rules mean in practice and which arguments have worked.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Putusan ketika pengadilan dan komite PBB atau ILO menerapkan aturan-aturan ini pada kasus nyata. Putusan ini menunjukkan makna aturan dalam praktik dan argumen mana yang berhasil.</p>"
    },
    'section[data-view="corridors"]': {
      en: "<p><b>What this shows.</b> The main routes Indonesian workers take abroad, with the agreements that cover each route, what workers pay to be recruited and what help exists if something goes wrong after they return.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Rute utama pekerja Indonesia ke luar negeri, perjanjian yang mencakup tiap rute, biaya rekrutmen yang dibayar pekerja, dan bantuan yang tersedia bila ada masalah setelah mereka pulang.</p>"
    },
    'section[data-view="compare"]': {
      en: "<p><b>What this shows.</b> Two or more countries side by side: their scores, which treaties they joined and when, and how well they carry them out.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Dua negara atau lebih berdampingan: skornya, perjanjian yang diikuti dan kapan, serta seberapa baik pelaksanaannya.</p>"
    },
    'section[data-view="stats"]': {
      en: "<p><b>What this shows.</b> A tool to test your own questions, such as \"Do richer countries join more treaties?\". It can compare groups, check whether two measures rise and fall together, look at several factors at once, and show how fast countries join a treaty.</p><p><b>How to read it.</b> Each answer starts with the \"null hypothesis\", the assumption that there is no difference, much as a court presumes innocence. The <i>p-value</i> says how often a result this strong would appear by pure chance if that assumption were true. Below 0.05 (one in twenty), the assumption is rejected. A plain-language reading appears under every result.</p><p><b>Keep in mind.</b> Two things moving together does not mean one causes the other: ice cream sales and drownings both rise in summer.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Alat untuk menguji pertanyaan Anda sendiri, misalnya \"Apakah negara yang lebih kaya mengikuti lebih banyak perjanjian?\". Alat ini bisa membandingkan kelompok, memeriksa apakah dua ukuran naik-turun bersama, melihat beberapa faktor sekaligus, dan menunjukkan seberapa cepat negara mengikuti suatu perjanjian.</p><p><b>Cara membacanya.</b> Setiap jawaban dimulai dengan \"hipotesis nol\", anggapan bahwa tidak ada perbedaan, seperti pengadilan yang menganggap terdakwa tidak bersalah. <i>Nilai p</i> menunjukkan seberapa sering hasil sekuat ini muncul hanya karena kebetulan bila anggapan itu benar. Di bawah 0,05 (satu banding dua puluh), anggapan itu ditolak. Penjelasan sederhana muncul di bawah setiap hasil.</p><p><b>Perlu diingat.</b> Dua hal yang bergerak bersama tidak berarti yang satu menyebabkan yang lain: penjualan es krim dan kasus tenggelam sama-sama naik di musim panas.</p>"
    },
    'section[data-view="data"]': {
      en: "<p><b>What this shows.</b> Every table behind the Atlas, free to download as spreadsheets (CSV) or one complete file (JSON), so that anyone can check or reuse the data.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Semua tabel di balik Atlas, bebas diunduh sebagai lembar kerja (CSV) atau satu berkas lengkap (JSON), sehingga siapa pun bisa memeriksa atau memakai ulang datanya.</p>"
    },
    'section[data-view="method"]': {
      en: "<p><b>What this shows.</b> The rules behind every score on this site, written out in full so that anyone can apply them and check ours. Ratification records come from the ILO and the UN and were collected on 30 October 2026.</p>",
      id: "<p><b>Apa yang ditunjukkan.</b> Aturan di balik setiap skor di situs ini, ditulis lengkap agar siapa pun bisa menerapkannya dan memeriksa hasil kami. Data ratifikasi berasal dari ILO dan PBB dan dikumpulkan pada 30 Oktober 2026.</p>"
    }
  };

  /* ---------- pages ---------- */
  var PAGES = {
    "atlas": ATLAS,
    "migration-law": ATLAS,
    "gcc": {
      "#glance": {
        en: "<p><b>What this shows.</b> A quick comparison of how each of the six states' labor laws applies to migrant workers, feature by feature.</p><p><b>How to read it.</b> Each cell says whether a protection is in place, partly in place, or absent, according to the law on paper.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Perbandingan singkat bagaimana undang-undang ketenagakerjaan keenam negara berlaku bagi pekerja migran, fitur demi fitur.</p><p><b>Cara membacanya.</b> Setiap sel menunjukkan apakah suatu perlindungan berlaku, berlaku sebagian, atau tidak ada, menurut hukum di atas kertas.</p>"
      },
      "#score": S.score(["state", "negara"]),
      "#profiles": S.profiles(["state", "negara"]),
      "#people": {
        en: "<p><b>What this shows.</b> Who lives and works in each state: how many residents are nationals and how many are not, the balance of men and women, and the sectors where non-nationals work.</p><p><b>Keep in mind.</b> Figures come from national statistics offices and differ in year and definition, so compare them with care.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Siapa yang tinggal dan bekerja di tiap negara: berapa penduduk warga negara dan berapa bukan, perbandingan laki-laki dan perempuan, serta sektor tempat bukan-warga bekerja.</p><p><b>Perlu diingat.</b> Angka berasal dari kantor statistik nasional dengan tahun dan definisi yang berbeda, jadi bandingkan dengan hati-hati.</p>"
      },
      "#agreements": S.agreements,
      "#corridors": {
        en: "<p><b>What this shows.</b> The largest groups of migrants in each state by country of origin (UN figures for 2024). A highlighted bar marks a route with at least one labor agreement between the two countries on record.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Kelompok migran terbesar di tiap negara menurut negara asal (angka PBB 2024). Batang yang ditandai menunjukkan rute yang memiliki setidaknya satu perjanjian ketenagakerjaan antara kedua negara.</p>"
      },
      "#analyze": S.analyze,
      "#reforms": S.reforms,
      "#methods": S.methods(["English translations are unofficial; the Arabic text prevails.", "Terjemahan bahasa Inggris tidak resmi; teks bahasa Arab yang berlaku."])
    },
    "east-asia": {
      "#glance": {
        en: "<p><b>What this shows.</b> How the law treats seven groups of migrant workers in Taiwan, South Korea, Hong Kong and Japan, on ten features such as minimum wage, changing employer and bringing family.</p><p><b>How to read it.</b> The comparison is by worker group, not by country, because one country can treat groups very differently. In Taiwan, for example, fishers hired at home fall under the general labor law, while crew recruited abroad for the distant-water fleet fall under fisheries rules with a lower wage floor.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Bagaimana hukum memperlakukan tujuh kelompok pekerja migran di Taiwan, Korea Selatan, Hong Kong, dan Jepang, pada sepuluh fitur seperti upah minimum, pindah majikan, dan membawa keluarga.</p><p><b>Cara membacanya.</b> Perbandingan dilakukan per kelompok pekerja, bukan per negara, karena satu negara bisa memperlakukan kelompok secara sangat berbeda. Di Taiwan, misalnya, nelayan yang direkrut di dalam negeri tunduk pada hukum ketenagakerjaan umum, sedangkan awak kapal ikan jarak jauh yang direkrut di luar negeri tunduk pada aturan perikanan dengan upah minimum lebih rendah.</p>"
      },
      "#score": S.score(["group", "kelompok"]),
      "#intl": {
        en: "<p><b>What this shows.</b> The international rules that bind each jurisdiction. Taiwan cannot join UN or ILO treaties, so the page shows what stands in for them: its own law adopting the two UN human rights covenants, and trade measures by the United States and the European Union that reach its fishing fleet.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Aturan internasional yang mengikat tiap yurisdiksi. Taiwan tidak bisa mengikuti perjanjian PBB atau ILO, jadi halaman ini menunjukkan penggantinya: undang-undangnya sendiri yang mengadopsi dua kovenan HAM PBB, serta langkah perdagangan Amerika Serikat dan Uni Eropa yang menjangkau armada perikanannya.</p>"
      },
      "#profiles": S.profiles(["jurisdiction", "yurisdiksi"]),
      "#people": {
        en: "<p><b>What this shows.</b> How many workers are in each group, with the year and source of each figure.</p><p><b>Keep in mind.</b> Official figures on fishers are sparse and dated; estimates by advocacy groups are higher.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Berapa banyak pekerja di tiap kelompok, dengan tahun dan sumber setiap angka.</p><p><b>Perlu diingat.</b> Angka resmi tentang nelayan sedikit dan sudah lama; perkiraan kelompok advokasi lebih tinggi.</p>"
      },
      "#agreements": S.agreements,
      "#laws": S.laws,
      "#corridors": {
        en: "<p><b>What this shows.</b> The largest countries of origin for each jurisdiction, from the best official figure available. Indonesia, the Philippines and Vietnam appear everywhere.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Negara asal terbesar untuk tiap yurisdiksi, dari angka resmi terbaik yang tersedia. Indonesia, Filipina, dan Vietnam muncul di semua yurisdiksi.</p>"
      },
      "#analyze": S.analyze,
      "#reforms": S.reforms,
      "#methods": S.methods(["70 cells are coded (7 groups × 10 features); 30 have been checked against the official texts in the original language.", "Ada 70 sel yang dikodekan (7 kelompok × 10 fitur); 30 di antaranya sudah dicocokkan dengan teks resmi dalam bahasa aslinya."])
    },
    "domestic-workers": {
      "#glance": {
        en: "<p><b>What this shows.</b> How each country's law treats domestic workers who come from abroad, on 17 questions taken from the ILO Domestic Workers Convention, such as a weekly day off or keeping one's own passport. A second view shows what countries of origin do before their workers leave.</p><p><b>How to read it.</b> Full means the law meets the international standard, partial means it does so in part, none means the law does not provide for it. Click a cell to see the article of the law it rests on.</p><p><b>Keep in mind.</b> Only the law on paper is coded, not what happens in homes.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Bagaimana hukum tiap negara memperlakukan pekerja rumah tangga dari luar negeri, pada 17 pertanyaan dari Konvensi ILO tentang Pekerja Rumah Tangga, misalnya hari libur mingguan atau memegang paspor sendiri. Tampilan kedua menunjukkan apa yang dilakukan negara asal sebelum pekerjanya berangkat.</p><p><b>Cara membacanya.</b> Penuh berarti hukum memenuhi standar internasional, sebagian berarti hanya sebagian, tidak ada berarti hukum tidak mengaturnya. Klik sel untuk melihat pasal yang menjadi dasarnya.</p><p><b>Perlu diingat.</b> Yang dikodekan hanya hukum di atas kertas, bukan apa yang terjadi di dalam rumah.</p>"
      },
      "#compare": {
        en: "<p><b>What this shows.</b> The rules of up to four countries next to each other, with the article of the law for each answer.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Aturan hingga empat negara berdampingan, dengan pasal hukum untuk setiap jawaban.</p>"
      },
      "#c189": {
        en: "<p><b>What this shows.</b> For each rule in the ILO convention, how many of the 34 countries of destination follow it fully, in part or not at all. Long green bars are rules most countries already have; short ones show where the law is thinnest.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Untuk setiap aturan dalam konvensi ILO, berapa dari 34 negara tujuan yang mengikutinya sepenuhnya, sebagian, atau tidak sama sekali. Batang hijau yang panjang adalah aturan yang sudah dimiliki sebagian besar negara; yang pendek menunjukkan di mana hukumnya paling tipis.</p>"
      },
      "#corridors": {
        en: "<p><b>What this shows.</b> The path of one worker: the rules of the home country before departure, any agreement between the two countries, and the rules in the country where she works.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Jalur seorang pekerja: aturan negara asal sebelum berangkat, perjanjian antara kedua negara bila ada, dan aturan di negara tempat ia bekerja.</p>"
      },
      "#instruments": {
        en: "<p><b>What this shows.</b> Every treaty, agreement and law in the database. Binding means a state that has accepted it must follow it; not binding means it is guidance.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Semua traktat, perjanjian, dan hukum dalam basis data. Mengikat berarti negara yang menerimanya wajib mengikutinya; tidak mengikat berarti hanya pedoman.</p>"
      },
      "#timeline": {
        en: "<p><b>What this shows.</b> When the instruments were adopted. Most rules specific to domestic workers came after 2011, the year of the ILO convention.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Kapan instrumen diadopsi. Sebagian besar aturan khusus pekerja rumah tangga muncul setelah 2011, tahun konvensi ILO.</p>"
      },
      "#treaties": {
        en: "<p><b>What this shows.</b> Which international treaties each country has joined. Joining a treaty is a promise to bring the law into line with it.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Traktat internasional yang telah diikuti tiap negara. Mengikuti traktat adalah janji untuk menyesuaikan hukum dengannya.</p>"
      },
      "#score": S.score(["country", "negara"]),
      "#profiles": S.profiles(["country", "negara"]),
      "#analyze": S.analyze,
      "#methods": S.methods(["658 cells are coded (34 destinations × 17 features and 10 origins × 8 features). The UAE cells come from the official text; the others are being checked.", "Ada 658 sel yang dikodekan (34 negara tujuan × 17 fitur dan 10 negara asal × 8 fitur). Sel UEA berasal dari teks resmi; sisanya sedang diperiksa."])
    },
    "southeast-asia": {
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
    "countries-of-origin": {
      "#glance": {
        en: "<p><b>What this shows.</b> How eight major countries of origin regulate the recruitment, departure, protection and return of their workers, on nine features drawn from international standards, such as whether workers may be charged recruitment fees.</p><p><b>How to read it.</b> A higher value means the rule is closer to international standards. It does not mean the country is a safer place to leave from.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Bagaimana delapan negara asal utama mengatur rekrutmen, keberangkatan, perlindungan, dan kepulangan pekerjanya, pada sembilan fitur yang diambil dari standar internasional, misalnya apakah pekerja boleh dibebani biaya rekrutmen.</p><p><b>Cara membacanya.</b> Nilai lebih tinggi berarti aturannya lebih dekat ke standar internasional. Itu tidak berarti negara tersebut tempat yang lebih aman untuk berangkat.</p>"
      },
      "#score": S.score(["country", "negara"]),
      "#intl": {
        en: "<p><b>What this shows.</b> Which international treaties on migrant workers each country has joined. The UN Migrant Workers Convention is the only one that sets out the duties of countries of origin in detail.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Perjanjian internasional tentang pekerja migran yang telah diikuti tiap negara. Konvensi Pekerja Migran PBB adalah satu-satunya yang merinci kewajiban negara asal.</p>"
      },
      "#profiles": S.profiles(["country", "negara"]),
      "#outflows": {
        en: "<p><b>What this shows.</b> How many workers leave each country each year, from the latest official figure.</p><p><b>Keep in mind.</b> Each country counts something different (first-time placements, all departures including rehires, or approvals including renewals). The bars show rough size only, not a fair comparison.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Berapa banyak pekerja yang berangkat dari tiap negara setiap tahun, menurut angka resmi terbaru.</p><p><b>Perlu diingat.</b> Tiap negara menghitung hal yang berbeda (penempatan pertama, semua keberangkatan termasuk perpanjangan, atau persetujuan termasuk pembaruan). Batang hanya menunjukkan perkiraan besaran, bukan perbandingan yang setara.</p>"
      },
      "#agreements": S.agreements,
      "#laws": S.laws,
      "#violence": {
        en: "<p><b>What this shows.</b> What each country has put in place to protect its workers from violence: information before departure, help from embassies, shelters, bringing workers or their remains home, and punishing trafficking.</p><p><b>Keep in mind.</b> This is scored separately and is not part of the comparison above. Death counts say nothing about causes, which are rarely established.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Apa yang telah disiapkan tiap negara untuk melindungi pekerjanya dari kekerasan: informasi sebelum berangkat, bantuan perwakilan, rumah aman, pemulangan pekerja atau jenazahnya, dan penghukuman perdagangan orang.</p><p><b>Perlu diingat.</b> Bagian ini dinilai terpisah dan tidak termasuk perbandingan di atas. Angka kematian tidak menjelaskan penyebabnya, yang jarang bisa dipastikan.</p>"
      },
      "#corridors": {
        en: "<p><b>What this shows.</b> The main destinations for each country's workers, where an official breakdown exists. The Gulf states and Malaysia dominate South Asian departures; Japan, Taiwan, South Korea and Hong Kong dominate Southeast Asian ones.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Tujuan utama pekerja dari tiap negara, bila ada rincian resminya. Negara-negara Teluk dan Malaysia mendominasi keberangkatan dari Asia Selatan; Jepang, Taiwan, Korea Selatan, dan Hong Kong mendominasi keberangkatan dari Asia Tenggara.</p>"
      },
      "#analyze": S.analyze,
      "#reforms": S.reforms,
      "#methods": S.methods(["Binding policies such as ministerial decisions are coded alongside laws, because much of the regulation of emigration sits there.", "Kebijakan yang mengikat, seperti keputusan menteri, dikodekan bersama undang-undang, karena sebagian besar pengaturan emigrasi ada di sana."])
    },
    "government-hate-speech": {
      "#evidence": {
        en: "<p><b>What this shows.</b> Figures from monitoring projects and international surveys, for example the number of hate speech events recorded in India each year.</p><p><b>Keep in mind.</b> No dataset measures hate speech by governments as such. Each figure is a clue from a different angle (one country, one religion, one kind of speaker), not a single measure.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Angka dari proyek pemantauan dan survei internasional, misalnya jumlah peristiwa ucapan kebencian yang tercatat di India setiap tahun.</p><p><b>Perlu diingat.</b> Tidak ada data yang mengukur ucapan kebencian oleh pemerintah secara langsung. Setiap angka adalah petunjuk dari sudut yang berbeda (satu negara, satu agama, satu jenis pembicara), bukan satu ukuran tunggal.</p>"
      },
      "#timeline": {
        en: "<p><b>What this shows.</b> Nine well-documented cases in which officials' words came before violence against the group they targeted.</p><p><b>Keep in mind.</b> These cases were chosen because they are well documented. They illustrate the problem; they do not show how often it happens.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Sembilan kasus yang terdokumentasi baik ketika ucapan pejabat mendahului kekerasan terhadap kelompok yang disasarnya.</p><p><b>Perlu diingat.</b> Kasus-kasus ini dipilih karena terdokumentasi baik. Kasus ini menggambarkan masalahnya, bukan seberapa sering hal itu terjadi.</p>"
      },
      "#frameworks": {
        en: "<p><b>What this shows.</b> Six ways the law responds today, from international criminal law to platform rules, with what each one reaches and what it leaves out.</p><p><b>How to read it.</b> In the comparison tool, tick what matters to you; each response gets 2 points where it fully meets a criterion and 1 where it partly does. The ratings are IMR's reading, not a legal opinion.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Enam cara hukum merespons saat ini, dari hukum pidana internasional sampai aturan platform, beserta apa yang dijangkau dan apa yang terlewat.</p><p><b>Cara membacanya.</b> Di alat perbandingan, centang hal yang penting bagi Anda; tiap respons mendapat 2 poin bila sepenuhnya memenuhi suatu kriteria dan 1 bila sebagian. Penilaian ini adalah bacaan IMR, bukan pendapat hukum.</p>"
      },
      "#proposal": {
        en: "<p><b>What this shows.</b> The elements of the new offense the working paper proposes: who can commit it, what words it covers and what it does not cover, such as criticism of policies or of individuals.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Unsur-unsur tindak pidana baru yang diusulkan makalah kerja: siapa yang bisa melakukannya, ucapan apa yang dicakup, dan apa yang tidak dicakup, seperti kritik terhadap kebijakan atau individu.</p>"
      },
      "#testing": {
        en: "<p><b>What this shows.</b> Each claim of the working paper set against data from about 176 countries, computed live.</p><p><b>How to read it.</b> A <i>correlation</i> (from −1 to +1) shows how closely two measures rise and fall together; 0 means no link. The <i>p-value</i> says how often a link this strong would appear by pure chance; below 0.05 (one in twenty) counts as \"significant\". Some results point against the argument, and the page shows those too.</p><p><b>Keep in mind.</b> These are links across countries at one time, not proof that words cause violence.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Setiap klaim makalah kerja diuji dengan data dari sekitar 176 negara, dihitung langsung.</p><p><b>Cara membacanya.</b> <i>Korelasi</i> (dari −1 sampai +1) menunjukkan seberapa erat dua ukuran naik-turun bersama; 0 berarti tidak ada hubungan. <i>Nilai p</i> menunjukkan seberapa sering hubungan sekuat itu muncul hanya karena kebetulan; di bawah 0,05 (satu banding dua puluh) disebut \"signifikan\". Sebagian hasil justru melemahkan argumen, dan halaman ini juga menampilkannya.</p><p><b>Perlu diingat.</b> Ini hubungan antarnegara pada satu waktu, bukan bukti bahwa ucapan menyebabkan kekerasan.</p>"
      },
      "#explore": {
        en: "<p><b>What this shows.</b> Tools to explore the episodes, court decisions and legal responses yourself, and to test questions with cross-country data.</p><p><b>How to read the charts of violence before and after.</b> They show the number of recorded violent events in the 12 months before and after a statement. They show what happened around it, not whether the statement caused it. One source (UCDP) misses most riots, and another (ACLED) starts only in 2010–2020 in many countries, so a flat line or a gap may just mean nothing was recorded.</p><p><b>How to read the statistics.</b> Each answer states the \"null hypothesis\" (no link) and a <i>p-value</i>: how often a result this strong would appear by pure chance. Below 0.05 (one in twenty) counts as \"significant\".</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Alat untuk menjelajahi sendiri peristiwa, putusan pengadilan, dan respons hukum, serta menguji pertanyaan dengan data antarnegara.</p><p><b>Cara membaca grafik kekerasan sebelum dan sesudah.</b> Grafik menunjukkan jumlah peristiwa kekerasan yang tercatat 12 bulan sebelum dan sesudah suatu pernyataan. Grafik menunjukkan apa yang terjadi di sekitarnya, bukan apakah pernyataan itu penyebabnya. Satu sumber (UCDP) melewatkan sebagian besar kerusuhan, dan sumber lain (ACLED) di banyak negara baru mulai pada 2010–2020, jadi garis datar atau kosong bisa saja berarti tidak ada yang tercatat.</p><p><b>Cara membaca statistik.</b> Setiap jawaban menyebut \"hipotesis nol\" (tidak ada hubungan) dan <i>nilai p</i>: seberapa sering hasil sekuat itu muncul hanya karena kebetulan. Di bawah 0,05 (satu banding dua puluh) disebut \"signifikan\".</p>"
      }
    },
    "hate-speech-voting": {
      "#question": {
        en: "<p><b>In short.</b> Some countries' laws protect foreigners and migrants by name. Others use general words such as \"everyone\" or \"citizens\". This page asks whether countries that name them see less hate speech by parties and fewer votes for anti-immigration parties.</p><p><b>Keep in mind.</b> The questions were fixed before the data were analyzed. That matters: if you look first and then choose what to test, you will almost always find something by chance.</p>",
        id: "<p><b>Singkatnya.</b> Hukum sebagian negara melindungi orang asing dan migran dengan menyebut mereka secara tegas. Negara lain memakai kata umum seperti \"setiap orang\" atau \"warga negara\". Halaman ini bertanya apakah negara yang menyebut mereka secara tegas mengalami lebih sedikit ucapan kebencian oleh partai dan lebih sedikit suara bagi partai anti-imigrasi.</p><p><b>Perlu diingat.</b> Pertanyaan ditetapkan sebelum data dianalisis. Ini penting: bila data dilihat dulu lalu baru dipilih apa yang diuji, hampir selalu akan ditemukan sesuatu karena kebetulan.</p>"
      },
      "#glance": {
        en: "<p><b>What this shows.</b> Four parts of each country's law, each scored 2 if it names non-citizens, 1 if it uses general wording, and 0 if there is no such protection. A country is in the \"explicit\" group if its constitution or a law written for migrants scores 2.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Empat bagian hukum tiap negara, masing-masing bernilai 2 bila menyebut bukan-warga secara tegas, 1 bila memakai rumusan umum, dan 0 bila tidak ada perlindungan semacam itu. Suatu negara masuk kelompok \"tegas\" bila konstitusinya atau undang-undang khusus migrannya bernilai 2.</p>"
      },
      "#outcomes": {
        en: "<p><b>What this shows.</b> For each country: how often parties use hate speech (rated by experts, where higher means more often and 0 is roughly the world average) and how many votes went to parties that oppose immigration in the latest election up to 2019.</p><p><b>Keep in mind.</b> The hate speech measure covers hate against any group, not only migrants. Elections since 2020 are not yet included.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Untuk tiap negara: seberapa sering partai memakai ucapan kebencian (dinilai para pakar; makin tinggi makin sering, dan 0 kira-kira rata-rata dunia) dan berapa banyak suara bagi partai yang menentang imigrasi dalam pemilu terakhir hingga 2019.</p><p><b>Perlu diingat.</b> Ukuran ucapan kebencian mencakup kebencian terhadap kelompok mana pun, bukan hanya migran. Pemilu sejak 2020 belum dimasukkan.</p>"
      },
      "#findings": {
        en: "<p><b>What this shows.</b> The averages of the two groups of countries, compared five ways.</p><p><b>How to read it.</b> In October 2026, anti-immigration (nativist) parties won on average about 9% of the vote where the law names non-citizens, and about 17% elsewhere. That looks like a big gap, yet it is \"not significant\". Why? A few countries with very large votes drive the averages, and with only 33 countries a gap like this would still turn up about one time in five by pure chance (a p-value of 0.22). Since five comparisons are made, a further correction (Holm) makes the bar higher still.</p><p><b>So.</b> The data point in the expected direction, but they are not strong enough to tell a real difference from chance. They neither confirm nor rule out the idea. By contrast, party hate speech and voters' support for restricting immigration do rise and fall together strongly, a link unlikely to be chance, though it does not show which causes which.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Rata-rata kedua kelompok negara, dibandingkan dengan lima cara.</p><p><b>Cara membacanya.</b> Pada Oktober 2026, partai pro-pribumi rata-rata meraih sekitar 9% suara di negara yang hukumnya menyebut bukan-warga secara tegas, dan sekitar 17% di negara lain. Selisihnya tampak besar, tetapi \"tidak signifikan\". Mengapa? Beberapa negara dengan suara sangat besar menarik rata-ratanya, dan dengan hanya 33 negara, selisih seperti ini tetap muncul sekitar satu dari lima kali hanya karena kebetulan (nilai p 0,22). Karena ada lima perbandingan, koreksi tambahan (Holm) membuat batasnya lebih tinggi lagi.</p><p><b>Jadi.</b> Data mengarah ke arah yang diperkirakan, tetapi belum cukup kuat untuk membedakan perbedaan nyata dari kebetulan. Data tidak membenarkan maupun menolak gagasan itu. Sebaliknya, ucapan kebencian partai dan dukungan pemilih untuk membatasi imigrasi memang naik-turun bersama dengan kuat, hubungan yang kecil kemungkinannya karena kebetulan, meski tidak menunjukkan mana yang menjadi sebab.</p>"
      },
      "#impunity": {
        en: "<p><b>What this shows.</b> Whether crimes against migrants are punished: whether the law treats hostility to a victim's nationality as making a crime worse, how well the courts protect people in general, and, for 16 European and North American countries, what share of hate crimes recorded by the police were prosecuted and ended in a sentence.</p><p><b>Keep in mind.</b> Those shares cover all hate crimes, not only those against migrants, and police, prosecutors and courts count cases differently, so they are rough.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Apakah kejahatan terhadap migran dihukum: apakah hukum menganggap kebencian terhadap kewarganegaraan korban sebagai pemberat, seberapa baik pengadilan melindungi orang secara umum, dan, untuk 16 negara Eropa dan Amerika Utara, berapa bagian kejahatan kebencian yang dicatat polisi yang dituntut dan berakhir dengan hukuman.</p><p><b>Perlu diingat.</b> Bagian tersebut mencakup semua kejahatan kebencian, bukan hanya terhadap migran, dan polisi, jaksa, serta pengadilan menghitung kasus secara berbeda, jadi angkanya hanya perkiraan.</p>"
      },
      "#analyze": {
        en: "<p><b>What this shows.</b> Tools to change the definitions, leave out countries and rerun the tests yourself.</p><p><b>How to read it.</b> Compare your result with the fixed one in section IV to see how much the answer depends on coding choices. Results found by trying many settings should be treated as leads, not findings: run enough tests and some will look \"significant\" by chance, like buying many lottery tickets.</p>",
        id: "<p><b>Apa yang ditunjukkan.</b> Alat untuk mengubah definisi, mengeluarkan negara tertentu, dan menjalankan ulang uji sendiri.</p><p><b>Cara membacanya.</b> Bandingkan hasil Anda dengan hasil tetap di bagian IV untuk melihat seberapa jauh jawabannya bergantung pada pilihan pengodean. Hasil yang ditemukan dengan mencoba banyak pengaturan sebaiknya dianggap petunjuk, bukan temuan: bila cukup banyak uji dijalankan, sebagian akan tampak \"signifikan\" karena kebetulan, seperti membeli banyak lotre.</p>"
      },
      "#profiles": S.profiles(["country", "negara"]),
      "#methods": S.methods(["The 34 countries are democracies chosen to balance Western and non-Western regions; they are not a random sample, and 34 is few for statistics.", "Ke-34 negara adalah negara demokrasi yang dipilih untuk menyeimbangkan kawasan Barat dan non-Barat; bukan sampel acak, dan 34 adalah jumlah yang kecil untuk statistik."])
    }
  };

  /* ---------- UI ---------- */
  var L = {
    en: { sum: "In plain language", on: "Plain language: on", off: "Plain language: off", tip: "Show a short, plain explanation of what each section's data show" },
    id: { sum: "Dalam bahasa sederhana", on: "Bahasa sederhana: aktif", off: "Bahasa sederhana: nonaktif", tip: "Tampilkan penjelasan singkat dan sederhana tentang apa yang ditunjukkan data di tiap bagian" }
  };
  var pp = location.pathname.split("/").filter(Boolean); var page = (pp[0] === "government-hate-speech" && pp[1] === "elections" ? "hate-speech-voting" : (pp[0] || "")).toLowerCase();
  var T = PAGES[page];
  if (!T) return;
  var lang = function () { return (document.documentElement.lang || "en").slice(0, 2) === "id" ? "id" : "en"; };
  var get = function () { try { return localStorage.getItem(KEY) === "1"; } catch (e) { return false; } };
  var set = function (v) { try { localStorage.setItem(KEY, v ? "1" : "0"); } catch (e) {} };
  var boxes = [], btn;

  function css() {
    var s = document.createElement("style");
    s.textContent =
      ".imr-plain{grid-column:1;margin:14px 0 18px;max-width:760px;border:1px solid #B2C7BC;border-left:4px solid #1E6B4A;background:#E8F0EC;color:#172D24;font:400 16px/1.55 'Figtree',system-ui,sans-serif;text-align:left}" +
      ".imr-plain>summary{cursor:pointer;list-style:none;padding:10px 14px;font:600 13px/1.3 'Figtree',system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#1E6B4A;min-height:24px}" +
      ".imr-plain>summary::-webkit-details-marker{display:none}" +
      ".imr-plain>summary::before{content:'+';display:inline-block;width:1.1em;font-weight:700}" +
      ".imr-plain[open]>summary::before{content:'\\2212'}" +
      ".imr-plain>div{padding:0 16px 6px}.imr-plain p{margin:0 0 10px}" +
      ".imr-plain-sw{position:fixed;left:12px;bottom:12px;z-index:70;all:unset;position:fixed;left:12px;bottom:12px;z-index:70;cursor:pointer;background:#172D24;color:#fff;border-radius:999px;padding:10px 16px;font:600 13px/1 'Figtree',system-ui,sans-serif;letter-spacing:.04em;box-shadow:0 2px 8px rgba(0,0,0,.25)}" +
      ".imr-plain-sw[aria-pressed='true']{background:#1E6B4A}" +
      ".imr-plain-sw:focus-visible{outline:3px solid #E8B4B0;outline-offset:2px}" +
      "@media print{.imr-plain-sw{display:none}.imr-plain{display:none}body.imr-plain-on .imr-plain{display:block}}";
    document.head.appendChild(s);
  }

  function place(sec) {
    var sum = sec.querySelector(":scope>details>summary");
    var h2 = sec.querySelector("h2");
    var box = document.createElement("details");
    box.className = "imr-plain"; box.setAttribute("data-noi18n", "");
    box.innerHTML = "<summary></summary><div></div>";
    if (sum && sum.contains(h2)) sum.insertAdjacentElement("afterend", box);
    else if (h2) {
      // keep a short lead paragraph that directly follows the heading in front of the note
      var n = h2.nextElementSibling;
      (n && n.tagName === "P" && n.textContent.length < 400 ? n : h2).insertAdjacentElement("afterend", box);
    } else sec.insertBefore(box, sec.firstChild);
    return box;
  }

  function paint() {
    var l = lang(), on = get();
    boxes.forEach(function (b) {
      b.el.querySelector("summary").textContent = L[l].sum;
      b.el.querySelector("div").innerHTML = b.t[l] || b.t.en;
    });
    if (btn) { btn.textContent = on ? L[l].on : L[l].off; btn.setAttribute("aria-pressed", on); btn.title = L[l].tip; }
    document.body.classList.toggle("imr-plain-on", on);
  }

  function init() {
    css();
    Object.keys(T).forEach(function (sel) {
      var sec = document.querySelector(sel);
      if (sec) boxes.push({ el: place(sec), t: T[sel] });
    });
    if (!boxes.length) return;
    btn = document.createElement("button");
    btn.type = "button"; btn.className = "imr-plain-sw"; btn.setAttribute("data-noi18n", "");
    btn.addEventListener("click", function () {
      var v = !get(); set(v);
      boxes.forEach(function (b) { b.el.open = v; });
      paint();
    });
    document.body.appendChild(btn);
    var on = get();
    boxes.forEach(function (b) { b.el.open = on; });
    paint();
    new MutationObserver(paint).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
