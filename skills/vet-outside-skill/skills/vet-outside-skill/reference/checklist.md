# Outside skill checklist

_Answer every line in the verdict._

## Source

- Publisher, repository, licence, number of maintainers, date of last change.
- Exact version or commit pinned.
- Open issues or advisories that mention security.

## What it can reach

- Network: every address it calls, and why.
- Files: every path it reads or writes outside its own folder.
- Commands: every shell, subprocess or eval call, and what it runs.
- Credentials: does it read tokens, cookies, keychains, `.ssh`, `.aws`, browser profiles or password stores?
- Claude itself: does it change settings, hooks, permissions, CLAUDE.md or memory, or carry text telling the model to hide something from the user?
- Money and identity: does it log in to, or fill forms on, a bank, card, insurer or government site? Reject if yes.

## What it does

- The job in one sentence, and whether something already installed does it.
- What it adds to every session (the description is always loaded), and whether it should start only when called by name.
- What rebuilding it yourself would cost, in hours, against adopting it.

## Trial

- Run on fake data in a scratch folder, with its network calls watched.
- The result, and anything unexpected.

## Verdict

Adopt unchanged, rebuild, or reject, with the reason in one sentence and a date to look again.
