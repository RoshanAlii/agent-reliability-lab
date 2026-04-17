from __future__ import annotations

from dataclasses import asdict
from typing import List

from agent_reliability_lab.core.models import AgentState, HandoffRecord, RunResult, Scenario
from agent_reliability_lab.core.tooling import ToolRegistry, ToolSpec
from agent_reliability_lab.tools.mock_tools import MockSupportBackend
from agent_reliability_lab.tracing.trace import TraceCollector


class ReliabilityRuntime:
    def __init__(self, scenario: Scenario, trace_dir: str = "artifacts/traces") -> None:
        self.scenario = scenario
        self.trace = TraceCollector(trace_dir)
        self.state = AgentState()
        self.backend = MockSupportBackend(scenario.injected_faults)
        self.registry = ToolRegistry()
        self._register_tools()
        self.tools_used = []
        self.handoffs: List[HandoffRecord] = []
        self.policy_violations: list[str] = []

    def _register_tools(self) -> None:
        self.registry.register(ToolSpec("get_order_status", "Retrieve order status", self.backend.get_order_status))
        self.registry.register(ToolSpec("issue_refund", "Issue a refund", self.backend.issue_refund))
        self.registry.register(ToolSpec("search_kb", "Search knowledge base", self.backend.search_kb))
        self.registry.register(ToolSpec("update_ticket", "Update support ticket", self.backend.update_ticket))
        self.registry.register(ToolSpec("notify_human", "Escalate to human", self.backend.notify_human))

    def _handoff(self, from_agent: str, to_agent: str, reason: str) -> None:
        self.handoffs.append(HandoffRecord(from_agent=from_agent, to_agent=to_agent, reason=reason))
        self.trace.add("handoff", {"from": from_agent, "to": to_agent, "reason": reason})

    def _call_tool(self, name: str, **kwargs: object) -> dict:
        record = self.registry.call(name, **kwargs)
        self.tools_used.append(record)
        self.trace.add(
            "tool_call",
            {"tool": name, "args": kwargs, "success": record.success, "error": record.error},
        )
        if not record.success:
            return {"error": record.error}
        return record.result

    def run(self) -> RunResult:
        self.trace.add("scenario_start", {"scenario_id": self.scenario.scenario_id, "title": self.scenario.title})
        output = self._orchestrate(self.scenario.user_request)
        trace_path = self.trace.save(self.scenario.scenario_id)
        return RunResult(
            scenario_id=self.scenario.scenario_id,
            final_output=output,
            tools_used=self.tools_used,
            handoffs=self.handoffs,
            state_snapshot=asdict(self.state),
            policy_violations=self.policy_violations,
            success=not self.policy_violations,
            trace_path=trace_path,
        )

    def _orchestrate(self, request: str) -> str:
        self.trace.add("agent_decision", {"agent": "orchestrator", "request": request})
        lower = request.lower()
        if "refund" in lower:
            self._handoff("orchestrator", "billing_specialist", "refund intent detected")
            return self._billing_specialist(request)
        if "order" in lower or "delivery" in lower:
            self._handoff("orchestrator", "order_specialist", "order issue detected")
            return self._order_specialist(request)
        self._handoff("orchestrator", "knowledge_specialist", "general support / kb query")
        return self._knowledge_specialist(request)

    def _extract_order_id(self, request: str) -> str:
        for token in request.replace(",", " ").split():
            cleaned = token.strip(" .!?:;()[]{}").upper()
            if cleaned.startswith("ORD-"):
                return cleaned
        return "ORD-1001"

    def _extract_refund_amount(self, request: str) -> float:
        for token in request.replace("$", " ").split():
            if token.replace(".", "", 1).isdigit():
                return float(token)
        return 100.0

    def _inject_context_loss_if_needed(self) -> None:
        if "context_drop" in self.scenario.injected_faults:
            self.state.order_id = None
            self.trace.add("fault", {"name": "context_drop", "effect": "order_id removed from state"})

    def _recover_missing_order_id(self, request: str) -> None:
        if not self.state.order_id:
            self.state.order_id = self._extract_order_id(request)
            self.state.notes.append("Recovered missing order_id from original user request")
            self.trace.add("recovery", {"action": "recovered_order_id", "order_id": self.state.order_id})

    def _order_specialist(self, request: str) -> str:
        self.state.issue_type = "order_status"
        self.state.order_id = self._extract_order_id(request)
        status = self._call_tool("get_order_status", order_id=self.state.order_id)
        if status.get("error"):
            self.state.escalation_required = True
            self._call_tool("notify_human", reason="Order lookup failure")
            return "I could not retrieve the order safely, so I escalated this to a human agent."
        if not status.get("found"):
            return f"I could not find order {self.state.order_id}."
        if status.get("status") == "delayed":
            self._call_tool("update_ticket", summary="Delayed order follow-up", priority="medium")
            return f"Order {self.state.order_id} is delayed by about {status.get('eta_days')} days."
        return f"Order {self.state.order_id} status is {status.get('status')}."

    def _billing_specialist(self, request: str) -> str:
        self.state.issue_type = "refund"
        self.state.order_id = self._extract_order_id(request)
        self.state.refund_amount = self._extract_refund_amount(request)
        self._inject_context_loss_if_needed()
        self._recover_missing_order_id(request)

        order = self._call_tool("get_order_status", order_id=self.state.order_id)
        if order.get("error"):
            self.state.escalation_required = True
            self._call_tool("notify_human", reason="Refund blocked because order lookup failed")
            return "I could not verify the order safely, so I escalated the refund review."

        refund = self._call_tool(
            "issue_refund", order_id=self.state.order_id, amount=float(self.state.refund_amount or 0)
        )
        if refund.get("error"):
            message = str(refund["error"])
            if "threshold" in message or "eligible" in message:
                self.policy_violations.append(message)
                self.state.escalation_required = True
                self._call_tool("notify_human", reason=message)
                return "The refund could not be processed automatically, so I escalated it for review."
            self._call_tool("notify_human", reason="Unexpected refund failure")
            return "The refund flow hit an execution error and was escalated."
        self._call_tool("update_ticket", summary="Refund completed", priority="high")
        return f"Refund of ${self.state.refund_amount:.2f} was issued for order {self.state.order_id}."

    def _knowledge_specialist(self, request: str) -> str:
        self.state.issue_type = "kb"
        kb = self._call_tool("search_kb", query=request)
        if kb.get("error"):
            self._call_tool("notify_human", reason="KB unavailable")
            return "The knowledge base is unavailable, so I escalated your question."
        return kb["answer"]
