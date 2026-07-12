from system.agents import (
    BrokerExecutionAgent,
    DataAgent,
    LeaderAgent,
    PortfolioCapitalAgent,
    QuantConnectAgent,
    QuantEngineeringAgent,
    ReportingAgent,
    ResearchAgent,
    RiskControlAgent,
    StrategyAgent,
)


def test_all_core_agents_exist_and_run():
    agents = [
        LeaderAgent(),
        DataAgent(),
        ResearchAgent(),
        StrategyAgent(),
        QuantEngineeringAgent(),
        QuantConnectAgent(),
        PortfolioCapitalAgent(),
        RiskControlAgent(),
        BrokerExecutionAgent(),
        ReportingAgent(),
    ]
    assert len(agents) == 10
    for agent in agents:
        output = agent.run({"workflow_id": "wf"})
        assert output["metadata"]["workflow_id"] == "wf"
        assert output["agent"] == agent.name
    assert LeaderAgent().can_write_persistent
    assert not DataAgent().can_write_persistent


def test_leader_agent_delegates_to_full_team():
    output = LeaderAgent().run({"workflow_id": "wf", "task": "daily review"})
    delegated_agents = {item["agent"] for item in output["subagent_outputs"]}

    assert output["delegation_mode"] == "full_team"
    assert delegated_agents == {
        "DataAgent",
        "ResearchAgent",
        "StrategyAgent",
        "QuantEngineeringAgent",
        "QuantConnectAgent",
        "PortfolioCapitalAgent",
        "RiskControlAgent",
        "BrokerExecutionAgent",
        "ReportingAgent",
    }
