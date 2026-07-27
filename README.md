# GitHub Repo Health Dashboard

A real-time, interactive analytics dashboard built with [Streamlit](https://streamlit.io) that evaluates the health and activity of any public GitHub repository. It aggregates live data from the GitHub REST API and presents it through interactive Plotly charts, computed health metrics, and a side-by-side repository comparison mode.

> **Live demo:** [gitrepohealthdashboard.streamlit.app](https://gitrepohealthdashboard.streamlit.app/)

---

## Features

### Core Analytics
| Metric | Description |
|---|---|
| Repository Overview | Stars, forks, and open issue counts |
| Weekly Commit Activity | Bar chart of commit volume over the last 52 weeks |
| Top Contributors | Pie chart of commit share across the top 8 contributors |
| Issue Resolution Time | Average days from issue open to close |
| PR Merge Ratio | Percentage of pull requests that were merged |
| Release Frequency | Monthly release cadence over the project's lifetime |
| Language Breakdown | Proportional breakdown of languages by bytes of code |
| **Repo Health Index** | Composite 0–100 score derived from the above signals |

### Bus Factor Analysis
Calculates contributor concentration risk by measuring what percentage of total commits are owned by the top one or two developers.

- Displays a `⚠️` warning when the top contributor accounts for more than **50%** of commits
- Raises a critical alert when that figure exceeds **75%**, and applies a proportional penalty (up to −10 pts) to the Health Index

### Repository Comparison Mode 
Enable the **"Compare with another repository"** toggle to analyse two repositories simultaneously. All sections — overview metrics, Health Index, commit activity, contributors, issues, releases, and language breakdown — are rendered side-by-side using a two-column layout.

### API Caching
All GitHub API calls are wrapped with `@st.cache_data(ttl=3600)`. Data is fetched once per hour per repository, eliminating redundant network requests during active sessions.

---

## Project Structure

```
RepoHealthDashboard/
├── .streamlit/
│   ├── config.toml          # Streamlit theme and server config
│   └── secrets.toml         # GitHub token (local only, not committed)
├── app.py                   # Streamlit UI, layout, and rendering logic
├── github_api.py            # GitHub REST API calls (cached)
├── utils.py                 # Data processing and metric calculations
├── requirements.txt         # Python dependencies
├── test_github_api.py       # Unit tests — API layer
├── test_utils.py            # Unit tests — utility functions
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10 or later
- A GitHub Personal Access Token ([generate one here](https://github.com/settings/tokens)) — a token with no additional scopes is sufficient for reading public repositories

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Hexanol777/RepoHealthDashboard.git
cd RepoHealthDashboard

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create `.streamlit/secrets.toml` in the project root and add your token:

```toml
GITHUB_TOKEN = "ghp_yourtoken..."
```

### Running the App

```bash
streamlit run app.py
```

---

## Health Index Formula

The Repo Health Index is a composite score from 0 to 100 calculated as follows:

```
issue_score   = max(0, 100 − min(avg_resolution_days, 100))
pr_score      = min(pr_merge_ratio, 100)
release_score = min((total_releases / 12) × 100, 100)

health_score  = (issue_score × 0.30)
              + (pr_score    × 0.30)
              + (release_score × 0.40)
```

**Bus-factor penalty:** If the top contributor owns more than 75% of all commits, a penalty of up to 10 points is subtracted, scaling linearly with the excess above the 75% threshold.

---

## Running Tests

```bash
python -m unittest test_utils -v
python -m unittest test_github_api -v
```

The test suite covers issue resolution time, PR merge ratio, release counting, language summarisation, and all edge cases for the bus factor calculation (empty input, zero contributions, single contributor, boundary conditions, and unsorted input).

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI & server | [Streamlit](https://streamlit.io) |
| Charts | [Plotly Express](https://plotly.com/python/) |
| Data | [Pandas](https://pandas.pydata.org/) |
| API | [GitHub REST API v3](https://docs.github.com/en/rest) |
| Testing | Python `unittest` |
| Language | Python 3.10+ |

---

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.