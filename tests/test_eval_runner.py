from agent_reliability_lab.evals.runner import EvalRunner


def test_eval_runner_produces_reliability_score() -> None:
    report = EvalRunner(trace_dir="artifacts/test_traces", report_dir="artifacts/test_reports").run_dataset(
        "data/evals/core_benchmark.yaml"
    )
    assert report["summary"]["reliability_score"] >= 0.8
