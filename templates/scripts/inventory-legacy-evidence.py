#!/usr/bin/env python3
"""Discover and validate references to evidence that already exists in a repository."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = ROOT / "portfolio" / "legacy-evidence-catalog.json"
SCHEMA = ROOT / "schemas" / "legacy-evidence-catalog-v1.schema.json"
SKIP_PARTS = {".git", "node_modules", "vendor", "__pycache__", ".venv", ".bench-scratch", ".omc", "00.bak", ".terraform", ".bkit", "dist", "build", "target", ".next", "coverage"}
SOURCE_EXTENSIONS = {
    ".bash", ".c", ".cc", ".cpp", ".go", ".h", ".hpp", ".java", ".js", ".jsx", ".kt", ".kts",
    ".nix", ".php", ".py", ".rb", ".rs", ".scala", ".sh", ".swift", ".ts", ".tsx", ".vue",
}
CLASSES = {
    "verification-quality": ("qa", "test", "smoke", "regression", "lint", "typecheck", "build", "pass", "fail", "skip"),
    "deployment-reproducibility": ("install", "bootstrap", "provision", "upgrade", "air-gap", "compatib", "environment"),
    "reliability-recovery": ("failure", "incident", "retry", "rollback", "recovery", "negative", "error"),
    "runtime-performance": ("latency", "duration", "elapsed", "benchmark", "profil", "cpu", "memory", "storage", "network", "thermal"),
    "agent-assisted-engineering": ("agent", "trace", "intervention", "review", "attempt", "ci retry"),
    "release-adoption-evolution": ("release", "changelog", "compatib", "history", "migration", "version"),
    "architecture-requirements": ("architecture", "design", "lesson", "implementation status", "requirements", "rfp", "decision"),
}
NUMBER_RE = re.compile(r"(?<![A-Za-z])[+-]?(?:\d+(?:\.\d+)?|\.\d+)", re.I)
UNIT_RE = re.compile(r"(?<![A-Za-z])[+-]?(?:\d+(?:\.\d+)?|\.\d+)\s*(?:ms|s|sec|seconds|minutes?|hours?|bytes?|kb|mb|gb|tb|cpu|cores?|%)(?![A-Za-z])", re.I)
# An outcome word carries a count either way round ("6 pass", "passed: 67"). An enumerable
# noun does not: "Check 1" is a section heading, so the label-first form needs an explicit
# separator ("checks: 23") while "23 checks" still reads as a count.
_OUTCOME = r"pass(?:ed)?|fail(?:ed)?|skip(?:ped)?|total"
_ENUMERABLE = r"checks?|routes?"
COUNT_RE = re.compile(
    r"(?i)(?:"
    rf"\b(?:{_OUTCOME})\b\s*[:=]?\s*[+-]?\d+"
    rf"|[+-]?\d+[ \t]+\b(?:{_OUTCOME}|{_ENUMERABLE})\b"
    rf"|\b(?:{_ENUMERABLE})\b\s*[:=]\s*[+-]?\d+"
    r")"
)
# A bare ordinal after a section-heading label (Check 1, Step 2, Phase 3, ...) is an enumerated
# heading, not a measurement: no unit, no pass/fail sense, and no explicit ":"/"=" binding it to
# a field. Filters COUNT_RE hits like "Check 1" while leaving "6 pass; 4 fail" untouched.
LABEL_ORDINAL_RE = re.compile(r"(?i)^(?:check|step|phase|test|section|part)s?\s+[+-]?\d+(?:\.\d+)?$")
DATE_RE = re.compile(r"(?<!\d)(20\d{2}-\d{2}-\d{2})(?!\d)")
KNOWN_NUMERIC_KEYS = {"total", "passed", "pass", "failed", "fail", "skipped", "skip", "duration", "elapsed", "latency", "memory", "cpu", "bytes", "size", "count", "routes", "checks"}
EXPLICIT_ENV_RE = re.compile(r"(?im)^\s*(?:environment(?:_scope)?|scope)\s*[:=]\s*[`\"]?\s*(local-test|ci|simulation|live-test|unknown)\b")


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc


def is_text(path: Path) -> bool:
    try:
        data = path.read_bytes()
    except OSError:
        return False
    return b"\x00" not in data[:8192]


def evidence_class(text: str, path: Path) -> str:
    lowered_path = path.as_posix().lower()
    if "evals/traces/" in lowered_path:
        return "agent-assisted-engineering"
    if any(token in lowered_path for token in ("lesson", "implementation-status", "architecture", "requirements", "rfp")):
        return "architecture-requirements"
    if "qa-report" in lowered_path or "qa_report" in lowered_path:
        return "verification-quality"
    haystack = f"{path.as_posix()}\n{text}".lower()
    scores = {name: sum(haystack.count(signal) for signal in signals) for name, signals in CLASSES.items()}
    return max(sorted(scores), key=lambda name: scores[name])


def structured_values(text: str, path: Path) -> list[str]:
    if path.suffix.lower() != ".json":
        return []
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return []
    found: list[str] = []
    def walk(item: object, prefix: str = "") -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                key_lower = key.lower().replace("-", "_")
                child_path = f"{prefix}.{key}" if prefix else key
                recognized_key = key_lower in KNOWN_NUMERIC_KEYS or any(token in key_lower for token in ("duration", "elapsed", "latency", "memory", "bytes"))
                if recognized_key and isinstance(child, (int, float)) and not isinstance(child, bool):
                    found.append(f"{child_path}={child}")
                walk(child, child_path)
        elif isinstance(item, list):
            for child in item:
                walk(child, prefix)
    walk(value)
    return found


def recognised_metrics(text: str, path: Path) -> list[str]:
    found = COUNT_RE.findall(text) + UNIT_RE.findall(text)
    found.extend(structured_values(text, path))
    unique: list[str] = []
    for metric in found:
        metric = " ".join(metric.split())
        if LABEL_ORDINAL_RE.match(metric):
            continue
        if metric not in unique:
            unique.append(metric)
    return unique


def explicit_date(text: str, path: Path) -> str | None:
    path_match = DATE_RE.search(path.as_posix())
    if path_match:
        return path_match.group(1)
    if path.suffix.lower() == ".json":
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            value = None
        if isinstance(value, dict):
            for key in ("evidence_date", "evidenceDate", "date"):
                candidate = value.get(key)
                if isinstance(candidate, str) and re.fullmatch(r"20\d{2}-\d{2}-\d{2}", candidate):
                    return candidate
    frontmatter = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    if frontmatter:
        match = re.search(r"(?im)^\s*(?:evidence_date|date)\s*:\s*[\"']?(20\d{2}-\d{2}-\d{2})", frontmatter.group(1))
        if match:
            return match.group(1)
    return None


def environment(text: str) -> str:
    match = EXPLICIT_ENV_RE.search(text)
    if match:
        return match.group(1).lower()
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        value = None
    if isinstance(value, dict):
        for key in ("environment_scope", "environmentScope", "environment"):
            scope = value.get(key)
            if isinstance(scope, str) and scope.lower() in {"local-test", "ci", "simulation", "live-test", "unknown"}:
                return scope.lower()
    return "unknown"


def tracked_files(repo: Path) -> set[str] | None:
    """Return the set of git-tracked paths (repo-relative, POSIX) in repo, or None if repo is not a git work tree."""
    probe = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True,
    )
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return None
    listing = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z"],
        capture_output=True, text=True,
    )
    if listing.returncode != 0:
        return None
    return {entry for entry in listing.stdout.split("\0") if entry}


def availability(tracked: set[str] | None, relative: str) -> str:
    if tracked is None:
        return "unknown"
    return "committed" if relative in tracked else "local-only"


LOCAL_ONLY_NOTE = "Not present in a fresh clone; this working tree's copy is the only one and would be lost if discarded, so preserving it requires deliberately committing or archiving it."


def candidate(repository: str, repo: Path, path: Path, tracked: set[str] | None) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    metrics = recognised_metrics(text, path)
    relative = path.relative_to(repo)
    relative_posix = relative.as_posix()
    cls = evidence_class(text, relative)
    if cls == "architecture-requirements":
        strength = "contextual"
    elif metrics:
        strength = "measured"
    elif path.suffix.lower() in {".json", ".log", ".txt", ".csv"} or "report" in path.name.lower():
        strength = "observed"
    else:
        strength = "contextual"
    facts = f"Recognized metrics extracted: {'; '.join(metrics[:8])}." if metrics else f"{cls.replace('-', ' ').capitalize()} artifact; no recognized metric extracted."
    avail = availability(tracked, relative_posix)
    limitations = "Heuristic discovery; review the source artifact before quantitative reuse." + (" No recognized metric was recorded." if not metrics else "")
    if avail == "local-only":
        limitations = f"{limitations} {LOCAL_ONLY_NOTE}"
    return {
        "repository": repository,
        "path": relative_posix,
        "evidence_date": explicit_date(text, relative),
        "evidence_class": cls,
        "evidence_strength": strength,
        "environment_scope": environment(text),
        "metrics_or_facts": facts,
        "limitations": limitations,
        "future_paper_use": f"Candidate source for {cls} analysis after manual scope and privacy review.",
        "privacy_review": "secret-check-required",
        "availability": avail,
    }


def is_excluded_artifact(relative: Path) -> bool:
    """Return whether a path is tooling, synthetic data, or application source."""
    # D5: exclude instruments, blank templates, hidden config, and synthetic fixtures because they
    # do not record historical evidence; committed outputs remain eligible outside these paths.
    # D6: exclude application source to keep the catalog bounded to recorded artifacts; an explicit
    # output format can be added later without weakening this deterministic source-file boundary.
    parts = tuple(part.lower() for part in relative.parts)
    for index in range(len(parts) - 1):
        if parts[index:index + 2] in ((".github", "issue_template"), (".github", "workflows"), ("templates", "workflows")):
            return True
    if any(part in {"fixtures", "testdata"} for part in parts):
        return True
    if "src" in parts:
        return True
    if relative.name.startswith("."):
        return True
    return relative.suffix.lower() in SOURCE_EXTENSIONS


def discover(repo: Path, repository: str) -> list[dict[str, object]]:
    entries = []
    tracked = tracked_files(repo)
    paths: list[Path] = []
    for directory, dirnames, filenames in __import__("os").walk(repo):
        dirnames[:] = sorted(name for name in dirnames if name not in SKIP_PARTS)
        paths.extend(Path(directory) / name for name in sorted(filenames))
    for path in sorted(paths):
        if SKIP_PARTS.intersection(path.relative_to(repo).parts) or not is_text(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lowered = text.lower()
        name = path.name.lower()
        relative = path.relative_to(repo)
        if is_excluded_artifact(relative):
            continue
        parts = {part.lower() for part in relative.parts}
        evidence_area = bool(parts.intersection({"evidence", "research", "experiments", "results", "reports"}))
        trace_area = "evals" in parts and "traces" in parts
        signals = sum(lowered.count(signal) for values in CLASSES.values() for signal in values)
        named = any(token in name for token in ("report", "trace", "result", "benchmark", "profile", "lesson", "status", "compat", "acceptance", "incident", "verification", "mistake", "requirement", "architecture"))
        if not evidence_area and not trace_area and not named:
            continue
        if not evidence_area and not trace_area and signals < 3 and not named:
            continue
        entries.append(candidate(repository, repo, path, tracked))
    return entries


def validate(doc: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(doc, dict) or doc.get("schema_version") != "openforge-legacy-evidence-catalog/v1":
        return ["schema_version must be openforge-legacy-evidence-catalog/v1"]
    entries = doc.get("entries")
    if not isinstance(entries, list):
        return ["entries must be an array"]
    pending = doc.get("pending_repositories", [])
    if not isinstance(pending, list):
        errors.append("pending_repositories must be an array")
    else:
        for index, item in enumerate(pending):
            if not isinstance(item, dict) or not isinstance(item.get("repository"), str) or not item.get("repository", "").strip():
                errors.append(f"pending_repositories[{index}] must contain a repository")
            if isinstance(item, dict) and item.get("status") != "not-scanned":
                errors.append(f"pending_repositories[{index}] status must be not-scanned")
    required = {"repository", "path", "evidence_date", "evidence_class", "evidence_strength", "environment_scope", "metrics_or_facts", "limitations", "future_paper_use", "privacy_review", "availability"}
    allowed = {
        "evidence_class": set(CLASSES),
        "evidence_strength": {"measured", "observed", "derived", "contextual"},
        "environment_scope": {"local-test", "ci", "simulation", "live-test", "unknown"},
        "privacy_review": {"public-ok", "secret-check-required", "exclude"},
        "availability": {"committed", "local-only", "unknown"},
    }
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entries[{index}] must be an object")
            continue
        missing = sorted(required - entry.keys())
        errors.extend(f"entries[{index}] missing {key}" for key in missing)
        for key, values in allowed.items():
            if key in entry and entry[key] not in values:
                errors.append(f"entries[{index}] invalid {key}: {entry[key]!r}")
        for key in ("repository", "path", "metrics_or_facts", "limitations", "future_paper_use"):
            if key in entry and (not isinstance(entry[key], str) or not entry[key].strip()):
                errors.append(f"entries[{index}] {key} must be a non-empty string")
        date = entry.get("evidence_date")
        if date is not None and (not isinstance(date, str) or not re.fullmatch(r"20\d{2}(?:-\d{2}(?:-\d{2})?)?", date)):
            errors.append(f"entries[{index}] invalid evidence_date: {date!r}")
        if entry.get("evidence_strength") == "measured" and "recognized metric" not in str(entry.get("metrics_or_facts", "")).lower():
            errors.append(f"entries[{index}] measured entry must name recognized metrics")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--repository")
    parser.add_argument("--catalog", "--config", dest="catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--refresh", action="store_true", help="replace this repository's entries in --catalog")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.validate:
        try:
            errors = validate(load_json(args.catalog))
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        if errors:
            print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
            return 1
        print(f"Legacy evidence catalog valid: {args.catalog}")
        return 0
    if not args.repo or not args.repository:
        parser.error("--repo and --repository are required unless --validate is used")
    entries = discover(args.repo.resolve(), args.repository)
    if args.refresh:
        doc = load_json(args.catalog)
        doc["entries"] = [entry for entry in doc["entries"] if entry.get("repository") != args.repository] + entries
        doc["entries"].sort(key=lambda entry: (entry["repository"], entry["path"]))
        args.catalog.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(entries, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
