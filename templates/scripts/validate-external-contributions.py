#!/usr/bin/env python3
"""Validate the external-contributions registry against the OpenForge contract.

Structural rules come from schemas/external-contributions-v1.schema.json (checked with a small
stdlib evaluator, so CI needs no extra packages); cross-field rules the schema cannot express
live here. Input is distrusted: any violation is a hard error.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "external-contributions-v1.schema.json"
DEFAULT_PATH = ROOT / "portfolio" / "external-contributions.json"
PROJECTS_PATH = ROOT / "portfolio" / "projects.json"
URL_SEGMENT = {"issue": "issues", "pull_request": "pull"}


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc


def parse_datetime(value: object) -> dt.datetime | None:
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc) if isinstance(value, str) else None
    except ValueError:
        return None


def portfolio_repositories(path: Path = PROJECTS_PATH) -> set[str]:
    doc = load_json(path)
    return {p["repository"] for p in doc.get("projects", []) if isinstance(p, dict) and isinstance(p.get("repository"), str)}


def is_type(value: object, name: str) -> bool:
    checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    }
    if name not in checks:
        raise ValueError(f"unsupported schema type {name}")
    return checks[name](value)


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
        if len(value) > schema.get("maxLength", len(value)):
            errors.append(f"{path}: longer than {schema['maxLength']} characters")
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


def check_semantics(doc: dict, repositories: set[str], now: dt.datetime) -> list[str]:
    errors: list[str] = []
    record_at = parse_datetime(doc["observed_at"])
    if record_at is None:
        errors.append(f"observed_at {doc['observed_at']!r} is not a valid UTC datetime")
    elif record_at > now:
        errors.append(f"observed_at {doc['observed_at']} is in the future (now {now:%Y-%m-%dT%H:%M:%SZ})")
    seen_ids: set[str] = set()
    seen_threads: set[tuple[str, int]] = set()
    for index, entry in enumerate(doc["entries"]):
        where = f"entries[{index}] ({entry['id']})"
        if entry["id"] in seen_ids:
            errors.append(f"{where}: duplicate id")
        seen_ids.add(entry["id"])
        thread = (entry["repository"], entry["number"])
        if thread in seen_threads:
            errors.append(f"{where}: duplicate thread {entry['repository']}#{entry['number']}")
        seen_threads.add(thread)
        if entry["repository"] not in repositories:
            errors.append(f"{where}: repository {entry['repository']} is not a portfolio project repository")
        expected_url = f"https://github.com/{entry['repository']}/{URL_SEGMENT[entry['kind']]}/{entry['number']}"
        if entry["url"] != expected_url:
            errors.append(f"{where}: url {entry['url']} must equal {expected_url} for kind {entry['kind']} and number {entry['number']}")
        if entry["kind"] == "issue" and entry["state"] == "merged":
            errors.append(f"{where}: an issue cannot be merged")
        handles = entry["contributors"]
        if len({h.lower() for h in handles}) != len(handles):
            errors.append(f"{where}: duplicate contributor handle (GitHub handles are case-insensitive)")
        if handles != sorted(handles, key=str.lower):
            errors.append(f"{where}: contributors must be sorted case-insensitively")
        entry_at = parse_datetime(entry["observed_at"])
        if entry_at is None:
            errors.append(f"{where}: observed_at {entry['observed_at']!r} is not a valid UTC datetime")
        elif entry_at > now:
            errors.append(f"{where}: observed_at is in the future")
        elif record_at is not None and entry_at > record_at:
            errors.append(f"{where}: observed_at is later than the record observed_at")
    keys = [(e["repository"], e["number"]) for e in doc["entries"]]
    if keys != sorted(keys):
        errors.append("entries must be sorted by (repository, number)")
    return errors


def check_handles(doc: object) -> list[str]:
    """Explain the common privacy mistakes (emails, @-prefixed handles) instead of a bare pattern error."""
    errors: list[str] = []
    for index, entry in enumerate(doc.get("entries", []) if isinstance(doc, dict) else []):
        for handle in entry.get("contributors", []) if isinstance(entry, dict) and isinstance(entry.get("contributors"), list) else []:
            if isinstance(handle, str) and "@" in handle:
                errors.append(f"entries[{index}].contributors: {handle!r} looks like an email or @-prefixed handle; store the bare GitHub handle only")
    return errors


def validate(doc: object, repositories: set[str] | None = None, now: dt.datetime | None = None) -> list[str]:
    schema = load_json(SCHEMA)
    errors = check_handles(doc) + check_schema(doc, schema, schema, "$")
    if errors:
        return errors
    return check_semantics(doc, portfolio_repositories() if repositories is None else repositories, now or dt.datetime.now(dt.timezone.utc))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_PATH, help="default: portfolio/external-contributions.json")
    parser.add_argument("--validate", action="store_true", help="validate (default behaviour)")
    parser.add_argument("--now", help="YYYY-MM-DDTHH:MM:SSZ upper bound for observed_at (default: current UTC time)")
    args = parser.parse_args()
    now = parse_datetime(args.now) if args.now else None
    if args.now and now is None:
        print(f"ERROR: invalid --now {args.now!r}", file=sys.stderr)
        return 2
    try:
        errors = validate(load_json(args.path), None, now)
    except ValueError as exc:
        errors = [str(exc)]
    if errors:
        print("\n".join(f"ERROR: {args.path}: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"External contributions registry valid: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
