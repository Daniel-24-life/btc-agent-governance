# 本地记录查看器 UI 审计

审计日期：2026-10-15  
范围：新增 `demo/` 本地静态查看器前的源码审计  
目标用户：希望核对四个合成治理场景、路由理由、证据与原始记录的代码审阅者  
主要任务：不接触真实数据或交易能力，在浏览器中快速区分“已运行”“未运行”和“被治理阻断”

## 发现（实现前）

### [P1] 没有可视化记录入口

- Layer: required
- Evidence: 仓库根目录无 `demo/` 或 HTML 入口；`README.md` 的“先运行一次”仅列出 `python public_demo.py` 与 `--json`，`README.en.md` 的 Run 亦只有 CLI；完整记录仅存在于 `sample.fake.json`。
- Impact: 不运行 Python 或不熟悉嵌套 JSON 的读者无法直接浏览四场景及其治理结果。
- Basis: 内容与结构；页面目的和主要任务应能通过语义层级被识别。
- Minimal fix: 增加无依赖静态查看器，从根服务器读取 `../sample.fake.json`，并在双语 README 提供本地运行入口。
- Confidence: high
- Verification: not tested（实现前没有页面）；实现后从仓库根目录启动本地服务器，确认页面成功读取样例且显示四个场景。

### [P1] `null` 需要明确表达“未运行”，阻断必须来自实际决定

- Layer: required
- Evidence: `sample.fake.json` 中 `research_candidate.lifecycle`、`promotion_request.lifecycle`、`live_request.lifecycle` 都为 `null`；但路由分别为 `allow`、`approval_required`、`refuse`。单看空值无法判断阶段未适用，还是因治理决定未执行。
- Impact: 读者可能把正常未运行误解为缺失数据，或错误推断空阶段本身执行过并产生了阻断。
- Basis: 名称与说明、内容完整性；状态不能只依赖空值或颜色。
- Minimal fix: 生命周期或证据为 `null` 时统一标为“未运行”；只有实际路由拒绝、晋级拒绝、证据不允许或发布阻断才标为“已阻断”，同时保留原始 JSON 供核对。
- Confidence: high
- Verification: 展开研究、晋级、实盘三个场景，空生命周期/证据均显示“未运行”；实际拒绝决定显示“已阻断”；原始 JSON 仍显示真实 `null`。

### [P1] 真实公开边界在浏览任务中缺少持续可见位置

- Layer: required
- Evidence: `sample.fake.json` 顶层声明 `contains_real_data: false`、`system_status: research_only`，汇总中真实订单与成交均为 0；每个场景 `execution_authority` 均为 false。现有边界只在 CLI/README/JSON 中表达，没有浏览界面。
- Impact: 浏览局部场景时，读者可能误把 `simulated_fill` 或研究结果理解成真实交易记录。
- Basis: 内容诚实与产品边界。
- Minimal fix: 顶部固定信息区直接展示合成数据、研究状态、零真实订单/成交，并明确“绝不模型交易”；场景状态重复展示无执行权限。
- Confidence: high
- Verification: 所有宽度均可见边界摘要；`dry_run_lifecycle` 的模拟成交旁明确标注非真实成交。

### [P2] 嵌套 JSON 缺少任务导向的阅读顺序

- Layer: contextual
- Evidence: `sample.fake.json` 的每个场景按 task、route、lifecycle、evidence、promotion、release 顺序存储，但读者需要自行跨对象拼接“请求 → 路由 → 阶段 → 发布”的因果关系。
- Impact: 四个场景横向比较和定位阻断理由较慢。
- Basis: 层级与阅读路径；仪表界面应优先当前状态、异常与下一步。
- Minimal fix: 默认选择 `dry_run_lifecycle`，用原生场景选择控件和阶段化详情呈现路由、治理阶段、原因/证据，最后提供原始 JSON。
- Confidence: high
- Verification: 首次载入默认显示模拟生命周期；键盘可切换四场景；标题层级与 DOM 阅读顺序一致。

### [P2] 新页面需要明确的窄屏与键盘基线

- Layer: required
- Evidence: 当前仓库没有网页样式、控件或响应式规则可复用。
- Impact: 若直接把长键值和 JSON 平铺，320px 下容易整页横向滚动；自定义选项也可能缺少键盘与焦点支持。
- Basis: 键盘操作、可见焦点、320 CSS px reflow、目标尺寸。
- Minimal fix: 使用原生按钮与 `details/summary`；可见 `:focus-visible`；长标识符局部换行，原始 JSON 仅在自身容器横向滚动；320px 单列布局。
- Confidence: high
- Verification: 在 320、375、768、1440 CSS px 检查整页无水平溢出；完整键盘遍历并确认焦点可见。

### [P3] 需要从治理产品语义而非通用卡片模板建立视觉辨识

- Layer: preference
- Evidence: 用户指定浅色 `#f3f6f8`、内容深色 `#102536`、导航/强调 `#12685f`，仓库现有封面亦以治理流程为核心，但没有网页视觉合同。
- Impact: 若使用无差别卡片网格，治理顺序与因果关系会被弱化。
- Basis: 产品特定结构与层级。
- Minimal fix: 用“场景索引 + 治理阶段轨道 + 记录详情”的结构；颜色服务于导航、状态与焦点，不以装饰效果替代信息。
- Confidence: medium
- Verification: 1440px 首屏可辨识页面目的、当前场景、边界和阶段顺序；窄屏仍保持相同优先级。

## 实现约束与成功条件

- 保留 Python、JSON、Markdown 的既有栈与业务语义，不修改路由、证据分类、晋级门禁和 dry-run 生命周期。
- 页面只读取仓库内合成样例；不发起外部请求、不接入账户、不生成策略、不提供下单或模型交易能力。
- 统一使用浅色 `#f3f6f8`、内容深色 `#102536`、导航/强调 `#12685f`；正文不小于 16px，标签不小于 13px；中文正文不强制字距。
- 原生语义控件、可见焦点、320px 响应式；所有状态同时使用文字，不只依赖颜色。
- 必测：默认场景、四场景切换、加载成功、加载错误、未运行/实际阻断区分、`approval_required` 不暗示已批准、每场景执行权限严格为 false、原始 JSON、键盘焦点、200% 文本、文本间距覆盖、减少动画偏好及 320/375/768/1440px。

## 实现前验证矩阵

| 检查 | 状态/视口 | 结果 | 证据 | 完成条件 |
| --- | --- | --- | --- | --- |
| 内容结构 | 页面入口 | not tested | 页面尚不存在 | 页面具备语言、标题、导航、main、层级标题与状态文本 |
| 数据读取 | 根服务器 | not tested | 页面尚不存在 | 成功 fetch `../sample.fake.json`，失败时显示恢复说明 |
| 状态语义 | 四场景 | not tested | 仅有原始空值 | 空阶段显示未运行；阻断只对应实际拒绝决定；需审批不暗示已批准 |
| 键盘与焦点 | 全页面 | not tested | 页面尚不存在 | 所有控件可操作，焦点清晰可见且顺序符合阅读路径 |
| Reflow | 320/375/768/1440px | not tested | 页面尚不存在 | 页面无二维滚动；JSON 滚动限制在代码容器 |
| 文本放大 | 200% | not tested | 页面尚不存在 | 无内容丢失、遮挡或不可操作控件 |
| 文本间距 | WCAG 覆盖值 | not tested | 页面尚不存在 | 无裁切、重叠或隐藏内容 |
| 对比度 | 默认/交互状态 | not tested | 页面尚不存在 | 正文至少 4.5:1，焦点和必要边界至少 3:1 |
| 浏览器运行 | 本地 HTTP | not tested | 页面尚不存在 | 控制台无影响显示的错误，截图记录稳定状态 |

