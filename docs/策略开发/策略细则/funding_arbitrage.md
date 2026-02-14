# Funding Rate Arbitrage（资金费率套利）

用途：利用不同交易品种或交易所间资金费率差异（或 funding_rate 与历史均值偏离）进行套利或对冲持仓以赚取 funding 收益。

适用场景：funding_rate 异常（高正或高负），或交易所间 funding 存在稳定差值。

关键触发信号：
- funding_rate_zscore > 阈值（例如 2）
- perp 与 spot/basis 价差（basis）超过成本阈值

主要参数（BTC/USDT 永续推荐起始值）：
- `funding_zscore_threshold`: 2.0
- `hedge_ratio`: 1.0（全仓对冲）
- `max_position`: 2.0
- `order_amount`: 0.001

风险控制：
- 保证金与强平监控，设置 funding 反转报警并分段平仓。
- 考虑闪崩时的基差快速收敛导致的滑点与对手方风险。

示例 conf 模板：`conf/templates/btcusdt_perp_funding_arbitrage.yml`

---
