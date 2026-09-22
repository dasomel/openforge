#!/usr/bin/env python3
"""Validate OpenForge portfolio maintenance/lifecycle governance metadata."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTS_PATH = ROOT / "portfolio" / "projects.json"
MAINTENANCE_PATH = ROOT / "portfolio" / "maintenance.json"


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    projects_doc = load(PROJECTS_PATH)
    maintenance_doc = load(MAINTENANCE_PATH)
    errors: list[str] = []

    if maintenance_doc.get("version") != "openforge-maintenance/v1":
        errors.append("maintenance.version must be openforge-maintenance/v1")

    project_ids = {p["id"] for p in projects_doc.get("projects", []) if isinstance(p, dict) and p.get("id")}
    allowed = maintenance_doc.get("allowed", {})
    required_enums = ("strategic_role", "blast_radius", "exit_path_status", "maintenance_status")
    for key in required_enums:
        values = allowed.get(key)
        if not isinstance(values, list) or not values:
            errors.append(f"maintenance.allowed.{key} must be a non-empty array")

    entries = maintenance_doc.get("projects")
    if not isinstance(entries, list):
        errors.append("maintenance.projects must be an array")
        entries = []

    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"maintenance.projects[{index}] must be an object")
            continue
        project = entry.get("project")
        if project not in project_ids:
            errors.append(f"maintenance.projects[{index}] references unknown project {project!r}")
            continue
        if project in seen:
            errors.append(f"duplicate maintenance project: {project}")
        seen.add(project)

        owner = entry.get("maintenance_owner")
        status = entry.get("maintenance_status")
        if status != "unowned" and (not isinstance(owner, str) or not owner.strip()):
            errors.append(f"{project}: maintenance_owner is required unless maintenance_status=unowned")
        for key in required_enums:
            if entry.get(key) not in set(allowed.get(key, [])):
                errors.append(f"{project}: unsupported {key} {entry.get(key)!r}")
        cadence = entry.get("review_cadence")
        if cadence not in {"monthly", "quarterly", "semiannual", "annual"}:
            errors.append(f"{project}: unsupported review_cadence {cadence!r}")

    missing = sorted(project_ids - seen)
    if missing:
        errors.append("maintenance registry missing projects: " + ", ".join(missing))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    owned = sum(1 for entry in entries if entry.get("maintenance_status") == "owned")
    high = sum(1 for entry in entries if entry.get("blast_radius") == "high")
    exit_review = sum(1 for entry in entries if entry.get("exit_path_status") == "review-required")
    print(f"maintenance registry valid: projects={len(entries)} owned={owned} high-blast-radius={high} exit-review-required={exit_review}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
