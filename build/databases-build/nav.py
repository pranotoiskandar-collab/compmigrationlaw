# Adds "All databases" (/databases/) as the first item of both menus on every page, and a homepage link. Safe to rerun.
import glob
SITE = '/mnt/project-files/theimr-site'
A1 = '<div class="menu">\n<a href="/migration-law/">Migration Law Atlas</a>'
A2 = '<div class="menu">\n<a href="/gcc/">Gulf States</a>'
ITEM = '<a href="/databases/" style="font-weight:600">All databases</a>\n'
n = 0
for p in glob.glob(SITE + '/**/*.html', recursive=True):
    s = open(p, encoding='utf-8').read()
    if 'href="/databases/" style="font-weight:600"' in s: continue
    o = s
    s = s.replace(A1, '<div class="menu">\n' + ITEM + A1[len('<div class="menu">\n'):])
    s = s.replace(A2, '<div class="menu">\n' + ITEM + A2[len('<div class="menu">\n'):])
    if s != o: open(p, 'w', encoding='utf-8').write(s); n += 1
print('nav updated on', n, 'pages')
h = SITE + '/index.html'; s = open(h, encoding='utf-8').read()
a = '<p style="font-weight: 600"><a href="#projects">Explore our projects</a></p>'
if '/databases/">All databases and a welcoming remark' not in s and a in s:
    s = s.replace(a, '<p style="font-weight: 600"><a href="#projects">Explore our projects</a> · <a href="/databases/">All databases and a welcoming remark</a></p>')
    open(h, 'w', encoding='utf-8').write(s); print('homepage link added')
print('done')
