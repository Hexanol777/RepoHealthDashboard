import requests
from datetime import datetime
import re
import time
import os
import streamlit as st


BASE_URL = "https://api.github.com"


HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {st.secrets['GITHUB_TOKEN']}"
}

def normalize_repo_input(user_input):
    user_input = user_input.strip()

    # Case 1: Full GitHub URL
    match = re.search(r"github\.com/([^/]+/[^/]+)", user_input)
    if match:
        return match.group(1)

    # Case 2: Already owner/repo
    if "/" in user_input:
        return user_input

    # Case 3: Single repo name -> search GitHub for most popular match
    search_url = f"https://api.github.com/search/repositories?q={user_input}&sort=stars&order=desc"
    res = requests.get(search_url, headers={"Accept": "application/vnd.github+json"})
    if res.ok and res.json()["items"]:
        return res.json()["items"][0]["full_name"]  # owner/repo

    return None  # No match found


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


def get_commit_activity(repo, retries=3, delay=2):
    """Returns weekly commit activity (last 52 weeks). Retries if GitHub returns 202."""
    url = f"{BASE_URL}/repos/{repo}/stats/commit_activity"
    for attempt in range(retries):
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 202:
            time.sleep(delay)  # Wait for GitHub to generate stats
            continue
        if res.ok:
            return res.json()
        break
    return None


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
