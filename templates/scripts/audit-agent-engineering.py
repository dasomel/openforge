#!/usr/bin/env python3
"""Audit repository agent instructions against executable engineering controls.

The audit intentionally separates machine-observable facts from human-judgment fields.
It does not infer architecture quality or high-risk boundaries from keywords alone.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "openforge-agent-audit/v1"
INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", "CODING_STANDARDS.md")
SOURCE_DOCS = (
    "README.md",
    "CONTRIBUTING.md",
    "DESIGN.md",
    "ARCHITECTURE.md",
    "docs/architecture.md",
    "docs/development.md",
)
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


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def discover_commands(root: Path) -> dict[str, list[str]]:
    commands: dict[str, list[str]] = {"verify": [], "build": [], "test": [], "lint": []}
    makefile = root / "Makefile"
    if makefile.is_file():
        text = read_text(makefile)
        targets = set(re.findall(r"^([A-Za-z0-9_.-]+):(?:\s|$)", text, re.M))
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


def tooling_corpus(root: Path) -> str:
    candidates = [root / "Makefile", root / "package.json", root / "pyproject.toml", root / "Cargo.toml"]
    workflows = root / ".github" / "workflows"
    if workflows.is_dir():
        candidates.extend(sorted(workflows.glob("*.yml")))
        candidates.extend(sorted(workflows.glob("*.yaml")))
    return "\n".join(read_text(path) for path in candidates if path.is_file()).lower()


def audit(root: Path, repository: str | None = None) -> dict[str, Any]:
    instructions = [name for name in INSTRUCTION_FILES if (root / name).is_file()]
    source_docs = [name for name in SOURCE_DOCS if (root / name).is_file()]
    agent_text = "\n".join(read_text(root / name) for name in instructions)
    corpus = tooling_corpus(root)
    controls = {
        name: any(hint in corpus for hint in hints)
        for name, hints in DETERMINISTIC_RULE_HINTS.items()
    }
    prompt_hints = [name for name, pattern in PROMPT_RULE_PATTERNS.items() if pattern.search(agent_text)]
    commands = discover_commands(root)
    false_green: list[str] = []
    if instructions and not any(controls.values()):
        false_green.append("agent instructions exist but no deterministic control was detected")
    if "lint" in agent_text.lower() and not controls["lint"]:
        false_green.append("agent instructions reference linting but no lint owner was detected")
    if "test" in agent_text.lower() and not controls["tests"]:
        false_green.append("agent instructions reference tests but no test owner was detected")

    return {
        "schemaVersion": SCHEMA,
        "repository": repository or root.name,
        "root": str(root),
        "instructions": instructions,
        "source_of_truth_docs": source_docs,
        "canonical_commands": commands,
        "deterministic_controls": controls,
        "prompt_deterministic_hints": prompt_hints,
        "false_green_findings": false_green,
        "manual_review": {
            "high_risk_paths": "review-required",
            "bug_reproduction_automation": "review-required",
            "duplicated_or_obsolete_prompt_rules": "review-required",
            "architecture_boundary_guidance": "review-required",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
