from datetime import datetime
import statistics


def calc_issue_resolution_time(issues):
    """Returns average issue resolution time in days."""
    durations = []
    for issue in issues:
        if issue.get("closed_at") and issue.get("created_at"):
            created = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
            closed = datetime.fromisoformat(issue["closed_at"].replace("Z", "+00:00"))
            delta = (closed - created).days
            durations.append(delta)
    if durations:
        return round(statistics.mean(durations), 2)
    return None


def calc_pr_merge_ratio(prs):
    """Returns % of PRs that were merged."""
    total = len(prs)
    merged = sum(1 for pr in prs if pr.get("merged_at"))
    if total == 0:
        return None
    return round(merged / total * 100, 2)


def count_releases_per_month(releases):
    """Returns a dictionary of release counts per YYYY-MM."""
    counts = {}
    for rel in releases:
        date = rel.get("created_at")
        if date:
            dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
            key = dt.strftime("%Y-%m")
            counts[key] = counts.get(key, 0) + 1
    return counts


def summarize_languages(lang_dict):
    """Returns sorted list of languages by usage percentage."""
    if not lang_dict:
        return []
    total = sum(lang_dict.values())
    return sorted(
        [{"language": lang, "percent": round((v / total) * 100, 2)}
         for lang, v in lang_dict.items()],
        key=lambda x: x["percent"],
        reverse=True
    )


def count_open_closed_issues(issues):
    """Count open vs closed issues."""
    open_count = sum(1 for i in issues if i.get("state") == "open")
    closed_count = sum(1 for i in issues if i.get("state") == "closed")
    return {"open": open_count, "closed": closed_count}


def summarize_commits_per_week(commit_data):
    """Summarize commits over time from commit_activity API."""
    if not commit_data:
        return []
    return [{"week": c["week"], "commits": c["total"]} for c in commit_data]


def top_contributors(contributors, top_n=8):
    """Return top N contributors sorted by contributions."""
    if not contributors:
        return []
    sorted_contribs = sorted(contributors, key=lambda x: x["contributions"], reverse=True)
    return sorted_contribs[:top_n]


def calculate_bus_factor(contributors):
    """
    Analyze contributor concentration risk (the 'bus factor').

    Returns a dict with:
        top1_login   - GitHub login of the #1 contributor
        top1_pct     - % of total commits by the top contributor
        top2_pct     - % of total commits by the top 2 contributors combined
        is_critical  - True when top1_pct > 75 (single point of failure)

    Returns None if the contributors list is empty or has zero total contributions.
    """
    if not contributors:
        return None

    total = sum(c.get("contributions", 0) for c in contributors)
    if total == 0:
        return None

    sorted_contribs = sorted(
        contributors, key=lambda x: x.get("contributions", 0), reverse=True
    )

    top1_contributions = sorted_contribs[0].get("contributions", 0)
    top1_pct = round(top1_contributions / total * 100, 2)

    top2_contributions = top1_contributions
    if len(sorted_contribs) > 1:
        top2_contributions += sorted_contribs[1].get("contributions", 0)
    top2_pct = round(top2_contributions / total * 100, 2)

    return {
        "top1_login": sorted_contribs[0].get("login", "Unknown"),
        "top1_pct": top1_pct,
        "top2_pct": top2_pct,
        "is_critical": top1_pct > 75,
    }