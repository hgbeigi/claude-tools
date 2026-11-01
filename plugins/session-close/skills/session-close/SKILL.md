---
name: session-close
description: Ends a session so the next one can pick up without the old conversation. Use when the user says "close the session", "wrap up", "we're done", "handoff", "hand off", "write a prompt for a new session", "save where we are", or "commit and push".
---

# Session close

Goal: the next session starts from files, not from this conversation. The notes say where work stopped, every promise has a status, and, in a git project, only this session's files are committed.

## What the close leaves behind

1. The project's notes file (for example `NOTES.md` in the project folder) ends with a dated entry and a "Resume here" line saying where the next session starts. If there is no notes file, start one from `reference/notes-template.md`.
2. If the project keeps a list of projects with a status column, this project's row carries today's date, its status and the next step.
3. Promised items: every item promised in this session, as `item | done, with evidence | not done | blocked, because`. Cover the whole session, not only the last task.
4. The handoff prompt, ready to paste, in the shape of `reference/handoff-template.md`. Write it into the notes file and show it in the reply.

## Committing (git projects only)

- Run `git status --short`. Stage only the files this session changed, by name. Never `git add -A` or `git add .`.
- Other changed files may belong to another session. Leave them and name them.
- Write a plain message saying what changed.
- Push if the project uses a remote. Then read back: `git log -1 --name-only` and `git status -sb`.
- The reply names the commit's short ID and says whether anything is left unpushed. No ID, no claim of "committed" or "pushed".

If the project does not use git, skip this part and say so.

## Done means

The notes file was read back, every promised item has a status, the handoff follows the template, and, in a git project, the reply gives the commit ID with its files. End with READY, or BLOCKED and the reason.

## Known problems

- `git add -A` sweeps in another session's files. Stage by name.
- A status list that closes skip falls behind within a week.
- "Committed and pushed" has been reported when nothing reached the repository. Read the commit back.
