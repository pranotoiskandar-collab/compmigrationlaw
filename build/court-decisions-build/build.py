import json,csv,io,sys,os,re
sys.path.insert(0,os.path.dirname(__file__)); import decisions as m
OUT='/mnt/project-files/theimr-site/court-decisions/'
VERSION='0.1'; DATE='2026-11-01'
D=m.D
import links, branch as BRM
NLINK=links.apply(D)
import harvest_links; NHL=harvest_links.apply(D); print('harvest links added to',NHL,'existing entries')
_AL={k:l for k,e,i,l in m.ARGS}
for _d in D: _d['branch']=BRM.branch(_d,_AL)
import reasoning as RSN
for _d in D: _d['tools']=RSN.code(_d)
CODEBOOK=[
('id','Stable identifier of the decision entry','text'),
('name','Case name as commonly cited','text'),
('court','Court or body that decided','text'),
('tier','national = a domestic court; regional = a regional human rights court; international = a global court or treaty body','national | regional | international'),
('forum','For national courts: destination = the country where the migrant worked; origin = the worker’s own country. Regional and international bodies are coded as such','destination | origin | regional | international'),
('level','Place of the court in its hierarchy','apex | appeal | first | regional | advisory | international'),
('country','ISO 3166 code of the state whose law or conduct was at issue','code'),
('region','Region of that state, used for ordering (Asia, Africa, the Middle East and Latin America first)','asia | africa | mideast | gulf | latam | pacific | europe | americas | intl (pacific includes Australia and New Zealand)'),
('date','Date of the decision (YYYY-MM-DD; a year alone where the day is not yet confirmed)','date'),
('citation','Docket or report citation','text'),
('sector','Sector of work involved','text'),
('issues','Legal issues, semicolon separated','list'),
('situations','Visitor-facing situations the decision speaks to','list'),
('stages','Stage of the migration journey where the problem arose: 1 recruitment, 2 leaving, 3 working abroad, 4 changing or losing the job, 5 return and after','list of 1–5'),
('branch','Type of case: criminal = prosecution of a person; private = dispute between private parties (labor, contract, tort), including claims against recruitment agencies and employers; administrative = challenge to a decision or practice of a government agency (immigration, labor, welfare) on ordinary legal grounds; constitutional = constitutional review, fundamental-rights petitions, and complaints to regional or international human rights bodies. Coded by rule from the court, the parties and the arguments, then corrected by hand; to be confirmed by researchers','criminal | private | administrative | constitutional'),
('outcome','Result for the worker or migrant side','won | lost | advisory | unknown (candidates not yet checked)'),
('follow_up','What happened after the decision: carried = remedy or reform carried out; partly; not = not carried out; unknown = not yet established; none = nothing to carry out (worker lost, advisory, or law kept as it was)','carried | partly | not | unknown | none'),
('arguments','Argument codes made for the worker side with 1 = accepted, 0 = rejected (see arguments.csv)','list'),
('tools','Reasoning tools (after Farnsworth, The Legal Analyst, 2007): exante | lca | agency | rule | standard | slope | remedy | baseline | proof; see reasoning-tools.csv. Coded by rule from the argument codes and the wording of the question and holding (AI-assisted), full entries only; to be confirmed against the judgment','list'),
('status','C = unchecked candidate: name, court, year and topic only, shown with a mark, to be confirmed or removed; S = full entry coded from secondary sources and summaries, pending a line-by-line check against the judgment; P = checked against the judgment','C | S | P'),
]
for d in D: d.setdefault('status','S')
js={'version':VERSION,'date':DATE,'decisions':[{**{k:v for k,v in d.items() if k not in('args','after','src')},
     'args':[{'a':a,'ok':bool(o)} for a,o in d['args']],
     'after':[{'d':x,'en':e,'id':i} for x,e,i in d['after']],
     'src':[{'t':t,'u':u} for t,u in d['src']]} for d in D],
    'args':[{'k':k,'en':e,'id':i,'law':l} for k,e,i,l in m.ARGS],
    'tools':[{'k':k,'en':e,'id':i,'ch':c,'def':de,'def_id':di} for k,e,i,c,de,di in RSN.TOOLS],
    'codebook':[{'v':v,'def':de,'vals':va} for v,de,va in CODEBOOK]}
open(OUT+'cd-data.js','w',encoding='utf-8').write('/* Migration Jurisprudence from the South, v%s (%s). Generated from /mnt/project-files/court-decisions-build/decisions.py; do not edit by hand. */\nwindow.CD=%s;\n'%(VERSION,DATE,json.dumps(js,ensure_ascii=False)))
def w(name,rows,head):
    with open(OUT+'data/'+name,'w',encoding='utf-8',newline='') as f:
        c=csv.writer(f); c.writerow(head); c.writerows(rows)
w('decisions.csv',[[d['id'],d['name'],d['court'],d['tier'],d['forum'],d['level'],d['cc'],d['region'],d['date'],d['cite'],d['branch'],d['sector'],';'.join(d['issues']),';'.join(d['situations']),';'.join(map(str,d['stages'])),d['outcome'],d['follow'],';'.join('%s=%d'%(a,o) for a,o in d['args']),d['status'],';'.join(d['tools']),d['q'],d['held'],d['plain'],d['plain_id'],' | '.join(u for _,u in d['src'])] for d in D],
  ['id','name','court','tier','forum','level','country','region','date','citation','branch','sector','issues','situations','stages','outcome','follow_up','arguments','status','reasoning_tools','question','holding','plain_en','plain_id','sources'])
w('arguments.csv',[[d['id'],a,o,d['tier'],d['cc'],d['date'][:4],d['outcome'],d['follow']] for d in D for a,o in d['args']],['decision_id','argument','accepted','tier','country','year','outcome','follow_up'])
w('argument-codes.csv',[list(a) for a in m.ARGS],['code','label_en','label_id','type_of_law'])
w('reasoning.csv',[[d['id'],k,d['tier'],d['cc'],d['date'][:4],d['outcome']] for d in D for k in d['tools']],['decision_id','tool','tier','country','year','outcome'])
w('reasoning-tools.csv',[list(x) for x in RSN.TOOLS],['code','label_en','label_id','farnsworth_chapter','definition_en','definition_id'])
w('timeline.csv',[[d['id'],x,e,i] for d in D for x,e,i in d['after']],['decision_id','date','event_en','event_id'])
w('codebook.csv',CODEBOOK,['variable','definition','values'])
json.dump(js,open(OUT+'data/decisions.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
from collections import Counter
cnt=Counter(); first={}
for d in D:
    for h in {links.host(u) for _,u in d['src']}:
        cnt[h]+=1; first.setdefault(h,[u for _,u in d['src'] if links.host(u)==h][0])
SOURCES=[(links.DB.get(h,(h,''))[0],links.DB.get(h,(h,''))[1],h,links.kind(h),n,re.match(r'https?://[^/#?]+',first[h])[0]+'/') for h,n in cnt.most_common()]
w('sources.csv',[list(x) for x in SOURCES],['database','run_by','site','kind','decisions_linked','home'])
json.dump(SOURCES,open(os.path.dirname(__file__)+'/sources.json','w'),ensure_ascii=False)
with open('/mnt/project-files/court-decisions-checking/source-links-to-check.csv','w',newline='',encoding='utf-8') as f:
    c=csv.writer(f); c.writerow(['id','status','name','court','country','date','citation','problem','current_link','correct_url (fill in)'])
    for d in D:
        if all(links.generic(u) for _,u in d['src']): c.writerow([d['id'],d['status'],d['name'],d['court'],d['cc'],d['date'],d['cite'],'no direct link yet',d['src'][0][1],''])
        elif d.get('_built'): c.writerow([d['id'],d['status'],d['name'],d['court'],d['cc'],d['date'],d['cite'],'link built from citation or a search: open and confirm',d['src'][0][1],''])
print(len(D),'decisions written;',NLINK,'given direct links;',len(SOURCES),'source sites;',Counter(d['branch'] for d in D))
