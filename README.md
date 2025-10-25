# GitHub Repo Health Dashboard

A real-time, interactive dashboard built with [Streamlit](https://streamlit.io) that analyzes the health and activity of any public GitHub repository using the GitHub REST API.

![demo]([https://your-screenshot-or-gif-link-here](https://gitrepohealthdashboard.streamlit.app/))

---

## Features

- Input any GitHub repo (e.g., `streamlit/streamlit`)
- View repository stats: stars, forks, open issues
- Weekly commit activity (last 52 weeks)
- Top contributors breakdown
- Issue resolution time calculation
- Pull request merge ratio
- Monthly release frequency
- Language usage breakdown (bytes of code)
- Custom Repo Health Index (0–100)

---

## Tech Used

- **Python 3.10+**
- [Streamlit](https://streamlit.io) for the dashboard UI
- [Plotly](https://plotly.com/python/) for interactive charts
- **GitHub REST API** for live data
- **Pandas** for data manipulation
- **Unit tests** with `unittest` and `mock`

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/repo-health-dashboard.git
cd repo-health-dashboard

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

---

## Authentication (Optional) 

To increase API rate limits, you can add a **GitHub personal access token**:

- Open `github_api.py`
- Add your token in the `HEADERS` dictionary:

```python
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer YOUR_GITHUB_TOKEN"
}
```

Tokens are generated [here](https://github.com/settings/tokens)
