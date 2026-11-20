"""Place a digest in Buttondown as a DRAFT. It never sends.

    BUTTONDOWN_API_KEY=... python3 tools/digest/buttondown_draft.py 2026-11

The draft appears under Emails > Drafts in Buttondown, where one person reads it
and presses Send (or schedules it). Run by .github/workflows/digest-draft.yml.
"""
import json
import os
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]


def main():
    key = os.environ.get("BUTTONDOWN_API_KEY", "").strip()
    if not key:
        print("No BUTTONDOWN_API_KEY: nothing to do.")
        return
    for month in sys.argv[1:]:
        folder = ROOT / "newsletter" / month
        subject = (folder / "subject.txt").read_text(encoding="utf-8").strip()
        body = (folder / "email.html").read_text(encoding="utf-8")
        payload = json.dumps({"subject": subject, "body": body, "status": "draft"}).encode()
        request = urllib.request.Request(
            "https://api.buttondown.com/v1/emails", data=payload, method="POST",
            headers={"Authorization": f"Token {key}", "Content-Type": "application/json"})
        with urllib.request.urlopen(request) as response:
            created = json.load(response)
        print(f"{month}: draft created in Buttondown (status {created.get('status')}, id {created.get('id')})")
        if created.get("status") not in (None, "draft"):
            sys.exit(f"Unexpected status {created.get('status')!r}: check Buttondown at once.")


if __name__ == "__main__":
    main()
