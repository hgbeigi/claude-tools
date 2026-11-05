# Weekday date check

A Claude Code hook and a small script. Claude can write "Monday, November 18" when the 18th is a Wednesday, and the mistake goes out in a scheduling email. After Claude writes a Markdown, text, email or HTML file, this checks each weekday next to a date against the calendar and tells Claude what to fix. It never blocks.

## What it reads

"Wednesday 18 November", "Thu, Nov 5, 2026", "Monday 2026-11-02", "the 3rd of March (Sat)", "Friday 11/20", "11/18 (Tue)".

## Check a file by hand

```
python weekday_check.py draft.md
python weekday_check.py --year 2027 draft.md
python weekday_check.py --day-first draft.md
```

## Limits

- A date with no year is taken as its nearest occurrence to today, and the message says which year it used. An old note can therefore draw a false flag.
- 3/4 is read as March 4 unless you set `--day-first`, or `WEEKDAY_DAY_FIRST=1` in the `env` block of your settings for the hook.
- It checks a weekday and date that sit side by side, in English. "Next Tuesday" and text inside a chat reply are not checked.
- `WEEKDAY_CHECK_EXTENSIONS` changes the file types.

## Try it

1. Draft an email offering Tuesday, November 18 and Friday, November 20 for a call.
2. Check the dates in `draft.md`.
3. Check `plan.md`, taking every date as 2027.

## Sample data

`examples/sample-email.md` holds one wrong weekday and one right one. `python weekday_check.py --year 2026 examples/sample-email.md` reports one mismatch.

## Install

```
/plugin marketplace add hgbeigi/claude-tools
/plugin install weekday-date-check@hgbeigi-tools
```

Privacy: nothing is collected or sent anywhere. See [PRIVACY.md](../../PRIVACY.md).
