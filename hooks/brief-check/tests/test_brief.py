"""Run: python tests/test_brief.py. Uses made-up briefs in a throwaway folder."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "brief_check.py")
FULL = "Goal: one table. Read: notes.md. Required: three columns. Done means filled. Output: table.md."


class Brief(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.makedirs(os.path.join(self.tmp.name, ".claude", "agents"))
        with open(os.path.join(self.tmp.name, ".claude", "agents", "reader.md"), "w", encoding="utf-8") as fh:
            fh.write("---\nname: reader\n---\n")

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, **tool_input):
        mode = tool_input.pop("mode", "warn")
        env = dict(os.environ, CLAUDE_TOOLS_LOG_DIR=self.tmp.name, CLAUDE_CONFIG_DIR=self.tmp.name, BRIEF_CHECK_MODE=mode)
        event = {"cwd": self.tmp.name, "tool_input": tool_input}
        done = subprocess.run([sys.executable, SCRIPT], input=json.dumps(event), capture_output=True, text=True, env=env)
        self.assertEqual(done.returncode, 0)
        return done.stdout

    def test_complete(self):
        self.assertEqual(self.check(prompt=FULL), "")

    def test_warns_and_names_the_gap(self):
        out = self.check(prompt="Goal: find things.", subagent_type="general-purpose")
        self.assertIn("went ahead", out)
        self.assertIn("Required", out)
        self.assertNotIn("Goal,", out)

    def test_block(self):
        self.assertIn('"deny"', self.check(prompt="do it", mode="block"))

    def test_off(self):
        self.assertEqual(self.check(prompt="do it", mode="off"), "")

    def test_named_agent(self):
        self.assertEqual(self.check(prompt="do it", subagent_type="reader"), "")

    def test_built_in(self):
        self.assertEqual(self.check(prompt="do it", subagent_type="Explore"), "")

    def test_ready_does_not_count_as_read(self):
        self.assertIn("Read", self.check(prompt="Goal Required Done Output ready"))


if __name__ == "__main__":
    unittest.main()
