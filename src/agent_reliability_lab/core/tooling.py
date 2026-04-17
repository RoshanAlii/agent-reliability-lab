from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from agent_reliability_lab.core.models import ToolCallRecord


ToolFn = Callable[..., Dict[str, Any]]


@dataclass
class ToolSpec:
    name: str
    description: str
    fn: ToolFn


@dataclass
class ToolRegistry:
    tools: Dict[str, ToolSpec] = field(default_factory=dict)

    def register(self, spec: ToolSpec) -> None:
        self.tools[spec.name] = spec

    def call(self, name: str, **kwargs: Any) -> ToolCallRecord:
        spec = self.tools[name]
        try:
            result = spec.fn(**kwargs)
            return ToolCallRecord(tool_name=name, args=kwargs, success=True, result=result)
        except Exception as exc:  # noqa: BLE001
            return ToolCallRecord(
                tool_name=name,
                args=kwargs,
                success=False,
                result={},
                error=str(exc),
            )

    def list_tools(self) -> list[str]:
        return list(self.tools.keys())
