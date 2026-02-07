# Process Log — Game Theory Country Analysis Dashboard

## Step 1: Project Setup & Data Module (`data.py`)
- Created `data.py` with hardcoded, normalized (0–100) scores for 19 countries across 14 sub-factors
- Data sourced from: Human Freedom Index (Cato/Fraser), Democracy Index (EIU), Press Freedom Index (RSF), OECD Better Life Index, IMF GDP PPP data, World Bank Ease of Business, PISA 2022, QS University Rankings, UNESCO education spending, Numbeo cost of living
- Defined 4 main factors: Freedom & Personal Choice (35%), Income & Career Growth (30%), Education Quality & Access (20%), Cost of Living & Affordability (15%)
- Organized countries into regions with distinct color coding

## Step 2: Analysis Module (`analysis.py`)
- Implemented game theory analysis functions:
  - **Weighted utility scoring**: sum of factor × weight, with auto-normalizing weights
  - **Pareto frontier detection**: identifies countries where no other country dominates on all factors simultaneously
  - **Dominant strategy check**: looks for a country that leads in ALL factors (none found — real life has trade-offs)
  - **Nash equilibrium analogy**: finds the most balanced country (lowest variance across factors)
  - **Trade-off matrix**: shows gap vs. best-in-class for top 10 countries
  - **Pairwise trade-off summary**: for each pair of factors, shows what the best-in-A country gives up in B

## Step 3: Static Dashboard (`static_dashboard.py`)
- Built a multi-panel Matplotlib/Seaborn figure with 5 subplots:
  1. Radar/spider chart — top 5 + Israel + bottom 2
  2. Heatmap — all countries × 14 sub-factors, sorted by overall rank
  3. Pareto frontier scatter — Freedom vs Income, bubble size = Education, color = Affordability
  4. Ranked horizontal bar chart — weighted utility scores, color-coded by region
  5. Trade-off table — color-coded deltas vs best-in-class
- Output saved as `dashboard.png` (300 DPI) and `dashboard.pdf`
- Israel highlighted in bold orange throughout

## Step 4: Interactive Streamlit App (`app.py`)
- Built full interactive dashboard with Plotly charts
- Sidebar controls: weight sliders (auto-normalize to 100%), country multi-select, highlight picker
- All 5 chart types from static dashboard, now interactive (hover, zoom, etc.)
- Summary metrics box: Dominant Strategy, Pareto Optimal count, Israel Rank, Nash Equilibrium
- EDA section with: correlation matrix, factor distributions, scatter pairs, summary statistics
- Full data table with CSV download
- Game theory concepts explanation section
- Added "How to read this" explanations before every chart

## Step 5: Expanded European Data
- Added 30 European countries (total now 49):
  - **EU Western**: Austria, Belgium, Ireland, Luxembourg
  - **EU Southern**: Italy, Spain, Portugal, Greece, Cyprus, Malta, Croatia
  - **EU Central/Eastern**: Slovenia, Czech Republic, Poland, Hungary, Slovakia, Romania, Bulgaria, Estonia, Latvia, Lithuania
  - **Non-EU Europe**: Iceland, Serbia, Montenegro, North Macedonia, Albania, Bosnia and Herzegovina, Moldova, Ukraine, Turkey
- All 14 sub-factors populated with real index data where available
- Estimated values tracked in `ESTIMATED` set and flagged with * in the data table
- Countries with most estimates: Montenegro, North Macedonia, Albania, Bosnia and Herzegovina, Moldova (smaller countries with limited index coverage)

## Step 6: Sidebar Filter — "Compare Against"
- Added 3-option radio button at top of sidebar:
  - **Top 20 (Original)** — the original 19 countries
  - **All Europe + Israel** — 39 European countries + Israel
  - **All Countries** — all 49 countries
- Filter updates ALL charts, rankings, Pareto analysis, Nash equilibrium, and summary metrics
- Sidebar reordered: Compare Against → Country Filter → Highlight Country → Factor Weights

## Step 7: Sidebar Reorder
- Moved Country Filter and Highlight Country above Factor Weights per user request
- Added divider between filter section and weight section for clarity

## Step 8: Documentation
- Created `process.md` (this file) documenting every step
- Created `readme.md` with project context, setup instructions, and usage guide

## Step 9: Data Sources Section in App
- Added a full "Data Sources" section at the bottom of the Streamlit app (below Game Theory Concepts)
- Lists every index used with: source name, organization, what it measures, which sub-factor(s) it feeds, edition year, and a link to the original source
- Includes a note about the Doing Business discontinuation (2021) and how estimated values are handled
- Updated `readme.md` with the same detailed source table and links
- Updated `process.md` (this file) to reflect the change

---

## Key Results (Default Weights: Freedom 35%, Income 30%, Education 20%, Affordability 15%)

### Original 19 Countries
- **Top 3**: Norway, Denmark, Sweden
- **Israel Rank**: #19/19 (last — primarily due to affordability crisis)
- **Nash Equilibrium**: Japan (most balanced)
- **Dominant Strategy**: None

### All 49 Countries
- **Top 5**: Norway, Denmark, Sweden, Finland, Switzerland
- **Israel Rank**: #36/49
- **Pareto Optimal**: 11 countries
- Israel's biggest weakness: Housing Affordability (18/100) — worst in dataset
