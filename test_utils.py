# test_utils.py

import unittest
import utils


class TestUtils(unittest.TestCase):

    def test_calc_issue_resolution_time(self):
        issues = [
            {"created_at": "2024-01-01T00:00:00Z", "closed_at": "2024-01-05T00:00:00Z"},
            {"created_at": "2024-01-10T00:00:00Z", "closed_at": "2024-01-15T00:00:00Z"}
        ]
        avg = utils.calc_issue_resolution_time(issues)
        self.assertEqual(avg, 4.5)

    def test_calc_pr_merge_ratio(self):
        prs = [
            {"merged_at": "2024-01-01T00:00:00Z"},
            {"merged_at": None},
            {"merged_at": "2024-01-02T00:00:00Z"}
        ]
        ratio = utils.calc_pr_merge_ratio(prs)
        self.assertEqual(ratio, 66.67)

    def test_count_releases_per_month(self):
        releases = [
            {"created_at": "2024-01-15T00:00:00Z"},
            {"created_at": "2024-01-20T00:00:00Z"},
            {"created_at": "2024-02-01T00:00:00Z"}
        ]
        count = utils.count_releases_per_month(releases)
        self.assertEqual(count["2024-01"], 2)
        self.assertEqual(count["2024-02"], 1)

    def test_summarize_languages(self):
        langs = {"Python": 5000, "C++": 3000}
        result = utils.summarize_languages(langs)
        self.assertEqual(result[0]["language"], "Python")
        self.assertAlmostEqual(result[0]["percent"], 62.5)


if __name__ == "__main__":
    unittest.main()
