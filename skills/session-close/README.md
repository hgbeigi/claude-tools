# Session close

Ends a Claude Code session so the next one picks up from files, not the old conversation: dated notes, every promise with a status, a paste-ready handoff prompt, and a commit of only this session's files.

## Try it

1. Wrap up the session and write a handoff for tomorrow.
2. We're done. Save where we are and commit only what this session changed.
3. Write a prompt for a new session to continue this work.

## Sample data

No sample data needed: it works on the session you are in.

## Install

```
/plugin marketplace add hgbeigi/claude-tools
/plugin install session-close@hgbeigi-tools
```

Privacy: nothing is collected or sent anywhere. See [PRIVACY.md](../../PRIVACY.md).
