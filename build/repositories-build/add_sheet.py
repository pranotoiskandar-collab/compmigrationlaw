import sys, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
sys.path.insert(0,'/mnt/project-files/repositories-build')
from registry import R
from verdicts import V
P='/mnt/project-files/court-decisions-checking/ra-databases-to-search.xlsx'
wb=openpyxl.load_workbook(P)
ALREADY={'https://www.saflii.org/','https://new.kenyalaw.org/','https://bj.scjn.gob.mx/','https://sjconsulta.csjn.gov.ar/','https://supremecourt.lk/','https://cons.judicial.gov.tw/','https://www.courts.go.jp/app/hanrei_jp/search1'}
SEARCH={'courts':'migrant worker, foreign worker, domestic worker, farm/agricultural worker, recruitment agency, deportation, work permit, wages, trafficking (use local-language terms)',
        'laws':'labour/employment act, immigration or foreigners act, overseas employment or recruitment law, domestic worker rules, anti-discrimination law, latest amendment'}
TASK={'bot-check':'Open in a normal browser. If it works, note what the site covers and how to search it. Do not solve repeated captchas or use tools to get round the check.',
 'down':'Try again on two different days. If still down, look for the current address on the court or ministry home page and paste it in "correct URL".',
 'wrong-url':'Find the correct page on the same official site and paste it in "correct URL".',
 'moved':'Confirm the new address is the same repository and paste it in "correct URL".',
 'not-confirmed':'Open in a browser and confirm this is the repository (judgments or laws). Paste the direct search page in "correct URL".',
 'login':'Do not create an account. Note what can be seen without one.',
 'captcha-search':'Search by hand with the terms in "what to search"; record cases on the worksheet as usual.',
 'blocked':'Try again later in a browser, slowly.'}
LABEL={'opens':'Opens','bot-check':'Bot check','down':'Down / unreachable','wrong-url':'Wrong address','moved':'Moved','not-confirmed':'Opens, content not confirmed','login':'Login needed to search','captcha-search':'Opens, search has captcha','blocked':'Temporarily blocked'}
name='National repositories'
if name in wb.sheetnames: del wb[name]
ws=wb.create_sheet(name)
hdr=['priority','country','group','type','repository','run by','url','language','source type','check 2026-11-13','note from check','RA task','what to search','also on "Databases to search"','RA name','date done','correct URL','covers migrant-worker material? (yes/no/some)','notes']
ws.append(hdr)
def pri(v,group):
    if v in ('opens',): return ''
    if v=='captcha-search' or group in ('Gulf','East Asia','Southeast Asia','Southeast Asia (origin)','Origin states'): return 1
    return 2
rows=[]
for r in R:
    iso,country,group,kind,nm,op,url,lang,st=r
    v,note=V.get(url,('opens',''))
    rows.append([pri(v,group),country,group,'court decisions' if kind=='courts' else 'laws',nm,op,url,lang,
      {'official':'official','official-guidance':'official guidance (ministry/agency)','lii-free':'free legal information institute (not government): flag as secondary','secondary':'secondary (not official)'}[st],
      LABEL[v],note,TASK.get(v,''),SEARCH[kind],'yes' if url in ALREADY else '','','','','',''])
rows.sort(key=lambda x:(x[0]=='' ,x[0] if x[0]!='' else 9,x[2],x[1]))
for x in rows: ws.append(x)
bold=Font(bold=True); fill=PatternFill('solid',fgColor='E8F0E8')
for c in ws[1]: c.font=bold; c.fill=fill; c.alignment=Alignment(wrap_text=True,vertical='top')
W=[8,16,18,14,34,26,36,16,22,18,36,44,40,12,12,12,30,18,24]
for i,w in enumerate(W): ws.column_dimensions[openpyxl.utils.get_column_letter(i+1)].width=w
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment=Alignment(wrap_text=True,vertical='top')
ws.freeze_panes='C2'; ws.auto_filter.ref=ws.dimensions
rm=wb['Read me']
lines=[r[0].value for r in rm.iter_rows()]
add=['NEW 2026-11-13: sheet "National repositories" lists official national (and regional) sites for court decisions and for laws on migrant workers. Rows with a priority and an "RA task" are the ones Claude could not open or confirm; rows without a priority opened normally and need no action yet.',
     'For those rows: follow the RA task, fill "correct URL" and "covers migrant-worker material?", and add any cases found to the verification worksheet. Official sites only; a site marked "secondary" or "not government" can be used but must be labelled as such.']
for a in add:
    if a not in lines: rm.append([a])
wb.save(P)
from collections import Counter
print(Counter(x[9] for x in rows), sum(1 for x in rows if x[0]!=''))
