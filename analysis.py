"""
analysis.py — Game theory analysis functions for country comparison.

Implements:
  - Weighted utility scoring
  - Pareto frontier detection
  - Dominant strategy identification
  - Nash equilibrium analogy (most balanced choice)
  - Trade-off (payoff) matrix generation
"""

import pandas as pd
import numpy as np
from itertools import combinations
from data import FACTOR_NAMES, DEFAULT_WEIGHTS


# ── Weighted Utility ──────────────────────────────────────────────────

def compute_weighted_utility(
    factor_df: pd.DataFrame,
    weights: dict | None = None,
) -> pd.DataFrame:
    """
    Add a 'Weighted Score' column: sum(factor_i × weight_i).
    Weights are auto-normalized to sum to 1.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    # Normalize weights
    total = sum(weights.values())
    w = {k: v / total for k, v in weights.items()}

    df = factor_df.copy()
    df["Weighted Score"] = sum(df[f] * w[f] for f in FACTOR_NAMES)
    df["Weighted Score"] = df["Weighted Score"].round(2)
    df["Rank"] = df["Weighted Score"].rank(ascending=False).astype(int)
    return df.sort_values("Weighted Score", ascending=False).reset_index(drop=True)


# ── Pareto Frontier ───────────────────────────────────────────────────

def find_pareto_optimal(factor_df: pd.DataFrame) -> list[str]:
    """
    Return list of Pareto-optimal countries: those where no other country
    is strictly better in ALL four factors simultaneously.
    A country is Pareto-dominated if another country is >= in all factors
    and strictly > in at least one.
    """
    countries = factor_df["Country"].tolist()
    scores = factor_df[FACTOR_NAMES].values  # (n_countries, 4)
    n = len(countries)
    dominated = set()

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            # Check if j dominates i
            if np.all(scores[j] >= scores[i]) and np.any(scores[j] > scores[i]):
                dominated.add(i)
                break

    return [countries[i] for i in range(n) if i not in dominated]


def pareto_frontier_2d(
    factor_df: pd.DataFrame,
    x_col: str = "Freedom & Personal Choice",
    y_col: str = "Income & Career Growth",
) -> pd.DataFrame:
    """
    Return a DataFrame of points on the 2-D Pareto frontier (for plotting).
    Sorted by x_col ascending.
    """
    df = factor_df[["Country", x_col, y_col]].copy()
    df = df.sort_values(x_col, ascending=True).reset_index(drop=True)

    frontier = []
    max_y = -np.inf
    # Sweep from right to left (highest x first) to collect frontier
    for _, row in df.sort_values(x_col, ascending=False).iterrows():
        if row[y_col] >= max_y:
            frontier.append(row)
            max_y = row[y_col]

    frontier_df = pd.DataFrame(frontier).sort_values(x_col).reset_index(drop=True)
    return frontier_df


# ── Dominant Strategy ─────────────────────────────────────────────────

def find_dominant_strategy(factor_df: pd.DataFrame) -> str | None:
    """
    A dominant strategy is a country that scores highest in ALL four factors.
    Returns the country name if one exists, else None.
    """
    best_per_factor = {}
    for f in FACTOR_NAMES:
        best_per_factor[f] = factor_df.loc[factor_df[f].idxmax(), "Country"]

    countries = set(best_per_factor.values())
    if len(countries) == 1:
        return countries.pop()
    return None


# ── Nash Equilibrium Analogy ──────────────────────────────────────────

def find_nash_equilibrium(factor_df: pd.DataFrame) -> str:
    """
    Nash equilibrium analogy: the country with the smallest variance
    across factors — the most *balanced* choice where switching emphasis
    to any single factor wouldn't dramatically help.
    Ties broken by higher mean score.
    """
    df = factor_df.copy()
    df["Factor Std"] = df[FACTOR_NAMES].std(axis=1)
    df["Factor Mean"] = df[FACTOR_NAMES].mean(axis=1)
    # Lowest std, then highest mean
    df = df.sort_values(["Factor Std", "Factor Mean"], ascending=[True, False])
    return df.iloc[0]["Country"]


# ── Trade-off Matrix ──────────────────────────────────────────────────

def build_tradeoff_matrix(scored_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    For the top-N countries (by Weighted Score), build a trade-off table
    showing for each factor how far above/below the best-in-class the
    country is.

    Returns a DataFrame: rows = countries, columns = factor trade-off strings.
    """
    df = scored_df.head(top_n).copy()

    # Best-in-class among these top_n
    best = {f: df[f].max() for f in FACTOR_NAMES}

    records = []
    for _, row in df.iterrows():
        rec = {"Country": row["Country"], "Weighted Score": row["Weighted Score"]}
        for f in FACTOR_NAMES:
            diff = row[f] - best[f]
            rec[f + " Δ"] = round(diff, 1)
        records.append(rec)
    return pd.DataFrame(records)


def pairwise_tradeoff_summary(scored_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    For each pair of factors among the top-N countries, identify the country
    that is best in factor A and show what it gives up in factor B.
    """
    df = scored_df.head(top_n).copy()
    rows = []
    for fa, fb in combinations(FACTOR_NAMES, 2):
        best_a_idx = df[fa].idxmax()
        best_a_country = df.loc[best_a_idx, "Country"]
        best_a_val = df.loc[best_a_idx, fa]
        trade_b_val = df.loc[best_a_idx, fb]
        best_b_val = df[fb].max()
        rows.append({
            "Factor A": fa,
            "Factor B": fb,
            "Best in A": best_a_country,
            "A Score": best_a_val,
            "B Score": trade_b_val,
            "B Best-in-class": best_b_val,
            "B Gap": round(trade_b_val - best_b_val, 1),
        })
    return pd.DataFrame(rows)


# ── Convenience: full analysis bundle ─────────────────────────────────

def run_full_analysis(factor_df: pd.DataFrame, weights: dict | None = None):
    """
    Run all analyses and return a dict with results.
    """
    scored = compute_weighted_utility(factor_df, weights)
    pareto = find_pareto_optimal(factor_df)
    dominant = find_dominant_strategy(factor_df)
    nash = find_nash_equilibrium(factor_df)
    tradeoff = build_tradeoff_matrix(scored)
    pairwise = pairwise_tradeoff_summary(scored)

    return {
        "scored_df": scored,
        "pareto_optimal": pareto,
        "dominant_strategy": dominant,
        "nash_equilibrium": nash,
        "tradeoff_matrix": tradeoff,
        "pairwise_tradeoffs": pairwise,
    }


if __name__ == "__main__":
    from data import build_factor_df
    ff = build_factor_df()
    results = run_full_analysis(ff)

    print("=== Weighted Scores ===")
    print(results["scored_df"][["Country", "Weighted Score", "Rank"]].to_string(index=False))
    print(f"\nPareto-optimal countries: {results['pareto_optimal']}")
    print(f"Dominant strategy: {results['dominant_strategy']}")
    print(f"Nash equilibrium (most balanced): {results['nash_equilibrium']}")
    print("\n=== Trade-off Matrix (top 10) ===")
    print(results["tradeoff_matrix"].to_string(index=False))
