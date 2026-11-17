"""Add the Projects menu to the existing theimr.org pages.

Usage: python3 patch_nav.py SITE_FOLDER
Edits index.html, about.html, publications.html, people.html and contact.html in place.
Running it twice does nothing the second time.
"""
import sys, os, re

STYLE = """<style>
.nav details{position:relative}
.nav summary{cursor:pointer;padding:10px 0;list-style:none;color:#231C16;font-weight:600}
.nav summary::-webkit-details-marker{display:none}
.nav summary::after{content:" \\25BE";font-size:11px}
.nav .menu{position:absolute;right:0;top:100%;z-index:5;min-width:230px;background:#FBF8F2;border:1px solid #D8CDBB;padding:6px 0}
.nav .menu a{display:block;padding:8px 16px;color:#231C16;text-decoration:none}
.nav .menu a:hover{color:#6B3F1F}
@media (max-width:640px){.nav .menu{right:auto;left:0}}
</style>
"""
MENU = """<details>
<summary>Projects</summary>
<div class="menu">
<a href="/migration-law/">Migration Law Atlas</a>
<a href="/atlas/">Farmworker Norms Atlas</a>
<a href="/government-hate-speech/">Government Hate Speech</a>
</div>
</details>
<details>
<summary>Migration and Labor Laws in Comparison</summary>
<div class="menu">
<a href="/gcc/">Gulf States</a>
<a href="/east-asia/">East Asia</a>
<a href="/countries-of-origin/">Countries of Origin</a>
<a href="/hate-speech-voting/">Hate Speech and Voting</a>
<a href="/court-decisions/">Court Decisions</a>
</div>
</details>
"""
SCRIPT = """<script>
document.addEventListener('click', function (e) {
  document.querySelectorAll('.nav details[open]').forEach(function (d) { if (!d.contains(e.target)) d.removeAttribute('open'); });
});
</script>
"""
def patch(path):
    s = open(path, encoding='utf-8').read()
    if 'href="/migration-law/"' in s:
        return 'already done'
    nav_open = '<nav aria-label="Main" style="display: flex; flex-wrap: wrap; gap: 2px 22px">'
    if nav_open not in s:
        return 'nav not found, left unchanged'
    s = s.replace(nav_open, '<nav aria-label="Main" class="nav" style="display: flex; flex-wrap: wrap; align-items: center; gap: 2px 22px">', 1)
    # The menu goes after the About link, as on the Government Hate Speech page
    m = re.search(r'<a href="about\.html"[^>]*>(?:About &amp; )?Legal Clinic</a>\n', s)
    if not m:
        return 'About link not found, left unchanged'
    s = s[:m.end()] + MENU + s[m.end():]
    s = s.replace('</head>', STYLE + '</head>', 1).replace('</body>', SCRIPT + '</body>', 1)
    open(path, 'w', encoding='utf-8').write(s)
    return 'patched'

if __name__ == '__main__':
    root = sys.argv[1]
    for f in ['index.html', 'about.html', 'publications.html', 'people.html', 'contact.html']:
        p = os.path.join(root, f)
        print(f, patch(p) if os.path.exists(p) else 'missing')
