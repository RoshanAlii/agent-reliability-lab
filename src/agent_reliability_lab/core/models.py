from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    role: str
    content: str


@dataclass
class AgentState:
    user_id: str = "demo-user"
    order_id: Optional[str] = None
    refund_amount: Optional[float] = None
    issue_type: Optional[str] = None
    escalation_required: bool = False
    notes: List[str] = field(default_factory=list)
    memory: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCallRecord:
    tool_name: str
    args: Dict[str, Any]
    success: bool
    result: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class HandoffRecord:
    from_agent: str
    to_agent: str
    reason: str


@dataclass
class RunResult:
    scenario_id: str
    final_output: str
    tools_used: List[ToolCallRecord] = field(default_factory=list)
    handoffs: List[HandoffRecord] = field(default_factory=list)
    state_snapshot: Dict[str, Any] = field(default_factory=dict)
    policy_violations: List[str] = field(default_factory=list)
    success: bool = True
    trace_path: Optional[str] = None


@dataclass
class Scenario:
    scenario_id: str
    title: str
    user_request: str
    expected_tools: List[str]
    expected_handoffs: List[str]
    required_state_keys: List[str]
    disallowed_tools: List[str] = field(default_factory=list)
    must_fail_safe: bool = False
    injected_faults: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
