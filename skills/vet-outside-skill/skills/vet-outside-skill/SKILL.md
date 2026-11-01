---
name: vet-outside-skill
description: Checks an outside skill, plugin, MCP server, script or repository before it is installed or run, and ends in a written adopt, rebuild or reject verdict. Use when the user says "install this skill", "try this plugin", "add this MCP", "I found this repo", "is this safe", or before downloading anyone else's code into a project.
---

# Vet an outside skill

Goal: nothing from outside runs with access to the user's files until it has been read in full, scanned, tried on fake data, and the user has the verdict in writing.

## Constraints

- Nothing installs straight from a marketplace or a link. Get a copy first.
- Nothing from the folder runs while it is being vetted.
- A clean scan proves only that these patterns are absent. The full read still happens.
- Reject anything that logs in to, or fills forms on, a bank, card, insurer or government site.

## Steps

1. Source and trust: who publishes it, how many people maintain it, the last change, open security issues. A well-known publisher lowers the risk; it does not remove the read.
2. Get a copy without running it, pinned to a version or commit, into a new, empty scratch folder. Clone or download only; no install script.
3. Scan: `python -I scripts/scan_skill.py <folder>`. Explain every HIGH line, every binary file and every file the scan could not read.
4. Read every file in full, scripts included, against `reference/checklist.md`.
5. Decide: rebuild the idea yourself when it is small; adopt unchanged only when it is safe and cannot reasonably be rebuilt; reject anything that reaches money, logins or credentials.
6. An adopted item is tried on fake data first, then copied in pinned, never set to auto-update.
7. Write the verdict for the user: version, scan counts with each HIGH line explained, the checklist answers, and the decision with its reason.

## Done means

The verdict names the version, the scan counts with each HIGH line explained, every checklist line answered, and the decision with its reason. The user says yes before anything is installed.

## Known problems

- The scan flags ordinary words in documentation ("system prompt", "token"). Read the line before treating it as a finding.
- Skills often look harmless in SKILL.md and do the real work in a script. Read the scripts.
