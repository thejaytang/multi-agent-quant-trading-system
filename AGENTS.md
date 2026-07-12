# AGENTS.md

## System mission

Build and operate `trading-os`, a Codex-operated multi-agent quantitative trading research and execution system. The system supports research, strategy ingestion, local stubs for backtesting, QuantConnect-oriented artifacts, paper trading preparation, risk review, reporting, and long-term asset storage.

## Agent hierarchy

`LeaderAgent` is the top-level orchestrator. It may call and coordinate `DataAgent`, `ResearchAgent`, `StrategyAgent`, `QuantEngineeringAgent`, `QuantConnectAgent`, `PortfolioCapitalAgent`, `RiskControlAgent`, `BrokerExecutionAgent`, and `ReportingAgent`.

## Session bootstrap

Every Codex or Claude Code session in this repository must start by routing the user request through `LeaderAgent`.

Default command:

```bash
make leader TASK="short description of the user request"
```

This command writes `leader_packet.json`, `delegation_plan.json`, and `agent_trace.json` under `workspace/active_runs/<workflow_id>`, and updates `workspace/handoff/leader_packet.json`.

The default delegation mode is `full_team`: `LeaderAgent` calls `DataAgent`, `ResearchAgent`, `StrategyAgent`, `QuantEngineeringAgent`, `QuantConnectAgent`, `PortfolioCapitalAgent`, `RiskControlAgent`, `BrokerExecutionAgent`, and `ReportingAgent`. For trivial read-only questions, the assistant may avoid running the command only if it still explicitly reasons as `LeaderAgent` and no file, workflow, trading, capital, risk, or promotion decision is involved.

## LeaderAgent authority

`LeaderAgent` can create subagents, assign skills, call all agents, review candidate artifacts, and promote approved artifacts from `workspace` to `persistent`. It cannot override `RiskControlAgent`, execute live trades, modify a real broker account, disable audit logs, or write real credentials.

## Subagent rules

Subagents can write to `workspace` and produce promotion candidates. Subagents cannot write to `persistent` directly. Any candidate asset must enter `workspace/promotion_queue` before promotion.

## Skill assignment rules

Skills are grouped by agent function. Data skills handle market and macro inputs, research skills produce structured evidence, strategy skills manage lifecycle and registries, quant skills create code and quick backtest stubs, portfolio skills manage capital views, risk skills gate trading and promotion, broker skills expose paper-safe execution stubs, and reporting skills create report drafts.

## File management rules

`workspace` is temporary. `persistent` is the long-term project asset library. `persistent` is organized by asset type, not by agent. Important outputs must include `metadata`, `workflow_id`, `source`, `created_at`, and `created_by`.

## workspace vs persistent

Use `workspace/active_runs` for workflow run artifacts, `workspace/shared_context` for current state, `workspace/handoff` for agent packets, and `workspace/promotion_queue` for candidates. Use `persistent` only for promoted project assets such as strategies, experiments, portfolios, reports, decisions, ledgers, and knowledge.

## Promotion policy

Only `LeaderAgent` can promote files to `persistent`. Promotion must validate the candidate schema, source path, target path, metadata, policy requirements, and audit logging. Trading, capital, portfolio, ledger, and live-related assets require `RiskControlAgent` review when policy marks risk review as required.

## RiskControlAgent authority

`RiskControlAgent` has highest priority for risk decisions. Its rejection cannot be overridden by `LeaderAgent`. It enforces position limits, capital limits, drawdown controls, paper-to-live gates, broker mode safety, human approval requirements, and key-leak checks.

## Broker execution rules

`BrokerExecutionAgent` defaults to paper mode. It rejects natural language orders and accepts only structured `OrderSchema`. Live orders require `risk_approved=true`, `human_approved=true`, and live broker mode explicitly enabled outside this stub system.

## Testing requirements

Tests must cover schemas, promotion boundaries, risk rejection, broker mode defaults, live approval gates, natural language order rejection, workflow outputs, and security checks for committed secrets.

## Do-not-do list

- Do not execute live trades.
- Do not write real API keys.
- Do not allow subagents to write persistent directly.
- Do not bypass RiskControlAgent.
- Do not accept natural language orders.
- Do not promote files without LeaderAgent review.
- Do not use old provider name for Massive.
- Do not assume external integrations are live unless configured.
