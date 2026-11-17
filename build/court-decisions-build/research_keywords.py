# Adds a visible "For researchers" block, meta keywords and JSON-LD keywords to IMR data pages (idempotent).
import re,json
SITE='/mnt/project-files/theimr-site'
COMMON=['empirical legal studies','empirical legal scholarship','quantitative legal research','statistical analysis in law','law and economics','law and economics of migration','comparative law','socio-legal studies','legal pluralism','migration law','labor migration','migrant workers’ rights','human rights law','access to justice','Global South','Asia','Africa','Middle East','Latin America','Indonesia','open data','replication data']
PAGES={
 'court-decisions/index.html':('decision set',['case law','jurisprudence','judicial decisions','comparative constitutional law','courts and migration','judicial behavior','litigation outcomes','refugee law','non-refoulement','citizenship and nationality']),
 'migration-law/index.html':('atlas',['treaty ratification','international law compliance','legal indicators','regional integration','legal origins']),
 'atlas/index.html':('atlas',['agricultural labor','farmworkers','ILO conventions','treaty ratification','legal indicators']),
 'gcc/index.html':('comparison',['Gulf states','kafala','labor market regulation','labor mobility','wage protection','recruitment fees']),
 'gcc/mechanisms/index.html':('comparison',['Gulf states','dispute resolution','labor courts','wage protection']),
 'east-asia/index.html':('comparison',['East Asia','Taiwan','South Korea','Hong Kong','Japan','temporary labor migration programs','labor mobility','migrant fishers','domestic workers']),
 'east-asia/mechanisms/index.html':('comparison',['East Asia','dispute resolution','labor inspection','complaint mechanisms']),
 'countries-of-origin/index.html':('comparison',['emigration policy','countries of origin','recruitment regulation','remittances','diaspora policy','bilateral labor agreements']),
 'hate-speech-voting/index.html':('dataset',['hate speech','political behavior','voting','anti-immigration parties','regression analysis','constitutional democracies','impunity']),
 'government-hate-speech/index.html':('project',['hate speech','officials and politicians','criminal law','freedom of expression','impunity']),
 'legal-help/index.html':('directory',['legal aid','access to justice','legal services','legal needs']),
}
EN={'decision set':'This collection of decisions','atlas':'This atlas','comparison':'This comparison','dataset':'This dataset','project':'This project','directory':'This directory'}
ID={'decision set':'Koleksi putusan ini','atlas':'Atlas ini','comparison':'Perbandingan ini','dataset':'Dataset ini','project':'Proyek ini','directory':'Direktori ini'}
I18N={}
for f,(kind,extra) in PAGES.items():
    p=SITE+'/'+f; s=open(p).read()
    kw=extra+COMMON
    s=re.sub(r'\n?<section id="imr-research".*?</section>\n?','\n',s,flags=re.S)
    s=re.sub(r'<meta name="keywords"[^>]*>\n?','',s)
    s=s.replace('<meta name="description"','<meta name="keywords" content="%s">\n<meta name="description"'%', '.join(kw),1)
    def addkw(m):
        try: j=json.loads(m.group(1))
        except Exception: return m.group(0)
        if isinstance(j,dict) and j.get('@type')=='Dataset':
            old=j.get('keywords',[]); old=old if isinstance(old,list) else [x.strip() for x in str(old).split(',')]
            j['keywords']=list(dict.fromkeys(old+kw))
        return '<script type="application/ld+json">%s</script>'%json.dumps(j,ensure_ascii=False)
    s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',addkw,s,flags=re.S)
    p1='%s is built for empirical legal scholarship and socio-legal research on migration and the rights of migrant workers, as well as for advocacy.'%EN[kind]
    p2='The coded variables support statistical analysis in law: cross-national comparison, regression and event-history designs, and law and economics questions such as how recruitment fees, wage protection and limits on changing employer affect migrant workers. The data can be downloaded for replication.'
    k1='Keywords: '+'; '.join(kw)+'.'
    I18N[p1]='%s disusun untuk penelitian hukum empiris dan sosio-legal tentang migrasi dan hak pekerja migran, serta untuk advokasi.'%ID[kind]
    I18N[p2]='Variabel yang dikodekan mendukung analisis statistik dalam hukum: perbandingan lintas negara, desain regresi dan analisis riwayat peristiwa, serta pertanyaan hukum dan ekonomi seperti bagaimana biaya perekrutan, perlindungan upah dan pembatasan pindah majikan memengaruhi pekerja migran. Data bisa diunduh untuk replikasi.'
    I18N['For researchers']='Untuk peneliti'
    sec=('<section id="imr-research" style="max-width:1120px;margin:0 auto;padding:28px 24px 36px;font-family:\'Familjen Grotesk\',system-ui,sans-serif;color:#172D24;border-top:1px solid #B2C7BC">'
         '<h2 style="font-size:18px;margin:0 0 8px">For researchers</h2><p style="margin:0 0 8px;max-width:760px">%s</p><p style="margin:0 0 8px;max-width:760px">%s</p>'
         '<p style="margin:0;max-width:760px;font-size:13px;color:#3D5A4C">%s</p></section>\n')%(p1,p2,k1)
    if '<footer' in s: s=s.replace('<footer',sec+'<footer',1)
    else: k=s.rfind('</body>'); s=s[:k]+sec+s[k:]
    open(p,'w').write(s)
# Indonesian strings for lang.js (keywords line left in English, as a list of search terms)
L=SITE+'/assets/lang.js'; s=open(L).read()
j=s.index('{"id":{')+len('{"id":{')
add=''.join('%s:%s,'%(json.dumps(k,ensure_ascii=False),json.dumps(v,ensure_ascii=False)) for k,v in I18N.items() if json.dumps(k,ensure_ascii=False)+':' not in s)
s=s[:j]+add+s[j:]; open(L,'w').write(s)
print(len(PAGES),'pages;',len(I18N),'strings')
