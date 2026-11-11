#!/usr/bin/env python3
"""BFCM dates and change freeze window.

  Thanksgiving   fourth Thursday of November
  Black Friday   day after Thanksgiving
  Cyber Monday   Monday after Black Friday
  Freeze start   Friday one week before Black Friday
  Freeze end     Wednesday after Cyber Monday, inclusive
  Prep window    8 weeks before Black Friday

Fix by dates are business days before freeze start, weekends skipped. Public holidays
are not modelled, so pull a date earlier by hand if it lands on one.

  python3 freeze_window.py
  python3 freeze_window.py --year 2026 --json
  python3 freeze_window.py --today 2026-11-24

Standard library only. Python 3.7 or later. No runtime specific assumptions.
"""

import argparse
import json
from datetime import date, timedelta

THURSDAY, FRIDAY, WEDNESDAY, MONDAY = 3, 4, 2, 0


def thanksgiving(year: int) -> date:
    d = date(year, 11, 1)
    return d + timedelta(days=(THURSDAY - d.weekday()) % 7) + timedelta(weeks=3)


def business_days_before(d: date, n: int) -> date:
    moved = 0
    while moved < n:
        d -= timedelta(days=1)
        if d.weekday() < 5:
            moved += 1
    return d


def next_business_day(d: date) -> date:
    d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def compute(year: int, today: date) -> dict:
    black_friday = thanksgiving(year) + timedelta(days=1)
    cyber_monday = black_friday + timedelta(days=3)
    freeze_start = black_friday - timedelta(days=7)
    freeze_end = cyber_monday + timedelta(days=2)
    prep_start = black_friday - timedelta(weeks=8)

    assert black_friday.weekday() == FRIDAY
    assert cyber_monday.weekday() == MONDAY
    assert freeze_start.weekday() == FRIDAY
    assert freeze_end.weekday() == WEDNESDAY

    reversal = next_business_day(freeze_end)
    return {
        "year": year,
        "today": today.isoformat(),
        "black_friday": black_friday.isoformat(),
        "cyber_monday": cyber_monday.isoformat(),
        "prep_window_start": prep_start.isoformat(),
        "freeze_start": freeze_start.isoformat(),
        "freeze_end": freeze_end.isoformat(),
        "days_until_freeze_start": (freeze_start - today).days,
        "days_until_black_friday": (black_friday - today).days,
        "inside_freeze_window": freeze_start <= today <= freeze_end,
        "inside_prep_window": prep_start <= today <= freeze_end,
        "fix_by": {
            "P0": business_days_before(freeze_start, 5).isoformat(),
            "P1": business_days_before(freeze_start, 2).isoformat(),
            "P2": freeze_start.isoformat(),
            "P3": reversal.isoformat(),
        },
        "reversal_date": reversal.isoformat(),
    }


def render(r: dict) -> str:
    out = [
        "BFCM {}".format(r["year"]),
        "",
        "  Black Friday       {}".format(r["black_friday"]),
        "  Cyber Monday       {}".format(r["cyber_monday"]),
        "  Prep window opens  {}".format(r["prep_window_start"]),
        "  Freeze start       {}".format(r["freeze_start"]),
        "  Freeze end         {} inclusive".format(r["freeze_end"]),
        "",
        "  Today              {}".format(r["today"]),
        "  Days to freeze     {}".format(r["days_until_freeze_start"]),
        "  Inside freeze      {}".format("YES" if r["inside_freeze_window"] else "no"),
        "  Inside prep window {}".format("YES" if r["inside_prep_window"] else "no"),
        "",
        "  Fix by",
        "    P0               {}".format(r["fix_by"]["P0"]),
        "    P1               {}".format(r["fix_by"]["P1"]),
        "    P2               {}".format(r["fix_by"]["P2"]),
        "    P3               {}".format(r["fix_by"]["P3"]),
        "",
        "  Reversal date      {}".format(r["reversal_date"]),
    ]
    if r["inside_freeze_window"]:
        out += [
            "",
            "  FREEZE WINDOW OPEN. Routine change suspended. Each remaining item",
            "  is a risk decision, not a scheduled fix.",
        ]
    return "\n".join(out)


def main() -> None:
    p = argparse.ArgumentParser(description="BFCM freeze window calculator")
    p.add_argument("--year", type=int)
    p.add_argument("--today", help="YYYY-MM-DD, defaults to now")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    today = date.fromisoformat(a.today) if a.today else date.today()
    year = a.year or today.year
    if not a.year and today > date.fromisoformat(compute(year, today)["freeze_end"]):
        year += 1

    r = compute(year, today)
    print(json.dumps(r, indent=2) if a.json else render(r))


if __name__ == "__main__":
    main()
