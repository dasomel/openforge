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
OUTPUT_MD_KO = ROOT / "docs" / "agent-audit-matrix-ko.md"
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


def render_table(matrix: dict[str, Any]) -> list[str]:
    lines = [
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
    return lines


def render_markdown(matrix: dict[str, Any], korean: bool = False) -> str:
    if korean:
        lines = [
            "# Agent Engineering Portfolio Audit Matrix",
            "",
            "> 정확한 Git revision에 바인딩된 repository scan으로 생성합니다. 기계적으로 관찰 가능한 control은 자동 기록하고, 판단이 필요한 항목은 명시적인 review work로 남깁니다.",
            "",
        ]
        lines.extend(render_table(matrix))
        lines += [
            "",
            "## 해석",
            "",
            "- control이 탐지됐다는 것은 repository tooling에 executable owner가 존재한다는 뜻이며 모든 경로가 올바르게 검증된다는 의미는 아닙니다.",
            "- `false-green`은 지침이 deterministic verification을 요구하지만 대응되는 executable owner를 찾지 못한 상태입니다.",
            "- high-risk boundary, 실제 경로 bug reproduction 가능성, prompt debt, architecture guidance 품질은 keyword로 추론하지 않고 maintainer review로 남깁니다.",
            "- 각 행은 정확한 Git commit에 바인딩되어 이후 동일 시점의 scan을 재현할 수 있습니다.",
            "",
        ]
        return "\n".join(lines)
    lines = [
        "# Agent Engineering Portfolio Audit Matrix",
        "",
        "> Generated from revision-bound repository scans. Machine-observable controls are recorded automatically; judgment fields remain explicit review work.",
        "",
    ]
    lines.extend(render_table(matrix))
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
    md_ko_text = render_markdown(matrix, korean=True)
    if args.check:
        stale = []
        for path, text in ((OUTPUT_JSON, json_text), (OUTPUT_MD, md_text), (OUTPUT_MD_KO, md_ko_text)):
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            print("stale agent audit outputs: " + ", ".join(stale))
            return 1
        return 0
    OUTPUT_JSON.write_text(json_text, encoding="utf-8")
    OUTPUT_MD.write_text(md_text, encoding="utf-8")
    OUTPUT_MD_KO.write_text(md_ko_text, encoding="utf-8")
    print(f"Generated agent audit matrix for {len(matrix['repositories'])} repositories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
