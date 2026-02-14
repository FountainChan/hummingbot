#!/usr/bin/env python3
"""Minimal backtest runner (no Hummingbot client required).

Produces a CSV similar to `backtest_mm_example.py` and optionally plots it.

Usage:
  python tools/run_synthetic_backtest.py --out data/synth_backtest.csv --plot
  python tools/run_synthetic_backtest.py --input-price data/price_source.csv --out data/backtest_from_prices.csv --plot
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd


def generate_price_series(start_time: datetime, periods: int, freq_minutes: int = 1) -> pd.DataFrame:
    rng = pd.date_range(start_time, periods=periods, freq=f"{freq_minutes}min")
    price = 100 + np.cumsum(np.random.randn(periods) * 0.2)
    open_ = price
    high = open_ + np.abs(np.random.rand(periods) * 0.5)
    low = open_ - np.abs(np.random.rand(periods) * 0.5)
    close = open_ + np.random.randn(periods) * 0.1
    df = pd.DataFrame({
        "timestamp": (rng.view("int64") // 10 ** 6),
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
    })
    return df


def run_backtest_on_prices(df: pd.DataFrame, order_amount: float, bid_bps: float, ask_bps: float, fee_bps: float) -> pd.DataFrame:
    df = df.copy()
    df["ask_price"] = df["open"] * (1 + ask_bps / 10000)
    df["bid_price"] = df["open"] * (1 - bid_bps / 10000)
    df["buy_amount"] = (df["low"] <= df["bid_price"]).astype(float) * order_amount
    df["sell_amount"] = (df["high"] >= df["ask_price"]).astype(float) * order_amount
    df["fees_paid"] = (df["buy_amount"] * df["bid_price"] + df["sell_amount"] * df["ask_price"]) * fee_bps / 10000
    df["base_delta"] = df["buy_amount"] - df["sell_amount"]
    df["quote_delta"] = df["sell_amount"] * df["ask_price"] - df["buy_amount"] * df["bid_price"] - df["fees_paid"]
    return df


def load_price_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # expect open/high/low/close and timestamp
    if "timestamp" not in df.columns:
        # try to infer by a time-like column
        for c in ("time", "date", "datetime"):
            if c in df.columns:
                df = df.rename(columns={c: "timestamp"})
                break
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-price", help="CSV price source with open/high/low/close and timestamp (ms or ISO)")
    parser.add_argument("--out", help="Output CSV path", default="data/synth_backtest.csv")
    parser.add_argument("--periods", type=int, default=1440, help="Number of candles to generate when no input provided")
    parser.add_argument("--order-amount", type=float, default=0.1)
    parser.add_argument("--bid-bps", type=float, default=10)
    parser.add_argument("--ask-bps", type=float, default=10)
    parser.add_argument("--fee-bps", type=float, default=10)
    parser.add_argument("--plot", action="store_true", help="Also generate interactive plot using tools/backtest_plot.py")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    if args.input_price:
        price_df = load_price_csv(args.input_price)
    else:
        price_df = generate_price_series(datetime.utcnow() - timedelta(minutes=args.periods), args.periods)

    bt_df = run_backtest_on_prices(price_df, args.order_amount, args.bid_bps, args.ask_bps, args.fee_bps)
    bt_df.to_csv(args.out, index=False)
    print(f"Wrote backtest CSV: {args.out}")

    if args.plot:
        # call the plotting tool
        try:
            import subprocess

            out_html = os.path.splitext(args.out)[0] + ".html"
            subprocess.check_call(["/workspaces/hummingbot/.venv/bin/python", "tools/backtest_plot.py", "--csv", args.out, "--out", out_html])
            print(f"Generated plot: {out_html}")
        except Exception as e:
            print(f"Plot failed: {e}")


if __name__ == "__main__":
    main()
