#!/usr/bin/env python3
"""Show which skills and agents ran, and which skills never did.

  python usage_report.py              the last 30 days
  python usage_report.py --days 90    a longer window

"Never ran" compares the log with the skills in .claude/skills, in this folder and in
your home Claude folder. Plugin skills are counted when they run but are not listed as
never run. Reads only. Standard library only. No network calls.
"""

import collections
import datetime
import glob
import json
import os
import sys


def config_home():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")


def log_file():
    folder = os.environ.get("CLAUDE_TOOLS_LOG_DIR") or os.path.join(config_home(), "claude-tools-logs")
    return os.path.join(folder, "skill-usage.jsonl")


def read_rows(since):
    rows = []
    try:
        with open(log_file(), encoding="utf-8") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if str(row.get("time", ""))[:10] >= since:
                    rows.append(row)
    except OSError:
        pass
    return rows


def installed_skills(cwd):
    names = set()
    for base in (os.path.join(cwd, ".claude"), config_home()):
        for path in glob.glob(os.path.join(base, "skills", "*", "SKILL.md")):
            names.add(os.path.basename(os.path.dirname(path)))
    return names


def summary(rows):
    direct, through_agent, agents = collections.Counter(), collections.Counter(), collections.Counter()
    for row in rows:
        if row.get("event") == "PreToolUse" and row.get("skill"):
            direct[row["skill"]] += 1
        elif row.get("event") == "SubagentStart":
            agents[row.get("agent") or "(unnamed)"] += 1
            for skill in row.get("skills") or []:
                through_agent[skill] += 1
    return direct, through_agent, agents


def main(args):
    days = int(args[args.index("--days") + 1]) if "--days" in args else 30
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    rows = read_rows(since)
    direct, through_agent, agents = summary(rows)
    print(f"Skill and agent use since {since}: {len(rows)} events.\n")
    print("Skills (direct, through an agent):")
    for skill in sorted(set(direct) | set(through_agent), key=lambda s: -(direct[s] + through_agent[s])):
        print(f"  {skill}: {direct[skill]}, {through_agent[skill]}")
    print("\nAgents:")
    for agent, count in agents.most_common():
        print(f"  {agent}: {count}")
    silent = sorted(installed_skills(os.getcwd()) - set(direct) - set(through_agent))
    print(f"\nInstalled skills that never ran in this window: {len(silent)}")
    for skill in silent:
        print(f"  {skill}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main(sys.argv[1:])
