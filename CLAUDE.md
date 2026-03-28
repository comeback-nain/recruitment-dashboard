# CLAUDE.md — Recruitment Dashboard

AI assistant reference for working in this repository.

---

## Project Overview

Single-file Python/Streamlit web application for recruitment analytics. Ingests a CSV of hiring records and renders an interactive executive dashboard with KPI cards, 7 charts, data-quality checks, AI-generated insights, and multi-format exports (Markdown, CSV, PowerPoint).

---

## Repository Layout

```
recruitment-dashboard/
├── recruitment_analysis.py   # Entire application (single file, ~438 lines)
├── requirements.txt          # Python dependencies (pinned)
└── CLAUDE.md                 # This file
```

There is no `src/` directory, no package structure, no frontend build step, and no backend API.

---

## Tech Stack

| Layer | Library | Version |
|---|---|---|
| UI / server | Streamlit | 1.55.0 |
| Data processing | Pandas | 2.3.3 |
| Visualisation | Plotly | 6.6.0 |
| PPT export | python-pptx | 1.0.2 |

No database, no ORM, no Node.js, no REST API, no CI/CD pipeline.

---

## Running the App

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the Streamlit server (opens browser automatically)
python -m streamlit run recruitment_analysis.py
```

The app expects either:
- A file named `clean_recruitment_data.csv` in the working directory, **or**
- An uploaded CSV via the in-app file uploader

---

## Required CSV Schema

The input CSV must contain exactly these columns (names are case-sensitive):

| Column | Type | Notes |
|---|---|---|
| `Recruiter` | string | Name of the recruiter |
| `Joining_Date` | date/datetime | Parsed with `pd.to_datetime(..., errors="coerce")` |
| `Location` | string | Used to derive Work_Mode |
| `Client` | string | Company the candidate joins |
| `Candidate` | string | Candidate name |
| `Manager` | string | Hiring manager |
| `Work_Authorization` | string | e.g. US Citizen — uppercased on load |

Rows with unparseable `Joining_Date` are silently dropped during preprocessing.

---

## Code Architecture

All code lives in `recruitment_analysis.py`. Functions in call order:

### Data layer

| Function | Signature | Purpose |
|---|---|---|
| `normalize_text` | `(value: str) -> str` | Strips and collapses internal whitespace |
| `detect_name_variants` | `(series: pd.Series) -> List[List[str]]` | Fuzzy-groups names by alpha-only prefix (first 10 chars) to surface spelling variants |
| `preprocess` | `(df: pd.DataFrame) -> pd.DataFrame` | Validates required columns, cleans strings, parses dates, derives `Month`, `Weekday`, `Work_Mode` |

### UI layer

| Function | Signature | Purpose |
|---|---|---|
| `apply_filters` | `(df: pd.DataFrame) -> pd.DataFrame` | Renders sidebar controls (date range, multiselects) and returns filtered DataFrame |
| `generate_insights` | `(df: pd.DataFrame) -> List[str]` | Computes 9 bullet-point executive insights (stats, trend, name-variant note, recommendation) |
| `build_ppt` | `(insights, kpis) -> BytesIO` | Assembles a 3-slide PowerPoint: title, KPI snapshot, executive insights |
| `main` | `() -> None` | Orchestrates everything: page config, CSS, data load, preprocessing, filtering, KPIs, charts, exports |

### Derived columns (added by `preprocess`)

| Column | Logic |
|---|---|
| `Month` | First day of the joining month (`dt.to_period("M").dt.to_timestamp()`) |
| `Weekday` | Day name (`dt.day_name()`) |
| `Work_Mode` | `"Hybrid/Remote"` if Location contains `hybrid` or `remote` (case-insensitive), else `"Onsite/Other"` |

---

## Charts Rendered

Seven Plotly charts are displayed in a two-column layout + one full-width:

| Chart | Type | Data |
|---|---|---|
| Monthly Joining Trend | Line | `Month` vs join count |
| Top Clients by Joinings | Horizontal bar | Top 10 clients |
| Recruiter Performance | Horizontal bar | Top 10 recruiters |
| Manager Load Distribution | Horizontal bar | Top 10 managers |
| Work Authorization Mix | Donut pie | `Work_Authorization` value counts |
| Work Mode Split | Vertical bar | `Work_Mode` value counts |
| Joinings by Weekday | Vertical bar | Fixed Mon–Sun order |

All charts use `template="plotly_white"`.

---

## Export Formats

| Button | Output | File name pattern |
|---|---|---|
| Download Insights (.md) | Markdown bullet list of insights | `recruitment_insights_YYYYMMDD_HHMM.md` |
| Download Filtered Data (.csv) | Current filtered DataFrame | `filtered_recruitment_data_YYYYMMDD_HHMM.csv` |
| Download Summary Deck (.pptx) | 3-slide PowerPoint (requires python-pptx) | `recruitment_summary_YYYYMMDD_HHMM.pptx` |

The PPT export is guarded by `PPTX_AVAILABLE`; if `python-pptx` is missing the button is replaced with an `st.info()` message.

---

## Styling Conventions

- Background: CSS gradient (`#f8fafc` → `#eef2f7`) injected via `st.markdown(..., unsafe_allow_html=True)`
- KPI cards: white boxes with `border-radius: 12px` and `#e2e8f0` border (class `.kpi` — applied via Streamlit `st.metric`)
- Chart colour scales: `Blues`, `Tealgrn`, `Sunset`, `Mint` (Plotly named scales)
- Work-mode bars: `#0ea5e9` (sky-blue) and `#334155` (slate-gray)
- Do **not** add external CSS frameworks; keep styling in the single inline `<style>` block

---

## State Management

Pure Streamlit reactive model — no `st.session_state` is used explicitly. Every sidebar interaction triggers a full script re-run. There is no persistent state between sessions.

---

## Development Conventions

- **Language:** Python 3.x with `from __future__ import annotations`
- **Type hints:** All public functions are fully annotated (PEP 484)
- **Imports:** Standard library first, then third-party (`pandas`, `plotly`, `streamlit`), then optional (`pptx`)
- **Optional deps:** Guard with `try/except` at module level and a boolean flag (`PPTX_AVAILABLE`)
- **Error handling:** Surface errors to the UI via `st.error()` followed by `st.stop()`; do not raise unhandled exceptions in `main()`
- **No tests:** There is currently no test suite. If adding tests, use `pytest` and place them in a `tests/` directory
- **No `.env`:** No secrets or environment variables are used; do not add them without a corresponding `.env.example`
- **Single file:** Keep all logic in `recruitment_analysis.py` unless the file grows substantially; avoid premature modularisation

---

## Common Tasks

### Add a new chart
1. Compute the aggregated DataFrame from `filtered` inside `main()`
2. Create the `px.*` figure
3. Call `fig.update_layout(template="plotly_white")`
4. Place `st.plotly_chart(fig, width="stretch")` in the appropriate column

### Add a new insight
Edit `generate_insights()` — append a new string to the `insights` list.

### Add a new required column
Add the column name to `REQUIRED_COLUMNS` and add cleaning logic in `preprocess()`.

### Add a new export format
1. Prepare the data buffer in `main()` after the existing exports
2. Call `st.download_button()` with the appropriate `mime` type

---

## Git Workflow

- **Active development branch:** `claude/add-claude-documentation-k4p2q`
- **Main branch:** `main`
- **Remote:** `comeback-nain/recruitment-dashboard`
- Push with: `git push -u origin <branch-name>`

Commit messages should be short, imperative, and descriptive (e.g., `Add weekday chart`, `Fix date parsing for ISO format`).

---

## No CI/CD

There are no GitHub Actions, Dockerfiles, or deployment scripts. To deploy, use [Streamlit Community Cloud](https://streamlit.io/cloud) by pointing it at `recruitment_analysis.py` with `requirements.txt` in the same directory.
