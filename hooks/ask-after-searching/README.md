# Ask after searching

A Claude Code hook. When Claude asks you a question without searching first, the question goes back once with a note to search. A rule in a skill only asks for this; a hook holds. My own rule was broken three times before I built it.

## What passes

- The question says where Claude looked ("Searched notes/, not found") or that it is a "Decision:".
- The session searched since your last message.
- The same question comes a second time. You are never left without an answer.

## Settings

In the `env` block of your Claude Code settings:

- `ASK_AFTER_SEARCHING_MODE`: `remind` (default), `warn` to let it through with a note, or `off`.
- `ASK_AFTER_SEARCHING_PATHS`: words such as `notes,records`. When set, a search counts only if it names one of them, and reading a file there counts too.

## Limits

It watches the AskUserQuestion tool only, so a question written in plain chat text is not caught. It checks that a search happened, not that the search was a good one. Its log, in `claude-tools-logs` in your home Claude folder, holds the decision, a hash and the length, never the question.

Pairs with [check-the-record-first](../../skills/check-the-record-first).

## Try it

1. What is our Wi-Fi provider? (With the hook on, Claude must search your notes before it asks you.)
2. Show me the last ten decisions in the ask-after-searching log.
3. Set the ask-after-searching mode to warn for this project.

## Sample data

No sample data needed. `tests/test_ask.py` runs each case on made-up transcripts.

## Install

```
/plugin marketplace add hgbeigi/claude-tools
/plugin install ask-after-searching@hgbeigi-tools
```

Privacy: nothing is collected or sent anywhere. See [PRIVACY.md](../../PRIVACY.md).
