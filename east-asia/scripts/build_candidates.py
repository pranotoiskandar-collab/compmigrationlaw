"""Build east-asia/tables/candidates.csv from the raw browser exports in tables/raw/.

Each raw file is one source's search hits, deduplicated. This script normalises them
into one candidates table, keeps only migration matches (Korea needs a title filter,
because law.go.kr searches full text) and flags farm and fishing terms in titles.
"""
import csv, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "tables" / "raw"
KW = json.load(open(HERE / "keywords.json", encoding="utf-8"))
RETRIEVED = "2026-11-17"
COLS = ["jurisdiction", "source", "court", "case_no", "date", "title", "url", "lang",
        "matched_terms", "farm_terms", "retrieved"]


def farm(j, text):
    """Farm and fishing terms found in text. Latin-script terms must match whole words."""
    hits = []
    for t in KW.get(j, {}).get("farm", []):
        if t.isascii():
            if re.search(r"\b" + re.escape(t) + r"\b", text, re.I):
                hits.append(t)
        elif t in text:
            hits.append(t)
    return ";".join(hits)


ERA = {"令和": 2018, "平成": 1988, "昭和": 1925}


def jp_date(s):
    m = re.search(r"(令和|平成|昭和)(元|\d+)年(\d+)月(\d+)日", s)
    if not m:
        return ""
    y = ERA[m.group(1)] + (1 if m.group(2) == "元" else int(m.group(2)))
    return f"{y:04d}-{int(m.group(3)):02d}-{int(m.group(4)):02d}"


def dotted_date(s):
    m = re.search(r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.", s)
    return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else ""


def japan():
    for r in csv.DictReader(open(RAW / "jp_courts.csv", encoding="utf-8")):
        if r["category"].startswith("知"):  # intellectual property courts
            continue
        p1, p2 = r["case"], r["date_court"]
        case_no, _, title = p1.partition(" ")
        court = re.sub(r"^.*?日\s*", "", p2).split(" ")[0]
        yield dict(jurisdiction="JP", source="courts.go.jp (" + r["category"] + ")", court=court,
                   case_no=case_no, date=jp_date(p2), title=title, url=r["detail_url"], lang="ja",
                   matched_terms=r["terms"], farm_terms=farm("JP", p1))


KR_TITLE = re.compile(r"난민|출입국|강제퇴거|체류|사증|귀화|국적|외국인|고용허가|출국|입국|인신매매|이주|결혼이민|재외동포|보호명령취소|여권")
KR_STRONG = ["고용허가", "체류자격", "출입국관리법", "강제퇴거", "난민법", "외국인보호소", "결혼이민"]


def korea():
    for r in csv.DictReader(open(RAW / "kr_lawgo.csv", encoding="utf-8")):
        terms = r["terms"].split(";")
        strong = [t for t in terms if t in KR_STRONG]
        text = r["title"]
        keep = bool(KR_TITLE.search(text)) or ("외국인근로자" in terms and strong) or len(strong) >= 2
        if not keep:
            continue
        meta = r["meta"].strip("[]")
        if r["kind"] == "prec":
            court = meta.split(" ")[0]
            m = re.search(r"선고\s+(\S+)", meta)
            case_no = m.group(1) if m else ""
            url = "https://www.law.go.kr/LSW/precInfoP.do?precSeq=" + r["id"]
        else:
            court = "헌법재판소 " + meta.split(" ")[0]
            case_no = meta.split(" ")[1].rstrip(",") if " " in meta else ""
            url = "https://www.law.go.kr/LSW/detcInfoP.do?detcSeq=" + r["id"]
        yield dict(jurisdiction="KR", source="law.go.kr (" + ("판례" if r["kind"] == "prec" else "헌재결정례") + ")",
                   court=court, case_no=case_no, date=dotted_date(meta), title=text, url=url, lang="ko",
                   matched_terms=r["terms"], farm_terms=farm("KR", text))


KR_FARM_KEEP = re.compile(r"급여|요양|해고|위자료|대지급금|평균임금|사증|산재|임금|보험급여")


def korea_farm():
    """Targeted searches for foreign farm, livestock and fishing workers (law.go.kr precedents)."""
    f = RAW / "kr_lawgo_farm.csv"
    if not f.exists():
        return
    for r in csv.DictReader(open(f, encoding="utf-8")):
        if not KR_FARM_KEEP.search(r["title"]):
            continue
        terms = r["terms"].split(";")
        if terms == ["계절근로"] and "계절" not in r["title"]:
            continue
        meta = r["meta"].strip("[]")
        m = re.match(r"(\S+?)(?:\s+\d{4}\.|\s+\d{2,4}[가-힣])", meta)
        court = meta.split(" ")[0]
        m2 = re.search(r"(\d{2,4}[가-힣]+\d+)", meta)
        farm_hits = sorted({w for t in terms for w in KW["KR"]["farm"] if w in t} | {"선원" for t in terms if "선원" in t})
        yield dict(jurisdiction="KR", source="law.go.kr (판례, farm search)", court=court, case_no=m2.group(1) if m2 else "",
                   date=dotted_date(meta), title=r["title"], url="https://www.law.go.kr/LSW/precInfoP.do?precSeq=" + r["id"],
                   lang="ko", matched_terms=r["terms"], farm_terms=";".join(farm_hits) or "농업")


MONTHS = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def hk_date(s):
    m = re.match(r"(\d{1,2}) (\w{3}),? (\d{4})", s.strip())
    return f"{m.group(3)}-{MONTHS.get(m.group(2), 0):02d}-{int(m.group(1)):02d}" if m else ""


def hongkong():
    seen = {}
    for f in sorted(RAW.glob("hk_hklii_*.csv")):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if "/cases/" not in r["href"]:
                continue
            if r["href"] in seen:
                seen[r["href"]]["matched_terms"] += ";" + r["term"]
                continue
            seen[r["href"]] = dict(jurisdiction="HK", source="HKLII", court=r["db"], case_no=r["cite"],
                                   date=hk_date(r["date"]), title=r["title"], url="https://www.hklii.hk" + r["href"],
                                   lang="en", matched_terms=r["term"], farm_terms=farm("HK", r["title"]))
    yield from seen.values()


MO_COURT = {"tui": "終審法院", "tsi": "中級法院", "ta": "行政法院"}


def macau():
    f = RAW / "mo_court.csv"
    if not f.exists():
        return
    seen = {}
    for r in csv.DictReader(open(f, encoding="utf-8")):
        k = (r["court"], r["num"])
        if k in seen:
            if r["term"] not in seen[k]["matched_terms"]:
                seen[k]["matched_terms"] += ";" + r["term"]
            continue
        d = re.match(r"(\d{2})/(\d{2})/(\d{4})", r["date"])
        seen[k] = dict(jurisdiction="MO", source="court.gov.mo", court=MO_COURT.get(r["court"], r["court"]),
                       case_no=r["num"], date=f"{d.group(3)}-{d.group(2)}-{d.group(1)}" if d else r["date"],
                       title=(r["type"] + " " + r["subj"]).strip(), url=("https://www.court.gov.mo" + r["pdf"]) if r["pdf"] else "",
                       lang="zh", matched_terms=r["term"], farm_terms=farm("MO", r["subj"]))
    yield from seen.values()


def main():
    rows = [*korea(), *japan(), *hongkong(), *macau()]
    seen = {r["url"] for r in rows}
    for r in korea_farm():
        if r["url"] in seen:
            for x in rows:
                if x["url"] == r["url"]:
                    x["farm_terms"] = r["farm_terms"]
        else:
            rows.append(r)
    for r in rows:
        r["retrieved"] = RETRIEVED
    rows.sort(key=lambda r: (r["jurisdiction"], r["date"]), reverse=False)
    with open(HERE / "tables" / "candidates.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, COLS)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(len(rows), Counter(r["jurisdiction"] for r in rows), "farm:", sum(1 for r in rows if r["farm_terms"]))


if __name__ == "__main__":
    main()
