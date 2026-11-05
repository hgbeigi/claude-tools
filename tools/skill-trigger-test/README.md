# Skill trigger test

A Claude Code skill and script. Claude picks a skill by matching your request against its description, so a description in words you never say is a skill that does not start. When I tested my own setup, the right skill matched 3 of 20 real requests. After a rewrite in my own words, it matched 20 of 20.

It gives two measures: a score against requests you save in a file, and a count of how often you really typed each quoted phrase, read from your transcripts on this computer.

## Run it

```
python trigger_test.py --skills .claude/skills --requests requests.json
python trigger_test.py --skills .claude/skills --transcripts --days 90
```

## Limits

This is a stand-in, not the real picker. It reads only phrases in quotation marks, while Claude reads the whole description, so a skill can load without a match. Use it to compare before and after a rewrite. Write the requests in your own words, or the score proves nothing. The transcript measure reads your own sessions on this computer, and prints only counts.

## Try it

1. Run the skill trigger test on `examples/skills` with `examples/requests.json`.
2. My skills never load. Test my skill descriptions.
3. Which phrases in my skill descriptions have I never typed?

## Sample data

`examples/` holds three made-up skills and four requests. Expected result: 2 of 4 pick the right skill, and `travel-plan` is named as having no quoted phrases.

## Install

```
/plugin marketplace add hgbeigi/claude-tools
/plugin install skill-trigger-test@hgbeigi-tools
```

Privacy: nothing is collected or sent anywhere. See [PRIVACY.md](../../PRIVACY.md).
