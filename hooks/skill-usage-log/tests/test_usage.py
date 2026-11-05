"""Run: python tests/test_usage.py. Uses made-up events in a throwaway folder."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
LOGGER = os.path.join(HERE, "..", "scripts", "usage_log.py")
REPORT = os.path.join(HERE, "..", "scripts", "usage_report.py")


class Usage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = os.path.join(self.tmp.name, ".claude")
        os.makedirs(os.path.join(base, "agents"))
        for skill in ("used-skill", "silent-skill"):
            os.makedirs(os.path.join(base, "skills", skill))
            with open(os.path.join(base, "skills", skill, "SKILL.md"), "w", encoding="utf-8") as fh:
                fh.write("---\nname: x\n---\n")
        with open(os.path.join(base, "agents", "reader.md"), "w", encoding="utf-8") as fh:
            fh.write("---\nname: reader\nskills:\n  - loaded-skill\n---\nBody\n")
        self.env = dict(os.environ, CLAUDE_TOOLS_LOG_DIR=self.tmp.name, CLAUDE_CONFIG_DIR=base)

    def tearDown(self):
        self.tmp.cleanup()

    def send(self, **event):
        event["cwd"] = self.tmp.name
        done = subprocess.run([sys.executable, LOGGER], input=json.dumps(event), capture_output=True,
                              text=True, env=self.env)
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def rows(self):
        with open(os.path.join(self.tmp.name, "skill-usage.jsonl"), encoding="utf-8") as fh:
            return [json.loads(line) for line in fh]

    def test_direct_and_through_agent(self):
        self.send(hook_event_name="PreToolUse", tool_name="Skill", tool_input={"skill": "used-skill"})
        self.send(hook_event_name="SubagentStart", agent_type="reader")
        self.send(hook_event_name="SubagentStart", agent_type="Explore")
        rows = self.rows()
        self.assertEqual(rows[0]["skill"], "used-skill")
        self.assertEqual(rows[1]["skills"], ["loaded-skill"])
        self.assertFalse(rows[2]["named_agent"])

    def test_other_tools_are_not_logged(self):
        self.send(hook_event_name="PreToolUse", tool_name="Read", tool_input={"file_path": "secret.txt"})
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "skill-usage.jsonl")))

    def test_report(self):
        self.send(hook_event_name="PreToolUse", tool_name="Skill", tool_input={"skill": "used-skill"})
        self.send(hook_event_name="SubagentStart", agent_type="reader")
        out = subprocess.run([sys.executable, os.path.abspath(REPORT)], cwd=self.tmp.name, capture_output=True,
                             text=True, env=self.env).stdout
        self.assertIn("used-skill: 1, 0", out)
        self.assertIn("loaded-skill: 0, 1", out)
        self.assertIn("never ran in this window: 1", out)
        self.assertIn("  silent-skill", out)

    def test_broken_input_never_fails(self):
        done = subprocess.run([sys.executable, LOGGER], input="not json", capture_output=True, text=True, env=self.env)
        self.assertEqual((done.returncode, done.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
