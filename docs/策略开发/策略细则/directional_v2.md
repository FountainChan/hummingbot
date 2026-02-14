# Directional / Trend-Following（趋势/趋势跟随，Strategy V2 控制器）

用途：捕捉明显的单边行情，通过信号控制器判断趋势方向并由 Executor 分段入场、止损与止盈。

适用场景：MA 突破、成交量放大、持续的方向性移动（短中期）。不适用于震荡区间或流动性极差时。

关键触发信号：
- MA5/MA20 与 MA50 的交叉与斜率
- 成交量放大（相对历史均值）
- 突破确认（价格在阻力/支撑上方/下方持续 N 根 K 线）

主要参数（BTC/USDT 永续推荐起始值）：
- `entry_threshold`: 0.002（价格突破 0.2% 视作进场信号）
- `stop_loss_pct`: 0.01（1%）
- `take_profit_pct`: 0.02（2%）
- `pyramiding_limit`: 2
- `order_amount`: 0.002

风险控制：
- 使用滑点保护与限速下单；在资金费率极端或保证金不足时暂停新仓位。
- 结合 `TWAP` 执行降低大额滑点。

示例 conf 模板：`conf/templates/btcusdt_perp_directional_v2.yml`

---
