let snapshot = null;
let currentLanguage = localStorage.getItem("compounding_language") || "zh";
let currentResearchTab = "news";
let selectedStrategyId = null;
const confirmedActionsKey = "confirmed_actions_v2";
const dismissedActionsKey = "dismissed_actions_v2";
let confirmedActions = new Set(JSON.parse(localStorage.getItem(confirmedActionsKey) || "[]"));
let dismissedActions = new Set(JSON.parse(localStorage.getItem(dismissedActionsKey) || "[]"));

const i18n = {
  zh: {
    brand: "个人复利系统",
    navToday: "今日",
    navPortfolio: "组合与策略",
    navSystem: "系统",
    actionBrief: "行动摘要",
    actionQueue: "持仓行动",
    dailyReport: "当前研究快照",
    reportState: "快照状态",
    currentSnapshot: "当前研究快照",
    snapshotOnly: "当前快照",
    snapshotSource: "快照来源",
    snapshotType: "分析类型",
    singleResearchSnapshot: "每日复利分析",
    researchCoverage: "研究覆盖",
    riskConclusion: "风控结论",
    positionActions: "持仓动作",
    reviewItems: "{count} 条需复核",
    confirmItems: "{count} 条待确认",
    noActionItems: "无待处理持仓",
    researchLens: "研究视角",
    compoundingSummary: "复利概览",
    compoundCurve: "复利曲线",
    performance: "收益表现",
    currentHoldings: "当前持仓",
    strategyLibrary: "策略库",
    strategyDetail: "策略详情",
    signal: "信号",
    backtestMetrics: "Backtest 指标",
    backtestRuns: "Backtest 运行记录",
    pluginApiStatus: "插件与 API 状态",
    accounts: "账户",
    automationSchedule: "自动化时间表",
    agentMemory: "运行上下文",
    agentTrace: "Agent Trace",
    agentChat: "Agent Chat",
    runWorkflow: "运行分析",
    running: "运行中",
    refresh: "刷新",
    ask: "提问",
    chatPlaceholder: "询问风险、策略、市场或收益",
    waitingAgent: "等待项目 Agent...",
    backToPortfolio: "返回组合与策略",
    noData: "暂无数据",
    na: "N/A",
    noSignal: "暂无信号",
    unassignedSignal: "全局信号",
    noBacktests: "暂无回测记录",
    notSet: "未设置",
    pendingBacktestMetric: "等待回测指标",
    pendingData: "待接入",
    pendingMetric: "等待数据",
    waitingCompoundCurve: "等待净值快照",
    yes: "是",
    no: "否",
    view: "查看",
    confirm: "记录确认",
    dismiss: "暂不处理",
    confirmed: "已记录确认",
    dismissed: "已暂不处理",
    opening: "开盘",
    closing: "收盘",
    news: "消息面",
    fundamentals: "基本面",
    technicals: "技术面",
    noAction: "无需行动",
    reviewNeeded: "需要复核",
    confirmNeeded: "需要确认",
    riskBlocked: "风控阻断",
    defineExits: "补充退出规则",
    holdReview: "持有并复核",
    wait: "等待",
    requiresCurrentPrice: "需要实时价格后由 RiskControlAgent 计算",
    researchReady: "研究就绪",
    riskGate: "Risk Gate",
    totalEquity: "总资产",
    baseCurrency: "基准货币",
    pendingActions: "待执行",
    summary: "摘要",
    exitRules: "退出规则",
    actionState: "今日结论",
    packets: "研究包",
    missingExitRules: "{count} 个持仓缺少 Stop-Loss / Take-Profit",
    exitRulesReady: "退出规则已记录",
    riskPass: "风控通过",
    riskReject: "风控拒绝",
    actionLine: "{state} · {missing} · {risk}",
    portfolioLine: "总资产：{equity} · 持仓：{positions} · 策略：{strategies}",
    strategyLine: "{strategy} · {status} · 回测 {backtests}",
    systemLine: "连接：{plugins}/{totalPlugins} · 账户：{accounts} · {broker} 模式",
    actionProposal: "Agent 建议",
    currentPosition: "当前持仓",
    thesisChange: "Thesis 变化",
    currentExit: "当前退出线",
    notLive: "未接入实时行情",
    readOnly: "只读文件",
    loaded: "已加载",
    missing: "缺失",
    connected: "已连接",
    available: "可用",
    planned: "计划中",
    pendingConnection: "待接入",
    manual: "手动 / 定时",
    liveBlocked: "实盘关闭",
    localApi: "本地 Cockpit API",
    marketData: "Market Data",
    quantConnect: "QuantConnect",
    brokerSafety: "Broker 安全",
    watchlist: "当前标的",
    strategyRegistry: "策略库状态",
    researchContext: "研究上下文",
    researchContextLoaded: "研究包已加载；长期偏好未初始化",
    todayPnl: "今日 PnL",
    compoundPoints: "净值快照",
    curveNeedsMoreSnapshots: "至少需要 2 个净值快照生成曲线",
    oneSnapshotRecorded: "已记录 1 个快照，曲线尚未形成",
    snapshotCount: "{count} 个快照",
    includedToday: "已纳入今日运行",
    notIncludedToday: "未纳入今日运行",
    trades: "交易",
    dividends: "分红",
    fxEvents: "汇率事件",
    account: "账户",
    balance: "余额",
    assets: "资产",
    access: "接入",
    readOnlyAccess: "API 只读",
    manualRecord: "手动记录",
    apiReadOnly: "API 只读",
    positions: "持仓",
    positionCount: "{count} 个持仓",
    strategyCount: "{count} 个策略",
    components: "组成",
    dailySnapshot: "每日复利快照",
    manualRefresh: "手动刷新",
    marketOpen: "未设置固定开盘时间",
    marketClose: "未设置固定收盘时间",
    user: "用户",
    moreEvidence: "另有 {count} 条证据在研究包中",
    sourceDate: "日期",
    signalSummary: "{symbol} 当前信号为 {signal}，周期 {timeframe}",
    enabled: "启用",
    disabled: "未启用",
    shares: "股",
    completedStub: "已完成（本地模拟）",
    localBacktest: "本地回测",
    strategyGroupExample: "示例",
    strategyGroupClassic: "经典",
    strategyGroupAdvanced: "进阶",
    strategyGroupFrontier: "前沿",
    localInterface: "本地接口",
    quantArtifacts: "QuantConnect 文件",
    codexPlugin: "Codex plugin",
    localResearchPackets: "公开数据 + 本地研究包",
    researchPacketLoaded: "研究包已加载",
    researchPacketMissing: "研究包缺失",
    latestRun: "最新运行",
    agentHandoff: "Agent 交接",
    packet: "数据包",
    buttonTrigger: "按钮触发",
    workflowRun: "运行",
    packetCount: "数据包数量",
  },
  en: {
    brand: "Personal Compounding OS",
    navToday: "Today",
    navPortfolio: "Portfolio & Strategies",
    navSystem: "System",
    actionBrief: "Action Brief",
    actionQueue: "Position Action Queue",
    dailyReport: "Research Snapshot",
    reportState: "Snapshot Status",
    currentSnapshot: "Current Research Snapshot",
    snapshotOnly: "Current snapshot",
    snapshotSource: "Snapshot source",
    snapshotType: "Analysis type",
    singleResearchSnapshot: "Daily compounding analysis",
    researchCoverage: "Coverage",
    riskConclusion: "Risk conclusion",
    positionActions: "Position actions",
    reviewItems: "{count} review items",
    confirmItems: "{count} items to confirm",
    noActionItems: "No position review items",
    researchLens: "Research Lens",
    compoundingSummary: "Compounding Summary",
    compoundCurve: "Compound Curve",
    performance: "Performance",
    currentHoldings: "Current Holdings",
    strategyLibrary: "Strategy Library",
    strategyDetail: "Strategy Detail",
    signal: "Signal",
    backtestMetrics: "Backtest Metrics",
    backtestRuns: "Backtest Runs",
    pluginApiStatus: "Plugin & API Status",
    accounts: "Accounts",
    automationSchedule: "Automation Schedule",
    agentMemory: "Run Context",
    agentTrace: "Agent Trace",
    agentChat: "Agent Chat",
    runWorkflow: "Run Analysis",
    running: "Running",
    refresh: "Refresh",
    ask: "Ask",
    chatPlaceholder: "Ask about risk, strategy, market, or performance",
    waitingAgent: "Waiting for project agent...",
    backToPortfolio: "Back to Portfolio & Strategies",
    noData: "No data",
    na: "N/A",
    noSignal: "No signal",
    unassignedSignal: "Global signal",
    noBacktests: "No backtest runs",
    notSet: "Not set",
    pendingBacktestMetric: "Awaiting backtest metric",
    pendingData: "Pending",
    pendingMetric: "Awaiting data",
    waitingCompoundCurve: "Waiting for equity snapshots",
    yes: "Yes",
    no: "No",
    view: "View",
    confirm: "Record confirm",
    dismiss: "Skip for now",
    confirmed: "Confirmed locally",
    dismissed: "Skipped",
    opening: "Opening",
    closing: "Closing",
    news: "News",
    fundamentals: "Fundamentals",
    technicals: "Technicals",
    noAction: "No action",
    reviewNeeded: "Review needed",
    confirmNeeded: "Confirmation needed",
    riskBlocked: "Risk blocked",
    defineExits: "Define exits",
    holdReview: "Hold and review",
    wait: "Wait",
    requiresCurrentPrice: "Requires current price and RiskControlAgent calculation",
    researchReady: "Research Ready",
    riskGate: "Risk Gate",
    totalEquity: "Total Equity",
    baseCurrency: "Base currency",
    pendingActions: "Pending Actions",
    summary: "Summary",
    exitRules: "Exit Rules",
    actionState: "Decision",
    packets: "Packets",
    missingExitRules: "{count} holdings missing Stop-Loss / Take-Profit",
    exitRulesReady: "Exit rules recorded",
    riskPass: "Risk passed",
    riskReject: "Risk rejected",
    actionLine: "{state} · {missing} · {risk}",
    portfolioLine: "equity: {equity} · positions: {positions} · strategies: {strategies}",
    strategyLine: "{strategy} · {status} · backtests {backtests}",
    systemLine: "connections: {plugins}/{totalPlugins} · accounts: {accounts} · broker {broker}",
    actionProposal: "Agent proposal",
    currentPosition: "Current position",
    thesisChange: "Thesis change",
    currentExit: "Current exit line",
    notLive: "not live-connected",
    readOnly: "read-only / artifact workflow",
    loaded: "loaded",
    missing: "missing",
    connected: "connected",
    available: "available",
    planned: "planned",
    pendingConnection: "pending connection",
    manual: "manual / scheduled",
    liveBlocked: "live disabled",
    localApi: "Local Cockpit API",
    marketData: "Market Data",
    quantConnect: "QuantConnect",
    brokerSafety: "Broker safety",
    watchlist: "Current symbols",
    strategyRegistry: "Strategy library",
    researchContext: "Research context",
    researchContextLoaded: "Research packets loaded; saved preferences not initialized",
    todayPnl: "Today PnL",
    compoundPoints: "Equity Snapshots",
    curveNeedsMoreSnapshots: "At least 2 equity snapshots are needed",
    oneSnapshotRecorded: "1 snapshot recorded; curve not formed yet",
    snapshotCount: "{count} snapshots",
    includedToday: "Included today",
    notIncludedToday: "Not included today",
    trades: "Trades",
    dividends: "Dividends",
    fxEvents: "FX Events",
    account: "Account",
    balance: "Balance",
    assets: "Assets",
    access: "Access",
    readOnlyAccess: "read-only",
    manualRecord: "manual",
    apiReadOnly: "API read-only",
    positions: "Positions",
    positionCount: "{count} positions",
    strategyCount: "{count} strategies",
    components: "Components",
    dailySnapshot: "Daily Compounding Snapshot",
    manualRefresh: "Manual Refresh",
    marketOpen: "No fixed opening time set",
    marketClose: "No fixed closing time set",
    user: "User",
    moreEvidence: "{count} more evidence items in the research packet",
    sourceDate: "Date",
    signalSummary: "{symbol} current signal is {signal} on {timeframe}",
    enabled: "Active",
    disabled: "Inactive",
    shares: "shares",
    completedStub: "Completed local stub",
    localBacktest: "Local backtest record",
    strategyGroupExample: "Example",
    strategyGroupClassic: "Classic",
    strategyGroupAdvanced: "Advanced",
    strategyGroupFrontier: "Frontier",
    localInterface: "Local interface",
    quantArtifacts: "QuantConnect files",
    codexPlugin: "Codex plugin",
    localResearchPackets: "Public data + local research packets",
    researchPacketLoaded: "research packet loaded",
    researchPacketMissing: "research packet missing",
    latestRun: "latest run",
    agentHandoff: "agent handoff",
    packet: "packet",
    buttonTrigger: "button",
    workflowRun: "run",
    packetCount: "Packets",
  },
};

const fieldLabels = {
  zh: {
    symbol: "标的",
    quantity: "数量",
    current_position: "当前持仓",
    thesis_change: "Thesis 状态",
    suggested_action: "建议动作",
    current_exit: "当前退出线",
    agent_proposal: "Agent 建议",
    exit_status: "退出规则",
    avg_cost: "Avg Cost",
    avg_price: "平均成本",
    position_size: "持仓",
    currency: "货币",
    account_id: "账户",
    strategy_id: "策略",
    status: "状态",
    signal: "信号",
    timeframe: "周期",
    experiment_id: "运行",
    run_id: "运行",
    risk_state: "风险状态",
    latest_signal: "最新信号",
    backtest_count: "回测次数",
    cagr: "CAGR",
    max_drawdown: "Max Drawdown",
    sharpe: "Sharpe",
    provider: "Provider",
    source: "来源",
    name: "名称",
    mode: "模式",
    cadence: "频率",
    owner: "负责人",
    plugin: "插件",
    connector_status: "连接状态",
    connectors: "Connectors",
    research_packet: "Research Packet",
    handoff: "Handoff",
    agent: "Agent",
    action: "操作",
    balance: "余额",
    assets: "资产",
    access: "接入",
    value: "值",
  },
  en: {
    symbol: "Symbol",
    quantity: "Quantity",
    current_position: "Current Position",
    thesis_change: "Thesis Change",
    suggested_action: "Suggested Action",
    current_exit: "Stop-Loss / Take-Profit",
    agent_proposal: "Agent Proposal",
    exit_status: "Exit Status",
    avg_cost: "Avg Cost",
    avg_price: "Avg Price",
    position_size: "Position",
    currency: "Currency",
    account_id: "Account",
    strategy_id: "Strategy ID",
    status: "Status",
    signal: "Signal",
    timeframe: "Timeframe",
    experiment_id: "Experiment",
    run_id: "Run",
    risk_state: "Risk State",
    latest_signal: "Latest Signal",
    backtest_count: "Backtests",
    cagr: "CAGR",
    max_drawdown: "Max Drawdown",
    sharpe: "Sharpe",
    provider: "Provider",
    source: "Source",
    name: "Name",
    mode: "Mode",
    cadence: "Cadence",
    owner: "Owner",
    plugin: "Plugin",
    connector_status: "Connector Status",
    connectors: "Connectors",
    research_packet: "Research Packet",
    handoff: "Handoff",
    agent: "Agent",
    action: "Action",
    balance: "Balance",
    assets: "Assets",
    access: "Access",
    value: "Value",
  },
};

document.addEventListener("DOMContentLoaded", () => {
  bindNavigation();
  bindControls();
  applyLanguage();
  loadCockpit();
});

window.addEventListener("hashchange", () => {
  routeFromHash();
});

function bindControls() {
  document.getElementById("refresh").addEventListener("click", loadCockpit);
  document.getElementById("run-workflow").addEventListener("click", runWorkflow);
  document.getElementById("language-toggle").addEventListener("click", toggleLanguage);
  document.getElementById("back-to-portfolio").addEventListener("click", () => navigateTo("#/portfolio"));
  document.getElementById("chat-form").addEventListener("submit", askAgent);
}

function bindNavigation() {
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => navigateTo(button.dataset.route));
  });
}

function navigateTo(hash) {
  if (window.location.hash === hash) {
    routeFromHash();
    return;
  }
  window.location.hash = hash;
}

function routeFromHash() {
  const hash = window.location.hash || "#/today";
  const route = parseRoute(hash);
  document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));

  if (route.page === "strategy") {
    selectedStrategyId = route.strategyId;
    document.getElementById("strategy-detail-page").classList.add("active");
    document.getElementById("nav-portfolio").classList.add("active");
  } else {
    document.getElementById(route.page).classList.add("active");
    document.getElementById(`nav-${route.page}`).classList.add("active");
  }
  renderAll();
}

function parseRoute(hash) {
  if (hash.startsWith("#/strategy/")) {
    return {page: "strategy", strategyId: decodeURIComponent(hash.replace("#/strategy/", ""))};
  }
  if (hash === "#/portfolio") return {page: "portfolio"};
  if (hash === "#/system") return {page: "system"};
  return {page: "today"};
}

function activePage() {
  const route = parseRoute(window.location.hash || "#/today");
  return route.page;
}

function t(key) {
  return i18n[currentLanguage][key] || i18n.en[key] || key;
}

function applyLanguage() {
  document.documentElement.lang = currentLanguage === "zh" ? "zh-CN" : "en";
  document.getElementById("brand-title").textContent = t("brand");
  document.getElementById("nav-today").textContent = t("navToday");
  document.getElementById("nav-portfolio").textContent = t("navPortfolio");
  document.getElementById("nav-system").textContent = t("navSystem");
  document.getElementById("language-toggle").textContent = currentLanguage === "zh" ? "EN" : "中文";
  document.getElementById("run-workflow").textContent = t("runWorkflow");
  document.getElementById("refresh").textContent = t("refresh");
  document.getElementById("back-to-portfolio").textContent = t("backToPortfolio");
  document.getElementById("chat-input").placeholder = t("chatPlaceholder");
  document.getElementById("chat-submit").textContent = t("ask");

  setText("action-brief-title", t("actionBrief"));
  setText("action-queue-title", t("actionQueue"));
  setText("daily-report-title", t("dailyReport"));
  setText("research-title", t("researchLens"));
  setText("portfolio-summary-title", t("compoundingSummary"));
  setText("compound-title", t("compoundCurve"));
  setText("performance-title", t("performance"));
  setText("holdings-title", t("currentHoldings"));
  setText("strategy-library-title", t("strategyLibrary"));
  setText("strategy-detail-title", t("strategyDetail"));
  setText("strategy-signal-title", t("signal"));
  setText("strategy-metrics-title", t("backtestMetrics"));
  setText("strategy-backtests-title", t("backtestRuns"));
  setText("plugin-status-title", t("pluginApiStatus"));
  setText("account-status-title", t("accounts"));
  setText("automation-title", t("automationSchedule"));
  setText("memory-title", t("agentMemory"));
  setText("trace-title", t("agentTrace"));
  setText("chat-title", t("agentChat"));
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
}

function toggleLanguage() {
  currentLanguage = currentLanguage === "zh" ? "en" : "zh";
  localStorage.setItem("compounding_language", currentLanguage);
  renderAll();
}

async function loadCockpit() {
  const response = await fetch("/api/cockpit", {cache: "no-store"});
  snapshot = await response.json();
  if (!window.location.hash) window.location.hash = "#/today";
  routeFromHash();
}

async function runWorkflow() {
  const button = document.getElementById("run-workflow");
  button.disabled = true;
  button.textContent = t("running");
  try {
    await fetch("/api/run/daily-compounding", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: "{}",
    });
    await loadCockpit();
  } finally {
    button.disabled = false;
    button.textContent = t("runWorkflow");
  }
}

async function askAgent(event) {
  event.preventDefault();
  const input = document.getElementById("chat-input");
  const output = document.getElementById("chat-output");
  const message = input.value.trim();
  if (!message) return;
  output.textContent = t("waitingAgent");
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message}),
  });
  const payload = await response.json();
  output.textContent = [
    payload.agent,
    localizedNarrative(payload.message),
    "",
    `${t("workflowRun")}: ${workflowDisplay(payload.workflow_id)}`,
    `${labelFor("source")}: ${localizedNarrative(payload.source)}`,
    `limitations: ${(payload.limitations || []).map(localizedNarrative).join("; ") || "none"}`,
  ].join("\n");
}

function renderAll() {
  applyLanguage();
  if (!snapshot) return;
  renderHeader();
  renderToday();
  renderPortfolio();
  renderStrategyDetail();
  renderSystem();
}

function renderHeader() {
  const page = activePage();
  const route = parseRoute(window.location.hash || "#/today");
  const titleMap = {
    today: t("navToday"),
    portfolio: t("navPortfolio"),
    strategy: t("strategyDetail"),
    system: t("navSystem"),
  };
  document.getElementById("section-title").textContent = titleMap[page] || t("navToday");
  document.getElementById("context-line").textContent = contextLine(route);
}

function contextLine(route) {
  const risk = snapshot.portfolio_risk || {};
  const metrics = snapshot.top_metrics || {};
  const strategy = snapshot.strategy_center || {};
  const pluginCounts = researchPacketCounts();
  if (route.page === "today") {
    const state = actionDecision().label;
    const missing = missingExitSymbolSet().size;
    const missingText = missing ? t("missingExitRules").replace("{count}", String(missing)) : t("exitRulesReady");
    const riskText = risk.risk_decision === "PASS" ? t("riskPass") : t("riskReject");
    return t("actionLine").replace("{state}", state).replace("{missing}", missingText).replace("{risk}", riskText);
  }
  if (route.page === "portfolio") {
    return t("portfolioLine")
      .replace("{equity}", portfolioEquityText(metrics))
      .replace("{positions}", String((risk.positions || []).length))
      .replace("{strategies}", String(strategy.strategy_library_summary?.total_count || 0));
  }
  if (route.page === "strategy") {
    const detail = selectedStrategySummary(route.strategyId);
    return t("strategyLine")
      .replace("{strategy}", strategyDisplayName(detail.strategyId) || "unknown")
      .replace("{status}", strategyStatusLabel(detail.active))
      .replace("{backtests}", String(detail.experiments.length));
  }
  return t("systemLine")
    .replace("{plugins}", String(pluginCounts.loaded))
    .replace("{totalPlugins}", String(pluginCounts.total))
    .replace("{accounts}", String((risk.accounts || []).length))
    .replace("{broker}", risk.checks?.broker_mode || "unknown");
}

function renderToday() {
  renderActionBrief();
  renderActionQueue();
  renderDailyReport();
  renderResearchTabs();
}

function renderActionBrief() {
  const decision = actionDecision();
  const counts = researchPacketCounts();
  const missingExitCount = missingExitSymbolSet().size;
  const risk = snapshot.portfolio_risk || {};
  document.getElementById("action-brief-meta").textContent = workflowDisplay(snapshot.workflow_id);
  const cards = [
    {label: t("actionState"), value: decision.label, tone: decision.tone},
    {label: t("researchReady"), value: `${counts.loaded}/${counts.total}`, tone: counts.loaded === counts.total ? "pass" : "warn"},
    {label: t("riskGate"), value: risk.risk_decision || "unknown", tone: risk.risk_decision === "PASS" ? "pass" : "danger"},
    {
      label: t("exitRules"),
      value: missingExitCount ? t("missingExitRules").replace("{count}", String(missingExitCount)) : t("exitRulesReady"),
      tone: missingExitCount ? "warn" : "pass",
    },
  ];
  document.getElementById("action-brief").innerHTML = cards.map((card) => `
    <div class="brief-card ${escapeHtml(card.tone)}">
      <span>${escapeHtml(card.label)}</span>
      <strong>${escapeHtml(card.value)}</strong>
    </div>
  `).join("");
}

function actionDecision() {
  const risk = snapshot.portfolio_risk || {};
  const execution = snapshot.execution_desk || {};
  if (risk.risk_decision === "REJECT" || risk.risk_decision === "HALT") {
    return {label: t("riskBlocked"), tone: "danger"};
  }
  if ((execution.pending_actions || []).length) {
    return {label: t("confirmNeeded"), tone: "warn"};
  }
  if (missingExitSymbolSet().size) {
    return {label: t("reviewNeeded"), tone: "warn"};
  }
  return {label: t("noAction"), tone: "pass"};
}

function renderActionQueue() {
  const rows = actionQueueRows();
  document.getElementById("action-queue-meta").textContent = t("positionCount").replace("{count}", String(rows.length));
  document.getElementById("position-action-queue").innerHTML = tableFromObjects(rows, {
    actionRenderer: actionQueueActionCell,
  });
  document.querySelectorAll(".confirm-action").forEach((button) => {
    button.addEventListener("click", () => confirmAction(button.dataset.actionId));
  });
  document.querySelectorAll(".dismiss-action").forEach((button) => {
    button.addEventListener("click", () => dismissAction(button.dataset.actionId));
  });
}

function actionQueueRows() {
  const risk = snapshot.portfolio_risk || {};
  const positions = risk.positions || [];
  const exits = risk.stop_loss_take_profit || [];
  const impacts = thesisImpacts();
  const missingSymbols = missingExitSymbolSet();
  return positions.map((position) => {
    const symbol = position.symbol || "unknown";
    const exit = exits.find((item) => item.symbol === symbol) || {};
    const thesis = impacts.find((item) => item.symbol === symbol) || {};
    const needsExit = missingSymbols.has(symbol) || (exit.stop_loss == null && exit.take_profit == null);
    const actionId = `exit-${symbol}`;
    return {
      symbol,
      current_position: positionSize(position),
      thesis_change: thesisImpactLabel(thesis),
      suggested_action: needsExit ? t("defineExits") : t("holdReview"),
      current_exit: `SL: ${exit.stop_loss ?? t("notSet")} / TP: ${exit.take_profit ?? t("notSet")}`,
      agent_proposal: needsExit ? t("requiresCurrentPrice") : t("holdReview"),
      action: actionQueueState(actionId),
    };
  });
}

function actionQueueState(actionId) {
  if (confirmedActions.has(actionId)) return `confirmed:${actionId}`;
  if (dismissedActions.has(actionId)) return `dismissed:${actionId}`;
  return actionId;
}

function actionQueueActionCell(value) {
  if (String(value).startsWith("confirmed:")) return statusBadge(t("confirmed"));
  if (String(value).startsWith("dismissed:")) return `<span class="muted">${escapeHtml(t("dismissed"))}</span>`;
  return `
    <div class="inline-actions">
      <button class="inline-button confirm-action" data-action-id="${escapeHtml(value)}">${escapeHtml(t("confirm"))}</button>
      <button class="inline-button dismiss-action" data-action-id="${escapeHtml(value)}">${escapeHtml(t("dismiss"))}</button>
    </div>
  `;
}

function thesisImpactLabel(thesis) {
  const value = thesis.status || thesis.impact || "";
  if (!value) return t("noData");
  if (currentLanguage === "zh") {
    if (value === "company_thesis_intact") return "公司 Thesis 未破坏";
    if (value === "company_thesis_strengthening") return "公司 Thesis 加强";
    if (value === "coverage_profile_loaded") return "覆盖资料已加载";
    if (value === "benchmark_context_loaded") return "基准背景已加载";
  }
  return humanizeCode(value);
}

async function confirmAction(actionId) {
  await fetch("/api/actions/confirm", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({action_id: actionId}),
  });
  dismissedActions.delete(actionId);
  confirmedActions.add(actionId);
  localStorage.setItem(confirmedActionsKey, JSON.stringify([...confirmedActions]));
  localStorage.setItem(dismissedActionsKey, JSON.stringify([...dismissedActions]));
  renderActionQueue();
}

function dismissAction(actionId) {
  confirmedActions.delete(actionId);
  dismissedActions.add(actionId);
  localStorage.setItem(confirmedActionsKey, JSON.stringify([...confirmedActions]));
  localStorage.setItem(dismissedActionsKey, JSON.stringify([...dismissedActions]));
  renderActionQueue();
}

function renderDailyReport() {
  const risk = snapshot.portfolio_risk || {};
  document.getElementById("report-status").innerHTML = `<span class="meta-pill">${escapeHtml(t("snapshotOnly"))}</span>`;
  document.getElementById("daily-report").innerHTML = `
    ${rows([
      [t("snapshotSource"), pluginReadinessText(snapshot.market_lens?.external_sources || {})],
      [t("snapshotType"), t("singleResearchSnapshot")],
      [t("researchCoverage"), researchCoverageText()],
      [t("riskConclusion"), localizedNarrative(risk.reason)],
      [t("positionActions"), positionActionSummary()],
    ])}
  `;
}

function researchCoverageText() {
  const symbols = watchlist();
  const counts = researchPacketCounts();
  const coverage = symbols.length ? symbols.join(", ") : t("noData");
  return `${coverage} · ${counts.loaded}/${counts.total} ${t("packets")}`;
}

function positionActionSummary() {
  const execution = snapshot.execution_desk || {};
  const pendingActions = (execution.pending_actions || []).length;
  const missingExits = missingExitSymbolSet().size;
  if (pendingActions) return t("confirmItems").replace("{count}", String(pendingActions));
  if (missingExits) return t("reviewItems").replace("{count}", String(missingExits));
  return t("noActionItems");
}

function renderResearchTabs() {
  const tabs = [
    {id: "news", label: t("news")},
    {id: "fundamentals", label: t("fundamentals")},
    {id: "technicals", label: t("technicals")},
  ];
  document.getElementById("research-tabs").innerHTML = tabs.map((tab) => tabButton(tab, currentResearchTab)).join("");
  document.querySelectorAll("#research-tabs .segment").forEach((button) => {
    button.addEventListener("click", () => {
      currentResearchTab = button.dataset.tab;
      renderResearchTabs();
    });
  });
  const lens = snapshot.market_lens || {};
  if (currentResearchTab === "technicals") {
    document.getElementById("research-lens").innerHTML = evidenceList(lens.technicals?.signals || []);
    return;
  }
  const section = lens[currentResearchTab] || {};
  const items = researchItemsForTab(currentResearchTab, section.items || []);
  document.getElementById("research-lens").innerHTML = rows([[t("summary"), localizedNarrative(section.summary)]]) +
    evidenceList(items);
}

function researchItemsForTab(tabId, items) {
  const dimensionsByTab = {
    news: ["macro", "sector_sentiment", "price_action", "market_context"],
    fundamentals: [
      "fundamentals",
      "company_tearsheet",
      "issuer_actions",
      "market_benchmark",
      "portfolio_exposure",
      "portfolio_concentration",
      "screening_comps",
      "transaction_read",
    ],
  };
  const allowed = dimensionsByTab[tabId] || [];
  if (!allowed.length) return items;
  const filtered = items.filter((item) => allowed.includes(item.dimension));
  return filtered.length ? filtered : items;
}

function tabButton(tab, activeId) {
  return `<button class="segment ${tab.id === activeId ? "active" : ""}" data-tab="${escapeHtml(tab.id)}" type="button">${escapeHtml(tab.label)}</button>`;
}

function evidenceList(items) {
  if (!items.length) return `<div class="empty">${escapeHtml(t("noData"))}</div>`;
  const visibleItems = items.slice(0, 6);
  const hiddenCount = Math.max(items.length - visibleItems.length, 0);
  return `
    <div class="evidence-list">
      ${visibleItems.map((item) => evidenceItem(item)).join("")}
      ${hiddenCount ? `<div class="evidence-more">${escapeHtml(t("moreEvidence").replace("{count}", String(hiddenCount)))}</div>` : ""}
    </div>
  `;
}

function evidenceItem(item) {
  const symbol = item.symbol || item.dimension || item.timeframe || t("na");
  const signal = item.signal || item.status || item.readiness || item.dimension || t("na");
  const summary = evidenceSummary(item);
  const source = item.source || item.name || item.source_url || "";
  const sourceDate = item.source_date || item.retrieved_at || "";
  const dimension = dimensionLabel(item.dimension);
  return `
    <article class="evidence-item">
      <div class="evidence-topline">
        <strong>${escapeHtml(symbol)}</strong>
        ${statusBadge(signal)}
      </div>
      <p>${escapeHtml(summary)}</p>
      <div class="evidence-meta">
        ${dimension ? `<span>${escapeHtml(dimension)}</span>` : ""}
        ${source ? `<span>${escapeHtml(source)}</span>` : ""}
        ${sourceDate ? `<span>${escapeHtml(t("sourceDate"))}: ${escapeHtml(sourceDate)}</span>` : ""}
      </div>
    </article>
  `;
}

function dimensionLabel(dimension) {
  if (!dimension) return "";
  if (currentLanguage !== "zh") return humanizeCode(dimension);
  const labels = {
    macro: "宏观",
    sector_sentiment: "板块情绪",
    price_action: "价格动作",
    market_context: "市场环境",
    fundamentals: "公司财务",
    company_tearsheet: "公司资料",
    issuer_actions: "公司行动",
    market_benchmark: "市场基准",
    portfolio_exposure: "组合敞口",
    portfolio_concentration: "持仓重叠",
    screening_comps: "同业筛选",
    transaction_read: "交易视角",
  };
  return labels[dimension] || humanizeCode(dimension);
}

function evidenceSummary(item) {
  if (item.summary || item.banker_read || item.impact || item.reported_metrics) {
    return localizedNarrative(item.summary || item.banker_read || item.impact || item.reported_metrics);
  }
  if (item.symbol && item.signal) {
    return t("signalSummary")
      .replace("{symbol}", item.symbol)
      .replace("{signal}", item.signal)
      .replace("{timeframe}", item.timeframe || t("na"));
  }
  return t("noData");
}

function renderPortfolio() {
  const risk = snapshot.portfolio_risk || {};
  const performance = snapshot.performance_journal || {};
  const ledgerCounts = performance.pnl?.ledger_counts || {};
  const metrics = snapshot.top_metrics || {};
  document.getElementById("portfolio-summary-meta").textContent = `${t("baseCurrency")} ${metrics.base_currency || t("na")}`;
  document.getElementById("portfolio-metrics").innerHTML = metricCards([
    [t("totalEquity"), moneyOrPending(metrics.total_equity, metrics.base_currency)],
    [t("todayPnl"), moneyOrPending(metrics.today_pnl, metrics.base_currency)],
    ["CAGR", metricPercentOrPending(performance.cagr, performance.compound_curve || [])],
    ["Max Drawdown", metricPercentOrPending(performance.max_drawdown, performance.compound_curve || [])],
  ]);
  drawCompoundCurve(performance.compound_curve || []);
  document.getElementById("performance-summary").innerHTML = rows([
    [t("compoundPoints"), compoundSnapshotText(performance.compound_curve || [])],
    [t("trades"), ledgerCounts.trades],
    [t("dividends"), ledgerCounts.dividends],
    [t("fxEvents"), ledgerCounts.fx],
  ]);
  const holdings = (risk.positions || []).map((position) => positionRow(position, risk.accounts || []));
  document.getElementById("holdings-meta").textContent = t("positionCount").replace("{count}", String(holdings.length));
  document.getElementById("portfolio-holdings").innerHTML = tableFromObjects(holdings);
  renderStrategyLibrary();
}

function positionRow(position, accounts) {
  return {
    symbol: position.symbol,
    position_size: positionSize(position),
    avg_price: `${formatAmount(position.avg_cost)} ${position.currency || ""}`.trim(),
    account_id: accountNameForPosition(position, accounts),
    exit_status: missingExitSymbolSet().has(position.symbol) ? t("defineExits") : t("exitRulesReady"),
  };
}

function positionSize(position) {
  const quantity = formatQuantity(position.quantity);
  if (position.sec_type === "STK") return `${quantity} ${t("shares")}`;
  return quantity;
}

function accountNameForPosition(position, accounts) {
  const account = accounts.find((item) => item.account_id === position.account_id);
  if (account) return accountDisplayName(account);
  return humanizeCode(position.account_id) || t("na");
}

function renderStrategyLibrary() {
  const strategy = snapshot.strategy_center || {};
  const library = strategy.strategy_library_summary?.strategies || [];
  const activeStrategies = strategy.active_strategies || [];
  document.getElementById("strategy-library-meta").textContent = t("strategyCount").replace("{count}", String(library.length));
  if (!library.length) {
    document.getElementById("strategy-library").innerHTML = `<div class="empty">${escapeHtml(t("noData"))}</div>`;
    return;
  }
  const rows = library.map((strategyId) => {
    const signal = latestSignalForStrategy(strategyId, {allowGlobal: activeStrategies.includes(strategyId)});
    return {
      strategy_id: strategyDisplayName(strategyId),
      status: strategyStatusLabel(activeStrategies.includes(strategyId)),
      latest_signal: latestSignalText(signal),
      backtest_count: experimentsForStrategy(strategyId).length,
      risk_state: strategyRunState(activeStrategies.includes(strategyId)),
      action: strategyId,
    };
  });
  document.getElementById("strategy-library").innerHTML = tableFromObjects(rows, {
    actionRenderer: (strategyId) => `<button class="inline-button strategy-button" data-strategy-id="${escapeHtml(strategyId)}">${escapeHtml(t("view"))}</button>`,
  });
  document.querySelectorAll(".strategy-button").forEach((button) => {
    button.addEventListener("click", () => navigateTo(`#/strategy/${encodeURIComponent(button.dataset.strategyId)}`));
  });
}

function renderStrategyDetail() {
  const route = parseRoute(window.location.hash || "#/today");
  const detail = selectedStrategySummary(route.strategyId);
  if (!detail.strategyId) {
    document.getElementById("strategy-detail-meta").textContent = t("noData");
    document.getElementById("strategy-detail-overview").innerHTML = `<div class="empty">${escapeHtml(t("noData"))}</div>`;
    document.getElementById("strategy-detail-signals").innerHTML = `<div class="empty">${escapeHtml(t("noData"))}</div>`;
    document.getElementById("strategy-detail-metrics").innerHTML = `<div class="empty">${escapeHtml(t("noData"))}</div>`;
    document.getElementById("strategy-detail-backtests").innerHTML = `<div class="empty">${escapeHtml(t("noData"))}</div>`;
    return;
  }
  document.getElementById("strategy-detail-meta").textContent = strategyStatusLabel(detail.active);
  document.getElementById("strategy-detail-overview").innerHTML = rows([
    [labelFor("strategy_id"), strategyDisplayName(detail.strategyId)],
    [labelFor("status"), strategyStatusLabel(detail.active)],
    [labelFor("risk_state"), strategyRunState(detail.active)],
    [labelFor("backtest_count"), `${detail.experiments.length}`],
  ]);
  document.getElementById("strategy-detail-signals").innerHTML = detail.signals.length
    ? tableFromObjects(detail.signals)
    : `<div class="empty">${escapeHtml(t("noSignal"))}</div>`;
  document.getElementById("strategy-detail-metrics").innerHTML = rows([
    [labelFor("cagr"), t("pendingBacktestMetric")],
    [labelFor("max_drawdown"), t("pendingBacktestMetric")],
    [labelFor("sharpe"), t("pendingBacktestMetric")],
  ]);
  document.getElementById("strategy-detail-backtests").innerHTML = detail.experiments.length
    ? tableFromObjects(backtestRunRows(detail.experiments))
    : `<div class="empty">${escapeHtml(t("noBacktests"))}</div>`;
}

function backtestRunRows(experiments) {
  return experiments.map((experiment) => ({
    run_id: backtestRunLabel(experiment.experiment_id),
    status: backtestStatusLabel(experiment.status),
    strategy_id: strategyDisplayName(experiment.strategy_id) || t("na"),
    source: t("localBacktest"),
  }));
}

function backtestRunLabel(experimentId) {
  const match = String(experimentId || "").match(/^exp_(\d{4})(\d{2})(\d{2})_(.+)$/);
  if (!match) return humanizeCode(experimentId) || t("na");
  return `${match[1]}-${match[2]}-${match[3]} · #${match[4]}`;
}

function backtestStatusLabel(status) {
  if (status === "completed_stub") return t("completedStub");
  return humanizeCode(status) || t("na");
}

function renderSystem() {
  const risk = snapshot.portfolio_risk || {};
  const trace = snapshot.agent_trace || {};
  document.getElementById("system-sources").innerHTML = tableFromObjects(systemStatusRows());
  document.getElementById("system-accounts").innerHTML = tableFromObjects(systemAccountRows(risk.accounts || []));
  document.getElementById("system-automation").innerHTML = tableFromObjects([
    {name: t("opening"), mode: t("pendingConnection"), cadence: t("marketOpen"), owner: "ResearchAgent"},
    {name: t("closing"), mode: t("pendingConnection"), cadence: t("marketClose"), owner: "ResearchAgent"},
    {name: t("dailySnapshot"), mode: t("available"), cadence: t("manual"), owner: "LeaderAgent"},
    {name: t("manualRefresh"), mode: t("available"), cadence: t("buttonTrigger"), owner: t("user")},
  ]);
  document.getElementById("system-memory").innerHTML = rows([
    [t("brokerSafety"), `${risk.checks?.broker_mode || "unknown"} · ${t("liveBlocked")}`],
    [t("watchlist"), watchlist().join(", ") || t("noData")],
    [t("strategyRegistry"), t("strategyCount").replace("{count}", String(snapshot.strategy_center?.strategy_library_summary?.total_count || 0))],
    [t("researchContext"), t("researchContextLoaded")],
  ]);
  document.getElementById("trace-list").innerHTML = tableFromObjects(systemTraceRows(trace));
}

function systemAccountRows(accounts) {
  return accounts.map((account) => ({
    account_id: accountDisplayName(account),
    balance: accountBalance(account),
    assets: accountAssets(account),
    access: accountAccess(account),
    source: accountSourceLabel(account.source),
  }));
}

function accountDisplayName(account) {
  if (account.account_ref) return `${account.provider || t("account")} ${account.account_ref}`;
  if (account.provider) return account.provider;
  return humanizeCode(account.account_id) || t("na");
}

function accountBalance(account) {
  if (account.net_liquidation?.amount != null) {
    return `${formatAmount(account.net_liquidation.amount)} ${account.net_liquidation.currency || account.base_currency || ""}`.trim();
  }
  if (account.total_amount != null) {
    return `${formatAmount(account.total_amount)} ${account.currency || ""}`.trim();
  }
  if (account.amount != null) {
    return `${formatAmount(account.amount)} ${account.currency || ""}`.trim();
  }
  return t("na");
}

function accountAssets(account) {
  if (Array.isArray(account.positions) && account.positions.length) {
    const symbols = account.positions.map((position) => position.symbol).filter(Boolean).join(", ");
    return `${account.positions.length} ${t("positions")}${symbols ? ` · ${symbols}` : ""}`;
  }
  if (Array.isArray(account.components) && account.components.length) {
    const total = account.components
      .map((component) => accountComponentName(component.name || component.asset_type))
      .filter(Boolean)
      .join(", ");
    return `${account.components.length} ${t("components")}${total ? ` · ${total}` : ""}`;
  }
  return humanizeAssetType(account.asset_type) || t("na");
}

function accountAccess(account) {
  if (account.read_only_configured) return t("apiReadOnly");
  if (account.source === "manual_user_report") return t("manualRecord");
  if (String(account.source || "").includes("api")) return t("readOnlyAccess");
  return t("manualRecord");
}

function accountSourceLabel(source) {
  if (source === "ibkr_api") return "IBKR API";
  if (source === "manual_user_report") return t("manualRecord");
  return humanizeCode(source) || t("na");
}

function humanizeCode(value) {
  if (!value) return "";
  return String(value).replaceAll("_", " ");
}

function humanizeAssetType(value) {
  if (!value) return "";
  if (currentLanguage === "zh" && value === "cash_like") return "现金类";
  if (currentLanguage === "zh" && value === "cash") return "现金";
  return String(value).replaceAll("_", "-");
}

function accountComponentName(value) {
  if (!value) return "";
  if (currentLanguage === "zh") {
    const map = {
      "BSU deposit": "BSU 存款",
      "Three-month fixed deposit": "三个月定期存款",
      Balance: "现金余额",
    };
    if (map[value]) return map[value];
  }
  return value;
}

function systemStatusRows() {
  const externalSources = snapshot.market_lens?.external_sources || {};
  const connected = externalSources.connected || {};
  return [
    {name: t("localApi"), status: t("connected"), source: t("localInterface")},
    {name: t("quantConnect"), status: t("readOnly"), source: t("quantArtifacts")},
    {name: t("marketData"), status: t("notLive"), source: t("localResearchPackets")},
    {
      name: "Public Equity Investing",
      status: connected.public_equity_investing ? t("loaded") : t("missing"),
      source: pluginStatusSummary(externalSources, "public_equity_investing"),
    },
    {
      name: "Investment Banking",
      status: connected.investment_banking ? t("loaded") : t("missing"),
      source: pluginStatusSummary(externalSources, "investment_banking"),
    },
  ];
}

function systemTraceRows(trace) {
  const packets = trace.packets || [];
  return [
    {name: "Workflow", value: workflowDisplay(trace.workflow_id), source: t("latestRun")},
    {name: t("packetCount"), value: String(packets.length), source: t("agentHandoff")},
    ...packets.map((packet) => ({
      name: tracePacketName(packet.name),
      value: packet.agent || t("na"),
      source: t("packet"),
    })),
  ];
}

function selectedStrategySummary(strategyId) {
  const strategy = snapshot?.strategy_center || {};
  const library = strategy.strategy_library_summary?.strategies || [];
  const selected = strategyId || selectedStrategyId || (strategy.active_strategies || [])[0] || library[0] || null;
  const active = (strategy.active_strategies || []).includes(selected);
  selectedStrategyId = selected;
  return {
    strategyId: selected,
    active,
    signals: signalsForStrategy(selected, {allowGlobal: active}),
    experiments: experimentsForStrategy(selected),
  };
}

function strategyStatusLabel(active) {
  return active ? t("enabled") : t("disabled");
}

function strategyRunState(active) {
  return active ? t("includedToday") : t("notIncludedToday");
}

function strategyDisplayName(strategyId) {
  if (!strategyId) return "";
  const group = strategyGroupLabel(strategyId);
  const normalized = String(strategyId)
    .replace(/_v\d+$/i, "")
    .replace(/^(example|classic|advanced|frontier)_/i, "");
  const name = normalized
    .split("_")
    .filter(Boolean)
    .map(formatStrategyToken)
    .join(" ");
  return group ? `${group} · ${name}` : name;
}

function strategyGroupLabel(strategyId) {
  if (strategyId.startsWith("example_")) return t("strategyGroupExample");
  if (strategyId.startsWith("classic_")) return t("strategyGroupClassic");
  if (strategyId.startsWith("advanced_")) return t("strategyGroupAdvanced");
  if (strategyId.startsWith("frontier_")) return t("strategyGroupFrontier");
  return "";
}

function formatStrategyToken(token) {
  const upper = {
    ma: "MA",
    rsi2: "RSI2",
    ml: "ML",
    etf: "ETF",
    vix: "VIX",
  };
  const normalized = token.toLowerCase();
  if (upper[normalized]) return upper[normalized];
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}

function latestSignalForStrategy(strategyId, options = {}) {
  return signalsForStrategy(strategyId, options)[0] || null;
}

function signalsForStrategy(strategyId, options = {}) {
  const signals = snapshot.strategy_center?.signals || [];
  const ownedSignals = signals.filter((signal) => signal.strategy_id === strategyId);
  if (ownedSignals.length) return ownedSignals;
  if (options.allowGlobal) {
    return signals.filter((signal) => !signal.strategy_id).map((signal) => ({...signal, source: t("unassignedSignal")}));
  }
  return [];
}

function latestSignalText(signal) {
  if (!signal) return t("noSignal");
  return [signal.symbol, signal.signal].filter(Boolean).join(" · ") || t("noData");
}

function experimentsForStrategy(strategyId) {
  const experiments = snapshot.strategy_center?.strategy_library_summary?.experiments || [];
  return experiments.filter((item) => item.strategy_id === strategyId);
}

function researchPacketCounts() {
  const externalSources = snapshot.market_lens?.external_sources || {};
  return researchPacketCountsFromSources(externalSources);
}

function pluginReadinessText(externalSources) {
  const {loaded, total} = researchPacketCountsFromSources(externalSources);
  return `${loaded}/${total} ${t("loaded")}`;
}

function researchPacketCountsFromSources(externalSources) {
  const packets = externalSources.research_packets_loaded || {};
  const packetValues = Object.values(packets);
  if (packetValues.length) {
    return {
      loaded: packetValues.filter(Boolean).length,
      total: Object.keys(packets).length,
    };
  }
  const connected = externalSources.connected || {};
  const pluginKeys = ["public_equity_investing", "investment_banking"].filter((key) => key in connected);
  return {
    loaded: pluginKeys.filter((key) => Boolean(connected[key])).length,
    total: pluginKeys.length || 2,
  };
}

function pluginStatusSummary(externalSources, name) {
  const plugin = externalSources.connector_status?.plugins?.[name] || {};
  const source = externalSources.sources?.[name] || {};
  const connectors = connectorSummary(plugin.connectors || []);
  const packetStatus = plugin.research_packet_status || source._source_status || "unknown";
  const packetText = researchPacketStatusText(packetStatus);
  if (connectors === t("noData")) return `${t("codexPlugin")} · ${packetText}`;
  return `${t("codexPlugin")} · ${connectors} · ${packetText}`;
}

function connectorSummary(connectors) {
  if (!Array.isArray(connectors) || !connectors.length) return t("noData");
  return connectors.map((connector) => `${connector.name || "connector"} ${translateStatus(connector.status || "unknown")}`).join(", ");
}

function researchPacketStatusText(status) {
  const normalized = String(status || "").toLowerCase();
  if (normalized === "loaded") return t("researchPacketLoaded");
  if (normalized === "missing") return t("researchPacketMissing");
  return translateStatus(status);
}

function tracePacketName(name) {
  const zh = {
    research_packet: "研究数据包",
    strategy_packet: "策略数据包",
    risk_packet: "风控数据包",
    execution_packet: "执行数据包",
    performance_packet: "收益数据包",
  };
  const en = {
    research_packet: "Research packet",
    strategy_packet: "Strategy packet",
    risk_packet: "Risk packet",
    execution_packet: "Execution packet",
    performance_packet: "Performance packet",
  };
  const map = currentLanguage === "zh" ? zh : en;
  return map[name] || humanizeCode(name) || t("na");
}

function missingExitSymbolSet() {
  const risk = snapshot.portfolio_risk || {};
  return new Set((risk.alerts || []).flatMap((alert) => alert.symbols || []));
}

function thesisImpacts() {
  const sources = snapshot.market_lens?.external_sources?.sources || {};
  return Object.values(sources).flatMap((source) => Array.isArray(source.thesis_impacts) ? source.thesis_impacts : []);
}

function watchlist() {
  const positions = snapshot.portfolio_risk?.positions || [];
  const signals = snapshot.strategy_center?.signals || [];
  return [...new Set([
    ...positions.map((item) => item.symbol).filter(Boolean),
    ...signals.map((item) => item.symbol).filter(Boolean),
  ])];
}

function rows(items) {
  return `<div class="kv-list">${items.map(([label, value]) => `
    <div class="kv-row"><span>${escapeHtml(label)}</span><strong>${escapeHtml(formatValue(value))}</strong></div>
  `).join("")}</div>`;
}

function metricCards(items) {
  return items.map(([label, value]) => `
    <div class="metric">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(formatValue(value))}</strong>
    </div>
  `).join("");
}

function tableFromObjects(items, options = {}) {
  if (!items.length) return `<div class="empty">${escapeHtml(t("noData"))}</div>`;
  const keys = [...new Set(items.flatMap((item) => Object.keys(item)))];
  return `<div class="table-wrap"><table><thead><tr>${keys.map((key) => `<th>${escapeHtml(labelFor(key))}</th>`).join("")}</tr></thead><tbody>
    ${items.map((item) => `<tr>${keys.map((key) => `<td>${cellValue(key, item[key], options)}</td>`).join("")}</tr>`).join("")}
  </tbody></table></div>`;
}

function cellValue(key, value, options) {
  if (key === "action" && options.actionRenderer) return options.actionRenderer(value);
  if (isStatusField(key)) return statusBadge(value);
  return escapeHtml(formatValue(value));
}

function isStatusField(key) {
  return ["status", "risk_state", "exit_status", "suggested_action", "access", "mode"].includes(key);
}

function statusBadge(value) {
  const text = statusText(value);
  return `<span class="status-badge ${statusTone(`${value} ${text}`)}">${escapeHtml(text)}</span>`;
}

function statusText(value) {
  return formatValue(translateStatus(value));
}

function statusTone(value) {
  const normalized = String(value || "").toLowerCase();
  if (
    normalized.includes("inactive") ||
    normalized.includes("review") ||
    normalized.includes("wait") ||
    normalized.includes("manual") ||
    normalized.includes("planned") ||
    normalized.includes("not live") ||
    normalized.includes("watch") ||
    normalized.includes("risk") ||
    normalized.includes("未启用") ||
    normalized.includes("补充") ||
    normalized.includes("复核") ||
    normalized.includes("等待") ||
    normalized.includes("未纳入") ||
    normalized.includes("计划") ||
    normalized.includes("未接入") ||
    normalized.includes("待接入") ||
    normalized.includes("not included") ||
    normalized.includes("pending connection")
  ) {
    return "warn";
  }
  if (
    normalized.includes("pass") ||
    normalized.includes("positive") ||
    normalized.includes("正面") ||
    normalized.includes("active") ||
    normalized.includes("loaded") ||
    normalized.includes("connected") ||
    normalized.includes("available") ||
    normalized.includes("ready") ||
    normalized.includes("completed") ||
    normalized.includes("confirmed") ||
    normalized.includes("included today") ||
    normalized.includes("read-only") ||
    normalized.includes("只读") ||
    normalized.includes("启用") ||
    normalized.includes("已纳入") ||
    normalized.includes("已加载") ||
    normalized.includes("已连接") ||
    normalized.includes("可用") ||
    normalized.includes("完成") ||
    normalized.includes("通过") ||
    normalized.includes("已记录")
  ) {
    return "pass";
  }
  if (
    normalized.includes("missing") ||
    normalized.includes("reject") ||
    normalized.includes("halt") ||
    normalized.includes("blocked") ||
    normalized.includes("negative") ||
    normalized.includes("负面") ||
    normalized.includes("缺失") ||
    normalized.includes("拒绝") ||
    normalized.includes("阻断")
  ) {
    return "danger";
  }
  return "neutral";
}

function labelFor(key) {
  return fieldLabels[currentLanguage][key] || fieldLabels.zh[key] || key;
}

function formatValue(value) {
  if (value === null || value === undefined || value === "") return t("na");
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(4);
  if (typeof value === "boolean") return value ? t("yes") : t("no");
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function formatAmount(value) {
  const number = Number(value);
  if (Number.isNaN(number)) return formatValue(value);
  return number.toLocaleString(currentLanguage === "zh" ? "zh-CN" : "en-US", {
    maximumFractionDigits: 2,
    minimumFractionDigits: Number.isInteger(number) ? 0 : 2,
  });
}

function portfolioEquityText(metrics) {
  if (metrics.total_equity === null || metrics.total_equity === undefined || metrics.total_equity === "") {
    return t("pendingData");
  }
  return `${formatAmount(metrics.total_equity)} ${metrics.base_currency || ""}`.trim();
}

function moneyOrPending(value, currency) {
  if (value === null || value === undefined || value === "") return t("pendingData");
  return `${formatAmount(value)} ${currency || ""}`.trim();
}

function formatQuantity(value) {
  const number = Number(value);
  if (Number.isNaN(number)) return formatValue(value);
  return number.toLocaleString(currentLanguage === "zh" ? "zh-CN" : "en-US", {
    maximumFractionDigits: 4,
  });
}

function formatPercent(value) {
  if (value === null || value === undefined || value === "") return t("na");
  const number = Number(value);
  if (Number.isNaN(number)) return String(value);
  return `${(number * 100).toFixed(2)}%`;
}

function metricPercentOrPending(value, compoundRows = []) {
  if (value === null || value === undefined || value === "") {
    return compoundRows.length < 2 ? t("curveNeedsMoreSnapshots") : t("pendingMetric");
  }
  return formatPercent(value);
}

function compoundSnapshotText(rows) {
  if (!rows.length) return t("waitingCompoundCurve");
  if (rows.length === 1) return t("oneSnapshotRecorded");
  return t("snapshotCount").replace("{count}", String(rows.length));
}

function workflowDisplay(workflowId) {
  if (!workflowId) return t("na");
  const match = String(workflowId).match(/(?:compounding|leader)_([a-f0-9]{8})/i);
  if (match) return `${t("workflowRun")} ${match[1]}`;
  return humanizeCode(workflowId);
}

function localizedNarrative(value) {
  if (!value) return value;
  const text = String(value);
  if (currentLanguage !== "zh") return text;
  if (text.includes("Paper-safe workflow snapshot only")) {
    return "仅纸面模式快照，未请求实盘执行。";
  }
  if (text.includes("Public-equity review is loaded for MSFT")) {
    return "研究包已覆盖 MSFT、NVDA 与 SPY。MSFT 的 Cloud 和 AI 增长仍强，NVDA 是 AI 基础设施核心敞口但预期风险更高，SPY 对大型科技与 AI 龙头敞口较高。本内容仅供研究，不构成实盘交易建议。";
  }
  if (text.includes("Investment Banking screening packet is loaded")) {
    return "Investment Banking 研究包已加载。MSFT 与 NVDA 当前按上市公司和战略交易对手资料处理，SPY 作为市场基准和风险背景。因专业行情与一致预期数据尚未配置，当前仍是筛选级材料。";
  }
  if (text.includes("Latest technical context is derived from local daily signal output")) {
    return "技术面来自本地日频信号输出，当前不是实时行情。";
  }
  if (text.includes("External research packets are loaded")) {
    return "外部研究包已加载，当前结果来自本地工作流快照。";
  }
  if (text.includes("FY26 Q3 revenue was $82.9B")) {
    return "MSFT FY26 Q3 收入 82.9B 美元，同比 +18%；EPS 4.27 美元，同比 +23%。Microsoft Cloud 收入 54.5B 美元，Azure 等云服务收入 +40%。";
  }
  if (text.includes("Q1 FY27 revenue was $81.6B")) {
    return "NVDA Q1 FY27 收入 81.6B 美元，同比 +85%；Data Center 收入 75.2B 美元，同比 +92%。Q2 收入指引约 91.0B 美元，但未计入中国 Data Center compute 收入。";
  }
  if (text.includes("SPY fund characteristics show 504 holdings")) {
    return "SPY 当前有 504 个持仓，FY1 P/E 为 22.83，预计 3-5 年 EPS 增长 18.60%，Information Technology 权重 38.66%。";
  }
  if (text.includes("SPY top holdings include NVIDIA")) {
    return "SPY 前十大持仓中 NVDA 权重 8.16%，MSFT 权重 4.88%。直接持有 MSFT/NVDA 会与指数仓位产生重叠敞口。";
  }
  if (text.includes("MSFT closed at $416.67")) {
    return "MSFT 2026-06-05 收于 416.67 美元，当日 -2.66%。这不是 Thesis 证据，但提示短期估值和利率敏感性。";
  }
  if (text.includes("NVDA closed at $205.10")) {
    return "NVDA 2026-06-05 收于 205.10 美元，当日 -4.40%，背景是 AI semiconductor 板块整体回撤。";
  }
  if (text.includes("SPY closed at $737.55")) {
    return "SPY 2026-06-05 收于 737.55 美元，当日 -2.58%。市场下跌与强于预期的就业数据和更高利率预期有关。";
  }
  if (text.includes("U.S. stock futures extended declines")) {
    return "Reuters 报道，美国股指期货在强于预期的非农数据后继续下跌，市场重新定价今年加息概率。";
  }
  if (text.includes("U.S.-traded chipmakers lost over $1T")) {
    return "Reuters 报道，美国上市芯片股在 2026-06-05 市值蒸发超过 1T 美元，NVDA 等 AI 龙头受到影响。";
  }
  if (text.includes("AI infrastructure platform issuer with exceptional reported growth")) {
    return "NVDA 仍是 AI 基础设施平台型公司，增长和战略重要性突出，但也更依赖 hyperscale、AI cloud、enterprise、edge、robotics 和 networking 的持续需求。";
  }
  if (text.includes("Scale software, cloud, and AI platform issuer")) {
    return "MSFT 是规模型 software、cloud 和 AI 平台公司，FY26 Q3 增长强。相关观察重点是 AI infrastructure capex、战略合作、cloud capacity 和资本回报能力。";
  }
  if (text.includes("Approximately $20.0B returned in Q1 FY27")) {
    return "NVDA Q1 FY27 通过回购和分红返还约 20.0B 美元；原有授权剩余 38.5B 美元，另新增 80.0B 美元授权。";
  }
  return text;
}

function translateStatus(value) {
  const normalized = String(value || "").toLowerCase();
  if (normalized === "loaded") return t("loaded");
  if (normalized === "missing") return t("missing");
  if (normalized === "connected") return t("connected");
  if (normalized === "available") return t("available");
  if (currentLanguage === "zh" && normalized === "positive") return "正面";
  if (currentLanguage === "zh" && normalized === "negative") return "负面";
  if (currentLanguage === "zh" && normalized === "negative_near_term") return "短期承压";
  if (currentLanguage === "zh" && normalized === "neutral") return "中性";
  if (currentLanguage === "zh" && normalized === "watch") return "观察";
  if (currentLanguage === "zh" && normalized === "risk") return "风险";
  if (currentLanguage === "zh" && normalized === "screening_grade") return "筛选级";
  return String(value || "unknown");
}

function drawCompoundCurve(rows) {
  const canvas = document.getElementById("compound-chart");
  if (!canvas) return;
  const context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#fbfaf7";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.strokeStyle = "#e3dfd7";
  context.strokeRect(0.5, 0.5, canvas.width - 1, canvas.height - 1);
  if (rows.length < 2) {
    context.fillStyle = "#78716c";
    context.font = "15px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif";
    context.fillText(rows.length ? t("curveNeedsMoreSnapshots") : t("waitingCompoundCurve"), 24, 42);
    return;
  }
  const values = rows.map((row) => Number(row.equity || row.value || 0));
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  context.beginPath();
  values.forEach((value, index) => {
    const x = 28 + index * ((canvas.width - 56) / Math.max(values.length - 1, 1));
    const y = canvas.height - 28 - ((value - min) / range) * (canvas.height - 58);
    if (index === 0) context.moveTo(x, y);
    else context.lineTo(x, y);
  });
  context.strokeStyle = "#2f6f4e";
  context.lineWidth = 2;
  context.stroke();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
