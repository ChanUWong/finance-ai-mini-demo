# T2 ETF Comparison — SPY, TLT, GLD (Annual Fees and Maximum Drawdown)

This report extends the T1 project plan (synthetic teaching data) by upgrading the SPY / TLT / GLD comparison to real historical price data from the T2 ETF Data Pack.

## Sources and Setup

- **Input files:** `data/t2/daily_prices.csv` (7,536 daily observations) and `data/t2/fund_info.csv` (three disclosed fund records).
- **Pack preparation date:** 2026-09-25.
- **Fee disclosure dates:** SPY — fund-information as-of date 2026-09-10, fee-specific effective date not stated; TLT — current prospectus, specific date not stated in the fee panel; GLD — not stated in the selected field. All fee records accessed on 2026-09-25.
- **Common drawdown window:** 2016-09-01 through 2026-08-31, inclusive; **2,512 observations per ETF**. Daily frequency; weekends and full-day closures have no rows; early-close sessions are included.
- **Adjustment basis:** `adjusted_close` (provider's split and dividend-distribution adjustments, USD).
- **Script:** `artifacts/t2/calculate_drawdown.py` (Python 3.9.6 standard library only), run as `python3 artifacts/t2/calculate_drawdown.py`.
- **Input-check result:** all checks passed — exact ticker set {SPY, TLT, GLD}; unique ticker/date pairs; dates ascending within each ticker; finite positive `close` and `adjusted_close`; 2,512 rows per ETF (7,536 total); common first/last dates 2016-09-01 / 2026-08-31; identical date sets across tickers.
- **Calculation method:** for each ticker, `high_t` = largest `adjusted_close` from the window start through day `t`; `drawdown_t_pct = (adjusted_close_t / high_t - 1) * 100`; `max_drawdown_pct` = minimum drawdown over the full window. On ties, the earliest trough and its earliest corresponding peak were selected; peak is on or before trough. Full precision kept internally; only display values are rounded to two decimals.

## 1. Comparison

| Ticker | Annual expense ratio (%) | Calculated max drawdown (%) | Peak date | Trough date |
|---|---|---|---|---|
| SPY | 0.0945 | -33.72 | 2020-02-19 | 2020-03-23 |
| TLT | 0.15 | -48.35 | 2020-08-04 | 2023-10-19 |
| GLD | 0.4 | -26.40 | 2026-01-29 | 2026-07-16 |

Fee precision is preserved as disclosed. Maximum drawdowns are displayed to two decimals. Peak and trough `adjusted_close` values (full precision): SPY 307.63949585 / 203.911895752; TLT 141.584442139 / 73.1267700195; GLD 495.899993896 / 364.959991455.

## 2. Observation

**GLD has the smallest drawdown loss (closest to zero) in this period, at -26.40%**, compared with SPY at -33.72% and TLT at -48.35%; there are no ties among the displayed two-decimal results. These drawdowns were calculated from `adjusted_close` (a provider-adjusted price series) using a cumulative maximum from the window start — they were not read from a precomputed snapshot. Drawdowns are non-positive, so closer to zero means a smaller loss. One limitation: this measures daily-close drawdown only within the fixed 2016-09-01 to 2026-08-31 window; it is not an all-time measure, and the currently disclosed annual fees are disclosure snapshots (accessed 2026-09-25), not average fees over the ten-year price window. This comparison is for a classroom exercise, not investment advice.

## 3. Agent Check (self-check by the Agent)

- **Ticker checked:** SPY.
- **Source rows re-read from `data/t2/daily_prices.csv`:** peak `2020-02-19, SPY, close 338.3399963378906, adjusted_close 307.6394958496094`; trough `2020-03-23, SPY, close 222.9499969482422, adjusted_close 203.91189575195312`.
- **Check command:** inline Python (standard library) reading the CSV directly and recomputing `(trough / peak - 1) * 100`.
- **Actual output:** `(trough/peak - 1)*100 = -33.717257210811` (display -33.72); full-series recompute for SPY returned the same minimum drawdown, peak date 2020-02-19 and trough date 2020-03-23; peak is on or before trough; the running high at the trough date equals the reported peak price.
- **Comparison:** the recomputed value matches the report exactly (-33.72% to two decimals) and matches the full-precision value; no correction was needed.
- **Method inspection:** for all dates, the script uses all `adjusted_close` observations, tracks the cumulative high from the window start, enforces peak-before-trough order, and applies the earliest-trough / earliest-peak tie rule. The observation was checked against all three results: -26.40% (GLD) is closest to zero, so the observation stands.
- This is the Agent's own self-check of its calculation; it is not an independent verification, and no student has checked this data.
