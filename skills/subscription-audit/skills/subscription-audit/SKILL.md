---
name: subscription-audit
description: Lists every recurring charge in a folder of bank and card CSV exports, with cadence, last amount, the paying account and a "still used" column you fill in. Use when the user says "what subscriptions do I have", "what am I paying every month", "cancel subscriptions", "what is this charge", or "audit my recurring charges".
---

# Subscription audit

Goal: one list of every recurring charge, each one kept or cancelled by the user, and none left unexplained.

## Constraints

- Local only. Read the CSV files on this computer and sends nothing anywhere. Never paste transaction lines, amounts or account numbers into a web search or another tool.
- Every row is read and counted. A file is trusted only when its row counts agree under two independent counts (step 3).
- `still_used` holds only the user's own answers, never a guess.
- An unexpected charge is never explained from its timing ("it started when I signed up for X"). Name it only from the seller's own billing page.
- Payments between people (Zelle, Venmo, Cash App) are counted and left out, never named or totalled per person.

## Steps

1. Ask the user for a folder of CSV exports. Each bank and card site has a "Download" or "Export" button on its activity page. Twelve months gives annual charges a chance to show. A file name with the account's last four digits (`card-1234.csv`) labels the account.
2. Write a short script of your own, following `reference/method.md`, and run it on the folder. Keep the script in a scratch folder outside the exports. It writes `subscriptions.csv` outside the exports folder. Use Python if it is installed; if not, use whatever the computer has. Check it on `examples/sample-exports` first.
3. Count every file twice, as `reference/method.md` says. A file whose counts disagree, or whose format you do not know, is named with the reason and never reported as read. For an unknown format, compare three rows with the statement, then add the bank to `reference/categories.md`.
4. Report the counts your script printed: files, rows, active charges, the monthly total, by group, and how many need tracing. Do not list every row in the chat; the file holds them.
5. For each `trace_needed` row, tell the user where to look (`trace_where`) to name the product.
6. Ask the user to fill `still_used` (yes, no, or cancel). A rerun keeps those answers. A charge the user knows about that the exports do not show yet can be added as a row with `kind` set to `added`.
7. Wrong category: fix the pattern in `reference/categories.md` and run your script again. Never edit the output by hand.

## Done means

`subscriptions.csv` exists, every file matched its two counts or was named with its reason, the counts were read back from your script's output, and every `trace_needed` row has a place to look.

## Known problems

- A cloud or AI charge that changes every month is often two products on one account. The billing report, by product, is the only way to tell.
- Virtual card services (such as Privacy.com) hide the merchant. Their card list names it.
- Two merchants that share a first word (a city or county name) can merge. Add the word to the Common first words table.
