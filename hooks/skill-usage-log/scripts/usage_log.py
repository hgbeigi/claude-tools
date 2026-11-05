#!/usr/bin/env python3
"""Log which skills and agents actually run.

A skill that never runs gives no error, so it can sit unused for months. Claude Code
calls this hook when a helper agent starts and before the Skill tool runs. A skill can
also load through an agent's `skills:` line, so counting only the Skill tool would
show your most-used skills at zero. This hook logs both.

It adds one JSON line per event to skill-usage.jsonl: the time, the event, the session
and the skill or agent name. It never logs prompts or file contents, never blocks and
never prints into the conversation. Read the log with usage_report.py.

Standard library only. No network calls.
"""

import datetime
import json
import os
import re
import sys

LOG_NAME = "skill-usage.jsonl"
SKILL_FIELDS = ("skill", "skill_name", "name", "command")


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


def frontmatter_skills(path):
    """The skills named on an agent file's `skills:` line or list."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return []
    if not lines or lines[0].strip() != "---":
        return []
    skills, inside = [], False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if key:
            inside = key.group(1) == "skills"
            if inside and key.group(2).strip():
                skills += [s.strip(" \"'") for s in key.group(2).strip("[] ").split(",") if s.strip(" \"'")]
        elif inside:
            item = re.match(r"^\s+-\s*(.+)$", line)
            if item:
                skills.append(item.group(1).strip(" \"'"))
    return skills


def agent_skills(agent, cwd):
    for folder in (os.path.join(cwd, ".claude", "agents"), os.path.join(config_home(), "agents")):
        path = os.path.join(folder, agent + ".md")
        if agent and os.path.isfile(path):
            return True, frontmatter_skills(path)
    return False, []


def record_for(data):
    event = data.get("hook_event_name", "")
    base = {"event": event, "session": data.get("session_id", "")}
    if event == "SubagentStart":
        agent = str(data.get("agent_type") or "")
        named, skills = agent_skills(agent, data.get("cwd") or os.getcwd())
        base.update({"agent": agent, "named_agent": named, "skills": skills})
        return base
    if event == "PreToolUse" and data.get("tool_name") == "Skill":
        tool_input = data.get("tool_input") or {}
        base["skill"] = next((str(tool_input[k]) for k in SKILL_FIELDS if tool_input.get(k)), "")
        return base
    return None


def main():
    record = record_for(json.loads(sys.stdin.read() or "{}"))
    if record:
        log(record)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # a log must never stop the work it logs
        log({"event": "error", "why": repr(exc)[:200]})
    sys.exit(0)
