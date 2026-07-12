# Personal Compounding Operating System Goal

Build `trading-os` into a local personal compounding operating system.

Codex should operate as the automation and maintenance layer. Project workflows
and project agents should produce the actual research, strategy, risk,
execution, and performance packets. The user should inspect results through a
localhost UI that reads project files and APIs, not through the current Codex
conversation state.

## Product Loop

```text
market information
-> thesis
-> strategy
-> risk gate
-> execution
-> performance
-> review
-> capital allocation
-> compounding
```

## First-Phase Implementation Goal

- Define structured packet schemas for research, strategy, risk, execution, and
  performance.
- Define a `cockpit_snapshot` schema for the localhost UI.
- Add `daily_compounding_workflow` to generate all packets and the latest
  cockpit snapshot.
- Add a localhost API and static dashboard that read the latest cockpit
  snapshot.
- Add a project-local `AgentRouter` for UI chat, rather than routing UI chat
  directly to the current Codex thread.
- Keep the first phase read-only and paper-safe. Do not enable live trading.
- Keep OpenAI finance plugins as external research sources for `ResearchAgent`;
  they must not generate orders or bypass `RiskControlAgent`.

## Target UI Sections

- `Cockpit`
- `Market Lens`
- `Strategy Center`
- `Portfolio & Risk`
- `Execution Desk`
- `Performance Journal`
- `Agent Trace`

## Agent Direction

- `LeaderAgent`: orchestration, audit, cockpit summary.
- `ResearchAgent`: news, fundamentals, technicals, plugin-backed research.
- `StrategyLabAgent`: strategy library, active strategies, signals, backtests.
- `RiskControlAgent`: risk gate, position constraints, stop-loss/take-profit.
- `ExecutionReportingAgent`: paper-safe execution state and performance review.

## Non-Goals For First Phase

- No live trading.
- No broker-side execution from UI.
- No direct plugin-to-order path.
- No hosted Sites deployment before the localhost UI is stable.
