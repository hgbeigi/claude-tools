# Where a correction goes

| The correction is about | Its home | Example |
|---|---|---|
| A step of one skill | That skill's `SKILL.md` step, plus a dated line under Known problems | The audit skipped a column the user always wants |
| A checklist field, or where a value hides | The skill's reference checklist | The interest rate is on the terms page, not the summary |
| How one agent behaves | Its definition file in `.claude/agents/` | The reader agent must not click buttons |
| Something every session must do | The project's `CLAUDE.md`, as one numbered rule | Search the user's files before asking them |
| A fact about the user's own setup | The project file that holds those facts | Which account pays which bill |
| What a tool cannot do, and the route that works | One "known limits" file, read before saying "impossible" | A connector cannot search the spam folder |
| This computer only (a path, a profile, a device) | A memory note | Which browser profile holds which sign-in |
| A shared standard used by several projects | Written up for that standard's own repository, not edited here | A writing rule that holds everywhere |

When two rows fit, the narrower one wins, and the wider file gets a one-line pointer.
