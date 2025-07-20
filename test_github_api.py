import unittest
from unittest.mock import patch
import github_api


class TestGitHubAPI(unittest.TestCase):

    @patch("github_api.requests.get")
    def test_get_repo_stats(self, mock_get):
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            "stargazers_count": 100,
            "forks_count": 10,
            "open_issues_count": 5
        }
        result = github_api.get_repo_stats("test/test")
        self.assertEqual(result["stars"], 100)
        self.assertEqual(result["forks"], 10)
        self.assertEqual(result["open_issues"], 5)

    @patch("github_api.requests.get")
    def test_get_contributors(self, mock_get):
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = [{"login": "user1", "contributions": 42}]
        result = github_api.get_contributors("test/test")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["login"], "user1")

    @patch("github_api.requests.get")
    def test_get_languages(self, mock_get):
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {"Python": 5000, "C++": 3000}
        result = github_api.get_languages("test/test")
        self.assertIn("Python", result)
        self.assertEqual(result["C++"], 3000)

    @patch("github_api.requests.get")
    def test_get_commit_activity(self, mock_get):
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = [{"total": 5, "week": 12345678}]
        result = github_api.get_commit_activity("test/test")
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["total"], 5)


if __name__ == "__main__":
    unittest.main()
