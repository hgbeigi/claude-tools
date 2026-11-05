"""Run: python tests/test_trigger.py. Uses the made-up sample skills and a made-up transcript."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCRIPT = os.path.join(ROOT, "skills", "skill-trigger-test", "scripts", "trigger_test.py")
SKILLS = os.path.join(ROOT, "examples", "skills")
sys.path.insert(0, os.path.dirname(SCRIPT))
import trigger_test as t  # noqa: E402


class Trigger(unittest.TestCase):
    def test_sample_score(self):
        out = subprocess.run([sys.executable, SCRIPT, "--skills", SKILLS, "--requests",
                              os.path.join(ROOT, "examples", "requests.json")],
                             capture_output=True, text=True).stdout
        self.assertIn("2 of 4 pick the right skill", out)
        self.assertIn("No quoted phrases in the description of: travel-plan", out)

    def test_tie_is_a_miss(self):
        chosen, _ = t.pick("alpha", {"one": ["alpha"], "two": ["alpha"]})
        self.assertIsNone(chosen)

    def test_whole_words_only(self):
        self.assertEqual(t.pick("alphabet", {"one": ["alpha"]}), (None, {}))

    def test_hidden_skill_is_left_out(self):
        with tempfile.TemporaryDirectory() as folder:
            os.mkdir(os.path.join(folder, "quiet"))
            with open(os.path.join(folder, "quiet", "SKILL.md"), "w", encoding="utf-8") as fh:
                fh.write('---\nname: quiet\ndescription: Use for "hello there".\ndisable-model-invocation: true\n---\n')
            self.assertEqual(t.read_skills(folder, skip_hidden=True), {})
            self.assertEqual(t.read_skills(folder), {"quiet": ["hello there"]})

    def test_transcripts_count_only_what_you_typed(self):
        with tempfile.TemporaryDirectory() as home:
            os.makedirs(os.path.join(home, "projects", "p"))
            rows = [
                {"type": "user", "timestamp": "2099-01-01T00:00:00Z", "message": {"content": "please add up the bills"}},
                {"type": "user", "timestamp": "2099-01-01T00:00:00Z", "isMeta": True, "message": {"content": "add up the bills"}},
                {"type": "user", "timestamp": "2099-01-01T00:00:00Z",
                 "message": {"content": [{"type": "tool_result", "content": "add up the bills"}]}},
                {"type": "assistant", "timestamp": "2099-01-01T00:00:00Z", "message": {"content": "add up the bills"}},
            ]
            with open(os.path.join(home, "projects", "p", "s.jsonl"), "w", encoding="utf-8") as fh:
                fh.writelines(json.dumps(r) + "\n" for r in rows)
            target = os.path.join(home, "out.csv")
            out = subprocess.run([sys.executable, SCRIPT, "--skills", SKILLS, "--transcripts", "--csv", target],
                                 capture_output=True, text=True, env=dict(os.environ, CLAUDE_CONFIG_DIR=home)).stdout
            self.assertIn("1 of your messages", out)
            self.assertIn('"add up the bills" 1', out)
            self.assertIn("meeting-notes: 0 of 2 phrases used   NONE USED", out)
            self.assertTrue(os.path.exists(target))


if __name__ == "__main__":
    unittest.main()
