"""Turn the East Asia candidates into IMR Court Decisions entries (status C, harvest).

Scope chosen by IMR: apex and appeal courts, plus every case with a farm or fishing term.
Writes imr_candidates.json here (the site's own field names) and
data/east-asia/incoming/migration-cases-top-courts-2026-11-17.csv
(the decisions.csv columns). Entries are unchecked: name, court, date and topic only.
"""
import csv, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sitefilter import site, clean, level  # noqa: E402
from names_en import N  # noqa: E402

INCOMING = HERE.parent.parent / "data" / "east-asia" / "incoming"
KR_ROM = [("구합", "Guhap"), ("구단", "Gudan"), ("가합", "Gahap"), ("가단", "Gadan"), ("헌마", "Hun-Ma"), ("헌바", "Hun-Ba"), ("헌가", "Hun-Ka"), ("헌사", "Hun-Sa"), ("헌라", "Hun-Ra"),
          ("헌아", "Hun-A"), ("두", "Du"), ("누", "Nu"), ("도", "Do"), ("다", "Da"), ("구", "Gu"), ("나", "Na"),
          ("노", "No"), ("므", "Meu"), ("마", "Ma"), ("부", "Bu"), ("카", "Ka"), ("초", "Cho"), ("모", "Mo"),
          ("그", "Geu"), ("아", "A"), ("재", "Jae"), ("오", "O"), ("스", "Seu"), ("즈", "Jeu"), ("느", "Neu"), ("드", "Deu")]
JP_ERA = {"令和": "Reiwa", "平成": "Heisei", "昭和": "Showa"}
JP_KIND = {"行ツ": "Gyo-Tsu", "行ヒ": "Gyo-Hi", "行コ": "Gyo-Ko", "行ウ": "Gyo-U", "行ケ": "Gyo-Ke", "行ス": "Gyo-Su",
           "行フ": "Gyo-Fu", "行ト": "Gyo-To", "行ク": "Gyo-Ku", "行タ": "Gyo-Ta", "行テ": "Gyo-Te", "オ": "O", "ネ": "Ne",
           "ツ": "Tsu", "あ": "A", "う": "U", "ク": "Ku", "許": "Kyo", "受": "Ju", "し": "Shi", "さ": "Sa", "ラ": "Ra",
           "テ": "Te", "ム": "Mu", "の": "No", "く": "Ku", "ヒ": "Hi", "ウ": "U", "せ": "Se", "も": "Mo", "わ": "Wa"}
COURTS = {"대법원": "Supreme Court of Korea", "헌법재판소 전원재판부": "Constitutional Court of Korea",
          "헌법재판소 지정재판부": "Constitutional Court of Korea (designated panel)", "서울고등법원": "Seoul High Court",
          "부산고등법원": "Busan High Court", "대구고등법원": "Daegu High Court", "광주고등법원": "Gwangju High Court",
          "대전고등법원": "Daejeon High Court", "수원고등법원": "Suwon High Court",
          "Court of Appeal": "Court of Appeal, Hong Kong", "Court of Final Appeal": "Court of Final Appeal, Hong Kong",
          "終審法院": "Court of Final Appeal, Macau", "中級法院": "Court of Second Instance, Macau"}
JP_HC = {"東京": "Tokyo", "大阪": "Osaka", "名古屋": "Nagoya", "福岡": "Fukuoka", "広島": "Hiroshima", "仙台": "Sendai",
         "札幌": "Sapporo", "高松": "Takamatsu"}


def mo_name(t):
    """English name for a Macau judgment from its subject keywords (unchecked)."""
    if re.search(r"驅逐|非法移民|遣返", t):
        n = "Expulsion of an illegal immigrant"
    elif re.search(r"禁止入境|禁止進入", t):
        n = "Entry ban"
    elif re.search(r"非本地勞工|外地僱員|勞工", t):
        n = "Non-resident worker and family residence"
    elif re.search(r"永久性居民|居留權", t):
        n = "Permanent residence and right of abode"
    elif re.search(r"居留", t):
        if re.search(r"續期", t):
            n = "Renewal of residence permit"
        elif re.search(r"廢止|取消|失效|無效|註銷", t):
            n = "Revocation or lapse of residence permit"
        else:
            n = "Residence permit"
        if re.search(r"團聚|夫妻|家庭|家團", t):
            n += " (family reunion)"
        elif re.search(r"投資", t):
            n += " (investor)"
        elif re.search(r"犯罪前科", t):
            n += " (criminal record)"
    elif re.search(r"逗留", t):
        n = "Permission to stay"
    else:
        n = "Immigration case"
    if t.startswith("效力之中止") or "效力中止" in t[:20]:
        n = "Suspension of effects: " + n[0].lower() + n[1:]
    if "統一司法見解" in t:
        n += " (uniform jurisprudence)"
    if t.startswith("刑事"):
        n = "Criminal appeal: " + n[0].lower() + n[1:]
    return n


def court_en(c):
    if c in COURTS:
        return COURTS[c]
    if c.startswith("最高裁判所"):
        return "Supreme Court of Japan" + (" (Grand Bench)" if "大法廷" in c else "")
    for k, v in JP_HC.items():
        if c.startswith(k + "高等裁判所"):
            return v + " High Court" + (" (" + c.split("支部")[0].replace(k + "高等裁判所", "") + " branch)" if "支部" in c else "")
    for k, v in COURTS.items():
        if c.startswith(k):
            return v
    return LOWER.get(c, c)


LOWER = {
    "서울행정법원": "Seoul Administrative Court",
    "대전지방법원": "Daejeon District Court",
    "광주지방법원": "Gwangju District Court",
    "수원지방법원": "Suwon District Court",
    "대구지방법원포항지원": "Daegu District Court (Pohang branch)",
    "横浜地方裁判所": "Yokohama District Court",
}


def cite(x):
    n = x["case_no"]
    if x["jurisdiction"] == "KR":
        for k, v in KR_ROM:
            n = n.replace(k, v)
        return n
    if x["jurisdiction"] == "JP":
        m = re.match(r"(令和|平成|昭和)(元|\d+)\((.+?)\)(\d+)", n)
        if m:
            return f"{JP_ERA[m.group(1)]} {1 if m.group(2) == '元' else m.group(2)} ({JP_KIND.get(m.group(3), m.group(3))}) No. {m.group(4)}"
    return n


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40].strip("-")


SMALL = {"v", "of", "and", "for", "the", "in", "on", "by", "to", "a"}


def hk_name(t):
    words = re.split(r"(\s+)", t.strip())
    out = []
    for w in words:
        lw = w.lower()
        if w.isspace():
            out.append(w)
        elif lw in ("v.", "v"):
            out.append("v.")
        elif lw in SMALL and out:
            out.append(lw)
        else:
            out.append(w[:1].upper() + w[1:].lower() if w.isupper() else w)
    return "".join(out)


TOPICS = [  # (key, test on text, plain_en, plain_id, situations, stages, sector)
    ("nonref", r"non-refoulement|torture claim|NON-REFOULEMENT|TORTURE", "Non-refoulement (torture and persecution) claim: challenge to the refusal of protection.",
     "Klaim non-refoulement (penyiksaan dan persekusi): gugatan atas penolakan perlindungan.", ["residence"], [4], "asylum seekers and torture claimants"),
    ("refugee", r"難民|난민|難民", "Refugee status: challenge to a refusal of refugee recognition.",
     "Status pengungsi: gugatan atas penolakan pengakuan sebagai pengungsi.", ["residence"], [4], "asylum seekers and refugees"),
    ("detention", r"仮放免|収容|보호명령|긴급보호|인신보호|제63조|detention", "Immigration detention.", "Penahanan imigrasi.", ["arrest"], [4], ""),
    ("deport", r"退去|강제퇴거|驅逐出境|deportation|removal", "Deportation or removal of a foreign national.",
     "Deportasi atau pengusiran warga negara asing.", ["residence"], [4], ""),
    ("labour", r"고용허가|외국인근로자|연수|技能実習|労働者|domestic helper|非本地勞工|外地僱員|非法僱用",
     "Migrant workers: rules on foreign workers' employment and stay.", "Pekerja migran: aturan tentang kerja dan tinggal pekerja asing.", ["employer"], [3], ""),
    ("traffic", r"人身取引|인신매매|販賣人口|trafficking", "Human trafficking.", "Perdagangan orang.", ["forced"], [3], ""),
    ("nationality", r"国籍|국적|帰化|귀화|right of abode|永住|재외동포", "Nationality, naturalisation or permanent status.",
     "Kewarganegaraan, naturalisasi atau status tetap.", ["residence"], [5], ""),
    ("visa", r"在留|체류|사증|査証|上陸|再入国|居留許可|逗留許可|禁止入境|입국|결혼이민", "Visa, entry or residence permit for a foreign national.",
     "Visa, izin masuk atau izin tinggal bagi warga negara asing.", ["residence"], [3], ""),
    ("emig", r"旅券|여권|해외이주|被爆者", "Emigration, passports and rights of nationals abroad.",
     "Emigrasi, paspor dan hak warga negara di luar negeri.", ["passport"], [2], ""),
    ("crime", r"출입국관리법위반|出入国管理|非法入境|非法移民|외국인등록|外国人登録", "Criminal case under immigration law.",
     "Perkara pidana berdasarkan hukum keimigrasian.", ["arrest"], [3], ""),
]


def topic(text, terms):
    for src in (text, terms):
        for t in TOPICS:
            if re.search(t[1], src):
                return t
    return ("other", "", "Migration-related case (topic to be confirmed).", "Perkara terkait migrasi (pokok perkara akan dikonfirmasi).", [], [], "")


def branch(x, name):
    c = x["court"]
    if "헌법재판소" in c:
        return "constitutional"
    if "(criminal)" in name or "被告" in x["title"] or re.search(r"위반$|위반\)|위반·|위반ㆍ", x["title"]) or "HKCC" in x["case_no"] or "刑事" in x["title"]:
        return "criminal"
    if x["jurisdiction"] == "HK" and not re.search(r"DIRECTOR|BOARD|SECRETARY|COMMISSIONER|TORTURE|IMMIGRATION|PETITION", x["title"], re.I):
        return "private"
    return "administrative"


SRC = {"KR": "law.go.kr (National Law Information Center)", "JP": "Courts in Japan (courts.go.jp)", "HK": "HKLII",
       "MO": "Courts of Macau (court.gov.mo)"}


def build(rows):
    out = {}
    for x in rows:
        if not site(x):
            continue
        j = x["jurisdiction"]
        t = clean(x["title"])
        if j == "HK":
            name = hk_name(t)
        elif j == "MO":
            name = mo_name(t)
        else:
            name = N.get(t)
            if not name:
                continue
        c = cite(x)
        yr = x["date"][:4]
        if j != "HK" and c:
            name = re.sub(r" \(appeal\)$", "", name) + ", " + c
        m = re.match(r"\[(\d{4})\] (HK\w+) (\d+)", c)
        key = f"{m.group(2)}-{m.group(1)}-{m.group(3)}" if m else c
        base = f"c-h-{j.lower()}-{slug(key) or slug(name)}" + (f"-{yr}" if yr and not m else "")
        br = branch(x, name)
        tp = topic(x["title"] + " " + name, x["matched_terms"])
        if br == "criminal" and tp[0] != "traffic":
            tp = next(t for t in TOPICS if t[0] == "crime")
        sector = tp[6]
        if j == "HK" and "domestic helper" in x["matched_terms"]:
            sector = "domestic work"
        if x["farm_terms"]:
            sector = sector or "agriculture or fishing"
        e = {"id": base, "name": name, "court": court_en(x["court"]), "cc": j, "region": "asia", "forum": "destination",
             "tier": "national", "level": level(x) or "first", "date": x["date"] or yr, "cite": c, "sector": sector,
             "issues": [], "situations": tp[4], "stages": tp[5], "outcome": "unknown", "follow": "unknown", "status": "C",
             "q": "", "q_id": "", "held": "", "plain": tp[2], "plain_id": tp[3], "harvest": True, "branch": br,
             "tools": [], "args": [], "after": [], "src": [{"t": SRC[j], "u": x["url"]}],
             "title_local": t if j != "HK" else ""}
        i = 2
        while e["id"] in out:
            e["id"] = f"{base}-{i}"; i += 1
        out[e["id"]] = e
    return list(out.values())


COLS = ["id", "name", "court", "tier", "forum", "level", "country", "region", "date", "citation", "branch", "sector", "issues",
        "situations", "stages", "outcome", "follow_up", "arguments", "status", "reasoning_tools", "question", "holding",
        "plain_en", "plain_id", "sources"]


def to_row(e):
    return {"id": e["id"], "name": e["name"], "court": e["court"], "tier": e["tier"], "forum": e["forum"], "level": e["level"],
            "country": e["cc"], "region": e["region"], "date": e["date"], "citation": e["cite"], "branch": e["branch"],
            "sector": e["sector"], "issues": ";".join(e["issues"]), "situations": ";".join(e["situations"]),
            "stages": ";".join(map(str, e["stages"])), "outcome": e["outcome"], "follow_up": e["follow"], "arguments": "",
            "status": e["status"], "reasoning_tools": "", "question": "", "holding": e["held"], "plain_en": e["plain"],
            "plain_id": e["plain_id"], "sources": " | ".join(s["u"] for s in e["src"])}


def main():
    rows = list(csv.DictReader(open(INCOMING / "migration-cases-all-2026-11-17.csv", encoding="utf-8")))
    ents = build(rows)
    json.dump(ents, open(HERE / "imr_candidates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    with open(INCOMING / "migration-cases-top-courts-2026-11-17.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, COLS)
        w.writeheader()
        w.writerows(to_row(e) for e in ents)
    from collections import Counter
    print(len(ents), Counter(e["cc"] for e in ents), Counter(e["level"] for e in ents))


if __name__ == "__main__":
    main()
