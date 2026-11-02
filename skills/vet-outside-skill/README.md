# Vet an outside skill

Before you install someone else's skill, plugin, MCP server or script: a pattern scan that reads the files without running them, a checklist for the full read, and a written adopt, rebuild or reject verdict.

## Try it

1. Is this skill safe to install? https://github.com/hgbeigi/claude-tools/tree/main/skills/subscription-audit
2. I found this repo with Claude Code plugins. Vet it before I add the marketplace.
3. Check the MCP server in `./downloads/some-mcp` before I run it.

## Sample data

Try it on this repository itself. The scan flags a few MEDIUM and LOW lines: web addresses in the manifests, the audit script writing its output file, and rules that mention logins only to forbid them. The full read then shows each one is harmless. That is what a normal result looks like: the scan points at lines, and the reading decides.

## Install

```
/plugin marketplace add hgbeigi/claude-tools
/plugin install vet-outside-skill@hgbeigi-tools
```

Privacy: nothing is collected or sent anywhere. See [PRIVACY.md](../../PRIVACY.md).
