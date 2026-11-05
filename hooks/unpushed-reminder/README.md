# Unpushed reminder

A Claude Code hook. A commit you never pushed exists on one computer only. When a turn ends, this tells you if commits have waited unpushed for 20 minutes, at most once an hour. It stays quiet the rest of the time, and it never pushes.

## Settings

In the `env` block of your Claude Code settings:

- `UNPUSHED_WAIT_MINUTES`: how long a commit waits first (default 20).
- `UNPUSHED_REPEAT_MINUTES`: the quiet time between reminders (default 60).

## Limits

It runs when a turn ends, so it cannot help if you close the session straight after a commit. A branch with no upstream is skipped. It writes one small time stamp inside the `.git` folder and reads only local git state.

## Try it

1. Make a commit here, and remind me if I forget to push it.
2. Set the unpushed reminder to wait five minutes in this project.
3. Do I have commits that exist only on this computer?

## Sample data

No sample data needed. `tests/test_reminder.py` runs on a throwaway repository with made-up commits.

## Install

```
/plugin marketplace add hgbeigi/claude-tools
/plugin install unpushed-reminder@hgbeigi-tools
```

Privacy: nothing is collected or sent anywhere. See [PRIVACY.md](../../PRIVACY.md).
