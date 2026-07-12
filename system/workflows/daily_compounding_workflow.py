from __future__ import annotations

import json
import csv
from pathlib import Path
from typing import Any

from system.schemas import (
    CockpitSnapshotSchema,
    ExecutionPacketSchema,
    PerformancePacketSchema,
    ResearchPacketSchema,
    RiskPacketSchema,
    StrategyPacketSchema,
)
from system.workflows._helpers import (
    leader_packet,
    metadata,
    new_workflow_id,
    root_path,
    write_json,
    write_leader_packet,
)


def run(root: str | Path | None = None, workflow_id: str | None = None) -> dict[str, Any]:
    root_dir = root_path(root)
    workflow_id = workflow_id or new_workflow_id("compounding")
    run_dir = root_dir / "workspace" / "active_runs" / workflow_id
    run_dir.mkdir(parents=True, exist_ok=True)

    leader = leader_packet(workflow_id, "daily compounding workflow", "daily_compounding_workflow")
    leader_packet_path = write_leader_packet(root_dir, run_dir, leader)

    active_strategies = _read_json(root_dir, "persistent/project_state/active_strategies.json", {"active_strategies": []})
    broker_mode = _read_json(root_dir, "persistent/project_state/current_broker_mode.json", {"mode": "paper", "live_enabled": False})
    risk_mode = _read_json(root_dir, "persistent/project_state/current_risk_mode.json", {"risk_mode": "normal"})
    portfolio = _read_json(root_dir, "persistent/portfolios/current_portfolio.json", {"positions": []})
    capital_snapshot = _read_json(root_dir, "persistent/capital/capital_snapshot_latest.json", {"accounts": []})
    asset_allocations = _read_json(root_dir, "persistent/portfolios/asset_allocations/latest.json", {"allocations": []})
    exposure = _read_json(root_dir, "persistent/portfolios/exposure/exposure_latest.json", {"exposure": {}})
    pnl_summary = _read_json(root_dir, "persistent/ledgers/pnl/pnl_summary.json", {"status": "missing"})
    daily_signals = _read_json(root_dir, "outputs/daily_signals/latest.json", {"signals": [], "broker_mode": "paper"})
    strategy_registry = _read_strategy_registry(root_dir)
    experiment_index = _read_json(root_dir, "persistent/experiments/experiment_index.json", {"experiments": []})
    ledgers = {
        "trades": _read_csv(root_dir, "persistent/ledgers/trades/trade_ledger_2026.csv"),
        "dividends": _read_csv(root_dir, "persistent/ledgers/dividends/dividends_2026.csv"),
        "fx": _read_csv(root_dir, "persistent/ledgers/fx/fx_events_2026.csv"),
        "unrealized_pnl": _read_csv(root_dir, "persistent/ledgers/pnl/unrealized_pnl_snapshots.csv"),
    }
    external_research = _read_external_research(root_dir)
    portfolio_context = _build_portfolio_context(portfolio, capital_snapshot, asset_allocations, exposure)

    research_packet = _build_research_packet(workflow_id, daily_signals, external_research)
    strategy_packet = _build_strategy_packet(workflow_id, active_strategies, daily_signals, strategy_registry, experiment_index)
    risk_packet = _build_risk_packet(workflow_id, risk_mode, broker_mode, portfolio_context, strategy_packet)
    execution_packet = _build_execution_packet(workflow_id, broker_mode, strategy_packet, risk_packet)
    performance_packet = _build_performance_packet(workflow_id, pnl_summary, ledgers, portfolio_context)
    cockpit_snapshot = _build_cockpit_snapshot(
        workflow_id,
        research_packet,
        strategy_packet,
        risk_packet,
        execution_packet,
        performance_packet,
        portfolio_context,
    )

    packets = {
        "research_packet": research_packet.to_dict(),
        "strategy_packet": strategy_packet.to_dict(),
        "risk_packet": risk_packet.to_dict(),
        "execution_packet": execution_packet.to_dict(),
        "performance_packet": performance_packet.to_dict(),
        "cockpit_snapshot": cockpit_snapshot.to_dict(),
    }
    packet_paths = {
        name: str(write_json(run_dir / f"{name}.json", payload))
        for name, payload in packets.items()
    }
    for name, payload in packets.items():
        write_json(root_dir / "workspace" / "handoff" / f"{name}.json", payload)

    latest_snapshot_path = write_json(root_dir / "outputs" / "compounding" / "latest.json", cockpit_snapshot.to_dict())

    return {
        "workflow_id": workflow_id,
        "run_dir": str(run_dir),
        "leader_packet": str(leader_packet_path),
        "cockpit_snapshot": str(run_dir / "cockpit_snapshot.json"),
        "latest_snapshot": str(latest_snapshot_path),
        "packet_paths": packet_paths,
        "risk_decision": risk_packet.decision,
        "status": cockpit_snapshot.status,
    }


def _read_json(root_dir: Path, relative_path: str, default: dict[str, Any]) -> dict[str, Any]:
    path = root_dir / relative_path
    if not path.exists():
        return {**default, "_source_path": relative_path, "_source_status": "missing"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {**default, "_source_path": relative_path, "_source_status": "invalid_json"}
    if isinstance(payload, dict):
        return {**payload, "_source_path": relative_path, "_source_status": "loaded"}
    return {**default, "_source_path": relative_path, "_source_status": "not_object"}


def _read_csv(root_dir: Path, relative_path: str) -> dict[str, Any]:
    path = root_dir / relative_path
    if not path.exists():
        return {"rows": [], "_source_path": relative_path, "_source_status": "missing"}
    with path.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return {
        "rows": rows,
        "row_count": len(rows),
        "_source_path": relative_path,
        "_source_status": "loaded",
    }


def _read_strategy_registry(root_dir: Path) -> dict[str, Any]:
    path = root_dir / "persistent" / "strategies" / "registry.yaml"
    if not path.exists():
        return {"strategies": [], "_source_path": "persistent/strategies/registry.yaml", "_source_status": "missing"}
    strategies: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            strategies.append(stripped[2:].strip())
    return {
        "strategies": strategies,
        "_source_path": "persistent/strategies/registry.yaml",
        "_source_status": "loaded",
    }


def _read_external_research(root_dir: Path) -> dict[str, Any]:
    sources = {
        "public_equity_investing": _read_json(
            root_dir,
            "workspace/handoff/public_equity_research_packet.json",
            {"items": [], "summary": "Public Equity Investing plugin output is not connected yet."},
        ),
        "investment_banking": _read_json(
            root_dir,
            "workspace/handoff/investment_banking_research_packet.json",
            {"items": [], "summary": "Investment Banking plugin output is not connected yet."},
        ),
    }
    connector_status = _connector_status_with_research_packets(
        _read_json(
            root_dir,
            "workspace/handoff/plugin_connector_status.json",
            {
                "plugins": {},
                "summary": "No plugin connector status file is available yet.",
            },
        ),
        sources,
    )
    return {
        "sources": sources,
        "connected": {
            name: _plugin_connector_available(connector_status, name) or payload.get("_source_status") == "loaded"
            for name, payload in sources.items()
        },
        "research_packets_loaded": {
            name: payload.get("_source_status") == "loaded"
            for name, payload in sources.items()
        },
        "connector_status": connector_status,
    }


def _connector_status_with_research_packets(
    connector_status: dict[str, Any],
    sources: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    plugins = dict(connector_status.get("plugins", {}))
    for name, payload in sources.items():
        plugin = dict(plugins.get(name, {}))
        plugin.setdefault("plugin", _plugin_display_name(name))
        plugin["research_packet_path"] = payload.get("_source_path")
        plugin["research_packet_status"] = payload.get("_source_status", "unknown")
        plugins[name] = plugin
    return {**connector_status, "plugins": plugins}


def _plugin_connector_available(connector_status: dict[str, Any], plugin_name: str) -> bool:
    plugin = connector_status.get("plugins", {}).get(plugin_name, {})
    available_states = {"available", "authorized", "connected", "loaded"}
    if str(plugin.get("status", "")).lower() in available_states:
        return True
    connectors = plugin.get("connectors", [])
    if not isinstance(connectors, list):
        return False
    return any(
        str(connector.get("status", "")).lower() in available_states
        for connector in connectors
        if isinstance(connector, dict)
    )


def _plugin_display_name(plugin_name: str) -> str:
    names = {
        "public_equity_investing": "Public Equity Investing",
        "investment_banking": "Investment Banking",
    }
    return names.get(plugin_name, plugin_name)


def _build_portfolio_context(
    portfolio: dict[str, Any],
    capital_snapshot: dict[str, Any],
    asset_allocations: dict[str, Any],
    exposure: dict[str, Any],
) -> dict[str, Any]:
    portfolio_positions = list(portfolio.get("positions", []))
    capital_positions = _positions_from_capital_snapshot(capital_snapshot)
    positions = portfolio_positions or capital_positions
    total_equity = _first_present(
        portfolio,
        "total_equity",
        "total_net_liquidation",
        "total_net_worth",
    )
    if total_equity is None:
        total_equity = _first_present(capital_snapshot, "total_net_worth_nok", "known_nok_assets_total")
    return {
        "positions": positions,
        "accounts": list(capital_snapshot.get("accounts", [])),
        "allocations": list(asset_allocations.get("allocations", [])),
        "exposure": exposure.get("exposure", {}),
        "total_equity": total_equity,
        "base_currency": capital_snapshot.get("base_currency"),
        "valuation_status": capital_snapshot.get("valuation_status"),
        "original_currency_totals": capital_snapshot.get("original_currency_totals", {}),
        "source_status": {
            "portfolio": portfolio.get("_source_status"),
            "capital_snapshot": capital_snapshot.get("_source_status"),
            "asset_allocations": asset_allocations.get("_source_status"),
            "exposure": exposure.get("_source_status"),
        },
    }


def _positions_from_capital_snapshot(capital_snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    positions: list[dict[str, Any]] = []
    for account in capital_snapshot.get("accounts", []):
        for position in account.get("positions", []):
            positions.append({
                **position,
                "account_id": account.get("account_id"),
                "provider": account.get("provider"),
                "source": account.get("source"),
            })
    return positions


def _envelope(workflow_id: str, source: str, created_by: str) -> dict[str, Any]:
    item_metadata = metadata(workflow_id, source, created_by)
    return {
        "workflow_id": item_metadata["workflow_id"],
        "source": item_metadata["source"],
        "created_at": item_metadata["created_at"],
        "created_by": item_metadata["created_by"],
        "metadata": item_metadata,
    }


def _build_research_packet(
    workflow_id: str,
    daily_signals: dict[str, Any],
    external_research: dict[str, Any],
) -> ResearchPacketSchema:
    signals = daily_signals.get("signals", [])
    public_equity = external_research["sources"]["public_equity_investing"]
    investment_banking = external_research["sources"]["investment_banking"]
    plugin_items = _research_items(public_equity) + _research_items(investment_banking)
    packet = {
        "market_lens": {
            "news": {
                "summary": _research_summary(public_equity, "No connected news plugin output is available yet."),
                "items": plugin_items,
            },
            "fundamentals": {
                "summary": _research_summary(investment_banking, "No connected fundamentals plugin output is available yet."),
                "items": plugin_items,
            },
            "technicals": {
                "summary": "Latest technical context is derived from local daily signal output.",
                "signals": signals,
            },
            "external_sources": external_research,
        },
        "thesis_impacts": list(public_equity.get("thesis_impacts", [])) + list(investment_banking.get("thesis_impacts", [])),
        "catalysts": list(public_equity.get("catalysts", [])) + list(investment_banking.get("catalysts", [])),
        "risks": list(public_equity.get("risks", [])) + list(investment_banking.get("risks", [])),
        "confidence": 0.55 if plugin_items else (0.35 if signals else 0.2),
        **_envelope(workflow_id, "daily_compounding_workflow.research_packet", "ResearchAgent"),
    }
    return ResearchPacketSchema.from_dict(packet)


def _build_strategy_packet(
    workflow_id: str,
    active_strategies: dict[str, Any],
    daily_signals: dict[str, Any],
    strategy_registry: dict[str, Any],
    experiment_index: dict[str, Any],
) -> StrategyPacketSchema:
    strategies = list(active_strategies.get("active_strategies", []))
    library = list(strategy_registry.get("strategies", []))
    experiments = list(experiment_index.get("experiments", []))
    packet = {
        "active_strategies": strategies,
        "signals": list(daily_signals.get("signals", [])),
        "strategy_library_summary": {
            "total_count": len(library),
            "active_count": len(strategies),
            "inactive_count": max(len(library) - len(strategies), 0),
            "strategies": library,
            "experiments_count": len(experiments),
            "experiments": experiments,
            "source_status": active_strategies.get("_source_status", "unknown"),
            "registry_source_status": strategy_registry.get("_source_status", "unknown"),
            "experiment_source_status": experiment_index.get("_source_status", "unknown"),
        },
        "backtest_refs": [str(item.get("experiment_id")) for item in experiments if item.get("experiment_id")],
        **_envelope(workflow_id, "daily_compounding_workflow.strategy_packet", "StrategyLabAgent"),
    }
    return StrategyPacketSchema.from_dict(packet)


def _build_risk_packet(
    workflow_id: str,
    risk_mode: dict[str, Any],
    broker_mode: dict[str, Any],
    portfolio_context: dict[str, Any],
    strategy_packet: StrategyPacketSchema,
) -> RiskPacketSchema:
    mode = str(risk_mode.get("risk_mode", "normal"))
    broker = str(broker_mode.get("mode", "paper"))
    live_enabled = bool(broker_mode.get("live_enabled", False))
    positions = list(portfolio_context.get("positions", []))
    stop_loss_take_profit = _extract_exit_levels(positions)
    alerts = _risk_alerts(positions, stop_loss_take_profit)

    if broker == "live" or live_enabled:
        decision = "REJECT"
        reason = "First-phase daily compounding workflow does not permit live execution."
        risk_gate_passed = False
    else:
        decision = "PASS"
        reason = "Paper-safe workflow snapshot only; no live execution requested."
        risk_gate_passed = True

    packet = {
        "risk_mode": mode,
        "decision": decision,
        "reason": reason,
        "risk_gate_passed": risk_gate_passed,
        "rejection_can_be_overridden": False,
        "checks": {
            "broker_mode": broker,
            "live_enabled": live_enabled,
            "positions_count": len(positions),
            "accounts_count": len(portfolio_context.get("accounts", [])),
            "active_strategy_count": len(strategy_packet.active_strategies),
            "structured_orders_only": True,
            "portfolio_source_status": portfolio_context.get("source_status", {}),
        },
        "alerts": alerts,
        "stop_loss_take_profit": stop_loss_take_profit,
        **_envelope(workflow_id, "daily_compounding_workflow.risk_packet", "RiskControlAgent"),
    }
    return RiskPacketSchema.from_dict(packet)


def _build_execution_packet(
    workflow_id: str,
    broker_mode: dict[str, Any],
    strategy_packet: StrategyPacketSchema,
    risk_packet: RiskPacketSchema,
) -> ExecutionPacketSchema:
    broker = str(broker_mode.get("mode", "paper"))
    signal_actions = [
        {
            "strategy_id": signal.get("strategy_id", "unknown"),
            "symbol": signal.get("symbol"),
            "action": signal.get("signal"),
            "timeframe": signal.get("timeframe"),
        }
        for signal in strategy_packet.signals
        if signal.get("signal") not in {None, "HOLD"}
    ]
    if not risk_packet.risk_gate_passed:
        pending_actions: list[dict[str, Any]] = []
        rejected_actions = [{**action, "reason": risk_packet.reason} for action in signal_actions]
        mode = "disabled"
    else:
        pending_actions = signal_actions
        rejected_actions = []
        mode = broker if broker in {"paper", "live"} else "disabled"

    packet = {
        "mode": mode,
        "pending_actions": pending_actions,
        "rejected_actions": rejected_actions,
        "confirmed_actions": [],
        "order_status": [],
        "human_confirmation_required": bool(pending_actions),
        **_envelope(workflow_id, "daily_compounding_workflow.execution_packet", "ExecutionReportingAgent"),
    }
    return ExecutionPacketSchema.from_dict(packet)


def _build_performance_packet(
    workflow_id: str,
    pnl_summary: dict[str, Any],
    ledgers: dict[str, dict[str, Any]],
    portfolio_context: dict[str, Any],
) -> PerformancePacketSchema:
    compound_curve = list(pnl_summary.get("compound_curve", [])) or _compound_curve_from_ledgers(ledgers, portfolio_context)
    ledger_counts = {
        name: payload.get("row_count", len(payload.get("rows", [])))
        for name, payload in ledgers.items()
    }
    packet = {
        "pnl": {
            **pnl_summary,
            "ledger_counts": ledger_counts,
            "recent_trades": ledgers["trades"].get("rows", [])[-10:],
            "recent_dividends": ledgers["dividends"].get("rows", [])[-10:],
            "recent_fx_events": ledgers["fx"].get("rows", [])[-10:],
        },
        "cagr": _optional_float(pnl_summary.get("cagr")),
        "max_drawdown": _optional_float(pnl_summary.get("max_drawdown")),
        "compound_curve": compound_curve,
        "strategy_contribution": list(pnl_summary.get("strategy_contribution", [])),
        "review_notes": ["Performance data is sourced from local PnL summary when available."],
        **_envelope(workflow_id, "daily_compounding_workflow.performance_packet", "ExecutionReportingAgent"),
    }
    return PerformancePacketSchema.from_dict(packet)


def _build_cockpit_snapshot(
    workflow_id: str,
    research_packet: ResearchPacketSchema,
    strategy_packet: StrategyPacketSchema,
    risk_packet: RiskPacketSchema,
    execution_packet: ExecutionPacketSchema,
    performance_packet: PerformancePacketSchema,
    portfolio_context: dict[str, Any],
) -> CockpitSnapshotSchema:
    status = "blocked" if risk_packet.decision in {"REJECT", "HALT"} else "partial"
    packet = {
        "snapshot_id": f"cockpit_{workflow_id}",
        "status": status,
        "top_metrics": {
            "total_equity": portfolio_context.get("total_equity"),
            "today_pnl": performance_packet.pnl.get("today_pnl"),
            "cagr": performance_packet.cagr,
            "max_drawdown": performance_packet.max_drawdown,
            "risk_mode": risk_packet.risk_mode,
            "base_currency": portfolio_context.get("base_currency"),
        },
        "market_lens": research_packet.market_lens,
        "strategy_center": {
            "active_strategies": strategy_packet.active_strategies,
            "signals": strategy_packet.signals,
            "strategy_library_summary": strategy_packet.strategy_library_summary,
            "backtest_refs": strategy_packet.backtest_refs,
        },
        "portfolio_risk": {
            "positions": list(portfolio_context.get("positions", [])),
            "accounts": list(portfolio_context.get("accounts", [])),
            "allocations": list(portfolio_context.get("allocations", [])),
            "exposure": portfolio_context.get("exposure", {}),
            "valuation_status": portfolio_context.get("valuation_status"),
            "original_currency_totals": portfolio_context.get("original_currency_totals", {}),
            "risk_decision": risk_packet.decision,
            "reason": risk_packet.reason,
            "alerts": risk_packet.alerts,
            "stop_loss_take_profit": risk_packet.stop_loss_take_profit,
            "checks": risk_packet.checks,
        },
        "execution_desk": {
            "mode": execution_packet.mode,
            "pending_actions": execution_packet.pending_actions,
            "rejected_actions": execution_packet.rejected_actions,
            "confirmed_actions": execution_packet.confirmed_actions,
            "human_confirmation_required": execution_packet.human_confirmation_required,
        },
        "performance_journal": {
            "pnl": performance_packet.pnl,
            "cagr": performance_packet.cagr,
            "max_drawdown": performance_packet.max_drawdown,
            "compound_curve": performance_packet.compound_curve,
            "strategy_contribution": performance_packet.strategy_contribution,
            "review_notes": performance_packet.review_notes,
        },
        "agent_trace": {
            "workflow_id": workflow_id,
            "packets": [
                {"name": "research_packet", "agent": "ResearchAgent"},
                {"name": "strategy_packet", "agent": "StrategyLabAgent"},
                {"name": "risk_packet", "agent": "RiskControlAgent"},
                {"name": "execution_packet", "agent": "ExecutionReportingAgent"},
                {"name": "performance_packet", "agent": "ExecutionReportingAgent"},
            ],
        },
        **_envelope(workflow_id, "daily_compounding_workflow.cockpit_snapshot", "LeaderAgent"),
    }
    return CockpitSnapshotSchema.from_dict(packet)


def _extract_exit_levels(positions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    levels = []
    for position in positions:
        symbol = position.get("symbol")
        if not symbol:
            continue
        levels.append({
            "symbol": symbol,
            "stop_loss": position.get("stop_loss"),
            "take_profit": position.get("take_profit"),
        })
    return levels


def _risk_alerts(positions: list[dict[str, Any]], exit_levels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    missing_exit_rules = [
        item["symbol"]
        for item in exit_levels
        if item.get("stop_loss") is None and item.get("take_profit") is None
    ]
    if positions and missing_exit_rules:
        return [{
            "level": "warning",
            "message": "Open positions are missing explicit stop-loss and take-profit levels.",
            "symbols": missing_exit_rules,
        }]
    return []


def _research_summary(payload: dict[str, Any], fallback: str) -> str:
    value = payload.get("summary") or payload.get("headline") or fallback
    return str(value)


def _research_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("items", "facts", "events", "notes"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item if isinstance(item, dict) else {"text": str(item)} for item in value]
    return []


def _compound_curve_from_ledgers(
    ledgers: dict[str, dict[str, Any]],
    portfolio_context: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = ledgers["unrealized_pnl"].get("rows", [])
    curve = [
        {
            "date": row.get("created_at"),
            "equity": _optional_float(row.get("amount")),
            "currency": row.get("currency"),
            "source": row.get("source"),
        }
        for row in rows
        if row.get("created_at") and _optional_float(row.get("amount")) is not None
    ]
    if curve:
        return curve
    total_equity = portfolio_context.get("total_equity")
    if total_equity is None:
        return []
    return [{
        "date": None,
        "equity": total_equity,
        "currency": portfolio_context.get("base_currency"),
        "source": "portfolio_context.total_equity",
    }]


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_present(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if value is not None and value != "":
            return value
    return None


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
