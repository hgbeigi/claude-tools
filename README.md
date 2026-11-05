# Claude Code tools from real household work

Free Claude Code skills and plugins for household paperwork and for working well with Claude: a subscription audit for bank and card CSV exports, a safety check for other people's skills, a review step before work is called done, and more. Each one installs as a Claude Code plugin, and each skill is a plain `SKILL.md` folder you can read first.

I am a civil engineer, not a programmer. I run my household paperwork and side projects with Claude Code, and these are skills, hooks, mods and small tools I built for myself and used for real before cleaning them up for anyone to use. More come out as they are cleaned up.

## Skills

| Skill | What it does |
|---|---|
| [subscription-audit](skills/subscription-audit) | Read-only, local, no login. Reads the bank and card CSV exports you download, finds every recurring charge, and gives you one list with a "still used" column. Every row is counted, so you know nothing was skipped. It never signs in to a bank and never cancels anything. |
| [vet-outside-skill](skills/vet-outside-skill) | Before you install someone else's skill, plugin or MCP server: a scan that never runs the code, a checklist for the full read, and a written verdict. |
| [correction-to-skill](skills/correction-to-skill) | When you correct Claude, the correction becomes a dated rule in the file that caused the mistake, so the next session does not repeat it. |
| [review-gate](skills/review-gate) | Before you call work done: a second reader that cannot edit checks it against five fixed conditions. Includes the reviewer agent. |
| [delegation-kit](skills/delegation-kit) | How to brief a helper agent so it finishes without coming back to ask, and the report it hands back. |
| [session-close](skills/session-close) | Ends a session with notes and a handoff, so the next session picks up without reading the old one. |
| [check-the-record-first](skills/check-the-record-first) | Claude searches your own files before it tells you a fact or asks you a question. |
| [known-limits](skills/known-limits) | One list of what your tools cannot do and the route that works, read before anyone says "impossible". |

## Hooks

A Claude Code hook runs by itself at a set moment, so it holds where a written rule only asks. Each one below is a plugin. They read local files only and send nothing anywhere.

| Hook | What it does |
|---|---|
| [commit-privacy-guard](hooks/commit-privacy-guard) | Refuses a git commit that holds bank statements, spreadsheets, card or account numbers, a transaction ledger, or your private names. |
| [ask-after-searching](hooks/ask-after-searching) | When Claude asks you something without searching first, the question goes back once with a note to search your files. |
| [brief-check](hooks/brief-check) | Warns when a brief for a helper agent (a subagent) misses its goal, its sources or what "done" means. |
| [skill-usage-log](hooks/skill-usage-log) | Logs which Claude skills and agents actually run, and lists the ones that never did. |
| [unpushed-reminder](hooks/unpushed-reminder) | Reminds you of git commits that exist only on this computer, at most once an hour. |
| [weekday-date-check](hooks/weekday-date-check) | Flags a weekday that does not match its date in a draft, such as Monday 18 November when the 18th is a Wednesday. |

## Tools

| Tool | What it does |
|---|---|
| [skill-trigger-test](tools/skill-trigger-test) | Tests whether a Claude skill's description would make it load, against saved requests or the words you really type. |

## Coming next

Mods for the Claude Code app (`mods/`), more standalone tools (`tools/`) and writing standards (`standards/`). Each folder fills as items are cleaned up and tested.

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

## Privacy

Nothing is collected or sent anywhere. See [PRIVACY.md](PRIVACY.md).

## Licence

MIT. See [LICENSE](LICENSE).
