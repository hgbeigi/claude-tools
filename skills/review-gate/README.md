# Review gate

A read-only second check before work is called done. A separate reviewer agent, which cannot edit, blocks only on a closed list of five problems and keeps everything else as advice.

## Try it

1. Review this plan before I start: `plan.md`.
2. Is it ready? Check the report in `out/summary.md` against what I asked for.
3. Pre-mortem: what could go wrong with the migration steps above?

## Sample data

No sample data needed: point it at any plan or document.

## Install

```
/plugin marketplace add hgbeigi/claude-tools
/plugin install review-gate@hgbeigi-tools
```

Privacy: nothing is collected or sent anywhere. See [PRIVACY.md](../../PRIVACY.md).
