# T1 Project Plan — Finance AI Mini Demo

## Project Goal

Develop a clear and reproducible research workflow for comparing three familiar asset classes represented by ETFs: `SPY` (US equities), `TLT` (long-term US Treasury bonds), and `GLD` (gold). The plan starts with a written project plan in T1 and is intended to guide a bounded, verifiable analysis in later tutorials.

## Available Data

`data/etf_snapshot.csv` is a small, fixed dataset with one row per ETF and the following columns (see `data/data_dictionary.md`):

- `ticker` — short identifier for the illustrative ETF
- `asset_class` — broad type of asset represented by the ETF
- `expected_return_pct` — illustrative annual return assumption
- `volatility_pct` — illustrative annual variability assumption
- `max_drawdown_pct` — illustrative largest peak-to-trough loss (negative values represent losses)
- `expense_ratio_pct` — illustrative annual fund fee as a percentage of invested assets

The dataset is **synthetic teaching data**: all numeric values are illustrative assumptions, not live or historical market observations. No download or data-cleaning step is required.

## Expected Final Deliverable

A concise comparison report that contrasts the three ETFs on expected return, volatility, and maximum drawdown, together with the reproducible workflow (plan, analysis steps, verification) used to produce it. The exact format of the final analysis report will be defined in a later tutorial.

## Three Project Milestones

1. **T1 — Project setup and plan**: Write this project plan and establish the repository structure (current milestone).
2. **T2 — Bounded analysis task**: Design a specific, bounded analysis task (for example, a risk–return comparison of the three ETFs) and implement it as planned work using the dataset.
3. **T3 — Verification and delivery**: Verify the analysis results against the repository inputs, document assumptions and limitations, and deliver the final report.

## One Data Limitation

The dataset contains only three rows of synthetic teaching values and omits correlations, taxes, transaction costs, liquidity, currency exposure, and investor-specific constraints, so any later analysis can only be illustrative and must not be used as investment advice or as the basis for a real investment decision.

## Next Action

Review this plan for consistency with the repository contents; once approved, the next step is to design the specific bounded analysis task for T2 (analysis itself is planned work and has not been completed yet).
