#!/usr/bin/env python3
"""Validate that operational traces correlate high-risk changes with scoped evidence."""

import argparse
import fnmatch
import json
import sys
from pathlib import Path

ACCEPTED_EVIDENCE_PREFIXES = ("test:", "ci:", "runtime:", "artifact:", "policy:")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_changed(path):
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def classify_high_risk(changed, policy):
    high = []
    required = set(policy.get("traceRequiredAt", []))
    for path in changed:
        matched = []
        for rule in policy.get("rules", []):
            if fnmatch.fnmatch(path, rule["pattern"]):
                matched.append(rule["risk"])
        if "high" in matched and "high" in required:
            high.append(path)
    return high


def trace_covers(trace, path):
    patterns = trace.get("changeContext", {}).get("paths", [])
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def validate_trace(trace, high_risk_paths):
    failures = []
    if trace.get("schemaVersion") != "openforge-agent-trace/v1":
        failures.append("trace schemaVersion must be openforge-agent-trace/v1")

    context = trace.get("changeContext")
    if not isinstance(context, dict):
        failures.append("trace changeContext is required")
        context = {}
    paths = context.get("paths", [])
    if not isinstance(paths, list) or not paths:
        failures.append("trace changeContext.paths must contain at least one path or glob")

    uncovered = [path for path in high_risk_paths if not trace_covers(trace, path)]
    if uncovered:
        failures.append("uncovered high-risk paths: " + ", ".join(uncovered))

    verification_events = [e for e in trace.get("events", []) if e.get("type") in {"verification", "regression_verification"}]
    if not verification_events:
        failures.append("trace must include verification or regression_verification events")
    else:
        scoped = [e for e in verification_events if str(e.get("scope", "")).strip()]
        if not scoped:
            failures.append("at least one verification event must declare scope")
        evidence = [ref for e in verification_events for ref in e.get("evidence", []) if isinstance(ref, str)]
        typed = [ref for ref in evidence if ref.startswith(ACCEPTED_EVIDENCE_PREFIXES)]
        if not typed:
            failures.append("verification must include typed evidence (test:, ci:, runtime:, artifact:, or policy:)")

    completion = [e for e in trace.get("events", []) if e.get("type") == "completion_claim"]
    if completion and not verification_events:
        failures.append("completion claim requires verification evidence")
    return failures


def main():
    parser = argparse.ArgumentParser(description="OpenForge trace/change evidence correlation gate")
    parser.add_argument("--policy", required=True)
    parser.add_argument("--changed-files", required=True)
    parser.add_argument("--trace", action="append", required=True)
    parser.add_argument("--report-out")
    args = parser.parse_args()

    policy = load_json(args.policy)
    changed = read_changed(args.changed_files)
    high_risk = classify_high_risk(changed, policy)
    traces = [load_json(path) for path in args.trace]

    failures = []
    uncovered = []
    for path in high_risk:
        if not any(trace_covers(trace, path) for trace in traces):
            uncovered.append(path)
    if uncovered:
        failures.append("no operational trace covers high-risk paths: " + ", ".join(uncovered))

    trace_results = []
    for source, trace in zip(args.trace, traces):
        trace_failures = validate_trace(trace, [p for p in high_risk if trace_covers(trace, p)])
        trace_results.append({"trace": source, "traceId": trace.get("traceId"), "failures": trace_failures})
        failures.extend(f"{source}: {item}" for item in trace_failures)

    report = {
        "schemaVersion": "openforge-agent-evidence-quality/v1",
        "highRiskPaths": high_risk,
        "traceResults": trace_results,
        "passed": not failures,
        "failures": failures,
    }
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.report_out:
        Path(args.report_out).write_text(rendered + "\n", encoding="utf-8")
    if failures:
        print("Agent trace evidence correlation failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
