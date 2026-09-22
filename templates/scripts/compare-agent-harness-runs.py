#!/usr/bin/env python3
"""Validate and summarize controlled OpenForge agent harness experiments."""

import argparse
import datetime as dt
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

DATASET_SCHEMA = "openforge-agent-harness-dataset/v1"
COMPARISON_SCHEMA = "openforge-agent-harness-comparison/v1"

COHORT_FIELDS = (
    "taskId",
    "taskClass",
    "repository",
    "repositoryRevision",
    "model",
    "environment",
)
USAGE_METRICS = (
    "inputTokens",
    "cachedInputTokens",
    "outputTokens",
    "reasoningTokens",
    "initialContextTokens",
    "instructionChars",
    "toolSchemaBytes",
    "turns",
    "toolCalls",
    "failedToolCalls",
    "elapsedSeconds",
    "humanInterventions",
    "contextCompactions",
    "estimatedApiCostUsd",
)
INTEGER_METRICS = set(USAGE_METRICS) - {"elapsedSeconds", "estimatedApiCostUsd"}
TASK_CLASSES = {"simple", "bug-fix", "cross-component", "runtime-ops", "multi-session"}
NETWORK_ACCESS = {"disabled", "restricted", "enabled"}
REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REVISION_PATTERN = re.compile(r"^[0-9a-f]{7,40}$")

TOP_LEVEL_KEYS = {"schemaVersion", "datasetId", "cohort", "runs"}
COHORT_KEYS = set(COHORT_FIELDS)
MODEL_KEYS = {"provider", "name", "version", "reasoningEffort"}
ENVIRONMENT_KEYS = {"operatingSystem", "networkAccess", "toolProfile", "maxTurns", "notes"}
RUN_KEYS = {"runId", "attempt", "traceId", "harness", "outcome", "usage", "measurementNotes"}
HARNESS_KEYS = {"name", "version", "configuration"}
OUTCOME_KEYS = {"success", "score", "safetyPassed", "evaluator"}
USAGE_KEYS = set(USAGE_METRICS) | {"pricingDate"}


def _is_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def _require_keys(value, keys, location, errors):
    if not isinstance(value, dict):
        errors.append(f"{location} must be an object")
        return False
    for key in keys:
        if key not in value:
            errors.append(f"{location}.{key} is required")
    return True


def _reject_unknown_keys(value, allowed, location, errors):
    if not isinstance(value, dict):
        return
    for key in sorted(set(value) - set(allowed)):
        errors.append(f"{location}.{key} is not allowed")


def validate_dataset(data):
    """Return semantic validation errors for one dataset."""
    errors = []
    if not isinstance(data, dict):
        return ["dataset must be an object"]
    _reject_unknown_keys(data, TOP_LEVEL_KEYS, "dataset", errors)
    if data.get("schemaVersion") != DATASET_SCHEMA:
        errors.append(f"schemaVersion must be {DATASET_SCHEMA}")
    if not _nonempty_string(data.get("datasetId")):
        errors.append("datasetId must be a non-empty string")

    cohort = data.get("cohort")
    if _require_keys(cohort, COHORT_FIELDS, "cohort", errors):
        _reject_unknown_keys(cohort, COHORT_KEYS, "cohort", errors)
        for field in ("taskId", "repository", "repositoryRevision"):
            if not _nonempty_string(cohort.get(field)):
                errors.append(f"cohort.{field} must be a non-empty string")
        if _nonempty_string(cohort.get("repository")) and not REPOSITORY_PATTERN.fullmatch(cohort["repository"]):
            errors.append("cohort.repository must be an owner/repository slug")
        if _nonempty_string(cohort.get("repositoryRevision")) and not REVISION_PATTERN.fullmatch(cohort["repositoryRevision"]):
            errors.append("cohort.repositoryRevision must be a 7-40 character lowercase git SHA")
        if cohort.get("taskClass") not in TASK_CLASSES:
            errors.append("cohort.taskClass is invalid")

        model = cohort.get("model")
        if _require_keys(model, ("provider", "name", "version", "reasoningEffort"), "cohort.model", errors):
            _reject_unknown_keys(model, MODEL_KEYS, "cohort.model", errors)
            for field in ("provider", "name", "version", "reasoningEffort"):
                if not _nonempty_string(model.get(field)):
                    errors.append(f"cohort.model.{field} must be a non-empty string")

        environment = cohort.get("environment")
        if _require_keys(environment, ("operatingSystem", "networkAccess", "toolProfile", "maxTurns"), "cohort.environment", errors):
            _reject_unknown_keys(environment, ENVIRONMENT_KEYS, "cohort.environment", errors)
            for field in ("operatingSystem", "toolProfile"):
                if not _nonempty_string(environment.get(field)):
                    errors.append(f"cohort.environment.{field} must be a non-empty string")
            if environment.get("networkAccess") not in NETWORK_ACCESS:
                errors.append("cohort.environment.networkAccess is invalid")
            max_turns = environment.get("maxTurns")
            if not isinstance(max_turns, int) or isinstance(max_turns, bool) or max_turns < 1:
                errors.append("cohort.environment.maxTurns must be a positive integer")

    runs = data.get("runs")
    if not isinstance(runs, list) or not runs:
        errors.append("runs must be a non-empty array")
        return errors

    run_ids = set()
    attempts = set()
    for index, run in enumerate(runs):
        location = f"runs[{index}]"
        if not _require_keys(run, ("runId", "attempt", "harness", "outcome", "usage", "measurementNotes"), location, errors):
            continue
        _reject_unknown_keys(run, RUN_KEYS, location, errors)
        run_id = run.get("runId")
        if not _nonempty_string(run_id):
            errors.append(f"{location}.runId must be a non-empty string")
        elif run_id in run_ids:
            errors.append(f"{location}.runId duplicates {run_id}")
        else:
            run_ids.add(run_id)

        attempt = run.get("attempt")
        if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
            errors.append(f"{location}.attempt must be a positive integer")

        harness = run.get("harness")
        harness_key = None
        if _require_keys(harness, ("name", "version", "configuration"), f"{location}.harness", errors):
            _reject_unknown_keys(harness, HARNESS_KEYS, f"{location}.harness", errors)
            for field in ("name", "version", "configuration"):
                if not _nonempty_string(harness.get(field)):
                    errors.append(f"{location}.harness.{field} must be a non-empty string")
            if all(_nonempty_string(harness.get(field)) for field in ("name", "version", "configuration")):
                harness_key = tuple(harness[field] for field in ("name", "version", "configuration"))
        if harness_key is not None and isinstance(attempt, int) and not isinstance(attempt, bool):
            attempt_key = harness_key + (attempt,)
            if attempt_key in attempts:
                errors.append(f"{location}.attempt duplicates attempt {attempt} for the same harness")
            attempts.add(attempt_key)

        outcome = run.get("outcome")
        if _require_keys(outcome, ("success", "score", "safetyPassed", "evaluator"), f"{location}.outcome", errors):
            _reject_unknown_keys(outcome, OUTCOME_KEYS, f"{location}.outcome", errors)
            if not isinstance(outcome.get("success"), bool):
                errors.append(f"{location}.outcome.success must be boolean")
            score = outcome.get("score")
            if score is not None and (not _is_number(score) or score < 0 or score > 1):
                errors.append(f"{location}.outcome.score must be null or a number from 0 to 1")
            if outcome.get("safetyPassed") is not None and not isinstance(outcome.get("safetyPassed"), bool):
                errors.append(f"{location}.outcome.safetyPassed must be boolean or null")
            if not _nonempty_string(outcome.get("evaluator")):
                errors.append(f"{location}.outcome.evaluator must be a non-empty string")

        usage = run.get("usage")
        required_usage = USAGE_METRICS + ("pricingDate",)
        if _require_keys(usage, required_usage, f"{location}.usage", errors):
            _reject_unknown_keys(usage, USAGE_KEYS, f"{location}.usage", errors)
            for metric in USAGE_METRICS:
                value = usage.get(metric)
                if value is None:
                    continue
                if not _is_number(value) or value < 0:
                    errors.append(f"{location}.usage.{metric} must be null or a non-negative number")
                elif metric in INTEGER_METRICS and not isinstance(value, int):
                    errors.append(f"{location}.usage.{metric} must be null or a non-negative integer")
            tool_calls = usage.get("toolCalls")
            failed_tool_calls = usage.get("failedToolCalls")
            if _is_number(tool_calls) and _is_number(failed_tool_calls) and failed_tool_calls > tool_calls:
                errors.append(f"{location}.usage.failedToolCalls cannot exceed toolCalls")
            cost = usage.get("estimatedApiCostUsd")
            pricing_date = usage.get("pricingDate")
            if cost is not None and not _nonempty_string(pricing_date):
                errors.append(f"{location}.usage.pricingDate is required when estimatedApiCostUsd is recorded")
            if cost is None and pricing_date is not None:
                errors.append(f"{location}.usage.pricingDate must be null when estimatedApiCostUsd is null")
            if _nonempty_string(pricing_date):
                try:
                    dt.date.fromisoformat(pricing_date)
                except ValueError:
                    errors.append(f"{location}.usage.pricingDate must be a valid YYYY-MM-DD date")

        notes = run.get("measurementNotes")
        if not isinstance(notes, list) or any(not _nonempty_string(note) for note in notes):
            errors.append(f"{location}.measurementNotes must be an array of non-empty strings")
    return errors


def load_dataset(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_dataset(data)
    if errors:
        raise ValueError(f"{path}: " + "; ".join(errors))
    return data


def _cohort_fingerprint(cohort):
    return json.dumps(cohort, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _aggregate(values, total):
    observed = [value for value in values if value is not None]
    mean = None if not observed else round(sum(observed) / len(observed), 6)
    return {"mean": mean, "observedRuns": len(observed), "totalRuns": total}


def _harness_key(harness):
    return harness["name"], harness["version"], harness["configuration"]


def compare_datasets(datasets):
    """Compare already validated datasets from one controlled cohort."""
    if not datasets:
        raise ValueError("at least one dataset is required")
    baseline = datasets[0]["cohort"]
    baseline_fingerprint = _cohort_fingerprint(baseline)
    for data in datasets[1:]:
        if _cohort_fingerprint(data["cohort"]) != baseline_fingerprint:
            raise ValueError(
                f"dataset {data['datasetId']} does not match the controlled cohort "
                "(task, revision, model, and environment must be identical)"
            )

    grouped = defaultdict(list)
    seen_run_ids = set()
    for data in datasets:
        for run in data["runs"]:
            if run["runId"] in seen_run_ids:
                raise ValueError(f"runId {run['runId']} appears in more than one dataset")
            seen_run_ids.add(run["runId"])
            grouped[_harness_key(run["harness"])].append(run)

    results = []
    for key in sorted(grouped):
        runs = grouped[key]
        total = len(runs)
        successes = sum(1 for run in runs if run["outcome"]["success"])
        safety_values = [run["outcome"]["safetyPassed"] for run in runs]
        safety_observed = [value for value in safety_values if value is not None]
        usage = {
            metric: _aggregate([run["usage"][metric] for run in runs], total)
            for metric in USAGE_METRICS
        }
        paired_tool_runs = [
            run for run in runs
            if run["usage"]["toolCalls"] is not None and run["usage"]["failedToolCalls"] is not None
        ]
        total_tool_calls = sum(run["usage"]["toolCalls"] for run in paired_tool_runs)
        total_failed_tool_calls = sum(run["usage"]["failedToolCalls"] for run in paired_tool_runs)
        tool_failure_rate = None if total_tool_calls == 0 else round(total_failed_tool_calls / total_tool_calls, 6)
        results.append({
            "harness": {"name": key[0], "version": key[1], "configuration": key[2]},
            "correctness": {
                "attempts": total,
                "successes": successes,
                "successRate": round(successes / total, 6),
                "score": _aggregate([run["outcome"]["score"] for run in runs], total),
            },
            "efficiency": {
                metric: usage[metric]
                for metric in (
                    "inputTokens", "cachedInputTokens", "outputTokens", "reasoningTokens",
                    "initialContextTokens", "instructionChars", "toolSchemaBytes", "turns",
                    "toolCalls", "elapsedSeconds", "estimatedApiCostUsd",
                )
            },
            "reliability": {
                "failedToolCalls": usage["failedToolCalls"],
                "toolFailureRate": {
                    "rate": tool_failure_rate,
                    "failedToolCalls": total_failed_tool_calls,
                    "toolCalls": total_tool_calls,
                    "observedRuns": len(paired_tool_runs),
                    "totalRuns": total,
                },
                "humanInterventions": usage["humanInterventions"],
                "contextCompactions": usage["contextCompactions"],
            },
            "safety": {
                "passedRuns": sum(1 for value in safety_observed if value),
                "passRate": None if not safety_observed else round(sum(safety_observed) / len(safety_observed), 6),
                "observedRuns": len(safety_observed),
                "totalRuns": total,
            },
        })

    return {
        "schemaVersion": COMPARISON_SCHEMA,
        "cohort": baseline,
        "datasetIds": sorted(data["datasetId"] for data in datasets),
        "harnesses": results,
        "interpretation": {
            "winnerSelected": False,
            "minimumRecommendedAttemptsPerHarness": 3,
            "note": "Interpret task-specific trade-offs; do not rank incomparable cohorts or infer a default harness.",
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate and summarize controlled OpenForge agent harness datasets"
    )
    parser.add_argument("datasets", nargs="+", help="One or more dataset JSON files from the same cohort")
    parser.add_argument("--out", help="Write the comparison JSON to this path")
    args = parser.parse_args()
    try:
        report = compare_datasets([load_dataset(path) for path in args.datasets])
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
