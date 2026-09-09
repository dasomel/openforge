#!/usr/bin/env python3
"""Audit repository agent instruction and Agent Skills hygiene.

This scanner is intentionally dependency-free. It validates the subset of SKILL.md
frontmatter OpenForge relies on, checks verification-evidence artifacts for mature
skills, and reports migration warnings without rewriting files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

SKILL_ROOTS = (Path(".agents/skills"), Path(".claude/skills"), Path("skills"))
VERIFICATION_ROOT = Path(".agents/skill-evals")
VERIFICATION_SCHEMA = "openforge-agent-skill-verification/v1"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ABSOLUTE_PATH_RE = re.compile(r"(?:/Users/[^/\s]+|/home/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+)")
GENERIC_PROJECT_NAMES = {
    "build", "check", "debug", "deploy", "fix", "install", "release", "test", "upgrade", "validate", "verification"
}
VALID_SCOPES = {"core", "domain", "project"}
VALID_MATURITY = {"draft", "verified", "stable", "deprecated"}
PASS_STATUSES = {"pass", "passed", "success", "successful", "ok", "verified"}


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


def load_verification_evidence(path: Path) -> tuple[Optional[dict], Optional[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(value, dict):
        return None, "top-level JSON value must be an object"
    return value, None


def passed_status(value: object) -> bool:
    return str(value or "").strip().lower() in PASS_STATUSES


def validate_verification_evidence(
    root: Path,
    skill_name: str,
    skill_version: Optional[str],
    maturity: str,
    skill_path: str,
) -> List[Finding]:
    findings: List[Finding] = []
    evidence_path = root / VERIFICATION_ROOT / f"{skill_name}.json"
    rel = str(evidence_path.relative_to(root))

    if not evidence_path.is_file():
        findings.append(
            Finding(
                "error",
                "SKILL-VERIFICATION-EVIDENCE",
                skill_path,
                f"{maturity} skill requires {VERIFICATION_ROOT}/{skill_name}.json.",
            )
        )
        return findings

    evidence, error = load_verification_evidence(evidence_path)
    if error or evidence is None:
        findings.append(Finding("error", "SKILL-VERIFICATION-JSON", rel, f"Invalid verification evidence: {error}"))
        return findings

    if evidence.get("schemaVersion") != VERIFICATION_SCHEMA:
        findings.append(
            Finding(
                "error",
                "SKILL-VERIFICATION-SCHEMA",
                rel,
                f"schemaVersion must be {VERIFICATION_SCHEMA}.",
            )
        )
    if evidence.get("skill") != skill_name:
        findings.append(Finding("error", "SKILL-VERIFICATION-NAME", rel, "Evidence skill must match SKILL.md name."))
    if str(evidence.get("skillVersion", "")) != str(skill_version or ""):
        findings.append(
            Finding(
                "error",
                "SKILL-VERIFICATION-VERSION",
                rel,
                "Evidence skillVersion must match metadata.openforge-version.",
            )
        )
    if evidence.get("freshSession") is not True:
        findings.append(
            Finding(
                "error",
                "SKILL-VERIFICATION-FRESH",
                rel,
                "verified/stable skill evidence must record freshSession=true.",
            )
        )

    runtime = evidence.get("agentRuntime")
    if not isinstance(runtime, str) or not runtime.strip():
        findings.append(
            Finding(
                "error",
                "SKILL-VERIFICATION-RUNTIME",
                rel,
                "agentRuntime must identify the runtime used for the replay.",
            )
        )

    happy = evidence.get("happyPath")
    if not isinstance(happy, dict) or not passed_status(happy.get("status")):
        findings.append(
            Finding(
                "error",
                "SKILL-VERIFICATION-HAPPY",
                rel,
                "happyPath.status must explicitly pass.",
            )
        )
    elif not isinstance(happy.get("evidence"), list) or not happy["evidence"]:
        findings.append(
            Finding(
                "error",
                "SKILL-VERIFICATION-HAPPY-EVIDENCE",
                rel,
                "happyPath.evidence must contain at least one evidence reference.",
            )
        )

    edge = evidence.get("edgeCase")
    if not isinstance(edge, dict) or not passed_status(edge.get("status")):
        findings.append(
            Finding(
                "error",
                "SKILL-VERIFICATION-EDGE",
                rel,
                "edgeCase.status must explicitly pass.",
            )
        )
    elif not isinstance(edge.get("evidence"), list) or not edge["evidence"]:
        findings.append(
            Finding(
                "error",
                "SKILL-VERIFICATION-EDGE-EVIDENCE",
                rel,
                "edgeCase.evidence must contain at least one regression/evidence reference.",
            )
        )

    checks = evidence.get("deterministicChecks")
    if not isinstance(checks, list) or not checks:
        findings.append(
            Finding(
                "error",
                "SKILL-VERIFICATION-CHECKS",
                rel,
                "deterministicChecks must contain at least one repository-owned check.",
            )
        )
    else:
        for index, check in enumerate(checks):
            if not isinstance(check, dict):
                findings.append(
                    Finding(
                        "error",
                        "SKILL-VERIFICATION-CHECK",
                        rel,
                        f"deterministicChecks[{index}] must be an object.",
                    )
                )
                continue
            if not str(check.get("command", "")).strip() or not passed_status(check.get("status")):
                findings.append(
                    Finding(
                        "error",
                        "SKILL-VERIFICATION-CHECK",
                        rel,
                        f"deterministicChecks[{index}] requires command and an explicit passing status.",
                    )
                )

    unverified = evidence.get("unverified")
    if unverified is not None and not isinstance(unverified, list):
        findings.append(Finding("error", "SKILL-VERIFICATION-UNVERIFIED", rel, "unverified must be a JSON array."))

    verified_at = str(evidence.get("verifiedAt", ""))
    if not DATE_RE.match(verified_at):
        findings.append(
            Finding(
                "error",
                "SKILL-VERIFICATION-DATE",
                rel,
                "verifiedAt must use YYYY-MM-DD.",
            )
        )
    else:
        try:
            parsed = date.fromisoformat(verified_at)
            if parsed > date.today():
                findings.append(Finding("error", "SKILL-VERIFICATION-FUTURE", rel, "verifiedAt cannot be in the future."))
        except ValueError:
            findings.append(Finding("error", "SKILL-VERIFICATION-DATE", rel, "verifiedAt is not a valid date."))

    return findings


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

        if name and maturity in {"verified", "stable"}:
            findings.extend(validate_verification_evidence(root, name, version, maturity, rel))

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
            print(f"{finding.severity.upper():5} {finding.code:30} {finding.path}: {finding.message}")

    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
