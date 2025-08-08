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
    get_languages
)

from utils import (
    calc_issue_resolution_time,
    calc_pr_merge_ratio,
    count_releases_per_month,
    summarize_languages,
    count_open_closed_issues,
    summarize_commits_per_week,
    top_contributors
)

st.set_page_config(page_title="GitHub Repo Health Dashboard", layout="wide")
st.title("📊 GitHub Repo Health Dashboard")

# ─────────────────────────────────────────────────────────────────────
# 📥 User input
user_input = st.text_input("Enter a repository (e.g. streamlit/streamlit)", value="streamlit/streamlit")
repo_name = normalize_repo_input(user_input)


if repo_name:
    with st.spinner("Fetching repository data..."):
        stats = get_repo_stats(repo_name)
        contributors = get_contributors(repo_name)
        commits = get_commit_activity(repo_name)  # retry-safe version
        issues = get_issues(repo_name, state="all")
        prs = get_pull_requests(repo_name, state="all")
        releases = get_releases(repo_name)
        languages = get_languages(repo_name)

    # ─────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📌 Repository Overview")
    col1, col2, col3 = st.columns(3)
    if stats:
        col1.metric("⭐ Stars", stats["stars"])
        col2.metric("🍴 Forks", stats["forks"])
        col3.metric("🐞 Open Issues", stats["open_issues"])

    # ─────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🕒 Weekly Commit Activity")
    if commits:
        weekly_data = summarize_commits_per_week(commits)
        if weekly_data:
            df_commits = pd.DataFrame(weekly_data)
            df_commits["week"] = pd.to_datetime(df_commits["week"], unit="s")
            fig_commits = px.bar(df_commits, x="week", y="commits", title="Commits Per Week (Last 52 Weeks)")
            st.plotly_chart(fig_commits, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("👥 Top Contributors")
    if contributors:
        df_contribs = pd.DataFrame(top_contributors(contributors))
        fig_contribs = px.pie(df_contribs, names="login", values="contributions", title="Top 10 Contributors")
        st.plotly_chart(fig_contribs, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📬 Issues & Pull Requests")
    col4, col5 = st.columns(2)

    # Issue resolution time
    avg_resolution = calc_issue_resolution_time(issues)
    if avg_resolution is not None:
        col4.metric("🕓 Avg Issue Resolution Time", f"{avg_resolution} days")

    # PR merge ratio
    pr_merge_ratio = calc_pr_merge_ratio(prs)
    if pr_merge_ratio is not None:
        col5.metric("✅ PR Merge Ratio", f"{pr_merge_ratio}%")

    # Open vs Closed issues chart
    issue_counts = count_open_closed_issues(issues)
    if issue_counts:
        df_issues = pd.DataFrame({
            "State": ["Open", "Closed"],
            "Count": [issue_counts["open"], issue_counts["closed"]]
        })
        fig_issues = px.bar(df_issues, x="State", y="Count", title="Open vs Closed Issues", color="State", barmode="group")
        st.plotly_chart(fig_issues, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📦 Releases Over Time")
    release_counts = count_releases_per_month(releases)
    if release_counts:
        df_releases = pd.DataFrame({
            "Month": list(release_counts.keys()),
            "Releases": list(release_counts.values())
        }).sort_values("Month")
        fig_releases = px.bar(df_releases, x="Month", y="Releases", title="Monthly Release Frequency")
        st.plotly_chart(fig_releases, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🧠 Languages Used")
    lang_summary = summarize_languages(languages)
    if lang_summary:
        df_langs = pd.DataFrame(lang_summary)
        fig_langs = px.pie(df_langs, names="language", values="percent", title="Language Breakdown by Bytes")
        st.plotly_chart(fig_langs, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📈 Repo Health Index")
    if avg_resolution and pr_merge_ratio and release_counts:
        release_score = min(sum(release_counts.values()) / 12 * 100, 100)
        pr_score = min(pr_merge_ratio, 100)
        issue_score = max(0, 100 - min(avg_resolution, 100))

        health_score = (
            issue_score * 0.3 +
            pr_score * 0.3 +
            release_score * 0.4
        )
        st.metric("🧪 Health Score", f"{round(health_score, 1)} / 100")

