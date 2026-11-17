import re,json,sys
sys.path.insert(0,'build'); from tr import T
from html.parser import HTMLParser
ea=open('/mnt/project-files/theimr-site/east-asia/ea-i18n.js').read()
lang=open('/mnt/project-files/theimr-site/assets/lang.js').read()
EA=dict(re.findall(r'^("(?:[^"\\]|\\.)*"): ("(?:[^"\\]|\\.)*"),?$', ea, re.M))
class P(HTMLParser):
    def __init__(s): super().__init__(); s.k=[]
    def handle_data(s,d):
        d=re.sub(r'\s+',' ',d).strip()
        if d and not re.fullmatch(r'[\W\d]*',d) and d not in s.k: s.k.append(d)
p=P(); p.feed(open('build/main.html').read())
out={}; miss=[]
for k in p.k:
    q=json.dumps(k,ensure_ascii=False)
    if q+':' in lang: continue
    if k in T: out[k]=T[k]
    elif q in EA: out[k]=json.loads(EA[q])
    else: miss.append(k)
out["Countries of Origin"]=T["Countries of Origin"]
print("missing",miss)
body=",\n".join(json.dumps(k,ensure_ascii=False)+": "+json.dumps(v,ensure_ascii=False) for k,v in out.items())
tail=ea[ea.index('};')+2:]
open('out/oc-i18n.js','w').write("/* Indonesian strings for the Countries of origin page. Loaded just before /assets/lang.js: the dictionary that lang.js assigns\n   to window.SITE_I18N is extended at the moment it is assigned, so lang.js itself needs no change. */\n(function () {\n  var A = {\n"+body+"\n};"+tail)
print(len(out))
