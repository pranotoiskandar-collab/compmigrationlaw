
/* ---------- statistics: country dataset for IMRStats ---------- */
const UNREGION = (() => {
  const R = {
    Africa: "Algeria|Angola|Benin|Botswana|Burkina Faso|Burundi|Cabo Verde|Cameroon|Central African Republic|Chad|Comoros|Congo|Côte d'Ivoire|Democratic Republic of the Congo|Djibouti|Egypt|Equatorial Guinea|Eritrea|Eswatini|Ethiopia|Gabon|Gambia|Ghana|Guinea|Guinea-Bissau|Kenya|Lesotho|Liberia|Libya|Madagascar|Malawi|Mali|Mauritania|Mauritius|Morocco|Mozambique|Namibia|Niger|Nigeria|Rwanda|Sao Tome and Principe|Senegal|Seychelles|Sierra Leone|Somalia|South Africa|South Sudan|Sudan|Togo|Tunisia|Uganda|United Republic of Tanzania|Zambia|Zimbabwe",
    Americas: "Antigua and Barbuda|Argentina|Bahamas|Barbados|Belize|Bolivia|Brazil|Canada|Chile|Colombia|Costa Rica|Cuba|Dominica|Dominican Republic|Ecuador|El Salvador|Grenada|Guatemala|Guyana|Haiti|Honduras|Jamaica|Mexico|Nicaragua|Panama|Paraguay|Peru|Saint Kitts and Nevis|Saint Lucia|Saint Vincent and the Grenadines|Suriname|Trinidad and Tobago|United States of America|Uruguay|Venezuela",
    Asia: "Afghanistan|Armenia|Azerbaijan|Bahrain|Bangladesh|Cambodia|China|Cyprus|Democratic People's Republic of Korea|Georgia|India|Indonesia|Iran|Iraq|Israel|Japan|Jordan|Kazakhstan|Kuwait|Kyrgyzstan|Lao People's Democratic Republic|Lebanon|Malaysia|Maldives|Mongolia|Myanmar|Nepal|Oman|Pakistan|Philippines|Qatar|Republic of Korea|Saudi Arabia|Singapore|Sri Lanka|State of Palestine|Syrian Arab Republic|Tajikistan|Thailand|Timor-Leste|Türkiye|Turkmenistan|United Arab Emirates|Uzbekistan|Viet Nam|Yemen",
    Europe: "Albania|Andorra|Austria|Belarus|Belgium|Bosnia and Herzegovina|Bulgaria|Croatia|Czechia|Denmark|Estonia|Finland|France|Germany|Greece|Hungary|Iceland|Ireland|Italy|Latvia|Liechtenstein|Lithuania|Luxembourg|Malta|Monaco|Montenegro|Netherlands|North Macedonia|Norway|Poland|Portugal|Republic of Moldova|Romania|Russian Federation|San Marino|Serbia|Slovakia|Slovenia|Spain|Sweden|Switzerland|Ukraine|United Kingdom",
    Oceania: "Australia|Cook Islands|Fiji|Marshall Islands|New Zealand|Palau|Papua New Guinea|Samoa|Solomon Islands"
  };
  const o = {}; for (const k in R) R[k].split("|").forEach(c => o[c] = k); return o;
})();
const ASEAN10 = ["Brunei Darussalam","Cambodia","Indonesia","Lao People's Democratic Republic","Malaysia","Myanmar","Philippines","Singapore","Thailand","Viet Nam"];
const GCC6 = ["Bahrain","Kuwait","Oman","Qatar","Saudi Arabia","United Arab Emirates"];
const OECD38 = ["Australia","Austria","Belgium","Canada","Chile","Colombia","Costa Rica","Czechia","Denmark","Estonia","Finland","France","Germany","Greece","Hungary","Iceland","Ireland","Israel","Italy","Japan","Republic of Korea","Latvia","Lithuania","Luxembourg","Mexico","Netherlands","New Zealand","Norway","Poland","Portugal","Slovakia","Slovenia","Spain","Sweden","Switzerland","Türkiye","United Kingdom","United States of America"];
const STAT_ASOF = 2026.83;
const ADOPTED = k => +INAME[k].match(/(\d{4})$/)[1];
function survCfg(farm){
  const order = farm ? FARM.concat(REL) : ["ICRMW","C190","C181","P29","ICESCR"].concat(FARM, ["C169","C170"]);
  return { asOf: "October 2026", events: order.map(k => ({ key:k, adopted:ADOPTED(k), label:`${k}: ${INAME[k]}`, label_id:`${k}: ${INAME[k]}` })) };
}
const INCOME_ORDER = ["High income","Upper middle income","Lower middle income","Low income"];
const INCOME_ID = {"High income":"Pendapatan tinggi","Upper middle income":"Pendapatan menengah atas","Lower middle income":"Pendapatan menengah bawah","Low income":"Pendapatan rendah"};
const REGION_ID = {Africa:"Afrika",Americas:"Amerika",Asia:"Asia",Europe:"Eropa",Oceania:"Oseania"};
function implShare(c){ const rs=(IMPL[c]?.rows||[]).filter(r=>"FPG".includes(r[3])); if(rs.length<3) return null; return 100*rs.reduce((s,r)=>s+(r[3]==="F"?1:r[3]==="P"?.5:0),0)/rs.length; }
function statRows(){
  return C.map(d => {
    const cv = COV[d.c] || {}, r = {id:d.c, region:UNREGION[d.c]||null, sc:d.sc, br:d.br, en:d.en, n:d.n, nf:d.nf,
      eu:EU27.includes(d.c), asean:ASEAN10.includes(d.c), gcc:GCC6.includes(d.c), oecd:OECD38.includes(d.c), impl:implShare(d.c)};
    BASKET.forEach(k => { const s=d.cells[k]; r["p_"+k] = !!(s && "FPW".includes(s[1]));
      // time to ratification: years from adoption to ratification, or to the data date if not (yet) ratified
      const ev = !!(s && "FPWD".includes(s[1]) && s[2]!=null);
      r["e_"+k] = ev; r["t_"+k] = ev ? Math.max(0, +s[2]) : Math.max(0.01, STAT_ASOF - ADOPTED(k)); });
    ["income","gdppc","remit_gdp","migstock","agri_emp","rule_of_law","pop","ceacr"].forEach(k => { if (cv[k]!=null && cv[k]!=="") r[k]=cv[k]; });
    return r;
  });
}
function statVars(){
  const v = [
    {key:"sc",type:"num",label:"Ratification score (0–100)",label_id:"Skor ratifikasi (0–100)",src:"IMR, from NORMLEX and UN Treaty Collection"},
    {key:"br",type:"num",label:"Breadth of ratification (0–100)",label_id:"Keluasan ratifikasi (0–100)",src:"IMR"},
    {key:"en",type:"num",label:"Enthusiasm: speed and uptake (0–100)",label_id:"Antusiasme: kecepatan dan cakupan (0–100)",src:"IMR"},
    {key:"n",type:"num",label:"Instruments ratified (of 13)",label_id:"Instrumen yang diratifikasi (dari 13)",src:"IMR"},
    {key:"nf",type:"num",label:"Farm-specific conventions ratified (of 6)",label_id:"Konvensi khusus pertanian yang diratifikasi (dari 6)",src:"IMR"},
    {key:"impl",type:"num",label:"Domestic implementation (% of assessed obligations)",label_id:"Implementasi domestik (% kewajiban yang dinilai)",src:"IMR implementation assessment"},
    {key:"gdppc",type:"num",log:true,label:"GDP per person (US$)",label_id:"PDB per kapita (US$)",src:"World Bank NY.GDP.PCAP.CD"},
    {key:"remit_gdp",type:"num",label:"Remittances received (% of GDP)",label_id:"Remitansi yang diterima (% PDB)",src:"World Bank BX.TRF.PWKR.DT.GD.ZS"},
    {key:"migstock",type:"num",label:"International migrants (% of population)",label_id:"Migran internasional (% penduduk)",src:"World Bank SM.POP.TOTL.ZS"},
    {key:"agri_emp",type:"num",label:"Employment in agriculture (% of jobs)",label_id:"Pekerjaan di pertanian (% lapangan kerja)",src:"World Bank SL.AGR.EMPL.ZS"},
    {key:"rule_of_law",type:"num",label:"Rule of law (World Bank estimate, −2.5 to 2.5)",label_id:"Supremasi hukum (estimasi Bank Dunia, −2,5 sampai 2,5)",src:"World Bank WGI RL.EST"},
    {key:"pop",type:"num",log:true,label:"Population",label_id:"Jumlah penduduk",src:"World Bank SP.POP.TOTL"},
    {key:"ceacr",type:"num",label:"ILO expert comments since 2010 (key conventions)",label_id:"Komentar ahli ILO sejak 2010 (konvensi utama)",src:"NORMLEX, CEACR observations and direct requests"},
    {key:"region",type:"cat",label:"Region (UN)",label_id:"Kawasan (PBB)",cats_id:REGION_ID,order:["Africa","Americas","Asia","Europe","Oceania"],src:"UN M49"},
    {key:"income",type:"cat",label:"Income group (World Bank)",label_id:"Kelompok pendapatan (Bank Dunia)",cats_id:INCOME_ID,order:INCOME_ORDER,src:"World Bank"},
    {key:"eu",type:"bin",label:"EU member",label_id:"Anggota Uni Eropa",yes:"EU members",yes_id:"Anggota UE",no:"Other countries",no_id:"Negara lain"},
    {key:"asean",type:"bin",label:"ASEAN member",label_id:"Anggota ASEAN",yes:"ASEAN members",yes_id:"Anggota ASEAN",no:"Other countries",no_id:"Negara lain"},
    {key:"gcc",type:"bin",label:"Gulf Cooperation Council member",label_id:"Anggota Dewan Kerja Sama Teluk",yes:"Gulf states (GCC)",yes_id:"Negara Teluk (GCC)",no:"Other countries",no_id:"Negara lain"},
    {key:"oecd",type:"bin",label:"OECD member",label_id:"Anggota OECD",yes:"OECD members",yes_id:"Anggota OECD",no:"Other countries",no_id:"Negara lain"}
  ];
  BASKET.forEach(k => v.push({key:"p_"+k,type:"bin",label:`Party to ${k} (${INAME[k].replace(/, \d{4}$/,"")})`,label_id:`Pihak pada ${k} (${INAME[k].replace(/, \d{4}$/,"")})`,
    yes:`Parties to ${k}`,yes_id:`Negara pihak ${k}`,phrase:`are party to ${k}`,phrase1:`is party to ${k}`,phrase_id:`menjadi pihak pada ${k}`,no:`Non-parties to ${k}`,no_id:`Bukan pihak ${k}`,src:"NORMLEX / UN Treaty Collection"}));
  return v;
}
const STAT_PRESETS = {
  mig: [
    {q:"Do high-income countries ratify more?",q_id:"Apakah negara berpendapatan tinggi lebih banyak meratifikasi?",mode:0,y:"sc",g:"income"},
    {q:"Ratification score by region",q_id:"Skor ratifikasi menurut kawasan",mode:0,y:"sc",g:"region"},
    {q:"Are remittance-dependent countries more likely to join the Migrant Workers Convention?",q_id:"Apakah negara yang bergantung pada remitansi lebih mungkin menjadi pihak Konvensi Pekerja Migran?",mode:1,x:"remit_gdp",y2:"p_ICRMW"},
    {q:"Do countries hosting more migrants stay out of the Migrant Workers Convention?",q_id:"Apakah negara dengan banyak migran menjauhi Konvensi Pekerja Migran?",mode:1,x:"migstock",y2:"p_ICRMW"},
    {q:"Gulf states and the Migrant Workers Convention",q_id:"Negara Teluk dan Konvensi Pekerja Migran",mode:0,y:"p_ICRMW",g:"gcc"},
    {q:"What predicts ratification once income is held constant?",q_id:"Apa yang memprediksi ratifikasi bila pendapatan dikendalikan?",mode:2,ry:"sc",preds:["gdppc","migstock","remit_gdp","region"]},
    {q:"Do ILO experts comment more on countries that ratify more?",q_id:"Apakah ahli ILO lebih banyak berkomentar pada negara yang lebih banyak meratifikasi?",mode:1,x:"n",y2:"ceacr"},
    {q:"Is implementation better where more instruments are ratified?",q_id:"Apakah implementasi lebih baik di negara yang meratifikasi lebih banyak instrumen?",mode:1,x:"n",y2:"impl"},
    {q:"How fast do regions join the Migrant Workers Convention?",q_id:"Seberapa cepat tiap kawasan bergabung dengan Konvensi Pekerja Migran?",mode:3,ev:"ICRMW",sg:"region"},
    {q:"Do richer countries ratify the Violence and Harassment Convention faster?",q_id:"Apakah negara yang lebih kaya lebih cepat meratifikasi Konvensi Kekerasan dan Pelecehan?",mode:3,ev:"C190",sg:"income"}
  ],
  farm: [
    {q:"Do countries with more farm jobs ratify more farm conventions?",q_id:"Apakah negara dengan lebih banyak pekerjaan pertanian meratifikasi lebih banyak konvensi pertanian?",mode:1,x:"agri_emp",y2:"nf"},
    {q:"Is ratifying Labour Inspection (Agriculture) linked to income?",q_id:"Apakah ratifikasi Inspeksi Ketenagakerjaan (Pertanian) terkait pendapatan?",mode:0,y:"p_C129",g:"income"},
    {q:"Farm conventions ratified, by region",q_id:"Konvensi pertanian yang diratifikasi, menurut kawasan",mode:0,y:"nf",g:"region"},
    {q:"Are EU members more likely to ratify Safety and Health in Agriculture (C184)?",q_id:"Apakah anggota UE lebih mungkin meratifikasi K3 di Pertanian (C184)?",mode:0,y:"p_C184",g:"eu"},
    {q:"Does joining C184 go with a stronger rule of law?",q_id:"Apakah menjadi pihak C184 sejalan dengan supremasi hukum yang lebih kuat?",mode:0,y:"rule_of_law",g:"p_C184"},
    {q:"What predicts farm ratifications?",q_id:"Apa yang memprediksi ratifikasi konvensi pertanian?",mode:2,ry:"nf",preds:["agri_emp","gdppc","rule_of_law","region"]},
    {q:"How fast do regions ratify Safety and Health in Agriculture (C184)?",q_id:"Seberapa cepat tiap kawasan meratifikasi K3 di Pertanian (C184)?",mode:3,ev:"C184",sg:"region"},
    {q:"Did EU members ratify Labour Inspection (Agriculture) faster?",q_id:"Apakah anggota UE lebih cepat meratifikasi Inspeksi Ketenagakerjaan (Pertanian)?",mode:3,ev:"C129",sg:"eu"},
    {q:"Is implementation better where more instruments are ratified?",q_id:"Apakah implementasi lebih baik di negara yang meratifikasi lebih banyak instrumen?",mode:1,x:"n",y2:"impl"}
  ]
};
let STAT_LENS = null;
function drawStats(){
  if (STAT_LENS === LENS || !window.IMRStats) return;
  STAT_LENS = LENS;
  const farm = LENS === "farm";
  IMRStats.mount($("#statsout"), {
    rows: statRows(), vars: statVars(), surv: survCfg(farm), presets: STAT_PRESETS[LENS] || STAT_PRESETS.mig, idLabel: "country", save,
    filename: PFX(), defaults: farm ? {y:"nf", g:"region", x:"agri_emp", y2:"nf", preds:["agri_emp","gdppc","region"]} : {y:"sc", g:"region", x:"gdppc", y2:"sc", preds:["gdppc","migstock","region"]},
    note: `Ratification data: NORMLEX and UN Treaty Collection, collected October 2026.${Object.keys(COV).length ? " Country indicators: World Bank WDI and Worldwide Governance Indicators (latest year available), collected " + (COV.__date || "October 2026") + "." : ""} Regions follow the UN M49 standard.`,
    note_id: `Data ratifikasi: NORMLEX dan UN Treaty Collection, dikumpulkan Oktober 2026.${Object.keys(COV).length ? " Indikator negara: WDI dan Worldwide Governance Indicators Bank Dunia (tahun terbaru), dikumpulkan " + (COV.__date ? COV.__date.replace("October","Oktober") : "Oktober 2026") + "." : ""} Kawasan mengikuti standar M49 PBB.`
  });
}
