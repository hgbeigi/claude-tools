#!/usr/bin/env python3
"""Warn when a brief for a helper agent misses a needed section.

Claude Code calls this before the Agent tool. A named agent carries its rules in its
own definition, and a built-in such as Explore has a narrow job, so both pass. A
general-purpose brief must hold the words Goal, Read, Required, Done and Output.

Settings, in the env block of your Claude Code settings:

  BRIEF_CHECK_MODE    warn (default), block (refuse the call), off
  BRIEF_CHECK_WORDS   comma-separated words to use instead of the five above

The log holds the agent type, the decision and the length of the brief, never its
text. Any error lets the call through. Standard library only. No network calls.
"""

import datetime
import json
import os
import re
import sys

DEFAULT_WORDS = ["Goal", "Read", "Required", "Done", "Output"]
CHECKED_TYPES = {"", "general-purpose", "claude"}
LOG_NAME = "brief-check.jsonl"


def config_home():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")


def log(record):
    try:
        folder = os.environ.get("CLAUDE_TOOLS_LOG_DIR") or os.path.join(config_home(), "claude-tools-logs")
        os.makedirs(folder, exist_ok=True)
        record["time"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        with open(os.path.join(folder, LOG_NAME), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError:
        pass


def named_agents(cwd):
    names = set()
    for folder in (os.path.join(cwd, ".claude", "agents"), os.path.join(config_home(), "agents")):
        try:
            names.update(f[:-3] for f in os.listdir(folder) if f.endswith(".md"))
        except OSError:
            pass
    return names


def missing_words(brief, words):
    return [w for w in words if not re.search(r"\b" + re.escape(w) + r"s?\b", brief, re.I)]


def decide(tool_input, mode, agents, words):
    agent = str(tool_input.get("subagent_type") or "").strip()
    if mode == "off":
        return "off", []
    if agent in agents:
        return "pass-named", []
    if agent.lower() not in CHECKED_TYPES:
        return "pass-built-in", []
    missing = missing_words(str(tool_input.get("prompt") or ""), words)
    if not missing:
        return "pass-complete", []
    return ("block" if mode == "block" else "warn"), missing


def main():
    data = json.loads(sys.stdin.read() or "{}")
    tool_input = data.get("tool_input") or {}
    mode = os.environ.get("BRIEF_CHECK_MODE", "warn").strip().lower()
    words = [w.strip() for w in os.environ.get("BRIEF_CHECK_WORDS", "").split(",") if w.strip()] or DEFAULT_WORDS
    decision, missing = decide(tool_input, mode, named_agents(data.get("cwd") or os.getcwd()), words)
    agent = str(tool_input.get("subagent_type") or "general-purpose")
    log({"session": data.get("session_id", ""), "agent": agent, "decision": decision,
         "missing": missing, "chars": len(str(tool_input.get("prompt") or ""))})
    if decision not in ("warn", "block"):
        return
    gap = f"the brief for this {agent} agent is missing {', '.join(missing)}. Add those sections or use a named agent."
    if decision == "warn":
        note = "Brief check, the call went ahead: " + gap
        print(json.dumps({"systemMessage": note, "hookSpecificOutput": {
            "hookEventName": "PreToolUse", "additionalContext": note}}))
    else:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Brief check refused this call: " + gap,
        }}))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # a check on briefs must not stop the work
        log({"decision": "error", "why": repr(exc)[:200]})
    sys.exit(0)
