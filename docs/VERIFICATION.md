# 验证与公开状态

pytest 测试覆盖路由、证据类别、晋级条件、模拟事件、公开演示输出，以及静态查看器
的结构、视觉合同、默认场景、空值语义和非交易边界。测试运行与 Actions 结果是工程检查，
不能当作策略收益或生产验证。

```powershell
python -m pip install -r requirements-dev.txt
python -B -m pytest tests -q
python public_demo.py
python -m http.server 8000
```

启动服务器后访问 <http://localhost:8000/demo/>。浏览器视觉复核矩阵与结果记录在
[UI 审计](UI_AUDIT.md)；静态测试不能替代浏览器键盘、缩放和响应式检查。

四场景预期路由依次为 allow、allow、approval_required、refuse。
发布状态依次为 research_only、research_only、blocked、blocked。
真实订单和成交均为 0，execution_authority 始终为 false。
