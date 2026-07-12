.PHONY: test leader daily compounding cockpit strategy-ingestion backtest

test:
	python3 -m pytest

leader:
	python3 -m system.workflows.leader_orchestrated_workflow "$(TASK)"

daily:
	python3 -m system.workflows.daily_workflow

compounding:
	python3 -m system.workflows.daily_compounding_workflow

cockpit:
	python3 -m apps.api.server --host 127.0.0.1 --port 8765

strategy-ingestion:
	python3 -m system.workflows.strategy_ingestion_workflow

backtest:
	python3 -m system.workflows.backtest_workflow
