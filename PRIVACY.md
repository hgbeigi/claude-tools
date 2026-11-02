# Privacy

Last updated: 2 November 2026.

These plugins run inside Claude Code on your own computer. The author runs no server and collects nothing.

- **What they read:** files on your computer that you point them to, such as bank and card CSV exports you downloaded (subscription-audit), your own notes (check-the-record-first), or another skill's files (vet-outside-skill).
- **What they write:** files on your computer, such as `subscriptions.csv`, dated notes, or rules in your own instruction files.
- **What they send:** nothing. The scripts use only Python's standard library and make no network calls. Nothing reaches the author.
- **What Claude sees:** what you and the skill show it in your session, under your own agreement with Anthropic. The skills tell Claude not to paste transaction lines, amounts or account numbers into web searches or other tools.
- **Retention:** the author keeps nothing. You delete the output files whenever you want.
- **Children:** not intended for anyone under 18.

Questions: open an issue at https://github.com/hgbeigi/claude-tools/issues.
