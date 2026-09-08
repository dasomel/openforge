#!/usr/bin/env python3
"""Bind a real command result into strict verification events without hiding failures from the behavior evaluator."""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ALLOWED_EVENT_TYPES = {"verification", "regression_verification"}


def bind(trace, event_ids, command):
    if trace.get("consistencyMode") != "strict":
        raise ValueError("dynamic verification binding requires consistencyMode=strict")
    by_id = {event.get("id"): event for event in trace.get("events", [])}
    targets = []
    for event_id in event_ids:
        event = by_id.get(event_id)
        if not event or event.get("type") not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"{event_id} must identify verification/regression_verification")
        targets.append(event)
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    status = "passed" if completed.returncode == 0 else "failed"
    for event in targets:
        event["status"] = status
        event["commandExitCode"] = completed.returncode
        evidence = event.setdefault("evidence", [])
        ref = f"runtime:command-exit-{completed.returncode}"
        if ref not in evidence:
            evidence.append(ref)
    return completed, status


def write_trace(path, trace, source):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(trace, indent=2, ensure_ascii=False) + "\n"
    if path.resolve() == Path(source).resolve():
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            stream.write(text)
            temp = Path(stream.name)
        temp.replace(path)
    else:
        path.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Bind live command evidence into a strict OpenForge agent trace")
    parser.add_argument("--trace", required=True)
    parser.add_argument("--event-id", action="append", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        print("ERROR: command is required", file=sys.stderr)
        return 2
    try:
        trace = json.loads(Path(args.trace).read_text(encoding="utf-8"))
        completed, status = bind(trace, args.event_id, command)
        write_trace(args.out, trace, args.trace)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if completed.stdout:
        print(completed.stdout, end="")
    print(f"Bound {','.join(args.event_id)} status={status} commandExitCode={completed.returncode}")
    # A verification command failure is evidence, not a binder failure. The strict
    # evaluator/regression gate owns the policy decision and will fail afterward.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
