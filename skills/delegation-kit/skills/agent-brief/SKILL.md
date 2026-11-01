---
name: agent-brief
description: How to brief a helper agent, and how many to send at once. Use when the user says "send an agent", "send agents", "fan out", "split this up", "get a helper on it", "do these in parallel", or before you start any helper agent with a prompt you wrote yourself.
---

# Agent brief

Goal: a helper that reads only its brief can finish the job, or say exactly why not, without coming back to ask.

## Pick the agent first

If a named agent already fits the job (for example a reviewer), use it. Its own file carries its rules, so the brief names only the target and the output file. Otherwise write a full brief.

## A full brief

Fill every heading of `reference/brief-template.md`. Name the skill the helper must load, or write "none". The four headings most often left out:

- the second route: where to look next before writing "blocked";
- writing to the output file as it goes, so a helper that stops early still leaves its work;
- no helpers of its own;
- the language of the output.

If the job is a file, pick an agent type that can write files. Read-only types (in Claude Code, Explore and Plan) cannot, so never give them an output path.

## How many to send

Helpers share your plan's usage limit. Check how much is left first (type `/usage`, or look at your plan's usage page), then say how many you are sending and why.

- Plenty left: several helpers, each with one task.
- Running low: fewer helpers, or one.
- Helpers that read the web use more: keep those to a small number.

## Done means

Every heading of the template is filled, and you said how many helpers you sent and the usage figure that decided it.

## Known problems

- Helpers launched without checking usage can all stop at the limit with nothing written.
- A brief that does not name the output language gets English back.
- A brief that allows "say so if not found" gets blanks. Ask for a second route.
- A brief that forbids reading the project folder makes the helper miss facts already on file. Pass the known facts in the brief.
- Helpers sent at an untested site each rediscover that it refuses them. Test once first.
