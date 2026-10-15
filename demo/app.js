(function () {
  "use strict";

  const DATA_URL = "../sample.fake.json";
  const DEFAULT_SCENARIO = "dry_run_lifecycle";
  const LABELS = {
    research_candidate: "研究候选",
    dry_run_lifecycle: "模拟生命周期",
    promotion_request: "状态晋级请求",
    live_request: "实盘请求",
    allow: "允许",
    approval_required: "需要审批",
    refuse: "拒绝",
    research_only: "仅研究",
    blocked: "已阻断",
  };

  function label(value) {
    return LABELS[value] || value || "未提供";
  }

  function stageState(scenario, stage) {
    if (stage === "route") {
      return scenario.route.decision === "refuse" ? "blocked" : "complete";
    }
    if (stage === "lifecycle") {
      if (scenario.lifecycle) return "complete";
      return "not-run";
    }
    if (stage === "evidence") {
      if (scenario.evidence) return scenario.evidence.allowed ? "complete" : "blocked";
      return "not-run";
    }
    if (stage === "promotion") {
      if (scenario.promotion) return scenario.promotion.decision.allowed ? "complete" : "blocked";
      return "not-run";
    }
    return scenario.release.decision === "blocked" ? "blocked" : "complete";
  }

  function stageDescription(scenario, stage, state) {
    if (stage === "route") {
      return scenario.route.decision === "approval_required"
        ? "已评估：需要明确审批；不代表已经批准"
        : `决定：${label(scenario.route.decision)}`;
    }
    if (stage === "lifecycle" && scenario.lifecycle) {
      return `已模拟并对账，${scenario.lifecycle.events.length} 个事件；不含真实订单或成交`;
    }
    if (stage === "evidence" && scenario.evidence) {
      return `证据类别：${scenario.evidence.evidence_class}`;
    }
    if (stage === "promotion" && scenario.promotion) {
      return `晋级未获准：${scenario.promotion.decision.blockers.join("、")}`;
    }
    if (stage === "release") return `发布判断：${label(scenario.release.decision)}；执行权限：无`;
    return "未运行：此场景未请求或不适用该阶段";
  }

  function buildStages(scenario) {
    return [
      ["route", "任务路由"],
      ["lifecycle", "Dry-run 生命周期"],
      ["evidence", "证据分类"],
      ["promotion", "晋级门禁"],
      ["release", "发布边界"],
    ].map(([key, title]) => {
      const state = stageState(scenario, key);
      return { key, title, state, description: stageDescription(scenario, key, state) };
    });
  }

  function create(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function statusClass(value) {
    if (value === "blocked" || value === "refuse") return "blocked";
    if (value === "approval_required") return "pending";
    return "safe";
  }

  function renderBoundary(payload) {
    const values = document.querySelector("#boundary-values");
    values.replaceChildren();
    const rows = [
      ["系统状态", label(payload.system_status)],
      ["真实订单", String(payload.summary.real_orders_submitted)],
      ["真实成交", String(payload.summary.real_fills_recorded)],
    ];
    rows.forEach(([term, value]) => {
      const row = create("div");
      row.append(create("dt", "", term), create("dd", "", value));
      values.append(row);
    });
  }

  function renderScenarioList(payload, selectedName) {
    const list = document.querySelector("#scenario-list");
    list.replaceChildren();
    payload.scenarios.forEach((scenario, index) => {
      const button = create("button", "scenario-button");
      button.type = "button";
      button.dataset.scenario = scenario.scenario;
      button.setAttribute("aria-pressed", String(scenario.scenario === selectedName));
      button.append(
        create("span", "", `0${index + 1} · ${label(scenario.route.decision)}`),
        create("strong", "", label(scenario.scenario))
      );
      button.addEventListener("click", () => renderScenario(payload, scenario.scenario, true));
      list.append(button);
    });
  }

  function renderReasons(scenario) {
    const reasons = document.querySelector("#route-reasons");
    reasons.replaceChildren();
    scenario.route.reasons.forEach((reason) => reasons.append(create("li", "", reason)));
  }

  function renderStages(scenario) {
    const list = document.querySelector("#stage-list");
    list.replaceChildren();
    buildStages(scenario).forEach((stage, index) => {
      const item = create("li", `stage-item ${stage.state}`);
      const marker = create("span", "stage-marker", String(index + 1));
      marker.setAttribute("aria-hidden", "true");
      const copy = create("div", "stage-copy");
      copy.append(create("strong", "", stage.title), create("span", "", stage.description));
      item.append(marker, copy);
      list.append(item);
    });
  }

  function evidenceEntries(scenario) {
    if (scenario.evidence) {
      return [
        ["证据类别", scenario.evidence.evidence_class],
        ["证据判断", scenario.evidence.allowed ? "可支持所请求的研究声明" : "不能支持所请求声明"],
        ["允许声明", scenario.evidence.allowed_claims.join("、") || "无"],
        ["阻断声明", scenario.evidence.blocked_claims.join("、") || "无"],
        ["证据原因", scenario.evidence.reasons.join("；")],
      ];
    }
    if (scenario.promotion) {
      return [
        ["晋级目标", `${scenario.promotion.request.current_status} → ${scenario.promotion.request.target_status}`],
        ["晋级结果", scenario.promotion.decision.allowed ? "允许" : "阻断"],
        ["阻断原因", scenario.promotion.decision.blockers.join("、")],
        ["缺失证据", scenario.promotion.decision.missing_evidence.join("、") || "无"],
        ["缺失检查", scenario.promotion.decision.missing_checks.join("、") || "无"],
      ];
    }
    return null;
  }

  function renderEvidence(scenario) {
    const content = document.querySelector("#evidence-content");
    content.replaceChildren();
    const entries = evidenceEntries(scenario);
    if (!entries) {
      content.append(create(
        "p",
        "empty-state",
        "未运行：该场景没有证据分类记录；路由结果请以“路由决定”阶段为准。"
      ));
      return;
    }
    const grid = create("dl", "evidence-grid");
    entries.forEach(([term, value]) => {
      const item = create("div", "evidence-item");
      item.append(create("dt", "", term), create("dd", "", value));
      grid.append(item);
    });
    content.append(grid);
  }

  function renderScenario(payload, name, updateHash) {
    const scenario = payload.scenarios.find((item) => item.scenario === name) || payload.scenarios[0];
    if (!scenario) throw new Error("合成记录中没有场景");
    renderScenarioList(payload, scenario.scenario);
    document.querySelector("#scenario-kicker").textContent = `${scenario.task.task_id} · ${scenario.task.plane}`;
    document.querySelector("#scenario-title").textContent = label(scenario.scenario);
    document.querySelector("#scenario-description").textContent = scenario.task.description;
    document.querySelector("#route-status").textContent = label(scenario.route.decision);
    document.querySelector("#route-status").className = `status-label ${statusClass(scenario.route.decision)}`;
    const badge = create("span", `badge ${statusClass(scenario.release.decision)}`, label(scenario.release.decision));
    badge.setAttribute("aria-label", `发布状态：${label(scenario.release.decision)}；执行权限：无`);
    document.querySelector("#release-badge").replaceChildren(badge);
    renderReasons(scenario);
    renderStages(scenario);
    renderEvidence(scenario);
    document.querySelector("#raw-json").textContent = JSON.stringify(scenario, null, 2);
    if (updateHash) history.replaceState(null, "", `#${scenario.scenario}`);
  }

  function validatePayload(payload) {
    if (!payload || !Array.isArray(payload.scenarios) || payload.scenarios.length !== 4) {
      throw new Error("记录格式不符合四场景公开样例");
    }
    const allAuthorityDisabled = payload.scenarios.every(
      (scenario) => scenario.release && scenario.release.execution_authority === false
    );
    if (payload.contains_real_data !== false || payload.summary.real_orders_submitted !== 0 || payload.summary.real_fills_recorded !== 0 || !allAuthorityDisabled) {
      throw new Error("安全边界校验失败：查看器只接受无真实数据、零真实订单/成交且所有场景无执行权限的样例");
    }
    return payload;
  }

  async function init() {
    const status = document.querySelector("#load-status");
    try {
      const response = await fetch(DATA_URL, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = validatePayload(await response.json());
      renderBoundary(payload);
      const requested = decodeURIComponent(location.hash.slice(1));
      const initial = payload.scenarios.some((item) => item.scenario === requested)
        ? requested
        : DEFAULT_SCENARIO;
      renderScenario(payload, initial, false);
      document.querySelector("#scenarios").hidden = false;
      status.textContent = "已读取本地合成记录。数据为只读，页面不会发送或修改任何交易状态。";
    } catch (error) {
      status.className = "load-status error";
      status.textContent = `无法读取本地记录（${error.message}）。请从仓库根目录启动 HTTP 服务器，不要直接双击 HTML 文件。`;
    }
  }

  const api = { DEFAULT_SCENARIO, buildStages, stageState, validatePayload };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof document !== "undefined") init();
})();
