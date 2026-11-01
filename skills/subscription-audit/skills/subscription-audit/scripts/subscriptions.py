#!/usr/bin/env python3
"""List every recurring charge in a folder of bank and card CSV exports.

Why this exists. Subscriptions hide across several cards and accounts, and a
summary read from the first page of a statement misses rows. This reads every
row of every export, proves the count, finds the charges that repeat on a
steady cadence, and writes one list with a "still_used" column for you to fill.

Every file is counted twice: once by the csv parser and once by a scan that
does not use it. A file is MATCH only when both counts and the rows written
agree. A file that is not a transaction export is reported and skipped,
never guessed at.

Category guesses come from the tables in ../reference/categories.md, which you
can edit without touching this script. Payments between people (Zelle, Venmo,
Cash App) are counted and left out. Transfers between your own accounts and
card payments are not charges and are left out.

Usage:
    python subscriptions.py EXPORTS_FOLDER_OR_FILES [...] --out subscriptions.csv
                            [--since 2025-01-01] [--rules categories.md]

If --out already exists, your "still_used" answers are carried forward by
merchant, so a rerun never wipes them. A row whose kind you set to "added"
(a charge you know about that the exports do not show yet) is kept until the
script finds that merchant itself.

Prints counts only, never a transaction line. Reads local files only and
sends nothing anywhere. Python 3.8 or later, standard library only.
Exit 0 when every file matched its count, 1 when any file did not, 2 when it
could not run.
"""

import argparse
import csv
import io
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
CATEGORIES = HERE.parent / "reference" / "categories.md"
ADDED = "added"
COLUMNS = ["merchant", "group", "category", "kind", "cadence", "count", "last_amount", "median_amount",
           "monthly_equivalent", "first_seen", "last_seen", "paying_account", "all_accounts", "status",
           "what_for_guess", "still_used", "trace_needed", "trace_where", "last_source"]


# ------------------------------------------------------------------ rules file
def split_cells(line):
    cells = re.split(r"(?<!\\)\|", line.strip())
    return [c.strip().replace("\\|", "|") for c in cells[1:-1]]


def read_tables(path):
    """Return {section title: [row cells, ...]} for every markdown table, header row dropped."""
    tables, section = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            tables[section] = []
        elif section and line.startswith("|"):
            cells = split_cells(line)
            if cells and not set("".join(cells)) <= set("-: "):
                tables[section].append(cells)
    return {name: rows[1:] for name, rows in tables.items()}


class Rules:
    NEED = ["Patterns", "Person-to-person", "Bank categories", "Common first words", "Groups", "Trace routes"]

    def __init__(self, path):
        t = read_tables(path)
        missing = [n for n in self.NEED if n not in t]
        if missing:
            raise SystemExit(f"subscriptions: {path} lacks the table(s) {missing}")
        self.patterns = [(re.compile(r[0]), r[1], r[2], r[3] if len(r) > 3 else "") for r in t["Patterns"]]
        self.p2p = [re.compile(r[0]) for r in t["Person-to-person"]]
        self.bank = {r[0].lower(): (r[1], r[2] if len(r) > 2 else "") for r in t["Bank categories"]}
        self.common_first = {r[0].strip().upper() for r in t["Common first words"] if r}
        self.groups = {r[0]: r[1] for r in t["Groups"]}
        self.trace = {r[0]: r[1] for r in t["Trace routes"]}

    def match_pattern(self, up):
        for rx, cat, flow, what in self.patterns:
            if rx.search(up):
                return cat, flow, what
        return None

    def classify(self, desc, amount, bank_label, is_card):
        up = desc.upper()
        if any(rx.search(up) for rx in self.p2p):
            return "person-to-person", "person-to-person"
        hit = self.match_pattern(up)
        if hit is None and bank_label and bank_label.lower() in self.bank:
            cat, flow = self.bank[bank_label.lower()]
            hit = (cat, flow, "")
        cat, flow, _ = hit or ("other", "", "")
        if not flow:
            flow = "spend" if amount < 0 else ("refund" if is_card else "income")
        return cat, flow


# ------------------------------------------------------------------ reading exports
def count_records(text):
    """Count records holding any data with a quote-aware scan, not the csv module."""
    count, in_q, has_data = 0, False, False
    for ch in text:
        if ch == '"':
            in_q = not in_q
        elif ch == "\n" and not in_q:
            count += has_data
            has_data = False
        elif ch not in " \t\r,":
            has_data = True
    return count + has_data


def parse_date(raw):
    raw = raw.strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y", "%d %b %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"date not understood: {raw[:12]!r}")


def parse_amount(raw):
    raw = (raw or "").strip().replace("$", "").replace(",", "").replace(" ", "")
    if raw in ("", "-", "--"):
        return 0.0
    neg = raw.startswith("(") and raw.endswith(")")
    value = float(raw.strip("()"))
    return -value if neg else value


def clean_description(text):
    text = " ".join((text or "").split())
    return re.sub(r"\d{8,}", lambda m: "****" + m.group(0)[-4:], text)


# name: (institution, is_card, required header names, how to read one row)
FORMATS = [
    ("chase-checking", "Chase", False, ["details", "posting date", "description", "amount", "type", "balance"]),
    ("chase-card", "Chase", True, ["transaction date", "post date", "description", "category", "type", "amount"]),
    ("discover-card", "Discover", True, ["trans. date", "post date", "description", "amount", "category"]),
    ("discover-bank", "Discover", False, ["transaction date", "transaction description", "transaction type",
                                          "debit", "credit"]),
    ("capital-one", "Capital One", True, ["transaction date", "posted date", "card no.", "description", "debit",
                                          "credit"]),
    ("mint", "Mint", None, ["date", "original description", "amount", "transaction type", "account name"]),
    ("wells-fargo", "Wells Fargo", None, ["date", "description", "amount", "check #", "status"]),
]


def detect(header):
    h = [c.strip().strip('"').lower() for c in header]
    for name, inst, is_card, need in FORMATS:
        if set(need) <= set(h):
            return name, inst, is_card, True, None
    # Wells Fargo's own download has no header: date, amount, *, blank, description.
    if len(header) == 5 and header[2].strip() == "*":
        try:
            parse_date(header[0])
            parse_amount(header[1])
            return "wells-fargo-bare", "Wells Fargo", None, False, None
        except ValueError:
            pass

    def find(*names):
        for exact in (True, False):
            for name in names:
                for i, c in enumerate(h):
                    if (c == name) if exact else (name in c):
                        return i
        return None
    g = dict(date=find("date", "posting date", "transaction date", "posted date"),
             desc=find("description", "payee", "merchant", "name", "memo"),
             amount=find("amount"), debit=find("debit", "withdrawal"), credit=find("credit", "deposit"),
             cat=find("category"))
    if g["date"] is not None and g["desc"] is not None and (
            g["amount"] is not None or (g["debit"] is not None and g["credit"] is not None)):
        return "generic", "", None, True, g
    return None, "", None, True, None


def read_row(fmt, col, r, g):
    """Return (date, signed amount, description, bank label, last four or '') for one data row."""
    if fmt == "chase-checking":
        return parse_date(col(r, "posting date")), parse_amount(col(r, "amount")), col(r, "description"), \
            col(r, "type"), ""
    if fmt == "chase-card":
        return parse_date(col(r, "transaction date")), parse_amount(col(r, "amount")), col(r, "description"), \
            col(r, "type") if col(r, "type").lower() in ("payment", "return", "fee") else col(r, "category"), ""
    if fmt == "discover-card":  # purchases are positive in Discover's file
        return parse_date(col(r, "trans. date")), -parse_amount(col(r, "amount")), col(r, "description"), \
            col(r, "category"), ""
    if fmt in ("discover-bank", "capital-one"):
        amt = parse_amount(col(r, "credit")) - parse_amount(col(r, "debit"))
        d = col(r, "transaction date")
        desc = col(r, "transaction description") or col(r, "description")
        return parse_date(d), amt, desc, col(r, "category"), col(r, "card no.")
    if fmt == "mint":
        amt = parse_amount(col(r, "amount"))
        amt = -amt if col(r, "transaction type").lower() == "debit" else amt
        return parse_date(col(r, "date")), amt, col(r, "original description") or col(r, "description"), \
            col(r, "category"), col(r, "account name")
    if fmt == "wells-fargo":
        return parse_date(col(r, "date")), parse_amount(col(r, "amount")), col(r, "description"), "", ""
    if fmt == "wells-fargo-bare":
        return parse_date(r[0]), parse_amount(r[1]), r[4] if len(r) > 4 else "", "", ""
    amt = parse_amount(r[g["amount"]]) if g["amount"] is not None else \
        parse_amount(r[g["credit"]]) - parse_amount(r[g["debit"]])
    return parse_date(r[g["date"]]), amt, r[g["desc"]], r[g["cat"]] if g["cat"] is not None else "", ""


def read_file(path, rules):
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    data = [r for r in csv.reader(io.StringIO(text, newline="")) if any(c.strip().strip('"') for c in r)]
    res = dict(file=path.name, format=None, in_file=None, read=0, written=0, refused=[], note="")
    if not data:
        res["note"] = "empty file"
        return res, []
    fmt, inst, is_card, has_header, g = detect(data[0])
    res["format"] = fmt
    if fmt is None:
        res["note"] = "not a transaction export: no date, description and amount columns in the first row"
        return res, []
    header = [c.strip().strip('"').lower() for c in data[0]]
    idx = {h: i for i, h in enumerate(header)}

    def col(r, name):
        i = idx.get(name)
        return r[i] if i is not None and i < len(r) else ""

    body = data[1:] if has_header else data
    res["in_file"] = count_records(text) - (1 if has_header else 0)
    name_four = re.search(r"(?<!\d)(\d{4})(?!\d)", path.stem)
    if is_card is None:
        is_card = "card" in path.name.lower()
    rows = []
    for n, r in enumerate(body, 1):
        res["read"] += 1
        try:
            d, amt, desc, label, four = read_row(fmt, col, r, g)
        except (ValueError, IndexError) as exc:
            res["refused"].append((n, str(exc)))
            continue
        four = (re.search(r"\d{4}", four or "") or name_four or re.search("", "")).group(0)
        account = f"{inst or path.parent.name} {four}".strip()
        desc = clean_description(desc)
        cat, flow = rules.classify(desc, amt, label, is_card)
        rows.append(dict(date=d, amount=amt, description=desc, category=cat, flow=flow, account=account,
                         source=f"{path.name} row {n}"))
    res["written"] = len(rows)
    if not res["read"] == res["written"] == res["in_file"]:
        res["note"] = (f"{res['in_file']} rows in the file, {res['read']} read, {res['written']} written, "
                       f"{len(res['refused'])} refused")
    return res, rows


# ------------------------------------------------------------------ finding recurring charges
CADENCES = [("weekly", 7, 5, 9), ("biweekly", 14, 11, 17), ("monthly", 30.4, 25, 36), ("bimonthly", 61, 52, 70),
            ("quarterly", 91, 80, 102), ("semiannual", 182, 160, 205), ("annual", 365, 330, 400)]
PREFIXES = re.compile(r"^(?:SQ ?\*|TST\* ?|PY \*|SP |IC\* ?|FSP\*|CTLP\*|PAYPAL \*|PAYPAL INST XFER |EB \*|CL \*|"
                      r"DD \*|ACH WITHDRAWAL |ACH DEBIT |POS PURCHASE |PURCHASE AUTHORIZED ON |RECURRING PAYMENT )")
NOT_CHARGES = {"transfer-own", "card-payment", "person-to-person", "income", "refund"}


def merchant_key(desc):
    up = PREFIXES.sub("", desc.upper())
    up = up.replace("GOOGLE *", "GOOGLE ").replace("*", " ").replace("#", " ")
    up = re.sub(r"\b(WEB|PPD|TEL|CCD|CTX)?\s*ID:.*$", " ", up)
    tokens = [t for t in re.split(r"[\s,/\-]+", up) if t and not re.search(r"\d", t)]
    return " ".join(tokens[:4]) or up[:20]


def merge_groups(groups, common_first):
    """Merge keys of one category when one key's words begin the other's, or both start
    with the same distinctive word. Words in the Common first words table never count."""
    def cat(rs):
        return Counter(r["category"] for r in rs).most_common(1)[0][0]
    merged = {}
    for k in sorted(groups, key=lambda k: (len(k.split()), k)):
        toks = k.split()
        target = next((m for m in merged if cat(merged[m]) == cat(groups[k]) and (
            toks[:len(m.split())] == m.split() or
            (toks[0] == m.split()[0] and toks[0] not in common_first and len(toks[0]) >= 4))), None)
        if target:
            merged[target] += groups[k]
        else:
            merged[k] = list(groups[k])
    return merged


def cadence_of(dates):
    gaps = [(b - a).days for a, b in zip(dates, dates[1:])]
    if not gaps:
        return None, None
    med = statistics.median(gaps)
    for name, days, lo, hi in CADENCES:
        if lo <= med <= hi and sum(lo <= g <= hi for g in gaps) / len(gaps) >= 0.6:
            return name, days
    months = {(d.year, d.month) for d in dates}
    span = (dates[-1].year - dates[0].year) * 12 + dates[-1].month - dates[0].month + 1
    if span >= 3 and len(months) / span >= 0.8 and med >= 10:
        return "monthly", 30.4
    return None, None


def find_recurring(rows, since, rules):
    end_by_account = {}
    for r in rows:
        end_by_account[r["account"]] = max(end_by_account.get(r["account"], r["date"]), r["date"])
    groups = defaultdict(list)
    for r in rows:
        if r["date"] >= since and r["amount"] < 0 and r["flow"] not in NOT_CHARGES:
            groups[merchant_key(r["description"])].append(r)
    found = []
    for key, rs in merge_groups(groups, rules.common_first).items():
        rs.sort(key=lambda r: r["date"])
        dates = sorted({r["date"] for r in rs})
        amounts = [-r["amount"] for r in rs]
        med = statistics.median(amounts)
        fixed = sum(abs(a - med) <= max(0.15 * med, 1.0) for a in amounts) / len(amounts) >= 0.6
        cat = Counter(r["category"] for r in rs).most_common(1)[0][0]
        group = rules.groups.get(cat, "other")
        name, days = cadence_of(dates)
        if group == "everyday" and not fixed:
            continue
        if len(dates) >= 3 and name and (fixed or group in ("bills-and-loans", "subscriptions")):
            kind = "recurring"
        elif name == "annual" and len(dates) >= 2 and fixed:
            kind = "recurring"
        elif group == "subscriptions" and len(rs) >= 2:
            kind = "possible"
        else:
            continue
        last = rs[-1]
        window = 400 if kind == "possible" or name == "annual" else max(45, 1.5 * days)
        status = "active" if (end_by_account[last["account"]] - last["date"]).days <= window else "ended"
        hit = rules.match_pattern(last["description"].upper())
        guess = hit[2] if hit else ""
        needs = not guess or "unknown" in guess.lower() or (cat in rules.trace and not fixed)
        found.append(dict(
            merchant=key, group=group, category=cat, kind=kind, cadence=name or "irregular", count=len(rs),
            last_amount=f"{-last['amount']:.2f}", median_amount=f"{med:.2f}",
            monthly_equivalent=f"{med * 30.4 / days:.2f}" if days else "", first_seen=rs[0]["date"].isoformat(),
            last_seen=last["date"].isoformat(), paying_account=last["account"],
            all_accounts="; ".join(sorted({r["account"] for r in rs})), status=status,
            what_for_guess=guess or "not known from the description", still_used="",
            trace_needed="yes" if needs else "",
            trace_where=rules.trace.get(cat, rules.trace.get("other", "")) if needs else "",
            last_source=last["source"]))
    return found


# ------------------------------------------------------------------ your answers
def same_merchant(a, b):
    ta, tb = a.split(), b.split()
    n = min(len(ta), len(tb))
    return n > 0 and ta[:n] == tb[:n]


def carry_forward(found, out_path):
    if not Path(out_path).exists():
        return found, 0, 0
    with open(out_path, encoding="utf-8", newline="") as fh:
        prev = list(csv.DictReader(fh))
    answers = {r["merchant"]: r["still_used"] for r in prev if r.get("still_used")}
    added = [r for r in prev if r.get("kind") == ADDED]
    for f in found:
        f["still_used"] = answers.get(f["merchant"], "")
    for a in added:
        match = [f for f in found if same_merchant(f["merchant"], a["merchant"])]
        for f in match:
            f["still_used"] = f["still_used"] or a.get("still_used", "")
        if not match:
            found.append({c: a.get(c, "") for c in COLUMNS})
    return found, len(answers), len(added)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("inputs", nargs="+", help="CSV exports, or folders holding them")
    ap.add_argument("--out", required=True, help="the subscriptions.csv to write")
    ap.add_argument("--since", default=None, help="ignore charges before this date (YYYY-MM-DD)")
    ap.add_argument("--rules", default=str(CATEGORIES))
    args = ap.parse_args(argv)

    files = []
    for item in args.inputs:
        p = Path(item)
        if p.is_dir():
            files += sorted(q for q in p.rglob("*") if q.suffix.lower() == ".csv"
                            and q.resolve() != Path(args.out).resolve())
        elif p.is_file():
            files.append(p)
        else:
            print(f"subscriptions: not found: {item}")
            return 2
    if not files:
        print("subscriptions: no csv files found")
        return 2
    rules = Rules(args.rules)
    rows, bad = [], 0
    for f in files:
        res, got = read_file(f, rules)
        ok = res["format"] and not res["note"]
        status = "MATCH" if ok else ("REFUSED" if res["format"] is None else "MISMATCH")
        bad += status != "MATCH"
        print(f"{status}  {res['file']}  format={res['format']}  rows_in_file={res['in_file']}  "
              f"rows_read={res['read']}  rows_used={res['written']}" + (f"  note: {res['note']}" if res["note"] else ""))
        for n, why in res["refused"][:10]:
            print(f"    row {n} refused: {why}")
        rows += got
    if not rows:
        print("subscriptions: no transaction rows read")
        return 2
    since = date.fromisoformat(args.since) if args.since else min(r["date"] for r in rows)
    found = find_recurring(rows, since, rules)
    found, answers, added = carry_forward(found, args.out)
    order = {"active": 0, "ended": 1}
    found.sort(key=lambda r: (order.get(r["status"], 2), r["group"], r["merchant"]))
    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(found)

    active = [f for f in found if f["status"] == "active"]
    monthly = sum(float(f["monthly_equivalent"] or 0) for f in active)
    p2p = sum(r["flow"] == "person-to-person" for r in rows)
    print(f"subscriptions: {len(files)} files, {len(rows)} rows, window from {since.isoformat()}")
    print(f"subscriptions: {len(found)} recurring charges, {len(active)} active, about {monthly:.2f} a month")
    print("subscriptions: active by group: "
          + ", ".join(f"{k} {v}" for k, v in sorted(Counter(f["group"] for f in active).items())))
    print(f"subscriptions: {sum(f['trace_needed'] == 'yes' for f in found)} need the product named from the "
          f"seller's own record; {p2p} person-to-person rows left out")
    print(f"subscriptions: {answers} still_used answers and {added} added rows carried forward; "
          f"active rows still blank: {sum(not f['still_used'] for f in active)}")
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print(f"subscriptions: failed ({exc!r}). Nothing here should be trusted.")
        sys.exit(2)
