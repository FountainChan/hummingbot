# Hummingbot 工作空间开发指南

本文档为 AI 编码代理（GitHub Copilot 等）提供快速参考和最佳实践。

## 项目概述

**Hummingbot** 是开源的自动化交易框架，支持在 140+ 交易所上设计和部署交易策略。该项目使用 Python 3.10+ 和 Cython，采用异步架构（asyncio）。

**核心价值**：简化高频交易策略开发，民主化定量交易。

## 代码结构

### 关键目录

```
hummingbot/                     # 主源代码
├── client/                     # CLI 用户界面
├── connector/                  # 交易所 API 连接器（80+ 交易所）
│   ├── exchange/              # 现货交易所
│   └── derivative/            # 衍生品交易所
├── strategy/                  # V1 策略基类（旧版，已弃用）
├── strategy_v2/               # V2 现代框架（推荐使用）
│   ├── controllers/           # 独立交易算法模块
│   ├── executors/             # 订单执行引擎
│   ├── models/                # 数据模型和配置
│   └── backtesting/           # 回测框架
├── core/                      # 核心框架
│   ├── event/                 # 事件系统（订单、交易等）
│   ├── data_type/             # 基础数据类型
│   ├── api_throttler/         # API 请求限流
│   └── gateway/               # DEX 网关
└── data_feed/                 # 市场数据源（K线、价格）

controllers/                    # 实现的控制器
├── directional_trading/       # 方向性交易算法
├── market_making/             # 做市商算法
└── generic/                   # 通用算法

scripts/                        # 脚本策略示例
├── v2_*.py                    # StrategyV2 示例
└── simple_*.py                # ScriptStrategyBase 示例

test/                          # 单元和集成测试
conf/                          # 配置文件模板

docs/                          # 中文开发文档（新增）
├── README.md                  # 文档首页
├── 快速开始/
├── 核心概念/
├── 策略开发/
├── 控制器/
├── 执行器/
└── 部署运维/
```

## 代码风格与约定

### 命名规范

#### Python 类和函数

```python
# ✅ 类：PascalCase
class OrderExecutor:
    pass

class BollingerV1Controller:
    pass

# ✅ 函数/方法：snake_case
def create_executor():
    pass

def on_order_filled_event():
    pass

# ✅ 常量：UPPER_SNAKE_CASE
MAX_ORDER_SIZE = 1000
API_RETRY_ATTEMPTS = 3

# ✅ 私有方法：_leading_underscore
def _calculate_indicator():
    pass

# ✅ 配置类：SuffixWithConfig
class BollingerV1ControllerConfig:
    pass
```

#### 文件和模块

```python
# ✅ 模块：snake_case
order_executor.py
bollinger_v1_controller.py

# ✅ 包：snake_case
hummingbot/strategy_v2/executors/
```

### 格式化标准

- **行长**：120 字符（pyproject.toml 配置）
- **缩进**：4 个空格
- **格式化工具**：Black
- **代码检查**：Flake8
- **排序**：isort

```bash
# 格式化代码
black hummingbot/

# 检查代码
flake8 hummingbot/

# 排序导入
isort hummingbot/
```

### 导入规范

```python
# ✅ 标准库优先
import asyncio
import logging
from decimal import Decimal
from typing import Dict, List, Optional

# 空行

# ✅ 第三方库
import pandas as pd
from pydantic import BaseModel, Field

# 空行

# ✅ 本地导入
from hummingbot.connector.connector_base import ConnectorBase
from hummingbot.strategy_v2.controllers.controller_base import ControllerBase
```

### 类型提示

```python
# ✅ 始终使用类型提示
def process_order(
    side: TradeType,
    amount: Decimal,
    price: Optional[Decimal] = None
) -> OrderType:
    pass

# ✅ 类属性类型提示
class Config(BaseModel):
    order_amount: Decimal = Field(default=Decimal("1.0"))
    connector_name: str = "binance"
```

### 异步代码

```python
# ✅ 使用 async/await
async def execute_order(self):
    await self.connector.place_order()
    await asyncio.sleep(1)

# ❌ 不要使用回调风格（已过时）
```

### 日志记录

```python
# ✅ 使用 HummingbotLogger
from hummingbot.logger import HummingbotLogger

logger = HummingbotLogger(__name__)
logger.info("Order placed")
logger.warning("High slippage detected")
logger.error("Failed to connect", exc_info=True)
```

## 架构设计要点

### 分层架构

**第三层：StrategyV2Base**
- 职责：全局协调、风险管理、性能跟踪
- 位置：`hummingbot/strategy/strategy_v2_base.py`
- 管理多个 Controller

**第二层：Controllers**
- 职责：生成交易信号、技术指标计算
- 位置：`controllers/` 和 `hummingbot/strategy_v2/controllers/`
- 继承自 `DirectionalTradingControllerBase` 或 `ControllerBase`
- 创建 Executor 实例

**第一层：Executors**
- 职责：实际下单、头寸管理、订单跟踪
- 位置：`hummingbot/strategy_v2/executors/`
- 基类：`ExecutorBase`
- 包括：OrderExecutor、PositionExecutor、GridExecutor、TWAPExecutor 等

**0 层：Connectors**
- 职责：与交易所 API 交互
- 位置：`hummingbot/connector/`
- 基类：`ConnectorBase`、`ExchangeBase`、`DerivativeBase`

### 事件驱动设计

```python
# Hummingbot 的事件流
交易所 API → Connector → 事件系统 → Strategy/Controller → Executor → 新订单

# 关键事件
class BuySellEvent:      # 订单创建
class OrderFilledEvent:  # 订单成交
class OrderCanceledEvent: # 订单取消
class OrderFailedEvent:  # 订单失败
```

### 异步模式

```python
# Hummingbot 使用 asyncio 并发框架
async def run_strategy():
    # 多个 Controller 并发运行
    await asyncio.gather(
        controller_1.control_loop(),
        controller_2.control_loop(),
        executor_orchestrator.execute_orchestration(),
    )
```

## 开发工作流

### 开发新策略

#### 简单策略（ScriptStrategyBase）

1. 创建 `scripts/my_strategy.py`
2. 继承 `ScriptStrategyBase`
3. 实现 `on_tick()` 方法
4. 在 `init_markets()` 中定义市场

#### 复杂策略（StrategyV2 + Controllers）

1. 创建控制器（如果需要新算法）：`controllers/my_algorithm/`
2. 创建主策略：`scripts/my_complex_strategy.py`
3. 在策略中初始化多个控制器
4. 使用 `ExecutorOrchestrator` 协调执行器

### 测试

```bash
# 运行单元测试
pytest test/hummingbot/ -v

# 运行特定测试
pytest test/hummingbot/strategy_v2/executors/ -v

# 测试覆盖率
pytest --cov=hummingbot test/
```

### 构建和部署

```bash
# 本地开发构建
pip install -e .

# Docker 构建
docker build -t hummingbot:latest .
docker-compose up

# 发布（maintainers only）
python setup.py bdist_wheel
```

## 关键 API 和模式

### Connector 接口

```python
class ConnectorBase:
    async def place_order(
        self,
        order_id: str,
        trading_pair: str,
        is_buy: bool,
        amount: Decimal,
        order_type: OrderType,
        price: Decimal
    ) -> None:
        pass
    
    def cancel_order(self, order_id: str) -> None:
        pass
    
    def get_order_book(self, trading_pair: str) -> OrderBook:
        pass
```

### Controller 接口

```python
class ControllerBase(RunnableBase):
    async def control_task(self) -> None:
        """每个更新周期调用一次"""
        pass
    
    def get_performance_report(self):
        """返回性能指标"""
        pass
    
    def get_custom_info(self) -> dict:
        """返回自定义信息用于日志"""
        pass
```

### Executor 接口

```python
class ExecutorBase(RunnableBase):
    async def execute_task(self) -> None:
        """每个更新周期调用一次"""
        pass
    
    @property
    def is_active(self) -> bool:
        """执行器是否仍在活跃"""
        pass
    
    @property
    def is_trading(self) -> bool:
        """是否正在交易中"""
        pass
```

## 常见模式和最佳实践

### 配置管理（Pydantic）

```python
from pydantic import BaseModel, Field, field_validator


class MyConfig(BaseModel):
    """使用 Pydantic 定义配置"""
    
    exchange: str = Field(default="binance", description="交易所名称")
    amount: Decimal = Field(default=Decimal("1.0"))
    
    @field_validator("exchange")
    @classmethod
    def validate_exchange(cls, v):
        valid_exchanges = ["binance", "coinbase", "kraken"]
        if v not in valid_exchanges:
            raise ValueError(f"Unknown exchange: {v}")
        return v
```

### K 线数据获取

```python
from hummingbot.data_feed.candles_feed.data_types import CandlesConfig


class MyControllerConfig(DirectionalTradingControllerConfigBase):
    candles_config: List[CandlesConfig] = [
        CandlesConfig(
            connector="binance",
            trading_pair="BTC-USDT",
            interval="1h",
            max_records=1000
        )
    ]
```

### 异常处理

```python
# ✅ 捕获和日志记录异常
try:
    await self.connector.place_order(...)
except Exception as e:
    self.logger().error(f"Failed to place order: {e}", exc_info=True)
    # 不要直接中止，应该实现重试逻辑
```

## 常见开发任务

### 添加新的交易所连接器

1. 在 `hummingbot/connector/exchange/` 或 `derivative/` 中创建新文件
2. 继承 `ExchangeBase` 或 `DerivativeBase`
3. 实现必需方法：`place_order()`, `cancel_order()`, `get_balances()` 等
4. 添加 API 限流配置
5. 添加单元测试

### 添加新的技术指标

```python
# 使用 pandas_ta 库（已集成）
import pandas_ta as ta

# 计算 RSI
rsi = ta.rsi(closes, length=14)

# 计算 MACD
macd = ta.macd(closes, fast=12, slow=26)

# 计算布林带
bbands = ta.bbands(closes, length=20, std=2.0)
```

### 性能优化

```python
# ✅ 缓存频繁计算的值
self._cached_indicator = None
self._cached_timestamp = None

def get_indicator(self):
    if self._cached_timestamp != self.current_timestamp:
        self._cached_indicator = self._calculate_indicator()
        self._cached_timestamp = self.current_timestamp
    return self._cached_indicator

# ✅ 批量 API 调用
balances = await asyncio.gather(
    connector_1.get_balance(),
    connector_2.get_balance(),
    connector_3.get_balance(),
)

# ✅ 异步 I/O 优化
async def fetch_multiple_orders(self):
    tasks = [self.fetch_order(order_id) for order_id in order_ids]
    return await asyncio.gather(*tasks)
```

## 构建和测试

### 依赖管理

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 更新依赖（定期检查）
pip list --outdated

# pip-compile（生成锁文件）
pip-compile requirements.txt
```

### 单元测试

```python
from hummingbot.test.isolated_asyncio_wrapper_test_case import IsolatedAsyncioTestCase


class TestMyController(IsolatedAsyncioTestCase):
    
    async def asyncSetUp(self):
        self.config = MyControllerConfig()
        self.controller = MyController(self.config)
    
    async def test_control_task(self):
        await self.controller.control_task()
        # 断言语句
        self.assertTrue(...)
```

### 日志调试

```bash
# 查看详细日志
tail -f logs/trading_bot.log

# 搜索特定错误
grep -i "error" logs/trading_bot.log

# 按时间戳搜索
grep "2026-02-13 10:" logs/trading_bot.log
```

## 文档编写

### 中文文档规范

- **新增文档放在**：`docs/` 目录下，按分类组织
- **分类目录**：使用中文目录名（快速开始、核心概念等）
- **文档文件**：使用中文文件名，.md 格式
- **内容风格**：
  - 使用简体中文
  - 包含代码示例
  - 使用适当的 Markdown 格式
  - 链接到相关代码文件

## 性能指标和监控

### 关键性能指标（KPIs）

```python
# 利润因子
profit_factor = total_profit / total_loss

# 夏普比率（衡量风险调整回报）
sharpe_ratio = (mean_return - risk_free_rate) / std_dev

# 最大回撤
max_drawdown = (peak_value - trough_value) / peak_value

# 胜率
win_rate = (wins / total_trades) * 100
```

### 监控点

```python
# 日志关键信息
self.logger().info(f"PnL: {pnl}, Win rate: {win_rate}%")

# 设置警告阈值
if drawdown > max_allowed_drawdown:
    self.logger().warning("Drawdown exceeded limit")
    self.stop()
```

## 常见错误和陷阱

### ❌ 常见错误

1. **阻塞事件循环**：在 async 函数中使用 `time.sleep()`
   ```python
   # ❌ 错误
   time.sleep(1)
   
   # ✅ 正确
   await asyncio.sleep(1)
   ```

2. **忘记处理异常**：异步函数中未捕获的异常会被忽略
   ```python
   # ✅ 始终包装异步操作
   try:
       await self.place_order()
   except Exception as e:
       logger.error(e, exc_info=True)
   ```

3. **N+1 API 问题**：循环中调用 API
   ```python
   # ❌ 错误（N+1 调用）
   for order_id in order_ids:
       order = await connector.get_order(order_id)
   
   # ✅ 正确（并发调用）
   orders = await asyncio.gather(*[
       connector.get_order(oid) for oid in order_ids
   ])
   ```

4. **过度优化参数**：使用历史数据过度拟合
   ```python
   # ✅ 良好实践
   # 1. 在独立的测试集上验证
   # 2. 检查 walk-forward 性能
   # 3. 在出样集上测试
   ```

5. **忽视时区问题**
   ```python
   # ✅ 始终使用 UTC
   from datetime import datetime, timezone
   now = datetime.now(timezone.utc)
   ```

## 调试技巧

### 快速调试

```python
# 1. 添加临时日志
self.logger().debug(f"Variable value: {variable}")

# 2. 使用 pdb
import pdb; pdb.set_trace()

# 3. 单元测试验证
pytest test/specific_test.py -v -s
```

### 性能分析

```python
# 使用 cProfile
import cProfile
cProfile.run('strategy.control_loop()')

# 使用 timeit
import timeit
timeit.timeit('calculate_indicator()', number=1000)
```

## 有用的工具和资源

### 开发工具

- **IDE**：VS Code（推荐）、PyCharm
- **版本控制**：Git
- **包管理**：pip、conda
- **文档**：Sphinx、MkDocs

### 测试工具

- **单元测试**：pytest
- **覆盖率**：pytest-cov
- **Mock**：unittest.mock

### 分析工具

- **静态分析**：pylint、mypy
- **代码格式**：black、isort
- **性能分析**：cProfile、py-spy

## 项目贡献指南

### 提交 PR 清单

- [ ] 创建新分支（`feature/description` 或 `fix/issue-number`）
- [ ] 编写代码和测试
- [ ] 运行 `black` 和 `flake8`
- [ ] 添加/更新文档
- [ ] 通过所有测试
- [ ] 创建 PR 并填写模板

### 提交信息规范

```
<type>: <subject>

<body>

<footer>

# 类型: feat, fix, docs, style, refactor, test, chore
# 主题: 命令式，现在式，小写
# 正文: 解释做了什么和为什么
# 页脚: 关联 issue（Fixes #123）
```

## 快速参考

### 常用命令

```bash
# 启动开发环境
python -m hummingbot

# 运行测试
pytest test/

# 代码格式化
black hummingbot/

# 检查代码质量
flake8 hummingbot/

# 构建 Docker 镜像
docker build -t hummingbot:dev .

# 启动 Docker 容器
docker-compose up -d
```

### 重要文件

- `setup.py`：项目配置和依赖
- `pyproject.toml`：Build 系统和工具配置
- `Makefile`：常用命令
- `docker-compose.yml`：Docker 部署配置
- `docs/`：发展文档

---

**快速提示**：新开发者应该先阅读 `docs/` 目录中的文档，特别是 `docs/核心概念/架构设计.md`。

最后更新：2026-02-13
