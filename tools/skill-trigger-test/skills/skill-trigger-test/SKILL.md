---
name: skill-trigger-test
description: Tests whether skill descriptions would make the right skill load, against saved requests or the words you really type. Use when someone says "my skills never load", "test my skill descriptions", "why didn't my skill start", "which skill would fire", or "score my skills".
---

# Skill trigger test

Claude picks a skill by matching a request against its description. This test shows which requests would miss, and which quoted phrases the user never types.

## Steps

1. Find the skills folder. Usually `.claude/skills` in the project, or the one in the home Claude folder. Ask only if neither exists.
2. Choose the measure.
   - **Saved requests.** Write 10 to 20 real requests into a JSON file, in the user's own words, each with the skill that should start. Take them from the user, not from the descriptions, or the test proves nothing. Run:
     `python "${CLAUDE_PLUGIN_ROOT}/skills/skill-trigger-test/scripts/trigger_test.py" --skills <folder> --requests <file>`
   - **The user's own words.** This reads the user's transcripts on this computer, so say so first. Run:
     `python "${CLAUDE_PLUGIN_ROOT}/skills/skill-trigger-test/scripts/trigger_test.py" --skills <folder> --transcripts --days 90`
3. Report the score, each miss, and each skill with no quoted phrases.
4. For a miss, propose one change to the description: a quoted phrase in the words the user really typed. Change a description only when the user agrees.
5. Run the same test again and report before and after.

## Limits

Say this with the score: the test reads only the quoted phrases, while Claude reads the whole description, so it is a stand-in for comparing before and after. A skill can still load without a phrase match.

Do not quote transcript text beyond the phrase counts unless the user asks.
