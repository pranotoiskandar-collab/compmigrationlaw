"""Build the monthly "What's new in the databases" digest from the repository's own history.

    python3 tools/digest/digest.py --month 2026-11

What it does
------------
It compares the published data files (data/<database>/*.csv, never incoming/ or
sources/) as they stood at the start of the month with how they stand at the end
of it (or now, for the current month), and writes:

    site/updates/<YYYY-MM>/index.html   the issue as a web page (English and Indonesian)
    site/updates/index.html             the list of issues, with the sign-up form
    site/updates/feed.xml               an RSS feed of the issues
    newsletter/<YYYY-MM>/email.html     the same issue as an email (inline styles)
    newsletter/<YYYY-MM>/email.txt      a plain-text copy
    newsletter/<YYYY-MM>/summary.json   the counts, for the record

Nothing is sent. The monthly GitHub Action runs this script and opens a pull
request; once an editor merges it, a second Action can place the email in
Buttondown as a draft for one person to send (see README.md in this folder).

No staff writing is needed. An editor may add a short note for an issue in
tools/digest/notes/<YYYY-MM>.json ({"en": "...", "id": "..."}); it appears at the top.
"""
import argparse
import csv
import datetime as dt
import html
import io
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "site"
OUT_SITE = SITE / "updates"
OUT_MAIL = ROOT / "newsletter"
BASE_URL = "https://theimr.org"

CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))

MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August",
             "September", "October", "November", "December"]
MONTHS_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
             "September", "Oktober", "November", "Desember"]

# English and Indonesian country names for the codes used in the databases.
COUNTRIES = {
    "AE": ("United Arab Emirates", "Uni Emirat Arab"), "AO": ("Angola", "Angola"), "AR": ("Argentina", "Argentina"),
    "AT": ("Austria", "Austria"), "AU": ("Australia", "Australia"), "AZ": ("Azerbaijan", "Azerbaijan"),
    "BD": ("Bangladesh", "Bangladesh"), "BE": ("Belgium", "Belgia"), "BG": ("Bulgaria", "Bulgaria"),
    "BH": ("Bahrain", "Bahrain"), "BN": ("Brunei", "Brunei"), "BO": ("Bolivia", "Bolivia"), "BR": ("Brazil", "Brasil"),
    "BW": ("Botswana", "Botswana"), "CA": ("Canada", "Kanada"), "CD": ("DR Congo", "RD Kongo"),
    "CH": ("Switzerland", "Swiss"), "CI": ("Côte d’Ivoire", "Pantai Gading"), "CL": ("Chile", "Cile"),
    "CO": ("Colombia", "Kolombia"), "CY": ("Cyprus", "Siprus"), "DK": ("Denmark", "Denmark"),
    "DO": ("Dominican Republic", "Republik Dominika"), "EC": ("Ecuador", "Ekuador"), "EG": ("Egypt", "Mesir"),
    "ES": ("Spain", "Spanyol"), "FR": ("France", "Prancis"), "GB": ("United Kingdom", "Britania Raya"),
    "GH": ("Ghana", "Ghana"), "GN": ("Guinea", "Guinea"), "GR": ("Greece", "Yunani"), "GT": ("Guatemala", "Guatemala"),
    "HK": ("Hong Kong", "Hong Kong"), "HR": ("Croatia", "Kroasia"), "HU": ("Hungary", "Hungaria"),
    "ID": ("Indonesia", "Indonesia"), "IL": ("Israel", "Israel"), "IN": ("India", "India"), "IT": ("Italy", "Italia"),
    "JO": ("Jordan", "Yordania"), "JP": ("Japan", "Jepang"), "KE": ("Kenya", "Kenya"), "KG": ("Kyrgyzstan", "Kirgizstan"),
    "KR": ("South Korea", "Korea Selatan"), "KW": ("Kuwait", "Kuwait"), "KZ": ("Kazakhstan", "Kazakhstan"),
    "LB": ("Lebanon", "Lebanon"), "LK": ("Sri Lanka", "Sri Lanka"), "LS": ("Lesotho", "Lesotho"),
    "LV": ("Latvia", "Latvia"), "MA": ("Morocco", "Maroko"), "MG": ("Madagascar", "Madagaskar"),
    "MM": ("Myanmar", "Myanmar"), "MO": ("Macao", "Makau"), "MR": ("Mauritania", "Mauritania"),
    "MU": ("Mauritius", "Mauritius"), "MW": ("Malawi", "Malawi"), "MX": ("Mexico", "Meksiko"),
    "MY": ("Malaysia", "Malaysia"), "NA": ("Namibia", "Namibia"), "NE": ("Niger", "Niger"), "NG": ("Nigeria", "Nigeria"),
    "NI": ("Nicaragua", "Nikaragua"), "NL": ("Netherlands", "Belanda"), "NP": ("Nepal", "Nepal"),
    "NZ": ("New Zealand", "Selandia Baru"), "OM": ("Oman", "Oman"), "PA": ("Panama", "Panama"), "PE": ("Peru", "Peru"),
    "PG": ("Papua New Guinea", "Papua Nugini"), "PH": ("Philippines", "Filipina"), "PK": ("Pakistan", "Pakistan"),
    "PL": ("Poland", "Polandia"), "QA": ("Qatar", "Qatar"), "RW": ("Rwanda", "Rwanda"),
    "SA": ("Saudi Arabia", "Arab Saudi"), "SE": ("Sweden", "Swedia"), "SG": ("Singapore", "Singapura"),
    "SI": ("Slovenia", "Slovenia"), "SR": ("Suriname", "Suriname"), "TH": ("Thailand", "Thailand"),
    "TJ": ("Tajikistan", "Tajikistan"), "TN": ("Tunisia", "Tunisia"), "TW": ("Taiwan", "Taiwan"),
    "TZ": ("Tanzania", "Tanzania"), "UG": ("Uganda", "Uganda"), "US": ("United States", "Amerika Serikat"),
    "VE": ("Venezuela", "Venezuela"), "VN": ("Viet Nam", "Vietnam"), "ZA": ("South Africa", "Afrika Selatan"),
    "ZM": ("Zambia", "Zambia"), "ZW": ("Zimbabwe", "Zimbabwe"),
    "XA": ("Inter-American system", "Sistem Inter-Amerika"), "XM": ("Inter-American system", "Sistem Inter-Amerika"),
    "XF": ("African system", "Sistem Afrika"), "XI": ("International", "Internasional"),
}

# The published tables the digest watches, with how to tell one row from another.
LAW_TABLES = [
    # path, key columns, country column, title column, year column, database page, English and Indonesian name
    ("data/migration-law/migration-norms.csv", ("name", "citation"), None, "name", "adopted", "/migration-law/",
     "Migration Law Atlas", "Atlas Hukum Migrasi"),
    ("data/gcc/domestic-laws.csv", ("s", "title"), "s", "title", "year", "/gcc/",
     "Gulf States", "Negara-Negara Teluk"),
    ("data/east-asia/domestic-laws.csv", ("s", "title"), "s", "title", "year", "/east-asia/",
     "East Asia", "Asia Timur"),
    ("data/southeast-asia/domestic-laws.csv", ("s", "title"), "s", "title", "year", "/southeast-asia/",
     "Southeast Asia", "Asia Tenggara"),
    ("data/countries-of-origin/laws-policies.csv", ("s", "title"), "s", "title", "year", "/countries-of-origin/",
     "Countries of Origin", "Negara Asal"),
    ("data/domestic-workers/instruments.csv", ("id",), None, "title", "year", "/domestic-workers/",
     "Migrant Domestic Workers", "Pekerja Rumah Tangga Migran"),
]
DEV_TABLES = [
    ("data/countries-of-origin/developments.csv", "country", "/countries-of-origin/", "Countries of Origin", "Negara Asal"),
    ("data/east-asia/developments.csv", "jurisdiction", "/east-asia/", "East Asia", "Asia Timur"),
    ("data/southeast-asia/developments.csv", "state", "/southeast-asia/", "Southeast Asia", "Asia Tenggara"),
]
DECISIONS = "data/court-decisions/decisions.csv"
INCOMING_NAMES = {
    "africa": ("Africa", "Afrika"), "countries-of-origin": ("Countries of Origin", "Negara Asal"),
    "court-decisions": ("Court Decisions", "Putusan Pengadilan"), "east-asia": ("East Asia", "Asia Timur"),
    "gcc": ("Gulf States", "Negara-Negara Teluk"), "government-hate-speech": ("Government Hate Speech", "Ucapan Kebencian oleh Negara"),
    "migration-law": ("Migration Law Atlas", "Atlas Hukum Migrasi"), "southeast-asia": ("Southeast Asia", "Asia Tenggara"),
    "domestic-workers": ("Migrant Domestic Workers", "Pekerja Rumah Tangga Migran"),
}
STATUS = {"C": ("unchecked candidate", "kandidat belum diperiksa"),
          "S": ("full entry, to be checked against the judgment", "entri lengkap, belum dicocokkan dengan putusan"),
          "P": ("checked against the judgment", "sudah dicocokkan dengan putusan")}


# ---------------------------------------------------------------- git helpers
def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()


def commit_before(when, ref):
    return git("rev-list", "-1", "--first-parent", f"--before={when}", ref)


def read_csv_at(rev, path):
    """Rows of a CSV file as it stood at a commit (empty if it did not exist)."""
    if rev is None:
        text = (ROOT / path).read_text(encoding="utf-8-sig") if (ROOT / path).exists() else ""
    else:
        text = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT, capture_output=True,
                              check=False).stdout.decode("utf-8", "replace").lstrip("﻿")
    if not text:
        return []
    rows = list(csv.DictReader(io.StringIO(text)))
    for row in rows:  # some files carry a byte-order mark in the first header
        for k in list(row):
            if k and k.startswith("﻿"):
                row[k[1:]] = row.pop(k)
    return rows


def incoming_files_at(rev):
    """Content hash of every incoming/ CSV (raw portal listings left out), keyed by path."""
    out = {}
    for line in git("ls-tree", "-r", rev, "data").splitlines():
        meta, path = line.split("\t", 1)
        if "/incoming/" in path and "/raw/" not in path and path.endswith(".csv"):
            out[path] = meta.split()[2]
    return out


# ---------------------------------------------------------------- the comparison
def compare(base, end):
    """What was added or checked between two commits."""
    result = {"decisions_new": [], "decisions_checked": [], "laws": [], "developments": [], "incoming": {}}

    old = {r["id"]: r for r in read_csv_at(base, DECISIONS)}
    new = read_csv_at(end, DECISIONS)
    for r in new:
        before = old.get(r["id"])
        if before is None:
            result["decisions_new"].append(r)
        elif "CSP".index(r.get("status", "C") or "C") > "CSP".index(before.get("status", "C") or "C"):
            result["decisions_checked"].append(r)

    for path, key, ccol, tcol, ycol, page, en, id_ in LAW_TABLES:
        keyf = lambda r: tuple((r.get(k) or "").strip() for k in key)
        seen = {keyf(r) for r in read_csv_at(base, path)}
        added = [r for r in read_csv_at(end, path) if keyf(r) not in seen]
        if added:
            result["laws"].append({"page": page, "en": en, "id": id_, "rows": [
                {"country": (r.get(ccol) or "").strip() if ccol else "", "title": r.get(tcol, ""),
                 "orig": r.get("orig", ""), "year": (r.get(ycol) or "")[:4], "url": r.get("url") or r.get("link") or ""}
                for r in added]})

    for path, ccol, page, en, id_ in DEV_TABLES:
        keyf = lambda r: (r.get("date", ""), r.get(ccol, ""), r.get("change", ""))
        seen = {keyf(r) for r in read_csv_at(base, path)}
        for r in read_csv_at(end, path):
            if keyf(r) not in seen:
                result["developments"].append({"page": page, "en": en, "id": id_, "date": r.get("date", ""),
                                               "country": r.get(ccol, ""), "change": r.get("change", "")})

    before, after = incoming_files_at(base), incoming_files_at(end)
    for path, blob in after.items():
        if before.get(path) != blob:
            db = path.split("/")[1]
            result["incoming"][db] = result["incoming"].get(db, 0) + 1
    result["totals"] = {"decisions": len(new)}
    return result


# ---------------------------------------------------------------- wording helpers
def esc(s):
    return html.escape(s or "", quote=True)


def cname(code, lang):
    pair = COUNTRIES.get(code)
    return pair[0 if lang == "en" else 1] if pair else code


def nice_date(iso, lang):
    """2024-11-29 -> 29 November 2024 / 29 November 2024; 2024 -> 2024."""
    parts = (iso or "").split("-")
    months = MONTHS_EN if lang == "en" else MONTHS_ID
    try:
        if len(parts) == 3:
            return f"{int(parts[2])} {months[int(parts[1]) - 1]} {parts[0]}"
        if len(parts) == 2:
            return f"{months[int(parts[1]) - 1]} {parts[0]}"
    except (ValueError, IndexError):
        pass
    return iso or ""


def num(n, lang):
    s = f"{n:,}"
    return s.replace(",", ".") if lang == "id" else s


def by_country(rows, key="country"):
    counts = {}
    for r in rows:
        counts[r[key]] = counts.get(r[key], 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def decision_url(r):
    return f"{BASE_URL}/court-decisions/d/{r['id']}/"


def sections(data, month_label, lang, note):
    """The content of an issue as a list of (heading, [html blocks]) in one language.

    Kept free of styling so the web page and the email can each dress it their own way.
    Wording is descriptive throughout: no rankings and no judgments about any state.
    """
    en = lang == "en"
    T = lambda e, i: e if en else i
    out = []
    dn, dc = data["decisions_new"], data["decisions_checked"]
    laws_n = sum(len(t["rows"]) for t in data["laws"])
    full = [r for r in dn if r.get("status") in ("S", "P")]
    cands = [r for r in dn if r.get("status") not in ("S", "P")]

    # 1. In brief
    brief = []
    if note:
        brief.append(f"<p>{esc(note)}</p>")
    items = []
    if dn:
        items.append(T(f"<b>{num(len(dn), lang)}</b> court decisions added to Court Decisions"
                       f" ({num(len(full), lang)} full entries with a summary, {num(len(cands), lang)} unchecked candidates).",
                       f"<b>{num(len(dn), lang)}</b> putusan pengadilan ditambahkan ke basis data Putusan Pengadilan"
                       f" ({num(len(full), lang)} entri lengkap dengan ringkasan, {num(len(cands), lang)} kandidat belum diperiksa)."))
    if dc:
        items.append(T(f"<b>{num(len(dc), lang)}</b> earlier {'entry' if len(dc) == 1 else 'entries'} moved up a step in checking.",
                       f"<b>{num(len(dc), lang)}</b> entri lama naik satu tahap pemeriksaan."))
    if laws_n:
        items.append(T(f"<b>{num(laws_n, lang)}</b> laws, regulations and instruments added to the lists of legal texts.",
                       f"<b>{num(laws_n, lang)}</b> undang-undang, peraturan dan instrumen ditambahkan ke daftar teks hukum."))
    if data["developments"]:
        items.append(T(f"<b>{num(len(data['developments']), lang)}</b> new dated entries in the timelines of legal change.",
                       f"<b>{num(len(data['developments']), lang)}</b> entri baru dalam linimasa perubahan hukum."))
    inc = sum(data["incoming"].values())
    if inc:
        items.append(T(f"<b>{num(inc, lang)}</b> new or updated files of material received for review (not yet in the databases).",
                       f"<b>{num(inc, lang)}</b> berkas bahan baru atau yang diperbarui telah kami terima untuk ditinjau (belum masuk basis data)."))
    if not items:
        items.append(T("No new entries this month.", "Tidak ada entri baru bulan ini."))
    brief.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
    brief.append(T(f"<p>Court Decisions now holds <b>{num(data['totals']['decisions'], lang)}</b> decisions in all.</p>",
                   f"<p>Basis data Putusan Pengadilan kini memuat <b>{num(data['totals']['decisions'], lang)}</b> putusan.</p>"))
    out.append((T(f"In brief: {month_label}", f"Ringkasan: {month_label}"), brief))

    # 2. Full entries with a plain-language summary
    if full:
        blocks = [T("<p>These entries have a plain-language summary. They were coded from the courts’ own summaries, "
                    "law reports and news coverage and are still to be checked line by line against the judgment.</p>",
                    "<p>Entri berikut dilengkapi ringkasan dalam bahasa sederhana. Kami mengodekannya dari ringkasan pengadilan, "
                    "laporan hukum, dan pemberitaan; entri tersebut belum dicocokkan baris demi baris dengan teks putusan.</p>")]
        for r in sorted(full, key=lambda r: r.get("date", ""), reverse=True)[:CONFIG["max_full_entries"]]:
            summary = r.get("plain_en") if en else (r.get("plain_id") or r.get("plain_en"))
            blocks.append(
                f'<div class="item"><p class="t"><a href="{decision_url(r)}">{esc(r["name"])}</a></p>'
                f'<p class="m">{esc(r["court"])} · {esc(cname(r["country"], lang))} · {esc(nice_date(r["date"], lang))}</p>'
                + (f"<p>{esc(summary)}</p>" if summary else "") + "</div>")
        if len(full) > CONFIG["max_full_entries"]:
            blocks.append(T(f"<p>And {len(full) - CONFIG['max_full_entries']} more in the database.</p>",
                            f"<p>Dan {len(full) - CONFIG['max_full_entries']} lainnya di basis data.</p>"))
        out.append((T("New decisions with a summary", "Putusan baru dengan ringkasan"), blocks))

    # 3. Candidates: counts by country, plus the most recent ones
    if cands:
        rows = "".join(f"<tr><td>{esc(cname(c, lang))}</td><td class='n'>{num(n, lang)}</td></tr>"
                       for c, n in by_country(cands))
        blocks = [T("<p>Unchecked candidates are leads for researchers: a case name, court, date and topic taken from the "
                    "court’s own portal, with no summary yet. Each one links to the official source.</p>",
                    "<p>Kandidat belum diperiksa merupakan petunjuk bagi peneliti, yakni nama perkara, pengadilan, tanggal, "
                    "dan topik yang kami ambil dari portal resmi pengadilan, tanpa ringkasan. Setiap kandidat ditautkan ke sumber resminya.</p>"),
                  f"<table><thead><tr><th>{T('Country or system', 'Negara atau sistem')}</th>"
                  f"<th class='n'>{T('Added', 'Ditambahkan')}</th></tr></thead><tbody>{rows}</tbody></table>"]
        recent = sorted(cands, key=lambda r: r.get("date", ""), reverse=True)[:CONFIG["max_recent_candidates"]]
        blocks.append(f"<p class='sub'>{T('Most recent among them', 'Yang terbaru di antaranya')}</p><ul>" + "".join(
            f'<li><a href="{decision_url(r)}">{esc(r["name"])}</a>, {esc(r["court"])}, {esc(nice_date(r["date"], lang))}</li>'
            for r in recent) + "</ul>")
        out.append((T("New leads for researchers", "Petunjuk baru bagi peneliti"), blocks))

    # 4. Checked this month
    if dc:
        blocks = ["<ul>" + "".join(
            f'<li><a href="{decision_url(r)}">{esc(r["name"])}</a> ({esc(cname(r["country"], lang))}): '
            f'{esc(STATUS.get(r.get("status"), ("", ""))[0 if en else 1])}</li>' for r in dc[:20]) + "</ul>"]
        out.append((T("Entries checked further", "Entri yang diperiksa lebih lanjut"), blocks))

    # 5. Laws
    if data["laws"]:
        blocks = [T("<p>Titles are listed as they appear in the official gazettes or portals, with the year of adoption. "
                    "Entries marked as unverified on the database pages are still being checked.</p>",
                    "<p>Judul kami cantumkan sebagaimana tertulis dalam lembaran negara atau portal resmi, beserta tahun pengesahannya. "
                    "Entri yang ditandai belum diverifikasi di halaman basis data masih dalam pemeriksaan.</p>")]
        for t in data["laws"]:
            name = t["en"] if en else t["id"]
            blocks.append(f'<p class="sub"><a href="{BASE_URL}{t["page"]}">{esc(name)}</a>: '
                          f'{num(len(t["rows"]), lang)} {T("added", "ditambahkan")}</p>')
            groups = {}
            for r in t["rows"]:
                groups.setdefault(r["country"], []).append(r)
            lis = []
            for c in sorted(groups, key=lambda c: cname(c, lang)):
                shown = groups[c][:CONFIG["max_laws_per_country"]]
                more = len(groups[c]) - len(shown)
                titles = "; ".join(
                    (f'<a href="{esc(r["url"])}">{esc(r["title"])}</a>' if r["url"].startswith("http") else esc(r["title"]))
                    + (f" ({esc(r['year'])})" if r["year"] else "") for r in shown)
                if more:
                    titles += T(f"; and {more} more", f"; dan {more} lainnya")
                label = f"<b>{esc(cname(c, lang))}</b>: " if c else ""
                lis.append(f"<li>{label}{titles}</li>")
            blocks.append("<ul>" + "".join(lis) + "</ul>")
        out.append((T("New laws and instruments", "Undang-undang dan instrumen baru"), blocks))

    # 6. Timelines
    if data["developments"]:
        blocks = ["<ul>" + "".join(
            f'<li>{esc(nice_date(d["date"], lang))}, {esc(cname(d["country"], lang))}: {esc(d["change"])}</li>'
            for d in data["developments"][:20]) + "</ul>"]
        out.append((T("Added to the timelines", "Tambahan pada linimasa"), blocks))

    # 7. Waiting for review
    if data["incoming"]:
        rows = "".join(f"<li>{esc(INCOMING_NAMES.get(db, (db, db))[0 if en else 1])}: {num(n, lang)} {T('file' if n == 1 else 'files', 'berkas')}</li>"
                       for db, n in sorted(data["incoming"].items(), key=lambda kv: -kv[1]))
        blocks = [T("<p>Material collected from official portals and sent in for review. It is published on GitHub "
                    "for transparency but is not part of the databases until an editor has checked it.</p>",
                    "<p>Bahan yang kami himpun dari portal resmi dan diajukan untuk ditinjau. Bahan tersebut kami terbitkan di GitHub "
                    "demi keterbukaan, namun belum menjadi bagian dari basis data sebelum diperiksa editor.</p>"),
                  f"<ul>{rows}</ul>",
                  f'<p><a href="https://github.com/{CONFIG["repo"]}">{T("See the incoming folders on GitHub", "Lihat folder incoming di GitHub")}</a></p>']
        out.append((T("Waiting for review", "Menunggu tinjauan"), blocks))

    # 8. Using the data
    out.append((T("Using the data", "Memakai datanya"), [T(
        f'<p>All data are free to download under CC BY 4.0 from each database page and from '
        f'<a href="https://github.com/{CONFIG["repo"]}">GitHub</a>, where the history of every file is public. '
        f'Please cite the database page and the date you downloaded it. Corrections are welcome at '
        f'<a href="mailto:{CONFIG["contact"]}">{CONFIG["contact"]}</a>.</p>',
        f'<p>Seluruh data dapat diunduh gratis dengan lisensi CC BY 4.0 dari halaman setiap basis data dan dari '
        f'<a href="https://github.com/{CONFIG["repo"]}">GitHub</a>, tempat riwayat setiap berkas terbuka untuk umum. '
        f'Mohon kutip halaman basis data beserta tanggal anda mengunduhnya. Koreksi dapat dikirim ke '
        f'<a href="mailto:{CONFIG["contact"]}">{CONFIG["contact"]}</a>.</p>')]))
    return out


# ---------------------------------------------------------------- site page pieces
def site_chrome():
    """Masthead and footer copied from a current page, so the digest always matches the site's look."""
    page = (SITE / "ai-use" / "index.html").read_text(encoding="utf-8")
    head_css = re.search(r"(<style>\s*\.nav details.*?</style>)", page, re.S)
    mast = re.search(r'(<nav class="imr-bentham".*?</header>)', page, re.S)
    foot = re.search(r'(<div class="imr-ridge".*?</footer>)', page, re.S)
    return (head_css.group(1) if head_css else "", mast.group(1) if mast else "", foot.group(1) if foot else "")


PAGE_CSS = """
body{margin:0;font-variant-numeric:tabular-nums}
a{color:var(--nb-red,#8F5E12)}
.dg{max-width:760px;margin:0 auto;padding:0 24px}
.dg h1{margin:16px 0 0;font-weight:400;font-size:clamp(34px,6vw,52px);line-height:1.1}
.dg .eyebrow{margin:0;font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:var(--nb-red,#8F5E12)}
.dg .lede{margin:18px 0 0;color:var(--nb-soft,#4A3B2D)}
.dg section.s{padding:28px 0;border-top:1px solid var(--nb-rule,#C8BCB1)}
.dg h2{margin:0 0 10px;font-weight:500;font-size:26px;line-height:1.2}
.dg .item{margin:0 0 18px}.dg .item p{margin:0}.dg .item .t{font-weight:600}
.dg .item .m,.dg .sub{font-size:15px;color:var(--nb-mute,#5B4A3C)}.dg .sub{margin:14px 0 4px;font-weight:600}
.dg table{border-collapse:collapse;width:100%;max-width:420px;font-size:16px}
.dg th,.dg td{text-align:left;padding:4px 8px 4px 0;border-bottom:1px solid var(--nb-rule,#C8BCB1)}
.dg .n{text-align:right}
.dg ul{padding-left:20px}.dg li{margin:4px 0}
.dg .signup{margin:28px 0;padding:22px;border:1px solid var(--nb-rule,#C8BCB1);background:rgba(255,255,255,.35)}
.dg .signup h2{font-size:22px}
.dg .signup form{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.dg .signup input[type=email],.dg .signup select{font:inherit;font-size:16px;padding:9px 10px;border:1px solid var(--nb-rule,#C8BCB1);background:#fff;min-width:0;flex:1 1 220px}
.dg .signup button{font:inherit;font-size:16px;font-weight:600;padding:9px 18px;border:0;background:var(--nb-ink,#2E2116);color:#fff;cursor:pointer}
.dg .fine{font-size:14px;color:var(--nb-mute,#5B4A3C)}
html[lang=id] .dg [lang=en]{display:none}
html:not([lang=id]) .dg [lang=id]{display:none}
"""


def signup_form(lang):
    """Sign-up box. Uses Buttondown once its username is in config.json; until then a Netlify form collects addresses."""
    en = lang == "en"
    T = lambda e, i: e if en else i
    who = (f'<select name="metadata__audience" aria-label="{T("I am from", "Saya dari")}">'
           f'<option value="">{T("I am from… (optional)", "Saya dari… (opsional)")}</option>'
           f'<option value="university">{T("a university", "universitas")}</option>'
           f'<option value="ngo">{T("an NGO or union", "LSM atau serikat pekerja")}</option>'
           f'<option value="media">{T("the media", "media")}</option>'
           f'<option value="government">{T("a government or international body", "pemerintah atau lembaga internasional")}</option>'
           f'<option value="other">{T("elsewhere", "lainnya")}</option></select>')
    if CONFIG.get("buttondown_username"):
        action = f'https://buttondown.com/api/emails/embed-subscribe/{esc(CONFIG["buttondown_username"])}'
        form = (f'<form action="{action}" method="post" target="_blank">'
                f'<input type="email" name="email" required autocomplete="email" placeholder="{T("Your email address", "Alamat email anda")}" aria-label="{T("Your email address", "Alamat email anda")}">'
                f'{who}<input type="hidden" name="tag" value="database-updates">'
                f'<input type="hidden" name="tag" value="lang-{lang}">'
                f'<button type="submit">{T("Sign up", "Daftar")}</button></form>')
    else:
        name = "database-updates" if en else "database-updates-id"
        form = (f'<form name="{name}" method="POST" action="/updates/thanks/" data-netlify="true" netlify-honeypot="bot-field">'
                f'<input type="hidden" name="form-name" value="{name}"><p hidden><label>Leave this empty <input name="bot-field"></label></p>'
                f'<input type="email" name="email" required autocomplete="email" placeholder="{T("Your email address", "Alamat email anda")}" aria-label="{T("Your email address", "Alamat email anda")}">'
                f'{who}<button type="submit">{T("Sign up", "Daftar")}</button></form>')
    return (f'<div class="signup" lang="{lang}"><h2>{T("Get this update by email", "Dapatkan kabar ini lewat email")}</h2>'
            f'<p>{T("Once a month: new court decisions and laws in the databases, in English and Indonesian. Free, no other mail, unsubscribe at any time.", "Sebulan sekali: putusan pengadilan dan undang-undang baru dalam basis data, dalam bahasa Inggris dan Indonesia. Gratis, tanpa surat lain, dan dapat berhenti kapan saja.")}</p>'
            f'{form}<p class="fine">{T("We use your address only to send this update.", "Kami hanya memakai alamat anda untuk mengirim kabar ini.")}</p></div>')


def page(title, desc, canonical, body, extra_head=""):
    nav_css, mast, foot = site_chrome()
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Institute for Migrant Rights</title>
<meta name="description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&amp;display=swap">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="IMR database updates" href="/updates/feed.xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Institute for Migrant Rights">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
{nav_css}
<link rel="stylesheet" href="/assets/notebook.css">
<link rel="stylesheet" href="/assets/editorial.css">
<style>{PAGE_CSS}</style>
<!-- imr-analytics -->
<script data-goatcounter="https://theimr.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<script src="/assets/imr-events.js" defer></script>
{extra_head}
</head>
<body>
<div style="background: var(--nb-paper,#EEE9E5); color: var(--nb-ink,#2E2116); font-family: 'Figtree', system-ui, sans-serif; font-size: 19px; line-height: 1.65">
{mast}
<main class="dg" data-noi18n style="padding:72px 24px 24px">
{body}
</main>
{foot}
</div>
<script>
document.addEventListener('click', function (e) {{
  document.querySelectorAll('.nav details[open]').forEach(function (d) {{ if (!d.contains(e.target)) d.removeAttribute('open'); }});
}});
</script>
<script src="/assets/lang.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- email
EMAIL = {"paper": "#F4F8F5", "ink": "#172D24", "soft": "#2E493D", "mute": "#3D5A4D", "accent": "#1E6B4A", "rule": "#B2C7BC"}


def email_html(month, labels, secs, url):
    c = EMAIL
    style = {
        "<p>": f'<p style="margin:0 0 12px">',
        "<ul>": '<ul style="margin:0 0 12px;padding-left:20px">',
        "<li>": '<li style="margin:4px 0">',
        "<table>": f'<table style="border-collapse:collapse;width:100%;max-width:420px;font-size:15px;margin:0 0 12px">',
        "<th>": f'<th style="text-align:left;padding:4px 8px 4px 0;border-bottom:1px solid {c["rule"]}">',
        "<th class='n'>": f'<th style="text-align:right;padding:4px 0;border-bottom:1px solid {c["rule"]}">',
        "<td>": f'<td style="padding:4px 8px 4px 0;border-bottom:1px solid {c["rule"]}">',
        "<td class='n'>": f'<td style="text-align:right;padding:4px 0;border-bottom:1px solid {c["rule"]}">',
        '<div class="item">': '<div style="margin:0 0 16px">',
        '<p class="t">': '<p style="margin:0;font-weight:600">',
        '<p class="m">': f'<p style="margin:0;font-size:14px;color:{c["mute"]}">',
        '<p class="sub">': f'<p style="margin:14px 0 4px;font-size:15px;font-weight:600;color:{c["mute"]}">',
        "<p class='sub'>": f'<p style="margin:14px 0 4px;font-size:15px;font-weight:600;color:{c["mute"]}">',
        "<a ": f'<a style="color:{c["accent"]}" ',
    }

    def dress(block):
        for k, v in style.items():
            block = block.replace(k, v)
        return block

    parts = []
    for lang in ("en", "id"):
        anchor = f'<a name="{lang}" id="{lang}"></a>'
        parts.append(anchor + f'<p style="margin:28px 0 4px;font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:{c["accent"]}">'
                     + ("English" if lang == "en" else "Bahasa Indonesia") + "</p>")
        for head, blocks in secs[lang]:
            parts.append(f'<h2 style="margin:22px 0 8px;font-size:20px;font-weight:600;color:{c["ink"]}">{esc(head)}</h2>')
            parts.extend(dress(b) for b in blocks)
        parts.append(f'<p style="margin:16px 0 0"><a style="color:{c["accent"]}" href="{url}">'
                     + ("Read this update on the website" if lang == "en" else "Baca kabar ini di situs web") + "</a></p>")
        if lang == "en":
            parts.append(f'<hr style="border:0;border-top:1px solid {c["rule"]};margin:32px 0 0">')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(labels['subject'])}</title></head>
<body style="margin:0;background:{c['paper']}">
<div style="max-width:640px;margin:0 auto;padding:28px 20px;font-family:Figtree,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.6;color:{c['ink']}">
<p style="margin:0;font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:{c['accent']}">Institute for Migrant Rights · Migration Jurisprudence from the South</p>
<h1 style="margin:8px 0 4px;font-size:28px;line-height:1.2;font-weight:600">{esc(labels['h1_en'])}</h1>
<p style="margin:0;color:{c['soft']}">{esc(labels['h1_id'])} · <a style="color:{c['accent']}" href="#id">Baca dalam bahasa Indonesia</a></p>
{''.join(parts)}
<p style="margin:32px 0 0;font-size:13px;color:{c['mute']}">Institute for Migrant Rights, Jl. Amalia Rubini 35, Sayang, Cianjur, Jawa Barat 43213, Indonesia.
You receive this because you signed up at theimr.org/updates/. / Anda menerima email ini karena mendaftar di theimr.org/updates/.</p>
</div></body></html>
"""


def email_text(labels, secs, url):
    def plain(b):
        b = re.sub(r"<li>", "- ", b)
        b = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', r"\2 (\1)", b)
        b = re.sub(r"</(p|li|tr|div|h2)>", "\n", b)
        b = re.sub(r"</t[dh]>", "  ", b)
        b = re.sub(r"<[^>]+>", "", b)
        return html.unescape(re.sub(r"\n{3,}", "\n\n", b)).strip()
    out = [labels["h1_en"], labels["h1_id"], ""]
    for lang in ("en", "id"):
        out.append("=== " + ("English" if lang == "en" else "Bahasa Indonesia") + " ===\n")
        for head, blocks in secs[lang]:
            out.append(head.upper())
            out.extend(plain(b) for b in blocks)
            out.append("")
        out.append(url + "\n")
    return "\n".join(out)


# ---------------------------------------------------------------- archive and feed
def list_issues():
    return sorted((p.parent.name for p in OUT_SITE.glob("*/summary.json")), reverse=True)


def write_index():
    issues = list_issues()
    rows = {"en": [], "id": []}
    for m in issues:
        s = json.loads((OUT_SITE / m / "summary.json").read_text(encoding="utf-8"))
        y, mo = int(m[:4]), int(m[5:])
        rows["en"].append(f'<li><a href="/updates/{m}/">{MONTHS_EN[mo-1]} {y}</a>: {num(s["decisions_new"], "en")} decisions, {num(s["laws_new"], "en")} laws and instruments</li>')
        rows["id"].append(f'<li><a href="/updates/{m}/">{MONTHS_ID[mo-1]} {y}</a>: {num(s["decisions_new"], "id")} putusan, {num(s["laws_new"], "id")} undang-undang dan instrumen</li>')
    body = (
        '<p class="eyebrow">Migration Jurisprudence from the South</p>'
        '<h1 lang="en">What’s new in the databases</h1><h1 lang="id">Kabar terbaru basis data</h1>'
        '<p class="lede" lang="en">A short monthly update on the court decisions, laws and instruments added to the IMR databases. It is put together automatically from the public record of changes on GitHub, so every number can be traced to the files themselves.</p>'
        '<p class="lede" lang="id">Kabar bulanan singkat tentang putusan pengadilan, undang-undang dan instrumen yang ditambahkan ke basis data IMR. Kabar ini disusun secara otomatis dari catatan perubahan yang terbuka di GitHub, sehingga setiap angka dapat ditelusuri ke berkasnya.</p>'
        + signup_form("en") + signup_form("id")
        + '<section class="s"><h2 lang="en">Issues</h2><h2 lang="id">Edisi</h2>'
        f'<ul lang="en">{"".join(rows["en"]) or "<li>The first issue appears at the start of next month.</li>"}</ul>'
        f'<ul lang="id">{"".join(rows["id"]) or "<li>Edisi pertama terbit pada awal bulan depan.</li>"}</ul>'
        '<p class="fine" lang="en">Also available as an <a href="/updates/feed.xml">RSS feed</a>.</p>'
        '<p class="fine" lang="id">Tersedia juga sebagai <a href="/updates/feed.xml">umpan RSS</a>.</p></section>')
    (OUT_SITE / "index.html").write_text(page(
        "What’s new in the databases",
        "Monthly update on new court decisions and laws in the Institute for Migrant Rights databases, in English and Indonesian.",
        f"{BASE_URL}/updates/", body), encoding="utf-8")

    items = []
    for m in issues[:24]:
        s = json.loads((OUT_SITE / m / "summary.json").read_text(encoding="utf-8"))
        pub = dt.datetime.fromisoformat(s["published"]).strftime("%a, %d %b %Y 06:00:00 +0000")
        items.append(f"<item><title>{esc(s['title_en'])}</title><link>{BASE_URL}/updates/{m}/</link>"
                     f"<guid isPermaLink=\"true\">{BASE_URL}/updates/{m}/</guid><pubDate>{pub}</pubDate>"
                     f"<description>{esc(s['brief_en'])}</description></item>")
    (OUT_SITE / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
        "<title>Institute for Migrant Rights: what’s new in the databases</title>\n"
        f"<link>{BASE_URL}/updates/</link>\n"
        "<description>Monthly update on new court decisions and laws in the IMR databases.</description>\n"
        "<language>en</language>\n" + "\n".join(items) + "\n</channel></rss>\n", encoding="utf-8")

    thanks = OUT_SITE / "thanks" / "index.html"
    thanks.parent.mkdir(parents=True, exist_ok=True)
    thanks.write_text(page("Thank you", "Thank you for signing up.", f"{BASE_URL}/updates/thanks/",
        '<p class="eyebrow">Updates</p><h1 lang="en">Thank you for signing up</h1><h1 lang="id">Terima kasih telah mendaftar</h1>'
        '<p class="lede" lang="en">You will receive the monthly update on new court decisions and laws. You can unsubscribe at any time with the link in each email.</p>'
        '<p class="lede" lang="id">Anda akan menerima kabar bulanan tentang putusan pengadilan dan undang-undang baru. Anda dapat berhenti berlangganan kapan saja melalui tautan di setiap email.</p>'
        '<p><a href="/updates/">← Updates</a> · <a href="/databases/">Databases</a></p>',
        '<meta name="robots" content="noindex">'), encoding="utf-8")

    sitemap = SITE / "sitemap.xml"
    if sitemap.exists():
        text = sitemap.read_text(encoding="utf-8")
        for loc in [f"{BASE_URL}/updates/"] + [f"{BASE_URL}/updates/{m}/" for m in issues]:
            if f"<loc>{loc}</loc>" not in text:
                text = text.replace("</urlset>", f"<url><loc>{loc}</loc></url>\n</urlset>")
        sitemap.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- sign-up strip on the database pages
SIGNUP_PAGES = ["index.html", "databases/index.html", "migration-law/index.html", "gcc/index.html",
                "east-asia/index.html", "southeast-asia/index.html", "countries-of-origin/index.html",
                "domestic-workers/index.html", "government-hate-speech/index.html",
                "government-hate-speech/elections/index.html", "court-decisions/index.html",
                "court-decisions/all/index.html", "publications.html"]
STRIP_START, STRIP_END = "<!-- imr-updates-signup -->", "<!-- /imr-updates-signup -->"


def signup_strip():
    """A compact bilingual sign-up band placed just above the footer of the database pages."""
    def one(lang):
        en = lang == "en"
        T = lambda e, i: e if en else i
        ph = T("Your email address", "Alamat email anda")
        if CONFIG.get("buttondown_username"):
            open_form = (f'<form action="https://buttondown.com/api/emails/embed-subscribe/{esc(CONFIG["buttondown_username"])}" '
                         f'method="post" target="_blank"><input type="hidden" name="tag" value="database-updates">'
                         f'<input type="hidden" name="tag" value="lang-{lang}">')
        else:
            name = "database-updates" if en else "database-updates-id"
            open_form = (f'<form name="{name}" method="POST" action="/updates/thanks/" data-netlify="true" netlify-honeypot="bot-field">'
                         f'<input type="hidden" name="form-name" value="{name}"><p hidden><label>Leave this empty <input name="bot-field"></label></p>')
        return (f'<div class="iu-{lang}" lang="{lang}"><p class="iu-t"><b>{T("Monthly email", "Email bulanan")}</b>: '
                f'{T("new court decisions and laws in the databases, in English and Indonesian.", "putusan pengadilan dan undang-undang baru dalam basis data, dalam bahasa Inggris dan Indonesia.")} '
                f'<a href="/updates/">{T("See past issues", "Lihat edisi sebelumnya")}</a></p>'
                f'{open_form}<input type="email" name="email" required autocomplete="email" placeholder="{ph}" aria-label="{ph}">'
                f'<button type="submit">{T("Sign up", "Daftar")}</button></form></div>')
    css = ("<style>.imr-updates{background:var(--nb-paper,#EEE9E5);border-top:1px solid var(--nb-rule,#C8BCB1);padding:22px 0;font-family:'Figtree',system-ui,sans-serif;font-size:16px;line-height:1.5;color:var(--nb-ink,#2E2116)}"
           ".imr-updates .iu-in{max-width:1120px;margin:0 auto;padding:0 24px}.imr-updates .iu-t{margin:0 0 10px}"
           ".imr-updates a{color:var(--nb-red,#8F5E12)}"
           ".imr-updates form{display:flex;flex-wrap:wrap;gap:8px;max-width:560px}"
           ".imr-updates input[type=email]{flex:1 1 220px;min-width:0;font:inherit;padding:8px 10px;border:1px solid var(--nb-rule,#C8BCB1);background:#fff}"
           ".imr-updates button{font:inherit;font-weight:600;padding:8px 16px;border:0;background:var(--nb-ink,#2E2116);color:#fff;cursor:pointer}"
           "html[lang=id] .imr-updates .iu-en{display:none}html:not([lang=id]) .imr-updates .iu-id{display:none}</style>")
    return (f'{STRIP_START}\n<aside class="imr-updates" aria-label="Monthly updates by email" data-noi18n>{css}'
            f'<div class="iu-in">{one("en")}{one("id")}</div></aside>\n{STRIP_END}')


def add_signup_strips():
    strip = signup_strip()
    for rel in SIGNUP_PAGES:
        path = SITE / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if STRIP_START in text:
            text = re.sub(re.escape(STRIP_START) + ".*?" + re.escape(STRIP_END), lambda _: strip, text, flags=re.S)
        else:
            anchor = text.find('<div class="imr-ridge"')
            if anchor < 0:
                anchor = text.rfind("<footer")
            if anchor < 0:
                continue
            text = text[:anchor] + strip + "\n" + text[anchor:]
        path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--month", help="YYYY-MM; default: last month")
    ap.add_argument("--ref", default="HEAD", help="branch or commit to read history from")
    args = ap.parse_args()
    today = dt.date.today()
    if args.month:
        y, m = map(int, args.month.split("-"))
    else:
        first = today.replace(day=1) - dt.timedelta(days=1)
        y, m = first.year, first.month
    month = f"{y:04d}-{m:02d}"
    start = f"{month}-01T00:00:00Z"
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    stop = f"{ny:04d}-{nm:02d}-01T00:00:00Z"

    base = commit_before(start, args.ref)
    since_note = None
    if not base:
        # The first month of the repository: compare with the commit that first brought the data in.
        base = git("log", "--reverse", "--format=%H", args.ref, "--", DECISIONS).splitlines()[0]
        since_note = git("show", "-s", "--format=%cs", base)
    end = commit_before(stop, args.ref) or git("rev-parse", args.ref)
    data = compare(base, end)

    labels = {"en": f"{MONTHS_EN[m-1]} {y}", "id": f"{MONTHS_ID[m-1]} {y}"}
    note_file = HERE / "notes" / f"{month}.json"
    notes = json.loads(note_file.read_text(encoding="utf-8")) if note_file.exists() else {}
    if since_note and not notes:
        notes = {"en": f"This first issue covers everything added since the databases moved to GitHub on {nice_date(since_note, 'en')}.",
                 "id": f"Edisi pertama ini mencakup semua yang ditambahkan sejak basis data pindah ke GitHub pada {nice_date(since_note, 'id')}."}
    secs = {lang: sections(data, labels[lang], lang, notes.get(lang)) for lang in ("en", "id")}
    url = f"{BASE_URL}/updates/{month}/"
    title_en = f"What’s new in the databases: {labels['en']}"
    title_id = f"Kabar terbaru basis data: {labels['id']}"

    # web page
    body = [f'<p class="eyebrow"><a href="/updates/" style="color:inherit;text-decoration:none"><span lang="en">Monthly updates</span><span lang="id">Kabar bulanan</span></a></p>',
            f'<h1 lang="en">{esc(title_en)}</h1><h1 lang="id">{esc(title_id)}</h1>']
    for lang in ("en", "id"):
        body.append(f'<div lang="{lang}">')
        for head, blocks in secs[lang]:
            body.append(f'<section class="s"><h2>{esc(head)}</h2>{"".join(blocks)}</section>')
        body.append("</div>")
    body.append(signup_form("en") + signup_form("id"))
    out = OUT_SITE / month
    out.mkdir(parents=True, exist_ok=True)
    brief_en = re.sub(r"<[^>]+>", "", " ".join(secs["en"][0][1][1:2]))
    (out / "index.html").write_text(page(title_en, html.unescape(brief_en)[:300], url, "\n".join(body)), encoding="utf-8")

    summary = {"month": month, "base_commit": base, "end_commit": end,
               "published": dt.date(ny, nm, 1).isoformat(), "title_en": title_en, "title_id": title_id,
               "brief_en": html.unescape(brief_en),
               "decisions_new": len(data["decisions_new"]), "decisions_checked": len(data["decisions_checked"]),
               "laws_new": sum(len(t["rows"]) for t in data["laws"]),
               "developments_new": len(data["developments"]), "incoming_new": data["incoming"]}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")

    # email
    mail = OUT_MAIL / month
    mail.mkdir(parents=True, exist_ok=True)
    elabels = {"subject": f"IMR databases: what’s new, {labels['en']} / Kabar terbaru, {labels['id']}",
               "h1_en": title_en, "h1_id": title_id}
    (mail / "email.html").write_text(email_html(month, elabels, secs, url), encoding="utf-8")
    (mail / "email.txt").write_text(email_text(elabels, secs, url), encoding="utf-8")
    (mail / "subject.txt").write_text(elabels["subject"] + "\n", encoding="utf-8")

    write_index()
    add_signup_strips()
    print(f"{month}: base {base[:7]} -> end {end[:7]}; {summary['decisions_new']} decisions, "
          f"{summary['laws_new']} laws, {summary['developments_new']} timeline entries")


if __name__ == "__main__":
    main()
