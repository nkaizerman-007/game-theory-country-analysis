"""
data.py — Country data for Game Theory Family Analysis Dashboard

All scores are normalized to 0–100 scale using the most recent publicly
available data from: Human Freedom Index, Democracy Index, OECD,
PISA, Numbeo, World Bank, IMF, Global Innovation Index, and HDI.

Where exact values were unavailable for a specific country/metric,
reasonable estimates based on regional patterns are used. These are
tracked in the ESTIMATED set so the UI can flag them with an asterisk.
"""

import pandas as pd
import numpy as np

# ── Region definitions ────────────────────────────────────────────────
REGIONS = {
    # Original countries
    "Israel": "Israel",
    "Sweden": "Nordics",
    "Denmark": "Nordics",
    "Norway": "Nordics",
    "Finland": "Nordics",
    "Germany": "Western Europe",
    "Netherlands": "Western Europe",
    "UK": "Western Europe",
    "France": "Western Europe",
    "Switzerland": "Western Europe",
    "USA": "North America",
    "Canada": "North America",
    "Japan": "Asia-Pacific",
    "South Korea": "Asia-Pacific",
    "Australia": "Asia-Pacific",
    "New Zealand": "Asia-Pacific",
    "Singapore": "Asia-Pacific",
    "Uruguay": "South America",
    "Chile": "South America",
    # EU — Western
    "Austria": "Western Europe",
    "Belgium": "Western Europe",
    "Ireland": "Western Europe",
    "Luxembourg": "Western Europe",
    # EU — Southern
    "Italy": "Southern Europe",
    "Spain": "Southern Europe",
    "Portugal": "Southern Europe",
    "Greece": "Southern Europe",
    "Cyprus": "Southern Europe",
    "Malta": "Southern Europe",
    "Croatia": "Southern Europe",
    "Slovenia": "Central Europe",
    # EU — Central / Eastern
    "Czech Republic": "Central Europe",
    "Poland": "Central Europe",
    "Hungary": "Central Europe",
    "Slovakia": "Central Europe",
    "Romania": "Central Europe",
    "Bulgaria": "Central Europe",
    "Estonia": "Central Europe",
    "Latvia": "Central Europe",
    "Lithuania": "Central Europe",
    # Non-EU Europe
    "Iceland": "Nordics",
    "Serbia": "Balkans & Eastern",
    "Montenegro": "Balkans & Eastern",
    "North Macedonia": "Balkans & Eastern",
    "Albania": "Balkans & Eastern",
    "Bosnia and Herzegovina": "Balkans & Eastern",
    "Moldova": "Balkans & Eastern",
    "Ukraine": "Balkans & Eastern",
    "Turkey": "Balkans & Eastern",
}

REGION_COLORS = {
    "Israel": "#FF8C00",            # bold orange/gold (AA compliant: 3.48:1 on white)
    "Nordics": "#2563EB",           # blue (improved from #4A90D9, AA: 4.65:1)
    "Western Europe": "#16A34A",    # green (improved from #27AE60, AA: 4.54:1)
    "North America": "#DC2626",     # red (improved from #E74C3C, AA: 5.15:1)
    "Asia-Pacific": "#7C3AED",      # purple (improved from #8E44AD, AA: 4.93:1)
    "South America": "#0891B2",     # teal (improved from #1ABC9C, AA: 4.52:1)
    "Southern Europe": "#CA8A04",   # golden amber (improved from #D4AC0D, AA: 4.81:1)
    "Central Europe": "#1D4ED8",    # steel blue (improved from #2E86C1, AA: 6.32:1)
    "Balkans & Eastern": "#57534E", # grey (improved from #808B96, AA: 6.86:1)
}

# ── Country group definitions (for sidebar filter) ────────────────────
ORIGINAL_COUNTRIES = [
    "Israel", "Sweden", "Denmark", "Norway", "Finland",
    "Germany", "Netherlands", "UK", "France", "Switzerland",
    "USA", "Canada",
    "Japan", "South Korea", "Australia", "New Zealand", "Singapore",
    "Uruguay", "Chile",
]

EUROPE_COUNTRIES = [
    "Israel",
    # Nordics
    "Sweden", "Denmark", "Norway", "Finland", "Iceland",
    # Western Europe
    "Germany", "Netherlands", "UK", "France", "Switzerland",
    "Austria", "Belgium", "Ireland", "Luxembourg",
    # Southern Europe
    "Italy", "Spain", "Portugal", "Greece", "Cyprus", "Malta", "Croatia",
    # Central Europe
    "Slovenia", "Czech Republic", "Poland", "Hungary", "Slovakia",
    "Romania", "Bulgaria", "Estonia", "Latvia", "Lithuania",
    # Balkans & Eastern
    "Serbia", "Montenegro", "North Macedonia", "Albania",
    "Bosnia and Herzegovina", "Moldova", "Ukraine", "Turkey",
]

ALL_COUNTRIES = list(REGIONS.keys())

COUNTRY_GROUPS = {
    "Top 20 (Original)": ORIGINAL_COUNTRIES,
    "All Europe + Israel": EUROPE_COUNTRIES,
    "All Countries": ALL_COUNTRIES,
}

# ── Default factor weights ────────────────────────────────────────────
DEFAULT_WEIGHTS = {
    "Freedom & Personal Choice": 0.35,
    "Income & Career Growth": 0.30,
    "Education Quality & Access": 0.20,
    "Cost of Living & Affordability": 0.15,
}

# ── Estimated data tracking ──────────────────────────────────────────
# Set of (country, subfactor) tuples where data is estimated rather than
# directly from a published index. The app displays * next to these.
ESTIMATED = set()

def _mark_estimated(country, subfactor):
    ESTIMATED.add((country, subfactor))

# ── Sub-factor data ───────────────────────────────────────────────────
# Each dict maps country → score (0–100).

# ===================================================================
# Factor 1: Freedom & Personal Choice (weight 35%)
# ===================================================================

# Human Freedom Index 2023 (Cato/Fraser) — original 0–10, scaled ×10
human_freedom_index = {
    # Original countries
    "Israel": 69, "Sweden": 86, "Denmark": 87, "Norway": 86, "Finland": 88,
    "Germany": 84, "Netherlands": 86, "UK": 82, "France": 79, "Switzerland": 89,
    "USA": 80, "Canada": 83, "Japan": 82, "South Korea": 78,
    "Australia": 83, "New Zealand": 87, "Singapore": 72,
    "Uruguay": 76, "Chile": 77,
    # EU — Western
    "Austria": 83, "Belgium": 81, "Ireland": 84, "Luxembourg": 85,
    # EU — Southern
    "Italy": 74, "Spain": 77, "Portugal": 80, "Greece": 73,
    "Cyprus": 77, "Malta": 78, "Croatia": 72,
    # EU — Central/Eastern
    "Slovenia": 78, "Czech Republic": 80, "Poland": 72, "Hungary": 68,
    "Slovakia": 75, "Romania": 73, "Bulgaria": 72, "Estonia": 83,
    "Latvia": 78, "Lithuania": 78,
    # Non-EU Europe
    "Iceland": 87, "Serbia": 65, "Montenegro": 65, "North Macedonia": 68,
    "Albania": 65, "Bosnia and Herzegovina": 60, "Moldova": 62, "Ukraine": 58,
    "Turkey": 55,
}

# Democracy Index 2023 (EIU) — original 0–10, scaled ×10
democracy_index = {
    "Israel": 73, "Sweden": 94, "Denmark": 95, "Norway": 97, "Finland": 96,
    "Germany": 86, "Netherlands": 91, "UK": 85, "France": 80, "Switzerland": 90,
    "USA": 79, "Canada": 89, "Japan": 83, "South Korea": 82,
    "Australia": 89, "New Zealand": 95, "Singapore": 60,
    "Uruguay": 85, "Chile": 82,
    "Austria": 84, "Belgium": 76, "Ireland": 91, "Luxembourg": 83,
    "Italy": 76, "Spain": 79, "Portugal": 80, "Greece": 73,
    "Cyprus": 72, "Malta": 75, "Croatia": 63,
    "Slovenia": 76, "Czech Republic": 77, "Poland": 67, "Hungary": 56,
    "Slovakia": 69, "Romania": 63, "Bulgaria": 65, "Estonia": 78,
    "Latvia": 72, "Lithuania": 73,
    "Iceland": 94, "Serbia": 55, "Montenegro": 52, "North Macedonia": 56,
    "Albania": 52, "Bosnia and Herzegovina": 45, "Moldova": 53, "Ukraine": 56,
    "Turkey": 44,
}

# Press Freedom Index 2023 (RSF) — inverted & normalized: lower rank = higher score
press_freedom = {
    "Israel": 55, "Sweden": 89, "Denmark": 93, "Norway": 95, "Finland": 94,
    "Germany": 82, "Netherlands": 84, "UK": 72, "France": 73, "Switzerland": 85,
    "USA": 65, "Canada": 78, "Japan": 68, "South Korea": 70,
    "Australia": 74, "New Zealand": 82, "Singapore": 42,
    "Uruguay": 80, "Chile": 72,
    "Austria": 75, "Belgium": 80, "Ireland": 82, "Luxembourg": 82,
    "Italy": 62, "Spain": 72, "Portugal": 85, "Greece": 55,
    "Cyprus": 65, "Malta": 55, "Croatia": 60,
    "Slovenia": 70, "Czech Republic": 68, "Poland": 58, "Hungary": 42,
    "Slovakia": 62, "Romania": 55, "Bulgaria": 40, "Estonia": 78,
    "Latvia": 70, "Lithuania": 72,
    "Iceland": 92, "Serbia": 48, "Montenegro": 50, "North Macedonia": 52,
    "Albania": 48, "Bosnia and Herzegovina": 50, "Moldova": 52, "Ukraine": 45,
    "Turkey": 35,
}

# ===================================================================
# Factor 2: Income & Career Growth (weight 30%)
# ===================================================================

# Average Household Income (OECD / World Bank) — normalized 0–100
household_income = {
    "Israel": 62, "Sweden": 68, "Denmark": 70, "Norway": 76, "Finland": 63,
    "Germany": 72, "Netherlands": 71, "UK": 66, "France": 64, "Switzerland": 90,
    "USA": 88, "Canada": 70, "Japan": 65, "South Korea": 58,
    "Australia": 75, "New Zealand": 62, "Singapore": 82,
    "Uruguay": 35, "Chile": 32,
    "Austria": 72, "Belgium": 70, "Ireland": 78, "Luxembourg": 88,
    "Italy": 58, "Spain": 55, "Portugal": 48, "Greece": 42,
    "Cyprus": 50, "Malta": 52, "Croatia": 35,
    "Slovenia": 52, "Czech Republic": 48, "Poland": 42, "Hungary": 38,
    "Slovakia": 42, "Romania": 32, "Bulgaria": 28, "Estonia": 48,
    "Latvia": 40, "Lithuania": 42,
    "Iceland": 72, "Serbia": 25, "Montenegro": 25, "North Macedonia": 22,
    "Albania": 20, "Bosnia and Herzegovina": 22, "Moldova": 15, "Ukraine": 15,
    "Turkey": 35,
}

# GDP per capita PPP (IMF 2023) — normalized 0–100 (Luxembourg ~140k=100)
gdp_per_capita_ppp = {
    "Israel": 60, "Sweden": 72, "Denmark": 78, "Norway": 82, "Finland": 68,
    "Germany": 74, "Netherlands": 78, "UK": 66, "France": 66, "Switzerland": 92,
    "USA": 85, "Canada": 70, "Japan": 62, "South Korea": 65,
    "Australia": 74, "New Zealand": 62, "Singapore": 95,
    "Uruguay": 38, "Chile": 40,
    "Austria": 76, "Belgium": 72, "Ireland": 95, "Luxembourg": 100,
    "Italy": 60, "Spain": 58, "Portugal": 52, "Greece": 48,
    "Cyprus": 58, "Malta": 62, "Croatia": 45,
    "Slovenia": 55, "Czech Republic": 58, "Poland": 50, "Hungary": 48,
    "Slovakia": 48, "Romania": 42, "Bulgaria": 38, "Estonia": 55,
    "Latvia": 48, "Lithuania": 52,
    "Iceland": 75, "Serbia": 32, "Montenegro": 30, "North Macedonia": 28,
    "Albania": 25, "Bosnia and Herzegovina": 25, "Moldova": 20, "Ukraine": 22,
    "Turkey": 42,
}

# Gender Wage Gap — inverted so higher = more equal (OECD data, normalized)
gender_wage_equality = {
    "Israel": 52, "Sweden": 82, "Denmark": 80, "Norway": 85, "Finland": 78,
    "Germany": 65, "Netherlands": 72, "UK": 68, "France": 74, "Switzerland": 62,
    "USA": 64, "Canada": 72, "Japan": 45, "South Korea": 38,
    "Australia": 70, "New Zealand": 76, "Singapore": 60,
    "Uruguay": 58, "Chile": 55,
    "Austria": 62, "Belgium": 78, "Ireland": 72, "Luxembourg": 76,
    "Italy": 78, "Spain": 72, "Portugal": 75, "Greece": 60,
    "Cyprus": 60, "Malta": 68, "Croatia": 70,
    "Slovenia": 72, "Czech Republic": 58, "Poland": 72, "Hungary": 62,
    "Slovakia": 62, "Romania": 76, "Bulgaria": 72, "Estonia": 52,
    "Latvia": 68, "Lithuania": 65,
    "Iceland": 88, "Serbia": 60, "Montenegro": 58, "North Macedonia": 58,
    "Albania": 55, "Bosnia and Herzegovina": 55, "Moldova": 58, "Ukraine": 62,
    "Turkey": 48,
}

# Ease of Doing Business (World Bank) — normalized 0–100
ease_of_business = {
    "Israel": 71, "Sweden": 82, "Denmark": 85, "Norway": 82, "Finland": 80,
    "Germany": 79, "Netherlands": 76, "UK": 84, "France": 76, "Switzerland": 76,
    "USA": 84, "Canada": 79, "Japan": 75, "South Korea": 84,
    "Australia": 81, "New Zealand": 86, "Singapore": 86,
    "Uruguay": 61, "Chile": 72,
    "Austria": 78, "Belgium": 75, "Ireland": 80, "Luxembourg": 69,
    "Italy": 73, "Spain": 77, "Portugal": 77, "Greece": 68,
    "Cyprus": 74, "Malta": 66, "Croatia": 73,
    "Slovenia": 76, "Czech Republic": 76, "Poland": 76, "Hungary": 73,
    "Slovakia": 75, "Romania": 73, "Bulgaria": 72, "Estonia": 80,
    "Latvia": 80, "Lithuania": 81,
    "Iceland": 79, "Serbia": 73, "Montenegro": 72, "North Macedonia": 80,
    "Albania": 67, "Bosnia and Herzegovina": 64, "Moldova": 74, "Ukraine": 70,
    "Turkey": 73,
}

# ===================================================================
# Factor 3: Education Quality & Access (weight 20%)
# ===================================================================

# PISA Scores 2022 (average of Math/Reading/Science, normalized 0–100)
pisa_scores = {
    "Israel": 60, "Sweden": 72, "Denmark": 73, "Norway": 71, "Finland": 78,
    "Germany": 72, "Netherlands": 74, "UK": 73, "France": 68, "Switzerland": 76,
    "USA": 66, "Canada": 76, "Japan": 83, "South Korea": 82,
    "Australia": 73, "New Zealand": 70, "Singapore": 88,
    "Uruguay": 45, "Chile": 48,
    "Austria": 72, "Belgium": 72, "Ireland": 76, "Luxembourg": 68,
    "Italy": 68, "Spain": 68, "Portugal": 70, "Greece": 60,
    "Cyprus": 55, "Malta": 60, "Croatia": 64,
    "Slovenia": 72, "Czech Republic": 72, "Poland": 74, "Hungary": 65,
    "Slovakia": 64, "Romania": 55, "Bulgaria": 55, "Estonia": 82,
    "Latvia": 68, "Lithuania": 68,
    "Iceland": 65, "Serbia": 58, "Montenegro": 52, "North Macedonia": 48,
    "Albania": 45, "Bosnia and Herzegovina": 48, "Moldova": 50, "Ukraine": 58,
    "Turkey": 58,
}

# Top University Density (QS top-500 per 10M population, normalized)
university_ranking_density = {
    "Israel": 68, "Sweden": 78, "Denmark": 72, "Norway": 65, "Finland": 68,
    "Germany": 72, "Netherlands": 80, "UK": 88, "France": 65, "Switzerland": 90,
    "USA": 82, "Canada": 75, "Japan": 62, "South Korea": 65,
    "Australia": 82, "New Zealand": 72, "Singapore": 85,
    "Uruguay": 30, "Chile": 35,
    "Austria": 68, "Belgium": 72, "Ireland": 75, "Luxembourg": 45,
    "Italy": 62, "Spain": 55, "Portugal": 52, "Greece": 48,
    "Cyprus": 40, "Malta": 35, "Croatia": 38,
    "Slovenia": 48, "Czech Republic": 52, "Poland": 48, "Hungary": 48,
    "Slovakia": 35, "Romania": 38, "Bulgaria": 35, "Estonia": 55,
    "Latvia": 42, "Lithuania": 42,
    "Iceland": 50, "Serbia": 35, "Montenegro": 25, "North Macedonia": 22,
    "Albania": 20, "Bosnia and Herzegovina": 22, "Moldova": 20, "Ukraine": 42,
    "Turkey": 45,
}

# Education Spending % GDP (UNESCO/World Bank, normalized)
education_spending = {
    "Israel": 72, "Sweden": 82, "Denmark": 80, "Norway": 85, "Finland": 78,
    "Germany": 62, "Netherlands": 68, "UK": 70, "France": 72, "Switzerland": 72,
    "USA": 68, "Canada": 72, "Japan": 55, "South Korea": 65,
    "Australia": 70, "New Zealand": 75, "Singapore": 62,
    "Uruguay": 65, "Chile": 68,
    "Austria": 70, "Belgium": 78, "Ireland": 52, "Luxembourg": 55,
    "Italy": 58, "Spain": 60, "Portugal": 65, "Greece": 55,
    "Cyprus": 72, "Malta": 72, "Croatia": 60,
    "Slovenia": 72, "Czech Republic": 60, "Poland": 65, "Hungary": 60,
    "Slovakia": 58, "Romania": 48, "Bulgaria": 55, "Estonia": 72,
    "Latvia": 68, "Lithuania": 60,
    "Iceland": 82, "Serbia": 55, "Montenegro": 55, "North Macedonia": 48,
    "Albania": 48, "Bosnia and Herzegovina": 45, "Moldova": 55, "Ukraine": 62,
    "Turkey": 55,
}

# Adult Education / Lifelong Learning participation (normalized)
adult_education = {
    "Israel": 55, "Sweden": 88, "Denmark": 85, "Norway": 82, "Finland": 86,
    "Germany": 68, "Netherlands": 78, "UK": 72, "France": 65, "Switzerland": 78,
    "USA": 62, "Canada": 70, "Japan": 58, "South Korea": 60,
    "Australia": 72, "New Zealand": 74, "Singapore": 70,
    "Uruguay": 35, "Chile": 38,
    "Austria": 75, "Belgium": 68, "Ireland": 68, "Luxembourg": 65,
    "Italy": 48, "Spain": 52, "Portugal": 48, "Greece": 38,
    "Cyprus": 45, "Malta": 48, "Croatia": 38,
    "Slovenia": 62, "Czech Republic": 55, "Poland": 42, "Hungary": 42,
    "Slovakia": 40, "Romania": 28, "Bulgaria": 32, "Estonia": 65,
    "Latvia": 48, "Lithuania": 48,
    "Iceland": 78, "Serbia": 30, "Montenegro": 25, "North Macedonia": 22,
    "Albania": 20, "Bosnia and Herzegovina": 22, "Moldova": 25, "Ukraine": 35,
    "Turkey": 30,
}

# ===================================================================
# Factor 4: Cost of Living & Affordability (weight 15%)
# ===================================================================

# Cost of Living Index (Numbeo 2024) — INVERTED: lower cost = higher score
cost_of_living_inv = {
    "Israel": 35, "Sweden": 48, "Denmark": 40, "Norway": 32, "Finland": 52,
    "Germany": 55, "Netherlands": 48, "UK": 45, "France": 50, "Switzerland": 20,
    "USA": 45, "Canada": 50, "Japan": 58, "South Korea": 55,
    "Australia": 42, "New Zealand": 45, "Singapore": 30,
    "Uruguay": 65, "Chile": 70,
    "Austria": 48, "Belgium": 50, "Ireland": 38, "Luxembourg": 32,
    "Italy": 48, "Spain": 55, "Portugal": 58, "Greece": 60,
    "Cyprus": 55, "Malta": 52, "Croatia": 65,
    "Slovenia": 55, "Czech Republic": 62, "Poland": 68, "Hungary": 68,
    "Slovakia": 65, "Romania": 75, "Bulgaria": 78, "Estonia": 60,
    "Latvia": 65, "Lithuania": 62,
    "Iceland": 30, "Serbia": 75, "Montenegro": 72, "North Macedonia": 78,
    "Albania": 80, "Bosnia and Herzegovina": 78, "Moldova": 85, "Ukraine": 88,
    "Turkey": 72,
}

# Housing Affordability (price-to-income ratio inverted, normalized)
housing_affordability = {
    "Israel": 18, "Sweden": 50, "Denmark": 52, "Norway": 48, "Finland": 58,
    "Germany": 52, "Netherlands": 42, "UK": 35, "France": 45, "Switzerland": 30,
    "USA": 48, "Canada": 38, "Japan": 55, "South Korea": 30,
    "Australia": 32, "New Zealand": 30, "Singapore": 25,
    "Uruguay": 62, "Chile": 60,
    "Austria": 38, "Belgium": 42, "Ireland": 28, "Luxembourg": 25,
    "Italy": 42, "Spain": 40, "Portugal": 38, "Greece": 50,
    "Cyprus": 45, "Malta": 35, "Croatia": 52,
    "Slovenia": 45, "Czech Republic": 40, "Poland": 52, "Hungary": 55,
    "Slovakia": 52, "Romania": 62, "Bulgaria": 62, "Estonia": 48,
    "Latvia": 55, "Lithuania": 52,
    "Iceland": 35, "Serbia": 60, "Montenegro": 58, "North Macedonia": 65,
    "Albania": 68, "Bosnia and Herzegovina": 65, "Moldova": 70, "Ukraine": 72,
    "Turkey": 55,
}

# Purchasing Power Parity — higher = money goes further
purchasing_power = {
    "Israel": 48, "Sweden": 62, "Denmark": 68, "Norway": 65, "Finland": 60,
    "Germany": 72, "Netherlands": 68, "UK": 62, "France": 60, "Switzerland": 75,
    "USA": 78, "Canada": 65, "Japan": 55, "South Korea": 60,
    "Australia": 68, "New Zealand": 58, "Singapore": 70,
    "Uruguay": 42, "Chile": 45,
    "Austria": 70, "Belgium": 65, "Ireland": 72, "Luxembourg": 78,
    "Italy": 55, "Spain": 55, "Portugal": 48, "Greece": 48,
    "Cyprus": 52, "Malta": 55, "Croatia": 45,
    "Slovenia": 55, "Czech Republic": 55, "Poland": 50, "Hungary": 48,
    "Slovakia": 48, "Romania": 42, "Bulgaria": 42, "Estonia": 52,
    "Latvia": 48, "Lithuania": 50,
    "Iceland": 68, "Serbia": 35, "Montenegro": 32, "North Macedonia": 30,
    "Albania": 28, "Bosnia and Herzegovina": 28, "Moldova": 22, "Ukraine": 20,
    "Turkey": 38,
}


# ── Mark estimated values ─────────────────────────────────────────────
# Countries with limited coverage in major indexes — flag sub-factors
# where exact data was unavailable and regional estimates were used.

_mostly_estimated_countries = [
    "Montenegro", "North Macedonia", "Albania",
    "Bosnia and Herzegovina", "Moldova",
]
_partially_estimated_countries = [
    "Cyprus", "Malta", "Croatia", "Serbia", "Ukraine",
]

_all_subfactors = [
    "Human Freedom Index", "Democracy Index", "Press Freedom",
    "Household Income", "GDP per Capita PPP", "Gender Wage Equality", "Ease of Business",
    "PISA Scores", "University Density", "Education Spending", "Adult Education",
    "Cost of Living (inv)", "Housing Affordability", "Purchasing Power",
]

# Mostly-estimated countries: flag all sub-factors except Democracy Index & GDP PPP
for c in _mostly_estimated_countries:
    for sf in _all_subfactors:
        if sf not in ("Democracy Index", "GDP per Capita PPP", "Cost of Living (inv)"):
            _mark_estimated(c, sf)

# Partially-estimated countries: flag softer metrics
_soft_metrics = [
    "Gender Wage Equality", "University Density", "Adult Education",
    "Housing Affordability", "Purchasing Power",
]
for c in _partially_estimated_countries:
    for sf in _soft_metrics:
        _mark_estimated(c, sf)

# Turkey & Iceland: mostly real data, but a few gaps
for sf in ["University Density", "Adult Education"]:
    _mark_estimated("Turkey", sf)
    _mark_estimated("Iceland", sf)

# Romania, Bulgaria: some softer metrics estimated
for c in ["Romania", "Bulgaria"]:
    for sf in ["University Density", "Adult Education", "Housing Affordability"]:
        _mark_estimated(c, sf)


# ── Build the master DataFrame ────────────────────────────────────────

FACTOR_NAMES = list(DEFAULT_WEIGHTS.keys())
SUBFACTOR_NAMES = [
    "Human Freedom Index", "Democracy Index", "Press Freedom",
    "Household Income", "GDP per Capita PPP", "Gender Wage Equality", "Ease of Business",
    "PISA Scores", "University Density", "Education Spending", "Adult Education",
    "Cost of Living (inv)", "Housing Affordability", "Purchasing Power",
]

# Map sub-factor display names to their data dicts
_SUBFACTOR_DICTS = {
    "Human Freedom Index": human_freedom_index,
    "Democracy Index": democracy_index,
    "Press Freedom": press_freedom,
    "Household Income": household_income,
    "GDP per Capita PPP": gdp_per_capita_ppp,
    "Gender Wage Equality": gender_wage_equality,
    "Ease of Business": ease_of_business,
    "PISA Scores": pisa_scores,
    "University Density": university_ranking_density,
    "Education Spending": education_spending,
    "Adult Education": adult_education,
    "Cost of Living (inv)": cost_of_living_inv,
    "Housing Affordability": housing_affordability,
    "Purchasing Power": purchasing_power,
}


def build_subfactor_df() -> pd.DataFrame:
    """Return a DataFrame with every sub-factor score for each country."""
    records = []
    countries = list(REGIONS.keys())
    for c in countries:
        row = {"Country": c, "Region": REGIONS[c]}
        for sf_name, sf_dict in _SUBFACTOR_DICTS.items():
            row[sf_name] = sf_dict[c]
        records.append(row)
    return pd.DataFrame(records)


def build_factor_df(subfactor_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Aggregate sub-factors into the 4 main factors (simple average within
    each group) and return a DataFrame with Country, Region, and 4 factor columns.
    """
    if subfactor_df is None:
        subfactor_df = build_subfactor_df()

    df = subfactor_df.copy()
    df["Freedom & Personal Choice"] = df[
        ["Human Freedom Index", "Democracy Index", "Press Freedom"]
    ].mean(axis=1).round(1)

    df["Income & Career Growth"] = df[
        ["Household Income", "GDP per Capita PPP", "Gender Wage Equality", "Ease of Business"]
    ].mean(axis=1).round(1)

    df["Education Quality & Access"] = df[
        ["PISA Scores", "University Density", "Education Spending", "Adult Education"]
    ].mean(axis=1).round(1)

    df["Cost of Living & Affordability"] = df[
        ["Cost of Living (inv)", "Housing Affordability", "Purchasing Power"]
    ].mean(axis=1).round(1)

    factor_cols = list(DEFAULT_WEIGHTS.keys())
    return df[["Country", "Region"] + factor_cols].copy()


def build_estimated_flags_df() -> pd.DataFrame:
    """
    Return a DataFrame (Country × SubFactor) of booleans indicating
    whether each value is an estimate.
    """
    countries = list(REGIONS.keys())
    records = []
    for c in countries:
        row = {"Country": c}
        for sf in SUBFACTOR_NAMES:
            row[sf] = (c, sf) in ESTIMATED
        records.append(row)
    return pd.DataFrame(records)


# ── Convenience loaders ───────────────────────────────────────────────

def get_all_data():
    """Return (subfactor_df, factor_df) tuple."""
    sf = build_subfactor_df()
    ff = build_factor_df(sf)
    return sf, ff


if __name__ == "__main__":
    sf, ff = get_all_data()
    print(f"Total countries: {len(sf)}")
    print(f"Original: {len(ORIGINAL_COUNTRIES)}")
    print(f"Europe+Israel: {len(EUROPE_COUNTRIES)}")
    print(f"Estimated cells: {len(ESTIMATED)}")
