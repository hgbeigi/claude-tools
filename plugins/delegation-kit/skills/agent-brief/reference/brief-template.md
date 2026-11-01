# Brief template

Copy the block, fill every heading, and delete nothing. Keep the headings as written, so a brief is easy to check at a glance.

```
Goal
One sentence: what exists when you finish that did not exist before.

Skill
Load the skill <name> first and follow it. Write "none" when no skill covers the job.

Read
Full paths, one per line. Then the facts already known that you must not work out again:
- (fact, and the file it came from)

Required
The fields or questions that must come back, as a numbered list. Each one gets a value
or "blocked, because <reason and what you tried>".

Second route
A blank is not an answer. Before writing "blocked", try the next place the value can hide:
another page of the same site, the full document instead of the summary, a second tool,
a saved copy in the project folder. Name what you tried.

Limits
If the project keeps a known-limits list, read it before calling anything impossible.
Do not start helper agents of your own.
Stop and hand back before any login, payment, submitted form, sent message or deletion.

Done means
Every required item filled or "blocked, because". Every value read back from where it
was written.

Output
Write findings to: <full path>
Write the first findings within your first few steps and add to the file as you go, so a
run that stops early still leaves its work on disk.
Language: <the language the user wants>

Handback
Use the agent-report shape: done or blocked per item, sources, what was not checked,
rows or pages read, read-back of every required field, and the commit if you made one.
```

## Notes on filling it

- The goal says what exists afterwards, not what to do. "One row per account in the output file, with all eight fields" beats "look at the accounts".
- Read paths are full paths. A helper cannot turn "the budget notes" into a path.
- Pass known facts inside the brief. Do not forbid the helper from reading the project folder.
- If the result is a file, the agent type must be able to write files.
- One task per helper. "Look into everything" comes back too vague to act on.
