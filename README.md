# Claude Code skills from real household work

I am a civil engineer, not a programmer. I run my household paperwork and side projects with Claude Code, and these are skills I built for myself and used for real before cleaning them up for anyone to use. More come out as they are cleaned up.

| Skill | What it does |
|---|---|
| [subscription-audit](plugins/subscription-audit) | Reads your bank and card CSV exports, finds every recurring charge, and gives you one list with a "still used" column. Every row is counted, so you know nothing was skipped. |
| [vet-outside-skill](plugins/vet-outside-skill) | Before you install someone else's skill, plugin or MCP server: a scan that never runs the code, a checklist for the full read, and a written verdict. |
| [correction-to-skill](plugins/correction-to-skill) | When you correct Claude, the correction becomes a dated rule in the file that caused the mistake, so the next session does not repeat it. |

## Install

In Claude Code:

```
/plugin marketplace add OWNER/claude-skills
/plugin install subscription-audit@hgbeigi-skills
```

Or copy one skill folder (for example `plugins/subscription-audit/skills/subscription-audit`) into your own `.claude/skills/`.

The scripts need Python 3.8 or later and use only its standard library.

## What these skills do not do

- They send nothing anywhere. The subscription audit reads CSV files on your computer and writes one CSV file back.
- They never log in to a bank or fill in a form.
- They are not financial, legal or security advice. Check what they find against your own statements.

Read any skill before you install it, these included. That is what `vet-outside-skill` is for.

## Licence

MIT. See [LICENSE](LICENSE).
