#!/usr/bin/env python3
"""OpenForge deterministic repository maturity assessor.

This tool intentionally has no AI/LLM dependency. It evaluates observable repository
artifacts and produces reproducible scores from versioned rules.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import Iterable

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_RULES = ROOT / "rules" / "maturity-v0.1.json"


@dataclass
class Finding:
    rule_id: str
    category: str
    title: str
    status: str
    score: float
    weight: float
    evidence: list[str]
    remediation: str


def _glob(root: pathlib.Path, patterns: Iterable[str]) -> list[str]:
    matches: set[str] = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file():
                matches.add(str(path.relative_to(root)))
    return sorted(matches)


def _contains(root: pathlib.Path, patterns: Iterable[str], needles: Iterable[str]) -> list[str]:
    evidence: list[str] = []
    lowered = [n.lower() for n in needles]
    for rel in _glob(root, patterns):
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        if any(n in text for n in lowered):
            evidence.append(rel)
    return evidence


def _command(root: pathlib.Path, command: list[str], timeout: int) -> tuple[bool, list[str]]:
    try:
        completed = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, [f"command error: {exc}"]
    detail = (completed.stdout + completed.stderr).strip().splitlines()
    evidence = [f"exit={completed.returncode}"] + detail[-3:]
    return completed.returncode == 0, evidence


def evaluate_rule(root: pathlib.Path, rule: dict, run_commands: bool) -> Finding:
    kind = rule["check"]["type"]
    evidence: list[str] = []
    passed = False

    if kind == "any_file":
        evidence = _glob(root, rule["check"]["patterns"])
        passed = bool(evidence)
    elif kind == "all_files":
        found = []
        passed = True
        for pattern in rule["check"]["patterns"]:
            current = _glob(root, [pattern])
            if not current:
                passed = False
            found.extend(current)
        evidence = sorted(set(found))
    elif kind == "contains":
        evidence = _contains(root, rule["check"]["patterns"], rule["check"]["needles"])
        passed = bool(evidence)
    elif kind == "command":
        if not run_commands:
            return Finding(rule["id"], rule["category"], rule["title"], "SKIP", 0.0,
                           float(rule["weight"]), ["execution checks disabled"], rule.get("remediation", ""))
        passed, evidence = _command(root, rule["check"]["command"], int(rule["check"].get("timeout", 60)))
    else:
        raise ValueError(f"unsupported check type: {kind}")

    status = "PASS" if passed else "FAIL"
    score = float(rule["weight"]) if passed else 0.0
    return Finding(rule["id"], rule["category"], rule["title"], status, score,
                   float(rule["weight"]), evidence, rule.get("remediation", ""))


def grade(score: float) -> str:
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "E"


def level(score: float) -> str:
    if score >= 90: return "L5 Optimizing"
    if score >= 80: return "L4 Resilient"
    if score >= 70: return "L3 Production"
    if score >= 55: return "L2 Managed"
    if score >= 35: return "L1 Repeatable"
    return "L0 Initial"


def assess(root: pathlib.Path, rules_path: pathlib.Path, run_commands: bool) -> dict:
    rules_doc = json.loads(rules_path.read_text(encoding="utf-8"))
    findings = [evaluate_rule(root, rule, run_commands) for rule in rules_doc["rules"]]

    category_totals: dict[str, dict[str, float]] = {}
    for f in findings:
        bucket = category_totals.setdefault(f.category, {"score": 0.0, "max": 0.0})
        if f.status != "SKIP":
            bucket["score"] += f.score
            bucket["max"] += f.weight

    categories = {}
    total_score = total_max = 0.0
    for name, values in sorted(category_totals.items()):
        pct = round(values["score"] / values["max"] * 100, 1) if values["max"] else 0.0
        categories[name] = {"score": pct, "earned": values["score"], "max": values["max"]}
        total_score += values["score"]
        total_max += values["max"]

    overall = round(total_score / total_max * 100, 1) if total_max else 0.0
    return {
        "schema": "openforge-assessment/v0.1",
        "ruleset": rules_doc["version"],
        "root": str(root.resolve()),
        "overall": overall,
        "grade": grade(overall),
        "level": level(overall),
        "categories": categories,
        "findings": [asdict(f) for f in findings],
    }


def print_text(report: dict) -> None:
    print("OpenForge Maturity Assessment")
    print("=" * 72)
    print(f"Overall: {report['overall']:>5.1f} / 100   Grade: {report['grade']}   {report['level']}")
    print("-" * 72)
    for name, result in report["categories"].items():
        print(f"{name:<24} {result['score']:>5.1f} / 100")
    print("-" * 72)
    failed = [f for f in report["findings"] if f["status"] == "FAIL"]
    if failed:
        print("Findings")
        for f in failed:
            print(f"  FAIL [{f['rule_id']}] {f['title']} (+{f['weight']:g} possible)")
            if f["remediation"]:
                print(f"       {f['remediation']}")
    else:
        print("No failed rules.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic OpenForge maturity assessment")
    parser.add_argument("path", nargs="?", default=".", help="repository path")
    parser.add_argument("--rules", default=str(DEFAULT_RULES), help="ruleset JSON")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", help="write report to file")
    parser.add_argument("--run-commands", action="store_true", help="enable explicit execution rules")
    parser.add_argument("--fail-under", type=float, default=None, help="non-zero exit when score is below threshold")
    args = parser.parse_args()

    report = assess(pathlib.Path(args.path), pathlib.Path(args.rules), args.run_commands)
    rendered = json.dumps(report, indent=2, ensure_ascii=False) if args.format == "json" else None

    if args.output:
        pathlib.Path(args.output).write_text(rendered or json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.format == "json":
        print(rendered)
    else:
        print_text(report)

    if args.fail_under is not None and report["overall"] < args.fail_under:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
