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
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

SKILL_ROOTS = (Path(".agents/skills"), Path(".claude/skills"), Path("skills"))
CANONICAL_SKILL_ROOT = SKILL_ROOTS[0]
VERIFICATION_ROOT = Path(".agents/skill-evals")
VERIFICATION_SCHEMA = "openforge-agent-skill-verification/v1"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ABSOLUTE_PATH_RE = re.compile(r"(?:/Users/[^/\s]+|/home/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+)")
GENERIC_PROJECT_NAMES = {
    "build",
    "check",
    "debug",
    "deploy",
    "fix",
    "install",
    "release",
    "test",
    "upgrade",
    "validate",
    "verification",
}
VALID_SCOPES = {"core", "domain", "project"}
VALID_MATURITY = {"draft", "verified", "stable", "deprecated"}
PASS_STATUSES = {"pass", "passed", "success", "successful", "ok", "verified"}

# Codes that are advisory in a report but contract-breaking in a repository-local gate.
# A repository opts into fail-closed enforcement with --strict; the default severities stay
# as they are so the central portfolio audit keeps its existing meaning.
STRICT_CONTRACT_CODES = frozenset(
    {
        "CLAUDE-NO-AGENTS",
        "CLAUDE-GLOBAL-DEPENDENCY",
        "SKILL-OWNER",
        "SKILL-SCOPE-MISSING",
        "SKILL-MATURITY-MISSING",
        "SKILL-VERIFICATION-COMMAND-OWNER",
    }
)


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


def path_uses_symlink(root: Path, path: Path) -> bool:
    """Return True when path is reached through a symlinked directory inside root."""
    current = path.parent
    while current != root and current != current.parent:
        if current.is_symlink():
            return True
        current = current.parent
    return False


def file_identity(path: Path) -> object:
    """Return a key that is equal for two paths reaching one physical file.

    A repository may expose the same skill through several runtime discovery roots
    (`.agents/skills/foo -> ../../.claude/skills/foo`), and the alias must be audited once.
    The filesystem's own (device, inode) pair answers that regardless of how the path was
    spelled. exFAT, SMB without `serverino` and some FUSE drivers report `st_ino == 0` for
    every file, so an inode of zero carries no identity and must not be trusted: collapsing
    on it would silently drop distinct skills, which is worse than the duplicate it prevents.
    """
    try:
        stat = path.stat()
    except OSError:
        return path.resolve(strict=False)
    if stat.st_ino:
        return (stat.st_dev, stat.st_ino)
    return path.resolve(strict=False)


def skill_file_entries(skills_root: Path) -> List[Path]:
    """Return each skill directory's SKILL.md under the name it actually has on disk.

    Matching two globs (`*/SKILL.md` and `*/skill.md`) cannot answer this. A case-insensitive
    filesystem satisfies both patterns from one file and hands back the *pattern's* spelling, so
    the file is discovered twice and a genuinely lowercase filename is reported as `SKILL.md` —
    hiding it from the SKILL-CASE check on exactly the platforms where it is easiest to create.
    Directory entries carry the real name, so read them instead and match case-insensitively.
    """
    entries: List[Path] = []
    try:
        skill_dirs = sorted(skills_root.iterdir(), key=lambda item: item.name)
    except OSError:
        return entries
    for skill_dir in skill_dirs:
        if not skill_dir.is_dir():
            continue
        try:
            children = sorted(skill_dir.iterdir(), key=lambda item: item.name)
        except OSError:
            continue
        entries.extend(child for child in children if child.name.lower() == "skill.md" and child.is_file())
    return entries


def skill_files(root: Path) -> List[tuple[Path, Path]]:
    """Discover skill files while collapsing runtime symlink aliases.

    A repository may expose the same physical skill through multiple runtime discovery
    roots (for example `.agents/skills/foo -> ../../.claude/skills/foo`). Such aliases
    are one source of truth and must be audited once. Real copied files remain distinct
    and are still caught later by duplicate-name/body checks.
    """
    candidates: List[tuple[Path, Path]] = []
    root_order = {skill_root: index for index, skill_root in enumerate(SKILL_ROOTS)}
    for skill_root in SKILL_ROOTS:
        absolute = root / skill_root
        if not absolute.is_dir():
            continue
        candidates.extend((skill_root, file) for file in skill_file_entries(absolute))

    selected: Dict[object, tuple[tuple[int, int, str], Path, Path]] = {}
    for skill_root, file in candidates:
        target = file_identity(file)
        rank = (
            1 if path_uses_symlink(root, file) else 0,
            root_order[skill_root],
            str(file),
        )
        current = selected.get(target)
        if current is None or rank < current[0]:
            selected[target] = (rank, skill_root, file)

    return sorted(
        ((skill_root, file) for _, skill_root, file in selected.values()),
        key=lambda item: str(item[1]),
    )


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


MAKE_INCLUDE_RE = re.compile(r"^\s*[-s]?include\s+\S", re.M)


def _make_target_exists(root: Path, directory: Optional[str], target: str) -> Optional[bool]:
    base = (root / directory) if directory else root
    saw_include = False
    for name in ("Makefile", "makefile", "GNUmakefile"):
        makefile = base / name
        if not makefile.is_file():
            continue
        try:
            text = makefile.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if re.search(rf"^{re.escape(target)}:", text, re.M):
            return True
        saw_include = saw_include or bool(MAKE_INCLUDE_RE.search(text))
    if saw_include:
        # The target may be defined in an included fragment, whose path can be a variable or a
        # glob. Resolving that means implementing make, so report unknown rather than claim the
        # target is missing.
        return None
    return False


# Yarn subcommands that are built into the tool rather than package.json scripts. `yarn audit`
# is a real verification command; resolving it against `scripts` would report a missing owner
# for a command that needs none.
YARN_BUILTINS = frozenset(
    {
        "add", "audit", "bin", "cache", "config", "create", "dedupe", "dlx", "exec", "info",
        "init", "install", "link", "node", "npm", "pack", "patch", "plugin", "publish", "rebuild",
        "remove", "set", "unlink", "up", "upgrade", "version", "why", "workspace", "workspaces",
    }
)


def _npm_script_exists(root: Path, script: str) -> bool:
    package = root / "package.json"
    if not package.is_file():
        return False
    try:
        data = json.loads(package.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    scripts = data.get("scripts") if isinstance(data, dict) else None
    return isinstance(scripts, dict) and script in scripts


MAKE_COMMAND_RE = re.compile(r"^make\s+(?:-C\s+(\S+)\s+)?(\S+)$")
NPM_PNPM_RUN_RE = re.compile(r"^(?:npm|pnpm)\s+run\s+(\S+)$")
NPM_TEST_RE = re.compile(r"^npm\s+test$")
YARN_RUN_RE = re.compile(r"^yarn\s+(\S+)$")
SCRIPT_PATH_RE = re.compile(r"^(?:\./(\S+)|bash\s+(\S+)|sh\s+(\S+)|python3?\s+(\S+))(?:\s|$)")


def resolve_verification_command(root: Path, command: str) -> Optional[bool]:
    """Best-effort, fail-quiet check that a deterministicChecks command has a repo-local owner.

    Only a small set of common command forms are machine-checkable (make target, npm/pnpm/yarn
    script, or a script path that exists). Everything else returns None ("unknown") rather than
    being flagged. This is a deliberate trade-off: a false positive here becomes a wrong red
    build across every downstream repository that adopts --strict, which is far worse than
    silently skipping a command form we cannot confidently resolve.
    """
    text = command.strip()

    match = MAKE_COMMAND_RE.match(text)
    if match:
        directory, target = match.groups()
        return _make_target_exists(root, directory, target)

    match = NPM_PNPM_RUN_RE.match(text)
    if match:
        return _npm_script_exists(root, match.group(1))

    if NPM_TEST_RE.match(text):
        return _npm_script_exists(root, "test")

    match = YARN_RUN_RE.match(text)
    if match:
        subcommand = match.group(1)
        if subcommand in YARN_BUILTINS or subcommand.startswith("-"):
            return None
        return _npm_script_exists(root, subcommand)

    match = SCRIPT_PATH_RE.match(text)
    if match:
        path = next(group for group in match.groups() if group)
        if path.startswith("-"):
            return None
        return (root / path).is_file()

    return None


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
            command = str(check.get("command", "")).strip()
            if not command or not passed_status(check.get("status")):
                findings.append(
                    Finding(
                        "error",
                        "SKILL-VERIFICATION-CHECK",
                        rel,
                        f"deterministicChecks[{index}] requires command and an explicit passing status.",
                    )
                )
            elif resolve_verification_command(root, command) is False:
                findings.append(
                    Finding(
                        "warn",
                        "SKILL-VERIFICATION-COMMAND-OWNER",
                        rel,
                        f"deterministicChecks[{index}] command '{command}' has no resolvable "
                        "repository-local owner (Makefile target/npm-pnpm-yarn script/script "
                        "path not found).",
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
            findings.append(
                Finding(
                    "warn",
                    "CLAUDE-LARGE",
                    "CLAUDE.md",
                    f"CLAUDE.md is {lines} lines; classify sections and move workflows/docs out of the adapter.",
                )
            )
        match = ABSOLUTE_PATH_RE.search(text)
        if match:
            findings.append(
                Finding(
                    "error",
                    "CLAUDE-PERSONAL-PATH",
                    "CLAUDE.md",
                    f"Personal absolute path detected: {match.group(0)}",
                )
            )
        if "~/.claude/CLAUDE.md" in text:
            findings.append(
                Finding(
                    "warn",
                    "CLAUDE-GLOBAL-DEPENDENCY",
                    "CLAUDE.md",
                    "Repository behavior references a maintainer-global Claude configuration; keep it optional.",
                )
            )

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

        skills.append(
            Skill(
                rel,
                str(skill_root),
                directory,
                name,
                description,
                scope,
                owner,
                maturity,
                version,
                lines,
                body_hash[:12],
            )
        )

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
            findings.append(
                Finding(
                    "error",
                    "SKILL-LENGTH",
                    rel,
                    f"SKILL.md is {lines} lines; Agent Skills recommends keeping it under 500.",
                )
            )
        elif lines > 250:
            findings.append(
                Finding(
                    "warn",
                    "SKILL-LENGTH-TARGET",
                    rel,
                    f"SKILL.md is {lines} lines; move detail to references/scripts when practical.",
                )
            )
        if ABSOLUTE_PATH_RE.search(text):
            findings.append(Finding("error", "SKILL-PERSONAL-PATH", rel, "Personal absolute path found in a portable workflow."))

        if scope and scope not in VALID_SCOPES:
            findings.append(Finding("error", "SKILL-SCOPE", rel, f"Unknown openforge-scope '{scope}'."))
        if maturity and maturity not in VALID_MATURITY:
            findings.append(Finding("error", "SKILL-MATURITY", rel, f"Unknown openforge-maturity '{maturity}'."))
        elif not maturity and skill_root == CANONICAL_SKILL_ROOT:
            # Adapter roots legitimately mirror the canonical file, so only the canonical
            # copy is required to declare a lifecycle stage.
            findings.append(
                Finding(
                    "warn",
                    "SKILL-MATURITY-MISSING",
                    rel,
                    "Canonical skill has no metadata.openforge-maturity; add draft, verified, stable, or deprecated.",
                )
            )
        if scope == "project":
            if not owner:
                findings.append(Finding("warn", "SKILL-OWNER", rel, "Project skill should declare openforge-owner."))
            if name in GENERIC_PROJECT_NAMES:
                findings.append(
                    Finding(
                        "warn",
                        "SKILL-GENERIC-NAME",
                        rel,
                        f"Project skill name '{name}' can collide globally; prefer <project>-<task>.",
                    )
                )
        if not scope:
            findings.append(
                Finding(
                    "info",
                    "SKILL-SCOPE-MISSING",
                    rel,
                    "Add OpenForge scope/owner/maturity/version metadata during migration.",
                )
            )

        if name and maturity in {"verified", "stable"}:
            findings.extend(validate_verification_evidence(root, name, version, maturity, rel))

        if name:
            if name in seen_names:
                findings.append(
                    Finding(
                        "error",
                        "SKILL-DUP-NAME",
                        rel,
                        f"Duplicate skill name; first seen at {seen_names[name]}.",
                    )
                )
            else:
                seen_names[name] = rel
        if description:
            normalized = " ".join(description.lower().split())
            if normalized in seen_desc:
                findings.append(
                    Finding(
                        "warn",
                        "SKILL-DUP-DESCRIPTION",
                        rel,
                        f"Same normalized description as {seen_desc[normalized]}.",
                    )
                )
            else:
                seen_desc[normalized] = rel
        if body.strip():
            if body_hash in seen_body:
                findings.append(
                    Finding(
                        "warn",
                        "SKILL-DUP-BODY",
                        rel,
                        f"Same normalized body as {seen_body[body_hash]}.",
                    )
                )
            else:
                seen_body[body_hash] = rel

    return skills, findings


def gate_failed(findings: List[Finding], strict: bool) -> bool:
    """Exit-code decision for a repository-local fail-closed gate.

    Default severities are unchanged (the central portfolio audit and downstream repositories
    consume them as-is); --strict additionally treats STRICT_CONTRACT_CODES findings, at any
    severity, as gate failures.
    """
    for finding in findings:
        if finding.severity == "error":
            return True
        if strict and finding.code in STRICT_CONTRACT_CODES:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "fail-closed repository-local gate: escalate STRICT_CONTRACT_CODES findings "
            "(advisory by default) to non-zero exit"
        ),
    )
    args = parser.parse_args()

    root = Path(args.path).resolve()
    skills, findings = audit(root)

    if args.json:
        print(
            json.dumps(
                {
                    "repository": str(root),
                    "skills": [asdict(skill) for skill in skills],
                    "findings": [asdict(finding) for finding in findings],
                },
                indent=2,
            )
        )
    else:
        print(f"Agent skills audit: {root}")
        print(f"skills: {len(skills)}  findings: {len(findings)}")
        for skill in skills:
            print(
                f"SKILL {skill.path}: name={skill.name or '-'} scope={skill.scope or '-'} "
                f"maturity={skill.maturity or '-'} lines={skill.lines}"
            )
        for finding in findings:
            print(f"{finding.severity.upper():5} {finding.code:30} {finding.path}: {finding.message}")

    if args.strict:
        escalated = sorted({finding.code for finding in findings if finding.code in STRICT_CONTRACT_CODES})
        if escalated:
            # stderr, not stdout: --json output must stay parseable for CI consumers that
            # pipe it straight into a JSON parser (see templates/github/agent-contract-gate.yml).
            print(
                f"STRICT: escalating advisory codes to gate the exit code: {', '.join(escalated)}",
                file=sys.stderr,
            )

    return 1 if gate_failed(findings, args.strict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
