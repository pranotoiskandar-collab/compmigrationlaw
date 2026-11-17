# Writes one plain-HTML page per decision at /court-decisions/d/<id>/ so search engines and chatbots
# can find each decision, plus sitemap entries and /llms.txt. Run after build.py and page.py.
import json,re,os,html,shutil
SITE='/mnt/project-files/theimr-site'; CD=SITE+'/court-decisions'
s=open(CD+'/cd-data.js').read(); D=json.loads(s[s.index('{'):s.rindex('}')+1])['decisions']
shell=open(CD+'/index.html').read()
COUNTRY=dict(re.findall(r'(\w\w): \["([^"]+)", "[^"]+"\]',open(CD+'/cd.js').read().split('var COUNTRY = ')[1].split('};')[0]+'}'))
BR={'criminal':'Criminal','private':'Private','administrative':'Administrative','constitutional':'Constitutional and human rights'}
TIER={'national':'National court','regional':'Regional court or body','international':'International body'}
OUT={'won':'Decided for the migrant side','lost':'Decided against the migrant side','partly':'Partly for the migrant side','mixed':'Mixed result','unknown':'Outcome to be confirmed'}
e=lambda x: html.escape(str(x or ''),quote=True)
head,rest=shell.split('<main',1); main_close=rest.index('</main>')
foot=rest[main_close+7:]
foot=re.sub(r'<script src="cd-(data|i18n)\.js" defer></script>\s*|<script src="cd\.js" defer></script>\s*','',foot)
head=re.sub(r'<script type="application/ld\+json">.*?</script>','',head,flags=re.S)
if os.path.isdir(CD+'/d'): shutil.rmtree(CD+'/d')
urls=[]
for d in D:
    url='https://theimr.org/court-decisions/d/%s/'%d['id']
    cn=COUNTRY.get(d['cc'],d['cc']); yr=d['date'][:4]
    desc=(d.get('plain') or d.get('held') or d['name'])[:300]
    title='%s (%s, %s)'%(d['name'],cn,yr)
    h=head.replace(re.search(r'<title>.*?</title>',head).group(0),'<title>%s · Institute for Migrant Rights</title>'%e(title))
    h=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="%s">'%e(desc),h)
    h=re.sub(r'<link rel="canonical" href="[^"]*">','<link rel="canonical" href="%s">'%url,h)
    h=re.sub(r'<meta property="og:[^>]*>\s*','',h)
    ld={"@context":"https://schema.org","@type":"CreativeWork","name":d['name'],"headline":title,"description":desc,"url":url,"inLanguage":["en","id"],
        "about":"Court decision on migrants' rights: "+d['court']+', '+cn+', '+d['date'],"dateModified":"2026-11-01","isAccessibleForFree":True,
        "isPartOf":{"@type":"Dataset","name":"Migration Jurisprudence from the South","url":"https://theimr.org/court-decisions/"},
        "publisher":{"@type":"Organization","name":"Institute for Migrant Rights","url":"https://theimr.org/"},
        "citation":d['cite'],"sameAs":[x['u'] for x in d['src'] if x.get('u') and 'front page' not in x['t']][:3]}
    h=h.replace('</head>','<script type="application/ld+json">%s</script>\n</head>'%json.dumps(ld,ensure_ascii=False))
    cand=d['status']=='C'
    m=['<main style="padding: 48px 0 72px" id="court-decision"><div class="g-wrap" style="max-width:820px;margin:0 auto;padding:0 24px">',
       '<p class="g-note"><a href="/court-decisions/">Migration Jurisprudence from the South</a> › %s</p>'%e(cn),
       '<h1>%s</h1>'%e(d['name']),
       '<p><b>%s</b> · %s · %s · %s</p>'%(e(d['court']),e(cn),e(d['date']),e(TIER.get(d['tier'],''))),
       '<p>Citation: %s<br>Type of case: %s<br>Outcome: %s</p>'%(e(d['cite']),e(BR.get(d.get('branch'),'')),e(OUT.get(d['outcome'],d['outcome'])))]
    if d['status']=='S': m.append('<p class="g-note"><a class="cd-pill s-S" href="/ai-use/#composition">Unverified</a> Summary pre-written by AI from secondary sources, being checked against the judgment.</p>')
    if cand: m.append('<p class="g-note"><b>Unchecked candidate.</b> This decision has been located in an official or free law database but has not yet been read and written up. The summary below describes the subject only.</p>')
    if d.get('q'): m.append('<h2>Question</h2><p>%s</p>'%e(d['q']))
    if d.get('held'): m.append('<h2>What the court decided</h2><p>%s</p>'%e(d['held']))
    if d.get('plain'): m.append('<h2>%s</h2><p>%s</p>'%('Subject' if cand else 'In plain language',e(d['plain'])))
    if d.get('plain_id'): m.append('<h2 lang="id">%s</h2><p lang="id">%s</p>'%('Pokok perkara' if cand else 'Dalam bahasa sederhana',e(d['plain_id'])))
    if d.get('q_id'): m.append('<p lang="id"><b>Pertanyaan:</b> %s</p>'%e(d['q_id']))
    if d.get('after'):
        m.append('<h2>What happened afterwards</h2><ul>'+''.join('<li>%s: %s</li>'%(e(a['d']),e(a['en'])) for a in d['after'])+'</ul>')
    m.append('<h2>Sources</h2><ul>'+''.join('<li><a href="%s" rel="noopener">%s</a></li>'%(e(x['u']),e(x['t'])) for x in d['src'] if x.get('u'))+'</ul>')
    m.append('<p><a href="/court-decisions/#d/%s">Open this decision in the interactive collection</a> (compare, filter, Indonesian view, downloads).</p>'%e(d['id']))
    m.append('<p class="g-note">Cite as: Institute for Migrant Rights (2026), Migration Jurisprudence from the South, version 0.1, %s. This page summarizes a court decision for research and advocacy; it is not legal advice.</p>'%url)
    m.append('</div></main>')
    os.makedirs(CD+'/d/'+d['id'],exist_ok=True)
    open(CD+'/d/%s/index.html'%d['id'],'w').write(h+'\n'.join(m)+foot)
    urls.append(url)
# index of all decisions as plain links (crawlable list)
lst=['<main style="padding: 48px 0 72px"><div style="max-width:820px;margin:0 auto;padding:0 24px"><h1>All decisions: list</h1><p>Every decision in <a href="/court-decisions/">Migration Jurisprudence from the South</a>, as plain links. %d decisions.</p><ul>'%len(D)]
for d in sorted(D,key=lambda d:(COUNTRY.get(d['cc'],d['cc']),d['date'])):
    lst.append('<li><a href="/court-decisions/d/%s/">%s</a> (%s, %s)</li>'%(e(d['id']),e(d['name']),e(COUNTRY.get(d['cc'],d['cc'])),e(d['date'][:4])))
lst.append('</ul></div></main>')
h=head.replace(re.search(r'<title>.*?</title>',head).group(0),'<title>All decisions · Migration Jurisprudence from the South · Institute for Migrant Rights</title>')
h=re.sub(r'<link rel="canonical" href="[^"]*">','<link rel="canonical" href="https://theimr.org/court-decisions/d/">',h)
h=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="List of all %d court decisions on migrants in Migration Jurisprudence from the South, with links to each decision page.">'%len(D),h)
open(CD+'/d/index.html','w').write(h+'\n'.join(lst)+foot)
urls.insert(0,'https://theimr.org/court-decisions/d/')
# sitemap
sm=open(SITE+'/sitemap.xml').read()
sm=re.sub(r'\s*<url><loc>https://theimr.org/court-decisions/d/[^<]*</loc>[^\n]*</url>','',sm)
sm=sm.replace('</urlset>',''.join('\n  <url><loc>%s</loc><lastmod>2026-11-01</lastmod></url>'%u for u in urls)+'\n</urlset>')
open(SITE+'/sitemap.xml','w').write(sm)
print(len(urls),'static pages; sitemap urls',sm.count('<url>'))
