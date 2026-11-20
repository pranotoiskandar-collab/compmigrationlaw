# Builds the live homepage in model F (Pranoto chose it 2026-11-16). Usage: python3 home_f.py SITE
# Keeps the homepage's <head> (title, meta, JSON-LD, analytics) and footer; replaces header + body with model F.
import os, re, sys, runpy, tempfile
SITE = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(SITE, 'index.html'); src = open(P, encoding='utf-8').read()
if 'data-home="f"' in src: print('home already model F'); sys.exit()
sys.argv = [sys.argv[0], SITE, tempfile.mkdtemp()]
G = runpy.run_path(os.path.join(HERE, 'models3.py'), run_name='models3')
M = G['G']['G']  # models.py globals
sys.path.insert(0, HERE); import masthead
head = src[:src.index('</head>')]
head = re.sub(r'<style>\nhtml\{scroll-behavior:smooth\}.*?</style>\n', '', head, flags=re.S)
head = re.sub(r'<style>html\{scroll-behavior:smooth\}\.wrap\{[^<]*</style>\n', '', head)
head += '<style>html{scroll-behavior:smooth}' + M['CSS'] + G['G']['EXTRA'] + '</style>\n'
body = G['body'].replace('<style>' + G['G']['EXTRA'] + '</style>', '')
# keep the old section ids that people may have bookmarked
body = body.replace('<h2>Ideas from the fields</h2>', '<h2 id="ideas">Ideas from the fields</h2>').replace('<h3 style="margin:0;font-size:20px">In the news</h3>', '<h3 id="news" style="margin:0;font-size:20px">In the news</h3>')
body = body.replace('<section class="clinic band">', '<section id="clinic-cta" class="clinic band">')
out = (head + '</head>\n<body data-home="f">\n<div>\n' + M['bentham'] + masthead.new_header(M['nav']) + '\n' + body + '\n' + M['tail'])
out = masthead.add_link(out)
open(P, 'w', encoding='utf-8').write(out)
print('homepage is now model F', len(out))
