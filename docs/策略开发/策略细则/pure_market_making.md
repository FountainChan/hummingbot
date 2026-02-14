# Pure Market Making（纯做市）

用途：在买卖两侧被动提供流动性以赚取点差，适合流动性较好的市场和低波动阶段。

适用场景：低波动、横盘区间、深度充足。

关键触发信号：
- 低 ATR、MA 突触频率低、orderbook imbalance 接近中性。

主要参数（BTC/USDT 永续推荐起始值）：
- `spread_bps`: 3
- `order_amount`: 0.001
- `order_refresh_time`: 5（秒）
- `inventory_target`: 0.0

风险控制：
- 当被吃单速度或滑点超过阈值时，缩小 spread 或撤单；当 funding_rate 或波动率异常时暂停。

示例 conf 模板：`conf/templates/btcusdt_perp_pure_market_making.yml`

---
