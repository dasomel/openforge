#!/usr/bin/env python3
"""Audit model-agnostic agent instruction debt.

This scanner is dependency-free and intentionally conservative. It reports likely
instruction debt without rewriting repository guidance.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ADAPTER_FILES = ("CLAUDE.md", "GEMINI.md")
SKILL_ROOTS = (Path(".agents/skills"), Path(".claude/skills"), Path("skills"))
MODEL_PROMPT_RE = re.compile(r"(?i)(?:prompt|instructions?)[-_]?(?:gpt|claude|gemini|llama|mistral|astra)")
UNCONDITIONAL_READ_RE = re.compile(
    r"(?i)(?:read|review|inspect)\s+(?:all|every|the repository'?s)\b.*(?:before|prior to)\b"
)
BROAD_TEST_RE = re.compile(r"(?i)(?:run|execute)\s+(?:all|the full|the entire)\s+(?:tests?|test suite)")
APPROVAL_RE = re.compile(r"(?i)(?:ask|request|require|obtain).{0,30}(?:approval|permission|confirmation)")
MODEL_NAME_RE = re.compile(r"(?i)\b(?:gpt[- ]?[0-9a-z.]+|claude(?:[- ][0-9a-z.]+)?|gemini(?:[- ][0-9a-z.]+)?|astra)\b")


@dataclass
class Finding:
    severity: str
    code: str
    path: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def line_count(text: str) -> int:
    return text.count("\n") + 1


def skill_files(root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for skill_root in SKILL_ROOTS:
        base = root / skill_root
        if not base.exists():
            continue
        for pattern in ("*/SKILL.md", "*/skill.md"):
            for path in base.glob(pattern):
                try:
                    target = path.resolve(strict=True)
                except OSError:
                    target = path.resolve(strict=False)
                if target in seen:
                    continue
                seen.add(target)
                yield path


def frontmatter_description(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    for line in text[4:end].splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip('"\'')
    return None


def audit_instruction_file(root: Path, path: Path, persistent: bool) -> list[Finding]:
    findings: list[Finding] = []
    text = read_text(path)
    rel = str(path.relative_to(root))
    lines = line_count(text)

    if persistent and lines > 160:
        findings.append(
            Finding(
                "warn",
                "INSTRUCTION-PERSISTENT-LARGE",
                rel,
                f"Persistent instruction file is {lines} lines; move task-specific detail behind progressive disclosure.",
            )
        )
    if UNCONDITIONAL_READ_RE.search(text):
        findings.append(
            Finding(
                "warn",
                "INSTRUCTION-UNCONDITIONAL-READ",
                rel,
                "Likely unconditional repository-wide reading requirement; prefer task-relevant inspection.",
            )
        )
    if BROAD_TEST_RE.search(text):
        findings.append(
            Finding(
                "info",
                "INSTRUCTION-BROAD-TEST",
                rel,
                "Broad test-suite requirement detected; verify that it is risk-scoped rather than habitual.",
            )
        )
    if APPROVAL_RE.search(text) and "production" not in text.lower() and "destructive" not in text.lower():
        findings.append(
            Finding(
                "info",
                "INSTRUCTION-APPROVAL-BOUNDARY",
                rel,
                "Approval language detected without an obvious high-risk boundary; review whether safe local work is blocked.",
            )
        )
    return findings


def audit_adapter(root: Path, path: Path) -> list[Finding]:
    findings = audit_instruction_file(root, path, persistent=True)
    text = read_text(path)
    rel = str(path.relative_to(root))

    if "AGENTS.md" not in text:
        findings.append(
            Finding(
                "warn",
                "ADAPTER-NO-CANONICAL-REFERENCE",
                rel,
                "Tool/model adapter does not reference the repository-wide AGENTS.md contract.",
            )
        )
    if line_count(text) > 120:
        findings.append(
            Finding(
                "warn",
                "ADAPTER-LARGE",
                rel,
                "Adapter is large; move generic policy or repeatable workflows to canonical guidance/skills.",
            )
        )
    return findings


def audit_skill(root: Path, path: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = read_text(path)
    rel = str(path.relative_to(root))
    description = frontmatter_description(text)

    if description and len(description) > 240:
        findings.append(
            Finding(
                "warn",
                "SKILL-TRIGGER-LONG",
                rel,
                "Skill description is long; keep activation conditions short and explicit.",
            )
        )
    if description and re.search(r"(?i)\b(?:all|any|every)\b.*\b(?:work|task|change|issue)\b", description):
        findings.append(
            Finding(
                "warn",
                "SKILL-TRIGGER-BROAD",
                rel,
                "Skill description appears overly broad; narrow the activation condition.",
            )
        )
    if line_count(text) > 250:
        findings.append(
            Finding(
                "warn",
                "SKILL-PROGRESSIVE-DISCLOSURE",
                rel,
                "Large SKILL.md; consider moving workflow detail to references/scripts loaded only when needed.",
            )
        )
    return findings


def audit(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    agents = root / "AGENTS.md"
    if not agents.exists():
        findings.append(Finding("error", "AGENT-ROOT-MISSING", "AGENTS.md", "No model-agnostic root contract found."))
    else:
        findings.extend(audit_instruction_file(root, agents, persistent=True))

    for name in ADAPTER_FILES:
        path = root / name
        if path.exists():
            findings.extend(audit_adapter(root, path))

    for path in skill_files(root):
        findings.extend(audit_skill(root, path))

    for path in root.iterdir():
        if path.is_file() and MODEL_PROMPT_RE.search(path.name):
            findings.append(
                Finding(
                    "warn",
                    "MODEL-PROMPT-FORK",
                    str(path.relative_to(root)),
                    "Model-named prompt/instruction file detected; require measured compatibility evidence and a review/removal condition.",
                )
            )

    if agents.exists():
        agents_text = read_text(agents)
        if MODEL_NAME_RE.search(agents_text) and "model-agnostic" not in agents_text.lower():
            findings.append(
                Finding(
                    "info",
                    "AGENT-MODEL-SPECIFIC",
                    "AGENTS.md",
                    "Model name appears in the persistent contract; verify that it is an example/integration note or evidence-backed override.",
                )
            )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit model-agnostic agent instruction debt")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    findings = audit(root)

    if args.json:
        print(json.dumps({"repository": str(root), "findings": [asdict(item) for item in findings]}, indent=2))
    else:
        print(f"Instruction debt audit: {root}")
        print(f"findings: {len(findings)}")
        for finding in findings:
            print(f"{finding.severity.upper():5} {finding.code:34} {finding.path}: {finding.message}")

    return 1 if any(item.severity == "error" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
