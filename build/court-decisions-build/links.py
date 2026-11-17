# Direct source links (2026-11-01). Many entries pointed only at a database front page.
# direct(d) builds a case-specific link from the citation where the database uses a stable URL pattern,
# or a case-specific search link where it does not. Search links are labelled "(search)".
import re
from urllib.parse import quote, quote_plus

def _q(s): return quote_plus(re.sub(r'\s*\(.*?\)|\[.*?\]','',s).strip())

DB={  # host -> (database name, who runs it)
 'saflii.org':('SAFLII','Southern African Legal Information Institute'),
 'austlii.edu.au':('AustLII','Australasian Legal Information Institute'),
 'nzlii.org':('NZLII','New Zealand Legal Information Institute'),
 'bailii.org':('BAILII','British and Irish Legal Information Institute'),
 'canlii.org':('CanLII','Canadian Legal Information Institute'),
 'scc-csc.lexum.com':('Supreme Court of Canada judgments','Supreme Court of Canada / Lexum'),
 'hklii.hk':('HKLII','Hong Kong Legal Information Institute'),
 'legalref.judiciary.hk':('Legal Reference System','Hong Kong Judiciary'),
 'doj.gov.hk':('Notable judgments','Department of Justice, Hong Kong'),
 'indiankanoon.org':('Indian Kanoon','Indian Kanoon'),
 'sci.gov.in':('Supreme Court of India','Supreme Court of India'),
 'lawphil.net':('Lawphil','Arellano Law Foundation, Philippines'),
 'elibrary.judiciary.gov.ph':('Supreme Court E-Library','Supreme Court of the Philippines'),
 'kenyalaw.org':('Kenya Law','National Council for Law Reporting, Kenya'),
 'paclii.org':('PacLII','Pacific Islands Legal Information Institute'),
 'hudoc.echr.coe.int':('HUDOC','European Court of Human Rights'),
 'juris.ohchr.org':('OHCHR jurisprudence database','UN Human Rights Office'),
 'docs.un.org':('UN Official Document System','United Nations'),
 'corteidh.or.cr':('Inter-American Court of Human Rights','Inter-American Court of Human Rights'),
 'achpr.au.int':('African Commission decisions','African Commission on Human and Peoples’ Rights'),
 'african-court.org':('African Court','African Court on Human and Peoples’ Rights'),
 'normlex.ilo.org':('NORMLEX','International Labour Organization'),
 'ilo.org':('ILO','International Labour Organization'),
 'icj-cij.org':('ICJ','International Court of Justice'),
 'supreme.justia.com':('Justia US Supreme Court','Justia'),
 'cons.judicial.gov.tw':('Constitutional Court','Constitutional Court, Taiwan'),
 'courts.go.jp':('Courts in Japan','Supreme Court of Japan'),
 'ccourt.go.kr':('Constitutional Court of Korea','Constitutional Court of Korea'),
 'elitigation.sg':('eLitigation','Supreme Court of Singapore'),
 'kehakiman.gov.my':('Judiciary of Malaysia','Office of the Chief Registrar, Malaysia'),
 'mkri.id':('Mahkamah Konstitusi','Constitutional Court of Indonesia'),
 'portal.stf.jus.br':('STF','Supreme Federal Court, Brazil'),
 'stf.jus.br':('STF','Supreme Federal Court, Brazil'),
 'worldlii.org':('WorldLII','World Legal Information Institute'),
 'commonlii.org':('CommonLII','Commonwealth Legal Information Institute'),
 'ecowas.int':('ECOWAS Court','Community Court of Justice of ECOWAS'),
 'courtecowas.org':('ECOWAS Court','Community Court of Justice of ECOWAS'),
 'tribunalconstitucional.gob.do':('Tribunal Constitucional','Constitutional Tribunal, Dominican Republic'),
 'tribunalconstitucional.cl':('Tribunal Constitucional','Constitutional Tribunal, Chile'),
 'scjn.gob.mx':('SCJN','Supreme Court of Justice, Mexico'),
 'corteconstitucional.gov.co':('Corte Constitucional','Constitutional Court, Colombia'),
 'supremecourt.gov.bd':('Supreme Court of Bangladesh','Supreme Court of Bangladesh'),
 'versa.cardozo.yu.edu':('Versa (Cardozo Law)','Cardozo School of Law, translations of Israeli Supreme Court judgments'),
 'supremecourt.gov.il':('Supreme Court of Israel','Judicial Authority of Israel'),
}
DB.update({
 'supreme.court.gov.il':('Supreme Court of Israel','Judicial Authority of Israel'),
 'hcourt.gov.au':('High Court of Australia','High Court of Australia'),
 'supremecourt.uk':('UK Supreme Court','UK Supreme Court'),
 'acerwc.africa':('ACERWC','African Committee of Experts on the Rights and Welfare of the Child'),
 'supremecourt.gov.pk':('Supreme Court of Pakistan','Supreme Court of Pakistan'),
 'eng.scourt.go.kr':('Supreme Court of Korea','Supreme Court of Korea'),
 'decisions.fca-caf.gc.ca':('Federal Court of Appeal decisions','Federal Court of Appeal, Canada'),
 'supremecourt.or.th':('Supreme Court of Thailand','Supreme Court of Thailand'),
 'refworld.org':('Refworld','UNHCR'),
 'oas.org':('Inter-American Commission on Human Rights','Organization of American States'),
 'repositorio.mpd.gov.ar':('Public Defender repository','Ministerio Público de la Defensa, Argentina'),
 'amnesty.org':('Amnesty International','Amnesty International'),
 'hrw.org':('Human Rights Watch','Human Rights Watch'),
 'business-humanrights.org':('Business & Human Rights Resource Centre','Business & Human Rights Resource Centre'),
 'ituc-csi.org':('ITUC','International Trade Union Confederation'),
 'hurights.or.jp':('HURIGHTS OSAKA','Asia-Pacific Human Rights Information Center'),
})
OFFICIAL={'hudoc.echr.coe.int','corteidh.or.cr','achpr.au.int','juris.ohchr.org','docs.un.org','courts.go.jp','cons.judicial.gov.tw','supreme.court.gov.il','elibrary.judiciary.gov.ph','icj-cij.org','normlex.ilo.org','ilo.org','elitigation.sg','mkri.id','corteconstitucional.gov.co','ccourt.go.kr','legalref.judiciary.hk','kehakiman.gov.my','acerwc.africa','african-court.org','scjn.gob.mx','portal.stf.jus.br','stf.jus.br','hcourt.gov.au','supremecourt.uk','doj.gov.hk','sci.gov.in','tribunalconstitucional.gob.do','supremecourt.gov.pk','eng.scourt.go.kr','courtecowas.org','decisions.fca-caf.gc.ca','supremecourt.or.th','tribunalconstitucional.cl','scc-csc.lexum.com','oas.org','repositorio.mpd.gov.ar','refworld.org','supremecourt.gov.bd'}
LEGALDB={'saflii.org','indiankanoon.org','hklii.hk','lawphil.net','canlii.org','commonlii.org','austlii.edu.au','nzlii.org','bailii.org','supreme.justia.com','kenyalaw.org','paclii.org','worldlii.org','versa.cardozo.yu.edu'}
def kind(h): return 'official' if h in OFFICIAL else 'legaldb' if h in LEGALDB else 'report'
def host(u):
    h=re.sub(r'^https?://','',u).split('/')[0].split('#')[0].lower()
    if h.startswith('www.'): h=h[4:]
    if h.startswith('new.'): h=h[4:]
    for k in DB:
        if h==k or h.endswith('.'+k): return k
    return h

def generic(u):
    p=re.sub(r'^https?://','',u).rstrip('/').split('/')
    return len(p)<=1 or (len(p)==2 and '?' not in u and '#' not in u and len(p[1])<12) or (len(p)==3 and p[1] in('caselaw','en','gd') and not p[2])

def direct(d):
    c=d.get('cite',''); n=d['name']; cc=d['cc']; out=[]
    m=re.search(r'\[(\d{4})\]\s*(ZACC|ZASCA|ZAGPPHC|ZAWCHC|ZALAC|ZALCJHB)\s*(\d+)',c)
    if m: out.append(('Judgment (SAFLII)','https://www.saflii.org/za/cases/%s/%s/%s.html'%(m[2],m[1],m[3])))
    m=re.search(r'\[(\d{4})\]\s*HCA\s*(\d+)',c)
    if m: out.append(('Judgment (AustLII)','https://www.austlii.edu.au/cgi-bin/viewdoc/au/cases/cth/HCA/%s/%s.html'%(m[1],m[2])))
    m=re.search(r'\[(\d{4})\]\s*NZSC\s*(\d+)',c)
    if m: out.append(('Judgment (NZLII)','https://www.nzlii.org/nz/cases/NZSC/%s/%s.html'%(m[1],m[2])))
    m=re.search(r'\[(\d{4})\]\s*UKSC\s*(\d+)',c)
    if m: out.append(('Judgment (BAILII)','https://www.bailii.org/uk/cases/UKSC/%s/%s.html'%(m[1],m[2])))
    m=re.search(r'\[(\d{4})\]\s*HKCFA\s*(\d+)',c)
    if m: out.append(('Judgment (HKLII)','https://www.hklii.hk/en/cases/hkcfa/%s/%s'%(m[1],m[2])))
    m=re.search(r'(\d{4})\s*(SCC|FCA)\s*(\d+)',c)
    if m: out.append(('Judgment (CanLII)','https://www.canlii.org/en/ca/%s/doc/%s/%s%s%s/%s%s%s.html'%(m[2].lower(),m[1],m[1],m[2].lower(),m[3],m[1],m[2].lower(),m[3])))
    m=re.search(r'^(\d+)\s+U\.S\.\s+(\d+)',c)
    if m: out.append(('Opinion (Justia)','https://supreme.justia.com/cases/federal/us/%s/%s/'%(m[1],m[2])))
    m=re.search(r'(CCPR|CEDAW|CERD|CAT|CRC|CESCR)/C/[\w./]+',c)
    if m: out.append(('Views (UN Official Document System)','https://docs.un.org/en/'+m[0]))
    m=re.search(r'Series C No\.\s*(\d+)',c)
    if m: out.append(('Judgment (Inter-American Court)','https://www.corteidh.or.cr/docs/casos/articulos/seriec_%s_ing.pdf'%m[1]))
    m=re.search(r'OC-(\d+)/',c)
    if m and not out: out.append(('Opinion (Inter-American Court)','https://www.corteidh.or.cr/docs/opiniones/seriea_%s_esp.pdf'%m[1]))
    m=re.findall(r'(\d{3,6}/\d{2})',c) if ('App.' in c or 'European Court of Human Rights' in d['court']) else []
    if m: out.append(('Judgment (HUDOC)','https://hudoc.echr.coe.int/eng#{%22appno%22:[%22'+m[0]+'%22]}'))
    m=re.search(r'\[(\d{4})\]\s*(SGHC|SGCA)\s*(\d+)',c)
    if m: out.append(('Judgment (Singapore Courts)','https://www.elitigation.sg/gd/s/%s_%s_%s'%(m[1],m[2],m[3])))
    m=re.search(r'G\.R\. No\.\s*(\d+)$',c.strip())
    if m and cc=='PH' and re.match(r'\d{4}-\d{2}-\d{2}$',d.get('date','')):
        y,mo,_=d['date'].split('-'); mon=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'][int(mo)-1]
        out.append(('Judgment (Lawphil)','https://lawphil.net/judjuris/juri%s/%s%s/gr_%s_%s.html'%(y,mon,y,m[1],y)))
    m=re.search(r'^(RE|ADPF|ADI|HC)\s*([\d.]+)',c)
    if m and cc=='BR': out.append(('Case file (STF)','https://portal.stf.jus.br/processos/listarProcessos.asp?classe=%s&numeroProcesso=%s'%(m[1],m[2].replace('.',''))))
    m=re.search(r'\[(\d{4})\]\s*\d\s*SCR\s*\d+',c)
    if m and cc=='CA': out.append(('Supreme Court of Canada (search)','https://scc-csc.lexum.com/scc-csc/en/d/s/index.do?cont='+_q(n.split(' v. ')[-1].split(' (')[0])))
    if out: return out
    # Case-specific searches where no stable URL can be built from the citation.
    short=_q(n.split(' (')[0])
    if cc=='IN': return [('Indian Kanoon (search)','https://indiankanoon.org/search/?formInput='+short)]
    if cc=='HK':
        f=re.search(r'(FACV|FACC|CACV|HCAL|DCCC)\s*(\d+)/(\d{4})',c)
        q='%s %s/%s'%(f[1],f[2],f[3]) if f else n.split(' (')[0]
        return [('HKLII (search)','https://www.hklii.hk/en/search?query='+quote_plus(q))]
    if cc=='KE': return [('Kenya Law (search)','https://new.kenyalaw.org/search/?q='+short)]
    if cc in('BW','ZW','PG'): return [('CommonLII / PacLII (search)','https://www.commonlii.org/cgi-bin/sinosrch.cgi?method=auto&meta=%2Fcommonlii&query='+short)]
    if cc=='PK': return [('CommonLII (search)','https://www.commonlii.org/cgi-bin/sinosrch.cgi?method=auto&meta=%2Fcommonlii&query='+short)]
    return []

def apply(D):
    n=0
    for d in D:
        if all(generic(u) for _,u in d['src']):
            add=direct(d)
            if add:
                d['src']=add+[(DB.get(host(u),(host(u),''))[0]+' (front page)',u) for t,u in d['src']]; d['_built']=True; n+=1
    return n
