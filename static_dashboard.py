"""
static_dashboard.py — Generate a multi-panel static dashboard.

Outputs:
  dashboard.png  (300 DPI)
  dashboard.pdf

Panels:
  1. Radar / Spider chart (top countries + Israel)
  2. Heatmap (countries × sub-factors)
  3. Pareto frontier scatter plot
  4. Ranked bar chart (weighted utility)
  5. Trade-off payoff table (top 10)
"""

import matplotlib
matplotlib.use("Agg")  # non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import seaborn as sns
import numpy as np
import pandas as pd
from math import pi

from data import (
    build_subfactor_df, build_factor_df, get_all_data,
    REGIONS, REGION_COLORS, FACTOR_NAMES, DEFAULT_WEIGHTS,
)
from analysis import (
    run_full_analysis, pareto_frontier_2d,
    find_pareto_optimal, find_nash_equilibrium, find_dominant_strategy,
)

# ── Style setup ───────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=0.85)
ISRAEL_COLOR = "#FF8C00"
HIGHLIGHT_ALPHA = 1.0
OTHER_ALPHA = 0.45


def _country_color(country: str) -> str:
    return REGION_COLORS.get(REGIONS.get(country, ""), "#888888")


# ── Panel 1: Radar Chart ─────────────────────────────────────────────

def _draw_radar(ax, factor_df, scored_df):
    """Radar chart: top 5 + Israel + bottom 2."""
    top5 = scored_df.head(5)["Country"].tolist()
    bottom2 = scored_df.tail(2)["Country"].tolist()
    show = list(dict.fromkeys(top5 + ["Israel"] + bottom2))  # deduplicate, keep order

    angles = [n / len(FACTOR_NAMES) * 2 * pi for n in range(len(FACTOR_NAMES))]
    angles += angles[:1]  # close the loop

    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(0)

    ax.set_xticks(angles[:-1])
    short_labels = ["Freedom", "Income", "Education", "Affordability"]
    ax.set_xticklabels(short_labels, fontsize=8)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=6, color="grey")

    for country in show:
        row = factor_df[factor_df["Country"] == country].iloc[0]
        values = [row[f] for f in FACTOR_NAMES] + [row[FACTOR_NAMES[0]]]
        is_israel = country == "Israel"
        color = ISRAEL_COLOR if is_israel else _country_color(country)
        lw = 2.5 if is_israel else 1.2
        alpha = HIGHLIGHT_ALPHA if is_israel else OTHER_ALPHA
        ax.plot(angles, values, linewidth=lw, linestyle="solid", label=country,
                color=color, alpha=alpha)
        ax.fill(angles, values, alpha=0.08 if is_israel else 0.03, color=color)

    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=6,
              frameon=True, framealpha=0.9)
    ax.set_title("Radar: Factor Profiles", fontsize=10, fontweight="bold", pad=20)


# ── Panel 2: Heatmap ─────────────────────────────────────────────────

def _draw_heatmap(ax, subfactor_df, scored_df):
    """Heatmap of countries (sorted by overall score) × sub-factors."""
    order = scored_df["Country"].tolist()
    sub_cols = [c for c in subfactor_df.columns if c not in ("Country", "Region")]
    df = subfactor_df.set_index("Country").loc[order, sub_cols]

    sns.heatmap(
        df, ax=ax, cmap="YlGnBu", annot=True, fmt=".0f",
        annot_kws={"size": 5.5}, linewidths=0.4, linecolor="white",
        cbar_kws={"shrink": 0.6, "label": "Score (0–100)"},
    )
    ax.set_title("Heatmap: Sub-factor Scores (sorted by overall rank)", fontsize=10, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis="x", rotation=45, labelsize=6)
    ax.tick_params(axis="y", labelsize=7)

    # Highlight Israel row label
    for label in ax.get_yticklabels():
        if label.get_text() == "Israel":
            label.set_color(ISRAEL_COLOR)
            label.set_fontweight("bold")


# ── Panel 3: Pareto Frontier Scatter ─────────────────────────────────

def _draw_pareto_scatter(ax, factor_df):
    """
    X = Freedom, Y = Income, size = Education, color = Affordability.
    Pareto frontier line drawn.
    """
    x_col, y_col = "Freedom & Personal Choice", "Income & Career Growth"
    size_col = "Education Quality & Access"
    color_col = "Cost of Living & Affordability"

    x = factor_df[x_col]
    y = factor_df[y_col]
    sizes = factor_df[size_col]
    colors = factor_df[color_col]

    scatter = ax.scatter(
        x, y,
        s=sizes * 3,
        c=colors,
        cmap="RdYlGn",
        edgecolors="grey",
        linewidths=0.5,
        alpha=0.85,
        zorder=3,
    )

    # Labels
    for _, row in factor_df.iterrows():
        bold = row["Country"] == "Israel"
        ax.annotate(
            row["Country"],
            (row[x_col], row[y_col]),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=6,
            fontweight="bold" if bold else "normal",
            color=ISRAEL_COLOR if bold else "black",
        )

    # Pareto frontier line
    frontier = pareto_frontier_2d(factor_df, x_col, y_col)
    ax.plot(frontier[x_col], frontier[y_col], "r--", linewidth=1.5, alpha=0.7,
            label="Pareto Frontier", zorder=2)

    ax.set_xlabel("Freedom & Personal Choice", fontsize=8)
    ax.set_ylabel("Income & Career Growth", fontsize=8)
    ax.set_title("Pareto Frontier: Freedom vs. Income", fontsize=10, fontweight="bold")

    cbar = plt.colorbar(scatter, ax=ax, shrink=0.7)
    cbar.set_label("Affordability (greener = cheaper)", fontsize=7)

    # Size legend
    for sz_val, label in [(40, "Low Edu"), (65, "Mid"), (85, "High Edu")]:
        ax.scatter([], [], s=sz_val * 3, c="grey", alpha=0.5, label=f"Education ≈ {sz_val}")
    ax.legend(fontsize=5.5, loc="lower right", framealpha=0.9)


# ── Panel 4: Ranked Bar Chart ────────────────────────────────────────

def _draw_ranked_bars(ax, scored_df):
    """Horizontal bars sorted by weighted score, colored by region."""
    df = scored_df.sort_values("Weighted Score", ascending=True)  # bottom-to-top
    colors = [REGION_COLORS.get(REGIONS.get(c, ""), "#888") for c in df["Country"]]

    bars = ax.barh(df["Country"], df["Weighted Score"], color=colors, edgecolor="white",
                   linewidth=0.5)

    # Highlight Israel bar border
    for bar, country in zip(bars, df["Country"]):
        if country == "Israel":
            bar.set_edgecolor(ISRAEL_COLOR)
            bar.set_linewidth(2.5)

    ax.set_xlabel("Weighted Utility Score", fontsize=8)
    ax.set_title("Overall Ranking (Weighted Utility)", fontsize=10, fontweight="bold")
    ax.tick_params(axis="y", labelsize=7)

    # Annotate values
    for bar, val in zip(bars, df["Weighted Score"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", fontsize=6)

    # Region legend
    handles = [mpatches.Patch(color=c, label=r) for r, c in REGION_COLORS.items()]
    ax.legend(handles=handles, fontsize=5.5, loc="lower right", framealpha=0.9)

    # Bold Israel y-label
    for label in ax.get_yticklabels():
        if label.get_text() == "Israel":
            label.set_color(ISRAEL_COLOR)
            label.set_fontweight("bold")


# ── Panel 5: Trade-off Table ─────────────────────────────────────────

def _draw_tradeoff_table(ax, tradeoff_df):
    """Render trade-off matrix as a colored table."""
    ax.axis("off")
    cols = ["Country"] + [c for c in tradeoff_df.columns if c.endswith("Δ")]
    display_df = tradeoff_df[cols].copy()

    # Shorten column names for display
    short = {c: c.replace(" & Personal Choice", "").replace(" & Career Growth", "")
                  .replace(" Quality & Access", "").replace(" & Affordability", "")
                  .replace(" Δ", " Δ")
             for c in cols}
    display_df = display_df.rename(columns=short)

    cell_text = display_df.values.tolist()
    col_labels = display_df.columns.tolist()

    # Color: green if 0, red shading for negative
    cell_colors = []
    for row in cell_text:
        row_colors = []
        for j, val in enumerate(row):
            if j == 0:
                row_colors.append("#f7f7f7")
            else:
                v = float(val)
                if v == 0:
                    row_colors.append("#d4edda")
                elif v >= -5:
                    row_colors.append("#fff3cd")
                else:
                    row_colors.append("#f8d7da")
            row_colors.append
        cell_colors.append(row_colors)

    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        cellColours=cell_colors,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(6)
    table.scale(1, 1.3)

    # Header styling
    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_text_props(fontweight="bold")
            cell.set_facecolor("#d6e9f8")
        cell.set_edgecolor("white")

    ax.set_title("Trade-off Matrix: Δ vs. Best-in-Class (Top 10)",
                 fontsize=10, fontweight="bold", pad=12)


# ── Assemble the dashboard ───────────────────────────────────────────

def generate_dashboard():
    subfactor_df, factor_df = get_all_data()
    results = run_full_analysis(factor_df)
    scored = results["scored_df"]
    tradeoff = results["tradeoff_matrix"]

    # Layout: 3 rows
    #   Row 1: Radar (polar) | Pareto scatter
    #   Row 2: Heatmap (wide)
    #   Row 3: Bar chart | Trade-off table
    fig = plt.figure(figsize=(22, 28))

    # Title
    weight_str = "  |  ".join(f"{k}: {int(v*100)}%" for k, v in DEFAULT_WEIGHTS.items())
    fig.suptitle(
        "Game Theory Analysis: Best Countries to Raise a Family\n(Trade-off Framework)",
        fontsize=18, fontweight="bold", y=0.98,
    )
    fig.text(0.5, 0.96, f"Weights: {weight_str}", ha="center", fontsize=11, color="grey")

    # Summary text
    pareto_str = ", ".join(results["pareto_optimal"])
    dominant_str = results["dominant_strategy"] or "None (no country dominates all factors)"
    nash_str = results["nash_equilibrium"]
    israel_rank = scored[scored["Country"] == "Israel"]["Rank"].values[0]
    summary = (
        f"Dominant Strategy: {dominant_str}    |    "
        f"Pareto-Optimal: {pareto_str}\n"
        f"Nash Equilibrium (most balanced): {nash_str}    |    "
        f"Israel Ranking: #{israel_rank} out of {len(scored)}"
    )
    fig.text(0.5, 0.945, summary, ha="center", fontsize=9, color="#333",
             style="italic",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#fffbe6", edgecolor="#ccc"))

    # Row 1
    ax_radar = fig.add_subplot(3, 2, 1, polar=True)
    _draw_radar(ax_radar, factor_df, scored)

    ax_pareto = fig.add_subplot(3, 2, 2)
    _draw_pareto_scatter(ax_pareto, factor_df)

    # Row 2: heatmap (spans full width)
    ax_heat = fig.add_subplot(3, 1, 2)
    _draw_heatmap(ax_heat, subfactor_df, scored)

    # Row 3
    ax_bars = fig.add_subplot(3, 2, 5)
    _draw_ranked_bars(ax_bars, scored)

    ax_table = fig.add_subplot(3, 2, 6)
    _draw_tradeoff_table(ax_table, tradeoff)

    # Game theory legend
    legend_text = (
        "Game Theory Concepts:\n"
        "• Payoff Matrix — each country scored across multiple competing factors\n"
        "• Pareto Efficiency — countries where improving one factor requires sacrificing another\n"
        "• Dominant Strategy — a country outperforming all others in every factor (rare)\n"
        "• Nash Equilibrium — the most balanced choice; switching focus wouldn't improve utility\n"
        "• Weighted Utility — overall score = Σ(factor × weight)"
    )
    fig.text(0.02, 0.005, legend_text, fontsize=7, verticalalignment="bottom",
             fontfamily="monospace", color="#555",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#f0f0f0", edgecolor="#ccc"))

    plt.tight_layout(rect=[0, 0.04, 1, 0.935])

    fig.savefig("dashboard.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig("dashboard.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Saved dashboard.png and dashboard.pdf")


if __name__ == "__main__":
    generate_dashboard()
