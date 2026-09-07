#!/usr/bin/env python3
"""Generate and validate OpenForge OSS portfolio views from canonical JSON data.

The portfolio registry is intentionally data-first. Markdown dashboards, Mermaid graphs,
and impact reports are generated artifacts and must not become independent sources of truth.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROJECTS_PATH = ROOT / "portfolio" / "projects.json"
RELATIONSHIPS_PATH = ROOT / "portfolio" / "relationships.json"
MILESTONES_PATH = ROOT / "portfolio" / "milestones.json"
MAINTENANCE_PATH = ROOT / "portfolio" / "maintenance.json"
STATUS_SCHEMA_PATH = ROOT / "portfolio" / "status.schema.json"
DASHBOARD_PATH = ROOT / "docs" / "portfolio-dashboard.md"
ARCHITECTURE_PATH = ROOT / "docs" / "portfolio-architecture.md"
IMPACT_PATH = ROOT / "docs" / "portfolio-impact.md"
DASHBOARD_JSON_PATH = ROOT / "portfolio" / "dashboard.json"

ALLOWED_IMPACT = {"high", "medium", "low"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    return value


def project_map(projects_doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    projects = projects_doc.get("projects")
    if not isinstance(projects, list) or not projects:
        raise ValueError("portfolio/projects.json: projects must be a non-empty array")
    result: dict[str, dict[str, Any]] = {}
    repositories: set[str] = set()
    for item in projects:
        if not isinstance(item, dict):
            raise ValueError("portfolio/projects.json: every project must be an object")
        project_id = item.get("id")
        repository = item.get("repository")
        if not isinstance(project_id, str) or not project_id:
            raise ValueError("portfolio/projects.json: every project requires a non-empty id")
        if project_id in result:
            raise ValueError(f"duplicate project id: {project_id}")
        if not isinstance(repository, str) or repository.count("/") != 1:
            raise ValueError(f"{project_id}: invalid repository: {repository!r}")
        if repository in repositories:
            raise ValueError(f"duplicate repository: {repository}")
        repositories.add(repository)
        result[project_id] = item
    return result


def validate_registry(
    projects_doc: dict[str, Any], relationships_doc: dict[str, Any], milestones_doc: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    try:
        projects = project_map(projects_doc)
    except ValueError as exc:
        return [str(exc)]

    allowed_statuses = set(milestones_doc.get("allowed_statuses", []))
    if not allowed_statuses:
        errors.append("portfolio/milestones.json: allowed_statuses must be non-empty")

    for project_id, project in projects.items():
        status = project.get("development_status")
        if status not in allowed_statuses:
            errors.append(f"{project_id}: unsupported development_status {status!r}")
        adoption = project.get("adoption_percent")
        if adoption is not None and not isinstance(adoption, (int, float)):
            errors.append(f"{project_id}: adoption_percent must be number or null")
        elif isinstance(adoption, (int, float)) and not 0 <= adoption <= 100:
            errors.append(f"{project_id}: adoption_percent out of range: {adoption}")

    allowed_types = set(relationships_doc.get("relationship_types", []))
    relationships = relationships_doc.get("relationships", [])
    if not isinstance(relationships, list):
        errors.append("portfolio/relationships.json: relationships must be an array")
        relationships = []

    for index, relation in enumerate(relationships):
        if not isinstance(relation, dict):
            errors.append(f"relationship[{index}] must be an object")
            continue
        source = relation.get("source")
        target = relation.get("target")
        relation_type = relation.get("type")
        impact = relation.get("impact")
        if source not in projects:
            errors.append(f"relationship[{index}]: unknown source {source!r}")
        if target not in projects:
            errors.append(f"relationship[{index}]: unknown target {target!r}")
        if relation_type not in allowed_types:
            errors.append(f"relationship[{index}]: unsupported type {relation_type!r}")
        if impact not in ALLOWED_IMPACT:
            errors.append(f"relationship[{index}]: unsupported impact {impact!r}")

    for standard in relationships_doc.get("standards", []):
        if not isinstance(standard, dict):
            errors.append("standards entries must be objects")
            continue
        source = standard.get("source")
        if source not in projects:
            errors.append(f"standard {standard.get('id')}: unknown source {source!r}")
        for affected in standard.get("affected_projects", []):
            project_id = affected.get("project") if isinstance(affected, dict) else None
            impact = affected.get("impact") if isinstance(affected, dict) else None
            if project_id not in projects:
                errors.append(f"standard {standard.get('id')}: unknown affected project {project_id!r}")
            if impact not in ALLOWED_IMPACT:
                errors.append(f"standard {standard.get('id')}: invalid impact {impact!r}")

    for milestone in milestones_doc.get("milestones", []):
        if not isinstance(milestone, dict):
            errors.append("milestone entries must be objects")
            continue
        status = milestone.get("status")
        if status not in allowed_statuses:
            errors.append(f"milestone {milestone.get('id')}: unsupported status {status!r}")
        for project_id in milestone.get("projects", {}):
            if project_id not in projects:
                errors.append(f"milestone {milestone.get('id')}: unknown project {project_id!r}")

    return errors


def fmt_percent(value: Any) -> str:
    return "—" if value is None else f"{float(value):.1f}%"


def repo_link(project: dict[str, Any]) -> str:
    return f"[{project['name']}](https://github.com/{project['repository']})"


EVIDENCE_FIELDS = ("ci", "security", "runtime")
VERIFICATION_FIELDS = ("unit", "integration", "runtime", "security")


def fmt_revision(project: dict[str, Any]) -> str:
    """Short SHA for the last verified status update, linked to the commit when known."""
    status = project.get("status")
    revision = status.get("revision") if isinstance(status, dict) else None
    if not revision:
        return "—"
    evidence = status.get("evidence") if isinstance(status, dict) else None
    commit = evidence.get("commit") if isinstance(evidence, dict) else None
    if commit:
        return f"[`{revision}`](https://github.com/{project['repository']}/commit/{commit})"
    return f"`{revision}`"


def fmt_evidence(project: dict[str, Any]) -> str:
    """Compact ci/security/runtime evidence summary; only fields actually present are shown."""
    status = project.get("status")
    evidence = status.get("evidence") if isinstance(status, dict) else None
    if not isinstance(evidence, dict):
        return "—"
    parts = [f"{field}: {evidence[field]}" for field in EVIDENCE_FIELDS if evidence.get(field)]
    return " · ".join(parts) if parts else "—"


def capability_verification_rows(project: dict[str, Any]) -> list[tuple[str, str, str]]:
    """(project name, capability id, compact verification summary) rows for capabilities with recorded verification."""
    status = project.get("status")
    capabilities = status.get("capabilities") if isinstance(status, dict) else None
    if not isinstance(capabilities, dict):
        return []
    rows: list[tuple[str, str, str]] = []
    for capability_id, capability in capabilities.items():
        verification = capability.get("verification") if isinstance(capability, dict) else None
        if not isinstance(verification, dict):
            continue
        parts = [f"{field} {verification[field]}" for field in VERIFICATION_FIELDS if verification.get(field)]
        if parts:
            rows.append((project["name"], capability_id, " · ".join(parts)))
    return rows


def render_dashboard(projects_doc: dict[str, Any], milestones_doc: dict[str, Any]) -> str:
    projects = list(project_map(projects_doc).values())
    portfolio = projects_doc.get("portfolio", {})
    status_counts = Counter(project.get("development_status", "unknown") for project in projects)
    measured = [p for p in projects if p.get("adoption_percent") is not None]
    measured_sorted = sorted(measured, key=lambda p: (-float(p["adoption_percent"]), p["name"].lower()))

    lines = [
        "# OpenForge OSS Portfolio Dashboard",
        "",
        "> Generated from `portfolio/*.json`. Do not hand-edit measured or relationship state in this document.",
        "",
        "## Portfolio pulse",
        "",
        f"- Projects: **{len(projects)}**",
        f"- Engineering metrics: **{portfolio.get('standard_metrics', '—')}**",
        f"- OpenForge standard maturity: **{fmt_percent(portfolio.get('standard_maturity_percent'))}**",
        f"- Portfolio adoption: **{fmt_percent(portfolio.get('adoption_percent'))}**",
        f"- Adoption target: **{fmt_percent(portfolio.get('adoption_target_percent'))}**",
        f"- ADRs: **{portfolio.get('adr_count', '—')}**",
        f"- Active projects: **{status_counts.get('active', 0)}**",
        "",
        "## Development board",
        "",
        "| Project | Role | Development | OpenForge adoption | Domains | Verified revision | Evidence (ci · security · runtime) |",
        "|---|---|---|---:|---|---|---|",
    ]
    for project in projects:
        lines.append(
            f"| {repo_link(project)} | `{project['role']}` | **{project['development_status']}** | "
            f"{fmt_percent(project.get('adoption_percent'))} | {', '.join(project.get('domains', []))} | "
            f"{fmt_revision(project)} | {fmt_evidence(project)} |"
        )

    lines += ["", "## Capability verification", ""]
    verification_rows = [row for project in projects for row in capability_verification_rows(project)]
    if verification_rows:
        lines += [
            "| Project | Capability | Verification (unit · integration · runtime · security) |",
            "|---|---|---|",
        ]
        for project_name, capability_id, summary in verification_rows:
            lines.append(f"| {project_name} | `{capability_id}` | {summary} |")
    else:
        lines.append("No project-level capability verification records are currently registered.")

    lines += ["", "## Adoption snapshot", ""]
    if measured_sorted:
        lines += [
            "| Project | Adoption |",
            "|---|---:|",
        ]
        for project in measured_sorted:
            lines.append(f"| {project['name']} | {fmt_percent(project['adoption_percent'])} |")
    else:
        lines.append("No project-level adoption measurements are currently registered.")

    lines += ["", "## Current milestones", "", "| Milestone | Status | Progress |", "|---|---|---|"]
    for milestone in milestones_doc.get("milestones", []):
        if "current" in milestone and "target" in milestone:
            progress = f"{milestone['current']}{milestone.get('unit', '')} / {milestone['target']}{milestone.get('unit', '')}"
        else:
            states = milestone.get("projects", {})
            progress = ", ".join(f"{key}: {value}" for key, value in states.items()) or "—"
        lines.append(f"| {milestone['name']} | **{milestone['status']}** | {progress} |")

    lines += [
        "",
        "## Status publication workflow",
        "",
        "```text",
        "Project change merged",
        "        ↓",
        "project CI + required verification",
        "        ↓",
        "openforge-project-status/v1 payload",
        "        ↓",
        "PR to OpenForge portfolio registry",
        "        ↓",
        "portfolio validation + impact review",
        "        ↓",
        "merge = official portfolio state change",
        "        ↓",
        "dashboard / graph / infographic regeneration",
        "```",
        "",
        "See [Portfolio Governance](portfolio-governance.md), [Architecture Graph](portfolio-architecture.md), and [Impact Graph](portfolio-impact.md).",
        "",
    ]
    return "\n".join(lines)


def render_architecture(projects_doc: dict[str, Any], relationships_doc: dict[str, Any]) -> str:
    projects = project_map(projects_doc)
    lines = [
        "# OpenForge OSS Portfolio Architecture",
        "",
        "> Generated from `portfolio/projects.json` and `portfolio/relationships.json`.",
        "",
        "## Ecosystem graph",
        "",
        "```mermaid",
        "flowchart TB",
    ]

    groups = {
        "Governance": ["openforge"],
        "Platform": ["narwhal", "narwhal-portal", "clusterdeck"],
        "AIData": ["kubemetal", "beluga", "beluga-manager"],
        "Foundation": ["kube-ready-box", "nfs-quota-agent", "ldapium"],
        "DeveloperCommunity": ["egovframe-launcher", "cka-lab", "dasomel-github-io", "kairos"],
    }
    labels = {
        "Governance": "Standards & Governance",
        "Platform": "Platform Engineering",
        "AIData": "AI / Data Platforms",
        "Foundation": "Runtime / Shared Services",
        "DeveloperCommunity": "Developer / Community",
    }
    for group, ids in groups.items():
        lines.append(f"  subgraph {group}[\"{labels[group]}\"]")
        for project_id in ids:
            project = projects[project_id]
            label = project["name"].replace('"', "'")
            lines.append(f"    {project_id.replace('-', '_')}[\"{label}\\n{project['role']}\"]")
        lines.append("  end")

    important_types = {"standardizes", "provides", "consumes", "control-surface", "shared-contract", "reference-implementation"}
    seen: set[tuple[str, str, str]] = set()
    for relation in relationships_doc.get("relationships", []):
        if relation.get("type") not in important_types:
            continue
        key = (relation["source"], relation["target"], relation["type"])
        if key in seen:
            continue
        seen.add(key)
        source = relation["source"].replace("-", "_")
        target = relation["target"].replace("-", "_")
        relation_type = relation["type"]
        lines.append(f"  {source} -->|{relation_type}| {target}")

    lines += [
        "```",
        "",
        "## Relationship semantics",
        "",
        "| Type | Meaning |",
        "|---|---|",
        "| `standardizes` | OpenForge rule/contract is expected to influence the target |",
        "| `reference-implementation` | project experience feeds a reusable OpenForge rule |",
        "| `provides` | source exposes a capability consumed by target |",
        "| `consumes` | source depends on or integrates a target capability |",
        "| `control-surface` | source is an operational/user control surface for target |",
        "| `shared-contract` | projects share a portable contract without hard runtime dependency |",
        "| `security-impact` | changes may alter trust or authorization boundaries |",
        "",
        "Relationship edges express engineering influence and integration intent, not necessarily build-time package dependencies.",
        "",
    ]
    return "\n".join(lines)


def render_impact(projects_doc: dict[str, Any], relationships_doc: dict[str, Any]) -> str:
    projects = project_map(projects_doc)
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
    outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
    weights = {"high": 3, "medium": 2, "low": 1}
    scores: dict[str, int] = defaultdict(int)

    for relation in relationships_doc.get("relationships", []):
        incoming[relation["target"]].append(relation)
        outgoing[relation["source"]].append(relation)
        scores[relation["source"]] += weights[relation["impact"]]
        scores[relation["target"]] += weights[relation["impact"]]

    ranked = sorted(projects, key=lambda project_id: (-scores[project_id], project_id))
    lines = [
        "# OpenForge OSS Dependency & Impact Intelligence",
        "",
        "> Generated impact view. Scores are graph-weighted coordination indicators, not product quality scores.",
        "",
        "## Cross-project influence ranking",
        "",
        "| Project | Impact score | Incoming edges | Outgoing edges |",
        "|---|---:|---:|---:|",
    ]
    for project_id in ranked:
        project = projects[project_id]
        lines.append(
            f"| {project['name']} | {scores[project_id]} | {len(incoming[project_id])} | {len(outgoing[project_id])} |"
        )

    lines += ["", "## Standards blast radius", ""]
    for standard in relationships_doc.get("standards", []):
        lines += [f"### `{standard['id']}`", "", "```mermaid", "flowchart LR", f"  standard[\"{standard['id']}\"]"]
        for affected in standard.get("affected_projects", []):
            project_id = affected["project"]
            node = project_id.replace("-", "_")
            label = projects[project_id]["name"]
            lines.append(f"  {node}[\"{label}\\n{affected['impact'].upper()}\"]")
            lines.append(f"  standard -->|{affected['impact']}| {node}")
        lines += ["```", ""]

    lines += [
        "## Change-impact rule",
        "",
        "A change to a standard or provider should trigger review of directly related `high` impact projects first, then transitive or `medium` relationships. `low` relationships are advisory unless the changed scope explicitly touches them.",
        "",
        "OpenForge does not mark downstream implementation complete automatically. The affected repository owns implementation and verification; completion is published back through a status PR.",
        "",
    ]
    return "\n".join(lines)


def render_dashboard_json(projects_doc: dict[str, Any], relationships_doc: dict[str, Any], milestones_doc: dict[str, Any], maintenance_doc: dict[str, Any]) -> str:
    projects = project_map(projects_doc)
    weights = {"high": 3, "medium": 2, "low": 1}
    impact_scores = {project_id: 0 for project_id in projects}
    for relation in relationships_doc.get("relationships", []):
        weight = weights[relation["impact"]]
        impact_scores[relation["source"]] += weight
        impact_scores[relation["target"]] += weight
    maintenance_entries = {
        item["project"]: item
        for item in maintenance_doc.get("projects", [])
        if isinstance(item, dict) and item.get("project") in projects
    }
    maintenance_summary = {
        "owned_projects": sum(1 for item in maintenance_entries.values() if item.get("maintenance_status") == "owned"),
        "unowned_projects": sum(1 for item in maintenance_entries.values() if item.get("maintenance_status") == "unowned"),
        "high_blast_radius_projects": sum(1 for item in maintenance_entries.values() if item.get("blast_radius") == "high"),
        "exit_path_review_required": sum(1 for item in maintenance_entries.values() if item.get("exit_path_status") == "review-required"),
        "review_cadence_default": maintenance_doc.get("review_cadence_default"),
    }
    output = {
        "version": "openforge-dashboard/v1",
        "generated_from": ["portfolio/projects.json", "portfolio/relationships.json", "portfolio/milestones.json", "portfolio/maintenance.json"],
        "updated_at": max(filter(None, [projects_doc.get("updated_at"), maintenance_doc.get("updated_at")])),
        "portfolio": projects_doc.get("portfolio", {}),
        "maintenance": {
            "summary": maintenance_summary,
            "projects": maintenance_doc.get("projects", []),
        },
        "projects": [
            dict(project, impact_score=impact_scores[project_id], maintenance=maintenance_entries.get(project_id))
            for project_id, project in projects.items()
        ],
        "relationships": relationships_doc.get("relationships", []),
        "standards": relationships_doc.get("standards", []),
        "milestones": milestones_doc.get("milestones", []),
    }
    return json.dumps(output, ensure_ascii=False, indent=2) + "\n"


def validate_status_payload(path: Path, projects_doc: dict[str, Any], milestones_doc: dict[str, Any]) -> list[str]:
    payload = load_json(path)
    errors: list[str] = []
    projects = project_map(projects_doc)
    allowed_statuses = set(milestones_doc.get("allowed_statuses", []))
    required = {"version", "project", "repository", "revision", "updated_at", "development", "evidence"}
    missing = sorted(required - payload.keys())
    if missing:
        errors.append(f"status payload missing required fields: {', '.join(missing)}")
    if payload.get("version") != "openforge-project-status/v1":
        errors.append("status payload version must be openforge-project-status/v1")
    project_id = payload.get("project")
    if project_id not in projects:
        errors.append(f"status payload references unknown project {project_id!r}")
    elif payload.get("repository") != projects[project_id]["repository"]:
        errors.append(
            f"status payload repository mismatch for {project_id}: expected {projects[project_id]['repository']!r}"
        )
    development = payload.get("development")
    if not isinstance(development, dict):
        errors.append("development must be an object")
    elif development.get("status") not in allowed_statuses:
        errors.append(f"unsupported development status: {development.get('status')!r}")
    evidence = payload.get("evidence")
    if not isinstance(evidence, dict) or not evidence.get("commit"):
        errors.append("evidence.commit is required")
    return errors


def generated_files(projects_doc: dict[str, Any], relationships_doc: dict[str, Any], milestones_doc: dict[str, Any], maintenance_doc: dict[str, Any]) -> dict[Path, str]:
    return {
        DASHBOARD_PATH: render_dashboard(projects_doc, milestones_doc),
        ARCHITECTURE_PATH: render_architecture(projects_doc, relationships_doc),
        IMPACT_PATH: render_impact(projects_doc, relationships_doc),
        DASHBOARD_JSON_PATH: render_dashboard_json(projects_doc, relationships_doc, milestones_doc, maintenance_doc),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated outputs are stale")
    parser.add_argument("--validate-only", action="store_true", help="validate registry without writing outputs")
    parser.add_argument("--validate-status", type=Path, help="validate one project status publication payload")
    args = parser.parse_args()

    projects_doc = load_json(PROJECTS_PATH)
    relationships_doc = load_json(RELATIONSHIPS_PATH)
    milestones_doc = load_json(MILESTONES_PATH)
    maintenance_doc = load_json(MAINTENANCE_PATH)

    errors = validate_registry(projects_doc, relationships_doc, milestones_doc)
    if args.validate_status:
        errors.extend(validate_status_payload(args.validate_status, projects_doc, milestones_doc))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.validate_only or args.validate_status:
        print("Portfolio registry validation: PASS")
        return 0

    outputs = generated_files(projects_doc, relationships_doc, milestones_doc, maintenance_doc)
    stale: list[Path] = []
    for path, content in outputs.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"generated {path.relative_to(ROOT)}")

    if stale:
        for path in stale:
            print(f"STALE: {path.relative_to(ROOT)}", file=sys.stderr)
        print("Run: python3 templates/scripts/generate-portfolio.py", file=sys.stderr)
        return 1
    if args.check:
        print("Portfolio generated outputs: up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
