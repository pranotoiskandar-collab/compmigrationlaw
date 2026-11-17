"""Copy the data files into the site before Netlify publishes it.

data/<database>/<file>  ->  site/<database>/data/<file>

Files inside any "incoming/" folder are not published: they wait for
review and for the database page to be rebuilt.
"""
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = ROOT / "site"

copied = 0
download_only = set()
for source in sorted(DATA.rglob("*")):
    if not source.is_file():
        continue
    relative = source.relative_to(DATA)
    if "incoming" in relative.parts or source.name.startswith(".") or source.suffix == ".md":
        continue
    database = relative.parent
    if not (SITE / database).is_dir():
        download_only.add(str(database))
    target = SITE / database / "data" / relative.name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    copied += 1

for database in sorted(download_only):
    print(f"Note: data/{database}/ has no page folder in site/; its files are published as downloads only")
print(f"Copied {copied} data files into site/")
