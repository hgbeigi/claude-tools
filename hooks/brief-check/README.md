# Brief check

A Claude Code hook. A helper agent knows only what its brief says. Before a general-purpose agent starts, this checks that the brief holds the words Goal, Read, Required, Done and Output, and warns about any that are missing. Named agents and built-ins such as Explore pass, because they carry their own rules.

## Settings

In the `env` block of your Claude Code settings:

- `BRIEF_CHECK_MODE`: `warn` (default), `block` to refuse the call, or `off`.
- `BRIEF_CHECK_WORDS`: your own comma-separated section words.

## Limits

It looks for the words, not for good sections. A brief can pass and still be poor. Its log, in `claude-tools-logs` in your home Claude folder, holds the agent type, the decision and the length, never the brief.

Pairs with [delegation-kit](../../skills/delegation-kit), whose template holds the five sections.

## Try it

1. Send a helper agent to list the TODO comments in this folder. (A short brief draws the warning.)
2. Set the brief check to block for this project.
3. Show me which briefs the check warned about this week.

## Sample data

No sample data needed. `tests/test_brief.py` runs each case on made-up briefs.

## Install

```
/plugin marketplace add hgbeigi/claude-tools
/plugin install brief-check@hgbeigi-tools
```

Privacy: nothing is collected or sent anywhere. See [PRIVACY.md](../../PRIVACY.md).
