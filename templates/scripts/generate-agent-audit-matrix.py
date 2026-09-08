#!/usr/bin/env python3
"""Generate a revision-bound portfolio agent-engineering audit matrix."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
AUDIT_SCRIPT = ROOT / "templates" / "scripts" / "audit-agent-engineering.py"
OUTPUT_JSON = ROOT / "portfolio" / "agent-audit.json"
OUTPUT_MD = ROOT / "docs" / "agent-audit-matrix.md"
SCHEMA = "openforge-agent-audit-matrix/v1"
PRIORITY_REPOSITORIES = [
    "dasomel/narwhal",
    "dasomel/narwhal-portal",
    "dasomel/beluga",
    "dasomel/beluga-manager",
    "dasomel/kubemetal",
    "dasomel/clusterdeck",
    "dasomel/ldapium",
    "dasomel/nfs-quota-agent",
    "dasomel/egovframe-launcher",
    "dasomel/kube-ready-box",
]

spec = importlib.util.spec_from_file_location("agent_audit", AUDIT_SCRIPT)
agent_audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(agent_audit)


def git_revision(path: Path) -> str:
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def parse_repo_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--repo must be owner/name=/path/to/clone")
    repository, path = value.split("=", 1)
    if repository.count("/") != 1:
        raise argparse.ArgumentTypeError(f"invalid repository: {repository}")
    return repository, Path(path).resolve()


def build(entries: list[tuple[str, Path]]) -> dict[str, Any]:
    audits = []
    for repository, path in entries:
        result = agent_audit.audit(path, repository)
        result.pop("root", None)
        result["revision"] = git_revision(path)
        audits.append(result)
    audits.sort(key=lambda item: PRIORITY_REPOSITORIES.index(item["repository"]) if item["repository"] in PRIORITY_REPOSITORIES else 999)
    return {
        "schemaVersion": SCHEMA,
        "priority_repositories": PRIORITY_REPOSITORIES,
        "repositories": audits,
    }


def validate(matrix: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if matrix.get("schemaVersion") != SCHEMA:
        errors.append(f"schemaVersion must be {SCHEMA}")
    rows = matrix.get("repositories")
    if not isinstance(rows, list):
        return errors + ["repositories must be an array"]
    names = [row.get("repository") for row in rows if isinstance(row, dict)]
    if len(names) != len(set(names)):
        errors.append("duplicate repository audit records")
    missing = [repo for repo in PRIORITY_REPOSITORIES if repo not in names]
    if missing:
        errors.append("missing priority repositories: " + ", ".join(missing))
    for row in rows:
        if not isinstance(row, dict):
            errors.append("repository audit record must be object")
            continue
        revision = row.get("revision")
        if not isinstance(revision, str) or len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision.lower()):
            errors.append(f"{row.get('repository')}: invalid revision")
        if row.get("schemaVersion") != "openforge-agent-audit/v1":
            errors.append(f"{row.get('repository')}: unsupported audit schema")
        manual = row.get("manual_review", {})
        for field in (
            "high_risk_paths",
            "bug_reproduction_automation",
            "duplicated_or_obsolete_prompt_rules",
            "architecture_boundary_guidance",
        ):
            if field not in manual:
                errors.append(f"{row.get('repository')}: missing manual review field {field}")
    return errors


def render_markdown(matrix: dict[str, Any]) -> str:
    lines = [
        "# Agent Engineering Portfolio Audit Matrix",
        "",
        "> Generated from revision-bound repository scans. Machine-observable controls are recorded automatically; judgment fields remain explicit review work.",
        "",
        "| Repository | Revision | Instructions | Verify / Build / Test / Lint | Deterministic controls | False-green | Manual review |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in matrix["repositories"]:
        commands = row.get("canonical_commands", {})
        command_text = "<br>".join(
            f"`{kind}`: {', '.join(values) if values else '—'}"
            for kind, values in commands.items()
        )
        controls = ", ".join(name for name, enabled in row.get("deterministic_controls", {}).items() if enabled) or "—"
        findings = row.get("false_green_findings", [])
        manual = row.get("manual_review", {})
        pending = sum(value == "review-required" for value in manual.values())
        lines.append(
            f"| `{row['repository']}` | `{row['revision'][:12]}` | "
            f"{', '.join(row.get('instructions', [])) or '—'} | {command_text} | {controls} | "
            f"{len(findings)} | {pending} review-required |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- A detected control means the repository exposes an executable owner in its tooling; it does not prove that every path is correctly covered.",
        "- `false-green` means instructions require deterministic verification but no corresponding executable owner was detected.",
        "- High-risk boundaries, real-path bug reproduction feasibility, prompt debt, and architecture guidance quality are not inferred from keywords and remain maintainer-reviewed fields.",
        "- Every row is bound to an exact Git commit so later reviews can reproduce what was scanned.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", type=parse_repo_arg, default=[])
    parser.add_argument("--validate", action="store_true", help="validate the checked-in matrix")
    parser.add_argument("--check", action="store_true", help="fail if generated outputs differ from checked-in files")
    args = parser.parse_args()

    if args.validate:
        matrix = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        errors = validate(matrix)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        print(f"Agent audit matrix valid: {len(matrix['repositories'])} repositories")
        return 0

    if not args.repo:
        parser.error("at least one --repo owner/name=/path is required for generation")
    matrix = build(args.repo)
    errors = validate(matrix)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    json_text = json.dumps(matrix, ensure_ascii=False, indent=2) + "\n"
    md_text = render_markdown(matrix)
    if args.check:
        stale = []
        if not OUTPUT_JSON.exists() or OUTPUT_JSON.read_text(encoding="utf-8") != json_text:
            stale.append(str(OUTPUT_JSON.relative_to(ROOT)))
        if not OUTPUT_MD.exists() or OUTPUT_MD.read_text(encoding="utf-8") != md_text:
            stale.append(str(OUTPUT_MD.relative_to(ROOT)))
        if stale:
            print("stale agent audit outputs: " + ", ".join(stale))
            return 1
        return 0
    OUTPUT_JSON.write_text(json_text, encoding="utf-8")
    OUTPUT_MD.write_text(md_text, encoding="utf-8")
    print(f"Generated agent audit matrix for {len(matrix['repositories'])} repositories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
