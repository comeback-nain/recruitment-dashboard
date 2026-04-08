# themes.py — Theme Factory for the Recruitment Executive Dashboard
# Provides CSS, Plotly color scales, and accent palettes for each theme.

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Theme:
    name: str
    label: str
    # Plotly template name
    plotly_template: str
    # CSS variables injected into the Streamlit page
    css_vars: Dict[str, str]
    # Ordered list of hex accent colours (used for multi-series charts)
    accents: List[str]
    # Continuous scale for single-metric heat-maps / bars
    continuous_scale: str
    # Canvas art palette (JS-ready hex strings)
    art_palette: List[str]


# ---------------------------------------------------------------------------
# Theme definitions
# ---------------------------------------------------------------------------

THEMES: Dict[str, Theme] = {
    "executive": Theme(
        name="executive",
        label="Executive Dark",
        plotly_template="plotly_dark",
        css_vars={
            "--bg-primary": "#0f172a",
            "--bg-secondary": "#1e293b",
            "--bg-card": "#1e293b",
            "--border-color": "#334155",
            "--text-primary": "#f1f5f9",
            "--text-secondary": "#94a3b8",
            "--accent-1": "#f59e0b",
            "--accent-2": "#0ea5e9",
            "--accent-gradient": "linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)",
            "--shadow": "0 4px 24px rgba(0,0,0,0.5)",
            "--radius": "14px",
        },
        accents=["#f59e0b", "#0ea5e9", "#10b981", "#f43f5e", "#a855f7", "#06b6d4"],
        continuous_scale="Plasma",
        art_palette=["#f59e0b", "#ef4444", "#0ea5e9", "#1e293b", "#0f172a"],
    ),
    "corporate": Theme(
        name="corporate",
        label="Corporate Blue",
        plotly_template="plotly_white",
        css_vars={
            "--bg-primary": "#f0f4ff",
            "--bg-secondary": "#e8eeff",
            "--bg-card": "#ffffff",
            "--border-color": "#c7d2fe",
            "--text-primary": "#1e2560",
            "--text-secondary": "#4f60a0",
            "--accent-1": "#3b82f6",
            "--accent-2": "#06b6d4",
            "--accent-gradient": "linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)",
            "--shadow": "0 4px 24px rgba(59,130,246,0.12)",
            "--radius": "12px",
        },
        accents=["#3b82f6", "#06b6d4", "#6366f1", "#10b981", "#f59e0b", "#ef4444"],
        continuous_scale="Blues",
        art_palette=["#3b82f6", "#06b6d4", "#6366f1", "#bfdbfe", "#f0f4ff"],
    ),
    "emerald": Theme(
        name="emerald",
        label="Emerald Growth",
        plotly_template="plotly_white",
        css_vars={
            "--bg-primary": "#f0fdf4",
            "--bg-secondary": "#dcfce7",
            "--bg-card": "#ffffff",
            "--border-color": "#86efac",
            "--text-primary": "#14532d",
            "--text-secondary": "#166534",
            "--accent-1": "#10b981",
            "--accent-2": "#059669",
            "--accent-gradient": "linear-gradient(135deg, #10b981 0%, #06b6d4 100%)",
            "--shadow": "0 4px 24px rgba(16,185,129,0.12)",
            "--radius": "12px",
        },
        accents=["#10b981", "#059669", "#06b6d4", "#3b82f6", "#f59e0b", "#a3e635"],
        continuous_scale="Tealgrn",
        art_palette=["#10b981", "#059669", "#06b6d4", "#dcfce7", "#f0fdf4"],
    ),
    "sunset": Theme(
        name="sunset",
        label="Sunset Warm",
        plotly_template="plotly_white",
        css_vars={
            "--bg-primary": "#fff7ed",
            "--bg-secondary": "#ffedd5",
            "--bg-card": "#ffffff",
            "--border-color": "#fed7aa",
            "--text-primary": "#7c2d12",
            "--text-secondary": "#9a3412",
            "--accent-1": "#f97316",
            "--accent-2": "#ef4444",
            "--accent-gradient": "linear-gradient(135deg, #f97316 0%, #ec4899 100%)",
            "--shadow": "0 4px 24px rgba(249,115,22,0.15)",
            "--radius": "12px",
        },
        accents=["#f97316", "#ef4444", "#ec4899", "#f59e0b", "#a855f7", "#06b6d4"],
        continuous_scale="Sunset",
        art_palette=["#f97316", "#ef4444", "#ec4899", "#ffedd5", "#fff7ed"],
    ),
}

DEFAULT_THEME = "corporate"


class ThemeFactory:
    """Selects, applies, and exposes the active theme."""

    def __init__(self, theme_name: str = DEFAULT_THEME):
        self._theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])

    # ------------------------------------------------------------------
    @property
    def theme(self) -> Theme:
        return self._theme

    def select(self, theme_name: str) -> "ThemeFactory":
        self._theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
        return self

    # ------------------------------------------------------------------
    def build_css(self) -> str:
        """Return a <style> block with CSS variables + global overrides."""
        vars_block = "\n".join(
            f"    {k}: {v};" for k, v in self._theme.css_vars.items()
        )
        return f"""
<style>
:root {{
{vars_block}
}}

/* ── App shell ───────────────────────────────────────────── */
.stApp {{
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}}
section[data-testid="stSidebar"] {{
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-color);
}}

/* ── KPI / metric cards ──────────────────────────────────── */
div[data-testid="stMetric"] {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    padding: 14px 18px;
    box-shadow: var(--shadow);
    transition: transform .18s ease, box-shadow .18s ease;
}}
div[data-testid="stMetric"]:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}}
div[data-testid="stMetricValue"] {{
    color: var(--accent-1) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}}
div[data-testid="stMetricLabel"] {{
    color: var(--text-secondary) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: .06em;
}}

/* ── Section headings ────────────────────────────────────── */
h1, h2, h3 {{
    color: var(--text-primary) !important;
}}
h2::after {{
    content: "";
    display: block;
    width: 48px;
    height: 3px;
    background: var(--accent-gradient);
    border-radius: 2px;
    margin-top: 6px;
}}

/* ── Buttons ─────────────────────────────────────────────── */
.stDownloadButton > button,
.stButton > button {{
    background: var(--accent-gradient) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: .04em;
    transition: opacity .18s ease, transform .18s ease;
}}
.stDownloadButton > button:hover,
.stButton > button:hover {{
    opacity: .88;
    transform: translateY(-2px);
}}

/* ── Plotly chart frame ──────────────────────────────────── */
.js-plotly-plot {{
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow);
}}

/* ── Data tables ─────────────────────────────────────────── */
.stDataFrame {{
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow);
}}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: var(--bg-secondary); }}
::-webkit-scrollbar-thumb {{ background: var(--border-color); border-radius: 3px; }}
</style>
"""

    # ------------------------------------------------------------------
    def plotly_colors(self) -> dict:
        """Return kwargs to pass to px chart color arguments."""
        return {
            "color_discrete_sequence": self._theme.accents,
            "color_continuous_scale": self._theme.continuous_scale,
            "template": self._theme.plotly_template,
        }

    # ------------------------------------------------------------------
    @staticmethod
    def all_labels() -> Dict[str, str]:
        return {k: v.label for k, v in THEMES.items()}
