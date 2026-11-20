# Applies Pranoto's approved Indonesian (Google Doc "theimr.org – terjemahan bahasa Indonesia, versi baru", 2026-11-17)
# to /assets/lang.js and /legal-clinic/i18n.js. Run AFTER apply_guide.py. Idempotent.
# Usage: python3 apply_v2.py SITE   (reads docrows.json beside this script: en -> final)
import sys, os, re, json
HERE = os.path.dirname(os.path.abspath(__file__)); SITE = sys.argv[1]
J = lambda x: json.dumps(x, ensure_ascii=False)
rows = json.load(open(os.path.join(HERE, 'docrows.json'), encoding='utf-8'))
sys.path.insert(0, HERE); from newid import SITPAIR
NAME_OLD, NAME_NEW = 'Yurisprudensi Migrasi dari Selatan', 'Pandangan Hukum Migrasi dari Dunia Berkembang'
STR = r'"(?:[^"\\]|\\.)*"'
# Pranoto's doc writes lowercase 'anda' mid-sentence (2026-11-17)
ANDA = re.compile(r'(?<=[a-z0-9,;)\]] )Anda\b')
MO = 'Yang paling sering muncul: %s, serta %s'

CLIN = open(os.path.join(SITE, 'legal-clinic/i18n.js'), encoding='utf-8').read()
def patch(path, prefix):
    s = open(path, encoding='utf-8').read(); o = s; n = 0
    m = {}
    for r in rows:
        en, fi = r['en'], r['final']
        if en.startswith('Most often:') or en == 'English': continue
        m[en] = fi
    for a in SITPAIR:
        for b in SITPAIR:
            if a != b: m['Most often: %s, %s' % (a, b)] = MO % (SITPAIR[a], SITPAIR[b])
    # patterns: rewrite replacement of any __pat whose regex matches a doc row
    pats = re.findall(r'\[(%s),(%s)\]' % (STR, STR), s)
    for pre, prep in pats:
        rx = json.loads(pre); rx_py = rx
        for r in rows:
            g = re.match(rx_py, r['en'])
            if not g or r['en'].startswith('Most often:'): continue
            new = r['final']
            for i, v in enumerate(g.groups(), 1): new = new.replace(v, '$%d' % i, 1)
            if J(new) != prep:
                s = s.replace('[%s,%s]' % (pre, prep), '[%s,%s]' % (pre, J(new)), 1); n += 1
            m.pop(r['en'], None)
            break
    add = ''
    for en, fi in m.items():
        k = J(en) + ':'
        if k in s:
            s2 = re.sub(re.escape(k) + STR, lambda _: k + J(fi), s)
            if s2 != s: s = s2; n += 1
        elif prefix and J(en) + ':' not in CLIN and en[:1] and not re.match(r'^\d', en):
            add += k + J(fi) + ','
    if add and prefix:
        s = s.replace(prefix, prefix + add, 1); n += add.count('":"')
    s = s.replace(NAME_OLD, NAME_NEW).replace(NAME_OLD.upper(), NAME_NEW.upper())  # UPPER
    s = ANDA.sub('anda', s)
    if s != o: open(path, 'w', encoding='utf-8').write(s)
    return n

print('lang.js', patch(os.path.join(SITE, 'assets/lang.js'), 'window.SITE_I18N={"id":{'))
print('clinic', patch(os.path.join(SITE, 'legal-clinic/i18n.js'), None))
for p in ['court-decisions/cd-i18n.js', 'court-decisions/cd.js', 'legal-clinic/trafficking-check/index.html']:
    f = os.path.join(SITE, p)
    if os.path.exists(f):
        t = open(f, encoding='utf-8').read()
        t2 = ANDA.sub('anda', t.replace(NAME_OLD, NAME_NEW).replace(NAME_OLD.upper(), NAME_NEW.upper()))
        if t2 != t: open(f, 'w', encoding='utf-8').write(t2); print('name/anda ->', p)
