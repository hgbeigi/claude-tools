#!/usr/bin/env python3
"""Test whether a skill's description would make it load.

Claude picks a skill by matching your request against each skill's short description.
Phrases in quotation marks in a description, such as Use when I say "split the bill",
are a good guide to what it will match. This script gives two measures:

  python trigger_test.py --skills DIR --requests FILE.json
      For each saved request, picks the skill with the most quoted phrases in the text.
      A tie or no match is a miss. The file holds:
      {"requests": [{"id": 1, "text": "...", "expected": "skill-name"}]}

  python trigger_test.py --skills DIR --transcripts [--days 90]
      Counts how often you typed each quoted phrase in your own Claude Code sessions,
      read from the transcripts on this computer. A phrase you never say will not help.

Add --csv FILE to write the phrase counts to a file. --skills is a folder holding one
folder per skill, such as .claude/skills. Skills marked disable-model-invocation are
left out of the pick, because Claude never starts them by itself.

This is a stand-in: Claude reads the whole description, and this script reads only the
quoted phrases. Use it to compare before and after a rewrite, not as a promise.
Reads only. Standard library only. No network calls.
"""

import csv
import datetime
import glob
import json
import os
import re
import sys

QUOTED = re.compile(r"\"([^\"]{2,60})\"")
DESCRIPTION = re.compile(r"^description:\s*(?:[>|]-?\s*)?(.*?)(?=^[\w-]+:|^---)", re.S | re.M)
HIDDEN = re.compile(r"^disable-model-invocation:\s*true", re.M)
TAG = re.compile(r"<[a-z-]+>.*?</[a-z-]+>", re.S)


def has_phrase(phrase, text):
    return re.search(r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)", text) is not None


def read_skills(folder, skip_hidden=False):
    """{skill name: [quoted phrases]} from each SKILL.md in the folder."""
    skills = {}
    for path in sorted(glob.glob(os.path.join(folder, "*", "SKILL.md"))):
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        if skip_hidden and HIDDEN.search(text):
            continue
        found = DESCRIPTION.search(text)
        skills[os.path.basename(os.path.dirname(path))] = QUOTED.findall(found.group(1) if found else "")
    return skills


def pick(request, skills):
    """(the winning skill or None, {skill: [matched phrases]})."""
    low = request.lower()
    hits = {name: [p for p in phrases if has_phrase(p, low)] for name, phrases in skills.items()}
    hits = {name: found for name, found in hits.items() if found}
    if not hits:
        return None, hits
    top = max(len(found) for found in hits.values())
    winners = [name for name, found in hits.items() if len(found) == top]
    return (winners[0] if len(winners) == 1 else None), hits


def score(skills, requests):
    right = 0
    for row in requests:
        chosen, hits = pick(row["text"], skills)
        good = chosen == row["expected"]
        right += good
        shown = "; ".join(f"{name} ({', '.join(found)})" for name, found in hits.items())
        print(f"{row['id']:>3} {'ok  ' if good else 'MISS'} wanted {row['expected']}, got {chosen or 'none'}"
              + (f": {shown}" if shown else ""))
    print(f"\n{right} of {len(requests)} pick the right skill.")
    empty = [name for name, phrases in skills.items() if not phrases]
    if empty:
        print("No quoted phrases in the description of: " + ", ".join(empty))
    return right


def your_messages(path, since):
    """The text you typed in one transcript, without tool results or system notices."""
    messages = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("type") != "user" or row.get("isMeta") or row.get("isSidechain"):
                continue
            if str(row.get("timestamp") or "")[:10] < since:
                continue
            content = (row.get("message") or {}).get("content")
            if isinstance(content, list):
                if any(c.get("type") == "tool_result" for c in content if isinstance(c, dict)):
                    continue
                content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
            text = TAG.sub(" ", str(content or "")).strip()
            if text and not text.startswith("<"):
                messages.append(text.lower())
    return messages


def transcript_files():
    home = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    return glob.glob(os.path.join(home, "projects", "*", "*.jsonl"))


def count_phrases(skills, messages):
    return [(name, phrase, sum(has_phrase(phrase, m) for m in messages))
            for name, phrases in skills.items() for phrase in phrases]


def option(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default


def main(args):
    folder = option(args, "--skills")
    if not folder or not ("--requests" in args or "--transcripts" in args):
        print(__doc__)
        return 2
    if "--requests" in args:
        with open(option(args, "--requests"), encoding="utf-8") as fh:
            score(read_skills(folder, skip_hidden=True), json.load(fh)["requests"])
        return 0
    days = int(option(args, "--days", 90))
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    files = transcript_files()
    messages = [m for path in files for m in your_messages(path, since)]
    rows = count_phrases(read_skills(folder), messages)
    print(f"{len(messages)} of your messages since {since}, in {len(files)} transcripts.\n")
    grouped = {}
    for name, phrase, hits in rows:
        grouped.setdefault(name, []).append((phrase, hits))
    for name, items in grouped.items():
        used = sum(1 for _, hits in items if hits)
        print(f"{name}: {used} of {len(items)} phrases used{'   NONE USED' if not used else ''}")
        print("    " + "; ".join(f'"{p}" {hits}' for p, hits in items))
    target = option(args, "--csv")
    if target:
        with open(target, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["skill", "phrase", "hits"])
            writer.writerows(rows)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
