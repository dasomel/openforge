#!/usr/bin/env python3
"""Fail on mutable release/build references in explicitly protected paths."""

import argparse
import re
import sys
from pathlib import Path

ACTION_RE = re.compile(r"^\s*uses:\s*([^\s#]+)")
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
MUTABLE_PATTERNS = (
    ("container latest tag", re.compile(r"(?<![\w.-]):latest\b")),
    ("latest release download", re.compile(r"/releases/latest(?:/download)?(?:/|\b)")),
)


def iter_files(paths):
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            raise FileNotFoundError(raw)
        if path.is_file():
            yield path
            continue
        for child in sorted(path.rglob("*")):
            if child.is_file() and ".git" not in child.parts:
                yield child


def scan_file(path):
    failures = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return failures
    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for label, pattern in MUTABLE_PATTERNS:
            if pattern.search(line):
                failures.append((lineno, label, stripped))
        match = ACTION_RE.match(line)
        if match:
            ref = match.group(1)
            if ref.startswith("./"):
                continue
            if "@" not in ref:
                failures.append((lineno, "GitHub Action without immutable ref", stripped))
                continue
            action_ref = ref.rsplit("@", 1)[1]
            if not SHA40_RE.fullmatch(action_ref):
                failures.append((lineno, "GitHub Action ref is not a 40-char commit SHA", stripped))
    return failures


def main():
    parser = argparse.ArgumentParser(description="Check protected paths for mutable build/release inputs")
    parser.add_argument("paths", nargs="+", help="files or directories to protect")
    args = parser.parse_args()
    failures = []
    try:
        files = list(iter_files(args.paths))
    except FileNotFoundError as exc:
        print(f"ERROR: protected path does not exist: {exc}", file=sys.stderr)
        return 2
    for path in files:
        for lineno, label, text in scan_file(path):
            failures.append((path, lineno, label, text))
    if failures:
        for path, lineno, label, text in failures:
            print(f"{path}:{lineno}: {label}: {text}", file=sys.stderr)
        return 1
    print(f"Mutable-input guard passed for {len(files)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
