# Method

_Write a small script that follows this, and run it. Standard library only. It reads local files and sends nothing anywhere. Print counts only, never a transaction line._

## 1. Read every row, and count it twice

- Open each `.csv` under the folder (not the output file). Decode as UTF-8 with a byte-order mark, and fall back to cp1252.
- Count 1: parse with a CSV reader, dropping blank rows. Count 2: a quote-aware scan of the raw text that counts lines holding any data, with no CSV reader. A header row is not a record.
- A file is `MATCH` only when the file count, the rows read and the rows kept all agree. Otherwise it is `MISMATCH` (with the counts), or `REFUSED` when the first row has no date, description and amount columns. Never guess at a refused file and never report it as read.

## 2. Formats

Recognise the header, case-insensitively: Chase checking and card, Discover card and bank, Capital One, Mint, Wells Fargo (with or without a header; the bare file is date, amount, `*`, blank, description), or any file with date, description and either one amount column or debit and credit columns.

Make every amount signed so that money out is negative. Discover card files show purchases as positive, so flip them. Dates come as `%m/%d/%Y`, `%Y-%m-%d`, `%m/%d/%y`, `%d %b %Y` or `%b %d, %Y`. Amounts may carry `$`, commas, or parentheses for negative. Shorten any run of eight or more digits in a description to `****` and its last four. Label the account from the bank name and the last four digits in the file name (`card-1234.csv`).

## 3. Classify each row with `categories.md`

Upper-case the description. Check, in order: the Person-to-person table (Zelle, Venmo, Cash App; counted and left out, never named), then the Patterns table (first match wins), then the bank's own category in the Bank categories table. Money out with no flow is `spend`; money in is `refund` on a card and `income` on a bank account. Transfers between the user's own accounts, card payments, income, refunds and person-to-person rows are not charges.

## 4. Find the recurring charges

- Group money-out rows by merchant: strip processor prefixes (`SQ *`, `TST*`, `PAYPAL *`, `ACH DEBIT` and similar), drop punctuation and any word holding a digit, keep the first four words. Merge two keys of one category when one starts with the other's words, or both start with the same distinctive word of four or more letters that is not in the Common first words table.
- Gaps are the days between distinct charge dates. The cadence is the first of weekly (5 to 9 days), biweekly (11 to 17), monthly (25 to 36), bimonthly (52 to 70), quarterly (80 to 102), semiannual (160 to 205), annual (330 to 400) whose range holds the median gap and at least 60% of the gaps. Also call it monthly when three or more months are spanned, 80% of them hold a charge and the median gap is 10 days or more. A shop that charges every month on a different day still counts.
- The amount is fixed when at least 60% of charges are within 15% (or 1.00) of the median.
- `recurring`: three or more dates with a cadence, and either a fixed amount or a group of bills-and-loans or subscriptions; or two or more annual charges with a fixed amount. `possible`: a subscriptions-group merchant with two or more charges and no clear cadence. Everything else is dropped, and an everyday-group merchant with a moving amount is dropped.
- `active` when the last charge is within 1.5 cadences (at least 45 days) of the newest row on that account; 400 days for annual and possible charges. Otherwise `ended`.
- A charge needs tracing (`trace_needed`) when no pattern named what it is, or its category is in the Trace routes table and the amount moves. `trace_where` is that table's route. A cloud or AI bill whose amount moves is never called fixed.
- `monthly_equivalent` is the median times 30.4 divided by the cadence in days. The cadence in days is 7 for weekly, 14 for biweekly, 30.4 for monthly, 61 for bimonthly, 91 for quarterly, 182 for semiannual and 365 for annual.
- Both `recurring` and `possible` rows go in the list and in the "recurring charges" count; the `kind` column tells them apart. The `other` and `fees` groups follow the same rules as any group that is not bills-and-loans, subscriptions or everyday.
- Use the transaction date, not the post date. Treat a first row with no date in its first cell as a header. For Mint, the transaction type column gives the sign.

## 5. Write `subscriptions.csv`

Columns: merchant, group, category, kind, cadence, count, last_amount, median_amount, monthly_equivalent, first_seen, last_seen, paying_account, all_accounts, status, what_for_guess, still_used, trace_needed, trace_where, last_source. Sort active first, then by group and merchant.

If the file already exists, carry each `still_used` answer forward by merchant before overwriting, and keep every row whose `kind` is `added` until the audit finds that merchant itself. A rerun must never wipe the user's answers.

## 6. Print, counts only

Per file: status, format, rows in file, rows read, rows kept. Then: files, rows, window start; recurring, active, monthly total; active by group; how many need tracing; person-to-person rows left out; answers carried forward; active rows still blank.

## Check against the sample

`examples/sample-exports` holds two made-up files. Your script must give: both files `MATCH` (97 and 60 rows), 7 recurring charges, all active, about 283.93 a month, 12 person-to-person rows left out. If it does not, fix the script before touching real data.

A tested script that follows this method is in the repository's `tools/subscription-script` folder, for people who want to run it themselves.
