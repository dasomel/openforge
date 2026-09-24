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

# Keep in sync with portfolio/status.schema.json's evidence/capability verification enums.
ALLOWED_CI_VALUES = {"pass", "fail", "partial", "not-run"}
ALLOWED_EVIDENCE_VALUES = {"pass", "fail", "partial", "not-run", "not-applicable"}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected a JSON object")
    return value


def write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_capabilities(capabilities: Any) -> None:
    if not isinstance(capabilities, dict):
        raise SystemExit("payload.capabilities must be an object")
    for capability_id, capability in capabilities.items():
        if not isinstance(capability, dict):
            raise SystemExit(f"capabilities.{capability_id} must be an object")
        verification = capability.get("verification")
        if verification is None:
            continue
        if not isinstance(verification, dict):
            raise SystemExit(f"capabilities.{capability_id}.verification must be an object")
        for field, value in verification.items():
            if value not in ALLOWED_EVIDENCE_VALUES:
                raise SystemExit(
                    f"capabilities.{capability_id}.verification.{field} must be one of "
                    f"{sorted(ALLOWED_EVIDENCE_VALUES)}"
                )


def apply_status_update(
    old_status: dict[str, Any] | None, payload: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Merge one verified status payload onto a project's existing registry status.

    Returns `(status_update, report)`: `status_update` is the new `project["status"]` value,
    and `report` carries what changed for `--report` to render (evidence/capability downgrades
    and re-affirmed claims worth a reviewer's second look).
    """
    development = payload["development"]
    evidence = dict(payload["evidence"])
    capabilities: dict[str, Any] = {}
    for capability_id, capability in payload.get("capabilities", {}).items():
        capabilities[capability_id] = dict(capability) if isinstance(capability, dict) else capability
        if isinstance(capabilities[capability_id], dict) and isinstance(
            capabilities[capability_id].get("verification"), dict
        ):
            capabilities[capability_id]["verification"] = dict(capabilities[capability_id]["verification"])

    new_revision = payload.get("revision")
    old_revision = old_status.get("revision") if isinstance(old_status, dict) else None
    old_evidence = old_status.get("evidence") if isinstance(old_status, dict) else None
    old_evidence = old_evidence if isinstance(old_evidence, dict) else {}
    old_capabilities = old_status.get("capabilities") if isinstance(old_status, dict) else None
    old_capabilities = old_capabilities if isinstance(old_capabilities, dict) else {}

    # D1: evidence is revision-bound. A same-revision re-publish is a correction to that
    # revision's own claims, so the payload's values win outright with no downgrade logic
    # (guarded below by `revision_changed`). Once the revision actually differs (or a status
    # appears where none existed), anything the old status claimed that this payload is silent
    # on must be treated as unverified at the new revision -- never silently dropped (#106,
    # #108) and never left showing the old revision's value as if it still applied (#107).
    # Escape hatch: if a caller legitimately cannot re-run security/runtime checks every
    # revision, it should pass `not-run` explicitly rather than omitting the field; omission
    # is what triggers this downgrade.
    revision_changed = old_status is not None and old_revision != new_revision

    downgraded_evidence: list[str] = []
    if revision_changed:
        for dimension in ("security", "runtime"):
            if dimension in old_evidence and dimension not in evidence:
                evidence[dimension] = "not-run"
                downgraded_evidence.append(dimension)

    # D2: same treatment for capabilities -- one the payload is silent on at a new revision is
    # retained (the registry keeps remembering it exists) but every one of its verification
    # claims is escalated down to "not-run" instead of continuing to show the old revision's
    # pass/partial/fail. A `last_verified_revision` field was considered so a retained
    # capability could record when it was last actually checked, but status.schema.json's
    # capability object is `additionalProperties: false` and the change report already carries
    # this signal per-revision, so it was left out to keep this fix minimal. Escape hatch: add
    # it (+ schema and validate_registry update) if reviewers find the report insufficient.
    downgraded_capabilities: list[str] = []
    if revision_changed:
        for capability_id, capability in old_capabilities.items():
            if capability_id in capabilities or not isinstance(capability, dict):
                continue
            retained = dict(capability)
            verification = retained.get("verification")
            if isinstance(verification, dict):
                retained["verification"] = {field: "not-run" for field in verification}
            capabilities[capability_id] = retained
            downgraded_capabilities.append(capability_id)

    # D3: flag claims that look re-affirmed rather than re-verified -- the same value present
    # at the old revision and repeated verbatim in the payload for a new revision. This is not
    # proof of a stale claim (a fresh re-run can legitimately reproduce the same result), only
    # the #107 carry-forward signal: something a reviewer should double-check was actually
    # re-run at the new revision rather than copy-pasted forward.
    unchanged_claims: list[str] = []
    if revision_changed:
        payload_evidence = payload.get("evidence", {})
        for dimension in ("security", "runtime"):
            if (
                dimension in old_evidence
                and dimension in payload_evidence
                and old_evidence[dimension] == payload_evidence[dimension]
            ):
                unchanged_claims.append(f"evidence.{dimension}")
        payload_capabilities = payload.get("capabilities", {})
        for capability_id in capabilities:
            if capability_id in downgraded_capabilities:
                continue
            old_capability = old_capabilities.get(capability_id)
            new_capability = payload_capabilities.get(capability_id)
            if not isinstance(old_capability, dict) or not isinstance(new_capability, dict):
                continue
            old_verification = old_capability.get("verification")
            new_verification = new_capability.get("verification")
            if (
                isinstance(old_verification, dict)
                and isinstance(new_verification, dict)
                and old_verification == new_verification
            ):
                unchanged_claims.append(f"capabilities.{capability_id}.verification")

    status_update: dict[str, Any] = {
        "revision": new_revision,
        "updated_at": payload.get("updated_at"),
        "milestone": development.get("milestone"),
        "progress_percent": development.get("progress_percent"),
        "capabilities": capabilities,
        "evidence": evidence,
    }

    # Relationship updates are intentionally review-only. A payload may propose them, but
    # applying topology changes automatically would let a downstream repo redefine portfolio
    # architecture without OpenForge review.
    proposed_relationships = payload.get("relationships", [])
    if proposed_relationships:
        status_update["proposed_relationships"] = proposed_relationships

    report = {
        "project": payload.get("project"),
        "old_revision": old_revision,
        "new_revision": new_revision,
        "revision_changed": revision_changed,
        "old_evidence": old_evidence,
        "new_evidence": evidence,
        "downgraded_evidence": downgraded_evidence,
        "downgraded_capabilities": downgraded_capabilities,
        "unchanged_claims": unchanged_claims,
    }
    return status_update, report


def render_change_report(report: dict[str, Any]) -> str:
    """Markdown change report for `--report`: revision transition, per-dimension evidence
    changes, anything downgraded to not-run, and claims worth a reviewer's re-verification."""
    lines = [f"# Portfolio status change report: {report['project']}", ""]

    old_revision = report["old_revision"]
    new_revision = report["new_revision"]
    if old_revision is None:
        lines.append(f"- Revision: (none) -> `{new_revision}` (first published status)")
    elif report["revision_changed"]:
        lines.append(f"- Revision: `{old_revision}` -> `{new_revision}`")
    else:
        lines.append(f"- Revision: `{new_revision}` (unchanged; payload values applied as corrections)")
    lines.append("")

    lines.append("## Evidence changes")
    lines.append("")
    old_evidence = report["old_evidence"]
    new_evidence = report["new_evidence"]
    dimensions = [d for d in ("ci", "security", "runtime") if d in old_evidence or d in new_evidence]
    if dimensions:
        for dimension in dimensions:
            old_value = old_evidence.get(dimension, "(none)")
            new_value = new_evidence.get(dimension, "(none)")
            marker = (
                " -- downgraded (omitted from payload at new revision)"
                if dimension in report["downgraded_evidence"]
                else ""
            )
            lines.append(f"- {dimension}: `{old_value}` -> `{new_value}`{marker}")
    else:
        lines.append("- (no evidence recorded)")
    lines.append("")

    lines.append("## Downgraded to not-run")
    lines.append("")
    downgrades = [f"evidence.{dimension}" for dimension in report["downgraded_evidence"]]
    downgrades += [f"capabilities.{capability_id}" for capability_id in report["downgraded_capabilities"]]
    if downgrades:
        lines.extend(f"- {item}" for item in downgrades)
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Claims unchanged at a new revision (reviewer re-verification requested)")
    lines.append("")
    if report["unchanged_claims"]:
        for item in report["unchanged_claims"]:
            lines.append(
                f"- {item}: value repeated verbatim from the previous revision -- confirm this was "
                f"re-verified at `{new_revision}`, not carried forward"
            )
    else:
        lines.append("- None")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path, help="openforge-project-status/v1 JSON payload")
    parser.add_argument(
        "--allow-non-passing-ci",
        action="store_true",
        help="allow payloads whose evidence.ci is not pass (normally rejected)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="write a Markdown change report (revision transition, evidence/capability "
        "downgrades, unchanged-claim flags) to PATH",
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

    if evidence.get("ci") is not None and evidence.get("ci") not in ALLOWED_CI_VALUES:
        raise SystemExit(f"evidence.ci must be one of {sorted(ALLOWED_CI_VALUES)}")
    if not args.allow_non_passing_ci and evidence.get("ci") != "pass":
        raise SystemExit("status publication requires evidence.ci=pass by default")
    if not evidence.get("commit"):
        raise SystemExit("evidence.commit is required")
    for dimension in ("security", "runtime"):
        value = evidence.get(dimension)
        if value is not None and value not in ALLOWED_EVIDENCE_VALUES:
            raise SystemExit(f"evidence.{dimension} must be one of {sorted(ALLOWED_EVIDENCE_VALUES)}")
    validate_capabilities(payload.get("capabilities", {}))

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

    old_status = target.get("status") if isinstance(target.get("status"), dict) else None
    status_update, report = apply_status_update(old_status, payload)

    target["development_status"] = new_status
    target["status"] = status_update

    projects_doc["updated_at"] = payload.get("updated_at") or projects_doc.get("updated_at")
    write(PROJECTS_PATH, projects_doc)
    print(f"Applied portfolio status for {project_id}: {new_status} @ {payload.get('revision')}")

    if args.report:
        args.report.write_text(render_change_report(report), encoding="utf-8")
        print(f"Wrote change report to {args.report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
