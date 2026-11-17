import re,json
R='/mnt/project-files/theimr-site/'
src=open(R+'countries-of-origin/index.html',encoding='utf-8').read()
style=src[src.index('<style>'):src.index('</style>')+8]
header=src[src.index('<header'):src.index('</header>')+9]
header=header.replace(' aria-current="page"','')
header=header.replace('<a href="/court-decisions/">Migration Jurisprudence from the South</a>','<a href="/court-decisions/" aria-current="page">Migration Jurisprudence from the South</a>') if '/court-decisions/' in header else header.replace('<a href="/hate-speech-voting/">Hate Speech and Voting</a>','<a href="/hate-speech-voting/">Hate Speech and Voting</a>\n<a href="/court-decisions/" aria-current="page">Migration Jurisprudence from the South</a>')
ridge=src[src.index('<div class="imr-ridge"'):src.index('</footer>')+9]
desc="Court decisions on migrant workers from national, regional and international courts, led by Asia, Africa, the Middle East and Latin America: what was decided, the argument that decided it, what happened afterwards, plain-language summaries in English and Indonesian, and downloadable coded data."
ld={"@context":"https://schema.org","@type":"Dataset","name":"Migration Jurisprudence from the South","description":desc,"url":"https://theimr.org/court-decisions/","version":"0.1","dateModified":"2026-11-01","creator":{"@type":"Organization","name":"Institute for Migrant Rights","url":"https://theimr.org/"},"inLanguage":["en","id"],"isAccessibleForFree":True,
 "distribution":[{"@type":"DataDownload","encodingFormat":"text/csv","contentUrl":"https://theimr.org/court-decisions/data/"+f} for f in ["decisions.csv","arguments.csv","argument-codes.csv","timeline.csv","codebook.csv","sources.csv"]],
 "variableMeasured":["tier of court","type of case","forum","outcome","follow-up after judgment","arguments accepted or rejected","stage of migration"]}
cap='<figure class="imr-band" style="margin:0;position:relative;line-height:0;background:#DCE8E1"><img src="/images/cianjur-old/cianjur-railway-station.jpg" alt="" loading="lazy" decoding="async" width="2000" height="500" style="display:block;width:100%;height:clamp(84px,11vw,160px);object-fit:cover"><figcaption style="position:absolute;right:12px;bottom:8px;max-width:calc(100% - 24px);box-sizing:border-box;padding:3px 7px;border-radius:3px;background:rgba(23,45,36,.62);text-align:right;font:400 10.5px/1.45 \'JetBrains Mono\',monospace;letter-spacing:.05em;text-transform:uppercase;color:#EEF4F0"><span>Railway line at Cianjur station, c. 1890</span> · <a href="https://commons.wikimedia.org/wiki/File:Station_te_Tjiandjoer,_KITLV_40312.tiff" rel="noopener" style="color:#EEF4F0;text-decoration:underline;text-underline-offset:2px">KITLV, CC BY 4.0</a></figcaption></figure>'
extra_css='''<style>
.cd-srcg{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:8px 28px;margin-top:14px}.cd-src{list-style:none;padding:0;margin:0}.cd-src li{padding:6px 0;border-bottom:1px solid #DCE8E1;line-height:1.4}.cd-srcby{display:block;font-size:14px;color:#3D5A4D}.cd-srcn{font-family:'JetBrains Mono',monospace;font-size:13px;color:#3D5A4D}
.cd-views{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px;margin:28px 0 0}
.cd-vbtn{all:unset;box-sizing:border-box;cursor:pointer;display:flex;flex-direction:column;gap:4px;padding:14px 18px;min-height:64px;border:2px solid #B2C7BC;background:#FFFFFF;color:#172D24}
.cd-vbtn b{font-size:18px;font-weight:600}.cd-vbtn span{font-size:15px;color:#3D5A4D;line-height:1.4}
.cd-vbtn[aria-pressed="true"]{background:#1E6B4A;border-color:#1E6B4A;color:#FFFFFF}.cd-vbtn[aria-pressed="true"] span{color:#DCE8E1}
.cd-vbtn:focus-visible,.cd-chip:focus-visible,.cd-stage:focus-visible,.cd-link:focus-visible{outline:2px solid #172D24;outline-offset:2px}
.cd-frow{display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;margin:14px 0 0}
.cd-frow .g-btns{margin:0}.cd-flab{font-family:'JetBrains Mono',monospace;font-size:12.5px;color:#3D5A4D;min-width:150px;margin:0}
.cd-vh{margin:30px 0 6px;font-size:28px;font-weight:500!important}.cd-vh3{margin:26px 0 10px;font-size:22px;font-weight:600}
.cd-sel{font:inherit;font-size:16px;min-height:44px;padding:0 10px;border:1px solid #B2C7BC;background:#FFFFFF;color:#172D24;max-width:100%}
.cd-pick{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;margin:10px 0 18px}
.cd-cmp th[scope="row"]{font-weight:600;min-width:180px}.cd-cmp td,.cd-cmp th{vertical-align:top}.cd-cmp .cd-n{font-size:13px;color:#3D5A4D}
.cd-side td{min-width:220px}
.cd-test{border-left:4px solid #1E6B4A;background:#F6FAF7;padding:12px 16px;margin:12px 0}.cd-test p{margin:4px 0}
.cd-dhead .g-btns{display:flex;flex-wrap:wrap;gap:8px}
.cd-frow select{margin-top:4px}
.cd-chips{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 22px}
.cd-chip{font:inherit;font-size:16px;min-height:44px;padding:0 16px;border-radius:999px;border:1px solid #B2C7BC;background:#F6FAF7;color:#172D24;cursor:pointer}
.cd-chip[aria-pressed="true"]{background:#1E6B4A;border-color:#1E6B4A;color:#FFFFFF}
.cd-rows{border-top:1px solid #B2C7BC}
.cd-row{border-bottom:1px solid #B2C7BC;background:#FFFFFF}
.cd-row>summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:1fr auto;gap:2px 16px;align-items:center;padding:12px 16px 12px 40px;position:relative;min-height:44px}
.cd-row>summary::-webkit-details-marker{display:none}
.cd-row>summary::before{content:"+";position:absolute;left:14px;top:12px;font:600 18px/1.3 'JetBrains Mono',monospace;color:#1E6B4A}
.cd-row[open]>summary::before{content:"\2212"}
.cd-row>summary:hover{background:#F3F7F4}.cd-row>summary:focus-visible{outline:2px solid #172D24;outline-offset:-2px}
.cd-rn{font-size:17px;font-weight:600;line-height:1.35;color:#172D24}
.cd-rm{grid-column:1;font-family:'JetBrains Mono',monospace;font-size:12.5px;color:#3D5A4D;letter-spacing:.02em}
.cd-rp{grid-column:2;grid-row:1/span 2}
.cd-rb{padding:4px 16px 18px 40px;display:flex;flex-direction:column;gap:8px;font-size:16px;line-height:1.55;max-width:860px}.cd-rb p{margin:0}
.cd-row.cd-cand{background:#FBFCFA}.cd-row.cd-cand .cd-rn{font-weight:500}
.cd-srcl{margin:0;padding-left:18px}.cd-ract{display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.cd-refs{margin-top:22px}.cd-refs>summary{cursor:pointer;font-weight:600;min-height:44px;display:flex;align-items:center}
.cd-x>summary{cursor:pointer;color:#1E6B4A;text-decoration:underline;text-underline-offset:3px}.cd-xl{margin:8px 0 0;padding-left:16px;font-family:inherit;font-size:14px;text-align:left;min-width:220px}.cd-xl li{margin:3px 0}
.cd-about{margin:18px 0 0;max-width:820px}.cd-about>summary{cursor:pointer;font-weight:600;min-height:44px;display:flex;align-items:center}
@media (max-width:760px){.cd-row>summary{grid-template-columns:1fr}.cd-rp{grid-column:1;grid-row:auto}.cd-rb{padding-left:16px}}
.cd-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
.cd-card{background:#FFFFFF;border:1px solid #B2C7BC;padding:18px 20px;display:flex;flex-direction:column;gap:6px;font-size:16px;line-height:1.55}
.cd-card h3{margin:0;font-size:20px;line-height:1.3;font-weight:600}.cd-card h3 a{color:#172D24}.cd-card p{margin:0}
.cd-meta{margin:0;font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:#3D5A4D}
.cd-court{margin:0;font-size:15px;color:#2E493D}
.cd-pills{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 0!important}
.cd-pill{display:inline-block;padding:3px 9px;font-size:13.5px;border:1px solid #B2C7BC;background:#F6FAF7;color:#172D24}
.cd-pill.o-won{background:#DCE8E1;border-color:#9CC9B2;color:#134A33}.cd-pill.o-lost{background:#FFFFFF;border-style:dashed;color:#2E493D}.cd-pill.o-advisory{background:#E8F2EC}
.cd-pill.s-S{border-style:dashed;color:#3D5A4D;background:#FFFFFF}
.cd-pill.s-C{border:1px dashed #8A5A00;color:#6B4600;background:#FFF7D6}
a.cd-pill{text-decoration:none}a.cd-pill:hover{text-decoration:underline;text-underline-offset:3px}
.cd-card.cd-cand{border-style:dashed;background:#FBFCFA}.cd-card.cd-cand h3 a{font-weight:500}
.cd-empty{padding:18px;background:#EEF4F0;border:1px dashed #6F8A7D}.cd-empty p{margin:0 0 6px}
.cd-stages{list-style:none;margin:16px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}
.cd-stage{all:unset;box-sizing:border-box;cursor:pointer;width:100%;height:100%;display:flex;flex-direction:column;gap:6px;padding:14px 16px;border:2px solid #B2C7BC;background:#FFFFFF;color:#172D24;font-size:15px;line-height:1.4}
.cd-stage b{font-size:17px;font-weight:600}.cd-stage .cd-sd{color:#3D5A4D}.cd-stage .cd-sn{font-family:'JetBrains Mono',monospace;font-size:12.5px;color:#2E493D}
.cd-stage[aria-pressed="true"]{background:#1E6B4A;border-color:#1E6B4A;color:#FFFFFF}.cd-stage[aria-pressed="true"] .cd-sd,.cd-stage[aria-pressed="true"] .cd-sn,.cd-stage[aria-pressed="true"] .g-mono{color:#DCE8E1}
.cd-at{min-width:760px}.cd-bar{display:inline-block;vertical-align:middle;width:110px;height:10px;background:#DCE8E1;margin-right:8px;position:relative}.cd-bar span{position:absolute;left:0;top:0;bottom:0;background:#1E6B4A}
.cd-link{font:inherit;font-size:15px;min-height:40px;padding:0 12px;background:transparent;border:1px solid #172D24;color:#172D24;cursor:pointer}
tr.cd-sub td{background:#F6FAF7}tr.cd-sub ul{margin:4px 0 10px;padding-left:20px;font-size:15px}
#cd-detail{margin-top:40px;padding:26px 24px;background:#FFFFFF;border:2px solid #172D24;scroll-margin-top:12px}
#cd-detail h2{margin:8px 0 4px;font-size:32px;line-height:1.2;font-weight:500!important}
.cd-dhead{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px}
.cd-plain{margin:18px 0;padding:16px 18px;background:#DCE8E1}.cd-plain h3{margin:0 0 6px;font-size:17px;font-weight:600}.cd-plain p{margin:0}
.cd-coded{margin:18px 0}.cd-coded summary{cursor:pointer;font-weight:600;min-height:40px;display:flex;align-items:center}
.cd-warn{margin:18px 0 0;max-width:820px;padding:14px 18px;background:#FFFFFF;border:2px dashed #172D24;font-size:17px;line-height:1.6}.cd-warn p{margin:0}.cd-warn b{font-weight:700}
.cd-focus{margin:18px 0 0;max-width:820px;padding:14px 18px;background:#DCE8E1;border-left:0;font-size:17px;line-height:1.6}.cd-focus b{font-weight:600}
.cd-grp{margin:28px 0 4px;font-family:'JetBrains Mono',monospace;font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;color:#3D5A4D}
.cd-pill.ref{border-style:dashed;background:#FFFFFF;color:#3D5A4D}
.cd-sw{display:inline-block;width:12px;height:12px;border:1px solid #172D24;margin-right:6px;vertical-align:-1px}
@media (max-width:760px){.cd-flab{min-width:0;width:100%}.cd-list{grid-template-columns:1fr}#cd-detail{padding:20px 16px}}
</style>'''
import os
_S=json.load(open(os.path.dirname(os.path.abspath(__file__))+'/sources.json'))
def _li(x):
    name,by,site,kind,n,home=x
    lab=name if name!=site else site
    who=(' <span class="cd-srcby">'+by+'</span>') if by and by!=name else ''
    return '<li><a href="'+home+'" rel="noopener">'+lab+'</a>'+who+' <span class="cd-srcn">'+str(n)+'</span></li>'
def _grp(k): return ''.join(_li(x) for x in _S if x[3]==k)
_NO=sum(x[4] for x in _S)
SRC=f'''<section class="g-sec" id="sources">
<p class="g-eye">SOURCES</p>
<h2>Where the decisions come from</h2>
<p>Every decision page lists its sources under “Sources” or “Where to check”, with a direct link to the judgment wherever a public copy exists. Where a court does not publish judgments, the entry rests on a report and says “as reported”. The number after each source is how many decisions link to it. The full list is in <a href="data/sources.csv">sources.csv</a>, and each decision’s links are in the “sources” column of decisions.csv. Every decision also has its own page; see the <a href="/court-decisions/d/">list of all decisions</a>.</p>
<details class="cd-about"><summary>Show all sources</summary><div class="cd-srcg">
<div><h3 class="g-h4">Courts, treaty bodies and other official sites</h3><ul class="cd-src">{_grp('official')}</ul></div>
<div><h3 class="g-h4">Free legal information databases</h3><ul class="cd-src">{_grp('legaldb')}</ul></div>
<div><h3 class="g-h4">Reports and news (used where the judgment is not published)</h3><ul class="cd-src">{_grp('report')}</ul></div>
</div></details>
<p class="g-note">Some links open a search on the database rather than the judgment itself; they are labelled “(search)”. Links built from a case citation are being checked one by one.</p>
</section>
'''
body=f'''<main style="padding: 64px 0 88px" id="court-decisions">
<div class="g-wrap">
<p class="g-eye">MIGRATION AND LABOR LAWS IN COMPARISON</p>
<h1 class="g-h1">Migration Jurisprudence from the South</h1>
<p class="g-lede">What courts have decided about migrant workers, and whether it held. Each decision comes with the question, what the court decided, the arguments it accepted or rejected, what happened afterwards, and a plain-language summary in English and Indonesian.</p>

<div class="cd-warn" role="note"><p><b>Work in progress: please read with care.</b> This collection is still being built and checked. Most summaries were prepared from the courts' own summaries, law reports and news coverage, and have not yet been checked line by line against the judgments. Some dates, case numbers and outcomes may be incomplete or wrong; details still to confirm are shown in [square brackets]. Entries marked “Unchecked candidate” are leads for researchers only: they have no summary yet and may contain errors. Do not rely on this page for a case of your own: read the judgment itself, or ask the <a href="/legal-clinic/">Legal Clinic</a>.</p></div>
<details class="cd-about"><summary>About this collection: focus and comparators</summary><p class="cd-focus"><b>Focus: jurisprudence beyond Europe and North America.</b> Most collections of migration case law are built around European and United States courts. This one starts from courts in Asia, Africa, the Middle East, Latin America and the Pacific, including courts in countries of origin and the Inter-American and African systems. Decisions of the European Court of Human Rights, and a few from other European and United States courts, are kept, clearly marked, as points of comparison; each decision page names its closest European Court comparator.</p></details>
<div class="cd-views" id="cd-views" role="group" aria-label="Ways to explore the decisions">
<button type="button" class="cd-vbtn" data-view="situation" aria-pressed="true"><b>By situation</b><span>Start from what happened</span></button>
<button type="button" class="cd-vbtn" data-view="argument" aria-pressed="false"><b>By argument</b><span>Which arguments persuade courts</span></button>
<button type="button" class="cd-vbtn" data-view="journey" aria-pressed="false"><b>Along the journey</b><span>From recruitment to return</span></button>
<button type="button" class="cd-vbtn" data-view="compare" aria-pressed="false"><b>Compare</b><span>Groups side by side, with statistical tests</span></button>
</div>
<div id="cd-filters" data-noi18n></div>
<p class="g-mono" id="cd-count" style="margin:14px 0 0" data-noi18n></p>
<div id="cd-view" data-noi18n></div>
<section id="cd-detail" hidden aria-labelledby="cd-dtitle" data-noi18n></section>

<section class="g-sec" id="after">
<p class="g-eye">AFTER THE JUDGMENT</p>
<h2>Was the decision carried out?</h2>
<p class="g-lead">A judgment is only a beginning. Each entry records what followed: a law changed, a remedy paid, a ruling undone by a new law, or nothing. The bar counts the decisions shown above. It describes this collection only and does not rank countries.</p>
<div id="cd-sum" data-noi18n></div>
</section>

<section class="g-sec" id="method">
<p class="g-eye">METHOD</p>
<h2>How decisions are chosen and coded</h2>
<p class="imr-ai-note" style="margin:0 0 20px;max-width:820px;font-size:16px;line-height:1.55;color:#2E493D"><b>Use of AI:</b> AI is used to re-confirm that none of the data we use infringes intellectual property law, to test our labels and to edit summaries into plain language, which people then re-edit. Summaries pre-written by AI are marked “unverified”. <a href="/ai-use/">How we use AI</a></p>
<p class="g-lead">This is version 0.1, a first set of decisions. The collection deliberately centres jurisprudence from outside Europe and North America: courts in Asia, Africa, the Middle East and Latin America, the Inter-American Court, and global bodies. European and United States decisions appear only as comparison points, listed after the others and marked "Comparison". We chose well-documented decisions that turn on the rights of migrant workers and their families. Each decision is coded for the level of the court (national, regional or international), for whether a national court sits in the destination country or the country of origin, and for outcome, arguments, stage of migration and follow-up.</p>
<ul style="max-width:820px">
<li>Every entry is marked S for now. Its summary was prepared from the court's own summaries and from secondary sources. It is being checked line by line against the judgment, and an entry changes to P once that check is done. Details still to be confirmed appear in square brackets.</li>
<li>Type of case: criminal (a prosecution), private (a dispute between private parties, such as a wage claim against an employer or agency), administrative (a challenge to an agency decision on ordinary legal grounds), or constitutional and human rights (constitutional review, fundamental-rights petitions, and complaints to regional and international bodies). Each decision has one type, coded from the court, the parties and the arguments.</li>
<li>Outcome is coded from the side of the worker or migrant. "Worker side won" means the court accepted the main claim made for them.</li>
<li>Counts of accepted arguments describe this collection, not litigation as a whole. Courts and claimants choose which cases are brought and reported, so these counts are not success rates.</li>
<li>Gulf states and parts of South Asia: few judgments are published in full, so some entries rest on news reports of the decision and say so. They will be checked against official texts where these exist.</li>
</ul>
<div id="cd-reasoning" data-noi18n></div>
<details class="g-adv"><summary style="cursor:pointer;font-weight:600;min-height:44px;display:flex;align-items:center">Codebook</summary>
<div class="g-scroll" style="margin-top:10px"><table class="g-t" id="cd-codebook" data-noi18n></table></div></details>
</section>

{SRC}
<section class="g-sec" id="downloads">
<p class="g-eye">DATA</p>
<h2>Downloads and citation</h2>
<div class="g-btns" id="cd-dls" data-noi18n></div>
<p class="g-note">Cite as: Institute for Migrant Rights (2026), Migration Jurisprudence from the South, version 0.1, https://theimr.org/court-decisions/. The summaries are ours and the judgments belong to their courts. Links point to official or public copies.</p>
<p class="g-note">This page summarizes court decisions for research and advocacy. It is not legal advice. If you know a decision that should be here, or you find a mistake, write to <a href="mailto:secretariat@theimr.org">secretariat@theimr.org</a>.</p>
<div class="g-acts"><a href="/legal-clinic/">Open the Legal Clinic</a><a href="/legal-help/">Find free legal help</a></div>
</section>
</div>
</main>'''
head=f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Migration Jurisprudence from the South · Institute for Migrant Rights</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&amp;family=JetBrains+Mono:wght@400;500&amp;display=swap">
<link rel="canonical" href="https://theimr.org/court-decisions/">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Institute for Migrant Rights">
<meta property="og:title" content="Migration Jurisprudence from the South · Institute for Migrant Rights">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://theimr.org/court-decisions/">
<meta property="og:image" content="https://theimr.org/images/rice-fields-cianjur-1975.jpg">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
<meta name="twitter:card" content="summary_large_image">
{style}
{extra_css}
<link rel="stylesheet" href="/assets/notebook.css">
</head>
<body>
<div style="background: #E5EEE8; color: #172D24; font-family: 'Familjen Grotesk', system-ui, sans-serif; font-size: 19px; line-height: 1.65">
{header}
{cap}
'''
tail=f'''
{ridge}
</div>
<script>
document.addEventListener('click', function (e) {{
  document.querySelectorAll('.nav details[open]').forEach(function (d) {{ if (!d.contains(e.target)) d.removeAttribute('open'); }});
}});
</script>
<script src="cd-data.js" defer></script>
<script src="cd.js" defer></script>
<script src="cd-i18n.js" defer></script>
<script src="/assets/lang.js" defer></script>
</body>
</html>
'''
open(R+'court-decisions/index.html','w',encoding='utf-8').write(head+body+tail)
print('ok')
