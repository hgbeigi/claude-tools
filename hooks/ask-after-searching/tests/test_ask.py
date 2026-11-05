"""Run: python tests/test_ask.py. Uses made-up transcripts in a throwaway folder."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "ask_after_searching.py")


def you(text):
    return {"type": "user", "message": {"content": text}}


def tool(name, **tool_input):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": tool_input}]}}


class Ask(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.transcript = os.path.join(self.tmp.name, "t.jsonl")

    def tearDown(self):
        self.tmp.cleanup()

    def ask(self, question, rows=(), session="s1", **env):
        with open(self.transcript, "w", encoding="utf-8") as fh:
            fh.writelines(json.dumps(r) + "\n" for r in rows)
        event = {"session_id": session, "transcript_path": self.transcript,
                 "tool_input": {"questions": [{"question": question}]}}
        full = dict(os.environ, CLAUDE_TOOLS_LOG_DIR=self.tmp.name, **env)
        done = subprocess.run([sys.executable, SCRIPT], input=json.dumps(event),
                              capture_output=True, text=True, env=full)
        self.assertEqual(done.returncode, 0)
        return done.stdout

    def test_sent_back_once_then_through(self):
        self.assertIn('"deny"', self.ask("What is the dog's name?"))
        self.assertEqual(self.ask("What is the dog's name?"), "")

    def test_another_session_is_sent_back_again(self):
        self.ask("What is the dog's name?")
        self.assertIn('"deny"', self.ask("What is the dog's name?", session="s2"))

    def test_says_where_it_looked(self):
        self.assertEqual(self.ask("Searched notes/, not found. What is the dog's name?"), "")

    def test_decision(self):
        self.assertEqual(self.ask("Decision: blue or green?"), "")

    def test_searched_since_your_message(self):
        self.assertEqual(self.ask("Which one?", [you("hello"), tool("Grep", pattern="dog")]), "")

    def test_search_before_your_message_does_not_count(self):
        self.assertIn('"deny"', self.ask("Which one?", [tool("Grep", pattern="dog"), you("hello")]))

    def test_shell_search(self):
        self.assertEqual(self.ask("Which one?", [you("hi"), tool("Bash", command="grep -rn dog notes/")]), "")

    def test_paths_setting(self):
        rows = [you("hi"), tool("Grep", pattern="dog", path="src")]
        self.assertIn('"deny"', self.ask("Which one?", rows, ASK_AFTER_SEARCHING_PATHS="notes"))
        rows = [you("hi"), tool("Read", file_path="notes/pets.md")]
        self.assertEqual(self.ask("Which two?", rows, ASK_AFTER_SEARCHING_PATHS="notes"), "")

    def test_warn_and_off(self):
        self.assertIn("went ahead", self.ask("Which one?", ASK_AFTER_SEARCHING_MODE="warn"))
        self.assertEqual(self.ask("Which two?", ASK_AFTER_SEARCHING_MODE="off"), "")

    def test_log_never_holds_the_question(self):
        self.ask("What is the dog's name?")
        with open(os.path.join(self.tmp.name, "ask-after-searching.jsonl"), encoding="utf-8") as fh:
            self.assertNotIn("dog", fh.read())

    def test_broken_input_passes(self):
        full = dict(os.environ, CLAUDE_TOOLS_LOG_DIR=self.tmp.name)
        done = subprocess.run([sys.executable, SCRIPT], input="not json", capture_output=True, text=True, env=full)
        self.assertEqual((done.returncode, done.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
