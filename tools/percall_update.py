#!/usr/bin/env python3
"""Register or update the Machine Room listing in the AI Product Index (110kc3/seo).

  python tools/percall_update.py register
  python tools/percall_update.py update
"""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

LISTING = Path(__file__).parent / "percall_listing.json"


def token():
    out = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True, text=True,
    ).stdout
    for line in out.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1]
    raise SystemExit("no github token")


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "register").lower()
    prefix = "[update]" if mode.startswith("upd") else "[register]"
    listing = json.loads(LISTING.read_text(encoding="utf-8"))
    body = "```json\n" + json.dumps(listing, indent=2, ensure_ascii=False) + "\n```"
    payload = json.dumps(
        {"title": f"{prefix} Machine Room", "body": body}
    ).encode()
    req = urllib.request.Request(
        "https://api.github.com/repos/110kc3/seo/issues",
        data=payload,
        headers={
            "Authorization": "Bearer " + token(),
            "Accept": "application/vnd.github+json",
            "content-type": "application/json",
            "user-agent": "machine-room-registrar",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    print(f"{prefix} issue:", d.get("number"), d.get("html_url"))


if __name__ == "__main__":
    main()
