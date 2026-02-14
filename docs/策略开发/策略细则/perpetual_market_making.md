# Perpetual Market Making（永续合约做市）

用途：针对永续合约（perpetual）市场的做市策略，兼顾点差收益与资金费率对冲。

适用场景：资金费率可观察、流动性充足但价差波动中等；不适用于极端流动性枯竭或暴涨暴跌场景。

关键触发信号：
- funding_rate（资金费率）与历史均值偏离幅度
- orderbook 深度与 best_bid/ask spread
- open_interest 与资金流入/流出速率

主要参数（BTC/USDT 永续推荐起始值）：
- `connector`: 交易所（例如 `binance_perpetual`）
- `trading_pair`: `BTC-USDT`（或交易所格式）
- `leverage_limit`: 3
- `order_amount`: 0.001
- `spread_bps`: 2（可视流动性放宽到 5-20）
- `max_position`: 1.0（BTC）
- `funding_hedge_enabled`: true
- `inventory_target`: 0.0

风险控制：
- 实时监控保证金率，接近阈值时强制减仓或对冲。
- 若 funding_rate 异常（> 历史均值 ±2σ）则启动 funding hedge 或临时缩减挂单。
- 在波动率突增时（ATR 突破阈值）撤销所有被动挂单。

示例 conf 模板：`conf/templates/btcusdt_perp_perpetual_market_making.yml`

---
