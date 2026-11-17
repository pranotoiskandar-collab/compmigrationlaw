# Reasoning lens for court decisions, after Ward Farnsworth, The Legal Analyst: A Toolkit for Thinking about the Law (University of Chicago Press, 2007)
# Joel P. Trachtman, The Tools of Argument: How the Best Lawyers Think, Argue, and Win (CreateSpace, 2013),
# Pierre Schlag and David Skover, Tactics of Legal Reasoning (Carolina Academic Press, 1986),
# Frederick Schauer, Thinking Like a Lawyer (Harvard University Press, 2009),
# Janet Giltrow and others (eds), Legal Meanings (De Gruyter, Foundations in Language and Law),
# Scott Brewer (ed.), Precedents, Statutes, and Analysis of Legal Concepts (Garland 1998; Routledge 2011),
# Suvi Sankari, European Court of Justice Legal Reasoning in Context (Europa Law Publishing, 2013),
# and Richard K. Neumann, Ellie Margolis and Kathryn M. Stanchi, Legal Reasoning and Legal Writing (Aspen Publishing).
# Method of tagging (rule-based text analytics over coded factors) follows the approach surveyed in Kevin D. Ashley, Artificial Intelligence and Legal Analytics (Cambridge University Press, 2017), chs 3 and 10-11.
# Each tool names a pattern of legal reasoning; the definitions are IMR's own short wording, with the book chapter for further reading.
# Coding is by rule from the argument codes and the wording of the question and holding (AI-assisted), for full entries (status S) only.
# It describes how the reasoning can be read, not a claim about the court's own vocabulary; researchers should confirm it against the judgment.
import re

TOOLS = [
 # key, label EN, label ID, chapter, definition EN, definition ID
 ("exante", "Looking ahead: future incentives", "Melihat ke depan: insentif ke depan", "Farnsworth ch. 1, Ex ante and ex post",
  "The court asks what its ruling will encourage or deter in future, for example whether denying a claim would reward employers who hire workers without papers.",
  "Pengadilan menimbang apa yang akan didorong atau dicegah putusannya di masa depan, misalnya apakah menolak gugatan justru menguntungkan majikan yang mempekerjakan pekerja tanpa dokumen."),
 ("policy", "Purpose and policy of the rule", "Tujuan dan kebijakan aturan", "Neumann, Margolis and Stanchi, Legal Reasoning and Legal Writing, on policy arguments",
  "The court reasons from what the rule is for, such as protecting workers who cannot bargain on equal terms, and asks which result serves that purpose.",
  "Pengadilan bernalar dari untuk apa aturan itu dibuat, seperti melindungi pekerja yang tidak bisa berunding secara setara, dan menimbang hasil mana yang memenuhi tujuan itu."),
 ("lca", "Least-cost avoider", "Pihak yang paling mudah mencegah", "Farnsworth ch. 5, The least cost avoider",
  "Responsibility is placed on the party best able to prevent the harm at the lowest cost, such as the recruiter, the employer or the state.",
  "Tanggung jawab dibebankan kepada pihak yang paling mampu mencegah kerugian dengan biaya terendah, seperti perekrut, majikan atau negara."),
 ("agency", "Agents and intermediaries", "Agen dan perantara", "Farnsworth ch. 9, Agency",
  "The court deals with someone acting for another, such as a recruitment agency acting for a foreign employer, and with who answers for the agent's conduct.",
  "Pengadilan menangani pihak yang bertindak untuk pihak lain, seperti agen perekrutan yang bertindak untuk majikan asing, dan siapa yang bertanggung jawab atas perbuatan agen itu."),
 ("rule", "Bright-line rule", "Aturan tegas", "Farnsworth ch. 17; Schauer ch. 2, Rules",
  "The court lays down or applies a fixed, easily checked rule, such as a time limit on detention or a category that is always covered.",
  "Pengadilan menetapkan atau menerapkan aturan yang pasti dan mudah diperiksa, seperti batas waktu penahanan atau golongan yang selalu dilindungi."),
 ("standard", "Case-by-case standard", "Ukuran kasus per kasus", "Farnsworth ch. 17, Rules and standards",
  "The court calls for an individual assessment of the facts, such as reasonableness, proportionality or a person's own circumstances, instead of a blanket rule.",
  "Pengadilan meminta penilaian fakta secara individual, seperti kewajaran, proporsionalitas atau keadaan orang itu sendiri, bukan aturan pukul rata."),
 ("slope", "Slippery slope", "Lereng licin", "Farnsworth ch. 18, Slippery slopes; Schlag and Skover pt 2 (parade of horribles)",
  "One side argues that accepting a claim would lead step by step to wider results; the court accepts or answers the argument.",
  "Salah satu pihak berargumen bahwa menerima gugatan akan berujung selangkah demi selangkah pada akibat yang lebih luas; pengadilan menerima atau menjawab argumen itu."),
 ("analogy", "Argument by analogy", "Argumen analogi", "Schlag and Skover pt 2; Schauer ch. 5, Analogies",
  "The court treats the case as like, or unlike, another situation, for example likening tied employment to servitude or migrant workers to citizen workers, and the other side may call the analogy false.",
  "Pengadilan memperlakukan perkara sebagai serupa, atau tidak serupa, dengan keadaan lain, misalnya menyamakan kerja yang terikat dengan perhambaan atau pekerja migran dengan pekerja warga negara, dan pihak lain bisa menyebut analogi itu keliru."),
 ("abstraction", "Level of generality", "Tingkat keumuman", "Schlag and Skover pt 2, Attacks on levels of abstraction",
  "The result depends on how broadly the right or the question is framed: as a general guarantee to every person, or narrowly as a claim by one group in one setting.",
  "Hasil perkara bergantung pada seberapa luas hak atau pertanyaannya dirumuskan: sebagai jaminan umum bagi setiap orang, atau secara sempit sebagai tuntutan satu kelompok dalam satu keadaan."),
 ("remedy", "Kind of remedy: stop the act or pay for it", "Jenis pemulihan: hentikan perbuatan atau bayar ganti rugi", "Farnsworth ch. 20, Property rules and liability rules",
  "The court chooses between protecting the right outright (release, reinstatement, a ban on removal) and letting it be taken against payment (damages, back pay).",
  "Pengadilan memilih antara melindungi hak secara langsung (pembebasan, pemulihan kerja, larangan pengusiran) dan membolehkan hak diambil dengan pembayaran (ganti rugi, upah tertunggak)."),
 ("baseline", "Baseline: compared with whom?", "Garis dasar: dibandingkan dengan siapa?", "Farnsworth ch. 21, Baselines",
  "The case turns on the point of comparison: whether migrant workers are measured against citizens, against other workers, or against no protection at all.",
  "Perkara bergantung pada titik pembanding: apakah pekerja migran diukur terhadap warga negara, terhadap pekerja lain, atau terhadap tiadanya perlindungan sama sekali."),
 ("procedure", "Procedure: who may decide, and when", "Prosedur: siapa yang berwenang, dan kapan", "Trachtman ch. 3, Arguing in a legal system: procedure",
  "The case turns on jurisdiction, standing, admissibility, time limits or exhaustion of remedies, rather than on the merits alone.",
  "Perkara bergantung pada kewenangan mengadili, kedudukan hukum, dapat diterimanya permohonan, tenggat waktu atau upaya hukum yang harus ditempuh lebih dulu, bukan hanya pada pokok perkara."),
 ("text", "Reading the text", "Menafsirkan teks", "Trachtman ch. 4; Giltrow and others (eds), Legal Meanings; Brewer (ed.) 1998 (Frankfurter, Llewellyn, Miller); Sankari 2013 ch. 3 (wording, scheme, spirit)",
  "The court settles what the words of a statute, constitution, treaty or contract mean, by their wording, their purpose or their place in the whole instrument, or fills a gap the text left open.",
  "Pengadilan menentukan arti kata-kata undang-undang, konstitusi, perjanjian internasional atau kontrak, menurut bunyi, tujuan atau kedudukannya dalam keseluruhan instrumen, atau mengisi celah yang dibiarkan teks."),
 ("precedent", "Following or distinguishing precedent", "Mengikuti atau membedakan preseden", "Trachtman ch. 5; Schauer ch. 3; Brewer (ed.) 1998 (Goodhart on the ratio decidendi); Sankari 2013 ch. 4 (lines of cases)",
  "The court relies on, extends, distinguishes or departs from earlier decisions, its own or those of other courts and treaty bodies.",
  "Pengadilan bersandar pada, memperluas, membedakan atau meninggalkan putusan terdahulu, baik putusannya sendiri maupun putusan pengadilan dan badan traktat lain."),
 ("authority", "Drawing on outside authority", "Bersandar pada otoritas luar", "Schauer ch. 4, Authority and authorities",
  "A national court relies on treaties, the views of treaty bodies, or judgments of foreign, regional or international courts, whether as binding law or as persuasive support.",
  "Pengadilan nasional bersandar pada perjanjian internasional, pandangan badan traktat, atau putusan pengadilan asing, kawasan atau internasional, baik sebagai hukum yang mengikat maupun sebagai dukungan yang meyakinkan."),
 ("substance", "Substance over form", "Substansi di atas bentuk", "Trachtman ch. 8, Arguing about substantive responsibility",
  "The court looks past the label or formal arrangement, such as a signed contract, a worker's apparent consent or a scheme's name, to what actually happened.",
  "Pengadilan melihat melampaui label atau susunan formal, seperti kontrak yang ditandatangani, persetujuan pekerja yang tampak atau nama suatu skema, kepada apa yang sebenarnya terjadi."),
 ("proof", "Presumptions and burden of proof", "Praduga dan beban pembuktian", "Farnsworth chs 27–28; Trachtman ch. 6, Arguing about facts",
  "The outcome depends on who must prove what, and how surely: for example the state proving that someone is a foreigner, or a presumption that a trafficked person acted under compulsion.",
  "Hasil perkara bergantung pada siapa yang harus membuktikan apa, dan seberapa pasti: misalnya negara membuktikan bahwa seseorang adalah orang asing, atau praduga bahwa korban perdagangan orang bertindak karena terpaksa."),
]
KEYS = [t[0] for t in TOOLS]

BY_ARG = {
 "status": ["exante", "baseline"], "illegality": ["exante"], "equality": ["baseline"], "statusdisc": ["baseline"],
 "excluded": ["baseline"], "exitban": ["baseline"], "noncitizen": ["baseline"], "coverage": ["rule"],
 "recruiter": ["agency", "lca"], "punish": ["exante"], "investigate": ["lca"], "wagededuct": ["exante"],
 "detreview": ["rule"], "expulsion": ["standard"], "nonrefoul": ["standard"], "family": ["standard"],
 "burden": ["proof"], "nonpunish": ["proof"], "retaliation": ["proof"], "minterms": ["rule"], "hours": ["rule"],
 "reenact": ["rule", "precedent"], "nocrim": ["rule"], "checks": ["standard"], "worktoright": ["rule"],
}
KW = [
 ("exante", r"\bdeter|incentiv|encourag\w* employers|reward\w* employers|in future"),
 ("lca", r"best placed|in the best position|duty to prevent|due diligence"),
 ("agency", r"recruit\w* agenc|placement agenc|\bagent\b|on behalf of the employer|jointly (and severally )?liable|solidar"),
 ("rule", r"time limit|maximum period|\bno more than \d|within \d+ (days|hours)|bright.line|automatic\w*"),
 ("standard", r"proportional|reasonabl|individual(ly)? (assess|examin|review|circumstances)|case.by.case|best interests"),
 ("slope", r"floodgate|slippery|open the door|would lead to|every (migrant|foreigner)"),
 ("remedy", r"compensat|damages|back pay|arrears|reinstat|released|release (him|her|them)|quash|set aside the (deportation|removal|order)"),
 ("baseline", r"same as (citizens|nationals)|like (citizens|nationals)|equal(ly)? (treatment|pay)|compared? with|other workers"),
 ("proof", r"burden|presum|\bprove|evidence|standard of proof"),
 ("policy", r"purpose of (the )?(law|act|statute|rule|scheme|provision|convention)|object of the (act|law|statute)|aim of the (act|law|statute)|public interest|public policy|protective (purpose|aim|legislation)"),
 ("analogy", r"analog|akin to|comparable to|amount\w* to (slavery|servitude|forced labou?r)|similarly situated|like citizens|like nationals"),
 ("abstraction", r"human dignity|inherent dignity|every (person|human)|all persons|anyone who|everyone|whatever their (immigration )?status"),
 ("procedure", r"jurisdiction|admissib|standing|locus standi|exhaust|time.barred|out of time|leave to appeal|\bmoot"),
 ("text", r"interpret|meaning of|the words?\b|the term\b|purpose of the (act|law|provision|statute)|read (down|in)\b|constru"),
 ("precedent", r"precedent|followed (its|the|an) (earlier|own)|earlier (decision|ruling|judgment)|overrul|distinguish|reaffirm|same reasons"),
 ("substance", r"in substance|in reality|in practice|regardless of (the )?(label|form|name)|disguis|consent|waive|voluntar"),
]

AUTH = r"international law|treaty|treaties|\bconvention\b|covenant|\bilo\b|foreign (court|judgment|law)|comparative|european court|inter-american|committee on|general comment|un (human rights )?committee"

def code(d):
    if d.get("status", "S") == "C":
        return []
    s = set()
    for a, _ in d.get("args", []):
        s.update(BY_ARG.get(a, []))
    text = " ".join([d.get("q", ""), d.get("held", ""), d.get("plain", "")]).lower()
    for k, rx in KW:
        if re.search(rx, text):
            s.add(k)
    if d.get("tier") == "national" and re.search(AUTH, text):
        s.add("authority")
    return [k for k in KEYS if k in s]
