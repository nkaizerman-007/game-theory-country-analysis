# Game Theory Analysis: Best Countries to Raise a Family

A Python-based analytical dashboard using a **game theory trade-off framework** to evaluate which countries are best for raising a family where both parents can grow professionally, earn well, access education, and enjoy freedom of choice.

## What This Project Does

This project treats the question "Where should we raise our family?" as a **game theory problem**. Each country is a "strategy" a family can choose, and we evaluate the payoffs across competing factors:

- **Payoff Matrix**: 49 countries scored across 14 sub-factors (grouped into 4 main factors)
- **Pareto Efficiency**: Which countries represent the best possible trade-offs?
- **Dominant Strategy**: Is there a country that wins on everything? (Spoiler: no)
- **Nash Equilibrium**: Which country is the most balanced "safe bet"?
- **Weighted Utility**: An overall score based on customizable factor importance

## Factors Evaluated

| Factor | Default Weight | Sub-factors |
|--------|---------------|-------------|
| **Freedom & Personal Choice** | 35% | Human Freedom Index, Democracy Index, Press Freedom |
| **Income & Career Growth** | 30% | Household Income, GDP/capita PPP, Gender Wage Equality, Ease of Business |
| **Education Quality & Access** | 20% | PISA Scores, University Density, Education Spending, Adult Education |
| **Cost of Living & Affordability** | 15% | Cost of Living (inverted), Housing Affordability, Purchasing Power |

## Countries Included (49 total)

- **Israel** (highlighted in all charts)
- **Nordics**: Sweden, Denmark, Norway, Finland, Iceland
- **Western Europe**: Germany, Netherlands, UK, France, Switzerland, Austria, Belgium, Ireland, Luxembourg
- **Southern Europe**: Italy, Spain, Portugal, Greece, Cyprus, Malta, Croatia
- **Central Europe**: Slovenia, Czech Republic, Poland, Hungary, Slovakia, Romania, Bulgaria, Estonia, Latvia, Lithuania
- **Balkans & Eastern**: Serbia, Montenegro, North Macedonia, Albania, Bosnia and Herzegovina, Moldova, Ukraine, Turkey
- **North America**: USA, Canada
- **Asia-Pacific**: Japan, South Korea, Australia, New Zealand, Singapore
- **South America**: Uruguay, Chile

## Data Sources

All scores normalized to a 0–100 scale from the most recent available edition of each index.
Values marked with * in the data table are **estimates** based on regional patterns where exact index data was unavailable (primarily for smaller Balkan/Eastern European countries).

| Source | Organization | Used For | Sub-factor(s) | Edition |
|--------|-------------|----------|---------------|---------|
| [Human Freedom Index](https://www.cato.org/human-freedom-index) | Cato Institute / Fraser Institute | Personal, economic, and civil liberties | Human Freedom Index | 2023 |
| [Democracy Index](https://www.eiu.com/n/campaigns/democracy-index-2023/) | Economist Intelligence Unit (EIU) | Quality of democratic governance | Democracy Index | 2023 |
| [World Press Freedom Index](https://rsf.org/en/index) | Reporters Without Borders (RSF) | Media freedom and journalist safety | Press Freedom | 2023 |
| [OECD Better Life Index](https://www.oecdbetterlifeindex.org/) | OECD | Household income and well-being | Household Income | 2023 |
| [World Economic Outlook](https://www.imf.org/en/Publications/WEO) | International Monetary Fund (IMF) | Economic output per person | GDP per Capita PPP | 2023 |
| [Gender Wage Gap data](https://data.oecd.org/earnwage/gender-wage-gap.htm) | OECD | Pay equity between genders | Gender Wage Equality | 2023 |
| [Doing Business](https://archive.doingbusiness.org/) | World Bank | Ease of starting/running a business | Ease of Business | 2020 (last edition)* |
| [PISA](https://www.oecd.org/pisa/) | OECD | K-12 education quality (Math, Reading, Science) | PISA Scores | 2022 |
| [QS World University Rankings](https://www.topuniversities.com/world-university-rankings) | Quacquarelli Symonds | Higher education quality per capita | University Density | 2024 |
| [UNESCO Institute for Statistics](http://data.uis.unesco.org/) | UNESCO / World Bank | Government investment in education | Education Spending | 2022 |
| [Eurostat / OECD Adult Learning](https://ec.europa.eu/eurostat) | Eurostat & OECD | Lifelong learning participation rates | Adult Education | 2023 |
| [Cost of Living Index](https://www.numbeo.com/cost-of-living/rankings_by_country.jsp) | Numbeo | Consumer prices relative to NYC baseline | Cost of Living (inverted) | 2024 |
| [Property Price to Income Ratio](https://www.numbeo.com/property-investment/rankings_by_country.jsp) | Numbeo / OECD | Housing affordability | Housing Affordability | 2024 |
| [Purchasing Power Index](https://www.numbeo.com/cost-of-living/rankings_by_country.jsp) | Numbeo | What local salaries can actually buy | Purchasing Power | 2024 |

*The World Bank Doing Business report was discontinued in 2021. The 2020 edition (last available) is used.

## Outputs

### 1. Static Dashboard
- `dashboard.png` (300 DPI) and `dashboard.pdf`
- 5 panels: Radar chart, Heatmap, Pareto scatter, Ranked bars, Trade-off matrix
- Generated by running: `python static_dashboard.py`

### 2. Interactive Streamlit App
- Full interactive dashboard with Plotly charts
- Adjustable weight sliders to explore different priorities
- Country filter with 3 preset groups (Original 20, All Europe, All Countries)
- EDA section with correlations, distributions, and scatter pairs
- Downloadable CSV data
- Run with: `streamlit run app.py`

## Setup

```bash
pip install seaborn matplotlib pandas numpy streamlit plotly
```

## Usage

### Generate static dashboard:
```bash
python static_dashboard.py
```

### Launch interactive app:
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

## Project Structure

```
analysis_project/
  data.py               # Country data (49 countries, 14 sub-factors)
  analysis.py           # Game theory analysis functions
  static_dashboard.py   # Static Matplotlib/Seaborn dashboard generator
  app.py                # Interactive Streamlit app
  dashboard.png         # Generated static dashboard (PNG)
  dashboard.pdf         # Generated static dashboard (PDF)
  process.md            # Development process log
  readme.md             # This file
```

## Key Findings (Default Weights)

- **Top countries**: Norway, Denmark, Sweden consistently lead
- **Israel** ranks low overall, primarily due to housing affordability (worst in dataset at 18/100) and moderate freedom scores
- **No dominant strategy exists** — every country involves trade-offs
- **Japan** emerges as the Nash Equilibrium — the most balanced choice across all factors
- Adjusting weights significantly shifts rankings — try maxing affordability to see Eastern European countries rise
