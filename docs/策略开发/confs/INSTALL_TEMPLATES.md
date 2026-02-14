# 安装 conf 模板

仓库包含 `conf/templates/` 目录下的策略模板，直接拷贝到项目根 `conf/` 即可在 Hummingbot 客户端中加载。

示例：

```bash
# 将 pure market making 模板复制为 conf/pure_market_making.yml
cp conf/templates/pure_market_making.yml conf/pure_market_making.yml

# 启动客户端并加载配置（交互式）
python -m hummingbot
# 在 Hummingbot CLI 中运行：
# start pure_market_making  或 使用 script start 加载脚本版本
```

批量安装示例模板：

```bash
mkdir -p conf
cp conf/templates/*.yml conf/
```

注意：复制后请根据你的连接器（`connector`）与 API key 配置 `conf/` 下的敏感配置（例如 exchange API key、secret），并根据实际交易风险调整参数。
