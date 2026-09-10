#!/usr/bin/env python3
"""Audit repository agent instructions against executable engineering controls."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

SCHEMA = "openforge-agent-audit/v1"
INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", "CODING_STANDARDS.md")
SOURCE_DOCS = ("README.md", "CONTRIBUTING.md", "DESIGN.md", "ARCHITECTURE.md", "docs/architecture.md", "docs/development.md")
DETERMINISTIC_RULE_HINTS = {
    "formatting": ("format", "prettier", "gofmt", "rustfmt", "biome"),
    "lint": ("lint", "eslint", "golangci-lint", "clippy", "ruff"),
    "tests": ("test", "pytest", "go test", "cargo test", "vitest", "jest", "playwright"),
    "static-analysis": ("codeql", "staticcheck", "govulncheck", "mypy", "tsc"),
    "security-policy": ("trivy", "gitleaks", "dependency-review", "conftest", "policy"),
    "generated-files": ("generated", "generate", "codegen", "--check"),
}
PROMPT_RULE_PATTERNS = {
    "formatting": re.compile(r"\b(format|formatting|gofmt|prettier|rustfmt)\b", re.I),
    "import-order": re.compile(r"\bimport order\b", re.I),
    "braces": re.compile(r"\bbraces?\b", re.I),
    "naming": re.compile(r"\b(naming|name length|identifier length)\b", re.I),
}
VALIDATOR_COMMAND = re.compile(
    r"(?:^|[;&|()\s])(?:[^#\n]*?\b)?(?:markdownlint|shellcheck|eslint|ruff|golangci-lint|staticcheck|govulncheck|mypy|pytest|vitest|jest|playwright|trivy|gitleaks|conftest|codeql|prettier|gofmt|rustfmt|biome|cargo\s+(?:test|clippy|build)|go\s+(?:test|build)|npm\s+(?:test|run\s+(?:test|lint|build|check|verify)))\b",
    re.I,
)
SWALLOWED_FAILURE = re.compile(r"\|\|\s*(?:true|:)\s*(?:#.*)?$")

SKILL_AUDIT_SCRIPT = Path(__file__).with_name("audit-agent-skills.py")
_skill_spec = importlib.util.spec_from_file_location("openforge_agent_skills_audit", SKILL_AUDIT_SCRIPT)
assert _skill_spec and _skill_spec.loader
skill_audit = importlib.util.module_from_spec(_skill_spec)
sys.modules[_skill_spec.name] = skill_audit
_skill_spec.loader.exec_module(skill_audit)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def discover_commands(root: Path) -> dict[str, list[str]]:
    commands: dict[str, list[str]] = {"verify": [], "build": [], "test": [], "lint": []}
    makefile = root / "Makefile"
    if makefile.is_file():
        targets = set(re.findall(r"^([A-Za-z0-9_.-]+):(?:\s|$)", read_text(makefile), re.M))
        for key in commands:
            for target in (key, "check" if key == "verify" else ""):
                if target and target in targets:
                    commands[key].append(f"make {target}")
    package = root / "package.json"
    if package.is_file():
        try:
            scripts = json.loads(read_text(package)).get("scripts", {})
        except json.JSONDecodeError:
            scripts = {}
        for key in commands:
            if key in scripts:
                commands[key].append(f"npm run {key}")
    if (root / "go.mod").is_file():
        commands["test"].append("go test ./...")
        commands["build"].append("go build ./...")
    if (root / "Cargo.toml").is_file():
        commands["test"].append("cargo test")
        commands["build"].append("cargo build")
        commands["lint"].append("cargo clippy --all-targets --all-features")
    return {key: sorted(set(value)) for key, value in commands.items()}


def tooling_paths(root: Path) -> list[Path]:
    paths = [root / "Makefile", root / "package.json", root / "pyproject.toml", root / "Cargo.toml"]
    workflows = root / ".github" / "workflows"
    if workflows.is_dir():
        paths.extend(sorted(workflows.glob("*.yml")))
        paths.extend(sorted(workflows.glob("*.yaml")))
    return [path for path in paths if path.is_file()]


def tooling_corpus(root: Path) -> str:
    return "\n".join(read_text(path) for path in tooling_paths(root)).lower()


def swallowed_validator_findings(root: Path) -> list[str]:
    candidates = tooling_paths(root)
    for name in INSTRUCTION_FILES:
        path = root / name
        if path.is_file():
            candidates.append(path)
    commands = root / ".claude" / "commands"
    if commands.is_dir():
        candidates.extend(sorted(commands.glob("*.md")))
    findings: list[str] = []
    seen: set[Path] = set()
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        for lineno, line in enumerate(read_text(path).splitlines(), 1):
            if SWALLOWED_FAILURE.search(line) and VALIDATOR_COMMAND.search(line):
                rel = path.relative_to(root).as_posix()
                findings.append(f"{rel}:{lineno}: validator failure is unconditionally swallowed with '|| true' or '|| :' ")
    return findings


def audit_skills(root: Path) -> dict[str, Any]:
    skills, findings = skill_audit.audit(root)
    canonical = [skill for skill in skills if skill.root == ".agents/skills"]
    adapters = [skill for skill in skills if skill.root != ".agents/skills"]
    maturity_counts = {maturity: 0 for maturity in ("draft", "verified", "stable", "deprecated", "unspecified")}
    canonical_records = []
    evidence_backed_mature = 0
    for skill in canonical:
        maturity = skill.maturity if skill.maturity in maturity_counts else "unspecified"
        maturity_counts[maturity] += 1
        evidence_path = root / ".agents" / "skill-evals" / f"{skill.name}.json" if skill.name else None
        evidence_present = bool(evidence_path and evidence_path.is_file())
        if maturity in {"verified", "stable"} and evidence_present:
            evidence_backed_mature += 1
        canonical_records.append({"name": skill.name, "path": skill.path, "scope": skill.scope, "owner": skill.owner, "maturity": skill.maturity, "version": skill.version, "evidence_present": evidence_present})
    return {
        "canonical": canonical_records,
        "canonical_count": len(canonical_records),
        "adapter_count": len(adapters),
        "maturity_counts": maturity_counts,
        "evidence_backed_mature_count": evidence_backed_mature,
        "error_count": sum(finding.severity == "error" for finding in findings),
        "warning_count": sum(finding.severity == "warn" for finding in findings),
        "findings": [asdict(finding) for finding in findings],
    }


def audit(root: Path, repository: str | None = None) -> dict[str, Any]:
    instructions = [name for name in INSTRUCTION_FILES if (root / name).is_file()]
    source_docs = [name for name in SOURCE_DOCS if (root / name).is_file()]
    agent_text = "\n".join(read_text(root / name) for name in instructions)
    corpus = tooling_corpus(root)
    controls = {name: any(hint in corpus for hint in hints) for name, hints in DETERMINISTIC_RULE_HINTS.items()}
    prompt_hints = [name for name, pattern in PROMPT_RULE_PATTERNS.items() if pattern.search(agent_text)]
    commands = discover_commands(root)
    false_green: list[str] = swallowed_validator_findings(root)
    if instructions and not any(controls.values()):
        false_green.append("agent instructions exist but no deterministic control was detected")
    if "lint" in agent_text.lower() and not controls["lint"]:
        false_green.append("agent instructions reference linting but no lint owner was detected")
    if "test" in agent_text.lower() and not controls["tests"]:
        false_green.append("agent instructions reference tests but no test owner was detected")
    skills = audit_skills(root)
    if skills["error_count"]:
        false_green.append(f"Agent Skills audit reports {skills['error_count']} error(s); maturity/evidence claims are not fully valid")
    return {
        "schemaVersion": SCHEMA, "repository": repository or root.name, "root": str(root),
        "instructions": instructions, "source_of_truth_docs": source_docs, "canonical_commands": commands,
        "deterministic_controls": controls, "prompt_deterministic_hints": prompt_hints, "agent_skills": skills,
        "false_green_findings": false_green,
        "manual_review": {"high_risk_paths": "review-required", "bug_reproduction_automation": "review-required", "duplicated_or_obsolete_prompt_rules": "review-required", "architecture_boundary_guidance": "review-required"},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--repository")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    root = args.repo.resolve()
    if not root.is_dir():
        parser.error(f"repository path does not exist: {root}")
    result = audit(root, args.repository)
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 1 if result["false_green_findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
