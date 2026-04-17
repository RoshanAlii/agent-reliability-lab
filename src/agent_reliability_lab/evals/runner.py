from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import yaml

from agent_reliability_lab.agents.runtime import ReliabilityRuntime
from agent_reliability_lab.evals.grader import ScoreBreakdown, grade_run, summarize
from agent_reliability_lab.scenarios.library import SCENARIOS


class EvalRunner:
    def __init__(self, trace_dir: str = "artifacts/traces", report_dir: str = "artifacts/reports") -> None:
        self.trace_dir = trace_dir
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def load_dataset(self, path: str) -> List[str]:
        with open(path, "r", encoding="utf-8") as f:
            payload = yaml.safe_load(f)
        return payload["scenarios"]

    def run_dataset(self, dataset_path: str) -> Dict[str, Any]:
        scenario_ids = self.load_dataset(dataset_path)
        detailed: List[Dict[str, Any]] = []
        scores: List[ScoreBreakdown] = []
        for scenario_id in scenario_ids:
            scenario = SCENARIOS[scenario_id]
            run = ReliabilityRuntime(scenario, trace_dir=self.trace_dir).run()
            score = grade_run(run, scenario)
            scores.append(score)
            detailed.append(
                {
                    "scenario_id": scenario_id,
                    "final_output": run.final_output,
                    "tools_used": [t.tool_name for t in run.tools_used],
                    "handoffs": [h.to_agent for h in run.handoffs],
                    "policy_violations": run.policy_violations,
                    "score": score.weighted_score,
                    "trace_path": run.trace_path,
                    "notes": score.notes,
                }
            )
        summary = summarize(scores)
        report = {"summary": summary, "details": detailed}
        report_path = self.report_dir / "latest_report.json"
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        return report
