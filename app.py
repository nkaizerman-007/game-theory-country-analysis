"""
app.py — Interactive Streamlit dashboard for Game Theory Country Analysis.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data import (
    build_subfactor_df, build_factor_df, get_all_data, build_estimated_flags_df,
    REGIONS, REGION_COLORS, FACTOR_NAMES, SUBFACTOR_NAMES, DEFAULT_WEIGHTS,
    COUNTRY_GROUPS, ORIGINAL_COUNTRIES, EUROPE_COUNTRIES, ALL_COUNTRIES, ESTIMATED,
)
from analysis import (
    compute_weighted_utility, find_pareto_optimal, find_dominant_strategy,
    find_nash_equilibrium, pareto_frontier_2d, build_tradeoff_matrix,
    pairwise_tradeoff_summary, run_full_analysis,
)

# ── Page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Game Theory: Best Countries to Raise a Family",
    page_icon="🌍",
    layout="wide",
)

ISRAEL_COLOR = "#FF8C00"


# ── Load data (cached) ───────────────────────────────────────────────
@st.cache_data
def load_data():
    sf, ff = get_all_data()
    est = build_estimated_flags_df()
    return sf, ff, est

subfactor_df_all, factor_df_all, estimated_flags = load_data()

# ── Sidebar — Filters first, then weights ─────────────────────────────
st.sidebar.header("⚙️ Controls")

# --- Compare against (group filter) ---
st.sidebar.subheader("Compare Against")
group_choice = st.sidebar.radio(
    "Country set",
    options=list(COUNTRY_GROUPS.keys()),
    index=0,
    help="Choose which set of countries to include in the analysis",
)
group_countries = COUNTRY_GROUPS[group_choice]

# --- Country filter & highlight ---
st.sidebar.subheader("Country Filter")
selected_countries = st.sidebar.multiselect(
    "Select countries to display",
    options=group_countries,
    default=group_countries,
)

highlight = st.sidebar.selectbox(
    "Highlight Country",
    options=[c for c in selected_countries] if selected_countries else group_countries,
    index=([c for c in selected_countries].index("Israel")
           if "Israel" in selected_countries else 0),
)

st.sidebar.divider()

# --- Factor weights ---
st.sidebar.subheader("Factor Weights")
w1 = st.sidebar.slider("Freedom & Personal Choice (%)", 0, 100, 35)
w2 = st.sidebar.slider("Income & Career Growth (%)", 0, 100, 30)
w3 = st.sidebar.slider("Education Quality & Access (%)", 0, 100, 20)
w4 = st.sidebar.slider("Cost of Living & Affordability (%)", 0, 100, 15)

raw_total = w1 + w2 + w3 + w4
if raw_total == 0:
    raw_total = 1
weights = {
    "Freedom & Personal Choice": w1 / raw_total,
    "Income & Career Growth": w2 / raw_total,
    "Education Quality & Access": w3 / raw_total,
    "Cost of Living & Affordability": w4 / raw_total,
}
st.sidebar.caption(
    f"Normalized: "
    f"Freedom {weights['Freedom & Personal Choice']*100:.0f}% · "
    f"Income {weights['Income & Career Growth']*100:.0f}% · "
    f"Education {weights['Education Quality & Access']*100:.0f}% · "
    f"Affordability {weights['Cost of Living & Affordability']*100:.0f}%"
)

# ── Filter data ───────────────────────────────────────────────────────
factor_df = factor_df_all[factor_df_all["Country"].isin(selected_countries)].copy()
sf_filtered = subfactor_df_all[subfactor_df_all["Country"].isin(selected_countries)].copy()

if len(factor_df) == 0:
    st.warning("No countries selected. Use the sidebar to pick at least one country.")
    st.stop()

# ── Run analysis ──────────────────────────────────────────────────────
scored_df = compute_weighted_utility(factor_df, weights)
pareto_countries = find_pareto_optimal(factor_df)
dominant = find_dominant_strategy(factor_df)
nash = find_nash_equilibrium(factor_df)

# ── Title ─────────────────────────────────────────────────────────────
st.title("🌍 Game Theory Analysis: Best Countries to Raise a Family")
st.caption(f"Trade-off (Payoff) Framework — viewing **{group_choice}** ({len(selected_countries)} countries)")

# ── Summary box ───────────────────────────────────────────────────────
highlight_rank_row = scored_df[scored_df["Country"] == highlight]
highlight_rank = int(highlight_rank_row["Rank"].values[0]) if len(highlight_rank_row) else "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric("🏆 Dominant Strategy", dominant if dominant else "None")
col2.metric("⚖️ Pareto Optimal", f"{len(pareto_countries)} countries")
col3.metric(f"📍 {highlight} Rank", f"#{highlight_rank} / {len(scored_df)}")
col4.metric("📊 Nash Equilibrium", nash)

with st.expander("What do these metrics mean?"):
    st.markdown("""
- **Dominant Strategy** — Is there one country that beats ALL others in every single factor? (Almost never — real life has trade-offs.)
- **Pareto Optimal** — Countries where you can't improve one factor without losing ground on another. These are the "efficient" choices.
- **Your Country Rank** — Where your highlighted country lands in the overall weighted ranking.
- **Nash Equilibrium** — The most *balanced* country across all factors (lowest variance). Think of it as the "safest bet" — no single factor is amazing, but nothing is terrible either.
""")
    st.write("**Pareto-optimal countries:** " + ", ".join(pareto_countries))

st.divider()

# ── Chart 1: Radar Chart ─────────────────────────────────────────────
st.subheader("1 · Radar Chart — Factor Profiles")
st.markdown("""
**How to read this:** Each country is a shape with 4 corners — one per factor. The further a corner
reaches outward, the higher that country scores on that factor. A perfectly balanced country would
form a large, even diamond. A lopsided shape means the country is strong in some areas but weak in others.
Your highlighted country is shown in bold with a filled area so you can instantly compare its "shape" to others.
""")

# For readability, limit radar to top 8 + highlight + bottom 3 if many countries
if len(scored_df) > 15:
    top_n = scored_df.head(8)["Country"].tolist()
    bot_n = scored_df.tail(3)["Country"].tolist()
    radar_countries = list(dict.fromkeys(top_n + [highlight] + bot_n))
    st.caption(f"Showing top 8 + {highlight} + bottom 3 for readability. Full data in charts below.")
else:
    radar_countries = scored_df["Country"].tolist()

fig_radar = go.Figure()
for _, row in scored_df.iterrows():
    country = row["Country"]
    if country not in radar_countries:
        continue
    is_hl = country == highlight
    vals = [row[f] for f in FACTOR_NAMES] + [row[FACTOR_NAMES[0]]]
    region = REGIONS.get(country, "")
    color = ISRAEL_COLOR if is_hl else REGION_COLORS.get(region, "#888")
    fig_radar.add_trace(go.Scatterpolar(
        r=vals,
        theta=["Freedom", "Income", "Education", "Affordability", "Freedom"],
        name=country,
        line=dict(color=color, width=3 if is_hl else 1.2),
        opacity=1.0 if is_hl else 0.45,
        fill="toself" if is_hl else None,
        fillcolor=f"rgba(255,140,0,0.08)" if is_hl else None,
    ))

fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    height=500,
    margin=dict(t=30, b=30),
)
st.plotly_chart(fig_radar, use_container_width=True)

# ── Chart 2: Heatmap ─────────────────────────────────────────────────
st.subheader("2 · Heatmap — Sub-factor Scores")
st.markdown("""
**How to read this:** Each row is a country (sorted best-to-worst from top), each column is a specific
sub-factor (like PISA scores or housing affordability). **Darker blue = higher score, lighter = lower.**
Scan across a row to see a country's strengths and weaknesses. Scan down a column to see which countries
lead or lag on a specific metric. Hover over any cell to see the exact value.
Values marked with * in the data table are estimates.
""")

order = scored_df["Country"].tolist()
sub_cols = SUBFACTOR_NAMES
heat_data = sf_filtered.set_index("Country").loc[
    [c for c in order if c in sf_filtered["Country"].values], sub_cols
]

fig_heat = px.imshow(
    heat_data,
    text_auto=".0f",
    color_continuous_scale="YlGnBu",
    aspect="auto",
    labels=dict(color="Score"),
)
fig_heat.update_layout(height=max(450, len(heat_data) * 22), margin=dict(t=30, b=10))
fig_heat.update_xaxes(tickangle=45, tickfont_size=9)
st.plotly_chart(fig_heat, use_container_width=True)

# ── Chart 3: Pareto Frontier Scatter ──────────────────────────────────
st.subheader("3 · Pareto Frontier — Freedom vs. Income")
st.markdown("""
**How to read this:** This is the key trade-off chart. Each bubble is a country positioned by its
**Freedom score (X-axis)** and **Income score (Y-axis)**. The **bubble size** shows Education quality
(bigger = better), and the **color** shows Affordability (green = more affordable, red = expensive).

The **red dashed line** is the **Pareto frontier** — countries on or near this line represent the best
possible trade-off: you can't get more Freedom without giving up Income, or vice versa.
Countries far below/left of the line are "dominated" — another country beats them on both axes.
The ideal spot is the **top-right corner** (high Freedom + high Income), with a big green bubble
(great Education + affordable).
""")

x_col = "Freedom & Personal Choice"
y_col = "Income & Career Growth"
size_col = "Education Quality & Access"
color_col = "Cost of Living & Affordability"

fig_pareto = px.scatter(
    scored_df,
    x=x_col,
    y=y_col,
    size=size_col,
    color=color_col,
    color_continuous_scale="RdYlGn",
    hover_name="Country",
    text="Country",
    size_max=35,
    labels={color_col: "Affordability"},
)
fig_pareto.update_traces(textposition="top center", textfont_size=9)

frontier = pareto_frontier_2d(factor_df, x_col, y_col)
fig_pareto.add_trace(go.Scatter(
    x=frontier[x_col], y=frontier[y_col],
    mode="lines",
    line=dict(color="red", dash="dash", width=2),
    name="Pareto Frontier",
    showlegend=True,
))

fig_pareto.update_layout(height=550, margin=dict(t=30, b=30))
st.plotly_chart(fig_pareto, use_container_width=True)

# ── Chart 4: Ranked Bar Chart ────────────────────────────────────────
st.subheader("4 · Overall Ranking — Weighted Utility Score")
st.markdown("""
**How to read this:** The bottom line — every country's **final weighted score**, combining all four
factors using the weights you set in the sidebar. Longer bar = better overall.
Colors represent regions (blue = Nordics, green = Western Europe, red = North America,
purple = Asia-Pacific, teal = South America, gold = Southern Europe, steel blue = Central Europe,
grey = Balkans & Eastern, orange = Israel).
**Try moving the weight sliders** on the left to see how the ranking shifts when you prioritize
different factors — that's the game theory in action.
""")

bar_df = scored_df.sort_values("Weighted Score", ascending=True)
bar_colors = [
    ISRAEL_COLOR if c == highlight else REGION_COLORS.get(REGIONS.get(c, ""), "#888")
    for c in bar_df["Country"]
]

fig_bar = go.Figure(go.Bar(
    x=bar_df["Weighted Score"],
    y=bar_df["Country"],
    orientation="h",
    marker_color=bar_colors,
    text=bar_df["Weighted Score"].round(1),
    textposition="outside",
    textfont_size=10,
))
fig_bar.update_layout(
    height=max(400, len(bar_df) * 26),
    margin=dict(t=30, b=10, l=160),
    xaxis_title="Weighted Utility Score",
)
st.plotly_chart(fig_bar, use_container_width=True)

# ── Trade-off Matrix ─────────────────────────────────────────────────
st.subheader("5 · Trade-off Matrix — Gap vs Best-in-Class (Top 10)")
st.markdown("""
**How to read this:** For each of the top 10 countries, this table shows **how far behind the
best-in-class** they are on each factor. A value of **0.0 (green)** means that country *is*
the best among the top 10 for that factor. **Yellow** means a small gap (within 5 points).
**Red** means a significant gap — that's the price you pay (the "trade-off") for choosing
that country. No country is green across the board — that's why there's no dominant strategy.
""")
tradeoff = build_tradeoff_matrix(scored_df, top_n=min(10, len(scored_df)))

def color_delta(val):
    if isinstance(val, str):
        return ""
    if val == 0:
        return "background-color: #d4edda"
    elif val >= -5:
        return "background-color: #fff3cd"
    else:
        return "background-color: #f8d7da"

delta_cols = [c for c in tradeoff.columns if c.endswith("Δ")]
styled = tradeoff.style.map(color_delta, subset=delta_cols).format(
    {c: "{:.1f}" for c in delta_cols + ["Weighted Score"]}
)
st.dataframe(styled, use_container_width=True, hide_index=True)

st.divider()

# ── EDA Section ───────────────────────────────────────────────────────
with st.expander("📊 Exploratory Data Analysis (EDA)", expanded=False):
    eda_tab1, eda_tab2, eda_tab3, eda_tab4 = st.tabs([
        "Correlation Matrix", "Distributions", "Scatter Pairs", "Summary Stats"
    ])

    with eda_tab1:
        st.markdown("**Correlation between all sub-factors**")
        corr = sf_filtered[SUBFACTOR_NAMES].corr()
        fig_corr = px.imshow(
            corr, text_auto=".2f", color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1, aspect="auto",
        )
        fig_corr.update_layout(height=550)
        fig_corr.update_xaxes(tickangle=45, tickfont_size=8)
        st.plotly_chart(fig_corr, use_container_width=True)

    with eda_tab2:
        st.markdown("**Distribution of each factor across countries**")
        for f in FACTOR_NAMES:
            fig_hist = px.histogram(
                scored_df, x=f, nbins=12, title=f,
                color_discrete_sequence=["#4A90D9"],
            )
            fig_hist.update_layout(height=250, margin=dict(t=40, b=20))
            st.plotly_chart(fig_hist, use_container_width=True)

    with eda_tab3:
        st.markdown("**Scatter plots for each pair of factors**")
        from itertools import combinations
        for fa, fb in combinations(FACTOR_NAMES, 2):
            fig_sc = px.scatter(
                scored_df, x=fa, y=fb, hover_name="Country",
                text="Country", color="Region",
                color_discrete_map=REGION_COLORS,
            )
            fig_sc.update_traces(textposition="top center", textfont_size=8)
            fig_sc.update_layout(height=400, margin=dict(t=30, b=20))
            st.plotly_chart(fig_sc, use_container_width=True)

    with eda_tab4:
        st.markdown("**Summary statistics**")
        stats = sf_filtered[SUBFACTOR_NAMES].describe().T
        stats.columns = [c.capitalize() for c in stats.columns]
        st.dataframe(stats.style.format("{:.1f}"), use_container_width=True)

st.divider()

# ── Data Table with estimated flags ──────────────────────────────────
st.subheader("📋 Full Data Table")
st.caption("Values marked with * are estimates based on regional data (exact index data unavailable).")

display_df = scored_df.merge(sf_filtered, on=["Country", "Region"], how="left")

# Build a display version with asterisks on estimated values
display_show = display_df.copy()
for sf in SUBFACTOR_NAMES:
    if sf in display_show.columns:
        display_show[sf] = display_show.apply(
            lambda row: f"{row[sf]:.0f}*" if (row['Country'], sf) in ESTIMATED else f"{row[sf]:.0f}",
            axis=1,
        )

# Format numeric columns that aren't sub-factors (weighted score, rank, factors)
num_fmt = {}
for c in display_df.select_dtypes(include="number").columns:
    if c not in SUBFACTOR_NAMES:
        num_fmt[c] = "{:.1f}"

st.dataframe(display_show, use_container_width=True, hide_index=True)

csv = display_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download as CSV", csv, "country_analysis.csv", "text/csv")

# ── Game Theory Legend ────────────────────────────────────────────────
st.divider()
with st.expander("📖 Game Theory Concepts Explained"):
    st.markdown("""
| Concept | Meaning in This Analysis |
|---|---|
| **Payoff Matrix** | Each country is scored across multiple competing factors — the matrix of scores is the payoff table |
| **Pareto Efficiency** | Countries on the Pareto frontier: you can't improve one factor without losing another |
| **Dominant Strategy** | A country that beats all others in *every* factor (very rare in practice) |
| **Nash Equilibrium** | The most *balanced* choice — the country where shifting weight to any single factor wouldn't dramatically improve your outcome |
| **Weighted Utility** | Overall score = Σ(factor_score × weight), where weights reflect your family's priorities |
""")

# ── Data Sources ──────────────────────────────────────────────────────
st.divider()
st.subheader("📚 Data Sources")
st.markdown("""
All scores are normalized to a 0–100 scale. Data was collected from the most recent available edition
of each index. Values marked with * in the data table are **estimates** based on regional patterns
where exact index data was unavailable (primarily for smaller Balkan/Eastern European countries).

| Source | Used For | Sub-factors | Edition |
|--------|----------|-------------|---------|
| **[Human Freedom Index](https://www.cato.org/human-freedom-index)** — Cato Institute / Fraser Institute | Personal, economic, and civil liberties | Human Freedom Index | 2023 |
| **[Democracy Index](https://www.eiu.com/n/campaigns/democracy-index-2023/)** — Economist Intelligence Unit (EIU) | Quality of democratic governance | Democracy Index | 2023 |
| **[World Press Freedom Index](https://rsf.org/en/index)** — Reporters Without Borders (RSF) | Media freedom and journalist safety | Press Freedom | 2023 |
| **[OECD Better Life Index](https://www.oecdbetterlifeindex.org/)** — OECD | Household income, work-life balance | Household Income | 2023 |
| **[World Economic Outlook](https://www.imf.org/en/Publications/WEO)** — International Monetary Fund (IMF) | Economic output per person | GDP per Capita PPP | 2023 |
| **[Gender Wage Gap data](https://data.oecd.org/earnwage/gender-wage-gap.htm)** — OECD | Pay equity between genders | Gender Wage Equality | 2023 |
| **[Doing Business](https://archive.doingbusiness.org/)** — World Bank | Ease of starting/running a business | Ease of Business | 2020 (last edition) |
| **[PISA](https://www.oecd.org/pisa/)** — OECD Programme for International Student Assessment | K-12 education quality (Math, Reading, Science) | PISA Scores | 2022 |
| **[QS World University Rankings](https://www.topuniversities.com/world-university-rankings)** — Quacquarelli Symonds | Higher education quality per capita | University Density | 2024 |
| **[UNESCO Institute for Statistics](http://data.uis.unesco.org/)** — UNESCO / World Bank | Government investment in education | Education Spending | 2022 |
| **[Eurostat / OECD Adult Learning](https://ec.europa.eu/eurostat)** — Eurostat & OECD | Lifelong learning participation rates | Adult Education | 2023 |
| **[Cost of Living Index](https://www.numbeo.com/cost-of-living/rankings_by_country.jsp)** — Numbeo | Consumer prices relative to NYC baseline | Cost of Living (inverted) | 2024 |
| **[Property Price to Income Ratio](https://www.numbeo.com/property-investment/rankings_by_country.jsp)** — Numbeo / OECD | Housing affordability | Housing Affordability | 2024 |
| **[Purchasing Power Index](https://www.numbeo.com/cost-of-living/rankings_by_country.jsp)** — Numbeo | What local salaries can actually buy | Purchasing Power | 2024 |

**Note:** The World Bank *Doing Business* report was discontinued in 2021. The 2020 edition (last available) is used for the Ease of Business sub-factor.
Scores for countries not covered by a specific index (e.g., Montenegro in PISA) are estimated from regional peers and flagged.
""")
