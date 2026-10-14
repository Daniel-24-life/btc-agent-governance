<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/cover-dark.svg" />
  <img src="docs/assets/cover-light.svg" alt="btc-agent-governance" width="1280" />
</picture>

# BTC Agent 治理

[完整作品目录](https://github.com/Daniel-24-life/AIfile)

[English](README.en.md) · [完整作品目录](https://github.com/Daniel-24-life/AIfile)

把研究任务、模拟执行、证据声明和状态晋级分开判断的可运行参考实现。
公开版使用合成任务，演示一个请求如何通过路由、证据分类与发布门禁。

![任务与证据的治理流程](docs/assets/governed-run-flow.svg)

## 先运行一次

需要 Python 3.11+，从仓库根目录运行：

```powershell
python public_demo.py
python public_demo.py --json
```

| 场景 | 路由 | 发布判断 |
| --- | --- | --- |
| 研究候选 | 允许 | 仅研究 |
| 模拟生命周期 | 允许 | 仅研究 |
| 状态晋级请求 | 需要审批 | 阻断 |
| 实盘请求 | 拒绝 | 阻断 |

四个场景始终没有执行权限，真实订单与成交均为零。

## 从哪里深入

- [系统架构](docs/architecture.md)：研究、执行、治理和编排的职责。
- [源码阅读路线](docs/SOURCE_READING_GUIDE.md)：从路由到 JSON 输出逐层阅读。
- [验证说明](docs/VERIFICATION.md)：22 项测试覆盖的边界与复核方法。
- [合成输出](sample.fake.json)：完整四场景记录，时间戳也是样例。
- [迁移记录](MIGRATION.md)：原公开来源及独立维护位置。

## 测试

```powershell
python -m pip install -r requirements-dev.txt
python -B -m pytest tests -q
```

## 实现范围

这套骨架保留任务路由、模拟生命周期、证据类别和 fail-closed 晋级检查。
研究允许继续，不会因此获得部署或交易权限。模拟成交字段不能支持真实成交声明。

策略公式、市场数据、回测、账号、凭据、真实收益和完整生产执行链不在公开范围内。
本项目没有交易所连接；它用于阅读治理代码和复核边界。
