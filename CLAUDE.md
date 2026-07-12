# CLAUDE.md

Follow `AGENTS.md` as the source of truth for this repository.

Every Claude Code session must route the user request through `LeaderAgent` first:

```bash
make leader TASK="short description of the user request"
```

The default mode is `full_team`. `LeaderAgent` must call `DataAgent`, `ResearchAgent`, `StrategyAgent`, `QuantEngineeringAgent`, `QuantConnectAgent`, `PortfolioCapitalAgent`, `RiskControlAgent`, `BrokerExecutionAgent`, and `ReportingAgent`, then continue with the requested work.

Do not execute live trades, write real credentials, bypass `RiskControlAgent`, or promote files to `persistent` without `LeaderAgent` review.
