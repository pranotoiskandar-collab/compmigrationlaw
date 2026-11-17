# Builds /hate-speech-voting/index.html from the Countries of Origin page shell. Usage: python3 build_page.py SITE_ROOT OUT_HTML
import re, json, sys, os
site, out = sys.argv[1], sys.argv[2]
src = open(site + "/countries-of-origin/index.html").read()
main = open(os.path.join(os.path.dirname(__file__), "main.html")).read()
NAMES = ["United States","Canada","United Kingdom","Ireland","France","Germany","Netherlands","Belgium","Austria","Switzerland","Sweden","Denmark","Italy","Spain","Portugal","Greece","Australia","New Zealand","Japan","South Korea","Taiwan","India","Indonesia","Malaysia","Philippines","Sri Lanka","South Africa","Ghana","Kenya","Brazil","Argentina","Chile","Mexico","Colombia"]
desc = "How party hate speech relates to votes for anti-immigration parties in 34 constitutional democracies, Western and non-Western, and whether countries whose law explicitly protects non-citizens differ from those relying on general guarantees: a codebook, sourced legal codings, V-Dem and V-Party data, downloads and tools to test associations."
title = "Hate speech, voting and non-citizens · Institute for Migrant Rights"
U = "https://theimr.org/hate-speech-voting/"
ld = {"@context":"https://schema.org","@type":"Dataset","name":"Hate speech, voting and the legal protection of non-citizens","alternateName":"IMR hate speech and voting comparative dataset",
 "description":"Comparative data on 34 constitutional democracies: four de jure features of domestic law (constitutional equality guarantee, anti-discrimination statute, hate speech law, migrant-specific equality guarantee) coded by whether they explicitly protect non-citizens, with notes, sources and years in force; treaty status (ICERD, ICERD Article 14, ICRMW); party hate speech and online hate targets from V-Dem v16; party vote shares and immigration positions from V-Party; and country covariates.",
 "url":U,"version":"1.0","dateModified":"2026-10-31","inLanguage":["en","id"],
 "keywords":["hate speech","xenophobia","anti-immigration parties","radical right","voting","non-citizens","alienage","anti-discrimination law","constitutional equality","migrant rights","comparative constitutional law","empirical legal studies","V-Dem","V-Party","ICERD General Recommendation 30"],
 "creator":{"@type":"Organization","name":"Institute for Migrant Rights","url":"https://theimr.org/"},"publisher":{"@type":"Organization","name":"Institute for Migrant Rights","url":"https://theimr.org/"},
 "license":"https://creativecommons.org/licenses/by/4.0/","isAccessibleForFree":True,
 "spatialCoverage":[{"@type":"Place","name":n} for n in NAMES],"temporalCoverage":"2015/2026",
 "isBasedOn":["https://doi.org/10.23696/vdemds26","https://github.com/vdeminstitute/vdemdata"],
 "variableMeasured":["constitutional equality guarantee","anti-discrimination statute grounds","hate speech law grounds","migrant-specific equality guarantee","explicitness index","party hate speech (V-Dem v2smpolhate)","online hate speech targets (V-Dem v2smhargr)","nativist party vote share","restrictive party vote share","vote-weighted immigration stance","treaty status"],
 "distribution":[{"@type":"DataDownload","encodingFormat":f,"name":n,"contentUrl":U+"data/"+u} for n,u,f in [("Country data","country-data.csv","text/csv"),("Legal codings with notes and sources","codings.csv","text/csv"),("Codebook","codebook.csv","text/csv"),("Parties","parties.csv","text/csv"),("Treaty status","treaty-status.csv","text/csv"),("Citation (BibTeX)","imr-hate-speech-voting.bib","application/x-bibtex")]]}

TEASE = {"question": "Why compare explicit and conventional protection, and the three hypotheses tested.",
 "glance": "Four features of domestic law in 34 countries, scored by whether they name non-citizens.",
 "outcomes": "Party hate speech and votes for anti-immigration parties, country by country.",
 "findings": "Group comparisons, correlations and the interaction test, computed live.",
 "impunity": "Hate crime aggravation, access to justice and equal protection across groups.",
 "analyze": "Redefine the groups, choose countries and weights, test popularity against hate crime, and run your own tests.",
 "profiles": "Each country's provisions, treaties, outcomes and parties.",
 "methods": "Case selection, coding rules, measures, limitations and how to cite.",
 "help": "How advocates can use the gaps the coding identifies.",
 "sources": "CSV, JSON and BibTeX downloads, literature and version history."}
def fold(m):
    sid, body = m.group(1), m.group(2)
    hm = re.match(r'\s*(<p class="g-eye">.*?</p>)\s*(<h2>.*?</h2>)(.*)', body, re.S)
    eye, h2, rest = hm.group(1), hm.group(2), hm.group(3)
    op = " open" if sid == "question" else ""
    return ('<section class="g-sec fold" id="%s">\n<details%s>\n<summary class="fsum">%s%s<p class="teaser">%s</p><span class="chev" aria-hidden="true"></span></summary>\n<div class="fbody">%s</div>\n</details>\n</section>'
            % (sid, op, eye, h2, TEASE[sid], rest.rstrip()))
main = re.sub(r'<section class="g-sec" id="([a-z]+)">(.*?)</section>', fold, main, flags=re.S)
assert main.count('class="g-sec fold"') == len(TEASE)
main = main.replace('</ul>\n\n<section', '</ul>\n<p style="margin:18px 0 0"><button type="button" class="g-btn" id="foldall">Open all sections</button></p>\n\n<section', 1)
FOLDCSS = ('.g-sec.fold{padding:0;margin-top:40px}.g-sec.fold+.g-sec.fold{margin-top:0}'
 '.fsum{list-style:none;cursor:pointer;display:grid;grid-template-columns:1fr auto;column-gap:24px;align-items:center;padding:30px 0}'
 '.fsum::-webkit-details-marker{display:none}.fsum>*{grid-column:1}.fsum h2{margin:8px 0 0!important;transition:color .15s}'
 '.fsum .teaser{margin:6px 0 0;font-size:16px;color:#3A4138}'
 '.fsum .chev{grid-column:2;grid-row:1/span 3;width:44px;height:44px;border:1px solid #BFC6BA;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:26px;line-height:1;color:#B3261E;background:#fff}'
 '.fsum .chev::before{content:"+"}details[open]>.fsum .chev::before{content:"−"}details[open]>.fsum .teaser{display:none}'
 '.fsum:hover h2{color:#B3261E}.fsum:hover .chev{border-color:#B3261E}.fsum:focus-visible{outline:2px solid #1B1F1A;outline-offset:2px}'
 '.fbody{padding:4px 0 48px}@media print{details>.fbody{display:block!important}}')
FOLDJS = """<script>
(function(){
var ds=[].slice.call(document.querySelectorAll('section.fold>details')),b=document.getElementById('foldall');
var id=function(){return document.documentElement.lang==='id'};
function upd(){if(b)b.textContent=ds.every(function(d){return d.open})?(id()?'Tutup semua bagian':'Close all sections'):(id()?'Buka semua bagian':'Open all sections');}
function openFor(h){if(!h||h.length<2)return;var el=document.getElementById(h.slice(1));if(!el)return;var s=el.closest('section.fold');if(s){var d=s.querySelector(':scope>details');if(d&&!d.open)d.open=true;}}
ds.forEach(function(d){d.addEventListener('toggle',function(){if(d.open)window.dispatchEvent(new Event('resize'));upd();});});
if(b)b.addEventListener('click',function(){var all=ds.every(function(d){return d.open});ds.forEach(function(d){d.open=!all});});
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="#"]');if(a)openFor(a.getAttribute('href'));});
window.addEventListener('hashchange',function(){openFor(location.hash)});
window.addEventListener('beforeprint',function(){ds.forEach(function(d){d.open=true})});
new MutationObserver(upd).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
openFor(location.hash);upd();
})();
</script>
"""
h = src
h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, h)
h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + desc, h)
h = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + desc, h)
h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + title, h)
h = h.replace('https://theimr.org/countries-of-origin/"', U + '"')
h = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>", h, flags=re.S)
h = h.replace('<a href="/countries-of-origin/" aria-current="page">Countries of Origin</a>', '<a href="/countries-of-origin/">Countries of Origin</a>\n<a href="/hate-speech-voting/" aria-current="page">Hate Speech and Voting</a>')
h = h.replace("</style>", "#g-glance{min-width:820px}#g-out{min-width:900px}#g-ftab{min-width:900px}#g-ltab{min-width:640px}#g-cb{min-width:820px}#g-imp{min-width:760px}#g-out .g-cell{color:inherit;cursor:pointer}" + FOLDCSS + ".g-grid2>*{min-width:0}.g-card .g-mono{overflow-wrap:anywhere}" + "</style>", 1)
h = re.sub(r"<main.*?</main>", lambda m: main.strip(), h, flags=re.S)
h = h.replace('<script src="oc-data.js" defer></script>\n<script src="oc.js" defer></script>\n<script src="oc-i18n.js" defer></script>', '<script src="hv-data.js" defer></script>\n<script src="hv.js" defer></script>\n<script src="hv-i18n.js" defer></script>')
h = re.sub(r"@media print\{[^\n]*\}\}", "@media print{header,footer,.g-toc,.g-btns,.g-acts,#analyze{display:none!important}body{font-size:11pt}.g-sec{page-break-inside:avoid}}", h, count=1)
h = h.replace('<script src="/assets/lang.js" defer></script>', FOLDJS + '<script src="/assets/lang.js" defer></script>', 1)
assert "foldall" in h and "openFor" in h
assert "hv.js" in h and "Hate Speech and Voting" in h and "oc.js" not in h and "/hate-speech-voting/\"" in h
open(out, "w").write(h)
print("ok", len(h))
