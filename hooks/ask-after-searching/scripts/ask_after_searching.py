#!/usr/bin/env python3
"""Send a question back to Claude when it asks you without searching first.

Claude Code calls this before the AskUserQuestion tool. The question goes through if:

  1. the question says where Claude looked, or says it is a decision for you
  2. the session searched since your last message
  3. the same question was already sent back once in this session

Otherwise it is refused once, with a note telling Claude to search first.
Asking the same question again goes through, so you are never left without an answer.

Settings, in the env block of your Claude Code settings:

  ASK_AFTER_SEARCHING_MODE    remind (default), warn (let it through with a note), off
  ASK_AFTER_SEARCHING_PATHS   comma-separated words, such as notes,records. When set,
                              a search counts only if it names one of them.

The log holds the decision, a hash and the length of the question, never its text.
Any error lets the question through. Standard library only. No network calls.
"""

import datetime
import hashlib
import json
import os
import re
import sys

SAYS_WHERE = re.compile(r"\b(searched|looked in|looked at|checked|not found in|not on file|decision)\b", re.I)
SHELL_SEARCH = re.compile(r"\b(grep|rg|find|findstr|ls|dir|Select-String|Get-ChildItem)\b")
LINES_READ = 400
LOG_NAME = "ask-after-searching.jsonl"


def log_path():
    home = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    folder = os.environ.get("CLAUDE_TOOLS_LOG_DIR") or os.path.join(home, "claude-tools-logs")
    return os.path.join(folder, LOG_NAME)


def log(record):
    try:
        path = log_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        record["time"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError:
        pass


def question_sentences(tool_input):
    return " ".join(str(q.get("question") or "") for q in tool_input.get("questions") or [])


def whole_question(tool_input):
    parts = [question_sentences(tool_input)]
    for q in tool_input.get("questions") or []:
        for option in q.get("options") or []:
            parts += [str(option.get("label") or ""), str(option.get("description") or "")]
    return " ".join(parts)


def names_a_place(text, places):
    return not places or any(p.lower() in text.lower() for p in places)


def is_search(tool, tool_input, places):
    if tool == "Skill":
        return "check-the-record-first" in json.dumps(tool_input)
    if tool in ("Grep", "Glob"):
        where = " ".join(str(tool_input.get(k) or "") for k in ("path", "glob", "pattern"))
        return names_a_place(where, places)
    if tool in ("Bash", "PowerShell"):
        command = str(tool_input.get("command") or "")
        return bool(SHELL_SEARCH.search(command)) and names_a_place(command, places)
    if tool == "Read":
        return bool(places) and names_a_place(str(tool_input.get("file_path") or ""), places)
    return False


def is_your_message(record):
    if record.get("type") != "user" or record.get("isSidechain"):
        return False
    content = (record.get("message") or {}).get("content")
    if isinstance(content, str):
        return not content.lstrip().startswith("<")
    if isinstance(content, list):
        kinds = [c.get("type") for c in content if isinstance(c, dict)]
        return "text" in kinds and "tool_result" not in kinds
    return False


def searched_since_your_message(transcript_path, places):
    try:
        with open(transcript_path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()[-LINES_READ:]
    except (OSError, TypeError):
        return False
    found = False
    for line in lines:
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if is_your_message(record):
            found = False
        elif record.get("type") == "assistant" and not record.get("isSidechain"):
            for block in (record.get("message") or {}).get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use" \
                        and is_search(block.get("name"), block.get("input") or {}, places):
                    found = True
    return found


def sent_back_before(session, digest):
    try:
        with open(log_path(), encoding="utf-8") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if row.get("session") == session and row.get("hash") == digest and row.get("decision") == "remind":
                    return True
    except OSError:
        pass
    return False


def decide(data, mode, places, digest):
    tool_input = data.get("tool_input") or {}
    if mode == "off":
        return "off"
    if SAYS_WHERE.search(question_sentences(tool_input)):
        return "pass-said"
    if searched_since_your_message(data.get("transcript_path"), places):
        return "pass-searched"
    if sent_back_before(data.get("session_id", ""), digest):
        return "pass-second-ask"
    return "warn" if mode == "warn" else "remind"


def main():
    data = json.loads(sys.stdin.read() or "{}")
    mode = os.environ.get("ASK_AFTER_SEARCHING_MODE", "remind").strip().lower()
    places = [p.strip() for p in os.environ.get("ASK_AFTER_SEARCHING_PATHS", "").split(",") if p.strip()]
    text = whole_question(data.get("tool_input") or {})
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    decision = decide(data, mode, places, digest)
    log({"session": data.get("session_id", ""), "decision": decision, "hash": digest, "chars": len(text)})
    advice = ("If this is a fact, search the user's own files first, and ask only if nothing is found. "
              "Say in the question where you looked (\"Searched notes/, not found\"). "
              "If it is a choice, say \"Decision:\" in the question.")
    if decision == "warn":
        note = "Ask after searching, the question went ahead. " + advice
        print(json.dumps({"systemMessage": note, "hookSpecificOutput": {
            "hookEventName": "PreToolUse", "additionalContext": note}}))
    elif decision == "remind":
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Ask after searching sent this question back once. " + advice
                                        + " Asking the same question again goes through.",
        }}))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # never stand between you and a question
        log({"decision": "error", "why": repr(exc)[:200]})
    sys.exit(0)
