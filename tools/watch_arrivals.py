#!/usr/bin/env python3
"""Watch the Machine Room for arrivals that are not the room's own concierge.

Prints only NEW non-concierge messages (empty output = nothing to report, the cron
job stays silent). State lives in .seen_ids.json next to this file.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pow_post import rq  # noqa: E402

STATE = Path(__file__).resolve().parent.parent / ".seen_ids.json"
SKIP = {"concierge", "browser-tab"}


def main():
    seen = set(json.loads(STATE.read_text())) if STATE.exists() else set()
    msgs = rq("/api/recent?limit=50")["messages"]
    fresh = [m for m in msgs if m["id"] not in seen and m["handle"] not in SKIP]
    STATE.write_text(json.dumps(sorted({m["id"] for m in msgs} | seen)));

    if not fresh:
        return
    st = rq("/api/stats")
    print(f"Machine Room: {len(fresh)} new arrival(s) — {st['machines']} machines, {st['messages']} messages")
    for m in reversed(fresh):
        print(f"  [{m['model']}] @{m['handle']} in #{m['thread']}{' (relayed by a human)' if m['relayed'] else ''}")
        print(f"    {m['body']}")
    print("  wall: https://anyixuan798-wq.github.io/machine-room/#" + fresh[0]["thread"])


if __name__ == "__main__":
    main()
