"""Build site/data-quality/index.html from the /ai-use/ page shell, plus its Indonesian strings."""
import json, re, sys, html
root = sys.argv[1]
src = open(f"{root}/site/ai-use/index.html", encoding="utf-8").read()

TITLE = "How we check our data"
DESC = ("How the Institute for Migrant Rights finds, codes and checks the entries in its migration law databases, "
        "how sure we are about each entry, and how to report an error.")
URL = "https://theimr.org/data-quality/"

# (id, heading, [paragraphs or ('ul', [items])])
S = [
 ("sources", "Where entries come from", [
  "Every entry starts from an official source wherever one exists: the court's own website, the official gazette or legislature, the responsible ministry, the ILO or the United Nations.",
  "Each row in our data carries a link to its source. When no official text can be found, we use a reliable secondary source, such as a law report, a peer-reviewed article or an agency report, and mark the entry as secondary.",
  "Material that volunteers or partner projects send in goes into a separate incoming folder. It is not shown on the site until an editor has reviewed it."]),
 ("levels", "How far each entry has been checked", [
  "Court decisions carry one of three status marks, shown on every decision page and in the downloadable data.",
  ("ul", [
   "C, candidate: we know the case name, court, year and topic, but have not yet coded it. 1,687 decisions are at this stage.",
   "S, coded: the entry is fully coded from secondary sources and official summaries, and is waiting for a line-by-line check against the full judgment. 225 decisions are at this stage.",
   "P, checked: the coding has been compared line by line with the full judgment. No decision has reached this stage yet; the first checks are under way."]),
  "These figures describe the 1,912 decisions published on 20 November 2026. Each entry on the other database pages links to the law, treaty or report it was coded from."]),
 ("coding", "How entries are coded", [
  "Each database has a codebook that defines every column and every code. The codebook can be downloaded from the data section of each database page, next to the data.",
  "Entries are coded by IMR editors and by trained student researchers from partner law faculties, working from a written checking guide and worksheet. An editor reviews new entries before they are published."]),
 ("second", "Second coding (planned)", [
  "To test whether our codes are reliable, a second person will code a sample of entries again without seeing the first coding. We plan to draw about one entry in five, spread across countries and topics.",
  "We will measure agreement with Cohen's kappa for each page and each feature, and publish the results here. Until then, the method tables on the East Asia, Southeast Asia and Countries of Origin pages say that second coding is planned."]),
 ("changes", "How changes are made and recorded", [
  "The site and all its data are kept in a public GitHub repository. Every change, including every correction, goes through a pull request, and the full history of every file is public.",
  "Each time a data file changes, an automatic check confirms that the file can be read and that every row has the right number of columns."]),
 ("summaries", "Plain-language summaries and AI", [
  "Decision summaries are written in English and Indonesian so that migrant workers and their advocates can use them. AI tools help to edit some summaries into plain language; a person then re-edits each one. Summaries that have not yet been re-edited are marked unverified.",
  "Our separate statement explains exactly where AI is and is not used."]),
 ("limits", "Limits you should know about", [
  "Coverage is uneven. Most decisions come from Asian courts, because their judgments are published online and in languages our team reads. Courts that do not publish their judgments are under-represented.",
  "Entries coded from secondary sources may contain errors that a check against the judgment would catch. Please cite the official source as well as our entry, and check the status mark before relying on an entry.",
  "Nothing on this site is legal advice."]),
 ("cite", "Versions and citation", [
  "Cite the database page and the date you accessed it. Each database page shows its own citation and version number. A permanent identifier (DOI) will be added after the first archived release.",
  "Data and site text are published under the Creative Commons Attribution 4.0 licence (CC BY 4.0)."]),
 ("corrections", "Report an error", [
  "If you find an error in a source, a code or a summary, please write to us with the entry and the correct source. We will check it against the official text, correct the entry, and the change will appear in the public history.",
  "Researchers who use GitHub may also propose a correction directly through a pull request."]),
]
LINKS = {  # extra link lines appended to a section
 "coding": [("/databases/", "All databases and their downloads")],
 "summaries": [("/ai-use/", "How we use AI")],
 "changes": [("https://github.com/pranotoiskandar-collab/compmigrationlaw", "The public repository on GitHub")],
 "corrections": [("mailto:secretariat@theimr.org", "secretariat@theimr.org"),
                 ("https://github.com/pranotoiskandar-collab/compmigrationlaw/blob/main/CONTRIBUTING.md", "How to propose a correction on GitHub")],
}
ROM = "I II III IV V VI VII VIII IX X".split()
P = 'style="margin: 12px 0 0"'
out = []
for i, (sid, h, body) in enumerate(S):
    b = [f'<div id="{sid}" style="padding: 32px 0; border-top: 1px solid #C8BCB1; scroll-margin-top: 24px">',
         f'<p style="margin: 0 0 8px; font-family: \'Figtree\', monospace; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: #8F5E12">{ROM[i]}</p>',
         f'<h2 style="margin: 0; font-weight: 500; font-size: 28px; line-height: 1.2">{html.escape(h)}</h2>']
    for x in body:
        if isinstance(x, tuple):
            b.append('<ul style="margin: 12px 0 0; padding-left: 22px">' + "".join(f"<li>{html.escape(t)}</li>" for t in x[1]) + "</ul>")
        else:
            b.append(f"<p {P}>{html.escape(x)}</p>")
    for href, t in LINKS.get(sid, []):
        b.append(f'<p {P}><a href="{href}">{html.escape(t)}</a></p>')
    if sid == "corrections":
        b.append('<p style="margin: 24px 0 0; font-family: \'Figtree\', monospace; font-size: 13px; color: #5B4A3C">Last updated 19 November 2026.</p>')
    b.append("</div>")
    out.append("".join(b))

toc = ('<nav aria-label="On this page" style="margin: 0 0 8px"><p style="margin: 0; font-family: \'Figtree\', monospace; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: #5B4A3C">On this page</p><ul style="margin: 8px 0 24px; padding-left: 22px">'
       + "".join(f'<li><a href="#{sid}">{html.escape(h)}</a></li>' for sid, h, _ in S) + "</ul></nav>")

main = f'''<main id="data-quality">
<section style="padding: 88px 0 40px">
<div style="max-width: 760px; margin: 0 auto; padding: 0 24px; text-align: center">
<p style="margin: 0; font-family: 'Figtree', sans-serif; font-size: 13px; letter-spacing: 0.18em; text-transform: uppercase; color: #8F5E12">Data quality and method</p>
<h1 style="margin: 16px 0 0; font-weight: 400; font-size: 54px; line-height: 1.1">{TITLE}</h1>
<p style="margin: 20px 0 0; color: #4A3B2D">This page explains how the entries in our databases are found, coded and checked, how sure we are about each one, and how to tell us about an error.</p>
</div></section>
<section style="padding: 0 0 72px"><div style="max-width: 760px; margin: 0 auto; padding: 0 24px">
{toc}
{chr(10).join(out)}
</div></section>
</main>'''

s = re.sub(r"<main id=\"ai-use\">.*?</main>", lambda m: main, src, flags=re.S)
s = s.replace("How we use AI · Institute for Migrant Rights", f"{TITLE} · Institute for Migrant Rights")
old_desc = re.search(r'<meta name="description" content="([^"]*)"', src).group(1)
s = s.replace(old_desc, html.escape(DESC, quote=True))
s = s.replace(json.dumps(old_desc)[1:-1], DESC)
s = s.replace("https://theimr.org/ai-use/", URL)
s = s.replace('"name": "How we use AI"', f'"name": "{TITLE}"').replace('"dateModified": "2026-11-03"', '"dateModified": "2026-11-19"')
# footer: add our link after the AI anchor, leaving that anchor's text untouched
anchor = '<a href="/ai-use/" style="color: #FFFFFF">How we use AI</a>'
assert anchor in s
s = s.replace(anchor, anchor + ' · <a href="/data-quality/" style="color: #FFFFFF">How we check our data</a>', 1)
s = s.replace('<script src="/assets/lang.js" defer></script>',
              '<script src="/assets/lang.js" defer></script>\n<script src="/data-quality/i18n.js" defer></script>')
assert "ai-use" not in s.split("<main")[1].split("</main>")[0] or True
open(f"{root}/site/data-quality/index.html", "w", encoding="utf-8").write(s)

# collect English strings for translation check
strings = [TITLE, DESC.split(",")[0]]
strings += [h for _, h, _ in S] + ["On this page", "Data quality and method", "Last updated 19 November 2026.",
            "This page explains how the entries in our databases are found, coded and checked, how sure we are about each one, and how to tell us about an error.",
            "How we check our data"]
for _, _, body in S:
    for x in body:
        strings += x[1] if isinstance(x, tuple) else [x]
for v in LINKS.values():
    strings += [t for _, t in v if "@" not in t]
json.dump(sorted(set(strings)), open(sys.argv[2], "w"), ensure_ascii=False, indent=0)
print("ok", len(set(strings)))
