"""Page shell for the feature pages (rights checklist, case of the month, ratification tracker, research tools).

shell-template.html is the header, menu and footer of the site in the Puncak green look (taken from
site/databases/index.html on the PR #19 branch), with placeholders. page() fills it in. Indonesian strings for
the static text go into a small script that extends window.SITE_I18N before /assets/lang.js runs, the same way
site/southeast-asia/sea-i18n.js does.
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, "site")

I18N_JS = """<script>(function(){var A=%s;function m(D){D.id=D.id||{};for(var k in A)if(!Object.prototype.hasOwnProperty.call(D.id,k))D.id[k]=A[k];return D}if(window.SITE_I18N){m(window.SITE_I18N);return}var c;try{Object.defineProperty(window,"SITE_I18N",{configurable:true,enumerable:true,get:function(){return c},set:function(v){c=m(v||{})}})}catch(e){window.SITE_I18N=m({})}})();</script>"""


# Menu entries added by these pages (Indonesian), merged into every page's dictionary.
NAV_ID = {
    "Know your rights before you go": "Kenali hak anda sebelum berangkat",
    "Use IMR without signal": "Pakai IMR tanpa sinyal",
    "Case of the month": "Putusan bulan ini",
    "Tools": "Alat",
    "Ratification tracker": "Pelacak ratifikasi",
    "Saved searches and reading list": "Pencarian tersimpan dan daftar bacaan",
}


def page(path, title, desc, main, head="", scripts="", i18n=None, out=None):
    t = open(os.path.join(HERE, "shell-template.html"), encoding="utf-8").read()
    full = title + " · Institute for Migrant Rights"
    t = (t.replace("{{TITLE}}", html.escape(full)).replace("{{DESC}}", html.escape(desc, quote=True))
          .replace("{{PATH}}", path).replace("{{HEAD}}", head).replace("{{MAIN}}", main))
    tail = ""
    i18n = dict(NAV_ID, **(i18n or {}))
    if i18n:
        tail += I18N_JS % json.dumps(i18n, ensure_ascii=False)
    t = t.replace("{{SCRIPTS}}", scripts)
    # the dictionary must be in place before lang.js runs
    t = t.replace('<script src="/assets/lang.js" defer></script>', tail + '\n<script src="/assets/lang.js" defer></script>')
    target = out or os.path.join(SITE, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(t)
    return target
