import requests
from datetime import datetime

BASE_URL = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    # Optional: add your token for higher rate limits
    # "Authorization": "Bearer YOUR_PERSONAL_ACCESS_TOKEN"
}


def get_repo_stats(repo):
    """Returns stars, forks, open issues."""
    url = f"{BASE_URL}/repos/{repo}"
    res = requests.get(url, headers=HEADERS)
    if res.ok:
        data = res.json()
        return {
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "open_issues": data["open_issues_count"],
        }
    return None


def get_contributors(repo):
    """Returns top contributors with commit count."""
    url = f"{BASE_URL}/repos/{repo}/contributors"
    res = requests.get(url, headers=HEADERS)
    return res.json() if res.ok else None


def get_commit_activity(repo):
    """Returns weekly commit activity (last 52 weeks)."""
    url = f"{BASE_URL}/repos/{repo}/stats/commit_activity"
    res = requests.get(url, headers=HEADERS)
    return res.json() if res.ok else None


def get_issues(repo, state="all", per_page=100, max_pages=2):
    """Returns issues (open or closed). Use max_pages to limit calls."""
    issues = []
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/repos/{repo}/issues"
        params = {"state": state, "per_page": per_page, "page": page}
        res = requests.get(url, headers=HEADERS, params=params)
        if res.ok:
            issues += res.json()
        else:
            break
    return issues


def get_pull_requests(repo, state="all", per_page=100, max_pages=2):
    """Returns PRs and metadata."""
    prs = []
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/repos/{repo}/pulls"
        params = {"state": state, "per_page": per_page, "page": page}
        res = requests.get(url, headers=HEADERS, params=params)
        if res.ok:
            prs += res.json()
        else:
            break
    return prs


def get_releases(repo):
    """Returns list of releases with dates."""
    url = f"{BASE_URL}/repos/{repo}/releases"
    res = requests.get(url, headers=HEADERS)
    return res.json() if res.ok else None


def get_languages(repo):
    """Returns dictionary of languages used and bytes of code."""
    url = f"{BASE_URL}/repos/{repo}/languages"
    res = requests.get(url, headers=HEADERS)
    return res.json() if res.ok else None
