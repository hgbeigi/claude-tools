---
name: review-gate
description: A read-only second check of a plan, document or finished piece of work before it is called done. Use when the user says "review this", "check your work", "is it ready?", "grade it", "pre-mortem", "independent check", or before you write "ready" or "done" on work with several steps.
---

# Review gate

Goal: nothing is called done until a second reader, who did not write it, has checked it against a closed list. Anything that blocks is kept apart from advice.

## Constraints

- Read-only. A reviewer that can edit starts fixing instead of reporting.
- The writer never grades its own work. Send it to the `reviewer` agent in this plugin, or open a fresh session.
- An empty result is valid. The planted-defect test, not the number of findings, shows the gate works.

## Blocking: the closed list

Exactly these five. Nothing else blocks, and no sixth is added.

1. It breaks a written rule in the project's instruction file (for example `CLAUDE.md`). Quote the rule.
2. It quietly reverses a recorded decision. Quote the decision. If you keep no decisions file, start one from `reference/decisions-template.md`.
3. It names a checker, script, test or automatic step that does not exist.
4. It claims completion (done, ready, sent, saved, committed) with no evidence or read-back beside it.
5. It names a file or folder path that does not exist.

Each blocking item gives the condition number, the line, and what would clear it.

## Advice

Everything else. Each item names a risk and a rough cost, with no replacement wording. Advice never stops work.

## Steps

1. Pre-mortem: write three to five lines answering "three months from now this failed; how?" A line that matches a blocking condition moves to Blocking. The rest are advice.
2. Send the work to the reviewer with the file path only. Do not say what you expect it to find.
3. Return two sections, Blocking then Advice. An empty section says "none".

## Done means

Both sections are present, every blocking item cites one of the five conditions, and the gate has passed `reference/planted-defect-test.md` at least once.

## Known problems

- A gate that has only ever passed things is untested. Feed it a known failure before trusting it.
- An open-ended reviewer grows the document every round. The closed list is what makes it stop.
