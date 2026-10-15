#!/usr/bin/env python3
"""Import OpenSSF Scorecard v5 JSON (`scorecard --format=json`) into a security-readiness record.

The adapter normalizes upstream output; it never re-implements a Scorecard check. It updates an
existing `portfolio/security-readiness/<repo>.json` record (schema_version unchanged) and refuses
to write unless the result passes validate-security-readiness.py. Without --write the updated
record is printed to stdout (dry run). The input is distrusted: wrong format, missing `checks`,
an unsupported Scorecard major version, scores outside -1..10 and a repository that does not
match the record are errors, never silently clamped or skipped.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = Path(__file__).with_name("validate-security-readiness.py")
TOOL = "openssf-scorecard"
SUPPORTED_MAJOR = 5
SIGNAL_ORDER = ["scorecard", "security-policy", "actions-pinning", "sbom", "provenance", "release-signing"]
# D1: Scorecard check -> OpenForge severity, copied from the `Risk:` line of each check in
# https://github.com/ossf/scorecard/blob/v5.6.0/docs/checks.md. Cost: a new upstream check is
# reported as `info` until added here. Escape hatch: extend this table (unknown never raises).
RISK = {
    "Binary-Artifacts": "high", "Branch-Protection": "high", "CI-Tests": "low", "CII-Best-Practices": "low",
    "Code-Review": "high", "Contributors": "low", "Dangerous-Workflow": "critical",
    "Dependency-Update-Tool": "high", "Fuzzing": "medium", "License": "low", "Maintained": "high",
    "Packaging": "medium", "Pinned-Dependencies": "medium", "SAST": "medium", "SBOM": "medium",
    "Security-Policy": "medium", "Signed-Releases": "high", "Token-Permissions": "high",
    "Vulnerabilities": "high", "Webhooks": "critical",
}
# D2: checks that may fill another OpenForge signal. They fill only a signal that is absent or
# `not-run`; a directly observed signal is never overwritten. Value: (signal id, scope caveat).
GAP_FILL = {
    "Security-Policy": ("security-policy", ""),
    "Pinned-Dependencies": ("actions-pinning", " Scorecard also covers non-Actions dependencies (Dockerfiles, package managers)."),
    "Signed-Releases": ("release-signing", " Scorecard also credits provenance files."),
    "SBOM": ("sbom", " Experimental upstream check; absent from the default `scorecard` output."),
}
COMMIT = re.compile(r"[0-9a-f]{40}")
VERSION = re.compile(r"v(\d+)\.\d+\.\d+(?:[-+].*)?")


class ScorecardError(ValueError):
    pass


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_security_readiness", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def to_utc(value: object) -> str:
    if not isinstance(value, str):
        raise ScorecardError(f"date {value!r} is not a string")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ScorecardError(f"date {value!r} is not ISO 8601") from exc
    if parsed.tzinfo is None:
        raise ScorecardError(f"date {value!r} has no UTC offset")
    return parsed.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_scorecard(raw: object, repository: str) -> dict:
    """Validate raw Scorecard v5 JSON against `repository` and return the normalized facts."""
    if not isinstance(raw, dict) or not {"repo", "scorecard", "score", "checks", "date"} <= raw.keys():
        raise ScorecardError("not Scorecard JSON output (`scorecard --format=json`): need date, repo, scorecard, score, checks")
    checks, repo, tool = raw["checks"], raw["repo"], raw["scorecard"]
    if not isinstance(checks, list) or not checks:
        raise ScorecardError("`checks` must be a non-empty list")
    if not isinstance(repo, dict) or not isinstance(tool, dict):
        raise ScorecardError("`repo` and `scorecard` must be objects")
    match = VERSION.fullmatch(tool.get("version", "")) if isinstance(tool.get("version"), str) else None
    if match is None:
        raise ScorecardError(f"scorecard.version {tool.get('version')!r} is not a vMAJOR.MINOR.PATCH string")
    if int(match.group(1)) != SUPPORTED_MAJOR:
        raise ScorecardError(f"unsupported Scorecard major version {tool['version']}; only v{SUPPORTED_MAJOR}.x is mapped")
    expected = f"github.com/{repository}"
    if repo.get("name") != expected:
        raise ScorecardError(f"repo.name {repo.get('name')!r} does not match the record repository (expected {expected!r})")
    if not isinstance(repo.get("commit"), str) or not COMMIT.fullmatch(repo["commit"]):
        raise ScorecardError(f"repo.commit {repo.get('commit')!r} is not a full 40-hex commit")
    score = raw["score"]
    if not is_number(score) or not -1 <= score <= 10:
        raise ScorecardError(f"score {score!r} is outside -1..10")
    parsed_checks, seen = [], set()
    for index, check in enumerate(checks):
        name = check.get("name") if isinstance(check, dict) else None
        if not isinstance(name, str) or not name:
            raise ScorecardError(f"checks[{index}] has no name")
        if name in seen:
            raise ScorecardError(f"duplicate check {name}")
        seen.add(name)
        value, reason = check.get("score"), check.get("reason", "")
        if not is_number(value) or int(value) != value or not -1 <= value <= 10:
            raise ScorecardError(f"check {name}: score {value!r} is outside -1..10")
        if not isinstance(reason, str):
            raise ScorecardError(f"check {name}: reason must be a string")
        parsed_checks.append((name, int(value), " ".join(reason.split())))
    sc_commit = tool.get("commit")
    return {
        "observed_at": to_utc(raw["date"]), "version": tool["version"], "scorecard_commit": sc_commit if isinstance(sc_commit, str) else None,
        "commit": repo["commit"], "score": score, "checks": parsed_checks,
    }


def fmt_score(score: float) -> str:
    return f"{score:g}"


def finding(record_name: str, key: str, name: str, score: int, reason: str) -> dict:
    return {"id": f"{record_name}-{key}", "summary": f"{name} {score}/10" + (f": {reason}" if reason else ""), "severity": RISK.get(name, "info")}


def build_source(parsed: dict, repository: str, raw_path: str, check: str | None = None) -> dict:
    tool_commit = f"; scorecard commit {parsed['scorecard_commit'][:7]}" if parsed["scorecard_commit"] else ""
    ref = f"scorecard --repo=github.com/{repository} --format=json (scanned commit {parsed['commit']}{tool_commit}; raw output: {raw_path})"
    return {"tool": TOOL, "version": parsed["version"], "observed_at": parsed["observed_at"], "ref": ref + (f"; check {check}" if check else "")}


def overall_signal(parsed: dict, repository: str, raw_path: str) -> dict:
    name = repository.split("/", 1)[1]
    measured = [c for c in parsed["checks"] if c[1] >= 0]
    inconclusive = [c[0] for c in parsed["checks"] if c[1] < 0]
    score = parsed["score"]
    findings = [finding(name, f"scorecard-{c[0].lower()}", *c) for c in measured if c[1] < 10]
    detail = f"Scorecard {parsed['version']} overall {fmt_score(score)}/10 over {len(parsed['checks'])} checks ({len(measured)} conclusive)."
    if inconclusive:
        detail += f" Inconclusive (-1, never counted as pass): {', '.join(inconclusive)}."
    signal = {"id": "scorecard", "source": build_source(parsed, repository, raw_path)}
    if score == -1 or not measured:
        if score != -1:
            raise ScorecardError(f"overall score {fmt_score(score)} but every check is inconclusive")
        return {**signal, "status": "not-run", "note": detail + " No conclusive result; not-run, not pass."}
    if score == 10 and not findings:
        status = "pass"
    elif findings and score == 0:
        status = "fail"
    elif findings:
        status = "partial"
    else:
        raise ScorecardError(f"overall score {fmt_score(score)} < 10 but no conclusive check is below 10")
    note = detail + " Status follows the upstream score, not an OpenForge threshold: pass only at 10/10 with no check below 10, fail at 0, otherwise partial."
    signal.update(status=status, note=note)
    if findings:
        signal["findings"] = findings
    return signal


def gap_signal(parsed: dict, repository: str, raw_path: str, check: tuple[str, int, str], signal_id: str, caveat: str) -> dict:
    name, score, reason = check
    signal = {"id": signal_id, "source": build_source(parsed, repository, raw_path, name)}
    note = f"Derived from Scorecard {name} {score}/10 ({parsed['version']})." + caveat
    if score < 0:
        return {**signal, "status": "not-run", "note": note + f" Inconclusive: {reason or 'no reason given'}. Not-run, not pass."}
    status = "pass" if score == 10 else "fail" if score == 0 else "partial"
    signal.update(status=status, note=note)
    if score < 10:
        signal["findings"] = [finding(repository.split("/", 1)[1], f"{signal_id}-scorecard", name, score, reason)]
    return signal


def apply_scorecard(record: dict, parsed: dict, raw_path: str) -> tuple[dict, list[str]]:
    """Return (updated copy of record, notes about signals deliberately left untouched)."""
    repository, out, notes = record["repository"], copy.deepcopy(record), []
    signals = {s["id"]: s for s in out["signals"]}

    def put(signal: dict) -> None:
        signals[signal["id"]] = signal

    existing = signals.get("scorecard")
    if existing and existing["status"] != "not-run":
        # D3: refuse instead of guessing a rescan delta. Cost: a refresh needs a hand-written
        # `rescan` block; escape hatch: set the old scorecard signal to not-run in a scratch copy.
        raise ScorecardError(f"scorecard signal is already {existing['status']}; refusing to overwrite a measured signal (re-scan deltas are not computed)")
    put(overall_signal(parsed, repository, raw_path))
    by_name = {c[0]: c for c in parsed["checks"]}
    for check_name, (signal_id, caveat) in GAP_FILL.items():
        if check_name not in by_name:
            continue
        if signal_id in signals and signals[signal_id]["status"] != "not-run":
            notes.append(f"kept directly observed {signal_id} ({signals[signal_id]['status']}); Scorecard {check_name} not applied")
            continue
        put(gap_signal(parsed, repository, raw_path, by_name[check_name], signal_id, caveat))
    out["signals"] = [signals[key] for key in SIGNAL_ORDER if key in signals]
    # D4: the record observed_at is the latest observation it contains (validator requires
    # source.observed_at <= observed_at). `revision` is NOT changed: it stays the revision of the
    # direct observations; the scanned Scorecard commit is carried in each source.ref.
    out["observed_at"] = max(out["observed_at"], parsed["observed_at"])
    status_keys = load_validator().STATUS_KEYS
    counts = {key: 0 for key in status_keys.values()}
    for signal in out["signals"]:
        counts[status_keys[signal["status"]]] += 1
    out["summary"] = {"total": len(out["signals"]), **counts}
    return out, notes


def raw_ref(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.name


def run(record_path: Path, scorecard_path: Path, write: bool, today: dt.date | None = None) -> tuple[int, str]:
    validator = load_validator()
    try:
        record = validator.load_json(record_path)
        raw = validator.load_json(scorecard_path)
        if not isinstance(record, dict) or "repository" not in record:
            raise ScorecardError(f"{record_path} is not a security-readiness record")
        updated, notes = apply_scorecard(record, parse_scorecard(raw, record["repository"]), raw_ref(scorecard_path))
    except ValueError as exc:
        return 1, f"ERROR: {exc}"
    errors = validator.validate(updated, today or dt.datetime.now(dt.timezone.utc).date(), record_path)
    if errors:
        return 1, "\n".join(f"ERROR: result would be invalid: {error}" for error in errors)
    text = json.dumps(updated, ensure_ascii=False, indent=2) + "\n"
    if write:
        record_path.write_text(text, encoding="utf-8")
    return 0, "\n".join([*[f"NOTE: {n}" for n in notes], f"updated {record_path}" if write else text.rstrip("\n")])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, required=True, help="security-readiness record to update")
    parser.add_argument("--scorecard", type=Path, required=True, help="raw `scorecard --format=json` output for the same repository")
    parser.add_argument("--write", action="store_true", help="update --record in place (default: print the result)")
    args = parser.parse_args()
    code, message = run(args.record, args.scorecard, args.write)
    print(message, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
