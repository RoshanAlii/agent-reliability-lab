from __future__ import annotations

import argparse
import json
import sys

from agent_reliability_lab.evals.runner import EvalRunner


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--min-score", type=float, default=0.80)
    args = parser.parse_args()

    report = EvalRunner().run_dataset(args.dataset)
    score = report["summary"]["reliability_score"]
    print(json.dumps(report, indent=2))
    if score < args.min_score:
        print(f"Reliability gate failed: {score:.4f} < {args.min_score:.4f}")
        return 1
    print(f"Reliability gate passed: {score:.4f} >= {args.min_score:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
