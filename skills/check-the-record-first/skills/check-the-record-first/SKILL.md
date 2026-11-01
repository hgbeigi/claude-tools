---
name: check-the-record-first
description: Search the user's own notes and files before stating a fact about their health, money, home, car, insurance or accounts, and before asking them a question. Use when the user says "you should have known", "we already have that", "you have that already", "why are you asking", "check first", "look in my files", "it's in my notes", or before answering any question on a form.
---

# Check the record first

Goal: every fact stated about the user's life comes from a file or page opened in this session, and the user is asked only what the record cannot answer.

## Set up once

Copy `reference/where-to-look.md` into the project folder and fill it in: which folders hold which subjects, and where decisions and old session notes live. Until it is filled in, search the whole project folder.

## Where to look

1. One search across the project folder for the subject word (a name, a provider, an account, a symptom).
2. The places named in the user's filled-in `where-to-look.md`, in its order.
3. The decisions file and the project's notes, for anything already settled.
4. Notes from past sessions, if the user keeps them.

## Constraints

- Open the files. A folder name, a file title or a line on a form is not evidence of what is inside.
- Health: read the full record before summarizing it. Never treat a condition as milder because a form line is short.
- Name the source and its date beside each fact. A status older than the last session that touched the subject is out of date until it is read again.
- When you do ask the user, say where you looked first.

## Done means

Each fact in the answer names its file or page, and any question to the user lists the places searched.

## Known problems

- A plan was called expired from a folder name. The files inside showed otherwise.
- A health answer was taken from one line on a form. A full report in the user's files changed the picture.
- The user was asked how many accounts they have, when the account page was open to read.
- A session opened in the wrong folder never loaded this skill, and asked what the records already answered. Open the session in the records folder.
