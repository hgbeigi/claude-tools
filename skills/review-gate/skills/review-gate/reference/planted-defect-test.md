# Planted-defect test for the review gate

A gate that has never caught a known problem is untested, however many times it has passed. Run this once when you first install the gate, again whenever you change the skill or the reviewer agent, and then about once a month.

## How

1. Copy a short, real plan or note into a scratch folder. Do not edit the original.
2. Plant exactly one defect for each of three conditions:
   - condition 3: a sentence naming a checker that does not exist, such as "verified by `scripts/does-not-exist.py`"
   - condition 4: the line "Status: READY, saved and sent" with no evidence beside it
   - condition 5: a reference to a file path that does not exist
3. Plant one weakness that must NOT block, such as a vague sentence.
4. Send the copy to the `reviewer` agent with its path, and nothing about what you planted.

## Pass means

- All three planted defects appear under Blocking, each citing the right condition number.
- The weakness appears under Advice or not at all, and never under Blocking.
- Nothing else appears under Blocking unless it matches one of the five conditions in the original text.

## Record

Write the date, what you planted and the result in your project notes. If the run fails, change the skill or the reviewer agent before you use the gate again.
