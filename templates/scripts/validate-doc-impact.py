#!/usr/bin/env python3
"""Validate a machine-readable documentation/blog impact declaration for a change."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "openforge-doc-impact/v1"
DOC_STATES = {"none", "updated", "follow-up-required"}
BLOG_STATES = {"none", "candidate", "updated"}


def validate(payload: dict, changed_paths: list[str]) -> list[str]:
    errors: list[str] = []
    if payload.get("schemaVersion") != SCHEMA:
        errors.append(f"schemaVersion must be {SCHEMA}")
    docs = payload.get("documentation")
    blog = payload.get("blog_portfolio")
    if not isinstance(docs, dict) or docs.get("impact") not in DOC_STATES:
        errors.append("documentation.impact must be none, updated, or follow-up-required")
        docs = {}
    if not isinstance(blog, dict) or blog.get("impact") not in BLOG_STATES:
        errors.append("blog_portfolio.impact must be none, candidate, or updated")
        blog = {}

    doc_impact = docs.get("impact")
    if doc_impact == "none" and not str(docs.get("rationale", "")).strip():
        errors.append("documentation.rationale is required when impact is none")
    if doc_impact == "follow-up-required" and not str(docs.get("tracking_issue", "")).strip():
        errors.append("documentation.tracking_issue is required for follow-up-required")
    if doc_impact == "updated":
        declared = docs.get("updated_paths", [])
        if not isinstance(declared, list) or not declared:
            errors.append("documentation.updated_paths is required when impact is updated")
        else:
            missing = [path for path in declared if path not in changed_paths]
            if missing:
                errors.append("declared documentation paths not present in change: " + ", ".join(missing))

    blog_impact = blog.get("impact")
    if blog_impact == "none" and not str(blog.get("rationale", "")).strip():
        errors.append("blog_portfolio.rationale is required when impact is none")
    if blog_impact == "candidate" and not str(blog.get("candidate_topic", "")).strip():
        errors.append("blog_portfolio.candidate_topic is required when impact is candidate")
    if blog_impact == "updated":
        paths = blog.get("updated_paths", [])
        if not isinstance(paths, list) or not paths:
            errors.append("blog_portfolio.updated_paths is required when impact is updated")

    evidence = payload.get("evidence", [])
    if not isinstance(evidence, list) or not evidence:
        errors.append("at least one evidence item is required")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("declaration", type=Path)
    parser.add_argument("--changed", action="append", default=[])
    parser.add_argument("--changed-file-list", type=Path)
    args = parser.parse_args()
    changed = list(args.changed)
    if args.changed_file_list:
        changed.extend(line.strip() for line in args.changed_file_list.read_text(encoding="utf-8").splitlines() if line.strip())
    payload = json.loads(args.declaration.read_text(encoding="utf-8"))
    errors = validate(payload, changed)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Documentation/blog impact declaration valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
