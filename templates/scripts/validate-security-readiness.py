#!/usr/bin/env python3
"""Validate security-readiness evidence records against the OpenForge contract.

Structural rules come from schemas/security-readiness-evidence-v1.schema.json (checked with a
small stdlib evaluator, so CI needs no extra packages); semantic rules the schema cannot express
live here. An expired exception is a hard error (fail-closed).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "security-readiness-evidence-v1.schema.json"
DEFAULT_DIR = ROOT / "portfolio" / "security-readiness"
SECRET_PATTERN = re.compile(
    r"(?i)(?:bearer\s+[a-z0-9._~+/-]{12,}|gh[pousr]_[a-z0-9]{20,}|"
    r"(?:password|token|secret|api[_-]?key|authorization|cookie)[\"']?\s*[:=]\s*[\"']?[^\s,\"']{8,}|"
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"
)
STATUS_KEYS = {"pass": "pass", "fail": "fail", "partial": "partial", "not-run": "not_run", "not-applicable": "not_applicable"}


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc


def parse_date(value: object) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None


def parse_datetime(value: object) -> dt.datetime | None:
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc) if isinstance(value, str) else None
    except ValueError:
        return None


def is_type(value: object, name: str) -> bool:
    if name == "object":
        return isinstance(value, dict)
    if name == "array":
        return isinstance(value, list)
    if name == "string":
        return isinstance(value, str)
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    raise ValueError(f"unsupported schema type {name}")


def check_schema(value: object, schema: dict, root: dict, path: str) -> list[str]:
    """Evaluate the JSON Schema keyword subset the contract uses."""
    if "$ref" in schema:
        node = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            node = node[part]
        return check_schema(value, node, root, path)
    if "const" in schema:
        return [] if value == schema["const"] else [f"{path}: must equal {schema['const']!r}"]
    if "enum" in schema:
        return [] if value in schema["enum"] else [f"{path}: {value!r} not in {schema['enum']}"]
    if "type" in schema and not is_type(value, schema["type"]):
        return [f"{path}: must be {schema['type']}"]
    errors: list[str] = []
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: must not be empty")
        if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match {schema['pattern']}")
    elif isinstance(value, int) and not isinstance(value, bool):
        if value < schema.get("minimum", value):
            errors.append(f"{path}: must be >= {schema['minimum']}")
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: needs at least {schema['minItems']} item(s)")
        for index, item in enumerate(value):
            if "items" in schema:
                errors.extend(check_schema(item, schema["items"], root, f"{path}[{index}]"))
    elif isinstance(value, dict):
        properties = schema.get("properties", {})
        errors.extend(f"{path}: missing required {key}" for key in schema.get("required", []) if key not in value)
        for key, child in value.items():
            if key in properties:
                errors.extend(check_schema(child, properties[key], root, f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected property {key}")
    return errors


def strings(value: object, path: str = "$"):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from strings(child, f"{path}[{index}]")


def check_semantics(doc: dict, today: dt.date, now: dt.datetime) -> list[str]:
    errors: list[str] = []
    record_at = parse_datetime(doc["observed_at"])
    if record_at is None:
        errors.append(f"observed_at {doc['observed_at']!r} is not a valid UTC datetime")
    elif record_at > now:
        errors.append(f"observed_at {doc['observed_at']} is in the future (now {now:%Y-%m-%dT%H:%M:%SZ})")
    finding_ids = {f["id"] for sig in doc["signals"] for f in sig.get("findings", [])}
    signals = doc["signals"]
    seen_signals: set[str] = set()
    seen_ids: set[str] = set()
    counts = {key: 0 for key in STATUS_KEYS.values()}
    for index, signal in enumerate(signals):
        where = f"signals[{index}] ({signal['id']})"
        if signal["id"] in seen_signals:
            errors.append(f"{where}: duplicate signal id")
        seen_signals.add(signal["id"])
        status = signal["status"]
        counts[STATUS_KEYS[status]] += 1
        findings = signal.get("findings", [])
        exceptions = signal.get("exceptions", [])
        for item in (*findings, *exceptions):
            if item["id"] in seen_ids:
                errors.append(f"{where}: duplicate finding/exception id {item['id']}")
            seen_ids.add(item["id"])
        for exc in exceptions:
            expires = parse_date(exc["expires"])
            if expires is None:
                errors.append(f"{where}: exception {exc['id']} has invalid expires {exc['expires']!r}")
            elif expires < today:
                errors.append(f"{where}: exception {exc['id']} EXPIRED on {exc['expires']} (today {today}); renew or remediate")
            review = exc.get("review_date")
            if review is not None:
                review_date = parse_date(review)
                if review_date is None:
                    errors.append(f"{where}: exception {exc['id']} has invalid review_date {review!r}")
                elif expires is not None and review_date > expires:
                    errors.append(f"{where}: exception {exc['id']} review_date is after expires")
        source_at = parse_datetime(signal["source"]["observed_at"])
        if source_at is None:
            errors.append(f"{where}: source.observed_at {signal['source']['observed_at']!r} is not a valid UTC datetime")
        elif source_at > now:
            errors.append(f"{where}: source.observed_at is in the future")
        elif record_at is not None and source_at > record_at:
            errors.append(f"{where}: source.observed_at is later than the record observed_at")
        if status == "pass" and exceptions:
            errors.append(f"{where}: status pass contradicts having exceptions")
        if status == "pass" and findings:
            errors.append(f"{where}: status pass contradicts having findings")
        if status == "partial" and not findings:
            errors.append(f"{where}: status partial needs at least one finding describing the gap")
        if status == "not-run" and exceptions:
            errors.append(f"{where}: status not-run must not carry exceptions (nothing was measured)")
        for exc in exceptions:
            errors.extend(f"{where}: exception {exc['id']} references unknown finding {ref}" for ref in exc.get("finding_ids", []) if ref not in finding_ids)
        if status == "fail" and not (findings or exceptions or signal.get("remediation")):
            errors.append(f"{where}: status fail needs a finding, an exception, or a remediation")
        if status == "not-run" and findings:
            errors.append(f"{where}: status not-run must not carry findings (nothing was measured)")
        rescan = signal.get("rescan")
        if rescan:
            previous_at = parse_datetime(rescan["previous_observed_at"])
            if previous_at is None:
                errors.append(f"{where}: rescan.previous_observed_at is not a valid UTC datetime")
            elif source_at is not None and previous_at >= source_at:
                errors.append(f"{where}: rescan.previous_observed_at must be earlier than source.observed_at")
            errors.extend(f"{where}: rescan references unknown finding {ref}" for ref in rescan.get("finding_ids", []) if ref not in finding_ids)
    summary = doc["summary"]
    if summary["total"] != len(signals):
        errors.append(f"summary.total {summary['total']} != {len(signals)} signals")
    for key, expected in counts.items():
        if summary[key] != expected:
            errors.append(f"summary.{key} {summary[key]} != derived {expected}")
    return errors


def validate(doc: object, today: dt.date, path: Path | None = None, now: dt.datetime | None = None) -> list[str]:
    schema = load_json(SCHEMA)
    errors = check_schema(doc, schema, schema, "$")
    if errors:
        return errors
    errors.extend(check_semantics(doc, today, now or dt.datetime.now(dt.timezone.utc)))
    for location, text in strings(doc):
        if SECRET_PATTERN.search(text):
            errors.append(f"{location}: secret-pattern match")
    if path is not None and path.parent.name == "security-readiness" and path.parent.parent.name == "portfolio":
        if doc["repository"].split("/", 1)[1] != path.stem:
            errors.append(f"repository {doc['repository']} does not match file name {path.name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="default: portfolio/security-readiness/*.json")
    parser.add_argument("--validate", action="store_true", help="validate (default behaviour)")
    parser.add_argument("--today", help="YYYY-MM-DD used for expiry checks (default: current UTC date)")
    parser.add_argument("--now", help="YYYY-MM-DDTHH:MM:SSZ upper bound for observed_at (default: current UTC time)")
    args = parser.parse_args()
    now = parse_datetime(args.now) if args.now else None
    if args.now and now is None:
        print(f"ERROR: invalid --now {args.now!r}", file=sys.stderr)
        return 2
    today = parse_date(args.today) if args.today else dt.datetime.now(dt.timezone.utc).date()
    if today is None:
        print(f"ERROR: invalid --today {args.today!r}", file=sys.stderr)
        return 2
    paths = args.paths or sorted(DEFAULT_DIR.glob("*.json"))
    if not paths:
        print(f"ERROR: no evidence files found in {DEFAULT_DIR}", file=sys.stderr)
        return 1
    failed = False
    for path in paths:
        try:
            errors = validate(load_json(path), today, path, now)
        except ValueError as exc:
            errors = [str(exc)]
        if errors:
            failed = True
            print("\n".join(f"ERROR: {path}: {error}" for error in errors), file=sys.stderr)
        else:
            print(f"Security readiness evidence valid: {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
