# web_artifacts.py — Standalone Web Artifact Generator
# Produces self-contained HTML files (no server dependency) that
# embed Plotly charts + insights as portable, shareable reports.

from __future__ import annotations
import json
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.io as pio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _df_to_plotly_json(fig) -> str:
    return pio.to_json(fig)


def _build_chart_block(title: str, fig_json: str, idx: int) -> str:
    return f"""
    <div class="chart-card" data-aos="{idx}">
      <h3>{title}</h3>
      <div id="chart_{idx}" class="chart-container"></div>
    </div>
    <script>
      (function(){{
        const spec = {fig_json};
        Plotly.react('chart_{idx}', spec.data, spec.layout, {{responsive:true, displayModeBar:false}});
      }})();
    </script>
"""


# ---------------------------------------------------------------------------
# Main export function
# ---------------------------------------------------------------------------

def generate_html_report(
    filtered: pd.DataFrame,
    insights: List[str],
    kpis: Dict[str, str],
    theme_css_vars: Dict[str, str],
    accents: List[str],
    continuous_scale: str,
    title: str = "Recruitment Executive Dashboard",
) -> str:
    """
    Build and return a fully self-contained HTML artifact string.

    The file embeds Plotly via CDN (single external dependency) and
    all chart data inline so it renders without a server.
    """

    # ── Build charts ────────────────────────────────────────────────────
    monthly = (
        filtered.groupby("Month", as_index=False)
        .size()
        .rename(columns={"size": "Joinings"})
        .sort_values("Month")
    )
    top_clients = filtered["Client"].value_counts().head(10).reset_index()
    top_clients.columns = ["Client", "Joinings"]
    top_recruiters = filtered["Recruiter"].value_counts().head(10).reset_index()
    top_recruiters.columns = ["Recruiter", "Joinings"]
    manager_load = filtered["Manager"].value_counts().head(10).reset_index()
    manager_load.columns = ["Manager", "Joinings"]
    auth_mix = filtered["Work_Authorization"].value_counts().reset_index()
    auth_mix.columns = ["Work_Authorization", "Count"]

    tpl = "plotly_dark" if theme_css_vars.get("--bg-primary", "#fff").startswith("#0") else "plotly_white"

    charts = []

    fig1 = px.line(
        monthly, x="Month", y="Joinings", markers=True,
        title="Monthly Joining Trend",
        color_discrete_sequence=accents,
        template=tpl,
    )
    charts.append(("Monthly Joining Trend", _df_to_plotly_json(fig1)))

    fig2 = px.bar(
        top_clients.sort_values("Joinings"), x="Joinings", y="Client",
        orientation="h", title="Top Clients",
        color="Joinings", color_continuous_scale=continuous_scale,
        template=tpl,
    )
    charts.append(("Top Clients by Joinings", _df_to_plotly_json(fig2)))

    fig3 = px.bar(
        top_recruiters.sort_values("Joinings"), x="Joinings", y="Recruiter",
        orientation="h", title="Recruiter Performance",
        color="Joinings", color_continuous_scale=continuous_scale,
        template=tpl,
    )
    charts.append(("Recruiter Performance", _df_to_plotly_json(fig3)))

    fig4 = px.bar(
        manager_load.sort_values("Joinings"), x="Joinings", y="Manager",
        orientation="h", title="Manager Load",
        color="Joinings", color_continuous_scale=continuous_scale,
        template=tpl,
    )
    charts.append(("Manager Load Distribution", _df_to_plotly_json(fig4)))

    fig5 = px.pie(
        auth_mix, names="Work_Authorization", values="Count",
        hole=0.55, title="Work Authorization Mix",
        color_discrete_sequence=accents,
        template=tpl,
    )
    charts.append(("Work Authorization Mix", _df_to_plotly_json(fig5)))

    # ── CSS variables ────────────────────────────────────────────────────
    css_vars = "\n".join(f"  {k}: {v};" for k, v in theme_css_vars.items())

    # ── KPI cards HTML ───────────────────────────────────────────────────
    kpi_cards = "".join(
        f'<div class="kpi-card"><div class="kpi-value">{v}</div>'
        f'<div class="kpi-label">{k}</div></div>'
        for k, v in kpis.items()
    )

    # ── Insights list ────────────────────────────────────────────────────
    insight_items = "".join(f"<li>{i}</li>" for i in insights)

    # ── Charts HTML ──────────────────────────────────────────────────────
    charts_html = "".join(
        _build_chart_block(title_c, fig_j, idx)
        for idx, (title_c, fig_j) in enumerate(charts)
    )

    generated = datetime.now().strftime("%d %b %Y %H:%M")
    accent1 = theme_css_vars.get("--accent-1", accents[0])
    accent2 = theme_css_vars.get("--accent-2", accents[1] if len(accents) > 1 else accents[0])
    bg_primary = theme_css_vars.get("--bg-primary", "#f0f4ff")
    bg_card = theme_css_vars.get("--bg-card", "#ffffff")
    text_primary = theme_css_vars.get("--text-primary", "#1e2560")
    text_secondary = theme_css_vars.get("--text-secondary", "#4f60a0")
    border_color = theme_css_vars.get("--border-color", "#c7d2fe")
    shadow = theme_css_vars.get("--shadow", "0 4px 24px rgba(0,0,0,0.1)")
    radius = theme_css_vars.get("--radius", "12px")
    gradient = theme_css_vars.get("--accent-gradient", f"linear-gradient(135deg,{accent1},{accent2})")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title}</title>
  <script src="https://cdn.plot.ly/plotly-2.34.0.min.js"></script>
  <style>
    :root {{
{css_vars}
    }}
    *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.6;
    }}

    /* ── Header ──────────────────────────────────────────── */
    header {{
      background: {gradient};
      padding: 42px 40px 36px;
      position: relative;
      overflow: hidden;
    }}
    header::after {{
      content: "";
      position: absolute; inset:0;
      background: repeating-linear-gradient(
        45deg, rgba(255,255,255,.03) 0px, rgba(255,255,255,.03) 1px,
        transparent 1px, transparent 18px
      );
    }}
    header h1 {{
      color: #fff;
      font-size: clamp(1.5rem,4vw,2.4rem);
      font-weight: 800;
      letter-spacing: -.02em;
      position: relative; z-index:1;
    }}
    header p {{
      color: rgba(255,255,255,.75);
      font-size: .9rem;
      margin-top: 6px;
      position: relative; z-index:1;
    }}

    /* ── Main container ──────────────────────────────────── */
    main {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 36px 24px 60px;
    }}

    /* ── KPI strip ───────────────────────────────────────── */
    .kpi-strip {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px,1fr));
      gap: 16px;
      margin-bottom: 36px;
    }}
    .kpi-card {{
      background: {bg_card};
      border: 1px solid {border_color};
      border-radius: {radius};
      padding: 20px 18px;
      box-shadow: {shadow};
      text-align: center;
      transition: transform .18s, box-shadow .18s;
    }}
    .kpi-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 10px 32px rgba(0,0,0,.18);
    }}
    .kpi-value {{
      font-size: 2rem;
      font-weight: 800;
      color: {accent1};
      line-height: 1.1;
    }}
    .kpi-label {{
      font-size: .72rem;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: {text_secondary};
      margin-top: 4px;
    }}

    /* ── Charts grid ─────────────────────────────────────── */
    .charts-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%,520px),1fr));
      gap: 22px;
      margin-bottom: 36px;
    }}
    .chart-card {{
      background: {bg_card};
      border: 1px solid {border_color};
      border-radius: {radius};
      box-shadow: {shadow};
      padding: 20px 18px 14px;
      transition: transform .18s;
    }}
    .chart-card:hover {{ transform: translateY(-3px); }}
    .chart-card h3 {{
      font-size: .85rem;
      text-transform: uppercase;
      letter-spacing: .07em;
      color: {text_secondary};
      margin-bottom: 12px;
    }}
    .chart-container {{ width:100%; min-height:320px; }}

    /* ── Insights ────────────────────────────────────────── */
    .insights-section {{
      background: {bg_card};
      border: 1px solid {border_color};
      border-radius: {radius};
      box-shadow: {shadow};
      padding: 28px 32px;
      margin-bottom: 36px;
    }}
    .insights-section h2 {{
      font-size: 1.15rem;
      font-weight: 700;
      color: {text_primary};
      margin-bottom: 18px;
    }}
    .insights-section h2::after {{
      content: "";
      display: block;
      width: 44px; height: 3px;
      background: {gradient};
      border-radius: 2px;
      margin-top: 6px;
    }}
    .insights-section ol {{
      padding-left: 22px;
      display: grid;
      gap: 10px;
    }}
    .insights-section li {{
      font-size: .93rem;
      color: {text_secondary};
      line-height: 1.55;
    }}

    /* ── Footer ──────────────────────────────────────────── */
    footer {{
      text-align: center;
      font-size: .78rem;
      color: {text_secondary};
      padding: 24px;
      border-top: 1px solid {border_color};
    }}

    /* ── Fade-in animation ───────────────────────────────── */
    [data-aos] {{ opacity:0; transform:translateY(20px); animation: fadeUp .55s ease forwards; }}
    [data-aos="0"] {{ animation-delay:.05s }}
    [data-aos="1"] {{ animation-delay:.15s }}
    [data-aos="2"] {{ animation-delay:.25s }}
    [data-aos="3"] {{ animation-delay:.35s }}
    [data-aos="4"] {{ animation-delay:.45s }}
    @keyframes fadeUp {{ to {{ opacity:1; transform:none; }} }}
  </style>
</head>
<body>

<header>
  <h1>{title}</h1>
  <p>Generated on {generated} &nbsp;·&nbsp; Standalone Web Artifact</p>
</header>

<main>
  <div class="kpi-strip">
    {kpi_cards}
  </div>

  <div class="charts-grid">
    {charts_html}
  </div>

  <section class="insights-section">
    <h2>Executive Insights</h2>
    <ol>
      {insight_items}
    </ol>
  </section>
</main>

<footer>
  Recruitment Executive Dashboard &nbsp;|&nbsp; {generated} &nbsp;|&nbsp; Web Artifact
</footer>

</body>
</html>
"""
    return html


# ---------------------------------------------------------------------------
# Individual chart artifact
# ---------------------------------------------------------------------------

def generate_chart_artifact(fig, chart_title: str, theme_css_vars: Dict[str, str]) -> str:
    """Return a minimal self-contained HTML page containing a single Plotly chart."""
    fig_json = _df_to_plotly_json(fig)
    bg = theme_css_vars.get("--bg-primary", "#f0f4ff")
    card_bg = theme_css_vars.get("--bg-card", "#ffffff")
    text = theme_css_vars.get("--text-primary", "#1e2560")
    gradient = theme_css_vars.get("--accent-gradient", "linear-gradient(135deg,#3b82f6,#06b6d4)")
    radius = theme_css_vars.get("--radius", "12px")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{chart_title}</title>
  <script src="https://cdn.plot.ly/plotly-2.34.0.min.js"></script>
  <style>
    body {{ margin:0; background:{bg}; font-family:system-ui,sans-serif; display:flex;
           flex-direction:column; align-items:center; justify-content:center; min-height:100vh; }}
    h1 {{ font-size:1.1rem; background:{gradient}; -webkit-background-clip:text;
          -webkit-text-fill-color:transparent; margin-bottom:18px; font-weight:700; }}
    .card {{ background:{card_bg}; border-radius:{radius}; padding:24px;
             box-shadow:0 4px 32px rgba(0,0,0,.12); width:min(96vw,900px); }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{chart_title}</h1>
    <div id="chart" style="width:100%;min-height:420px;"></div>
  </div>
  <script>
    const spec = {fig_json};
    Plotly.react('chart', spec.data, spec.layout, {{responsive:true}});
  </script>
</body>
</html>
"""
