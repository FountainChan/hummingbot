# 策略配置示例与参数说明

本目录包含若干策略的示例配置（YAML 格式），可直接复制到你的 `conf/` 目录作参考或载入。每个文件顶部包含简要说明与关键参数注释；下方 `docs/策略开发/策略清单.md` 给出策略位置与使用方法。

常见参数说明（摘要）：

- `connector`：交易所连接器名称（例如 `binance`，`binance_paper_trade`）。
- `trading_pair`：交易对，如 `ETH-USDT`。
- `order_amount`：每笔订单基础数量（以基础币种为单位）。
- `bid_spread_bps` / `ask_spread_bps`：买/卖价相对基价的点数（1 bps = 0.01%）。
- `fee_bps`：手续费（basis points）。
- `paper_trade_enabled`：是否使用模拟交易（True/False）。
- `risk_aversion` / `inventory_risk`：策略的风险参数（模型专用）。
- `leverage`、`max_position`：衍生品策略专用（杠杆、仓位上限）。

请根据各策略头部注释调整参数与路径。
