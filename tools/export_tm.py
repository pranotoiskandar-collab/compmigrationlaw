"""Export the site's English -> Indonesian translations as a translation memory.

Reads window.SITE_I18N from site/assets/lang.js and writes
volunteers/translation-memory-en-id.csv (one row per segment), so translators
of new languages can reuse the reviewed Indonesian wording and see every string
the site needs. Run again after lang.js changes:

    python3 tools/export_tm.py
"""
import csv, json, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
src = (root / "site/assets/lang.js").read_text(encoding="utf-8")
m = re.match(r"\s*window\.SITE_I18N\s*=\s*", src)
obj, _ = json.JSONDecoder().raw_decode(src[m.end():])
rows = sorted((k, v) for k, v in obj["id"].items() if not k.startswith("__") and isinstance(v, str))
out = root / "volunteers/translation-memory-en-id.csv"
with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["en", "id"])
    w.writerows(rows)
print(f"{len(rows)} segments -> {out.relative_to(root)}")
