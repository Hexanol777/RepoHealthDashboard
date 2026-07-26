# app.py

import streamlit as st
import pandas as pd
import plotly.express as px

from github_api import (
    normalize_repo_input,
    get_repo_stats,
    get_contributors,
    get_commit_activity,
    get_issues,
    get_pull_requests,
    get_releases,
    get_languages,
)

from utils import (
    calc_issue_resolution_time,
    calc_pr_merge_ratio,
    count_releases_per_month,
    summarize_languages,
    count_open_closed_issues,
    summarize_commits_per_week,
    top_contributors,
    calculate_bus_factor,
)

st.set_page_config(page_title="GitHub Repo Health Dashboard", layout="wide")
st.title("📊 GitHub Repo Health Dashboard")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def fetch_repo_data(repo_name: str) -> dict:
    """Fetch all API data for a single repository and return as a dict."""
    return {
        "stats":        get_repo_stats(repo_name),
        "contributors": get_contributors(repo_name),
        "commits":      get_commit_activity(repo_name),
        "issues":       get_issues(repo_name, state="all"),
        "prs":          get_pull_requests(repo_name, state="all"),
        "releases":     get_releases(repo_name),
        "languages":    get_languages(repo_name),
    }


def compute_health_score(avg_resolution, pr_merge_ratio, release_counts, bus_factor) -> float | None:
    """
    Repo Health Index formula.

    Weights:
        issue resolution score  30 %
        PR merge ratio          30 %
        release cadence         40 %

    Bus-factor penalty: if the top contributor owns > 75 % of commits,
    subtract up to 10 points from the final score.
    """
    if not (avg_resolution and pr_merge_ratio and release_counts):
        return None

    release_score = min(sum(release_counts.values()) / 12 * 100, 100)
    pr_score      = min(pr_merge_ratio, 100)
    issue_score   = max(0, 100 - min(avg_resolution, 100))

    score = issue_score * 0.3 + pr_score * 0.3 + release_score * 0.4

    # Bus-factor penalty (up to −10 pts when is_critical)
    if bus_factor and bus_factor["is_critical"]:
        excess = bus_factor["top1_pct"] - 75          # 0–25 range
        penalty = round(min(excess / 25 * 10, 10), 2) # scales linearly to −10
        score = max(0, score - penalty)

    return round(score, 1)


def render_overview(stats, label: str = ""):
    """Render the Stars / Forks / Open Issues metric row."""
    heading = f"📌 Repository Overview — `{label}`" if label else "📌 Repository Overview"
    st.subheader(heading)
    if stats:
        c1, c2, c3 = st.columns(3)
        c1.metric("⭐ Stars",       stats["stars"])
        c2.metric("🍴 Forks",       stats["forks"])
        c3.metric("🐞 Open Issues", stats["open_issues"])


def render_commits_chart(commits, title_suffix: str = ""):
    """Return a Plotly bar chart for weekly commit activity, or None."""
    if not commits:
        return None
    weekly_data = summarize_commits_per_week(commits)
    if not weekly_data:
        return None
    df = pd.DataFrame(weekly_data)
    df["week"] = pd.to_datetime(df["week"], unit="s")
    return px.bar(df, x="week", y="commits",
                  title=f"Commits Per Week (Last 52 Weeks){title_suffix}")


def render_language_chart(languages, title_suffix: str = ""):
    """Return a Plotly pie chart for language breakdown, or None."""
    lang_summary = summarize_languages(languages)
    if not lang_summary:
        return None
    df = pd.DataFrame(lang_summary)
    return px.pie(df, names="language", values="percent",
                  title=f"Language Breakdown by Bytes{title_suffix}")


def render_bus_factor(bus_factor):
    """Display the Bus Factor metric with optional warning."""
    if not bus_factor:
        return
    top1_pct   = bus_factor["top1_pct"]
    top2_pct   = bus_factor["top2_pct"]
    top1_login = bus_factor["top1_login"]

    warning = " ⚠️" if top1_pct > 50 else ""
    st.metric(
        label=f"🚌 Bus Factor — top contributor{warning}",
        value=f"{top1_pct}%",
        help=(
            f"**{top1_login}** accounts for **{top1_pct}%** of all commits. "
            f"Top 2 contributors combined: **{top2_pct}%**."
        ),
    )
    if top1_pct > 75:
        st.error(
            f"⚠️ **Critical concentration risk:** `{top1_login}` owns "
            f"**{top1_pct}%** of all commits. This project has a very low bus factor."
        )
    elif top1_pct > 50:
        st.warning(
            f"⚠️ `{top1_login}` accounts for **{top1_pct}%** of commits. "
            "Consider spreading knowledge across more contributors."
        )


# ─────────────────────────────────────────────────────────────────────────────
# User input
# ─────────────────────────────────────────────────────────────────────────────

user_input = st.text_input(
    "Enter a repository (e.g. streamlit/streamlit)",
    value="streamlit/streamlit",
)

compare_mode = st.checkbox("Compare with another repository")

user_input_2 = ""
if compare_mode:
    user_input_2 = st.text_input(
        "Enter a second repository to compare against",
        value="",
        placeholder="e.g. facebook/react",
    )

repo_name  = normalize_repo_input(user_input)
repo_name2 = normalize_repo_input(user_input_2) if user_input_2.strip() else None

if not repo_name:
    st.warning("Could not resolve that repository. Please check the input.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Data fetching (cached per repo)
# ─────────────────────────────────────────────────────────────────────────────

with st.spinner("Fetching repository data..."):
    data1 = fetch_repo_data(repo_name)
    data2 = fetch_repo_data(repo_name2) if repo_name2 else None

# ─────────────────────────────────────────────────────────────────────────────
# Pre-compute derived values for both repos
# ─────────────────────────────────────────────────────────────────────────────

def derived(data: dict) -> dict:
    bus_factor     = calculate_bus_factor(data["contributors"])
    avg_resolution = calc_issue_resolution_time(data["issues"])
    pr_merge_ratio = calc_pr_merge_ratio(data["prs"])
    release_counts = count_releases_per_month(data["releases"] or [])
    health_score   = compute_health_score(
        avg_resolution, pr_merge_ratio, release_counts, bus_factor
    )
    return dict(
        bus_factor=bus_factor,
        avg_resolution=avg_resolution,
        pr_merge_ratio=pr_merge_ratio,
        release_counts=release_counts,
        health_score=health_score,
    )

d1 = derived(data1)
d2 = derived(data2) if data2 else None

# ─────────────────────────────────────────────────────────────────────────────
# Section: Repository Overview
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
if compare_mode and data2:
    col_a, col_b = st.columns(2)
    with col_a:
        render_overview(data1["stats"], label=repo_name)
    with col_b:
        render_overview(data2["stats"], label=repo_name2)
else:
    render_overview(data1["stats"])

# ─────────────────────────────────────────────────────────────────────────────
# Section: Health Score
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("📈 Repo Health Index")

if compare_mode and data2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.caption(f"`{repo_name}`")
        if d1["health_score"] is not None:
            st.metric("🧪 Health Score", f"{d1['health_score']} / 100")
        else:
            st.info("Not enough data to compute a health score.")
    with col_b:
        st.caption(f"`{repo_name2}`")
        if d2["health_score"] is not None:
            st.metric("🧪 Health Score", f"{d2['health_score']} / 100")
        else:
            st.info("Not enough data to compute a health score.")
else:
    if d1["health_score"] is not None:
        penalty_note = ""
        if d1["bus_factor"] and d1["bus_factor"]["is_critical"]:
            penalty_note = " *(bus-factor penalty applied)*"
        st.metric("🧪 Health Score", f"{d1['health_score']} / 100")
        if penalty_note:
            st.caption(penalty_note)
    else:
        st.info("Not enough data to compute a health score.")

# ─────────────────────────────────────────────────────────────────────────────
# Section: Weekly Commit Activity
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("🕒 Weekly Commit Activity")

fig1 = render_commits_chart(data1["commits"], f" — {repo_name}" if compare_mode and data2 else "")
fig2 = render_commits_chart(data2["commits"], f" — {repo_name2}") if data2 else None

if compare_mode and data2:
    col_a, col_b = st.columns(2)
    with col_a:
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No commit activity data.")
    with col_b:
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No commit activity data.")
else:
    if fig1:
        st.plotly_chart(fig1, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Section: Top Contributors + Bus Factor
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("👥 Top Contributors")

def render_contributors_section(data: dict, derived_data: dict, repo_label: str = ""):
    contributors = data["contributors"]
    bus_factor   = derived_data["bus_factor"]

    if repo_label:
        st.caption(f"`{repo_label}`")

    render_bus_factor(bus_factor)

    if contributors:
        df_contribs = pd.DataFrame(top_contributors(contributors))
        fig = px.pie(
            df_contribs, names="login", values="contributions",
            title=f"Top Contributors{' — ' + repo_label if repo_label else ''}",
        )
        st.plotly_chart(fig, use_container_width=True)

if compare_mode and data2:
    col_a, col_b = st.columns(2)
    with col_a:
        render_contributors_section(data1, d1, repo_name)
    with col_b:
        render_contributors_section(data2, d2, repo_name2)
else:
    render_contributors_section(data1, d1)

# ─────────────────────────────────────────────────────────────────────────────
# Section: Issues & Pull Requests
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("📬 Issues & Pull Requests")

def render_issues_section(data: dict, derived_data: dict):
    col4, col5 = st.columns(2)
    if derived_data["avg_resolution"] is not None:
        col4.metric("🕓 Avg Issue Resolution Time", f"{derived_data['avg_resolution']} days")
    if derived_data["pr_merge_ratio"] is not None:
        col5.metric("✅ PR Merge Ratio", f"{derived_data['pr_merge_ratio']}%")

    issue_counts = count_open_closed_issues(data["issues"])
    if issue_counts:
        df_issues = pd.DataFrame({
            "State": ["Open", "Closed"],
            "Count": [issue_counts["open"], issue_counts["closed"]],
        })
        fig = px.bar(
            df_issues, x="State", y="Count",
            title="Open vs Closed Issues", color="State", barmode="group",
        )
        st.plotly_chart(fig, use_container_width=True)

if compare_mode and data2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.caption(f"`{repo_name}`")
        render_issues_section(data1, d1)
    with col_b:
        st.caption(f"`{repo_name2}`")
        render_issues_section(data2, d2)
else:
    render_issues_section(data1, d1)

# ─────────────────────────────────────────────────────────────────────────────
# Section: Releases Over Time
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("📦 Releases Over Time")

def render_releases_section(release_counts: dict, label: str = ""):
    if release_counts:
        df_releases = pd.DataFrame({
            "Month":    list(release_counts.keys()),
            "Releases": list(release_counts.values()),
        }).sort_values("Month")
        fig = px.bar(
            df_releases, x="Month", y="Releases",
            title=f"Monthly Release Frequency{' — ' + label if label else ''}",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No release data available.")

if compare_mode and data2:
    col_a, col_b = st.columns(2)
    with col_a:
        render_releases_section(d1["release_counts"], repo_name)
    with col_b:
        render_releases_section(d2["release_counts"], repo_name2)
else:
    render_releases_section(d1["release_counts"])

# ─────────────────────────────────────────────────────────────────────────────
# Section: Languages Used
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("🧠 Languages Used")

fig_lang1 = render_language_chart(
    data1["languages"], f" — {repo_name}" if compare_mode and data2 else ""
)
fig_lang2 = render_language_chart(data2["languages"], f" — {repo_name2}") if data2 else None

if compare_mode and data2:
    col_a, col_b = st.columns(2)
    with col_a:
        if fig_lang1:
            st.plotly_chart(fig_lang1, use_container_width=True)
        else:
            st.info("No language data.")
    with col_b:
        if fig_lang2:
            st.plotly_chart(fig_lang2, use_container_width=True)
        else:
            st.info("No language data.")
else:
    if fig_lang1:
        st.plotly_chart(fig_lang1, use_container_width=True)