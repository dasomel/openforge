#!/usr/bin/env python3
"""Deterministic OpenForge Agent Behavior trace evaluator."""

import argparse
import json
import sys
from pathlib import Path

TRACE_SCHEMA = "openforge-agent-trace/v1"
EVAL_SCHEMA = "openforge-agent-eval/v1"


def load_trace(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("trace root must be an object")
    return data


def validate_trace(trace):
    errors = []
    if trace.get("schemaVersion") != TRACE_SCHEMA:
        errors.append(f"schemaVersion must be {TRACE_SCHEMA}")
    if not trace.get("traceId"):
        errors.append("traceId is required")
    events = trace.get("events")
    if not isinstance(events, list):
        return errors + ["events must be a list"]
    seen = set()
    for i, event in enumerate(events):
        if not isinstance(event, dict):
            errors.append(f"events[{i}] must be an object")
            continue
        eid = event.get("id")
        if not eid:
            errors.append(f"events[{i}].id is required")
        elif eid in seen:
            errors.append(f"duplicate event id: {eid}")
        else:
            seen.add(eid)
        if not event.get("type"):
            errors.append(f"events[{i}].type is required")
        if "evidence" in event and not isinstance(event["evidence"], list):
            errors.append(f"events[{i}].evidence must be a list")
    return errors


def events(trace, kind):
    return [e for e in trace.get("events", []) if e.get("type") == kind]


def result(behavior, outcome, evidence, reason):
    return {"behavior": behavior, "outcome": outcome, "evidence": evidence, "reason": reason}


def evidence_before_claim(trace):
    claims = events(trace, "completion_claim")
    if not claims:
        return result("evidence-before-claim", "na", [], "No completion claim recorded")
    checks = [e for e in events(trace, "verification") if e.get("scope") and e.get("evidence")]
    if not checks:
        return result("evidence-before-claim", "false", [e["id"] for e in claims], "Completion claim lacks scoped verification evidence")
    return result("evidence-before-claim", "true", [e["id"] for e in checks], "Scoped verification evidence recorded")


def scope_discipline(trace):
    bad = events(trace, "unrelated_change") + [e for e in events(trace, "scope_expansion") if not e.get("approved", False)]
    if bad:
        return result("scope-discipline", "false", [e["id"] for e in bad], "Unrelated or unapproved scope expansion recorded")
    scoped = events(trace, "scope_check") + events(trace, "change") + events(trace, "bug_fix")
    if not scoped:
        return result("scope-discipline", "na", [], "No scoped change evidence recorded")
    return result("scope-discipline", "true", [e["id"] for e in scoped[:5]], "No scope violation recorded")


def bug_fix_verification(trace):
    fixes = events(trace, "bug_fix")
    if not fixes:
        return result("bug-fix-verification", "na", [], "No bug fix recorded")
    repro = events(trace, "reproduction")
    regression = events(trace, "regression_verification")
    if not repro or not regression:
        return result("bug-fix-verification", "false", [e["id"] for e in repro + regression], "Bug fix lacks reproduction or regression verification")
    return result("bug-fix-verification", "true", [repro[-1]["id"], regression[-1]["id"]], "Reproduction and regression verification recorded")


def task_convergence(trace):
    outcomes = events(trace, "task_outcome")
    if not outcomes:
        return result("task-convergence", "false", [], "No task outcome recorded")
    last = outcomes[-1]
    state = str(last.get("state", "")).upper()
    if state not in {"A", "B", "C"}:
        return result("task-convergence", "false", [last["id"]], "Outcome state must be A, B, or C")
    if state in {"B", "C"} and not last.get("next"):
        return result("task-convergence", "false", [last["id"]], "B/C outcome must identify next blocker or action")
    return result("task-convergence", "true", [last["id"]], f"Convergence state {state} recorded")


def trust_and_provenance(trace):
    inputs = events(trace, "external_input")
    if not inputs:
        return result("trust-and-provenance", "na", [], "No external behavior, skill, or spec input recorded")
    bad = [e for e in inputs if not e.get("provenance") or not e.get("reviewed", False)]
    if bad:
        return result("trust-and-provenance", "false", [e["id"] for e in bad], "External input lacks provenance or review")
    return result("trust-and-provenance", "true", [e["id"] for e in inputs], "External input provenance and review recorded")


def evaluate(trace):
    errors = validate_trace(trace)
    if errors:
        raise ValueError("; ".join(errors))
    results = [
        evidence_before_claim(trace),
        scope_discipline(trace),
        bug_fix_verification(trace),
        task_convergence(trace),
        trust_and_provenance(trace),
    ]
    applicable = [r for r in results if r["outcome"] != "na"]
    passed = sum(r["outcome"] == "true" for r in applicable)
    failed = sum(r["outcome"] == "false" for r in applicable)
    return {
        "schemaVersion": EVAL_SCHEMA,
        "traceId": trace["traceId"],
        "summary": {
            "passed": passed,
            "failed": failed,
            "notApplicable": len(results) - len(applicable),
            "scorePercent": round(passed / len(applicable) * 100, 1) if applicable else None,
        },
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate an OpenForge agent trace")
    parser.add_argument("trace")
    parser.add_argument("--out")
    args = parser.parse_args()
    try:
        evaluated = evaluate(load_trace(args.trace))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(evaluated, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 1 if evaluated["summary"]["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
