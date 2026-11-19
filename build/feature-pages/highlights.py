"""Build the Case of the month pages: /court-decisions/highlights/ (list), one page per month, and feed.xml.
Content is in highlights_content.py."""
import csv
import html
import json
import os
from email.utils import format_datetime
import datetime as dt

from shell import page, ROOT, SITE
from highlights_content import HIGHLIGHTS

E = html.escape
MON_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MON_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
BASIS = {"S": ("Written from our database entry, which was coded from the judgment and reports of it; a line-by-line check against the judgment is still pending.",
               "Ditulis dari entri basis data kami, yang dikodekan dari putusan dan pemberitaannya; pemeriksaan baris demi baris terhadap putusan masih berlangsung."),
         "P": ("Checked against the judgment.", "Telah dicocokkan dengan putusan.")}

DEC = {r["id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data", "court-decisions", "decisions.csv"), encoding="utf-8-sig"))}

CSS = """<link rel="stylesheet" href="/assets/features.css">
<link rel="alternate" type="application/rss+xml" title="IMR Case of the month" href="/court-decisions/highlights/feed.xml">
<style>
.hl-art h2{margin:34px 0 0;font-size:24px;font-weight:600}
.hl-art p{margin:12px 0 0}
.hl-meta{margin:14px 0 0;font-size:16px;color:#2E493D}
.hl-post{white-space:pre-wrap;font-size:16px;background:#FFFFFF;border:1px dashed #7F9A8C;padding:12px 14px;margin:10px 0 0}
.hl-list{list-style:none;margin:20px 0 0;padding:0}
.hl-list li{margin:0 0 14px}
.hl-list a{display:block;background:#FFFFFF;border:1px solid #B2C7BC;padding:18px 20px;text-decoration:none;color:#172D24}
.hl-list a:hover{border-color:#1E6B4A}
.hl-list b{display:block;font-size:21px;font-weight:600}
.hl-list span{font-size:15px;color:#2E493D}
</style>"""


def mname(m, lang):
    y, mo = m.split("-")
    return (MON_EN if lang == "en" else MON_ID)[int(mo) - 1] + " " + y


def article(h):
    d = DEC.get(h["id"])
    if d is None:
        raise SystemExit("highlight %s: decision id %s not in decisions.csv" % (h["month"], h["id"]))
    def side(lang):
        body = h["body_" + lang]
        t = h["title_" + lang]
        court = h["court_" + lang]
        links = "".join('<li><a href="%s">%s</a></li>' % (E(u), E(en if lang == "en" else idn)) for u, en, idn in h["links"])
        post = h["post_" + lang]
        out = ['<p class="ft-eye">%s · %s</p>' % ("Case of the month" if lang == "en" else "Putusan bulan ini", mname(h["month"], lang)),
               '<h1 class="ft-h1">%s</h1>' % E(t), '<p class="hl-meta">%s</p>' % E(court)]
        for head, para in body:
            out.append("<h2>%s</h2><p>%s</p>" % (E(head), E(para)))
        out.append('<h2>%s</h2><ul>%s</ul>' % ("Read more" if lang == "en" else "Baca lebih lanjut", links))
        out.append('<h2>%s</h2><p class="ft-note">%s</p><div class="hl-post" data-noi18n>%s</div>'
                   '<div class="ft-row"><button type="button" class="ft-btn alt hl-copy">%s</button></div>'
                   % ("Share" if lang == "en" else "Bagikan",
                      "A short post for social media. Copy it as it is." if lang == "en" else "Unggahan singkat untuk media sosial. Salin apa adanya.",
                      E(post), "Copy post" if lang == "en" else "Salin unggahan"))
        out.append('<div class="ft-box">%s</div>' % E(BASIS[h["basis"]][0 if lang == "en" else 1]))
        cite = ("Cite this write-up as: Institute for Migrant Rights, &ldquo;%s&rdquo;, Case of the month, %s, theimr.org/court-decisions/highlights/%s/."
                if lang == "en" else
                "Kutip tulisan ini sebagai: Institute for Migrant Rights, &ldquo;%s&rdquo;, Putusan bulan ini, %s, theimr.org/court-decisions/highlights/%s/.")
        out.append('<p class="ft-note">%s</p>' % (cite % (E(t), mname(h["month"], lang), h["month"])))
        return "\n".join(out)
    return ('<div class="ft-en">%s</div>\n<div class="ft-id" data-noi18n lang="id">%s</div>' % (side("en"), side("id")))


COPY_JS = """<script>document.addEventListener('click',function(e){var b=e.target.closest('.hl-copy');if(!b)return;var t=b.parentNode.previousElementSibling.textContent;(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){window.IMRF&&IMRF.toast(document.documentElement.lang==='id'?'Disalin':'Copied')},function(){var r=document.createRange();r.selectNode(b.parentNode.previousElementSibling);getSelection().removeAllRanges();getSelection().addRange(r)})});</script>"""


def main():
    hs = sorted(HIGHLIGHTS, key=lambda h: h["month"], reverse=True)
    for h in hs:
        d = DEC[h["id"]]
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": h["title_en"], "inLanguage": ["en", "id"],
              "datePublished": h["month"] + "-01", "publisher": {"@type": "Organization", "name": "Institute for Migrant Rights", "url": "https://theimr.org/"},
              "about": {"@type": "Legislation", "name": d["citation"], "legislationJurisdiction": d["country"]},
              "url": "https://theimr.org/court-decisions/highlights/%s/" % h["month"]}
        main_html = ('<main id="highlight"><section style="padding:56px 0 24px"><div class="ft-narrow hl-art">%s'
                     '<p class="ft-note" style="margin-top:28px"><a href="/court-decisions/highlights/">All cases of the month</a></p></div></section></main>' % article(h))
        page("/court-decisions/highlights/%s/" % h["month"], h["title_en"] + " · Case of the month",
             "%s: %s" % (h["court_en"], h["body_en"][0][1][:150]), main_html,
             head=CSS + '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False),
             scripts='<script src="/assets/features.js" defer></script>\n' + COPY_JS,
             i18n={"All cases of the month": "Semua putusan bulan ini"})
    items = "".join('<li><a href="/court-decisions/highlights/%s/"><span class="ft-en">%s</span><span class="ft-id" data-noi18n>%s</span>'
                    '<b class="ft-en">%s</b><b class="ft-id" data-noi18n>%s</b><span class="ft-en">%s</span><span class="ft-id" data-noi18n>%s</span></a></li>'
                    % (h["month"], mname(h["month"], "en"), mname(h["month"], "id"), E(h["title_en"]), E(h["title_id"]), E(h["court_en"]), E(h["court_id"])) for h in hs)
    idx = """<main id="highlights"><section style="padding:56px 0 24px"><div class="ft-narrow">
<p class="ft-eye">Court Decisions</p>
<h1 class="ft-h1">Case of the month</h1>
<p class="ft-lede">Each month we pick one decision from the Court Decisions database and explain, in a few paragraphs, what the court decided, why it matters for migrant workers, and what to watch next. Every write-up comes in English and Indonesian, with a short post you can share.</p>
<p class="ft-note"><a href="/court-decisions/highlights/feed.xml">Follow by RSS</a> · <a href="/court-decisions/">All court decisions</a></p>
<ul class="hl-list">%s</ul>
</div></section></main>""" % items
    page("/court-decisions/highlights/", "Case of the month",
         "One court decision each month from the IMR Court Decisions database, explained in English and Indonesian: what the court decided, why it matters for migrant workers, and what to watch.",
         idx, head=CSS, scripts='<script src="/assets/features.js" defer></script>',
         i18n={"Court Decisions": "Putusan Pengadilan", "Case of the month": "Putusan bulan ini",
               "Each month we pick one decision from the Court Decisions database and explain, in a few paragraphs, what the court decided, why it matters for migrant workers, and what to watch next. Every write-up comes in English and Indonesian, with a short post you can share.":
               "Setiap bulan kami memilih satu putusan dari basis data Putusan Pengadilan dan menjelaskan dalam beberapa paragraf apa yang diputuskan pengadilan, mengapa putusan tersebut penting bagi pekerja migran, dan apa yang perlu dicermati selanjutnya. Setiap tulisan tersedia dalam bahasa Inggris dan Indonesia, disertai unggahan singkat yang dapat dibagikan.",
               "Follow by RSS": "Ikuti melalui RSS", "All court decisions": "Semua putusan pengadilan"})
    # RSS
    now = format_datetime(dt.datetime.now(dt.timezone.utc))
    rss_items = "".join("""<item><title>%s</title><link>https://theimr.org/court-decisions/highlights/%s/</link><guid>https://theimr.org/court-decisions/highlights/%s/</guid><pubDate>%s</pubDate><description>%s</description></item>"""
                        % (E(h["title_en"]), h["month"], h["month"],
                           format_datetime(dt.datetime.strptime(h["month"] + "-01", "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)),
                           E(h["court_en"] + ". " + h["body_en"][0][1])) for h in hs)
    with open(os.path.join(SITE, "court-decisions", "highlights", "feed.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>IMR Case of the month</title>'
                '<link>https://theimr.org/court-decisions/highlights/</link><description>One court decision on migrant workers each month, from the Institute for Migrant Rights.</description>'
                '<language>en</language><lastBuildDate>%s</lastBuildDate>%s</channel></rss>\n' % (now, rss_items))
    print("%d highlights" % len(hs))


main()
