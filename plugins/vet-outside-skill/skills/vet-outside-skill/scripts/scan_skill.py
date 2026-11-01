"""Scan an outside skill, plugin or tool folder for risky patterns before adoption.

Part of the vet-outside-skill skill. It reads every text file in the folder
and lists each line that matches a risk pattern, by file and line number. It
never runs anything from the folder and never fetches. A clean result means
only that these patterns were not found; the line-by-line read still
happens.

Run:   python -I scan_skill.py <folder>
       python -I scan_skill.py <folder> --json

Exit 0 when nothing high was found, 1 when a high pattern was found, 2 when
the folder cannot be read. Standard library only.
"""
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TEXT_EXT = {".md", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh", ".bash", ".zsh", ".ps1",
            ".psm1", ".psd1", ".bat", ".cmd", ".vbs", ".json", ".yaml", ".yml", ".toml", ".txt", ".html",
            ".htm", ".rb", ".go", ".rs", ".ini", ".cfg", ".php", ".pl", ".lua", ".java", ".kt", ".c",
            ".h", ".cpp", ".cs", ".swift", ".ipynb", ".sql", ".r", ".xml", ".env", ""}
BINARY_EXT = {".exe", ".dll", ".so", ".dylib", ".bin", ".pyc", ".jar", ".wasm", ".zip", ".tar", ".gz", ".7z"}

# (level, name, pattern). High: can move data or run code from elsewhere.
RULES = [
    ("high", "network call", r"\b(curl|wget|Invoke-WebRequest|iwr|requests\.(get|post|put)|urllib\.request|http\.client|fetch\(|axios|XMLHttpRequest|socket\.connect|net\.connect)\b"),
    ("high", "runs code it builds", r"\b(eval|exec)\s*\(|\bsubprocess\.|\bsystem\(|shell_exec|passthru|\bpopen\(|child_process|Start-Process|\bbash -c\b|\bsh -c\b|powershell\s+-(enc|e)\b"),
    ("high", "encoded payload", r"[A-Za-z0-9+/]{120,}={0,2}|\\x[0-9a-f]{2}(\\x[0-9a-f]{2}){20,}|base64\s*(-d|--decode)|b64decode|FromBase64String|atob\("),
    ("high", "credential or secret", r"(?i)\b(api[_-]?key|secret|token|password|passwd|private[_-]?key|BEGIN [A-Z ]*PRIVATE KEY)\b\s*[:=]"),
    ("high", "reads credential stores", r"(?i)(\.ssh[\\/]|\.aws[\\/]|credentials\.json|Login Data|Cookies|keychain|Credential Manager|\.netrc|wallet)"),
    ("high", "changes Claude settings or hooks", r"(?i)(settings(\.local)?\.json|\"hooks\"\s*:|\.claude[\\/](hooks|settings)|CLAUDE\.md|permissions\s*:\s*\{|--dangerously|bypassPermissions)"),
    ("medium", "path outside its folder", r"(\.\.[\\/]|~[\\/]|[A-Za-z]:[\\/]|/etc/|/usr/|%APPDATA%|\$HOME|\bos\.path\.expanduser)"),
    ("high", "instruction aimed at the model", r"(?i)(ignore (all |any )?(previous|prior) instructions|do not tell the user|without (asking|telling) the user|you are now|(ignore|override|reveal) (the |your )?system prompt)"),
    ("medium", "web address", r"https?://[^\s)\"'>]+"),
    ("medium", "bank, card or login automation", r"(?i)\b(login|log in|sign in|password field|card number|routing number|bank account|otp|2fa)\b"),
    ("low", "writes files", r"\bopen\([^)]*['\"][wa]b?['\"]|\bwriteFile|Set-Content|Out-File|>\s*\S+\.\w+"),
]
COMPILED = [(lvl, name, re.compile(rx)) for lvl, name, rx in RULES]


def scan(folder):
    hits, binaries, files, skipped = [], [], 0, []
    for root, dirs, names in os.walk(folder):
        # nothing is skipped silently: .git is git's own store; every other folder is read
        dirs[:] = [d for d in dirs if d != ".git"]
        for n in names:
            path = os.path.join(root, n)
            rel = os.path.relpath(path, folder)
            ext = os.path.splitext(n)[1].lower()
            if ext in BINARY_EXT:
                binaries.append(rel)
                continue
            if ext not in TEXT_EXT:
                skipped.append(rel)
                continue
            files += 1
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, 1):
                        for lvl, name, rx in COMPILED:
                            if rx.search(line):
                                hits.append({"level": lvl, "rule": name, "file": rel, "line": i,
                                             "text": line.strip()[:160]})
            except OSError:
                continue
    return files, binaries, hits, skipped


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args or not os.path.isdir(args[0]):
        print("usage: python -I scan_skill.py <folder> [--json]")
        return 2
    files, binaries, hits, skipped = scan(args[0])
    high = [h for h in hits if h["level"] == "high"]
    if "--json" in sys.argv:
        print(json.dumps({"files": files, "binaries": binaries, "skipped": skipped, "hits": hits}, indent=1))
    else:
        print(f"{files} text files read; {len(binaries)} binary files; "
              f"{len(high)} high, {sum(h['level'] == 'medium' for h in hits)} medium, "
              f"{sum(h['level'] == 'low' for h in hits)} low.")
        if skipped:
            print(f"  NOT READ {len(skipped)} files of an unknown type: " + ", ".join(skipped[:20])
                  + (" ..." if len(skipped) > 20 else "") + "  (read each by hand)")
        for b in binaries:
            print(f"  BINARY   {b}  (cannot be read; reject unless its source is in the folder)")
        for lvl in ("high", "medium", "low"):
            for h in hits:
                if h["level"] == lvl:
                    print(f"  {lvl.upper():<7}  {h['rule']}  {h['file']}:{h['line']}  {h['text']}")
    return 1 if high or binaries else 0


if __name__ == "__main__":
    sys.exit(main())
