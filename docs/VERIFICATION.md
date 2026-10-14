# 验证与公开状态

继承原公开包的 22 项 pytest 测试，覆盖路由、证据类别、晋级条件、模拟事件和
公开演示输出。测试运行与 Actions 结果是工程检查，不能当作策略收益或生产验证。

```powershell
python -m pip install -r requirements-dev.txt
python -B -m pytest tests -q
python public_demo.py
```

四场景预期路由依次为 allow、allow、approval_required、refuse。
发布状态依次为 research_only、research_only、blocked、blocked。
真实订单和成交均为 0，execution_authority 始终为 false。
