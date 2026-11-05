#!/usr/bin/env python3
"""Remind you of commits that exist only on this computer.

Claude Code calls this when a turn ends. It speaks only when commits have waited
unpushed for 20 minutes, and at most once an hour, so a normal session stays quiet.
A hook at the end of a session would be the natural place, but its output is not
shown, so this one runs at the end of each turn.

Settings, in the env block of your Claude Code settings:

  UNPUSHED_WAIT_MINUTES     how long a commit waits first (default 20)
  UNPUSHED_REPEAT_MINUTES   the quiet time between reminders (default 60)

It reads your local git state and writes one small time stamp inside the .git folder.
It never pushes. A branch with no upstream is skipped. Always exits 0.
Standard library only. No network calls.
"""

import json
import os
import subprocess
import sys
import time


def git(args, cwd):
    done = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, errors="replace")
    return done.stdout.strip() if done.returncode == 0 else None


def minutes(name, default):
    try:
        return max(0, int(os.environ.get(name, default)))
    except ValueError:
        return default


def reminder(cwd, now):
    if git(["rev-parse", "@{u}"], cwd) is None:
        return None
    stamps = (git(["log", "--format=%ct", "@{u}..HEAD"], cwd) or "").split()
    if not stamps or now - int(stamps[-1]) < minutes("UNPUSHED_WAIT_MINUTES", 20) * 60:
        return None
    stamp_file = os.path.join(cwd, git(["rev-parse", "--git-path", "unpushed-reminder.stamp"], cwd))
    try:
        with open(stamp_file, encoding="utf-8") as fh:
            last = int(fh.read().strip() or 0)
    except (OSError, ValueError):
        last = 0
    if now - last < minutes("UNPUSHED_REPEAT_MINUTES", 60) * 60:
        return None
    try:
        with open(stamp_file, "w", encoding="utf-8") as fh:
            fh.write(str(int(now)))
    except OSError:
        pass
    return f"{len(stamps)} commit(s) in this repository exist only on this computer. Push them before you switch."


def main():
    data = json.loads(sys.stdin.read() or "{}")
    cwd = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    message = reminder(cwd, time.time())
    if message:
        print(json.dumps({"systemMessage": message}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # a reminder must never stop a session
        pass
    sys.exit(0)
