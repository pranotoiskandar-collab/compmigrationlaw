# Field of law (2026-11-01, Pranoto's request): criminal | private | administrative | constitutional.
# 'constitutional' = constitutional review and human rights complaints (incl. regional and UN bodies).
# Coded by rule from court, parties and arguments, then corrected by hand in OVERRIDE. Researchers confirm.
import re
STATE=r"\b(Minister|Ministry|Director|Government|Union of India|Attorney[- ]General|Republic|Commission|Commissioner|Secretary|State of|Canada|Commonwealth|Chief|Department|Board|President|Immigration|Home Affairs|Security|Justice|Registration|Election|POEA|Director-General|Mayor|City|Province|Council|Authority|Tribunal|Pato)\b"
CRIM=r"^(People v\.|Public Prosecutor v\.|PP v\.|HKSAR v\.|R\. v\.|The State v\.|State v\.|S v\.|Prosecutor v\.)"
CONSTCOURT=r"Constitutional|Judicial Yuan|Mahkamah Konstitusi|Constitutional Tribunal|Supreme Federal Court|J\.Y\.|Hun-|PUU|Shura|Constitutional Council"
OVERRIDE={'hoffman-2002': 'administrative', 'sg-parti-liyani-2020': 'criminal', 'th-andy-hall-2016': 'criminal', 'ph-pasei-1988': 'constitutional', 'ph-jmm-1996': 'constitutional', 'ph-salac-2012': 'constitutional', 'pk-darshan-masih-1990': 'constitutional', 'il-gloten-2009': 'private', 'il-adam-2013': 'constitutional', 'il-desta-2015': 'constitutional', 'il-deposit-2020': 'constitutional', 'il-tsegata-2017': 'administrative', 'kw-dw-contract-2021': 'private', 'jp-lost-earnings-1997': 'private', 'jp-mclean-1978': 'administrative', 'jp-welfare-2014': 'administrative', 'jp-ushiku-2022': 'administrative', 'sa-oger-2017': 'private', 'sa-hail-dw-2015': 'private', 'sa-seemac-2018': 'private', 'ae-ad-cassation-2025': 'private', 'ae-dubai-waiver-2025': 'private', 'ae-gratuity-2014': 'private', 'qa-hamton-2019': 'private', 'om-sawadi-2016': 'private', 'my-93-workers-2024': 'private', 'hk-zn-2020': 'constitutional', 'hk-ubamaka-2012': 'constitutional', 'ca-andrews-1989': 'constitutional', 'us-plyler-1982': 'constitutional', 'us-graham-1971': 'constitutional', 'us-zadvydas-2001': 'administrative', 'ke-dadaab-2017': 'constitutional', 'ke-cord-2015': 'constitutional', 'c-ke-rck-2015': 'constitutional', 'c-au-al-kateb-2004': 'constitutional', 'c-au-s157-2003': 'constitutional', 'c-au-m68-2016': 'constitutional', 'c-ca-chiarelli-1992': 'constitutional', 'c-ph-nicolas-lewis-2019': 'constitutional', 'c-hk-lau-kong-yung-1999': 'constitutional', 'c-hk-gurung-2002': 'constitutional', 'c-hk-lau-fong-2004': 'constitutional', 'c-hk-qt-2018': 'constitutional', 'c-zw-salem-1994': 'constitutional', 'lb-contract-2020': 'administrative', 'ca-kanthasamy-2015': 'administrative', 'ca-baker-1999': 'administrative', 'ca-suresh-2002': 'constitutional', 'ca-ccr-2023': 'constitutional', 'c-h-mw-s-2023': 'administrative', 'c-h-mw-s-2023-2': 'administrative', 'c-h-mw-jones-ors-2005': 'administrative', 'c-h-za-jaga-1950': 'administrative', 'c-h-za-l-k-2023': 'administrative', 'c-h-za-road-accident-fund-2026': 'administrative', 'c-h-zw-piroro-2011': 'administrative'}
def branch(d,ARGLAW):
    if d['id'] in OVERRIDE: return OVERRIDE[d['id']]
    n=d['name']; c=d['court']+' '+d.get('cite','')
    if d['forum'] in('regional','international'): return 'constitutional'
    if re.search(CRIM,n) or re.search(r'murder|acquitted|prosecut|sentenc|trafficking trial|criminal',n+' '+d.get('held',''),re.I) and not re.search(STATE,n.split(' v. ')[0] if ' v. ' in n else ''): 
        if re.search(CRIM,n) or 'case' in n.lower(): return 'criminal'
    if re.search(CONSTCOURT,c): return 'constitutional'
    if d['cc'] in('IN','BD','PK','NP','LK') and not re.search(CRIM,n): return 'constitutional'  # writ and public interest petitions under the constitution
    laws=' '.join(ARGLAW.get(a,'') for a,_ in d['args'])
    if ' v. ' in n:
        a,b=n.split(' v. ',1)
        if not re.search(STATE,a) and not re.search(STATE,b): return 'private'
    if 'constitution' in laws: return 'constitutional'
    return 'administrative'
