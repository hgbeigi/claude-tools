#!/usr/bin/env python3
"""Refuse a git commit that holds money files or private details.

Runs in four ways:

  python commit_guard.py                check what is staged, as a git hook does
  python commit_guard.py --all          check every tracked file, for a first look
  python commit_guard.py --install      add this check to this repository's git hooks
  python commit_guard.py --claude-hook  read a Claude Code hook event from stdin

It reads the staged copy of each file, not the copy on disk, so it checks exactly
what the commit would hold. Messages give a rule and a line number and never print
the matched text, so a message is safe to paste into a note.

Exit codes: 0 clean, 1 refused, 2 the check itself could not run.
Standard library only. No network calls.
"""

import fnmatch
import json
import os
import re
import shutil
import stat
import subprocess
import sys

REFUSED_TYPES = {
    "xlsx", "xlsm", "xlsb", "xls", "ods", "csv", "tsv", "ofx", "qfx", "qif",
    "pdf", "png", "jpg", "jpeg", "gif", "heic", "webp", "bmp", "tif", "tiff",
    "zip", "7z", "msg", "eml", "mbox", "mhtml",
}
ALLOW_FILE = ".commit-guard-allow"
LINE_OK = "guard-ok"
LEDGER_MIN_LINES = 5
LEDGER_MAX_GAP = 3

WEB_ADDRESS = re.compile(r"(?:https?://|www\.)\S*", re.I)
CARD_OR_ACCOUNT = [
    re.compile(r"(?<![\w.\-])\d{13,19}(?!\w)"),
    re.compile(r"(?<!\d)\d{4}[ \-]\d{4}[ \-]\d{4}[ \-]\d{4}(?!\d)"),
    re.compile(r"(?i)\b(?:acct\.?|account\s*(?:#|no\.?|number)|routing(?:\s*(?:#|no\.?|number))?)[\s:#.\-]*\d{6,}"),
]
SOCIAL_SECURITY = re.compile(r"(?<![\d\-])\d{3}-\d{2}-\d{4}(?![\d\-])")

MONTH = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
LEDGER_DATE = re.compile(
    r"(?i)(?:\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b|\b" + MONTH + r"\s+\d{1,2}\b)"
)
LEDGER_AMOUNT = re.compile(r"-?\(?\$\s?-?\d[\d,]*(?:\.\d{2})?\)?|(?<![\w.])-?\d{1,6}\.\d{2}(?!\w)")
LEDGER_WORD = re.compile(r"[A-Za-z]{3,}")


def git(args, cwd, as_bytes=False):
    done = subprocess.run(["git"] + args, cwd=cwd, capture_output=True)
    return done.returncode, done.stdout if as_bytes else done.stdout.decode("utf-8", "replace")


def repo_root(cwd):
    code, out = git(["rev-parse", "--show-toplevel"], cwd)
    return out.strip() if code == 0 else None


def staged_files(root):
    """(status letter, path) for each added, copied, modified or renamed file."""
    _, out = git(["diff", "--cached", "--name-status", "-z", "--diff-filter=ACMR"], root)
    fields = [f for f in out.split("\0") if f]
    files = []
    i = 0
    while i < len(fields):
        letter = fields[i][0]
        step = 3 if letter in "RC" else 2
        files.append((letter, fields[i + step - 1]))
        i += step
    return files


def tracked_files(root):
    _, out = git(["ls-files", "-z"], root)
    return [("A", p) for p in out.split("\0") if p]


def read_blob(root, path, staged):
    if staged:
        code, data = git(["show", ":" + path], root, as_bytes=True)
        return data if code == 0 else b""
    try:
        with open(os.path.join(root, path), "rb") as fh:
            return fh.read()
    except OSError:
        return b""


def allowed_patterns(root):
    try:
        with open(os.path.join(root, ALLOW_FILE), encoding="utf-8") as fh:
            return [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    except OSError:
        return []


def name_patterns():
    """Your own private words, kept in a file outside the repository."""
    home = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    path = os.environ.get("COMMIT_GUARD_NAMES") or os.path.join(home, "commit-guard-names.txt")
    patterns = []
    try:
        with open(path, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if ln and not ln.startswith("#"):
                    patterns.append(re.compile(ln, re.I))
    except OSError:
        pass
    return patterns


def check_lines(lines, names):
    hits = []
    for number, line in lines:
        if LINE_OK in line:
            continue
        plain = WEB_ADDRESS.sub(" ", line)
        if SOCIAL_SECURITY.search(plain):
            hits.append(("social security", number, "looks like a US social security number"))
        if any(p.search(plain) for p in CARD_OR_ACCOUNT):
            hits.append(("account number", number, "looks like a card, account or routing number"))
        if any(p.search(line) for p in names):
            hits.append(("private name", number, "holds a word from your private name list"))
    return hits


def is_ledger_line(line):
    text = line.lstrip(" \t|\"'*-")
    date = LEDGER_DATE.search(text)
    amounts = LEDGER_AMOUNT.findall(text)
    if len(text) > 200 or not date or date.start() > 12 or not 1 <= len(amounts) <= 2:
        return False
    return bool(LEDGER_WORD.search(LEDGER_AMOUNT.sub(" ", LEDGER_DATE.sub(" ", text))))


def check_ledger(lines):
    """Five or more nearby lines with a date, an amount and a description."""
    numbers = [n for n, line in lines if LINE_OK not in line and is_ledger_line(line)]
    runs = []
    for n in numbers:
        if runs and n - runs[-1][-1] <= LEDGER_MAX_GAP:
            runs[-1].append(n)
        else:
            runs.append([n])
    return [
        ("ledger", run[0], f"{len(run)} lines from here each hold a date, an amount and a description")
        for run in runs if len(run) >= LEDGER_MIN_LINES
    ]


def find_problems(root, check_everything=False):
    files = tracked_files(root) if check_everything else staged_files(root)
    allowed = allowed_patterns(root)
    names = name_patterns()
    problems = []
    for status, path in files:
        name = os.path.basename(path)
        kind = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        exempt = any(fnmatch.fnmatch(path, p) for p in allowed)
        if kind in REFUSED_TYPES and status in "ACR" and not exempt:
            problems.append((path, "file type", f"a new .{kind} file. Keep it outside the repository, "
                             f"or list it in {ALLOW_FILE} if it is safe"))
        data = read_blob(root, path, staged=not check_everything)
        if b"\0" in data[:8000]:
            continue
        lines = list(enumerate(data.decode("utf-8", "replace").split("\n"), 1))
        for rule, number, message in check_lines(lines, names) + check_ledger(lines):
            problems.append((path, rule, f"line {number}: {message}"))
    return len(files), problems


def report(checked, problems):
    if not problems:
        return f"commit guard: {checked} files checked, clean."
    rows = [f"  {path}  [{rule}]  {message}" for path, rule, message in problems]
    return "\n".join(["commit guard: commit refused."] + rows + [
        f"commit guard: {len(problems)} problem(s) in {checked} files. "
        f"Fix them, or add {LINE_OK} to a line that is safe."
    ])


PRE_COMMIT = """#!/bin/sh
# Added by commit-privacy-guard. Remove this file to turn the check off.
here="$(dirname "$0")"
for py in python3 python py; do
  if "$py" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
    exec "$py" "$here/commit_guard.py"
  fi
done
echo "commit guard: Python 3.8 or later was not found, so the commit is refused." >&2
exit 2
"""


def install(root):
    _, out = git(["rev-parse", "--git-path", "hooks"], root)
    folder = os.path.join(root, out.strip())
    target = os.path.join(folder, "pre-commit")
    if os.path.exists(target):
        print(f"commit guard: {target} already exists. Nothing was changed. "
              "Call commit_guard.py from that file yourself.")
        return 1
    os.makedirs(folder, exist_ok=True)
    shutil.copyfile(os.path.abspath(__file__), os.path.join(folder, "commit_guard.py"))
    with open(target, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(PRE_COMMIT)
    os.chmod(target, os.stat(target).st_mode | stat.S_IEXEC)
    print(f"commit guard: added to {target}.")
    return 0


GIT_COMMIT = re.compile(r"\bgit\b[^;&|\n]*\scommit\b")
GIT_ADD = re.compile(r"\bgit\b[^;&|\n]*\sadd\b")


def claude_hook(stream):
    """PreToolUse on Bash: refuse `git commit` when the staged files fail.

    It only sees what is staged when Claude asks to run the command, so a single
    command that both adds and commits is told to split in two.
    """
    data = json.loads(stream.read() or "{}")
    command = str((data.get("tool_input") or {}).get("command") or "")
    if not GIT_COMMIT.search(command):
        return 0
    root = repo_root(data.get("cwd") or os.getcwd())
    if root is None:
        return 0
    if GIT_ADD.search(command):
        reason = ("Commit privacy guard: this command adds files and commits in one step, so the guard "
                  "cannot see them yet. Run git add first, then git commit as a separate command.")
    else:
        checked, problems = find_problems(root)
        if not problems:
            return 0
        reason = report(checked, problems)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    return 0


def main(args):
    if "--claude-hook" in args:
        try:
            return claude_hook(sys.stdin)
        except Exception as exc:  # a broken check must not stop the session; the git hook still refuses
            print(f"commit guard: the Claude Code check failed ({exc!r}).", file=sys.stderr)
            return 0
    root = repo_root(os.getcwd())
    if root is None:
        print("commit guard: this folder is not inside a git repository.")
        return 2
    if "--install" in args:
        return install(root)
    checked, problems = find_problems(root, check_everything="--all" in args)
    print(report(checked, problems))
    return 1 if problems else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as exc:  # nothing was verified, so refuse rather than pass quietly
        print(f"commit guard: the check itself failed ({exc!r}), so the commit is refused.")
        sys.exit(2)
