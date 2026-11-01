---
name: known-limits
description: The register of what the tools cannot do, and the route that works instead. Read it before saying "impossible", "can't access", "blocked", "not supported" or "it won't open". Use when the user says "is there any way", "can we connect", "did you try the browser", "you need to find a way", "why can't you", or before sending a helper agent at a site or file type that failed before.
---

# Known limits

Goal: no time goes on retrying what is known to fail, and nothing is called impossible after one look.

## The rule

Read the register before saying "impossible". Every "impossible" or "blocked" then names the method tried, the message it gave, and the second way tried or proposed.

"The web fetch tool and the browser both refused the site; the site's official download is the next route" is a finding. "The site is blocked" is not.

## Set up once

Copy `reference/limits.md` into the project folder. That copy is the register. It starts with three example entries; keep one only if you have seen it yourself.

## Use

1. Before calling something impossible, or sending a helper agent at a site or file it names, read the register.
2. If an entry matches, follow its route, and copy the entry into the helper's brief.
3. If nothing matches, try a second way before reporting a limit. Name both ways in the report.
4. When the same limit is confirmed twice, add a dated entry.

## Constraints

- A limit is a claim about a tool on a date. Tools change. If an entry is more than a month old and matters, test it once before trusting it.
- A refusal from the permission system is not missing access. Name the route the user has approved, rather than asking for more permission.
- After one failed sign-in, stop and tell the user. Repeated attempts can lock the account for longer.

## Done means

The answer or report names the method tried and the second way for every limit it hits.

## Known problems

- Several helper agents each rediscovered the same refusal because nobody read the register first.
- A file was called unreadable when it only needed a different tool.
- Three workarounds were tried before anyone checked whether the thing was supported. Read the official documentation first.
