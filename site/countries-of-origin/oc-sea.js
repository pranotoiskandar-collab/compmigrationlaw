/* Countries of origin, Southeast Asia extension (version 1.3 of the origin data, 13 November 2026).
   Adds Myanmar, Cambodia, Laos and Timor-Leste to window.OC. Loaded after oc-data.js and before oc.js on
   /countries-of-origin/ and /southeast-asia/. All cells are S (secondary sources and statutory citations not yet
   checked against the official text); a null value means the position could not be established and is shown as
   "Unclear". Official texts are being checked on the official sites only (Myanmar Law Information System,
   Cambodia MoLVT, Lao Official Gazette, Jornal da República; ministry sites as official guidance).
   Corrections: secretariat@theimr.org */
(function (G) {
  if (!G) return;
  G.version = "1.3";
  G.updated = "13 November 2026";

  G.states.push(
    {k:"MM", iso3:"MMR", n:"Myanmar", n_id:"Myanmar", sea:true,
     law:"Law Relating to Overseas Employment 1999 (State Peace and Development Council Law No. 3/99) and its rules; Anti-Trafficking in Persons Law 2022",
     policy:"Overseas employment through licensed agencies and government-to-government memoranda, mainly to Thailand, Malaysia, Singapore, Japan and South Korea; overseas worker identity cards; pre-departure orientation. Since 2024 the authorities have restricted overseas work permits for men of conscription age.",
     policy_id:"Penempatan kerja luar negeri melalui agensi berizin dan nota kesepahaman antarpemerintah, terutama ke Thailand, Malaysia, Singapura, Jepang dan Korea Selatan; kartu identitas pekerja luar negeri; orientasi pra-keberangkatan. Sejak 2024 otoritas membatasi izin kerja luar negeri bagi laki-laki usia wajib militer.",
     inst:"Ministry of Labour (Department of Labour); labor attachés in some missions",
     inst_id:"Kementerian Tenaga Kerja (Departemen Tenaga Kerja); atase tenaga kerja di sebagian perwakilan",
     status:"Party to the ICESCR (2017), CEDAW and the Palermo Protocol, and to ILO C29 and C87. Not party to the ICCPR, the UN migrant workers convention or ILO C97, C143, C181, C189 or C190.",
     status_id:"Pihak ICESCR (2017), CEDAW dan Protokol Palermo, serta ILO C29 dan C87. Bukan pihak ICCPR, Konvensi Pekerja Migran PBB maupun ILO C97, C143, C181, C189 atau C190.",
     complaints:"Department of Labour complaint desks; labor attachés; for workers in Thailand, the Thai hotlines and migrant worker assistance centers.",
     complaints_id:"Meja pengaduan Departemen Tenaga Kerja; atase tenaga kerja; bagi pekerja di Thailand, saluran bantuan dan pusat bantuan pekerja migran Thailand."},
    {k:"KH", iso3:"KHM", n:"Cambodia", n_id:"Kamboja", sea:true,
     law:"Sub-Decree No. 190 on the Management of Sending Cambodian Workers Abroad through Private Recruitment Agencies (2011) and its Prakas (ministerial regulations, 2013); Labour Migration Policy; Law on Suppression of Human Trafficking and Sexual Exploitation 2008",
     policy:"Placement through licensed private recruitment agencies with a deposit, and through memoranda with Thailand, Malaysia, South Korea and Japan; Prakas on pre-departure orientation, contracts and complaints; a national Labour Migration Policy.",
     policy_id:"Penempatan melalui agensi rekrutmen swasta berizin dengan deposit, dan melalui nota kesepahaman dengan Thailand, Malaysia, Korea Selatan dan Jepang; Prakas tentang orientasi pra-keberangkatan, kontrak dan pengaduan; Kebijakan Migrasi Tenaga Kerja nasional.",
     inst:"Ministry of Labour and Vocational Training (Department of Employment and Manpower); labor attachés in Thailand, Malaysia, South Korea and Japan",
     inst_id:"Kementerian Tenaga Kerja dan Pelatihan Vokasi (Departemen Ketenagakerjaan); atase tenaga kerja di Thailand, Malaysia, Korea Selatan dan Jepang",
     status:"Party to the ICCPR, ICESCR, CEDAW and the Palermo Protocol, and to ILO C29, C87 and C98. Signed but has not ratified the UN migrant workers convention (2004).",
     status_id:"Pihak ICCPR, ICESCR, CEDAW dan Protokol Palermo, serta ILO C29, C87 dan C98. Menandatangani tetapi belum meratifikasi Konvensi Pekerja Migran PBB (2004).",
     complaints:"Complaint mechanism of the Ministry of Labour and Vocational Training under the 2013 Prakas, with conciliation against agencies; provincial labor departments; labor attachés.",
     complaints_id:"Mekanisme pengaduan Kementerian Tenaga Kerja dan Pelatihan Vokasi menurut Prakas 2013, dengan konsiliasi terhadap agensi; dinas tenaga kerja provinsi; atase tenaga kerja."},
    {k:"LA", iso3:"LAO", n:"Laos", n_id:"Laos", sea:true,
     law:"Labour Law 2013 (No. 43/NA); Decree on the Dispatch of Lao Workers to Work Abroad (2020); Law on Anti-Trafficking in Persons 2015",
     policy:"Placement through licensed employment service enterprises and the memorandum with Thailand (2002, revised 2016); Thailand takes most workers, many outside the formal channel.",
     policy_id:"Penempatan melalui perusahaan jasa ketenagakerjaan berizin dan nota kesepahaman dengan Thailand (2002, direvisi 2016); Thailand menerima sebagian besar pekerja, banyak di luar jalur resmi.",
     inst:"Ministry of Labour and Social Welfare (Department of Skills Development and Employment); labor attaché in Bangkok",
     inst_id:"Kementerian Tenaga Kerja dan Kesejahteraan Sosial (Departemen Pengembangan Keterampilan dan Ketenagakerjaan); atase tenaga kerja di Bangkok",
     status:"Party to the ICCPR, ICESCR (2007), CEDAW and the Palermo Protocol, and to ILO C29. Not party to the UN migrant workers convention or ILO C87, C98, C97, C143, C181, C189 or C190.",
     status_id:"Pihak ICCPR, ICESCR (2007), CEDAW dan Protokol Palermo, serta ILO C29. Bukan pihak Konvensi Pekerja Migran PBB maupun ILO C87, C98, C97, C143, C181, C189 atau C190.",
     complaints:"Ministry of Labour and Social Welfare and provincial labor offices; labor attaché in Bangkok; village mediation units.",
     complaints_id:"Kementerian Tenaga Kerja dan Kesejahteraan Sosial dan kantor tenaga kerja provinsi; atase tenaga kerja di Bangkok; unit mediasi desa."},
    {k:"TL", iso3:"TLS", n:"Timor-Leste", n_id:"Timor-Leste", sea:true,
     law:"Labour Code (Law No. 4/2012); Law No. 3/2017 on Preventing and Combating Human Trafficking; government-to-government labor mobility schemes",
     policy:"Overseas work runs mainly through government-to-government schemes: South Korea's Employment Permit System, Australia's Pacific Australia Labour Mobility scheme and seasonal work in Australia, and the United Kingdom's seasonal worker route (to confirm). The state selects and prepares workers.",
     policy_id:"Kerja luar negeri terutama melalui skema antarpemerintah: Sistem Izin Kerja Korea Selatan, skema Pacific Australia Labour Mobility dan kerja musiman di Australia, serta jalur pekerja musiman Inggris (perlu dipastikan). Negara memilih dan menyiapkan pekerja.",
     inst:"Secretariat of State for Vocational Training and Employment (SEFOPE); labor attachés in South Korea and Australia",
     inst_id:"Sekretariat Negara untuk Pelatihan Vokasi dan Ketenagakerjaan (SEFOPE); atase tenaga kerja di Korea Selatan dan Australia",
     status:"Party to the UN migrant workers convention (2004), the two covenants, CEDAW and the Palermo Protocol, and to ILO C29, C87 and C98. Became the eleventh ASEAN member in 2025.",
     status_id:"Pihak Konvensi Pekerja Migran PBB (2004), kedua kovenan, CEDAW dan Protokol Palermo, serta ILO C29, C87 dan C98. Menjadi anggota ASEAN kesebelas pada 2025.",
     complaints:"SEFOPE and labor attachés; for scheme workers, the complaint channels of the destination scheme.",
     complaints_id:"SEFOPE dan atase tenaga kerja; bagi pekerja skema, saluran pengaduan skema negara tujuan."}
  );

  G.codes.MM = {
    rec:[1, "Overseas employment agencies must be licensed by the Ministry of Labour and can lose their licence; the 1999 Law does not make them jointly liable with the employer abroad.", "Law Relating to Overseas Employment 1999, Chapters 4–6"],
    fees:[1, "Service fees are set by the Ministry for each destination (for example under the Thailand memorandum); no general ban on fees charged to workers.", "Ministry of Labour notifications; Law Relating to Overseas Employment 1999"],
    contract:[1, "A contract is required for placement through licensed agencies and is approved by the Ministry; workers who go through informal channels have none.", "Law Relating to Overseas Employment 1999"],
    predep:[1, "Orientation is compulsory for workers placed through agencies; who bears the cost is not settled in the Law.", "Ministry of Labour"],
    welfare:[0, "No statutory welfare fund or compulsory insurance for overseas workers was found.", "Law Relating to Overseas Employment 1999"],
    attache:[1, "Labor attachés are posted in some destinations by administrative decision.", "Ministry of Labour"],
    redress:[1, "Complaints against agencies lead to licence sanctions or refunds; compensation needs the courts.", "Law Relating to Overseas Employment 1999"],
    exit:[null, "Restrictions have been both occupation- and sex-specific: a ban on women going abroad as domestic workers (2014, later relaxed for some destinations) and, since May 2024, a suspension of overseas work permits for men of conscription age. Neither fits one value of the codebook; to be coded after the official texts are checked.", "Ministry of Labour announcements, 2014 and 2024 (to check)"],
    return:[0, "No statutory or policy framework for reintegration by a public body was found.", "Ministry of Labour"]
  };
  G.codes.KH = {
    rec:[1, "Private recruitment agencies need a licence and a deposit and can be sanctioned; liability for the employer's obligations abroad is not joint.", "Sub-Decree No. 190 (2011); Prakas on recruitment agencies (2013)"],
    fees:[1, "Fees and the costs workers may be charged are regulated by Prakas, without a general ban.", "Sub-Decree No. 190 (2011); Prakas (2013)"],
    contract:[2, "A written employment contract with minimum terms must be signed and verified before departure.", "Sub-Decree No. 190 (2011); Prakas on contracts (2013)"],
    predep:[1, "Pre-departure orientation is compulsory; the cost may be passed to the worker through the agency.", "Prakas on pre-departure orientation (2013)"],
    welfare:[0, "No statutory welfare fund for overseas workers; the National Social Security Fund does not cover work abroad (to confirm).", "Sub-Decree No. 190 (2011)"],
    attache:[1, "Labor attachés are posted in the main destinations by administrative decision.", "Ministry of Labour and Vocational Training"],
    redress:[1, "The Ministry's complaint mechanism can order agencies to pay compensation through conciliation; enforcement relies on licence sanctions and the courts.", "Prakas on the complaint mechanism (2013)"],
    exit:[1, "A minimum age of 18; past suspensions of domestic work placements to Malaysia (2011–2015) were occupation-specific on their face, although almost all domestic workers are women.", "Sub-Decree No. 190 (2011); Ministry announcements"],
    return:[1, "Reintegration rests on the Labour Migration Policy and programs, without a statutory duty.", "Labour Migration Policy"]
  };
  G.codes.LA = {
    rec:[1, "Employment service enterprises must be licensed by the Ministry; no joint liability with the employer abroad was found.", "Labour Law 2013; Decree on the Dispatch of Lao Workers to Work Abroad (2020)"],
    fees:[1, "Service fees are regulated by the Decree without a general ban.", "Decree on the Dispatch of Lao Workers to Work Abroad (2020)"],
    contract:[1, "A contract is required for workers sent through enterprises; verification of minimum terms is not confirmed.", "Labour Law 2013"],
    predep:[1, "Pre-departure training is required for workers sent through enterprises; cost not settled.", "Decree on the Dispatch of Lao Workers to Work Abroad (2020)"],
    welfare:[0, "No statutory welfare fund for overseas workers was found.", "Labour Law 2013"],
    attache:[1, "A labor attaché is posted in Bangkok by administrative decision.", "Ministry of Labour and Social Welfare"],
    redress:[1, "Complaints to the Ministry can lead to sanctions on enterprises; compensation needs mediation or the courts.", "Labour Law 2013"],
    exit:[1, "Minimum age and occupation restrictions, sex-neutral on their face (to confirm).", "Decree on the Dispatch of Lao Workers to Work Abroad (2020)"],
    return:[1, "Reintegration rests on programs with development partners, without a statutory duty.", "Ministry of Labour and Social Welfare"]
  };
  G.codes.TL = {
    rec:[null, "Placement runs through government-to-government schemes run by SEFOPE; no private recruitment framework was found, so this feature does not apply in the usual way.", "SEFOPE; Labour Code (Law No. 4/2012)"],
    fees:[null, "Under the schemes the destination employer or government bears most costs; no Timorese rule on fees charged to workers was found.", "SEFOPE; scheme rules of the destination states"],
    contract:[2, "Scheme workers sign a contract with minimum terms set by the destination scheme and checked by SEFOPE before departure.", "SEFOPE; destination scheme rules"],
    predep:[2, "SEFOPE runs compulsory pre-departure training for scheme workers at no charge (to confirm).", "SEFOPE"],
    welfare:[null, "No statutory fund found; scheme workers are insured under destination rules.", "SEFOPE"],
    attache:[1, "Labor attachés in South Korea and Australia by administrative decision.", "SEFOPE"],
    redress:[0, "Only the ordinary courts; no specialized body found.", "Labour Code (Law No. 4/2012)"],
    exit:[2, "No emigration restrictions by sex or age beyond scheme eligibility.", "SEFOPE"],
    return:[1, "Reintegration rests on programs, without a statutory duty.", "SEFOPE"]
  };

  G.intl.MM = {iccpr:"", icescr:"p 2017", cedaw:"p 1997", icrmw:"", palermo:"p 2004", c29:"p 1955", c87:"p 1955", c98:"", c97:"", c143:"", c181:"", c189:"", c190:""};
  G.intl.KH = {iccpr:"p 1992", icescr:"p 1992", cedaw:"p 1992", icrmw:"", palermo:"p 2007", c29:"p 1969", c87:"p 1999", c98:"p 1999", c97:"", c143:"", c181:"", c189:"", c190:""};
  G.intl.LA = {iccpr:"p 2009", icescr:"p 2007", cedaw:"p 1981", icrmw:"", palermo:"p 2003", c29:"p 1964", c87:"", c98:"", c97:"", c143:"", c181:"", c189:"", c190:""};
  G.intl.TL = {iccpr:"p 2003", icescr:"p 2003", cedaw:"p 2003", icrmw:"p 2004", palermo:"p 2009", c29:"p 2009", c87:"p 2009", c98:"p 2009", c97:"", c143:"", c181:"", c189:"", c190:""};
  G.intl_note += " Myanmar, Cambodia, Laos and Timor-Leste (added 13 November 2026): ICESCR, ICRMW and the ILO C097, C143, C181, C189 and C190 columns come from the same official extracts (Cambodia signed the ICRMW in 2004 but has not ratified it; Timor-Leste is party since 2004); the other columns rest on secondary sources until checked.";
  G.intl_note_id += " Myanmar, Kamboja, Laos dan Timor-Leste (ditambahkan 13 November 2026): kolom ICESCR, ICRMW dan ILO C097, C143, C181, C189 dan C190 berasal dari ekstrak resmi yang sama (Kamboja menandatangani ICRMW pada 2004 tetapi belum meratifikasinya; Timor-Leste pihak sejak 2004); kolom lainnya bersandar pada sumber sekunder sampai diperiksa.";

  G.vcodes.MM = {shelter:[null, "Not yet documented.", ""], hotline:[null, "Not yet documented.", ""], legalaid:[null, "Not yet documented.", ""], gender:[null, "Not yet documented.", ""], death:[null, "Not yet documented.", ""],
    traffic:[2, "A dedicated anti-trafficking law covering forced labor, with victim protection; the 2005 Law was replaced in 2022.", "Anti-Trafficking in Persons Law 2022"]};
  G.vcodes.KH = {shelter:[null, "Not yet documented.", ""], hotline:[null, "Not yet documented.", ""], legalaid:[null, "Not yet documented.", ""], gender:[null, "Not yet documented.", ""], death:[null, "Not yet documented.", ""],
    traffic:[2, "A dedicated law criminalizes trafficking, including for labor, with victim provisions.", "Law on Suppression of Human Trafficking and Sexual Exploitation 2008"]};
  G.vcodes.LA = {shelter:[null, "Not yet documented.", ""], hotline:[null, "Not yet documented.", ""], legalaid:[null, "Not yet documented.", ""], gender:[null, "Not yet documented.", ""], death:[null, "Not yet documented.", ""],
    traffic:[2, "A dedicated law criminalizes trafficking for labor and provides victim assistance.", "Law on Anti-Trafficking in Persons 2015"]};
  G.vcodes.TL = {shelter:[null, "Not yet documented.", ""], hotline:[null, "Not yet documented.", ""], legalaid:[null, "Not yet documented.", ""], gender:[null, "Not yet documented.", ""], death:[null, "Not yet documented.", ""],
    traffic:[2, "A dedicated law criminalizes trafficking, including for labor, with victim protection.", "Law No. 3/2017 on Preventing and Combating Human Trafficking"]};

  [].push.apply(G.frameworks, [
    {s:"MM", partner:"Thailand", title:"MOU on cooperation in the employment of workers", level:"bilateral", nature:"mou", signed:"2003", in_force:"", scope:"Revised 2016; basis of the MOU system"},
    {s:"MM", partner:"South Korea", title:"MOU on sending workers under the Employment Permit System", level:"bilateral", nature:"mou", signed:"2007", in_force:"", scope:"Renewed periodically"},
    {s:"MM", partner:"Japan", title:"Memorandum of cooperation on Specified Skilled Workers", level:"bilateral", nature:"mou", signed:"2019", in_force:"", scope:""},
    {s:"KH", partner:"Thailand", title:"MOU on cooperation in the employment of workers", level:"bilateral", nature:"mou", signed:"2003", in_force:"", scope:"Revised 2015"},
    {s:"KH", partner:"Malaysia", title:"MOU on the recruitment and employment of Cambodian domestic workers", level:"bilateral", nature:"mou", signed:"2015", in_force:"", scope:"To confirm status"},
    {s:"KH", partner:"South Korea", title:"MOU on sending workers under the Employment Permit System", level:"bilateral", nature:"mou", signed:"2006", in_force:"", scope:"Renewed periodically"},
    {s:"KH", partner:"Japan", title:"Memorandum of cooperation on Specified Skilled Workers", level:"bilateral", nature:"mou", signed:"2019", in_force:"", scope:""},
    {s:"LA", partner:"Thailand", title:"MOU on employment cooperation", level:"bilateral", nature:"mou", signed:"2002", in_force:"", scope:"Revised 2016"},
    {s:"LA", partner:"South Korea", title:"E-10-2 fishing crew pathway and seasonal work arrangements", level:"bilateral", nature:"agreement", signed:"", in_force:"", scope:"To confirm"},
    {s:"TL", partner:"South Korea", title:"MOU on sending workers under the Employment Permit System", level:"bilateral", nature:"mou", signed:"2008", in_force:"", scope:"Renewed periodically"},
    {s:"TL", partner:"Australia", title:"Participation in the Pacific Australia Labour Mobility scheme", level:"bilateral", nature:"agreement", signed:"", in_force:"", scope:"Seasonal and longer-term placements"}
  ]);

  [].push.apply(G.laws, [
    {s:"MM", title:"Law Relating to Overseas Employment (SPDC Law No. 3/99)", orig:"", year:"1999", amended:"", type:"statute", topic:"Licensing of agencies, contracts, offences", url:"https://www.mlis.gov.mm/", link:"db"},
    {s:"MM", title:"Anti-Trafficking in Persons Law 2022", orig:"", year:"2022", amended:"", type:"statute", topic:"Trafficking, including for labor", url:"https://www.mlis.gov.mm/", link:"db"},
    {s:"KH", title:"Sub-Decree No. 190 on the Management of Sending Cambodian Workers Abroad through Private Recruitment Agencies", orig:"អនុក្រឹត្យលេខ ១៩០", year:"2011", amended:"", type:"regulation", topic:"Licensing, deposits, contracts, orientation, complaints", url:"https://www.mlvt.gov.kh/", link:"db"},
    {s:"KH", title:"Prakas implementing Sub-Decree No. 190 (pre-departure orientation, contracts, complaint mechanism, agency licensing)", orig:"ប្រកាស", year:"2013", amended:"", type:"regulation", topic:"Detailed rules", url:"https://www.mlvt.gov.kh/", link:"db"},
    {s:"KH", title:"Law on Suppression of Human Trafficking and Sexual Exploitation", orig:"", year:"2008", amended:"", type:"statute", topic:"Trafficking", url:"https://www.mlvt.gov.kh/", link:"db"},
    {s:"LA", title:"Labour Law (No. 43/NA)", orig:"ກົດໝາຍວ່າດ້ວຍແຮງງານ", year:"2013", amended:"", type:"statute", topic:"General labor law, including Lao workers abroad", url:"https://laoofficialgazette.gov.la/", link:"db"},
    {s:"LA", title:"Decree on the Dispatch of Lao Workers to Work Abroad", orig:"", year:"2020", amended:"", type:"regulation", topic:"Licensing, fees, contracts, training", url:"https://laoofficialgazette.gov.la/", link:"db"},
    {s:"LA", title:"Law on Anti-Trafficking in Persons", orig:"", year:"2015", amended:"", type:"statute", topic:"Trafficking", url:"https://laoofficialgazette.gov.la/", link:"db"},
    {s:"TL", title:"Labour Code (Law No. 4/2012)", orig:"Código do Trabalho (Lei n.º 4/2012)", year:"2012", amended:"", type:"statute", topic:"General labor law", url:"https://www.jornal.gov.tl/", link:"db"},
    {s:"TL", title:"Law No. 3/2017 on Preventing and Combating Human Trafficking", orig:"Lei n.º 3/2017", year:"2017", amended:"", type:"statute", topic:"Trafficking", url:"https://www.jornal.gov.tl/", link:"db"}
  ]);

  [].push.apply(G.reforms, [
    ["1999-07","MM","Law Relating to Overseas Employment enacted.","UU tentang Penempatan Kerja Luar Negeri diundangkan.","law"],
    ["2004-01","TL","Timor-Leste accedes to the UN migrant workers convention.","Timor-Leste mengaksesi Konvensi Pekerja Migran PBB.","law"],
    ["2011-08","KH","Sub-Decree No. 190 on sending workers abroad through private agencies.","Sub-Dekret No. 190 tentang pengiriman pekerja melalui agensi swasta.","law"],
    ["2011-10","KH","Suspension of domestic worker placements to Malaysia (lifted with the 2015 memorandum).","Penangguhan penempatan PRT ke Malaysia (dicabut dengan nota kesepahaman 2015).","restrict"],
    ["2013-07","LA","New Labour Law, with provisions on Lao workers abroad.","UU Ketenagakerjaan baru, dengan ketentuan tentang pekerja Laos di luar negeri.","law"],
    ["2017-10","MM","Myanmar ratifies the ICESCR.","Myanmar meratifikasi ICESCR.","law"],
    ["2024-05","MM","Suspension of overseas work permits for men of conscription age.","Penangguhan izin kerja luar negeri bagi laki-laki usia wajib militer.","restrict"]
  ]);

  G.advocacy.MM = {args:[["Myanmar is party to the ICESCR since 2017; Article 6 (right to work) and Article 2(2) (non-discrimination) can be raised on restrictions on leaving to work abroad.","Myanmar pihak ICESCR sejak 2017; Pasal 6 (hak atas pekerjaan) dan Pasal 2(2) (nondiskriminasi) bisa diajukan terhadap pembatasan keluar untuk bekerja."]],
    avenues:[["For workers in Thailand and Malaysia, the destination's labor courts and hotlines are usually more reachable than remedies at home.","Bagi pekerja di Thailand dan Malaysia, pengadilan perburuhan dan saluran bantuan negara tujuan biasanya lebih terjangkau daripada upaya di dalam negeri."]]};
  G.advocacy.KH = {args:[["Cambodia signed the UN migrant workers convention in 2004; ratification and a dedicated labor migration law have long been discussed, and the Prakas show what a statute could take over.","Kamboja menandatangani Konvensi Pekerja Migran PBB pada 2004; ratifikasi dan UU migrasi tenaga kerja khusus telah lama dibahas, dan Prakas menunjukkan apa yang bisa diangkat ke undang-undang."]],
    avenues:[["Complaints to the Ministry of Labour and Vocational Training under the 2013 complaint mechanism, which can lead to compensation from the agency.","Pengaduan ke Kementerian Tenaga Kerja dan Pelatihan Vokasi menurut mekanisme pengaduan 2013, yang bisa menghasilkan ganti rugi dari agensi."]]};
  G.advocacy.LA = {args:[["Most Lao workers in Thailand move outside the memorandum channel; the protections of the 2020 Decree reach only those sent through licensed enterprises.","Kebanyakan pekerja Laos di Thailand berpindah di luar jalur nota kesepahaman; perlindungan Dekret 2020 hanya menjangkau yang dikirim melalui perusahaan berizin."]],
    avenues:[["The labor attaché in Bangkok and the Thai hotlines.","Atase tenaga kerja di Bangkok dan saluran bantuan Thailand."]]};
  G.advocacy.TL = {args:[["As a party to the UN migrant workers convention since 2004, Timor-Leste reports to the Committee on Migrant Workers, which can review the protection of scheme workers abroad.","Sebagai pihak Konvensi Pekerja Migran PBB sejak 2004, Timor-Leste melapor kepada Komite Pekerja Migran, yang bisa meninjau perlindungan pekerja skema di luar negeri."]],
    avenues:[["SEFOPE and the labor attachés, and the complaint channels of the destination scheme.","SEFOPE dan atase tenaga kerja, serta saluran pengaduan skema negara tujuan."]]};

  if (G.changelog) G.changelog.unshift(["2026-11-13","1.3","Added Myanmar, Cambodia, Laos and Timor-Leste (36 cells on the nine features, all S; 7 marked unclear), with treaty status, 11 bilateral instruments, 10 laws and 7 developments, for the Southeast Asia page. Thailand and Singapore added to the bilateral matrix.","Menambahkan Myanmar, Kamboja, Laos dan Timor-Leste (36 sel pada sembilan fitur, semuanya S; 7 ditandai belum jelas), dengan status traktat, 11 instrumen bilateral, 10 hukum dan 7 perkembangan, untuk halaman Asia Tenggara. Thailand dan Singapura ditambahkan ke matriks bilateral."]);
})(window.OC);
