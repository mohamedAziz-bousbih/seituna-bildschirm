#!/usr/bin/env python3
"""Fetch the mosque's prayer times from its public MAWAQIT page and save them as prayer-times.json.

Runs every night on GitHub Actions (see .github/workflows/mawaqit.yml). Python standard library only.

The public mosque page contains the mosque's whole setup as JSON ("confData"): the calendar of the
year, the iqama times, the Jumu'a times. This is the same data the volunteer tools read.
It is NOT an official interface: if MAWAQIT changes its page, this script stops with an error
and leaves the last good prayer-times.json untouched, so the screen keeps working.

Usage:  MAWAQIT_SLUG=<slug> python fetch_mawaqit.py        (or: python fetch_mawaqit.py <slug>)
        The slug is the last part of the mosque's link, e.g. https://mawaqit.net/de/<slug>
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request

OUT = os.environ.get("MAWAQIT_OUT", "prayer-times.json")
KEEP = ["name", "timezone", "calendar", "iqamaCalendar", "iqamaEnabled",
        "jumua", "jumua2", "jumua3", "jumuaAsDuhr", "hijriAdjustment", "hijriDateForceTo30"]
HHMM = re.compile(r"^\d{1,2}:\d{2}$")
IQAMA = re.compile(r"^(\+?\d{1,3}|\d{1,2}:\d{2})$")


def fail(msg: str) -> None:
    print(f"FEHLER: {msg}\nprayer-times.json wurde NICHT verändert.", file=sys.stderr)
    sys.exit(1)


def fetch(slug: str) -> dict:
    url = f"https://mawaqit.net/de/{slug}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Seituna-Moschee-Bildschirm; 1x taeglich)",
        "Accept-Language": "de,ar;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "replace")
    except Exception as e:  # network, 404, Cloudflare block …
        fail(f"MAWAQIT-Seite nicht erreichbar ({url}): {e}")
    m = re.search(r"(?:var|let|const)\s+confData\s*=\s*", html)
    if not m:
        fail("confData nicht auf der Seite gefunden – MAWAQIT hat die Seite wohl geändert.")
    try:  # parse exactly one JSON object starting there, ignore the rest of the script
        data, _ = json.JSONDecoder().raw_decode(html, m.end())
    except ValueError as e:
        fail(f"confData ist kein gültiges JSON: {e}")
    return data


def check(d: dict) -> None:
    cal = d.get("calendar")
    if not isinstance(cal, list) or len(cal) != 12:
        fail("Kalender fehlt oder hat nicht 12 Monate.")
    for mi, month in enumerate(cal, 1):
        if not isinstance(month, dict) or len(month) < 28:
            fail(f"Monat {mi}: zu wenige Tage.")
        for day, row in month.items():
            if not isinstance(row, list) or len(row) not in (6, 7) or not all(HHMM.match(str(t)) for t in row):
                fail(f"Ungültige Zeiten am {day}.{mi}.: {row}")
    iq = d.get("iqamaCalendar")
    if iq is not None:
        if not isinstance(iq, list) or len(iq) != 12:
            fail("Iqama-Kalender hat nicht 12 Monate.")
        for mi, month in enumerate(iq, 1):
            for day, row in (month or {}).items():
                if not isinstance(row, list) or len(row) != 5 or not all(IQAMA.match(str(v).strip()) for v in row):
                    fail(f"Ungültige Iqama am {day}.{mi}.: {row}")


def main() -> None:
    slug = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MAWAQIT_SLUG", "")).strip().strip("/")
    slug = slug.rsplit("/", 1)[-1]  # a full link works too
    if not slug:
        fail("Kein MAWAQIT_SLUG angegeben.")
    d = fetch(slug)
    check(d)
    out = {k: d.get(k) for k in KEEP}
    out["slug"] = slug
    out["fetchedAt"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    today = dt.date.today()
    row = d["calendar"][today.month - 1].get(str(today.day))
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, OUT)  # write the new file only once it is complete
    print(f"OK: {out['name']} · heute {row} · Iqama {d.get('iqamaCalendar', [{}]*12)[today.month - 1].get(str(today.day))}"
          f" · Jumu'a {out['jumua']} {out['jumua2'] or ''} → {OUT}")


if __name__ == "__main__":
    main()
