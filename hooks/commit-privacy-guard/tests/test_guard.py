"""Run: python tests/test_guard.py. Builds throwaway repositories with made-up data."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "commit_guard.py")
CARD = "4111 1111 " + "1111 1111"  # a published test number, split so this file passes its own guard
SSN = "123-45-" + "6789"  # an example that is never issued


def run(args, cwd, text=None, env=None):
    full = dict(os.environ, COMMIT_GUARD_NAMES=os.path.join(cwd, "..", "no-such-file"))
    full.update(env or {})
    return subprocess.run([sys.executable, os.path.abspath(SCRIPT)] + args, cwd=cwd, input=text,
                          capture_output=True, text=True, env=full)


class Guard(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.tmp.name, "r")
        os.mkdir(self.repo)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def stage(self, name, content):
        with open(os.path.join(self.repo, name), "w", encoding="utf-8") as fh:
            fh.write(content)
        subprocess.run(["git", "add", name], cwd=self.repo, check=True)

    def test_clean(self):
        self.stage("notes.md", "Lunch on Friday cost a little.\n")
        self.assertEqual(run([], self.repo).returncode, 0)

    def test_new_spreadsheet(self):
        self.stage("statement.csv", "a,b\n")
        done = run([], self.repo)
        self.assertEqual(done.returncode, 1)
        self.assertIn("[file type]", done.stdout)

    def test_allow_file(self):
        self.stage(".commit-guard-allow", "*.csv\n")
        self.stage("template.csv", "a,b\n")
        self.assertEqual(run([], self.repo).returncode, 0)

    def test_card_number_and_no_echo(self):
        self.stage("notes.md", "pay with " + CARD + "\n")
        done = run([], self.repo)
        self.assertEqual(done.returncode, 1)
        self.assertIn("[account number]", done.stdout)
        self.assertNotIn(CARD, done.stdout)

    def test_ssn(self):
        self.stage("notes.md", "id " + SSN + "\n")
        self.assertIn("[social security]", run([], self.repo).stdout)

    def test_line_marker(self):
        self.stage("notes.md", "order " + CARD + " guard-ok\n")
        self.assertEqual(run([], self.repo).returncode, 0)

    def test_ledger(self):
        rows = "".join(f"2026-01-0{i},COFFEE SHOP,-4.5{i}\n" for i in range(1, 7))
        self.stage("rows.txt", rows)
        self.assertIn("[ledger]", run([], self.repo).stdout)

    def test_four_rows_are_not_a_ledger(self):
        rows = "".join(f"2026-01-0{i},COFFEE SHOP,-4.5{i}\n" for i in range(1, 5))
        self.stage("rows.txt", rows)
        self.assertEqual(run([], self.repo).returncode, 0)

    def test_private_names(self):
        names = os.path.join(self.tmp.name, "names.txt")
        with open(names, "w", encoding="utf-8") as fh:
            fh.write("# comment\nzebrafield\n")
        self.stage("notes.md", "Dear Zebrafield family\n")
        done = run([], self.repo, env={"COMMIT_GUARD_NAMES": names})
        self.assertEqual(done.returncode, 1)
        self.assertNotIn("Zebrafield", done.stdout)

    def test_web_address_is_not_a_number(self):
        self.stage("notes.md", "see https://example.com/1234567890123456\n")
        self.assertEqual(run([], self.repo).returncode, 0)

    def test_claude_hook_refuses(self):
        self.stage("statement.csv", "a,b\n")
        event = json.dumps({"tool_input": {"command": "git commit -m x"}, "cwd": self.repo})
        out = json.loads(run(["--claude-hook"], self.repo, text=event).stdout)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_claude_hook_splits_add_and_commit(self):
        event = json.dumps({"tool_input": {"command": "git add . && git commit -m x"}, "cwd": self.repo})
        self.assertIn("separate command", run(["--claude-hook"], self.repo, text=event).stdout)

    def test_claude_hook_ignores_other_commands(self):
        event = json.dumps({"tool_input": {"command": "git status"}, "cwd": self.repo})
        self.assertEqual(run(["--claude-hook"], self.repo, text=event).stdout, "")

    def test_install_then_git_refuses(self):
        self.assertEqual(run(["--install"], self.repo).returncode, 0)
        self.assertEqual(run(["--install"], self.repo).returncode, 1)
        self.stage("statement.csv", "a,b\n")
        done = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-qm", "x"],
                              cwd=self.repo, capture_output=True, text=True)
        self.assertNotEqual(done.returncode, 0)


if __name__ == "__main__":
    unittest.main()
