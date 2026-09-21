# Multi-agent Quantitative Trading System

`trading-os` is a Codex-operated multi-agent quantitative trading research and execution system. It is not a live trading bot. The current implementation is a safe local scaffold with stubs for external platforms and broker operations.

## Agents

The system keeps 10 core agents:

- `LeaderAgent`: orchestrates workflows, reviews candidates, and promotes approved assets.
- `DataAgent`: prepares market, news, macro, broker, and QuantConnect reference data packets through stubs.
- `ResearchAgent`: creates structured facts, interpretations, signals, risk flags, and confidence values.
- `StrategyAgent`: ingests external strategy ideas, manages lifecycle, and creates strategy packages.
- `QuantEngineeringAgent`: produces strategy code, QuantConnect-oriented code, schemas, and quick backtest stubs.
- `QuantConnectAgent`: prepares QuantConnect project artifacts and backtest or paper trading stubs.
- `PortfolioCapitalAgent`: summarizes capital, liquidity, FX exposure, and position sizing guidance.
- `RiskControlAgent`: enforces risk limits, approval gates, broker mode safety, and non-overridable rejection.
- `BrokerExecutionAgent`: reads broker status through stubs and accepts only structured approved order payloads.
- `ReportingAgent`: creates daily, weekly, strategy, risk, capital, execution, and review report drafts.

## Folder structure

- `system/`: agents, skills, workflows, schemas, prompts, and runtime utilities.
- `config/`: policy, risk, broker, agent, skill, path, universe, and reporting configuration.
- `workspace/`: temporary workflow runs, shared context, handoff packets, scratch work, and promotion candidates.
- `persistent/`: long-term promoted assets organized by asset type.
- `data/`: raw, normalized, feature, quality, and vendor cache locations.
- `quantconnect/`: QuantConnect-oriented algorithm and model stubs.
- `integrations/`: Massive, SEC EDGAR, FRED, IBKR, and QuantConnect adapter stubs.
- `outputs/`: generated daily signals, approved order placeholders, backtest, paper, live, and export outputs.
- `logs/`: agent, workflow, promotion, risk, broker, and system log locations.
- `tests/`: schema, promotion, risk, order, workflow, security, integration, and agent tests.
- `docs/`: architecture, policies, lifecycle, integration, and operating manual.

## Start a Codex or Claude Code session

```bash
make leader TASK="describe the current request"
```

This creates a `LeaderAgent` packet, a full-team delegation plan, and an agent trace under `workspace/active_runs`.

## Run daily workflow

```bash
make daily
```

This creates a local workflow run under `workspace/active_runs`, updates `outputs/daily_signals/latest.json`, and creates a report candidate under `workspace/promotion_queue/candidate_reports`.

## Run compounding workflow

```bash
make compounding
```

This creates a local personal compounding workflow run under `workspace/active_runs`, writes agent packets to `workspace/handoff`, and updates `outputs/compounding/latest.json` for the localhost cockpit.

## Start localhost cockpit

```bash
make cockpit
```

Open `http://127.0.0.1:8765` to view the local dashboard. The server exposes read-only product endpoints such as `/api/cockpit`, `/api/market-lens`, `/api/strategies`, `/api/portfolio-risk`, `/api/execution`, `/api/performance`, and `/api/agent-trace`. The `/api/chat` endpoint routes user questions to the project-local `AgentRouter`; it does not talk directly to Codex.

## Import a strategy

```bash
make strategy-ingestion
```

The stub workflow creates a candidate strategy package in `workspace/promotion_queue/candidate_strategies` with metadata, risk file, source text, local signal generator, and QuantConnect-oriented file.

## Run tests

```bash
make test
```

## Promotion model

Subagents write candidate assets to `workspace/promotion_queue`. `LeaderAgent` reviews candidates and is the only agent that can promote to `persistent`. Risk-sensitive assets require `RiskControlAgent` review before promotion.

## Risk and live limits

Default broker mode is `paper`. Live trading is disabled. Live orders require `risk_approved=true`, `human_approved=true`, and explicit live enablement. Natural language orders are rejected.

## Stub integrations

Massive, SEC EDGAR, FRED, QuantConnect, and IBKR are implemented as local adapter stubs. They do not call external APIs and do not confirm real external connectivity.

## Next integrations

Next steps are to add real credentials through environment variables, implement Massive price and news clients, connect QuantConnect project sync and backtest APIs, and add an IBKR read-only adapter before any execution pathway is considered.
