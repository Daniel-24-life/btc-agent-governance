# 源码阅读路线

| 顺序 | 入口 | 核心问题 |
| --- | --- | --- |
| 1 | [任务路由](../orchestrator/task_router.py) | 请求能否进入目标平面？ |
| 2 | [模拟生命周期](../execution/dryrun_lifecycle.py) | intent、event、对账如何组织？ |
| 3 | [证据分类](../governance/evidence_classifier.py) | 证据能支持什么声明？ |
| 4 | [晋级门禁](../governance/promotion_gate.py) | 哪些缺口和上限阻断晋级？ |
| 5 | [公开运行器](../public_demo.py) | 四种场景如何组合并输出 JSON？ |
| 6 | [测试](../tests/) | 哪些错误声明和权限升级被拒绝？ |

先运行四场景，再读边界测试，最后尝试修改合成输入。修改输入不会获得真实交易能力。
