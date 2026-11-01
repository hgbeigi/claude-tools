# Handoff template

The fixed shape for the paste-ready prompt that ends a session. Copy it, fill every heading, and keep the headings in this order. A heading with nothing under it says "none". Do not break lines by hand; the prompt is pasted as it is.

```
DO: <one sentence: the work the next session continues, and the project it belongs to>

Open in: <the project folder>

Files to load, in order:
1. <path>: <why, in a few words>
2. <path>: <why>

State already written (do not redo):
- <what is finished, the file that holds it, and the commit ID if there is one>

What is next:
1. <the first step, concrete enough to start without asking>
2. <the step after>

Questions, each with its default:
- Q1. <one decision>. Default: <what happens if nobody answers>.

Stop and ask before: <any login, payment, sent message or deletion the next steps would reach>.
```

## Rules for filling it

- Every path is a full path, or a path from the project folder.
- "State already written" names files and commits, never "we discussed". If something is only in the conversation, write it into the notes file first.
- "What is next" starts with the step named on the notes file's "Resume here" line.
- One decision per question, each with a default. Where there is a choice, give lettered options.
- If nothing is next, say the project is at rest and why.
