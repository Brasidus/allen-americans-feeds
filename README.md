# Allen Americans calendar feeds

Auto-updating iCalendar (`.ics`) feeds for the [Allen Americans](https://allenamericans.com/) (ECHL) — produced by filtering the team's official all-games feed.

## Available feeds

| Feed | Subscription URL |
|------|------------------|
| Away games only | `https://raw.githubusercontent.com/Brasidus/allen-americans-feeds/main/allen-americans-away.ics` |

The team publishes their own home-games and all-games feeds at [allenamericans.com/schedule](https://allenamericans.com/schedule); only the away-only split is hosted here.

## How it stays current

A GitHub Actions cron runs daily at 6:43 AM Central during hockey season (Oct–June; dormant July–Sept), fetches the live source, regenerates the filtered file, and commits it back to this repo if anything changed. Subscribed calendars then refresh on their normal cadence (Google Calendar polls external feeds every 8–24 hours).

## Adding to Google Calendar

In Google Calendar:

1. Left sidebar → **+** next to "Other calendars" → **From URL**
2. Paste the subscription URL above → **Add calendar**
