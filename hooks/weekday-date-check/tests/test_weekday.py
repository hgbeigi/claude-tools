"""Run: python tests/test_weekday.py."""
import datetime
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, HERE)
import weekday_check as w  # noqa: E402

TODAY = datetime.date(2026, 11, 5)  # a Thursday


def bad(text, **options):
    return [row[2] for row in w.check_text(text, today=TODAY, **options)]


class Weekday(unittest.TestCase):
    def test_right_pairs_pass(self):
        for text in ("Wednesday 18 November", "Thu, Nov 5, 2026", "Monday 2026-11-02", "Thursday, November 5",
                     "the 5th of November, Thursday", "Fri 11/20", "11/18 (Wed)", "Friday 11/20/26",
                     "Sat Sept 5, 2026", "Thurs. Nov. 5", "Tues Nov 10"):
            self.assertEqual(bad(text), [], text)

    def test_wrong_pairs_are_flagged(self):
        for text, day in (("Monday, November 18", "Wednesday"), ("Wed 5 Nov 2026", "Thursday"),
                          ("Tuesday 2026-11-02", "Monday"), ("Nov 5 (Fri)", "Thursday"), ("Monday 11/20", "Friday")):
            found = bad(text)
            self.assertEqual(len(found), 1, text)
            self.assertIn(day, found[0])

    def test_year_is_stated_when_assumed(self):
        self.assertIn("2026", bad("Monday, November 18")[0])

    def test_nearest_year_crosses_new_year(self):
        self.assertEqual(bad("Tuesday, January 5"), [])  # 5 January 2027

    def test_given_year(self):
        self.assertEqual(bad("Friday, November 19", year=2027), [])

    def test_day_first(self):
        self.assertEqual(bad("Friday 3/4", day_first=True, year=2026), [])
        self.assertTrue(bad("Friday 3/4", year=2026))

    def test_impossible_date(self):
        self.assertEqual(bad("Monday, February 30"), ["this date does not exist"])

    def test_ordinary_words_are_left_alone(self):
        for text in ("Sun 5 hours", "The sat 12 people", "Monday we meet", "mon 3 marketing ideas", "version 11/20.1"):
            self.assertEqual(bad(text), [], text)

    def test_line_numbers(self):
        rows = w.check_text("fine\nMonday, November 18\n", today=TODAY)
        self.assertEqual(rows[0][0], 2)

    def hook(self, **tool_input):
        done = subprocess.run([sys.executable, os.path.join(HERE, "weekday_check.py"), "--claude-hook"],
                              input=json.dumps({"tool_input": tool_input}), capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        return done.stdout

    def test_hook_on_write_and_edit(self):
        self.assertIn("additionalContext", self.hook(file_path="a.md", content="Monday 2026-11-03"))
        self.assertIn("additionalContext", self.hook(file_path="a.md", new_string="Monday 2026-11-03"))
        self.assertIn("additionalContext", self.hook(file_path="a.md", edits=[{"new_string": "Monday 2026-11-03"}]))

    def test_hook_skips_other_files_and_clean_text(self):
        self.assertEqual(self.hook(file_path="a.py", content="Monday 2026-11-03"), "")
        self.assertEqual(self.hook(file_path="a.md", content="Tuesday 2026-11-03"), "")


if __name__ == "__main__":
    unittest.main()
