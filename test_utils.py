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

    # ── calculate_bus_factor ──────────────────────────────────────────────────

    def test_bus_factor_normal(self):
        """Two balanced contributors: neither should be critical."""
        contributors = [
            {"login": "alice", "contributions": 60},
            {"login": "bob",   "contributions": 40},
        ]
        result = utils.calculate_bus_factor(contributors)
        self.assertIsNotNone(result)
        self.assertEqual(result["top1_login"], "alice")
        self.assertAlmostEqual(result["top1_pct"], 60.0)
        self.assertAlmostEqual(result["top2_pct"], 100.0)
        self.assertFalse(result["is_critical"])

    def test_bus_factor_critical(self):
        """One dominant contributor (> 75%) triggers is_critical."""
        contributors = [
            {"login": "solo",   "contributions": 900},
            {"login": "helper", "contributions": 100},
        ]
        result = utils.calculate_bus_factor(contributors)
        self.assertIsNotNone(result)
        self.assertEqual(result["top1_login"], "solo")
        self.assertAlmostEqual(result["top1_pct"], 90.0)
        self.assertAlmostEqual(result["top2_pct"], 100.0)
        self.assertTrue(result["is_critical"])

    def test_bus_factor_exactly_at_threshold(self):
        """Exactly 75% should NOT be critical (boundary is > 75, not >= 75)."""
        contributors = [
            {"login": "dev1", "contributions": 75},
            {"login": "dev2", "contributions": 25},
        ]
        result = utils.calculate_bus_factor(contributors)
        self.assertFalse(result["is_critical"])

    def test_bus_factor_single_contributor(self):
        """A solo contributor should be critical (100% ownership)."""
        contributors = [{"login": "lone_wolf", "contributions": 200}]
        result = utils.calculate_bus_factor(contributors)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["top1_pct"], 100.0)
        self.assertAlmostEqual(result["top2_pct"], 100.0)
        self.assertTrue(result["is_critical"])

    def test_bus_factor_empty_contributors(self):
        """Empty list should return None gracefully."""
        self.assertIsNone(utils.calculate_bus_factor([]))

    def test_bus_factor_none_contributors(self):
        """None input should return None gracefully."""
        self.assertIsNone(utils.calculate_bus_factor(None))

    def test_bus_factor_zero_contributions(self):
        """All-zero contributions should return None (avoid division by zero)."""
        contributors = [
            {"login": "ghost1", "contributions": 0},
            {"login": "ghost2", "contributions": 0},
        ]
        self.assertIsNone(utils.calculate_bus_factor(contributors))

    def test_bus_factor_top2_pct_with_one_contributor(self):
        """When there is only one contributor, top2_pct should equal top1_pct."""
        contributors = [{"login": "only_one", "contributions": 50}]
        result = utils.calculate_bus_factor(contributors)
        self.assertEqual(result["top1_pct"], result["top2_pct"])

    def test_bus_factor_ordering(self):
        """Unsorted input: top1 must always be the highest contributor."""
        contributors = [
            {"login": "junior", "contributions": 10},
            {"login": "senior", "contributions": 500},
            {"login": "mid",    "contributions": 200},
        ]
        result = utils.calculate_bus_factor(contributors)
        self.assertEqual(result["top1_login"], "senior")
        total = 710
        self.assertAlmostEqual(result["top1_pct"], round(500 / total * 100, 2))
        self.assertAlmostEqual(result["top2_pct"], round(700 / total * 100, 2))


if __name__ == "__main__":
    unittest.main()1