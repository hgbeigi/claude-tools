# Skill usage log

A Claude Code hook. A skill that never runs gives no error. When I finally measured my own setup, 0 of 39 scheduled runs had loaded a skill. This logs each skill and each helper agent as it runs, on your computer only, and reports the ones that never did.

It logs two routes: the Skill tool, and skills that load through an agent's `skills:` line. Counting one route alone shows your most-used skills at zero.

## See the report

```
python usage_report.py --days 30
```

Or ask Claude: "show my skill usage". The script is in this plugin's `scripts` folder.

## Limits

It logs from the day you install it, with no history. A skill you start by typing a slash command may not pass through the Skill tool, so it may not be counted. The "never ran" list covers skills in `.claude/skills`, not plugin skills. The log, in `claude-tools-logs` in your home Claude folder, holds times, sessions, and skill and agent names, never prompts or file contents.

## Try it

1. Show my skill usage for the last 30 days.
2. Which of my skills have never run?
3. Which agents load which skills?

## Sample data

No sample data needed. `tests/test_usage.py` runs on made-up events.

## Install

```
/plugin marketplace add hgbeigi/claude-tools
/plugin install skill-usage-log@hgbeigi-tools
```

Privacy: nothing is collected or sent anywhere. See [PRIVACY.md](../../PRIVACY.md).
