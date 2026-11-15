"""Regenerate allen-americans-away.ics from Allen Americans' live all-games feed.

Fetches https://allenamericans.com/schedule-all.ics, filters to away games
(SUMMARY starts with "Allen Americans @ "), and writes the result to
allen-americans-away.ics in the repo root.

Run by the allen-americans-away-ics.yml GitHub Action; the workflow commits
the file if it changed.
"""

from __future__ import annotations

import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SOURCE_URL = "https://allenamericans.com/schedule-all.ics"
OUTPUT_PATH = Path(__file__).parent / "allen-americans-away.ics"


BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def fetch_source() -> str:
    # allenamericans.com began refusing GitHub-runner IPs (HTTP 405) on 2026-11-09, which
    # stalled this calendar. Try direct, then fall back to the mlo-echl-proxy Worker (an
    # off-GitHub IP), the same approach as claude-workspace scripts/echl_http.py.
    try:
        return _get(SOURCE_URL)
    except Exception:
        proxy = os.environ.get("ECHL_PROXY", "").strip().rstrip("/")
        if not proxy:
            raise
        return _get(f"{proxy}?url={urllib.parse.quote(SOURCE_URL, safe='')}")


def filter_away_events(ics: str) -> str:
    header_match = re.search(r"^(.*?)(?=BEGIN:VEVENT)", ics, re.DOTALL)
    if not header_match:
        raise RuntimeError("Source .ics has no VEVENT block")
    header = header_match.group(1)

    events = re.findall(r"BEGIN:VEVENT.*?END:VEVENT\r?\n?", ics, re.DOTALL)
    away = [e for e in events if re.search(r"^SUMMARY:Allen Americans @ ", e, re.MULTILINE)]

    if not away:
        raise RuntimeError(f"No away events found among {len(events)} total events")

    # Drop DTSTAMP lines so cosmetic timestamp drift doesn't trigger commits.
    away = [re.sub(r"^DTSTAMP:.*\r?\n?", "", e, flags=re.MULTILINE) for e in away]
    header = re.sub(r"^DTSTAMP:.*\r?\n?", "", header, flags=re.MULTILINE)

    return header + "".join(away) + "END:VCALENDAR\n"


def main() -> int:
    source = fetch_source()
    output = filter_away_events(source)
    OUTPUT_PATH.write_text(output)
    away_count = output.count("BEGIN:VEVENT")
    print(f"Wrote {away_count} away events to {OUTPUT_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
