"""Regenerate allen-americans-away.ics from Allen Americans' live all-games feed.

Fetches https://allenamericans.com/schedule-all.ics, filters to away games
(SUMMARY starts with "Allen Americans @ "), and writes the result to
allen-americans-away.ics in the repo root.

Run by the allen-americans-away-ics.yml GitHub Action; the workflow commits
the file if it changed.
"""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

SOURCE_URL = "https://allenamericans.com/schedule-all.ics"
OUTPUT_PATH = Path(__file__).parent / "allen-americans-away.ics"


def fetch_source() -> str:
    req = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "mlo-daily-sales-report/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


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
