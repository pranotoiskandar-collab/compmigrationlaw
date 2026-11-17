import sys, html
sys.path.insert(0,'.')
from registry import R
from verdicts import V
e=html.escape
GROUPS=[('bot-check','1. Sites with a bot check','Open each site in a normal browser. If it opens, note what it covers and how to search it. If a "verify you are human" box keeps coming back, stop and write that down. Do not use any tool to get past the check.'),
('down','2. Sites that were down or did not answer','Try again on two different days. If a site is still down, look for its current address on the court\'s or ministry\'s home page. Some sites may work only from inside the country: if so, write "may be limited to the country".'),
('addr','3. Sites with a moved or wrong address','Find the right page on the same official site and paste the address.'),
('not-confirmed','4. Sites that opened but need a person to confirm','The page loaded, but we could not see its content. Check that it really holds judgments or laws, and paste the address of its search page.'),
('other','5. Sites where a person has to do the search','The site works, but the search form has a captcha, needs an account, or limited our visits. Search by hand with the terms below. Do not create accounts.')]
def g(v):
    if v in ('moved','wrong-url'): return 'addr'
    if v in ('captcha-search','login','blocked'): return 'other'
    return v
TYPE={'courts':'Court decisions','laws':'Laws'}
SRC={'lii-free':' (free legal information institute, not government: label as secondary)','secondary':' (not official: label as secondary)','official-guidance':' (ministry: "official guidance")'}
th='style="background:#E8F0E8;text-align:left"'
out=['<html><body>','<h1>National court and law repositories: tasks for research assistants</h1>',
'<p><i>Institute for Migrant Rights, Migration Jurisprudence from the South. Batch 1, 13 November 2026.</i></p>',
'<h2>What this is</h2>',
'<p>We are listing the official websites where each country publishes its court decisions and its laws on migrant workers (labour, immigration, domestic work, farm work, recruitment, non-discrimination). Claude checked 104 sites. 58 opened normally. The 46 below could not be opened or confirmed automatically, so they need a person.</p>',
'<h2>How to work</h2><ul>',
'<li>Write your name in a row before you start it, so two people do not do the same site.</li>',
'<li>In "What you found", give the correct address (if different), whether the site has material on migrant workers (yes / some / no), and the language.</li>',
'<li>Use the sites as an ordinary visitor. Do not create accounts, pay, or get round captchas or bot checks.</li>',
'<li>Use official sites only (courts, governments, parliaments). If you use anything else, label it "secondary".</li>',
'<li>If you find a relevant case, add it to the verification worksheet as usual, or send it to secretariat@theimr.org.</li>',
'<li>Gulf States: neutral wording only.</li></ul>',
'<p><b>Search words for court decisions:</b> migrant worker, foreign worker, domestic worker, farm or agricultural worker, recruitment agency, deportation, work permit, wages, trafficking. Use the local-language terms too.<br><b>Search words for laws:</b> labour or employment act, immigration or foreigners act, overseas employment or recruitment law, domestic worker rules, anti-discrimination law, latest amendment.</p>',
'<p>Beware false hits: "migration" can mean digital TV migration or moving staff between job grades. Search for immigration, foreign national, work permit or deportation instead.</p>']
rows=[(r,)+V.get(r[6],('opens','')) for r in R]
for key,title,intro in GROUPS:
    sel=[x for x in rows if g(x[1])==key]
    sel.sort(key=lambda x:(x[0][2],x[0][1]))
    out.append(f'<h2>{e(title)} ({len(sel)})</h2><p>{e(intro)}</p>')
    out.append(f'<table border="1" cellpadding="4" style="border-collapse:collapse"><tr><th {th}>Country</th><th {th}>Repository</th><th {th}>What we saw</th><th {th}>What you found</th><th {th}>Name and date</th></tr>')
    for r,v,note in sel:
        iso,country,group,kind,nm,op,url,lang,st=r
        out.append(f'<tr><td>{e(country)}</td><td><a href="{e(url)}">{e(nm)}</a><br>{TYPE[kind]}. {e(op)}{e(SRC.get(st,""))}</td><td>{e(note)}</td><td></td><td></td></tr>')
    out.append('</table>')
ok=[x for x in rows if x[1]=='opens']; ok.sort(key=lambda x:(x[0][2],x[0][1]))
out.append(f'<h2>6. Sites that opened normally ({len(ok)})</h2><p>No checking needed. These are good places to search for cases and laws.</p>')
out.append(f'<table border="1" cellpadding="4" style="border-collapse:collapse"><tr><th {th}>Country</th><th {th}>Repository</th><th {th}>Type</th></tr>')
for r,v,note in ok:
    iso,country,group,kind,nm,op,url,lang,st=r
    extra=e(SRC.get(st,''))+(' '+e(note) if note else '')
    out.append(f'<tr><td>{e(country)}</td><td><a href="{e(url)}">{e(nm)}</a>{extra}</td><td>{TYPE[kind]}</td></tr>')
out.append('</table><p>The same list, with more columns, is in the spreadsheet ra-databases-to-search.xlsx, sheet "National repositories".</p></body></html>')
open('students-gdoc.html','w').write('\n'.join(out))
print(len('\n'.join(out)))
