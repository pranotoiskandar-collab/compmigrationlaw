
  /* Protection from violence: legal and policy provisions of the state of origin. Coded separately from the nine features above and
     not part of the weighted comparison. Standards: ICRMW Art. 16(2), CEDAW General Recommendation No. 26 (paras. 24–26),
     ILO C190 and R206, UN General Assembly resolutions on violence against women migrant workers (latest A/RES/80/185, 2025). */
  vcodebook: [
    {k:"shelter", en:"Shelter for workers in distress abroad", id:"Tempat penampungan bagi pekerja bermasalah di luar negeri",
     l2:"A statute requires shelters or resource centers with temporary accommodation at missions in destination countries", l1:"Shelters or safe houses are run at some missions by policy or practice", l0:"No shelters documented",
     l2_id:"Undang-undang mewajibkan tempat penampungan atau pusat layanan dengan akomodasi sementara di perwakilan negara tujuan", l1_id:"Tempat penampungan dikelola di sebagian perwakilan berdasarkan kebijakan atau praktik", l0_id:"Tidak ada tempat penampungan yang terdokumentasi"},
    {k:"hotline", en:"Round-the-clock assistance line", id:"Layanan bantuan 24 jam",
     l2:"An official assistance line or crisis center for workers abroad operates 24 hours", l1:"An official line exists but not around the clock, or only at some missions", l0:"No official line documented",
     l2_id:"Saluran bantuan atau crisis center resmi bagi pekerja di luar negeri beroperasi 24 jam", l1_id:"Saluran resmi ada tetapi tidak 24 jam, atau hanya di sebagian perwakilan", l0_id:"Tidak ada saluran resmi yang terdokumentasi"},
    {k:"legalaid", en:"Legal assistance abroad", id:"Bantuan hukum di luar negeri",
     l2:"A statute provides or funds legal assistance for workers abroad, including in criminal and civil proceedings", l1:"Legal assistance is funded by policy or discretionary funds", l0:"No public legal assistance documented",
     l2_id:"Undang-undang menyediakan atau membiayai bantuan hukum bagi pekerja di luar negeri, termasuk dalam perkara pidana dan perdata", l1_id:"Bantuan hukum dibiayai berdasarkan kebijakan atau dana diskresioner", l0_id:"Tidak ada bantuan hukum publik yang terdokumentasi"},
    {k:"gender", en:"Gender-specific protection", id:"Pelindungan khusus gender",
     l2:"Statute contains specific duties on violence against women migrant workers (for example gender-responsive services or officers)", l1:"Gender-specific measures rest on policy or programs", l0:"No gender-specific provision found",
     l2_id:"Undang-undang memuat kewajiban khusus tentang kekerasan terhadap perempuan pekerja migran (misalnya layanan atau petugas yang responsif gender)", l1_id:"Langkah khusus gender bertumpu pada kebijakan atau program", l0_id:"Tidak ditemukan ketentuan khusus gender"},
    {k:"death", en:"Deaths abroad: repatriation and inquiry", id:"Kematian di luar negeri: pemulangan dan pemeriksaan",
     l2:"Repatriation of remains and a death benefit are guaranteed by law, and families can obtain an independent examination of the cause of death", l1:"Repatriation and a death benefit are provided, without a route to establish the cause of death", l0:"Neither is guaranteed",
     l2_id:"Pemulangan jenazah dan santunan kematian dijamin hukum, dan keluarga bisa memperoleh pemeriksaan independen atas sebab kematian", l1_id:"Pemulangan dan santunan kematian diberikan, tanpa jalur untuk memastikan sebab kematian", l0_id:"Tidak satu pun dijamin"},
    {k:"traffic", en:"Anti-trafficking law covering labor", id:"UU antiperdagangan orang yang mencakup kerja",
     l2:"A dedicated statute criminalizes trafficking for forced labor and provides victim assistance, protection or restitution", l1:"Trafficking is an offense under the general criminal law, with limited victim provisions", l0:"No offense of trafficking for labor",
     l2_id:"UU khusus memidanakan perdagangan orang untuk kerja paksa dan menyediakan bantuan, pelindungan atau restitusi bagi korban", l1_id:"Perdagangan orang adalah tindak pidana dalam hukum pidana umum, dengan ketentuan korban yang terbatas", l0_id:"Tidak ada tindak pidana perdagangan orang untuk kerja"}
  ],
  vcodes: {
    ID: {
      shelter:[1, "Missions run shelters for citizens in distress as part of citizen protection; no statutory duty to maintain them was found in Law 18/2017.", "Ministry of Foreign Affairs, citizen protection; Law 18/2017"],
      hotline:[1, "KP2MI runs a crisis center and complaint channels; round-the-clock operation is not confirmed.", "KP2MI"],
      legalaid:[2, "Protection during work includes legal assistance and advocacy by the government and missions.", "Law 18/2017 Art. 21"],
      gender:[1, "The 2017 Law states general principles of non-discrimination and gender equality; services for women survivors rest on programs with the women's empowerment ministry.", "Law 18/2017 Art. 2; KemenPPPA programs"],
      death:[1, "BPJS Ketenagakerjaan pays death benefits and the government repatriates remains; no procedure for an independent examination of the cause of death was found.", "Manpower Reg. 4/2023"],
      traffic:[2, "Law 21/2007 criminalizes trafficking for exploitation including forced labor, with restitution and witness and victim protection.", "Law 21/2007"]},
    PH: {
      shelter:[2, "Migrant Workers and Other Overseas Filipinos Resource Centers at missions provide counseling, legal services and temporary shelter.", "RA 8042 sec. 19 as amended; RA 11641"],
      hotline:[2, "The Department of Migrant Workers and OWWA operate a 24-hour operations center and hotlines.", "DMW; OWWA"],
      legalaid:[2, "A Legal Assistance Fund and a Legal Assistant for Migrant Workers' Affairs provide legal services to workers abroad.", "RA 8042 secs. 24–26 as amended"],
      gender:[2, "The law requires gender-sensitive programs and services for women migrant workers; the Magna Carta of Women adds duties for women overseas.", "RA 8042 sec. 2(d) as amended; RA 9710"],
      death:[1, "Repatriation of remains is at the agency's cost and OWWA pays death benefits; autopsies are available on the family's request through the National Bureau of Investigation, but no statutory inquiry procedure was found.", "RA 8042 sec. 15; RA 10801"],
      traffic:[2, "Comprehensive anti-trafficking law with victim protection, assistance and a council; amended in 2012 and 2022.", "RA 9208 as amended by RA 10364 and RA 11862"]},
    VN: {
      shelter:[0, "No dedicated shelters at missions were documented; labor management sections assist workers.", "Law 69/2020"],
      hotline:[1, "The Department of Overseas Labor and missions operate hotlines; round-the-clock operation is not confirmed.", "Department of Overseas Labor"],
      legalaid:[2, "The Overseas Employment Support Fund can fund legal support for workers abroad.", "Law 69/2020 Art. 67; Decision 40/2021/QĐ-TTg"],
      gender:[1, "The Law applies a general principle of gender equality; no specific duty on violence against women migrant workers was found.", "Law 69/2020; Law on Gender Equality 2006"],
      death:[1, "The Support Fund pays death support and repatriation costs; no independent examination route was found.", "Decision 40/2021/QĐ-TTg"],
      traffic:[2, "A dedicated Law on Human Trafficking Prevention and Combat (2011) with victim support; a new law adopted in 2024 replaces it (in force 2025, to be confirmed).", "Law 66/2011/QH12; Law on Prevention and Combat of Human Trafficking 2024"]},
    NP: {
      shelter:[1, "Safe houses are run at some missions with support from the Foreign Employment Welfare Fund.", "FEA 2007 s. 33; Foreign Employment Board"],
      hotline:[1, "The Department of Foreign Employment and the Foreign Employment Board run helplines; round-the-clock operation is not confirmed.", "DoFE; FEB"],
      legalaid:[1, "The Welfare Fund and missions provide assistance, but no statutory legal aid for proceedings abroad was found.", "FEA 2007 s. 33"],
      gender:[1, "The Foreign Employment Policy 2012 has a section on women workers; the Act has no specific provision on violence.", "Foreign Employment Policy 2012"],
      death:[1, "The Welfare Fund pays compensation to families and repatriates remains; causes of death are rarely examined after return.", "FEA 2007 s. 33; FEB"],
      traffic:[2, "Dedicated Act criminalizes trafficking and transportation, with rehabilitation and compensation for victims.", "Human Trafficking and Transportation (Control) Act 2007"]},
    BD: {
      shelter:[1, "Safe homes for women workers are run at some missions by policy.", "OEMP 2016; Ministry of Expatriates' Welfare"],
      hotline:[1, "Official helplines for migrants exist; round-the-clock operation is not confirmed.", "Probashi helpline; WEWB"],
      legalaid:[2, "The Wage Earners' Welfare Fund may be used for legal aid to migrant workers abroad.", "Wage Earners' Welfare Board Act 2018"],
      gender:[1, "The 2016 Policy has measures for women migrant workers, including safe homes and complaint desks; the 2013 Act has no specific provision on violence.", "OEMP 2016"],
      death:[1, "The Welfare Board pays burial costs (Tk 35,000) and compensation and receives remains; post-mortem examination on arrival is rare.", "WEWB; Daily Star, 2025"],
      traffic:[2, "Dedicated Act with special tribunals and victim protection and rehabilitation.", "Prevention and Suppression of Human Trafficking Act 2012"]},
    IN: {
      shelter:[1, "The Indian Community Welfare Fund pays for shelters for workers in distress at some missions.", "ICWF guidelines"],
      hotline:[1, "The MADAD portal and mission helplines; some missions run 24-hour lines.", "MEA; missions"],
      legalaid:[1, "The ICWF funds legal assistance at the mission's discretion; no statutory basis.", "ICWF guidelines"],
      gender:[1, "Advisories and ICWF assistance for women in distress; no specific statutory provision found.", "MEA"],
      death:[1, "PBBY (for ECR workers) and the ICWF cover repatriation of remains; no independent examination route found.", "PBBY 2017; ICWF guidelines"],
      traffic:[1, "Trafficking is an offense under the general criminal law (Bharatiya Nyaya Sanhita 2023 s. 143, formerly IPC s. 370); a comprehensive trafficking bill (2018) lapsed.", "BNS 2023; Trafficking of Persons Bill 2018"]},
    LK: {
      shelter:[1, "Safe houses for workers in distress are run at several missions by the Bureau.", "SLBFE"],
      hotline:[2, "The Bureau operates a 24-hour hotline.", "SLBFE"],
      legalaid:[1, "The Workers' Welfare Fund supports workers in distress; no statutory legal aid for proceedings abroad was found.", "SLBFE Act 1985 s. 45"],
      gender:[1, "The National Labour Migration Policy has measures for women workers; no specific statutory provision on violence.", "National Labour Migration Policy 2008"],
      death:[1, "Insurance and the Welfare Fund cover death benefits and repatriation; no independent examination route found.", "SLBFE"],
      traffic:[1, "Trafficking is an offense under the Penal Code (s. 360C, 2006); victims are covered by the 2015 victims and witnesses protection act.", "Penal Code s. 360C; Act No. 4 of 2015"]},
    PK: {
      shelter:[1, "Community Welfare Attachés arrange shelter at some missions; no statutory duty found.", "Ministry of Overseas Pakistanis"],
      hotline:[1, "The Overseas Pakistanis Foundation and the Ministry run helplines; round-the-clock operation is not confirmed.", "OPF"],
      legalaid:[1, "Missions may fund legal assistance by policy.", "National Emigration and Welfare Policy 2020"],
      gender:[0, "No gender-specific provision on violence against women migrant workers found in the Ordinance or the 2020 Policy.", "Emigration Ordinance 1979; NEWP 2020"],
      death:[1, "The Overseas Pakistanis Foundation repatriates remains free of charge and insurance pays a death benefit; no independent examination route found.", "OPF; Emigration Rules 1979"],
      traffic:[2, "Dedicated Act criminalizes trafficking in persons including for forced labor, with victim protection.", "Prevention of Trafficking in Persons Act 2018"]}
  },
  /* Deaths of workers abroad recorded by authorities of the country of origin. No breakdown by destination is shown. */
  deaths: [
    {s:"NP", v:1517, y:"FY 2024/25", what:"Deaths of workers abroad recorded by the Foreign Employment Board", what_id:"Kematian pekerja di luar negeri yang dicatat Dewan Ketenagakerjaan Luar Negeri", note:"A narrower count of deaths after labor approval with family compensation is 1,255; Nepal Police recorded 1,401 bodies repatriated.", note_id:"Hitungan yang lebih sempit (kematian setelah persetujuan kerja dengan santunan keluarga) adalah 1.255; Kepolisian Nepal mencatat 1.401 jenazah dipulangkan.", src:["Republica, citing the Foreign Employment Board", "https://myrepublica.nagariknetwork.com/news/1500-nepali-migrant-workers-die-abroad-in-a-year-15-98.html"]},
    {s:"BD", v:4813, y:"2024", what:"Remains of migrant workers received by the Wage Earners' Welfare Board", what_id:"Jenazah pekerja migran yang diterima Dewan Kesejahteraan Pekerja", note:"3,818 in 2021, 3,904 in 2022, 4,552 in 2023. About 94% were men.", note_id:"3.818 pada 2021, 3.904 pada 2022, 4.552 pada 2023. Sekitar 94% laki-laki.", src:["The Daily Star, citing WEWB", "https://www.thedailystar.net/nrb/migration/news/4813-bodies-migrant-workers-arrived-bangladesh-2024-3807321"]}
  ],
