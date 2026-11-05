"""Run: python tests/test_reminder.py. Builds throwaway repositories with made-up commits."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "unpushed_reminder.py")
IDENTITY = ["-c", "user.name=t", "-c", "user.email=t@example.com"]


class Reminder(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.origin = os.path.join(self.tmp.name, "origin.git")
        self.repo = os.path.join(self.tmp.name, "work")
        subprocess.run(["git", "init", "-q", "--bare", self.origin], check=True)
        subprocess.run(["git", "clone", "-q", self.origin, self.repo], check=True, capture_output=True)
        self.commit(time.time() - 7200)
        subprocess.run(["git", "push", "-q", "-u", "origin", "HEAD"], cwd=self.repo, check=True, capture_output=True)

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, when):
        env = dict(os.environ, GIT_COMMITTER_DATE=f"{int(when)} +0000", GIT_AUTHOR_DATE=f"{int(when)} +0000")
        subprocess.run(["git"] + IDENTITY + ["commit", "-q", "--allow-empty", "-m", "x"], cwd=self.repo, check=True, env=env)

    def hook(self, **env):
        full = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        full.update(env)
        done = subprocess.run([sys.executable, SCRIPT], input=json.dumps({"cwd": self.repo}),
                              capture_output=True, text=True, env=full)
        self.assertEqual(done.returncode, 0)
        return done.stdout

    def test_quiet_when_pushed(self):
        self.assertEqual(self.hook(), "")

    def test_quiet_for_a_fresh_commit(self):
        self.commit(time.time())
        self.assertEqual(self.hook(), "")

    def test_speaks_once_for_an_old_commit(self):
        self.commit(time.time() - 3000)
        self.commit(time.time())
        self.assertIn("2 commit(s)", self.hook())
        self.assertEqual(self.hook(), "")

    def test_settings(self):
        self.commit(time.time() - 120)
        self.assertEqual(self.hook(), "")
        self.assertIn("1 commit(s)", self.hook(UNPUSHED_WAIT_MINUTES="1"))

    def test_no_upstream(self):
        subprocess.run(["git", "checkout", "-q", "-b", "side"], cwd=self.repo, check=True)
        self.commit(time.time() - 3000)
        self.assertEqual(self.hook(), "")

    def test_outside_a_repository(self):
        done = subprocess.run([sys.executable, SCRIPT], input=json.dumps({"cwd": self.tmp.name}),
                              capture_output=True, text=True)
        self.assertEqual((done.returncode, done.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
