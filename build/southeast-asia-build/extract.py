import re,json,sys,html
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s): super().__init__(); s.stack=[]; s.out=[]
    def handle_starttag(s,t,a):
        if t in ('br','input','img','meta','link'): return
        s.stack.append(any(k=='data-noi18n' for k,v in a) or t in('script','style'))
    def handle_endtag(s,t):
        if t in ('br','input','img','meta','link'): return
        if s.stack: s.stack.pop()
    def handle_data(s,d):
        if any(s.stack): return
        t=re.sub(r'\s+',' ',d).strip()
        if t and re.search('[A-Za-z]',t): s.out.append(t)
p=P();p.feed(open(sys.argv[1]).read())
seen=[];[seen.append(x) for x in p.out if x not in seen]
json.dump(seen,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
print(len(seen))
