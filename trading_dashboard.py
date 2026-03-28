# trading_dashboard.py
# Multi-agent trading analysis dashboard powered by TradingAgents
# Run with:
#   python -m streamlit run trading_dashboard.py

from __future__ import annotations

import os
import traceback
from datetime import date, timedelta

import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Trading Analysis Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Multi-Agent Trading Analysis")
st.caption(
    "Powered by [TradingAgents](https://github.com/TauricResearch/TradingAgents) "
    "— a LangGraph multi-agent framework. **Educational use only. Not financial advice.**"
)

st.warning(
    "⚠️ **Disclaimer:** This tool produces AI-generated analysis for research and "
    "educational purposes only. It is NOT financial advice. Never risk money you "
    "cannot afford to lose. Always consult a licensed financial advisor.",
    icon="⚠️",
)

# ---------------------------------------------------------------------------
# Sidebar — configuration
# ---------------------------------------------------------------------------
st.sidebar.header("⚙️ Configuration")

PROVIDER_OPTIONS = ["anthropic", "openai", "google", "openrouter"]
provider = st.sidebar.selectbox("LLM Provider", PROVIDER_OPTIONS, index=0)

api_key_label = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}[provider]

# Pre-fill from environment if available
env_key = os.environ.get(api_key_label, "")
api_key = st.sidebar.text_input(
    f"{api_key_label}",
    value=env_key,
    type="password",
    help="Your API key for the selected LLM provider.",
)

MODEL_OPTIONS = {
    "anthropic": [
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001",
        "claude-opus-4-6",
    ],
    "openai": ["gpt-4o", "gpt-4o-mini", "o3-mini"],
    "google": ["gemini-2.5-pro", "gemini-2.0-flash"],
    "openrouter": ["meta-llama/llama-3.3-70b-instruct", "mistralai/mistral-large"],
}

deep_model = st.sidebar.selectbox(
    "Deep-Thinking Model (complex reasoning)",
    MODEL_OPTIONS[provider],
    index=0,
    help="Used by Bull/Bear researchers and Portfolio Manager.",
)
quick_model = st.sidebar.selectbox(
    "Quick-Thinking Model (fast tasks)",
    MODEL_OPTIONS[provider],
    index=min(1, len(MODEL_OPTIONS[provider]) - 1),
    help="Used by data-fetching and lightweight agents.",
)

st.sidebar.divider()
st.sidebar.subheader("📈 Asset & Date")

# Preset assets across the sectors the user cares about
ASSET_PRESETS = {
    "Crypto — ETH/USDT": "ETH-USD",
    "Crypto — BTC/USDT": "BTC-USD",
    "Crypto — SOL": "SOL-USD",
    "AI Equity — NVDA": "NVDA",
    "AI Equity — MSFT": "MSFT",
    "AI Equity — META": "META",
    "AI Infrastructure — AMD": "AMD",
    "Commodity — Gold (GC=F)": "GC=F",
    "Commodity — Crude Oil (CL=F)": "CL=F",
    "Custom ticker…": "__custom__",
}

preset = st.sidebar.selectbox("Asset", list(ASSET_PRESETS.keys()))
if ASSET_PRESETS[preset] == "__custom__":
    ticker = st.sidebar.text_input("Custom yfinance ticker", placeholder="e.g. AAPL")
else:
    ticker = ASSET_PRESETS[preset]

analysis_date = st.sidebar.date_input(
    "Analysis date",
    value=date.today() - timedelta(days=1),
    max_value=date.today() - timedelta(days=1),
    help="TradingAgents fetches historical data up to this date.",
)

st.sidebar.divider()
st.sidebar.subheader("🤖 Analyst Selection")

analyst_options = {
    "Market (technical indicators)": "market",
    "News sentiment": "news",
    "Fundamentals": "fundamentals",
    "Social media sentiment": "social",
}
selected_labels = st.sidebar.multiselect(
    "Active analysts",
    list(analyst_options.keys()),
    default=["Market (technical indicators)", "News sentiment", "Fundamentals"],
)
selected_analysts = [analyst_options[l] for l in selected_labels]

max_debate = st.sidebar.slider(
    "Bull/Bear debate rounds", min_value=1, max_value=3, value=1,
    help="More rounds = deeper analysis but slower and more expensive.",
)
max_risk = st.sidebar.slider(
    "Risk discussion rounds", min_value=1, max_value=3, value=1,
)

# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Asset: `{ticker}`  |  Date: `{analysis_date}`")

with col2:
    run_btn = st.button("▶ Run Analysis", type="primary", use_container_width=True)

st.divider()

if run_btn:
    if not ticker:
        st.error("Please enter a ticker symbol.")
        st.stop()

    if not api_key:
        st.error(f"Please enter your {api_key_label} in the sidebar.")
        st.stop()

    if not selected_analysts:
        st.error("Select at least one analyst.")
        st.stop()

    # Inject API key into environment for LangChain providers
    os.environ[api_key_label] = api_key

    # Also set common aliases expected by some LangChain integrations
    if provider == "anthropic":
        os.environ["ANTHROPIC_API_KEY"] = api_key
    elif provider == "openai":
        os.environ["OPENAI_API_KEY"] = api_key
    elif provider == "google":
        os.environ["GOOGLE_API_KEY"] = api_key

    config = {
        "llm_provider": provider,
        "deep_think_llm": deep_model,
        "quick_think_llm": quick_model,
        "max_debate_rounds": max_debate,
        "max_risk_discuss_rounds": max_risk,
        "data_vendors": {
            "core_stock_apis": "yfinance",
            "technical_indicators": "yfinance",
            "fundamental_data": "yfinance",
            "news_data": "yfinance",
        },
        "results_dir": "./trading_results",
    }

    progress = st.progress(0, text="Initialising agents…")

    try:
        from tradingagents.graph import TradingAgentsGraph

        progress.progress(10, text="Building agent graph…")
        ta = TradingAgentsGraph(
            selected_analysts=selected_analysts,
            debug=False,
            config=config,
        )

        progress.progress(30, text=f"Running multi-agent analysis for {ticker}…")
        final_state, signal = ta.propagate(
            ticker, analysis_date.strftime("%Y-%m-%d")
        )
        progress.progress(100, text="Analysis complete.")

        # -------------------------------------------------------------------
        # Display results
        # -------------------------------------------------------------------
        st.success("Analysis complete.")

        # Signal badge
        signal_upper = str(signal).upper() if signal else "UNKNOWN"
        if "BUY" in signal_upper or "LONG" in signal_upper:
            st.markdown(
                f"## 🟢 Signal: **{signal_upper}**",
            )
        elif "SELL" in signal_upper or "SHORT" in signal_upper or "BEAR" in signal_upper:
            st.markdown(f"## 🔴 Signal: **{signal_upper}**")
        else:
            st.markdown(f"## 🟡 Signal: **{signal_upper}**")

        st.divider()

        # Final trade decision (full text)
        decision_text = final_state.get("final_trade_decision", "")
        if decision_text:
            with st.expander("📋 Full Trade Decision (Portfolio Manager)", expanded=True):
                st.markdown(decision_text)

        # Individual analyst reports
        report_keys = {
            "market_report": "📈 Market Analyst Report",
            "news_report": "📰 News Analyst Report",
            "fundamentals_report": "🏦 Fundamentals Report",
            "sentiment_report": "💬 Social Sentiment Report",
        }
        for key, label in report_keys.items():
            content = final_state.get(key, "")
            if content:
                with st.expander(label):
                    st.markdown(content)

        # Bull vs Bear debate
        bull_history = final_state.get("bull_history", "")
        bear_history = final_state.get("bear_history", "")
        if bull_history or bear_history:
            with st.expander("⚔️ Bull vs Bear Debate"):
                b1, b2 = st.columns(2)
                with b1:
                    st.markdown("### 🐂 Bull Researcher")
                    st.markdown(bull_history or "_No output_")
                with b2:
                    st.markdown("### 🐻 Bear Researcher")
                    st.markdown(bear_history or "_No output_")

        # Risk debate
        risk_debate = final_state.get("risk_debate_state", {})
        if risk_debate:
            with st.expander("🛡️ Risk Committee Discussion"):
                for role, content in risk_debate.items():
                    if content:
                        st.markdown(f"**{role.replace('_', ' ').title()}**")
                        st.markdown(content)
                        st.divider()

        # Raw state inspector (debug)
        with st.expander("🔍 Raw agent state (debug)"):
            safe_state = {
                k: str(v)[:500] for k, v in final_state.items() if v
            }
            st.json(safe_state)

    except ImportError as e:
        st.error(f"TradingAgents import error: {e}\nRun `pip install git+https://github.com/TauricResearch/TradingAgents.git`")
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        with st.expander("Full traceback"):
            st.code(traceback.format_exc())

else:
    # Landing state
    st.info(
        "Configure your LLM provider and API key in the sidebar, select an asset, "
        "then click **▶ Run Analysis**."
    )

    st.subheader("How it works")
    st.markdown(
        """
The analysis pipeline runs these agents in sequence:

| Agent | Role |
|---|---|
| **Market Analyst** | Fetches OHLCV data via yfinance, computes RSI, MACD, Bollinger Bands, moving averages |
| **News Analyst** | Pulls recent headlines and scores sentiment |
| **Fundamentals Analyst** | Reads earnings, P/E, revenue growth (equities) or on-chain metrics (crypto) |
| **Social Analyst** | Aggregates social sentiment signals |
| **Bull Researcher** | Argues the long case using all reports |
| **Bear Researcher** | Argues the short/hold case |
| **Risk Committee** | Conservative, Neutral, and Aggressive debators weigh the risk |
| **Portfolio Manager** | Synthesises everything into a final BUY / SELL / HOLD signal |

**Data source:** `yfinance` — free, no API key required.
**LLM:** Your chosen provider (Anthropic Claude, OpenAI, Google Gemini, OpenRouter).
        """
    )

    st.subheader("Supported assets")
    st.markdown(
        """
| Sector | Example tickers |
|---|---|
| Crypto | `ETH-USD`, `BTC-USD`, `SOL-USD` |
| AI Equities | `NVDA`, `MSFT`, `META`, `GOOG` |
| AI Infrastructure | `AMD`, `INTC`, `SMCI` |
| Commodities | `GC=F` (Gold), `CL=F` (Crude Oil) |
        """
    )
