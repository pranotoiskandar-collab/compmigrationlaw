"""Helpers shared by the publish-time steps."""
import csv
import io
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
SITE = ROOT / "site"
BASE = "https://theimr.org"
COUNTRIES = json.loads((ROOT / "tools" / "publish" / "countries.json").read_text(encoding="utf-8"))
BY_ISO2 = {c["iso2"]: c for c in COUNTRIES}
# Codes the court decisions use for international and regional bodies
BODIES = {"XA": "Inter-American system", "XF": "African human rights system", "XI": "International Court of Justice",
          "XM": "Inter-American system (Mercosur states)"}
BODIES_ID = {"XA": "Sistem Inter-Amerika", "XF": "Sistem hak asasi manusia Afrika", "XI": "Mahkamah Internasional",
             "XM": "Sistem Inter-Amerika (negara Mercosur)"}


def norm(s):
    return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())


_LOOK = {}
for _c in COUNTRIES:
    for _n in [_c["iso2"], _c["iso3"], _c["en"], *_c["aliases"]]:
        _LOOK.setdefault(norm(_n), _c["iso2"])


def iso2(value):
    """ISO 3166-1 alpha-2 code for a name, ISO-2 or ISO-3 code; None if it is not a country."""
    v = (value or "").strip()
    if v in BODIES:
        return v
    return _LOOK.get(norm(v)) if v else None


def read_csv(path):
    text = path.read_text(encoding="utf-8").lstrip("﻿")
    return list(csv.DictReader(io.StringIO(text)))


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8")


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def ld_blocks(html):
    """(start, end, parsed JSON) for every JSON-LD script in a page."""
    out = []
    for m in re.finditer(r'(<script type="application/ld\+json">)(.*?)(</script>)', html, re.S):
        try:
            out.append((m.start(2), m.end(2), json.loads(m.group(2))))
        except ValueError:
            pass
    return out


def name(code, lang="en"):
    if code in BODIES:
        return (BODIES_ID if lang == "id" else BODIES)[code]
    c = BY_ISO2.get(code)
    return (c["id"] if lang == "id" else c["en"]) if c else code
