**Backtest Plot Tool**

**Purpose**: 使用 `tools/backtest_plot.py` 将回测生成的 CSV 转为交互式 Plotly HTML，可在浏览器中查看 K 线并标注买/卖点。

**脚本位置**: [tools/backtest_plot.py](tools/backtest_plot.py)

**示例 CSV（样例）**: [data/sample_backtest.csv](data/sample_backtest.csv)

**生成的示例 HTML**: [backtest_plot_example.html](backtest_plot_example.html)

**快速使用**:

- 安装依赖（如果尚未安装）:

```bash
pip install plotly pandas
```

- 运行脚本（支持 glob）:

```bash
python tools/backtest_plot.py --csv data/backtest_*.csv --out backtest_plot.html
```

**Docker / 容器内运行（快速示例）**:

```bash
# 构建镜像（仅示例）
docker build -t hummingbot:dev .

# 以交互方式进入容器并挂载当前代码（路径按需调整）
docker run --rm -it -v "$(pwd)":/hummingbot -w /hummingbot hummingbot:dev bash

# 容器内（如果项目虚拟环境存在，请激活或直接使用 python）
pip install plotly pandas
python tools/backtest_plot.py --csv data/backtest_*.csv --out /tmp/backtest_plot.html
```

**备注**:

- 脚本期望 CSV 包含 `open,high,low,close` 和 `timestamp`（毫秒或秒），以及可选的 `buy_amount` / `sell_amount` 列用于标注成交点。
- 若你使用 Hummingbot 自带回测脚本（例如 `scripts/utility/backtest_mm_example.py`），该脚本会将 CSV 写入 `data/` 目录，直接用本工具即可绘图。
