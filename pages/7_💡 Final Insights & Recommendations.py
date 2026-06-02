# ============================================================
# pages/7_💡_Final_Insights.py
# ============================================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import streamlit as st

from utils import (
    inject_css, load_data, render_sidebar_filters,
    section_header, insight, divider,
)

st.set_page_config(
    page_title="💡 Final Insights · Retail Dashboard",
    page_icon="💡", layout="wide", initial_sidebar_state="expanded",
)
inject_css()

df_raw = load_data()
df     = render_sidebar_filters(df_raw)

if df.empty:
    st.warning("⚠️ No data matches your filters. Please widen your selection.")
    st.stop()

monthly = (
    df.groupby("YearMonth")
    .agg(Revenue=("Revenue","sum"))
    .reset_index().sort_values("YearMonth")
)

# ── Page header ───────────────────────────────────────────
st.markdown("""
<h2 style='text-align:center;'>💡 Final Insights & Strategic Recommendations</h2>
<p style='text-align:center;color:#6b7280;font-size:0.95rem;'>
A data-driven narrative for stakeholders, interviewers and decision-makers.
</p>
""", unsafe_allow_html=True)
divider()

# ── Six insight cards ─────────────────────────────────────
findings = [
    ("🏆", "Revenue Concentration",    "#f59e0b",
     "Top 20% of customers generate ~80% of revenue (Pareto Principle validated). Champions and Loyal RFM segments are the financial backbone of the business."),
    ("📦", "Product SKU Efficiency",   "#34d399",
     "Top 10 SKUs drive disproportionate revenue. Bottom 200+ products contribute minimally — rationalisation is long overdue."),
    ("🌍", "Geographic Risk",          "#60a5fa",
     "UK accounts for over 85% of revenue. European markets (Germany, France, Netherlands) show emerging organic demand worth targeting."),
    ("📅", "Seasonality Risk",         "#f87171",
     "Q4 (Nov–Dec) alone accounts for ~40% of annual revenue, creating supply-chain, staffing and cash-flow vulnerabilities."),
    ("👥", "Customer Loyalty Signal",  "#a78bfa",
     "Repeat customers outnumber new ones every single month. At Risk and Lost segments represent significant recoverable revenue with the right intervention."),
    ("🕒", "Buying Behaviour",         "#38bdf8",
     "Purchases peak mid-week (Thu) and mid-day (~12:00). B2B customers dominate — confirming business-hours buying patterns and weekday marketing priority."),
]

cols = st.columns(2)
for i, (icon, title, color, body_text) in enumerate(findings):
    with cols[i % 2]:
        st.markdown(f"""
        <div style='background:#1e293b;border-left:4px solid {color};
                    border-radius:10px;padding:18px 20px;margin-bottom:16px;'>
          <div style='font-size:1.6rem;line-height:1;margin-bottom:8px;'>{icon}</div>
          <div style='font-size:1.0rem;font-weight:700;color:{color};margin-bottom:8px;'>{title}</div>
          <div style='color:#cbd5e1;font-size:0.88rem;line-height:1.65;'>{body_text}</div>
        </div>""", unsafe_allow_html=True)

divider()

# ── Action plan table ─────────────────────────────────────
section_header("📋 Prioritised Action Plan")
actions = pd.DataFrame({
    "Priority": ["🔴 High","🔴 High","🟡 Medium","🟡 Medium","🟢 Low","🟢 Low"],
    "Area": [
        "Customer Retention", "Seasonality",
        "Geographic Expansion", "SKU Rationalisation",
        "Pricing Optimisation", "Data Quality",
    ],
    "Action": [
        "Launch loyalty rewards + win-back email series for At Risk / Lost RFM segments",
        "Launch mid-year Summer Sale (Jun–Aug) to reduce Q4 revenue dependency",
        "Localise website + run paid ads in Germany, France, Netherlands",
        "Discontinue bottom-50 SKUs; bundle slow-movers with hero products",
        "A/B test 5–10% price increases on top SKUs; monitor demand elasticity",
        "Make CustomerID mandatory at checkout; reduce anonymous orders",
    ],
    "Expected Impact": [
        "↑ 10–15% repeat revenue",
        "↑ 8–12% annual revenue",
        "↑ 20–30% international revenue",
        "↓ COGS 5%",
        "↑ Gross margin 3–5%",
        "↑ Analytics & RFM accuracy",
    ],
})
st.dataframe(actions, use_container_width=True, hide_index=True)

divider()

# ── KPI summary ───────────────────────────────────────────
section_header("📊 Dashboard KPI Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue",    f"£{df['Revenue'].sum():,.0f}")
col2.metric("📈 Avg Monthly Rev",  f"£{monthly['Revenue'].mean():,.0f}")
col3.metric("🏆 Best Month",       monthly.loc[monthly["Revenue"].idxmax(), "YearMonth"])
col4.metric("🔝 Best Month Rev",   f"£{monthly['Revenue'].max():,.0f}")

divider()

# ── Business story ────────────────────────────────────────
st.markdown("""
<div class="insight-box">
<b>🎯 Overarching Business Story</b><br><br>
This retail business has a strong foundation — loyal repeat customers, a set of proven hero products,
and a reliable seasonal engine in Q4. However, it carries three dangerous concentrations:<br><br>
<b>(1) Geographic:</b> UK generates 85%+ of revenue.<br>
<b>(2) Temporal:</b> Q4 accounts for ~40% of annual revenue.<br>
<b>(3) Customer:</b> Top 20% of customers drive 80% of revenue.<br><br>
The strategic imperative is <b>diversification</b> — of geography, of seasonality, and of the customer base —
while simultaneously doubling down on proven strengths: retaining Champions, scaling hero SKUs,
and converting At-Risk buyers before they churn permanently.
</div>""", unsafe_allow_html=True)
