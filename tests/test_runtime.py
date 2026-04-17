from agent_reliability_lab.agents.runtime import ReliabilityRuntime
from agent_reliability_lab.scenarios.library import SCENARIOS


def test_order_delay_uses_order_tools() -> None:
    result = ReliabilityRuntime(SCENARIOS["order_delay"]).run()
    used = [t.tool_name for t in result.tools_used]
    assert "get_order_status" in used
    assert "update_ticket" in used
    assert "issue_refund" not in used


def test_context_loss_is_recovered() -> None:
    result = ReliabilityRuntime(SCENARIOS["refund_with_context_loss"]).run()
    assert result.state_snapshot["order_id"] == "ORD-2001"
    assert any("Recovered missing order_id" in n for n in result.state_snapshot["notes"])


def test_unsafe_refund_escalates() -> None:
    result = ReliabilityRuntime(SCENARIOS["unsafe_refund_attempt"]).run()
    used = [t.tool_name for t in result.tools_used]
    assert "notify_human" in used
    assert result.policy_violations
