#!/usr/bin/env python3
"""
Fitness First Singapore timetable scraper.

Pulls the public (no-login-required) timetable API for every club and
writes out classes.json / classes_min.json in the same schema the
Class Finder app expects:

    {"outlet": str, "day": "Mon".."Sun", "class": str,
     "start": "07:15am", "end": "08:15am", "instructor": str}

The endpoint is public — viewing the timetable never requires a member
session. Booking a class does, but we're only reading the schedule.

Run:
    pip install requests
    python3 scrape_timetable.py
"""

import json
import re
import time
import sys
from pathlib import Path

import requests

API_BASE = (
    "https://www.fitnessfirst.com/fitness-first/api/v2/"
    "%7BFAEC351B-47C0-4759-843F-EB7D6F5DB568%7D/timetable"
)

# exerpCenterIds for every SG club (confirmed against the live site).
# clubName is filled in from the API response itself, so this list only
# needs to stay in sync if Fitness First adds/removes a club.
CENTER_IDS = [
    "117", "109", "111", "121", "103", "110",
    "123", "118", "105", "108", "104", "124",
    "112", "115",
]

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.fitnessfirst.com/sg/en/timetable",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "culture": "en",
}


def clean_instructor(name):
    """API returns names like 'Ian Fung .' — strip the trailing marker."""
    if not name:
        return ""
    return re.sub(r"\s*\.\s*$", "", name).strip()


def fetch_center(center_id, timezone=8, retries=3):
    url = f"{API_BASE}?exerpCenterIds={center_id}&searchTerm=&timezone={timezone}"
    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("isSuccess"):
                raise RuntimeError(f"API returned isSuccess=false for center {center_id}")
            return data["data"]["timetable"]
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch center {center_id}: {last_err}")


def parse_timetable(timetable_days):
    """Flatten one center's timetable payload into our row schema."""
    rows = []
    for day_entry in timetable_days:
        day_short = day_entry["dayShort"]  # "Mon".."Sun"
        for session_block in ("morning", "afternoon", "evening"):
            for session in day_entry.get(session_block, []):
                time_text = session.get("timeText") or ""
                parts = [p.strip() for p in time_text.split(" - ")]
                start, end = (parts[0], parts[1]) if len(parts) == 2 else (None, None)
                rows.append({
                    "outlet": session.get("clubName", "").strip(),
                    "day": day_short,
                    "class": session.get("title", "").strip(),
                    "start": start,
                    "end": end,
                    "instructor": clean_instructor(session.get("instructor")),
                })
    return rows


def main():
    all_rows = []
    for i, center_id in enumerate(CENTER_IDS, 1):
        print(f"[{i}/{len(CENTER_IDS)}] fetching center {center_id}...", file=sys.stderr)
        timetable = fetch_center(center_id)
        rows = parse_timetable(timetable)
        all_rows.extend(rows)
        print(f"    -> {len(rows)} sessions", file=sys.stderr)
        time.sleep(0.5)  # be a polite scraper

    out_dir = Path(__file__).parent
    (out_dir / "classes.json").write_text(json.dumps(all_rows, indent=0), encoding="utf-8")
    (out_dir / "classes_min.json").write_text(
        json.dumps(all_rows, separators=(",", ":")), encoding="utf-8"
    )

    outlets = sorted(set(r["outlet"] for r in all_rows))
    classes = sorted(set(r["class"] for r in all_rows))
    instructors = sorted(set(r["instructor"] for r in all_rows if r["instructor"]))
    print(f"\nDone: {len(all_rows)} sessions across {len(outlets)} centers, "
          f"{len(classes)} class types, {len(instructors)} instructors.", file=sys.stderr)


if __name__ == "__main__":
    main()
