from __future__ import annotations

import json

import typer
from rich import print

from agent_reliability_lab.agents.runtime import ReliabilityRuntime
from agent_reliability_lab.evals.runner import EvalRunner
from agent_reliability_lab.scenarios.library import SCENARIOS

app = typer.Typer(help="Agent Reliability Lab CLI")


@app.command()
def list_scenarios() -> None:
    for scenario_id, scenario in SCENARIOS.items():
        print(f"- {scenario_id}: {scenario.title}")


@app.command()
def run(scenario: str, use_openai: bool = False) -> None:
    if scenario not in SCENARIOS:
        raise typer.BadParameter(f"Unknown scenario: {scenario}")
    if use_openai:
        print("[yellow]OpenAI mode placeholder selected. Local runtime used unless adapter is implemented.[/yellow]")
    result = ReliabilityRuntime(SCENARIOS[scenario]).run()
    print(json.dumps({
        "scenario_id": result.scenario_id,
        "final_output": result.final_output,
        "tools_used": [t.tool_name for t in result.tools_used],
        "handoffs": [h.to_agent for h in result.handoffs],
        "policy_violations": result.policy_violations,
        "trace_path": result.trace_path,
    }, indent=2))


@app.command()
def eval(dataset: str, min_score: float = 0.8) -> None:
    report = EvalRunner().run_dataset(dataset)
    score = report["summary"]["reliability_score"]
    print(json.dumps(report["summary"], indent=2))
    if score < min_score:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
