#!/usr/bin/env python3
"""T2 drawdown calculation for SPY, TLT, GLD using the T2 ETF Data Pack.

Reads data/t2/daily_prices.csv (and data/t2/fund_info.csv for the fee echo),
validates the inputs against the data dictionary, then computes, for each
ticker, the running cumulative maximum of adjusted_close from the window
start and the daily drawdown:

    high_t              = largest adjusted_close from window start through day t
    drawdown_t_pct      = (adjusted_close_t / high_t - 1) * 100
    max_drawdown_pct    = minimum drawdown_t_pct across the full window

Tie rule (data dictionary): select the earliest trough and its earliest
corresponding peak. If no loss occurs, use the first observation for both
dates and zero drawdown. Full precision is kept internally; only display
values are rounded to two decimal places.

Uses only the Python 3 standard library.
"""

import csv
import math
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRICES_PATH = os.path.join(BASE_DIR, "data", "t2", "daily_prices.csv")
FUND_INFO_PATH = os.path.join(BASE_DIR, "data", "t2", "fund_info.csv")

EXPECTED_TICKERS = ["SPY", "TLT", "GLD"]
EXPECTED_PER_TICKER = 2512
EXPECTED_FIRST_DATE = "2016-09-01"
EXPECTED_LAST_DATE = "2026-08-31"


def load_prices(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["date", "ticker", "close", "adjusted_close"]:
            raise ValueError("Unexpected header: %r" % (reader.fieldnames,))
        for i, row in enumerate(reader, start=2):
            try:
                close = float(row["close"])
                adj = float(row["adjusted_close"])
            except (TypeError, ValueError):
                raise ValueError("Non-numeric price at line %d: %r" % (i, row))
            rows.append(
                {
                    "line": i,
                    "date": row["date"],
                    "ticker": row["ticker"],
                    "close": close,
                    "adjusted_close": adj,
                }
            )
    return rows


def validate(rows):
    checks = []

    tickers = set(r["ticker"] for r in rows)
    checks.append(("Ticker set is exactly {SPY, TLT, GLD}", tickers == set(EXPECTED_TICKERS)))

    counts = {t: 0 for t in EXPECTED_TICKERS}
    for r in rows:
        counts[r["ticker"]] += 1
    checks.append(
        ("Per-ticker row count == %d (total %d rows)"
         % (EXPECTED_PER_TICKER, len(rows)),
         len(rows) == EXPECTED_PER_TICKER * len(EXPECTED_TICKERS)
         and all(counts[t] == EXPECTED_PER_TICKER for t in EXPECTED_TICKERS)))

    by_ticker = {t: [] for t in EXPECTED_TICKERS}
    for r in rows:
        by_ticker[r["ticker"]].append(r)

    # Dates ascending within each ticker group, and unique ticker/date keys.
    dupes = 0
    for t in EXPECTED_TICKERS:
        seen = set()
        prev = None
        for r in by_ticker[t]:
            if r["date"] in seen:
                dupes += 1
            seen.add(r["date"])
            if prev is not None and r["date"] < prev:
                raise ValueError("Date order violation for %s: %s after %s"
                                 % (t, r["date"], prev))
            prev = r["date"]
    checks.append(("Dates ascending within each ticker group", dupes == 0))
    checks.append(("No duplicate ticker/date keys", dupes == 0))

    # Finite positive prices (both close and adjusted_close).
    bad_prices = 0
    for r in rows:
        if not (math.isfinite(r["close"]) and r["close"] > 0
                and math.isfinite(r["adjusted_close"]) and r["adjusted_close"] > 0):
            bad_prices += 1
    checks.append(("All close/adjusted_close finite and positive", bad_prices == 0))

    # First/last dates per ticker.
    first_last_ok = all(
        by_ticker[t][0]["date"] == EXPECTED_FIRST_DATE
        and by_ticker[t][-1]["date"] == EXPECTED_LAST_DATE
        for t in EXPECTED_TICKERS)
    checks.append(("First date %s / last date %s for every ticker"
                   % (EXPECTED_FIRST_DATE, EXPECTED_LAST_DATE), first_last_ok))

    # Equal date sets across tickers.
    date_sets = {t: set(r["date"] for r in by_ticker[t]) for t in EXPECTED_TICKERS}
    equal_sets = len(set(frozenset(s) for s in date_sets.values())) == 1
    checks.append(("Date sets identical across all three tickers", equal_sets))

    return by_ticker, checks


def calculate(by_ticker):
    results = {}
    for t in EXPECTED_TICKERS:
        rows = by_ticker[t]
        running_high = None
        high_date = None
        min_drawdown = 0.0
        trough_date = None
        peak_date = None
        peak_price = None
        trough_price = None

        first_date = rows[0]["date"]
        first_price = rows[0]["adjusted_close"]

        for r in rows:
            price = r["adjusted_close"]
            if running_high is None or price > running_high:
                running_high = price
                high_date = r["date"]
            drawdown = (price / running_high - 1.0) * 100.0
            if drawdown < min_drawdown:
                # Strictly lower: first occurrence wins the earliest-trough tie.
                min_drawdown = drawdown
                trough_date = r["date"]
                trough_price = price
                peak_date = high_date
                peak_price = running_high

        if min_drawdown == 0.0:
            # No loss: use the first observation for both dates, zero drawdown.
            peak_date = first_date
            trough_date = first_date
            peak_price = first_price
            trough_price = first_price

        results[t] = {
            "min_drawdown_pct": min_drawdown,
            "peak_date": peak_date,
            "peak_price": peak_price,
            "trough_date": trough_date,
            "trough_price": trough_price,
            "n": len(rows),
        }
    return results


def load_fund_info(path):
    funds = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            funds[row["ticker"]] = row
    return funds


def main():
    rows = load_prices(PRICES_PATH)
    by_ticker, checks = validate(rows)
    results = calculate(by_ticker)
    funds = load_fund_info(FUND_INFO_PATH)

    print("INPUT PATHS")
    print("  daily_prices :", PRICES_PATH)
    print("  fund_info    :", FUND_INFO_PATH)

    print("\nINPUT-CHECK RESULTS")
    for desc, ok in checks:
        print("  [%s] %s" % ("OK " if ok else "FAIL", desc))
    if not all(ok for _, ok in checks):
        print("Input checks failed; stopping. Do not guess data.", file=sys.stderr)
        sys.exit(1)

    print("\nFUND-INFO ECHO (fee disclosure)")
    for t in EXPECTED_TICKERS:
        f = funds[t]
        print("  %s  expense_ratio_pct=%s  disclosure=%s  accessed=%s"
              % (t, f["expense_ratio_pct"], f["fee_disclosure_date"], f["fee_accessed_on"]))

    print("\nDRAWDOWN RESULTS (full precision; display rounded to 2 dp)")
    for t in EXPECTED_TICKERS:
        r = results[t]
        print("  %s: n=%d  peak=%s adj_close=%.12g  trough=%s adj_close=%.12g  max_drawdown_pct=%.12f (display %.2f)"
              % (t, r["n"], r["peak_date"], r["peak_price"], r["trough_date"],
                 r["trough_price"], r["min_drawdown_pct"], r["min_drawdown_pct"]))
        if not (r["peak_date"] <= r["trough_date"]):
            raise ValueError("Peak after trough for %s" % t)

    print("\nMETHOD")
    print("  high_t = max(adjusted_close) from window start through day t")
    print("  drawdown_t_pct = (adjusted_close_t / high_t - 1) * 100")
    print("  max_drawdown_pct = min(drawdown_t_pct) over full window")
    print("  Tie rule: earliest trough, earliest corresponding peak; "
          "no loss -> first observation, zero drawdown.")
    print("  Full precision kept internally; only display rounding to 2 dp.")


if __name__ == "__main__":
    main()
