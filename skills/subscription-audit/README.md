# Subscription audit

Read-only, local, no login. Reads the bank and card CSV exports you download yourself, finds every recurring charge, and writes one `subscriptions.csv` with cadence, last amount, paying account and a `still_used` column that only you fill in. It never signs in to a bank and never cancels anything. It is not financial advice: you decide what to keep.

## Try it

1. Audit my recurring charges in the folder `examples/sample-exports`.
2. What am I paying every month? My bank exports are in `~/Downloads/statements`.
3. What is this charge "ADOBE *CREATIVE CLD" in my card export, and how often does it come?

## Sample data

`examples/sample-exports/` holds two made-up exports (a card and a checking account, 12 months). The rows are invented: well-known merchant names with made-up dates and amounts, and no real person or account. Expected result: both files `MATCH`, 7 recurring charges, about 283.93 a month, 12 person-to-person rows left out.

## Install

```
/plugin marketplace add hgbeigi/claude-tools
/plugin install subscription-audit@hgbeigi-tools
```

Privacy: nothing is collected or sent anywhere. See [PRIVACY.md](../../PRIVACY.md).
