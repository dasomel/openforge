#!/usr/bin/env python3
"""Append a structured event to an OpenForge agent trace."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "openforge-agent-trace/v1"


def load_or_create(path: Path, trace_id: str, task: str):
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schemaVersion") != SCHEMA:
            raise ValueError(f"schemaVersion must be {SCHEMA}")
        if not isinstance(data.get("events"), list):
            raise ValueError("events must be a list")
        return data
    return {
        "schemaVersion": SCHEMA,
        "traceId": trace_id,
        "task": task,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "events": [],
    }


def next_id(events):
    max_id = 0
    for event in events:
        value = str(event.get("id", ""))
        if value.startswith("e") and value[1:].isdigit():
            max_id = max(max_id, int(value[1:]))
    return f"e{max_id + 1}"


def main():
    parser = argparse.ArgumentParser(description="Record one OpenForge agent trace event")
    parser.add_argument("--trace", required=True)
    parser.add_argument("--trace-id", default="agent-task")
    parser.add_argument("--task", default="Agent-assisted engineering task")
    parser.add_argument("--type", required=True, dest="event_type")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--scope")
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--state", choices=["A", "B", "C"])
    parser.add_argument("--next")
    parser.add_argument("--approved", action="store_true")
    parser.add_argument("--provenance")
    parser.add_argument("--reviewed", action="store_true")
    args = parser.parse_args()

    path = Path(args.trace)
    try:
        trace = load_or_create(path, args.trace_id, args.task)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    event = {
        "id": next_id(trace["events"]),
        "type": args.event_type,
        "summary": args.summary,
        "recordedAt": datetime.now(timezone.utc).isoformat(),
    }
    if args.scope:
        event["scope"] = args.scope
    if args.evidence:
        event["evidence"] = args.evidence
    if args.state:
        event["state"] = args.state
    if args.next:
        event["next"] = args.next
    if args.approved:
        event["approved"] = True
    if args.provenance:
        event["provenance"] = args.provenance
    if args.reviewed:
        event["reviewed"] = True

    trace["events"].append(event)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(trace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"recorded {event['id']} {event['type']} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
