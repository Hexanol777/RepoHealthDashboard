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
