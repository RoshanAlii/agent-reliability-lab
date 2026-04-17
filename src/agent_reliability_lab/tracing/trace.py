from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class TraceEvent:
    ts: str
    event_type: str
    payload: Dict[str, Any]


class TraceCollector:
    def __init__(self, output_dir: str = "artifacts/traces") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.events: List[TraceEvent] = []

    def add(self, event_type: str, payload: Dict[str, Any]) -> None:
        self.events.append(
            TraceEvent(
                ts=datetime.now(timezone.utc).isoformat(),
                event_type=event_type,
                payload=payload,
            )
        )

    def save(self, scenario_id: str) -> str:
        path = self.output_dir / f"{scenario_id}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump([asdict(event) for event in self.events], f, indent=2)
        return str(path)
