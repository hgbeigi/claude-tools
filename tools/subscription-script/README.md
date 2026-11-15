# subscription-script

The audit script behind the `subscription-audit` plugin, as a plain Python script for people who want to run it themselves. It reads every row of your bank and card CSV exports on your computer, counts each file twice, finds charges that repeat on a steady cadence, and writes one `subscriptions.csv` with a `still_used` column that only you fill in. It sends nothing anywhere.

```
python subscriptions.py sample-exports --out subscriptions.csv
```

Expected on the sample: both files `MATCH`, 7 recurring charges, about 283.93 a month, 12 person-to-person rows left out. The sample rows are made up. `categories.md` holds the merchant and category tables and can be edited without touching the script. Python 3.8 or later, standard library only.

It is not part of the plugin, because Claude's directory accepts scripts only from verified organizations. The plugin has Claude write the same script from `reference/method.md`.
