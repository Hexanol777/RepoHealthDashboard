# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

from github_api import (
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
    summarize_languages
)


st.set_page_config(page_title="GitHub Repo Health Dashboard", layout="wide")
st.title("📊 GitHub Repo Health Dashboard")

# ─────────────────────────────────────────────────────────────────────
# 📥 User input
repo_name = st.text_input("Enter a repository (e.g. streamlit/streamlit)", value="streamlit/streamlit")

if repo_name:
    with st.spinner("Fetching repository data..."):
        stats = get_repo_stats(repo_name)
        contributors = get_contributors(repo_name)
        commits = get_commit_activity(repo_name)
        issues = get_issues(repo_name, state="all")
        prs = get_pull_requests(repo_name, state="all")
        releases = get_releases(repo_name)
        languages = get_languages(repo_name)

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────────────
    # 🔢 Top-level KPIs
    col1, col2, col3 = st.columns(3)
    if stats:
        col1.metric("⭐ Stars", stats["stars"])
        col2.metric("🍴 Forks", stats["forks"])
        col3.metric("🐞 Open Issues", stats["open_issues"])

    # ─────────────────────────────────────────────────────────────────────
    # 📈 Commits per Week (Last 52 Weeks)
    if commits:
        df_commits = pd.DataFrame(commits)
        df_commits["week"] = pd.to_datetime(df_commits["week"], unit="s")
        fig_commits = px.bar(df_commits, x="week", y="total", title="🕒 Weekly Commits (Past Year)")
        st.plotly_chart(fig_commits, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────
    # 👥 Contributors Pie Chart
    if contributors:
        df_contribs = pd.DataFrame(contributors)
        df_contribs = df_contribs.sort_values("contributions", ascending=False).head(10)
        fig_contribs = px.pie(df_contribs, names="login", values="contributions", title="Top 10 Contributors")
        st.plotly_chart(fig_contribs, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────
    # 🧮 Issue Resolution Time
    avg_resolution = calc_issue_resolution_time(issues)
    if avg_resolution is not None:
        st.metric("🕓 Avg Issue Resolution Time", f"{avg_resolution} days")

    # ─────────────────────────────────────────────────────────────────────
    # 📬 Pull Request Merge Ratio
    pr_merge_ratio = calc_pr_merge_ratio(prs)
    if pr_merge_ratio is not None:
        st.metric("✅ PR Merge Ratio", f"{pr_merge_ratio}%")

    # ─────────────────────────────────────────────────────────────────────
    # 📦 Releases Per Month
    release_counts = count_releases_per_month(releases)
    if release_counts:
        df_releases = pd.DataFrame({
            "Month": list(release_counts.keys()),
            "Releases": list(release_counts.values())
        })
        df_releases = df_releases.sort_values("Month")
        fig_releases = px.bar(df_releases, x="Month", y="Releases", title="📅 Releases per Month")
        st.plotly_chart(fig_releases, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────
    # 🧠 Languages Used
    lang_summary = summarize_languages(languages)
    if lang_summary:
        df_langs = pd.DataFrame(lang_summary)
        fig_langs = px.pie(df_langs, names="language", values="percent", title="🧠 Codebase Language Breakdown")
        st.plotly_chart(fig_langs, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────
    # ✅ Repo Health Index (Bonus)
    if avg_resolution and pr_merge_ratio and release_counts:
        health_score = (
            (100 - min(avg_resolution, 100)) * 0.3 +
            min(pr_merge_ratio, 100) * 0.3 +
            min(len(release_counts), 12) * 8.3  # Max 12 months = 100%
        )
        st.metric("🧪 Repo Health Index", f"{round(health_score, 1)} / 100")
