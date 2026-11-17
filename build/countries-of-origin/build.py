import re, json, sys
src = open('/mnt/project-files/theimr-site/east-asia/index.html').read()
main = open('build/main.html').read()
desc = "Emigration and protection law and policy in eight countries of origin (Indonesia, the Philippines, Vietnam, Nepal, Bangladesh, India, Sri Lanka and Pakistan): recruitment, fees, contracts, welfare funds, labor attachés, redress, exit rules and reintegration, with a codebook, bilateral agreements, downloadable data and tools to compare."
title = "Countries of origin · Institute for Migrant Rights"
ld = {"@context":"https://schema.org","@type":"Dataset","name":"Countries of origin: emigration and protection law and policy compared","alternateName":"IMR countries of origin comparative dataset",
 "description":"Comparative legal data on eight countries of origin of migrant workers in Asia: nine de jure features of emigration governance (licensing and liability of recruiters, recruitment fees, contracts, pre-departure orientation, welfare funds and insurance, labor attachés, redress at home, sex- and age-specific exit restrictions, return and reintegration) coded with notes and sources; treaty status; international, regional, interregional and bilateral instruments; laws and policies with links to official sources; annual outflows; origin–destination corridors; and a dated timeline of legal developments.",
 "url":"https://theimr.org/countries-of-origin/","version":"1.1","dateModified":"2026-10-31","inLanguage":["en","id"],
 "keywords":["migrant workers","countries of origin","emigration law","labor migration governance","fair recruitment","recruitment fees","bilateral labor agreements","welfare funds","labor attachés","reintegration","CEDAW General Recommendation 26","ICRMW","violence against migrant workers","ILO C190","comparative law","empirical legal studies","Indonesia","Philippines","Vietnam","Nepal","Bangladesh","India","Sri Lanka","Pakistan"],
 "creator":{"@type":"Organization","name":"Institute for Migrant Rights","url":"https://theimr.org/"},"publisher":{"@type":"Organization","name":"Institute for Migrant Rights","url":"https://theimr.org/"},
 "license":"https://creativecommons.org/licenses/by/4.0/","isAccessibleForFree":True,
 "spatialCoverage":[{"@type":"Place","name":n} for n in ["Indonesia","Philippines","Vietnam","Nepal","Bangladesh","India","Sri Lanka","Pakistan"]],
 "temporalCoverage":"1979/2026",
 "variableMeasured":["licensing and liability of recruiters","recruitment fees","employment contract before departure","pre-departure orientation","welfare fund or compulsory insurance","labor or welfare officers abroad","redress at home","sex- and age-specific exit restrictions","return and reintegration","protection from violence (shelters, assistance lines, legal assistance, gender-specific protection, deaths abroad, anti-trafficking law)","treaty status","bilateral instruments","annual outflows"],
 "distribution":[{"@type":"DataDownload","encodingFormat":f,"name":n,"contentUrl":"https://theimr.org/countries-of-origin/data/"+u} for n,u,f in [("Coded cells with notes and sources","codings.csv","text/csv"),("Codebook","codebook.csv","text/csv"),("Treaty status","treaty-status.csv","text/csv"),("Instruments","instruments.csv","text/csv"),("Laws and policies","laws-policies.csv","text/csv"),("Outflows","outflows.csv","text/csv"),("Corridors","corridors.csv","text/csv"),("Protection from violence","protection.csv","text/csv"),("Legal developments","developments.csv","text/csv"),("Citation (BibTeX)","imr-countries-of-origin.bib","application/x-bibtex")]]}
h = src
h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, h)
h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1)+desc, h)
h = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1)+desc, h)
h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1)+title, h)
h = h.replace('https://theimr.org/east-asia/"', 'https://theimr.org/countries-of-origin/"')
h = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">'+json.dumps(ld, ensure_ascii=False)+'</script>', h, flags=re.S)
h = h.replace('<a href="/east-asia/" aria-current="page">East Asia</a>', '<a href="/east-asia/">East Asia</a>\n<a href="/countries-of-origin/" aria-current="page">Countries of Origin</a>')
h = h.replace('#g-cellnote{margin-top:18px}', '#g-cellnote{margin-top:18px}\n#g-outt,#g-atable,#g-ltable,#g-deaths{min-width:860px}#g-vglance{min-width:820px}#g-bmat{min-width:760px}', 1)
h = re.sub(r'<main.*?</main>', lambda m: main.strip(), h, flags=re.S)
h = h.replace('<script src="ea-data.js" defer></script>\n<script src="ea.js" defer></script>\n<script src="ea-i18n.js" defer></script>', '<script src="oc-data.js" defer></script>\n<script src="oc.js" defer></script>\n<script src="oc-i18n.js" defer></script>')
assert 'oc.js' in h and 'Countries of Origin' in h and 'east-asia/"' not in h.split('<main')[0].replace('href="/east-asia/"','')
open(sys.argv[1], 'w').write(h)
