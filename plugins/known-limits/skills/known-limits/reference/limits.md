# Known limits register

Read this before saying "impossible". Each entry says what fails, when it was seen, the method tried, and the route that works. Copy the matching entry into any helper agent's brief that goes near it.

Add an entry only when a limit has been confirmed twice, and date it. If an entry is more than a month old and matters, test it once before trusting it.

The three entries below are examples of the shape. Keep one only if you have seen it yourself; delete the rest.

## Entry shape

```
## <what fails, in a few words>

Seen: YYYY-MM-DD, and YYYY-MM-DD.
Method tried: <the tool or step, and the message it gave>.
Route: <the way that works instead, or "none verified; ask before trying more">.
```

## Example: a Google Docs or Sheets file in a synced Drive folder reads as almost empty

Seen: (your dates).
Method tried: opening a `.gdoc` or `.gsheet` file from a synced Google Drive folder with the file tools. The file is a small pointer, not the document.
Route: read it through a Google Drive connector, or export it to Word, Excel or PDF first, or open it in the browser.

## Example: read-only helper agents cannot write files

Seen: (your dates).
Method tried: giving an Explore or Plan agent an output file. Both are read-only by design, so writing is refused.
Route: when the result is a file, use a general-purpose agent or a named agent that can write.

## Example: a run started from the command line stops at permission prompts

Seen: (your dates).
Method tried: running Claude Code without a person present (for example with `claude -p` or a scheduled task). Each step that needs approval stops the run, and folders outside the project cannot be read.
Route: pass the folders and tools the run needs on the command line (`--add-dir` for folders, `--allowedTools` for the exact commands), and have the run write its results to a file.

## Your entries

(none yet)
