# Claude Code tools from real household work

I am a civil engineer, not a programmer. I run my household paperwork and side projects with Claude Code, and these are skills, hooks, mods and small tools I built for myself and used for real before cleaning them up for anyone to use. More come out as they are cleaned up.

## Skills

| Skill | What it does |
|---|---|
| [subscription-audit](skills/subscription-audit) | Reads your bank and card CSV exports, finds every recurring charge, and gives you one list with a "still used" column. Every row is counted, so you know nothing was skipped. |
| [vet-outside-skill](skills/vet-outside-skill) | Before you install someone else's skill, plugin or MCP server: a scan that never runs the code, a checklist for the full read, and a written verdict. |
| [correction-to-skill](skills/correction-to-skill) | When you correct Claude, the correction becomes a dated rule in the file that caused the mistake, so the next session does not repeat it. |
| [review-gate](skills/review-gate) | Before you call work done: a second reader that cannot edit checks it against five fixed conditions. Includes the reviewer agent. |
| [delegation-kit](skills/delegation-kit) | How to brief a helper agent so it finishes without coming back to ask, and the report it hands back. |
| [session-close](skills/session-close) | Ends a session with notes and a handoff, so the next session picks up without reading the old one. |
| [check-the-record-first](skills/check-the-record-first) | Claude searches your own files before it tells you a fact or asks you a question. |
| [known-limits](skills/known-limits) | One list of what your tools cannot do and the route that works, read before anyone says "impossible". |

## Coming next

Hooks (`hooks/`), mods for the Claude Code app (`mods/`), standalone tools (`tools/`) and writing standards (`standards/`). Each folder fills as items are cleaned up and tested.

## Install

In Claude Code:

```
/plugin marketplace add hgbeigi/claude-tools
/plugin install subscription-audit@hgbeigi-tools
```

Or copy one skill folder (for example `skills/subscription-audit/skills/subscription-audit`) into your own `.claude/skills/`.

The scripts need Python 3.8 or later and use only its standard library.

## What these skills do not do

- They send nothing anywhere. The subscription audit reads CSV files on your computer and writes one CSV file back.
- They never log in to a bank or fill in a form.
- They are not financial, legal or security advice. Check what they find against your own statements.

Read any skill before you install it, these included. That is what `vet-outside-skill` is for.

## Licence

MIT. See [LICENSE](LICENSE).
