#!/usr/bin/env python3
"""Flag a weekday that does not match its date.

Finds a weekday next to a date, such as "Wednesday 18 November", "Thu, Nov 5, 2026",
"Monday 2026-11-02", "11/18 (Tue)" or "Friday 11/20", and checks the two against the
calendar. A date with no year is taken as its nearest occurrence to today, or as the
year given with --year.

  python weekday_check.py draft.md notes.txt        check files
  python weekday_check.py --year 2027 draft.md      use this year when none is written
  python weekday_check.py --day-first draft.md      read 3/4 as 3 April, not March 4
  python weekday_check.py --claude-hook             read a Claude Code hook event

The hook checks only the text Claude just wrote and never blocks: it tells Claude what
to fix. Set WEEKDAY_DAY_FIRST=1 for day-first dates in the hook, and
WEEKDAY_CHECK_EXTENSIONS to change the file types (default .md,.txt,.eml,.html).
Exit codes: 0 clean, 1 mismatch found. Standard library only. No network calls.
"""

import datetime
import json
import os
import re
import sys

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
SHORT_DAYS = {"tues": 1, "weds": 2, "thur": 3, "thurs": 3}
MONTHS = ["january", "february", "march", "april", "may", "june", "july",
          "august", "september", "october", "november", "december"]

DAY_WORD = r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tues|tue|weds|wed|thurs|thur|thu|fri|sat|sun)\.?"
MONTH_WORD = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
DAY_NUMBER = r"\d{1,2}(?:st|nd|rd|th)?"
YEAR = r"(?:,?\s+(?P<{}>\d{{4}}))?"
DATE = (
    r"(?P<iso>\d{4}-\d{2}-\d{2})"
    r"|(?:the\s+)?(?P<d1>" + DAY_NUMBER + r")(?:\s+of)?\s+(?P<m1>" + MONTH_WORD + r")" + YEAR.format("y1") +
    r"|(?P<m2>" + MONTH_WORD + r")\s+(?P<d2>" + DAY_NUMBER + r")(?!\d)" + YEAR.format("y2") +
    r"|(?P<n1>\d{1,2})/(?P<n2>\d{1,2})(?:/(?P<y3>\d{2,4}))?"
)
BEFORE = re.compile(r"\b(?P<w>" + DAY_WORD + r"),?\s+(?:" + DATE + r")(?![\w/])", re.I)
AFTER = re.compile(r"(?<![\w/])(?:" + DATE + r")\s*(?:\(\s*|,\s*)(?P<w>" + DAY_WORD + r")(?!\w)", re.I)


def weekday_index(word):
    word = word.lower().rstrip(".")
    if word in SHORT_DAYS:
        return SHORT_DAYS[word]
    for index, day in enumerate(DAYS):
        if day == word or day[:3] == word:
            return index
    return None


def month_index(word):
    word = word.lower().rstrip(".")
    for index, month in enumerate(MONTHS, 1):
        if month == word or month[:3] == word or (word == "sept" and month == "september"):
            return index
    return None


def nearest_year(month, day, today):
    """The year that puts this date closest to today."""
    best = None
    for year in (today.year - 1, today.year, today.year + 1):
        try:
            date = datetime.date(year, month, day)
        except ValueError:
            continue
        if best is None or abs((date - today).days) < abs((best - today).days):
            best = date
    return best.year if best else today.year


def parts(match, day_first):
    """(year or None, month, day) from a regular expression match."""
    g = match.groupdict()
    if g["iso"]:
        y, m, d = g["iso"].split("-")
        return int(y), int(m), int(d)
    if g["d1"]:
        return int(g["y1"]) if g["y1"] else None, month_index(g["m1"]), int(re.sub(r"\D", "", g["d1"]))
    if g["m2"]:
        return int(g["y2"]) if g["y2"] else None, month_index(g["m2"]), int(re.sub(r"\D", "", g["d2"]))
    first, second = int(g["n1"]), int(g["n2"])
    month, day = (second, first) if day_first else (first, second)
    year = None
    if g["y3"]:
        year = int(g["y3"]) + (2000 if len(g["y3"]) == 2 else 0)
    return year, month, day


def check_text(text, year=None, day_first=False, today=None):
    """A list of (line number, written text, what is wrong)."""
    today = today or datetime.date.today()
    found = []
    for number, line in enumerate(text.split("\n"), 1):
        for pattern in (BEFORE, AFTER):
            for match in pattern.finditer(line):
                written = weekday_index(match.group("w"))
                y, month, day = parts(match, day_first)
                if written is None or month is None:
                    continue
                assumed = y is None
                if assumed:
                    y = year or nearest_year(month, day, today)
                try:
                    actual = datetime.date(y, month, day).weekday()
                except ValueError:
                    found.append((number, match.group(0), "this date does not exist"))
                    continue
                if actual != written:
                    note = f" (taking the year as {y})" if assumed else ""
                    found.append((number, match.group(0), f"that date is a {DAYS[actual].capitalize()}{note}"))
    return found


def claude_hook(stream):
    data = json.loads(stream.read() or "{}")
    tool_input = data.get("tool_input") or {}
    path = str(tool_input.get("file_path") or "")
    wanted = os.environ.get("WEEKDAY_CHECK_EXTENSIONS", ".md,.txt,.eml,.html").lower().split(",")
    if not path.lower().endswith(tuple(w.strip() for w in wanted if w.strip())):
        return
    pieces = [tool_input.get("content"), tool_input.get("new_string")]
    pieces += [e.get("new_string") for e in tool_input.get("edits") or [] if isinstance(e, dict)]
    text = "\n".join(str(p) for p in pieces if p)
    day_first = os.environ.get("WEEKDAY_DAY_FIRST", "") not in ("", "0")
    found = check_text(text, day_first=day_first)
    if not found:
        return
    rows = "; ".join(f'"{written}": {problem}' for _, written, problem in found[:10])
    note = f"Weekday check on {os.path.basename(path)}: {rows}. Check the calendar and fix the text."
    print(json.dumps({"systemMessage": note, "hookSpecificOutput": {
        "hookEventName": "PostToolUse", "additionalContext": note}}))


def main(args):
    if "--claude-hook" in args:
        try:
            claude_hook(sys.stdin)
        except Exception as exc:  # never stop a session over a date
            print(f"weekday check failed: {exc!r}", file=sys.stderr)
        return 0
    year = None
    if "--year" in args:
        at = args.index("--year")
        year = int(args[at + 1])
        del args[at:at + 2]
    day_first = "--day-first" in args
    bad = 0
    for path in [a for a in args if not a.startswith("--")]:
        with open(path, encoding="utf-8", errors="replace") as fh:
            found = check_text(fh.read(), year=year, day_first=day_first)
        for number, written, problem in found:
            print(f"{path}:{number}: \"{written}\": {problem}")
        bad += len(found)
    print(f"{bad} mismatch(es)." if bad else "No mismatches.")
    return 1 if bad else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
