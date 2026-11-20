"""Build site/volunteer/index.html and site/volunteer/thanks.html.

Reuses the header, menu and footer of site/contact.html so the page matches
the rest of the site. The sign-up form is a Netlify form named
"volunteer-signup", kept separate from the Legal Clinic form ("clinic-intake").

    python3 build/volunteer-build/volunteer_page.py
    python3 build/newspaper-build/puncak_green.py site   # turns the page green
"""
import pathlib, re

root = pathlib.Path(__file__).resolve().parents[2]
site = root / "site"
src = (site / "contact.html").read_text(encoding="utf-8").split("\n")
i_head_end = next(i for i, l in enumerate(src) if l.startswith("</header>"))
i_ridge = next(i for i, l in enumerate(src) if 'class="imr-ridge"' in l)
top = "\n".join(src[: i_head_end + 1])
bottom = "\n".join(src[i_ridge:])
for rel in ["apple-touch-icon.png", "favicon-32.png", "favicon.ico", "contact.html", "people.html", "publications.html"]:
    top = top.replace(f'href="{rel}"', f'href="/{rel}"')

DESC = "Volunteer with the Institute for Migrant Rights: spread the word, translate, research migration law, or work on data and code. Sign up and we reply with a first task."

def page(title, desc, url, body, noindex=False):
    t = top
    t = re.sub(r"<title>.*?</title>", f"<title>{title} · Institute for Migrant Rights</title>", t)
    t = re.sub(r'(<meta name="description" content=")[^"]*', r"\g<1>" + desc, t)
    t = re.sub(r'(<meta property="og:description" content=")[^"]*', r"\g<1>" + desc, t)
    t = re.sub(r'(<meta property="og:title" content=")[^"]*', r"\g<1>" + f"{title} · Institute for Migrant Rights", t)
    t = t.replace("https://theimr.org/contact.html", url)
    if noindex:
        t = t.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"', 1)
    return t + "\n" + body + "\n" + bottom

CSS = """<style>
.vol{max-width:760px;margin:0 auto;padding:0 24px}
.vol h2{font-weight:500;font-size:30px;line-height:1.2;margin:56px 0 12px}
.vol .kick{margin:0;font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:#8F5E12}
.vol .lede{color:#4A3B2D}
.lvls{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:14px;margin:20px 0 0;padding:0;list-style:none}
.lvls li{background:#FFFFFF;border:1px solid #C8BCB1;padding:16px 18px;font-size:16px;line-height:1.5}
.lvls b{display:block;font-weight:600;font-size:17px;margin-bottom:4px}
.vform{display:grid;gap:20px;margin-top:20px}
.vform label,.vform legend{font-weight:600;font-size:16px}
.vform small{display:block;font-weight:400;color:#5B4A3C;font-size:14px}
.vform input[type=text],.vform input[type=email],.vform select,.vform textarea{display:block;width:100%;box-sizing:border-box;margin-top:6px;padding:11px 12px;font:inherit;font-size:17px;border:1px solid #A89A8C;background:#FFFFFF;color:#2E2116;border-radius:2px}
.vform textarea{min-height:96px}
.vform fieldset{border:0;margin:0;padding:0}
.vform .opt{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:16px;margin-top:10px}
.vform .opt input{margin-top:5px;width:18px;height:18px;flex:none}
.vform button{justify-self:start;padding:13px 26px;font:600 17px 'Figtree',sans-serif;background:#8F5E12;color:#FFFFFF;border:0;border-radius:2px;cursor:pointer}
.vform button:hover{background:#6B450B}
.vnote{background:#E8E2DC;border-left:3px solid #8F5E12;padding:14px 18px;font-size:16px;margin-top:28px}
.vhide{position:absolute;left:-9999px}
</style>"""

BODY = CSS + """
<section style="padding: 88px 0 80px">
<div class="vol">
<p class="kick">Volunteer</p>
<h1 style="margin: 16px 0 0; font-weight: 400; font-size: 54px; line-height: 1.1">Work with us</h1>
<p class="lede" style="margin: 18px 0 0">IMR is a small team. Volunteers help us collect, check and translate migration law so that migrant workers and the people who help them can use it. Tell us what you can do, and we will reply with a first task that fits.</p>

<h2>Four ways to help</h2>
<ul class="lvls">
<li><b>1. Spread and spot</b>Share our pages, report a broken link, flag a new law or court ruling you read about. Ten minutes at a time.</li>
<li><b>2. Translate and review</b>Check our Indonesian, Arabic, Bengali, Dari, Nepali, Tagalog or Vietnamese pages, or start a new language. A second speaker checks every translation.</li>
<li><b>3. Legal research</b>Find the official text of a judgment or law, confirm the details, and record the link. Law students and lawyers welcome.</li>
<li><b>4. Data and code</b>Second coding of our law codings (Cohen's kappa), data checks, scrapers for court websites, and statistics.</li>
</ul>

<h2>Sign up</h2>
<p class="lede" style="margin:0">It takes about three minutes. We reply by email within two weeks.</p>
<form class="vform" name="volunteer-signup" method="POST" action="/volunteer/thanks.html" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="volunteer-signup">
<p class="vhide"><label>Leave this empty <input name="bot-field"></label></p>
<label>Your name<input type="text" name="name" required autocomplete="name"></label>
<label>Email<input type="email" name="email" required autocomplete="email"></label>
<label>Where you live<small>City and country</small><input type="text" name="location"></label>
<label>Languages you read well<small>For example: Tagalog (native), Spanish (fluent), Arabic (reading only)</small><input type="text" name="languages" required></label>
<fieldset><legend>What would you like to do?<small>Tick all that apply</small></legend>
<label class="opt"><input type="checkbox" name="level_spread" value="yes">Spread the word and spot problems</label>
<label class="opt"><input type="checkbox" name="level_translate" value="yes">Translate and review</label>
<label class="opt"><input type="checkbox" name="level_research" value="yes">Legal research</label>
<label class="opt"><input type="checkbox" name="level_data" value="yes">Data and code</label>
</fieldset>
<label>Time you can give<select name="time"><option value="">Choose one</option><option>About 1 hour a week</option><option>2 to 5 hours a week</option><option>More than 5 hours a week</option><option>A one-off task</option></select></label>
<label>Background<small>Study, work or skills that may help (law school, coding, statistics, community work)</small><textarea name="background"></textarea></label>
<label>University or organization<small>Optional. Tell us if you need credit or a supervisor's letter.</small><input type="text" name="organization"></label>
<label>How did you hear about us?<input type="text" name="heard"></label>
<fieldset><legend>Agreements</legend>
<label class="opt"><input type="checkbox" name="confidentiality" value="agreed" required>I understand that volunteers do not see Legal Clinic submissions or any personal information about people who ask IMR for help, and I will not ask to.</label>
<label class="opt"><input type="checkbox" name="credit" value="yes">You may credit me by name on the website when my work is published.</label>
</fieldset>
<button type="submit">Send</button>
</form>
<p class="vnote">Need legal help yourself? Volunteers cannot give legal advice. Please use the <a href="/legal-clinic/">Legal Clinic</a> or <a href="/legal-help/">find free legal help</a> near you.</p>
<p style="margin-top:28px;font-size:16px;color:#4A3B2D">Already working with us? The starter kit, task packs and translation glossary are on <a href="https://github.com/pranotoiskandar-collab/compmigrationlaw/tree/main/volunteers">GitHub</a>. Questions: <a href="mailto:secretariat@theimr.org?subject=Volunteer">secretariat@theimr.org</a>.</p>
</div>
</section>
"""

THANKS = """
<section style="padding: 112px 24px; text-align: center">
<p style="margin: 0; font-size: 13px; letter-spacing: 0.18em; text-transform: uppercase; color: #8F5E12">Volunteer</p>
<h1 style="margin: 16px 0 0; font-weight: 400; font-size: 48px; line-height: 1.1">Thank you for signing up</h1>
<p style="margin: 18px auto 0; max-width: 560px; color: #4A3B2D">We will write within two weeks with a first task that fits what you told us. In the meantime you can look at the <a href="https://github.com/pranotoiskandar-collab/compmigrationlaw/tree/main/volunteers">volunteer starter kit</a>.</p>
<p style="margin: 28px 0 0; font-size: 15px; font-weight: 600"><a href="/databases/">Our databases</a> · <a href="/">Home</a></p>
</section>
"""

out = site / "volunteer"
out.mkdir(exist_ok=True)
(out / "index.html").write_text(page("Volunteer", DESC, "https://theimr.org/volunteer/", BODY), encoding="utf-8")
(out / "thanks.html").write_text(page("Thank you", DESC, "https://theimr.org/volunteer/thanks.html", THANKS, noindex=True), encoding="utf-8")
print("wrote", out / "index.html", out / "thanks.html")
