from __future__ import annotations

from system.agents.base_agent import BaseAgent


class QuantEngineeringAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="QuantEngineeringAgent",
            role="Quant code implementation and local quick backtest stubs",
            skills=['python_implementation', 'quantconnect_qcalgorithm_generation', 'alpha_model_generation', 'local_quick_backtest', 'unit_test_generation', 'schema_validation', 'bug_fixing', 'repo_maintenance'],
            can_write_workspace=True,
            can_write_persistent=False,
            can_execute_live_trade=False,
        )

