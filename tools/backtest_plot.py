#!/usr/bin/env python3
"""工具：将回测 CSV 绘制成交点到交互式 K 线图（Plotly）

用法示例：
  python tools/backtest_plot.py --csv data/backtest_ETH-USDT_10_bid_10_ask.csv --out backtest_plot.html

说明：脚本会读取 CSV（包含 open/high/low/close/timestamp，及 buy_amount/sell_amount），
将时间戳解析为时间序列，绘制 Plotly 蜡烛图并在买/卖点添加标记，生成可交互的 HTML 文件。
"""
from __future__ import annotations

import argparse
import glob
import os
from typing import Optional

import pandas as pd
import plotly.graph_objects as go


def detect_time_column(df: pd.DataFrame) -> Optional[str]:
    for col in ("timestamp", "time", "date", "datetime"):
        if col in df.columns:
            return col
    return None


def load_backtest_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    tcol = detect_time_column(df)
    if tcol is None:
        raise ValueError("No timestamp column found in CSV. Expected one of: timestamp,time,date,datetime")
    # If timestamp looks numeric (ms), convert accordingly
    if pd.api.types.is_integer_dtype(df[tcol]) or pd.api.types.is_float_dtype(df[tcol]):
        # assume milliseconds if values larger than 1e10, else seconds
        sample = int(df[tcol].dropna().iloc[0])
        unit = "ms" if sample > 1e10 or sample > 1e9 else "s"
        df["__time"] = pd.to_datetime(df[tcol], unit=unit)
    else:
        df["__time"] = pd.to_datetime(df[tcol])

    df = df.sort_values("__time").reset_index(drop=True)
    return df


def plot_backtest(df: pd.DataFrame, out_path: str) -> None:
    fig = go.Figure()

    # Candlestick expects columns: open, high, low, close
    fig.add_trace(
        go.Candlestick(
            x=df["__time"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price",
        )
    )

    # Buy markers
    if "buy_amount" in df.columns:
        buys = df[df["buy_amount"].astype(float) > 0]
        if not buys.empty:
            fig.add_trace(
                go.Scatter(
                    x=buys["__time"],
                    y=buys["low"],
                    mode="markers",
                    marker_symbol="triangle-up",
                    marker=dict(color="green", size=10),
                    name="Buy",
                    hovertemplate="Buy: %{y}<extra></extra>",
                )
            )

    # Sell markers
    if "sell_amount" in df.columns:
        sells = df[df["sell_amount"].astype(float) > 0]
        if not sells.empty:
            fig.add_trace(
                go.Scatter(
                    x=sells["__time"],
                    y=sells["high"],
                    mode="markers",
                    marker_symbol="triangle-down",
                    marker=dict(color="red", size=10),
                    name="Sell",
                    hovertemplate="Sell: %{y}<extra></extra>",
                )
            )

    fig.update_layout(
        title_text="Backtest Candlestick with Trades",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    fig.write_html(out_path, include_plotlyjs="cdn")
    print(f"Saved interactive plot to: {out_path}")


def find_csv_glob(pattern: str) -> Optional[str]:
    matches = glob.glob(pattern)
    return matches[0] if matches else None


def main():
    parser = argparse.ArgumentParser(description="Plot backtest CSV to interactive Plotly HTML")
    parser.add_argument("--csv", help="Path to backtest CSV file or glob (e.g. data/backtest_*.csv)")
    parser.add_argument("--out", help="Output HTML file", default="backtest_plot.html")
    args = parser.parse_args()

    csv_path = args.csv
    if any(c in csv_path for c in "*?["):
        found = find_csv_glob(csv_path)
        if found is None:
            raise SystemExit(f"No CSV matched pattern: {csv_path}")
        csv_path = found

    if not os.path.exists(csv_path):
        raise SystemExit(f"CSV file not found: {csv_path}")

    df = load_backtest_csv(csv_path)
    plot_backtest(df, args.out)


if __name__ == "__main__":
    main()
