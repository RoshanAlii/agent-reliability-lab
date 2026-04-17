.PHONY: install test eval lint dashboard

install:
	pip install -e .

test:
	pytest

eval:
	python scripts/run_eval_gate.py --dataset data/evals/core_benchmark.yaml --min-score 0.80

lint:
	ruff check src tests

dashboard:
	streamlit run src/agent_reliability_lab/dashboard/app.py
