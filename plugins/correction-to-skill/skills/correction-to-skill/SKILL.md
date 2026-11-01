---
name: correction-to-skill
description: Turns a correction from the user into a dated rule in the skill, agent or instruction file that caused the mistake, in the same session, and says where it went. Use when the user says "that's wrong", "not what I asked", "I told you before", "why didn't you", "remember this", "from now on", or "learn from this".
---

# Correction to skill

Goal: a correction changes the rule that caused the mistake, so the next session cannot repeat it, and the user can see where it went.

## Constraints

- One home per rule. Find the file that owns it; do not scatter copies.
- A rule goes into the file that runs, not into a memory note. Memory is for facts about one computer.
- A correction that would reverse an earlier recorded decision is not filed. Quote the decision to the user and ask.
- A shared file that other projects use is not edited from inside one project. Write the change up for its own repository and say so.

## Steps

1. Write the correction as one line: what was wrong, what is right, and the source (the user's words, a document, a check).
2. Find the owner with `reference/filing-table.md`. Search the target first. If the rule is already there and was broken anyway, the fix is a sharper rule or a check, not a second copy.
3. If the procedure itself caused the mistake, change the step. Then add a dated line under Known problems: the date, what happened, the rule now.
4. If the skill file is getting long, move its dated lines into `reference/known-problems.md` and leave a pointer.
5. Read the change back from the file and tell the user in one line where it went (path and section).
6. If the folder is a git repository, commit that file alone, naming the skill.

## Done means

The rule or step changed, the dated line sits in the owner file and was read back, the user was told the path, and, in a repository, the commit names the skill.

## Known problems

- A correction left in the chat is lost when the session ends. File it before the session closes.
- A rule written as advice ("try to...") gets broken. Write what to do, and add a check where one is possible.
