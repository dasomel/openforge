#!/usr/bin/env python3
"""Audit repository agent instruction and Agent Skills hygiene.

This scanner is intentionally dependency-free. It validates the subset of SKILL.md
frontmatter OpenForge relies on and reports migration warnings without rewriting files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

SKILL_ROOTS = (Path(".agents/skills"), Path(".claude/skills"), Path("skills"))
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ABSOLUTE_PATH_RE = re.compile(r"(?:/Users/[^/\s]+|/home/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+)")
GENERIC_PROJECT_NAMES = {
    "build", "check", "debug", "deploy", "fix", "install", "release", "test", "upgrade", "validate", "verification"
}
VALID_SCOPES = {"core", "domain", "project"}
VALID_MATURITY = {"draft", "verified", "stable", "deprecated"}


@dataclass
class Finding:
    severity: str
    code: str
    path: str
    message: str


@dataclass
class Skill:
    path: str
    root: str
    directory: str
    name: Optional[str]
    description: Optional[str]
    scope: Optional[str]
    owner: Optional[str]
    maturity: Optional[str]
    version: Optional[str]
    lines: int
    body_hash: str


def parse_frontmatter(text: str) -> tuple[Dict[str, str], Dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    top: Dict[str, str] = {}
    metadata: Dict[str, str] = {}
    in_metadata = False
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line == "metadata:":
            in_metadata = True
            continue
        if in_metadata and line.startswith(("  ", "\t")) and ":" in line:
            key, value = line.strip().split(":", 1)
            metadata[key.strip()] = value.strip().strip('"\'')
            continue
        in_metadata = False
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            top[key.strip()] = value.strip().strip('"\'')
    return top, metadata, body


def skill_files(root: Path) -> List[tuple[Path, Path]]:
    found: List[tuple[Path, Path]] = []
    for skill_root in SKILL_ROOTS:
        absolute = root / skill_root
        if not absolute.exists():
            continue
        for file in absolute.glob("*/SKILL.md"):
            found.append((skill_root, file))
        for file in absolute.glob("*/skill.md"):
            found.append((skill_root, file))
    return sorted(set(found), key=lambda item: str(item[1]))


def audit(root: Path) -> tuple[List[Skill], List[Finding]]:
    findings: List[Finding] = []
    skills: List[Skill] = []

    agents = root / "AGENTS.md"
    claude = root / "CLAUDE.md"

    if not agents.exists():
        findings.append(Finding("error", "AGENT-ROOT-MISSING", "AGENTS.md", "No agent-neutral root contract found."))

    if claude.exists():
        text = claude.read_text(encoding="utf-8", errors="replace")
        lines = text.count("\n") + 1
        if "AGENTS.md" not in text:
            findings.append(Finding("warn", "CLAUDE-NO-AGENTS", "CLAUDE.md", "CLAUDE.md does not import/reference AGENTS.md."))
        if lines > 200:
            findings.append(Finding("warn", "CLAUDE-LARGE", "CLAUDE.md", f"CLAUDE.md is {lines} lines; classify sections and move workflows/docs out of the adapter."))
        match = ABSOLUTE_PATH_RE.search(text)
        if match:
            findings.append(Finding("error", "CLAUDE-PERSONAL-PATH", "CLAUDE.md", f"Personal absolute path detected: {match.group(0)}"))
        if "~/.claude/CLAUDE.md" in text:
            findings.append(Finding("warn", "CLAUDE-GLOBAL-DEPENDENCY", "CLAUDE.md", "Repository behavior references a maintainer-global Claude configuration; keep it optional."))

    seen_names: Dict[str, str] = {}
    seen_desc: Dict[str, str] = {}
    seen_body: Dict[str, str] = {}

    for skill_root, file in skill_files(root):
        text = file.read_text(encoding="utf-8", errors="replace")
        top, metadata, body = parse_frontmatter(text)
        rel = str(file.relative_to(root))
        directory = file.parent.name
        name = top.get("name")
        description = top.get("description")
        scope = metadata.get("openforge-scope")
        owner = metadata.get("openforge-owner")
        maturity = metadata.get("openforge-maturity")
        version = metadata.get("openforge-version")
        lines = text.count("\n") + 1
        body_hash = hashlib.sha256(body.strip().encode()).hexdigest()

        skills.append(Skill(rel, str(skill_root), directory, name, description, scope, owner, maturity, version, lines, body_hash[:12]))

        if file.name != "SKILL.md":
            findings.append(Finding("warn", "SKILL-CASE", rel, "Use canonical uppercase SKILL.md filename."))
        if not top:
            findings.append(Finding("error", "SKILL-FRONTMATTER", rel, "Missing or malformed YAML frontmatter."))
            continue
        if not name:
            findings.append(Finding("error", "SKILL-NAME", rel, "Missing required name."))
        elif not NAME_RE.match(name) or len(name) > 64:
            findings.append(Finding("error", "SKILL-NAME-FORMAT", rel, f"Invalid Agent Skills name: {name}"))
        elif name != directory:
            findings.append(Finding("error", "SKILL-DIR-MISMATCH", rel, f"name '{name}' must match directory '{directory}'."))
        if not description:
            findings.append(Finding("error", "SKILL-DESCRIPTION", rel, "Missing required description."))
        elif len(description) > 1024:
            findings.append(Finding("error", "SKILL-DESCRIPTION-LENGTH", rel, "Description exceeds 1024 characters."))
        if lines > 500:
            findings.append(Finding("error", "SKILL-LENGTH", rel, f"SKILL.md is {lines} lines; Agent Skills recommends keeping it under 500."))
        elif lines > 250:
            findings.append(Finding("warn", "SKILL-LENGTH-TARGET", rel, f"SKILL.md is {lines} lines; move detail to references/scripts when practical."))
        if ABSOLUTE_PATH_RE.search(text):
            findings.append(Finding("error", "SKILL-PERSONAL-PATH", rel, "Personal absolute path found in a portable workflow."))

        if scope and scope not in VALID_SCOPES:
            findings.append(Finding("error", "SKILL-SCOPE", rel, f"Unknown openforge-scope '{scope}'."))
        if maturity and maturity not in VALID_MATURITY:
            findings.append(Finding("error", "SKILL-MATURITY", rel, f"Unknown openforge-maturity '{maturity}'."))
        if scope == "project":
            if not owner:
                findings.append(Finding("warn", "SKILL-OWNER", rel, "Project skill should declare openforge-owner."))
            if name in GENERIC_PROJECT_NAMES:
                findings.append(Finding("warn", "SKILL-GENERIC-NAME", rel, f"Project skill name '{name}' can collide globally; prefer <project>-<task>."))
        if not scope:
            findings.append(Finding("info", "SKILL-SCOPE-MISSING", rel, "Add OpenForge scope/owner/maturity/version metadata during migration."))

        if name:
            if name in seen_names:
                findings.append(Finding("error", "SKILL-DUP-NAME", rel, f"Duplicate skill name; first seen at {seen_names[name]}."))
            else:
                seen_names[name] = rel
        if description:
            normalized = " ".join(description.lower().split())
            if normalized in seen_desc:
                findings.append(Finding("warn", "SKILL-DUP-DESCRIPTION", rel, f"Same normalized description as {seen_desc[normalized]}."))
            else:
                seen_desc[normalized] = rel
        if body.strip():
            if body_hash in seen_body:
                findings.append(Finding("warn", "SKILL-DUP-BODY", rel, f"Same normalized body as {seen_body[body_hash]}."))
            else:
                seen_body[body_hash] = rel

    return skills, findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    skills, findings = audit(root)

    if args.json:
        print(json.dumps({"repository": str(root), "skills": [asdict(s) for s in skills], "findings": [asdict(f) for f in findings]}, indent=2))
    else:
        print(f"Agent skills audit: {root}")
        print(f"skills: {len(skills)}  findings: {len(findings)}")
        for skill in skills:
            print(f"SKILL {skill.path}: name={skill.name or '-'} scope={skill.scope or '-'} maturity={skill.maturity or '-'} lines={skill.lines}")
        for finding in findings:
            print(f"{finding.severity.upper():5} {finding.code:24} {finding.path}: {finding.message}")

    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
