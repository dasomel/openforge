#!/usr/bin/env python3
"""Evaluate a trace and fail only when it regresses from a trusted baseline."""

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd):
    completed = subprocess.run(cmd, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    return completed.returncode


def main():
    parser = argparse.ArgumentParser(description="OpenForge Agent Eval CI gate")
    parser.add_argument("--trace", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--current-out", default=".agents/evals/current-eval.json")
    parser.add_argument("--comparison-out", default=".agents/evals/comparison.json")
    parser.add_argument("--scripts-dir", default=str(Path(__file__).resolve().parent))
    args = parser.parse_args()

    scripts = Path(args.scripts_dir)
    evaluator = scripts / "evaluate-agent-trace.py"
    comparator = scripts / "compare-agent-evals.py"
    current = Path(args.current_out)
    comparison = Path(args.comparison_out)
    current.parent.mkdir(parents=True, exist_ok=True)
    comparison.parent.mkdir(parents=True, exist_ok=True)

    # Evaluator returns 1 when the current trace itself has a failed behavior.
    # Do not fail here: the comparison determines whether this is a regression
    # relative to the trusted baseline.
    eval_rc = run([sys.executable, str(evaluator), args.trace, "--out", str(current)])
    if eval_rc == 2:
        return 2

    compare_rc = run([
        sys.executable,
        str(comparator),
        args.baseline,
        str(current),
        "--out",
        str(comparison),
    ])
    if compare_rc == 1:
        print("Agent behavior regression detected", file=sys.stderr)
    return compare_rc


if __name__ == "__main__":
    raise SystemExit(main())
