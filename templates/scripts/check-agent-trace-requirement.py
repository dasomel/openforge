#!/usr/bin/env python3
"""Require an operational trace when a change touches policy-defined high-risk paths."""

import argparse
import fnmatch
import json
import sys
from pathlib import Path

RISK_ORDER = {"low": 0, "medium": 1, "high": 2}


def load_policy(path: Path):
    data = json.loads(path.read_text())
    if data.get("schemaVersion") != "openforge-agent-risk-policy/v1":
        raise ValueError("unsupported risk policy schemaVersion")
    if not isinstance(data.get("rules"), list):
        raise ValueError("risk policy rules must be a list")
    return data


def match_path(path: str, pattern: str) -> bool:
    # fnmatch does not treat ** specially, but for repository paths this gives
    # the desired recursive behavior because * may match '/'.
    return fnmatch.fnmatchcase(path, pattern)


def classify(paths, policy):
    default = policy.get("defaultRisk", "low")
    if default not in RISK_ORDER:
        raise ValueError(f"unknown default risk: {default}")
    highest = default
    matches = []
    for path in paths:
        for rule in policy["rules"]:
            risk = rule.get("risk")
            pattern = rule.get("pattern")
            if risk not in RISK_ORDER or not pattern:
                raise ValueError("each risk rule requires known risk and non-empty pattern")
            if match_path(path, pattern):
                matches.append({"path": path, "risk": risk, "pattern": pattern, "reason": rule.get("reason", "")})
                if RISK_ORDER[risk] > RISK_ORDER[highest]:
                    highest = risk
    return highest, matches


def trace_changed(paths, prefix):
    return any(path.startswith(prefix) and path.endswith(".json") for path in paths)


def main():
    parser = argparse.ArgumentParser(description="OpenForge risk-based operational trace requirement")
    parser.add_argument("--policy", required=True)
    parser.add_argument("--changed-files", required=True, help="newline-delimited changed repository paths")
    parser.add_argument("--report-out")
    args = parser.parse_args()

    try:
        policy = load_policy(Path(args.policy))
        changed = [line.strip() for line in Path(args.changed_files).read_text().splitlines() if line.strip()]
        risk, matches = classify(changed, policy)
        required_levels = set(policy.get("traceRequiredAt", ["high"]))
        require_trace = risk in required_levels
        prefix = policy.get("tracePathPrefix", ".agents/evals/traces/")
        has_trace = trace_changed(changed, prefix)
        result = {
            "schemaVersion": "openforge-agent-risk-result/v1",
            "risk": risk,
            "traceRequired": require_trace,
            "traceChanged": has_trace,
            "changedFiles": changed,
            "matches": matches,
        }
        if args.report_out:
            out = Path(args.report_out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        if require_trace and not has_trace:
            print(
                f"High-risk change requires an operational trace change under {prefix}",
                file=sys.stderr,
            )
            return 1
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"risk policy error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
