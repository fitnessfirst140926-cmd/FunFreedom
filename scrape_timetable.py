#!/usr/bin/env python3
"""
Fitness First Singapore timetable + availability scraper.

Unlike the previous version, this pulls from the Exerp member booking
platform (fitnessfirst.exerp.site), which requires an authenticated
session but returns real-time class availability: how many people are
booked, total capacity, and waiting-list count.

Because this uses a real member login, credentials are read from
environment variables (set as GitHub Secrets in the workflow) rather
than hardcoded. Be mindful this runs against a personal account on a
schedule — if FF ever rate-limits or flags automated logins, this
script is the first thing to check.

Output schema (classes.json / classes_min.json), same shape as before
plus three new fields:

    {"outlet": str, "day": "Mon".."Sun", "date": "YYYY-MM-DD",
     "class": str, "start": "07:15am", "end": "08:15am",
     "instructor": str, "capacity": int, "booked": int, "waiting": int}

Run locally:
    pip install requests
    FF_EMAIL=you@example.com FF_PASSWORD=yourpassword python3 scrape_timetable.py
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

BASE_URL = "https://fitnessfirst.exerp.site"
AUTH_URL = f"{BASE_URL}/api/user/authenticate"
SEARCH_URL = f"{BASE_URL}/api/classes/search-booking-participations"

# All 14 SG clubs (centerId values, confirmed via captured traffic).
CENTER_IDS = [
    110, 117, 109, 111, 121, 103, 105,
    123, 108, 104, 124, 112, 118, 115,
]

DAYS_AHEAD = 7  # pull today + next 6 days (one week)

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": BASE_URL,
    "x-referer": f"{BASE_URL}/booking",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}

DAY_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def authenticate(email, password, retries=3):
    """Log in and return the bearer token."""
    body = {
        "email": email,
        "password": password,
        "sessionTimeoutOneMonth": False,
    }
    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.post(AUTH_URL, headers=HEADERS, json=body, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            token = data.get("token")
            if not token:
                raise RuntimeError("Login response had no token")
            return token
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Login failed: {last_err}")


def fetch_day(token, date_str, retries=3):
    """Fetch every class across all centers for a single date."""
    body = {
        "activityGroupIds": [],
        "activityIds": [],
        "centers": CENTER_IDS,
        "dateFrom": date_str,
        "dateTo": date_str,
    }
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.post(SEARCH_URL, headers=headers, json=body, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {date_str}: {last_err}")


def to_12h(hhmm):
    """'07:15' -> '7:15am'; '' / None -> ''"""
    if not hhmm:
        return ""
    try:
        return datetime.strptime(hhmm, "%H:%M").strftime("%I:%M%p").lstrip("0").lower()
    except ValueError:
        return hhmm


def parse_day(raw_items, date_str):
    """Flatten one day's response into our row schema."""
    weekday_idx = datetime.strptime(date_str, "%Y-%m-%d").weekday()
    day_short = DAY_SHORT[weekday_idx]

    rows = []
    for item in raw_items:
        booking = item.get("booking")
        if not booking:
            continue  # entries without a booking block aren't classes

        capacity = booking.get("classCapacity", 0)
        booked = booking.get("bookedCount", 0)
        instructors = booking.get("instructorNames") or []
        instructor = ", ".join(
            name.rstrip(" .") for name in instructors if name
        )

        rows.append({
            "outlet": item.get("centerName", "").strip(),
            "day": day_short,
            "date": date_str,
            "class": booking.get("name", "").strip(),
            "start": to_12h(booking.get("startTime")),
            "end": to_12h(booking.get("endTime")),
            "instructor": instructor,
            "capacity": capacity,
            "booked": booked,
            "spacesLeft": max(capacity - booked, 0),
            "waiting": booking.get("waitingListCount", 0),
        })
    return rows


def main():
    email = os.environ.get("FF_EMAIL")
    password = os.environ.get("FF_PASSWORD")
    if not email or not password:
        print("ERROR: FF_EMAIL and FF_PASSWORD must be set as environment variables.",
              file=sys.stderr)
        sys.exit(1)

    print("Logging in...", file=sys.stderr)
    token = authenticate(email, password)
    print("Login OK.", file=sys.stderr)

    all_rows = []
    today = datetime.now().date()
    for i in range(DAYS_AHEAD):
        date_str = (today + timedelta(days=i)).isoformat()
        print(f"[{i + 1}/{DAYS_AHEAD}] fetching {date_str}...", file=sys.stderr)
        raw_items = fetch_day(token, date_str)
        rows = parse_day(raw_items, date_str)
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
    print(f"\nDone: {len(all_rows)} sessions across {len(outlets)} centers, "
          f"{len(classes)} class types, {DAYS_AHEAD} days.", file=sys.stderr)


if __name__ == "__main__":
    main()
