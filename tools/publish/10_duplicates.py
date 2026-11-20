"""Remove the pages of merged duplicate court decisions and redirect their addresses."""
import shutil
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import DATA, SITE, read_csv  # noqa: E402

pairs = [(r["removed_id"], r["kept_id"]) for r in read_csv(DATA / "court-decisions" / "duplicates.csv")]
lines = []
for gone, kept in pairs:
    page = SITE / "court-decisions" / "d" / gone
    if page.is_dir():
        shutil.rmtree(page)
    lines.append(f"/court-decisions/d/{gone}/  /court-decisions/d/{kept}/  301!")
    lines.append(f"/court-decisions/d/{gone}  /court-decisions/d/{kept}/  301!")
redirects = SITE / "_redirects"
text = redirects.read_text(encoding="utf-8") if redirects.exists() else ""
new = [l for l in lines if l not in text]
if new:
    redirects.write_text(text.rstrip("\n") + "\n\n# Merged duplicate court decisions (data/court-decisions/duplicates.csv)\n" + "\n".join(new) + "\n", encoding="utf-8")
print(f"  {len(pairs)} duplicate decision pages redirected")
