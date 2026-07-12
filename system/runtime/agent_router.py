from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class AgentRouter:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or Path.cwd()).resolve()

    def route(self, message: str) -> dict[str, Any]:
        text = message.strip()
        snapshot = self._load_snapshot()
        workflow_id = snapshot.get("workflow_id", "unknown")
        agent = self._select_agent(text)
        response = self._response_for(agent, text, snapshot)
        return {
            "agent": agent,
            "message": response,
            "workflow_id": workflow_id,
            "source": "system.runtime.agent_router",
            "confidence": 0.6 if snapshot else 0.2,
            "limitations": self._limitations(snapshot),
        }

    def _select_agent(self, message: str) -> str:
        lowered = message.lower()
        if any(term in lowered for term in ("risk", "stop", "止损", "止盈", "仓位", "风险")):
            return "RiskControlAgent"
        if any(term in lowered for term in ("strategy", "signal", "backtest", "策略", "信号", "回测")):
            return "StrategyLabAgent"
        if any(term in lowered for term in ("pnl", "cagr", "drawdown", "performance", "收益", "复利", "回撤")):
            return "ExecutionReportingAgent"
        if any(term in lowered for term in ("news", "fundamental", "technical", "market", "消息", "基本面", "技术面", "市场")):
            return "ResearchAgent"
        return "LeaderAgent"

    def _response_for(self, agent: str, message: str, snapshot: dict[str, Any]) -> str:
        if not snapshot:
            return "当前还没有 cockpit snapshot。请先运行 daily_compounding_workflow。"
        if agent == "ResearchAgent":
            lens = snapshot.get("market_lens", {})
            return (
                f"消息面：{_summary(lens.get('news'))} "
                f"基本面：{_summary(lens.get('fundamentals'))} "
                f"技术面：{_summary(lens.get('technicals'))}"
            )
        if agent == "StrategyLabAgent":
            strategy = snapshot.get("strategy_center", {})
            return (
                f"当前 active strategy 数量为 {len(strategy.get('active_strategies', []))}，"
                f"今日信号数量为 {len(strategy.get('signals', []))}。"
            )
        if agent == "RiskControlAgent":
            risk = snapshot.get("portfolio_risk", {})
            return f"当前风险决策为 {risk.get('risk_decision')}。原因：{risk.get('reason')}"
        if agent == "ExecutionReportingAgent":
            perf = snapshot.get("performance_journal", {})
            execution = snapshot.get("execution_desk", {})
            return (
                f"执行模式为 {execution.get('mode')}，待确认动作 {len(execution.get('pending_actions', []))} 个。"
                f"CAGR={perf.get('cagr')}，max drawdown={perf.get('max_drawdown')}。"
            )
        return (
            f"我会基于当前 cockpit snapshot 回答。系统状态为 {snapshot.get('status')}，"
            f"workflow_id={snapshot.get('workflow_id')}。"
        )

    def _load_snapshot(self) -> dict[str, Any]:
        path = self.root / "outputs" / "compounding" / "latest.json"
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _limitations(snapshot: dict[str, Any]) -> list[str]:
        if not snapshot:
            return ["No cockpit snapshot is available."]
        limitations = []
        if snapshot.get("status") == "partial":
            limitations.append("Snapshot is partial because some external research, portfolio, or performance data is not connected.")
        return limitations


def _summary(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("summary", value))
    return str(value)
