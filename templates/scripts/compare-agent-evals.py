#!/usr/bin/env python3
"""Compare two OpenForge Agent Behavior eval results and report regressions."""

import argparse
import json
import sys
from pathlib import Path

EVAL_SCHEMA = "openforge-agent-eval/v1"
ORDER = {"false": 0, "na": 1, "true": 2}


def load_eval(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schemaVersion") != EVAL_SCHEMA:
        raise ValueError(f"{path}: schemaVersion must be {EVAL_SCHEMA}")
    return data


def compare(baseline, current):
    before = {r["behavior"]: r for r in baseline.get("results", [])}
    after = {r["behavior"]: r for r in current.get("results", [])}
    regressions = []
    improvements = []
    changes = []
    for behavior in sorted(set(before) | set(after)):
        old = before.get(behavior, {"outcome": "na"})["outcome"]
        new = after.get(behavior, {"outcome": "na"})["outcome"]
        if old == new:
            continue
        item = {"behavior": behavior, "from": old, "to": new}
        changes.append(item)
        if ORDER.get(new, -1) < ORDER.get(old, -1):
            regressions.append(item)
        elif ORDER.get(new, -1) > ORDER.get(old, -1):
            improvements.append(item)
    return {
        "schemaVersion": "openforge-agent-eval-comparison/v1",
        "baselineTraceId": baseline.get("traceId"),
        "currentTraceId": current.get("traceId"),
        "summary": {
            "regressions": len(regressions),
            "improvements": len(improvements),
            "changed": len(changes),
        },
        "regressions": regressions,
        "improvements": improvements,
        "changes": changes,
    }


def main():
    parser = argparse.ArgumentParser(description="Compare OpenForge agent eval results")
    parser.add_argument("baseline")
    parser.add_argument("current")
    parser.add_argument("--out")
    args = parser.parse_args()
    try:
        report = compare(load_eval(args.baseline), load_eval(args.current))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 1 if report["summary"]["regressions"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
