# Commit privacy guard

A Claude Code hook and a git hook that refuse a commit holding money files or private details, because a version history does not forget. It reads only the staged copy of each file and sends nothing anywhere.

## What it refuses

- A new spreadsheet, CSV, PDF, image, ZIP or mail export.
- A line that looks like a card, account or routing number, or a US social security number.
- Five or more nearby lines that each hold a date, an amount and a description, which is a transaction ledger.
- Any word in your private name list, if you make one: one pattern per line in `commit-guard-names.txt` in your home Claude folder, outside the repository. Set `COMMIT_GUARD_NAMES` to use another file.

Messages give the rule and the line number and never print the matched text.

## Two layers

The plugin checks each `git commit` that Claude runs. For commits you run yourself, also add the git hook once in each repository:

```
python commit_guard.py --install
```

It refuses to replace a `pre-commit` file that already exists. Use `--all` to look over every tracked file first.

## When it is wrong

- Add `guard-ok` to a line that is safe, such as a long order number.
- List safe files in `.commit-guard-allow` in the repository root, one pattern per line, such as `docs/*.png`.

## Limits

Each pattern is a guess: it can miss a number in an unusual shape, and it can refuse a safe one. A git hook can be skipped with `--no-verify`. The Claude Code layer sees only what is already staged, so it asks Claude to run `git add` and `git commit` as two commands. It does not clean what is already in your history. It is not legal or security advice.

## Try it

1. Install the commit guard in this repository, then show me what `--all` finds.
2. Commit this folder, and tell me if the guard refuses anything.
3. Why did the guard refuse my commit?

## Sample data

`tests/test_guard.py` builds a throwaway repository with made-up files and shows each rule firing.

## Install

```
/plugin marketplace add hgbeigi/claude-tools
/plugin install commit-privacy-guard@hgbeigi-tools
```

Privacy: nothing is collected or sent anywhere. See [PRIVACY.md](../../PRIVACY.md).
