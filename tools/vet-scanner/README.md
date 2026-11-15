# vet-scanner

The pattern scan used by the `vet-outside-skill` plugin, as a plain Python script for people who want to run it themselves. It reads every text file in a folder, lists each line that matches a risk pattern, and never runs or fetches anything from the folder.

```
python -I scan_skill.py <folder>
python -I scan_skill.py <folder> --json
```

Exit 0 when nothing high was found, 1 when a high pattern or a binary file was found, 2 when the folder cannot be read. Standard library only. A clean result means only that these patterns were absent. Read the files anyway.

It is not part of the plugin, because Claude's directory accepts scripts only from verified organizations. The plugin does the same scan with Claude's own search tool and `reference/patterns.md`.
