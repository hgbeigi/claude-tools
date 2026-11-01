---
name: agent-report
description: The handback shape for work given to a helper agent, and the read-back before anything is called done. Use when a helper finishes, or when the user asks "is it done?", "did you check?", "did you verify?", "did you finish?".
---

# Agent report

Goal: whoever sent the work can rely on the report without redoing it, and can see at once what was not done.

## The shape

At the top of the output file and in the handback:

1. Status per required item: `done` with the value, or `blocked, because` with the reason and what was tried. No other status counts.
2. Sources: the page, file or document behind each value.
3. Not checked: what was not looked at, and why.
4. Coverage: rows read out of rows in the file, or pages read out of pages available.
5. Read-back: each required value was read back from where it was written, and where.
6. Commit, if the project uses git: the commit's short ID from `git log -1` and its files from `git log -1 --name-only`. No ID, no claim of "committed".
7. Overall: `ready` only when every item is done or honestly blocked and the read-back is complete. Otherwise `blocked`, with the list.

## Rules

- Never write "read", "done" or "confirmed" beside a blank. A blank is "blocked, because", so the record shows what is missing.
- A tool's success message is not evidence. Read the result back where the user would see it.
- One search that finds nothing gives "not found in <where>", not "does not exist".
- Write the report to the output file, not only into the chat.

## Done means

The output file holds the shape above, every required item has a value or "blocked, because", and the read-back line names where each value was checked.

## Known problems

- A command that reports success whatever it is given proves nothing. Check the result, not the message.
- "It is not there" is often said before the right page was opened. Name the page you opened.
- "The form is filled" was said with required fields still empty. Read each field back.
- A helper that ran a very long time without writing anything left nothing behind when it stopped. Write as you go.
