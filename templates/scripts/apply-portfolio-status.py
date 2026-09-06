#!/usr/bin/env python3
"""Apply one verified downstream project status payload to OpenForge registry data.

This script is intended to run on a status-update branch before a pull request is opened.
It never talks to GitHub directly and never merges anything. The resulting registry diff is
reviewed and validated by the normal OpenForge PR workflow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROJECTS_PATH = ROOT / "portfolio" / "projects.json"
MILESTONES_PATH = ROOT / "portfolio" / "milestones.json"


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected a JSON object")
    return value


def write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path, help="openforge-project-status/v1 JSON payload")
    parser.add_argument(
        "--allow-non-passing-ci",
        action="store_true",
        help="allow payloads whose evidence.ci is not pass (normally rejected)",
    )
    args = parser.parse_args()

    payload = load(args.payload)
    projects_doc = load(PROJECTS_PATH)
    milestones_doc = load(MILESTONES_PATH)

    if payload.get("version") != "openforge-project-status/v1":
        raise SystemExit("unsupported status payload version")

    project_id = payload.get("project")
    repository = payload.get("repository")
    development = payload.get("development")
    evidence = payload.get("evidence")
    if not isinstance(project_id, str) or not project_id:
        raise SystemExit("payload.project is required")
    if not isinstance(development, dict):
        raise SystemExit("payload.development must be an object")
    if not isinstance(evidence, dict):
        raise SystemExit("payload.evidence must be an object")

    allowed_statuses = set(milestones_doc.get("allowed_statuses", []))
    new_status = development.get("status")
    if new_status not in allowed_statuses:
        raise SystemExit(f"unsupported development status: {new_status!r}")

    if not args.allow_non_passing_ci and evidence.get("ci") != "pass":
        raise SystemExit("status publication requires evidence.ci=pass by default")
    if not evidence.get("commit"):
        raise SystemExit("evidence.commit is required")

    projects = projects_doc.get("projects", [])
    target: dict[str, Any] | None = None
    for project in projects:
        if isinstance(project, dict) and project.get("id") == project_id:
            target = project
            break
    if target is None:
        raise SystemExit(f"unknown project: {project_id}")
    if target.get("repository") != repository:
        raise SystemExit(
            f"repository mismatch: registry={target.get('repository')!r}, payload={repository!r}"
        )

    target["development_status"] = new_status
    target["status"] = {
        "revision": payload.get("revision"),
        "updated_at": payload.get("updated_at"),
        "milestone": development.get("milestone"),
        "progress_percent": development.get("progress_percent"),
        "capabilities": payload.get("capabilities", {}),
        "evidence": evidence,
    }

    # Relationship updates are intentionally review-only. A payload may propose them, but
    # applying topology changes automatically would let a downstream repo redefine portfolio
    # architecture without OpenForge review.
    proposed_relationships = payload.get("relationships", [])
    if proposed_relationships:
        target["status"]["proposed_relationships"] = proposed_relationships

    projects_doc["updated_at"] = payload.get("updated_at") or projects_doc.get("updated_at")
    write(PROJECTS_PATH, projects_doc)
    print(f"Applied portfolio status for {project_id}: {new_status} @ {payload.get('revision')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
