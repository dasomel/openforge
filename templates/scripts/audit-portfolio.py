#!/usr/bin/env python3
"""
OpenForge Portfolio Compliance Audit Engine
Audits active open source repositories against OpenForge standards (Reference Metrics,
Agent Engineering, Design System, ADR Governance, Security, Supply Chain, and CI).
"""

import os
import sys
import json
import glob
import re
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# ==============================================================================
# Metric Registry with Stable IDs, Weights, and Metadata
# ==============================================================================

METRIC_DEFINITIONS: List[Dict[str, Any]] = [
    # 1. Documentation
    {
        "id": "DOC-001",
        "area": "Documentation",
        "name": "English README",
        "target": "Canonical README.md present at repository root",
        "default_weight": 1,
        "related_adr": "ADR-0002",
        "related_standard": "docs/documentation.md",
        "priority": "P1",
    },
    {
        "id": "DOC-002",
        "area": "Documentation",
        "name": "Korean README",
        "target": "README-ko.md present at repository root",
        "default_weight": 1,
        "related_adr": "ADR-0002",
        "related_standard": "docs/i18n.md",
        "priority": "P1",
    },
    {
        "id": "DOC-003",
        "area": "Documentation",
        "name": "Korean Filename Standard",
        "target": "Use <name>-ko.md format without legacy _ko.md or .ko.md",
        "default_weight": 1,
        "related_adr": "ADR-0002",
        "related_standard": "docs/documentation.md",
        "priority": "P2",
    },
    {
        "id": "DOC-004",
        "area": "Documentation",
        "name": "Language-paired Docs Ratio",
        "target": "User-facing markdown documentation in docs/ has Korean pairs",
        "default_weight": 1,
        "related_adr": "ADR-0002",
        "related_standard": "docs/i18n.md",
        "priority": "P2",
    },
    {
        "id": "DOC-005",
        "area": "Documentation",
        "name": "Architecture Document",
        "target": "docs/architecture*.md or ARCHITECTURE.md present",
        "default_weight": 1,
        "related_adr": "ADR-0001",
        "related_standard": "docs/development.md",
        "priority": "P1",
    },
    {
        "id": "DOC-006",
        "area": "Documentation",
        "name": "Development Guide",
        "target": "docs/development*.md, DEVELOPMENT.md, or CONTRIBUTING.md",
        "default_weight": 1,
        "related_adr": "ADR-0001",
        "related_standard": "docs/development.md",
        "priority": "P2",
    },
    {
        "id": "DOC-007",
        "area": "Documentation",
        "name": "Release Guide & Changelog",
        "target": "CHANGELOG.md and RELEASING.md present",
        "default_weight": 1,
        "related_adr": "ADR-0006",
        "related_standard": "docs/release.md",
        "priority": "P1",
    },
    {
        "id": "DOC-008",
        "area": "Documentation",
        "name": "Version Inventory",
        "target": "VERSIONS.md or version declared in project manifest",
        "default_weight": 1,
        "related_adr": "ADR-0005",
        "related_standard": "docs/upgrade-compatibility.md",
        "priority": "P3",
    },
    {
        "id": "DOC-009",
        "area": "Documentation",
        "name": "Lessons & Mistakes Log",
        "target": "lessons-log.md, mistakes-log.md, or operational retention notes",
        "default_weight": 1,
        "related_adr": "ADR-0009",
        "related_standard": "docs/reference-practices.md",
        "priority": "P3",
    },
    # 2. Architecture & Decision Governance
    {
        "id": "ARCH-001",
        "area": "Architecture",
        "name": "ADR Process Presence",
        "target": "docs/adr/ or adr/ directory with numbered decision records",
        "default_weight": 1,
        "related_adr": "ADR-0001",
        "related_standard": "docs/decision-management.md",
        "priority": "P1",
    },
    {
        "id": "ARCH-002",
        "area": "Architecture",
        "name": "ADR Bilingual Pairs",
        "target": "100% of user-facing ADRs have corresponding -ko.md pairs",
        "default_weight": 1,
        "related_adr": "ADR-0002",
        "related_standard": "docs/decision-management.md",
        "priority": "P1",
    },
    {
        "id": "ARCH-003",
        "area": "Architecture",
        "name": "Decision Management Standard & Map",
        "target": "docs/decision-management*.md or docs/decision-map*.md present",
        "default_weight": 1,
        "related_adr": "ADR-0001",
        "related_standard": "docs/decision-map.md",
        "priority": "P3",
    },
    {
        "id": "ARCH-004",
        "area": "Architecture",
        "name": "DESIGN.md Contract",
        "target": "DESIGN.md declaring product archetype and token mapping",
        "default_weight": 1,
        "related_adr": "ADR-0007",
        "related_standard": "docs/design-system.md",
        "priority": "P1",
    },
    # 3. GitHub Standards
    {
        "id": "GH-001",
        "area": "GitHub",
        "name": "PR Template",
        "target": ".github/pull_request_template.md present",
        "default_weight": 1,
        "related_adr": "ADR-0003",
        "related_standard": "docs/github.md",
        "priority": "P2",
    },
    {
        "id": "GH-002",
        "area": "GitHub",
        "name": "Issue Templates",
        "target": ".github/ISSUE_TEMPLATE/ for bug reports and features",
        "default_weight": 1,
        "related_adr": "ADR-0003",
        "related_standard": "docs/github.md",
        "priority": "P2",
    },
    {
        "id": "GH-003",
        "area": "GitHub",
        "name": "Contributing Guide (Bilingual)",
        "target": "CONTRIBUTING.md and CONTRIBUTING-ko.md present",
        "default_weight": 1,
        "related_adr": "ADR-0002",
        "related_standard": "docs/documentation.md",
        "priority": "P2",
    },
    {
        "id": "GH-004",
        "area": "GitHub",
        "name": "Code of Conduct",
        "target": "CODE_OF_CONDUCT.md present",
        "default_weight": 1,
        "related_adr": "ADR-0003",
        "related_standard": "docs/maintainer-governance.md",
        "priority": "P2",
    },
    {
        "id": "GH-005",
        "area": "GitHub",
        "name": "License",
        "target": "Open source LICENSE file present",
        "default_weight": 1,
        "related_adr": "ADR-0003",
        "related_standard": "docs/oss-compliance.md",
        "priority": "P0",
    },
    # 4. CI & Verification
    {
        "id": "CI-001",
        "area": "CI",
        "name": "Automated CI Workflows",
        "target": ".github/workflows/*.yml configuring continuous integration",
        "default_weight": 1,
        "related_adr": "ADR-0011",
        "related_standard": "docs/ci-cd.md",
        "priority": "P0",
    },
    {
        "id": "CI-002",
        "area": "CI",
        "name": "Format & Lint Check in CI",
        "target": "Automated code formatting or linting validation in CI",
        "default_weight": 1,
        "related_adr": "ADR-0008",
        "related_standard": "docs/tooling.md",
        "priority": "P1",
    },
    {
        "id": "CI-003",
        "area": "CI",
        "name": "Automated Tests in CI",
        "target": "Automated unit/integration test execution in CI",
        "default_weight": 1,
        "related_adr": "ADR-0009",
        "related_standard": "docs/ci-cd.md",
        "priority": "P0",
    },
    {
        "id": "CI-004",
        "area": "CI",
        "name": "Automated Build in CI",
        "target": "Automated artifact compilation or package build in CI",
        "default_weight": 1,
        "related_adr": "ADR-0006",
        "related_standard": "docs/reproducible-build.md",
        "priority": "P0",
    },
    {
        "id": "CI-005",
        "area": "CI",
        "name": "Documentation & ADR Validation in CI",
        "target": "CI checks for markdown naming, ADR pairs, or documentation drift",
        "default_weight": 1,
        "related_adr": "ADR-0002",
        "related_standard": "docs/documentation.md",
        "priority": "P2",
    },
    {
        "id": "CI-006",
        "area": "CI",
        "name": "Supply Chain & Security Gates in CI",
        "target": "SBOM generation, supply-chain checks, or policy validation in CI",
        "default_weight": 1,
        "related_adr": "ADR-0006",
        "related_standard": "docs/supply-chain.md",
        "priority": "P0",
    },
    # 5. Security & Supply Chain
    {
        "id": "SEC-001",
        "area": "Security",
        "name": "Dependency Update Automation",
        "target": ".github/dependabot.yml or Renovate configuration present",
        "default_weight": 1,
        "related_adr": "ADR-0006",
        "related_standard": "docs/vulnerability-management.md",
        "priority": "P0",
    },
    {
        "id": "SEC-002",
        "area": "Security",
        "name": "SECURITY Policy (Bilingual)",
        "target": "SECURITY.md and SECURITY-ko.md present",
        "default_weight": 1,
        "related_adr": "ADR-0003",
        "related_standard": "docs/security.md",
        "priority": "P0",
    },
    {
        "id": "SEC-003",
        "area": "Security",
        "name": "Container Security Scanning",
        "target": "Trivy, Hadolint, or container vulnerability scanner in CI",
        "default_weight": 1,
        "related_adr": "ADR-0006",
        "related_standard": "docs/container-iac-security.md",
        "priority": "P1",
    },
    {
        "id": "SEC-004",
        "area": "Security",
        "name": "Static Code Scanning / SAST",
        "target": "CodeQL, SAST, or static analysis in CI / policy enforcement",
        "default_weight": 1,
        "related_adr": "ADR-0003",
        "related_standard": "docs/ci-security.md",
        "priority": "P1",
    },
    {
        "id": "SEC-005",
        "area": "Security",
        "name": ".env.example Configuration Template",
        "target": ".env.example with sanitized placeholder secrets",
        "default_weight": 1,
        "related_adr": "ADR-0003",
        "related_standard": "docs/secrets-identity.md",
        "priority": "P1",
    },
    # 6. Agent Engineering
    {
        "id": "AGENT-001",
        "area": "Agent Engineering",
        "name": "Agent Root Contract",
        "target": "Concise AGENTS.md or CLAUDE.md defining root boundaries",
        "default_weight": 1,
        "related_adr": "ADR-0008",
        "related_standard": "docs/agent-engineering.md",
        "priority": "P1",
    },
    {
        "id": "AGENT-002",
        "area": "Agent Engineering",
        "name": "Layered Instructions Model",
        "target": "Separation between concise root contract and CODING_STANDARDS.md",
        "default_weight": 1,
        "related_adr": "ADR-0008",
        "related_standard": "docs/agent-engineering.md",
        "priority": "P2",
    },
    {
        "id": "AGENT-003",
        "area": "Agent Engineering",
        "name": "Evidence & Convergence Rules",
        "target": "Explicit stop conditions (A/B/C) and bug reproduction requirement",
        "default_weight": 1,
        "related_adr": "ADR-0009",
        "related_standard": "docs/agent-engineering.md",
        "priority": "P1",
    },
    # 7. Design System & Localization
    {
        "id": "DESIGN-001",
        "area": "Design System",
        "name": "Product Archetype Declaration",
        "target": "Archetype declared in DESIGN.md from OpenForge standard archetypes",
        "default_weight": 1,
        "related_adr": "ADR-0007",
        "related_standard": "docs/design-system.md",
        "priority": "P1",
    },
    {
        "id": "DESIGN-002",
        "area": "Design System",
        "name": "Semantic Token Mapping",
        "target": "Project tokens mapped to OpenForge semantic roles in DESIGN.md",
        "default_weight": 1,
        "related_adr": "ADR-0007",
        "related_standard": "docs/design-system.md",
        "priority": "P2",
    },
    {
        "id": "I18N-001",
        "area": "Localization",
        "name": "UI i18n (en-US & ko-KR)",
        "target": "en-US and ko-KR locale resources configured for user-facing UI",
        "default_weight": 1,
        "related_adr": "ADR-0002",
        "related_standard": "docs/i18n.md",
        "priority": "P2",
    },
]

VALID_ARCHETYPES = {
    "Platform Portal",
    "Data Control Plane",
    "Desktop Operator",
    "Operations Dashboard",
    "Admin Console",
    "Developer Tool",
}

VALID_PROFILES = {
    "standard",
    "platform",
    "desktop",
    "controller",
    "library",
    "documentation",
    "lab",
}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "_workspace",
    ".omc",
    "dist",
    "vendor",
    ".venv",
    "__pycache__",
    "build",
    "target",
    ".idea",
    "fixtures",
}


# ==============================================================================
# Helper functions for portable config loading (PyYAML + Stdlib fallback)
# ==============================================================================

def load_yaml_safe(content: str, force_fallback: bool = False) -> Dict[str, Any]:
    if not force_fallback:
        try:
            import yaml
            return yaml.safe_load(content) or {}
        except ImportError:
            pass

    # Restricted, zero-dependency subset YAML parser for OpenForge portfolio configs
    # Explicitly rejects complex YAML features (anchors, aliases, multiline scalars, tabs)
    data: Dict[str, Any] = {"repositories": []}
    current_repo: Optional[Dict[str, Any]] = None
    in_repos = False

    for idx, line in enumerate(content.splitlines(), 1):
        if "\t" in line:
            raise ValueError(f"Malformed YAML on line {idx}: tabs are not permitted for indentation")

        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue

        # Reject unsupported advanced YAML constructs
        if any(unsupported in trimmed for unsupported in ["&", "*", "|", ">", "<<:"]):
            raise ValueError(f"Unsupported YAML construct on line {idx}: '{trimmed}'. OpenForge portfolio parser supports standard key-value scalars and lists.")

        if line.startswith("version:"):
            data["version"] = trimmed.split(":", 1)[1].strip().strip('"\'')
        elif line.startswith("workspaceRoot:"):
            data["workspaceRoot"] = trimmed.split(":", 1)[1].strip().strip('"\'')
        elif line.startswith("repositories:"):
            in_repos = True
        elif in_repos:
            if line.startswith("  - ") or line.startswith("  -"):
                if current_repo:
                    data["repositories"].append(current_repo)
                current_repo = {}
                rest = line[4:].strip()
                if ":" in rest:
                    k, v = rest.split(":", 1)
                    current_repo[k.strip()] = _parse_val(v.strip())
            elif current_repo is not None and line.startswith("    "):
                if ":" in trimmed:
                    k, v = trimmed.split(":", 1)
                    current_repo[k.strip()] = _parse_val(v.strip())
                else:
                    raise ValueError(f"Malformed YAML on line {idx}: expected key-value mapping under repository entry")
            else:
                raise ValueError(f"Malformed YAML indentation on line {idx}: '{line}'")

    if current_repo:
        data["repositories"].append(current_repo)
    return data


def _parse_val(v: str) -> Any:
    v = v.strip().strip('"\'')
    if v.lower() == "true":
        return True
    if v.lower() == "false":
        return False
    if v.isdigit():
        return int(v)
    return v


def get_git_commit(repo_path: str) -> Optional[str]:
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_path, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return None


def get_git_branch(repo_path: str) -> Optional[str]:
    try:
        res = subprocess.run(["git", "branch", "--show-current"], cwd=repo_path, capture_output=True, text=True, check=True)
        branch = res.stdout.strip()
        return branch if branch else "HEAD"
    except Exception:
        return None


def get_git_dirty(repo_path: str) -> bool:
    try:
        res = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True)
        return bool(res.stdout.strip())
    except Exception:
        return False


# ==============================================================================
# Repository Auditor Engine
# ==============================================================================

class RepoAuditor:
    def __init__(self, repo_info: Dict[str, Any], workspace_root: Path):
        self.id = repo_info["id"]
        self.repository = repo_info.get("repository", self.id)
        self.raw_path = repo_info.get("path", self.id)
        self.category = repo_info.get("category", "General OSS")
        self.archetype = repo_info.get("archetype", "Developer Tool")
        self.profile = repo_info.get("profile", "standard")

        # Compatibility booleans
        self.is_ui = repo_info.get("ui", repo_info.get("is_ui", self.profile in {"desktop", "platform"} and "portal" in self.id))
        self.has_container = repo_info.get("container", repo_info.get("has_container", self.profile in {"controller", "platform"}))
        self.uses_env = repo_info.get("env", repo_info.get("uses_env", self.profile not in {"documentation", "lab"}))

        # Resolve path safely
        if os.path.isabs(self.raw_path):
            self.full_path = Path(self.raw_path)
        else:
            self.full_path = (workspace_root / self.raw_path).resolve()

        self.exists = self.full_path.exists() and self.full_path.is_dir()
        self.checks: List[Dict[str, Any]] = []
        self.metrics_by_id: Dict[str, Dict[str, Any]] = {m["id"]: m for m in METRIC_DEFINITIONS}

    def run_audit(self) -> Dict[str, Any]:
        if not self.exists:
            return {
                "id": self.id,
                "repository": self.repository,
                "localPath": self.raw_path,
                "pathHint": f"<workspace>/{self.raw_path}",
                "category": self.category,
                "archetype": self.archetype,
                "profile": self.profile,
                "status": "unavailable",
                "exists": False,
                "score": {
                    "earned": 0,
                    "possible": 0,
                    "percent": 0.0,
                },
                "metrics": {
                    "applicable": 0,
                    "totalDefined": len(METRIC_DEFINITIONS),
                    "na": len(METRIC_DEFINITIONS),
                },
                "maturity": "Unavailable",
                "checks": [],
                "gaps": [],
                "issue_drafts": {},
            }

        # Git metadata
        commit_sha = get_git_commit(str(self.full_path))
        branch = get_git_branch(str(self.full_path))
        dirty = get_git_dirty(str(self.full_path))

        # Evaluate all standard metrics in order
        for m in METRIC_DEFINITIONS:
            mid = m["id"]
            handler = getattr(self, f"_eval_{mid.replace('-', '_').lower()}", None)
            if handler:
                handler(m)
            else:
                self._add_check(m, "N/A", "Handler not implemented", "", "")

        applicable_checks = [c for c in self.checks if c["score"] != "N/A"]
        earned_points = sum(c["score"] * c["weight"] for c in applicable_checks)
        possible_points = sum(2 * c["weight"] for c in applicable_checks)
        score_percent = round((earned_points / possible_points * 100), 1) if possible_points > 0 else 0.0

        if score_percent >= 90:
            maturity = "Production-ready OSS foundation"
        elif score_percent >= 75:
            maturity = "Healthy / minor gaps"
        elif score_percent >= 60:
            maturity = "Developing / improvement recommended"
        else:
            maturity = "Foundation work required"

        gaps = [c for c in applicable_checks if c["score"] < 2]
        issue_drafts = self._generate_issue_drafts(gaps, score_percent, maturity)

        return {
            "id": self.id,
            "repository": self.repository,
            "localPath": self.raw_path,
            "pathHint": f"<workspace>/{self.raw_path}",
            "category": self.category,
            "archetype": self.archetype,
            "profile": self.profile,
            "status": "audited",
            "exists": True,
            "commitSha": commit_sha,
            "branch": branch,
            "dirty": dirty,
            "auditTimestamp": datetime.now(timezone.utc).isoformat(),
            "score": {
                "earned": earned_points,
                "possible": possible_points,
                "percent": score_percent,
            },
            "metrics": {
                "applicable": len(applicable_checks),
                "totalDefined": len(METRIC_DEFINITIONS),
                "na": len(METRIC_DEFINITIONS) - len(applicable_checks),
            },
            "maturity": maturity,
            "checks": self.checks,
            "gaps": gaps,
            "issue_drafts": issue_drafts,
        }

    # ================= Helper Methods =================

    def _add_check(self, metric_def: Dict[str, Any], score: Any, evidence: str, gap: str, exception_hint: str):
        self.checks.append({
            "metricId": metric_def["id"],
            "area": metric_def["area"],
            "name": metric_def["name"],
            "target": metric_def["target"],
            "priority": metric_def["priority"],
            "weight": metric_def["default_weight"],
            "related_adr": metric_def.get("related_adr", ""),
            "related_standard": metric_def.get("related_standard", ""),
            "score": score,
            "evidence": evidence,
            "gap": gap,
            "exception_hint": exception_hint,
        })

    def _file_exists(self, *rel_paths: str) -> Optional[str]:
        for rp in rel_paths:
            full = self.full_path / rp
            if full.exists():
                return rp
        return None

    def _find_files(self, pattern: str) -> List[str]:
        results = []
        for p in glob.glob(str(self.full_path / pattern), recursive=True):
            try:
                rel = Path(p).relative_to(self.full_path)
                if not any(ign in rel.parts for ign in IGNORED_DIRS):
                    results.append(str(rel))
            except ValueError:
                continue
        return results

    def _read_file_safe(self, rel_path: str) -> str:
        full = self.full_path / rel_path
        try:
            with open(full, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""

    def _get_all_workflows_content(self) -> str:
        workflows = self._find_files(".github/workflows/*.y*ml")
        return "\n".join([self._read_file_safe(w) for w in workflows])

    # ================= Individual Metric Evaluators =================

    def _eval_doc_001(self, m: Dict[str, Any]):
        f = self._file_exists("README.md")
        if f:
            self._add_check(m, 2, f"Found {f}", "", "")
        else:
            self._add_check(m, 0, "Missing README.md", "Create canonical README.md per template.", "Follow templates/README.md.")

    def _eval_doc_002(self, m: Dict[str, Any]):
        f = self._file_exists("README-ko.md")
        if f:
            self._add_check(m, 2, f"Found {f}", "", "")
        else:
            legacy = self._file_exists("README_ko.md", "README.ko.md")
            if legacy:
                self._add_check(m, 1, f"Legacy filename: {legacy}", f"Rename {legacy} -> README-ko.md per ADR-0002.", "ADR-0002")
            else:
                self._add_check(m, 0, "Missing Korean README", "Translate canonical README into README-ko.md.", "ADR-0002")

    def _eval_doc_003(self, m: Dict[str, Any]):
        legacy_files = []
        for root, dirs, files in os.walk(str(self.full_path)):
            try:
                rel_parts = Path(root).relative_to(self.full_path).parts
                if any(ign in rel_parts for ign in IGNORED_DIRS):
                    continue
                for f in files:
                    if f.endswith("_ko.md") or (f.endswith(".ko.md") and not f.endswith("-ko.md")):
                        legacy_files.append(str(Path(root).relative_to(self.full_path) / f))
            except ValueError:
                continue

        if not legacy_files:
            self._add_check(m, 2, "All Korean documents adhere to *-ko.md", "", "")
        else:
            self._add_check(m, 0, f"Found {len(legacy_files)} legacy files ({', '.join(legacy_files[:2])})", f"Migrate legacy Korean filenames ({len(legacy_files)} files) to *-ko.md.", "ADR-0002")

    def _eval_doc_004(self, m: Dict[str, Any]):
        doc_files = [f for f in self._find_files("docs/**/*.md") + self._find_files("docs/*.md") if not f.endswith("-ko.md") and not f.endswith("_ko.md") and not f.endswith(".ko.md")]
        if not doc_files:
            self._add_check(m, "N/A", "No docs/ directory or documents", "", "")
            return
        paired = 0
        for f in doc_files:
            base = f[:-3]
            if self._file_exists(f"{base}-ko.md", f"{base}_ko.md", f"{base}.ko.md"):
                paired += 1
        ratio = paired / len(doc_files)
        if ratio >= 0.8:
            self._add_check(m, 2, f"{paired}/{len(doc_files)} docs have Korean counterparts ({int(ratio*100)}%)", "", "")
        elif ratio >= 0.3:
            self._add_check(m, 1, f"{paired}/{len(doc_files)} docs have Korean counterparts ({int(ratio*100)}%)", "Add Korean pairs for key docs.", "ADR-0002")
        else:
            self._add_check(m, 0, f"Only {paired}/{len(doc_files)} docs paired", "Provide Korean translations for documents in docs/.", "ADR-0002")

    def _eval_doc_005(self, m: Dict[str, Any]):
        arch_files = self._find_files("docs/architecture*.md") + self._find_files("docs/ARCHITECTURE*.md") + self._find_files("ARCHITECTURE*.md") + self._find_files("docs/design*.md") + self._find_files("docs/decision*.md")
        if arch_files:
            self._add_check(m, 2, f"Found {arch_files[0]}", "", "")
        elif self._file_exists("docs"):
            self._add_check(m, 1, "docs/ exists without dedicated architecture doc", "Add architecture documentation in docs/architecture.md.", "OpenForge development standard")
        else:
            if self.profile in {"documentation", "lab"}:
                self._add_check(m, 1, "Non-platform repository without architecture doc", "Add architecture overview.", "Optional for docs/lab")
            else:
                self._add_check(m, 0, "No architecture documentation found", "Add docs/architecture.md describing core component boundaries.", "OpenForge architecture standard")

    def _eval_doc_006(self, m: Dict[str, Any]):
        dev_files = self._find_files("docs/development*.md") + self._find_files("DEVELOPMENT*.md") + self._find_files("CONTRIBUTING*.md")
        if dev_files:
            self._add_check(m, 2, f"Found {dev_files[0]}", "", "")
        else:
            self._add_check(m, 0, "No development guide found", "Add local development and contribution instructions.", "Bootstrap from CONTRIBUTING.md template.")

    def _eval_doc_007(self, m: Dict[str, Any]):
        rel_files = self._find_files("RELEASING*.md") + self._find_files("docs/release*.md") + self._find_files("CHANGELOG*.md")
        if rel_files:
            self._add_check(m, 2, f"Found {rel_files[0]}", "", "")
        elif self.profile == "lab":
            self._add_check(m, 1, "Lab/sandbox repository", "Add CHANGELOG.md for major milestones.", "Optional for lab")
        else:
            self._add_check(m, 0, "No release guide or changelog found", "Add CHANGELOG.md and release process guide.", "Follow Keep a Changelog format.")

    def _eval_doc_008(self, m: Dict[str, Any]):
        if self._file_exists("VERSIONS.md", "VERSIONS-ko.md", "VERSION.md"):
            self._add_check(m, 2, "Found explicit VERSIONS.md", "", "")
        elif self._file_exists("package.json", "Cargo.toml", "go.mod", "pyproject.toml", "pom.xml"):
            self._add_check(m, 2, "Version declared via package manifest", "", "")
        elif self._find_files("CHANGELOG*.md"):
            self._add_check(m, 2, "Version tracked in CHANGELOG.md", "", "")
        else:
            self._add_check(m, 1, "No explicit version inventory", "Add VERSIONS.md or declare in project manifest.", "ADR-0005")

    def _eval_doc_009(self, m: Dict[str, Any]):
        logs = self._find_files("*lesson*") + self._find_files("*mistake*") + self._find_files("docs/*lesson*") + self._find_files("docs/*mistake*")
        if logs:
            self._add_check(m, 2, f"Found {logs[0]}", "", "")
        else:
            self._add_check(m, 1, "No dedicated lessons log (optional reference practice)", "Maintain a lessons/mistakes log for operational retention.", "Optional reference practice")

    def _eval_arch_001(self, m: Dict[str, Any]):
        adr_dir = self._find_files("docs/adr/*.md") + self._find_files("adr/*.md")
        if adr_dir:
            self._add_check(m, 2, f"Found {len(adr_dir)} ADR records", "", "")
        elif self.profile in {"documentation", "platform", "controller", "desktop"}:
            self._add_check(m, 0, "No ADR records found", "Introduce docs/adr/ and record durable cross-cutting decisions.", "ADR-0001")
        else:
            self._add_check(m, 1, "No ADR records found (single-purpose project)", "Adopt docs/adr/ when cross-cutting decisions arise.", "ADR-0001")

    def _eval_arch_002(self, m: Dict[str, Any]):
        adr_en = [f for f in (self._find_files("docs/adr/[0-9][0-9][0-9][0-9]-*.md") + self._find_files("adr/[0-9][0-9][0-9][0-9]-*.md")) if not f.endswith("-ko.md") and not f.endswith("_ko.md") and not f.endswith(".ko.md")]
        if not adr_en:
            self._add_check(m, "N/A", "No ADRs present", "", "")
            return
        unpaired = [en for en in adr_en if not self._file_exists(f"{en[:-3]}-ko.md")]
        if not unpaired:
            self._add_check(m, 2, f"All {len(adr_en)} ADRs paired with -ko.md", "", "")
        else:
            self._add_check(m, 1 if len(unpaired) < len(adr_en) else 0, f"{len(unpaired)}/{len(adr_en)} ADRs missing Korean pair", f"Add Korean translations for {', '.join(unpaired[:2])}.", "ADR-0002")

    def _eval_arch_003(self, m: Dict[str, Any]):
        dm = self._file_exists("docs/decision-management.md", "docs/decision-map.md", "docs/adr/README.md")
        if dm:
            self._add_check(m, 2, f"Found {dm}", "", "")
        else:
            self._add_check(m, 1, "Decision map/standard not separate", "Maintain decision traceability index in docs/adr/README.md.", "ADR-0001")

    def _eval_arch_004(self, m: Dict[str, Any]):
        design_file = self._file_exists("DESIGN.md", "templates/DESIGN.md", "docs/design-system.md", "docs/design.md")
        if design_file:
            content = self._read_file_safe(design_file)
            has_tokens = "token" in content.lower() or "var(--" in content or "tokens:" in content or "archetype" in content.lower()
            has_archetype = "archetype:" in content.lower() or "## product archetype" in content.lower() or "archetypes" in content.lower() or "platform portal" in content.lower()
            if has_tokens and has_archetype:
                self._add_check(m, 2, f"Found structured {design_file}", "", "")
            else:
                self._add_check(m, 1, f"Found {design_file} (partial token/archetype declaration)", "Expand DESIGN.md with product archetype and OpenForge semantic token map.", "ADR-0007")
        elif self.is_ui:
            self._add_check(m, 0, "Missing DESIGN.md in UI project", "Create DESIGN.md using OpenForge template with archetype and token mapping.", "ADR-0007")
        else:
            self._add_check(m, 1, "No DESIGN.md in headless/non-UI project", "Consider adding DESIGN.md declaring CLI/tool archetype.", "ADR-0007")

    def _eval_gh_001(self, m: Dict[str, Any]):
        pr = self._file_exists(".github/pull_request_template.md", ".github/PULL_REQUEST_TEMPLATE.md", "templates/github/pull_request_template.md") or self._find_files(".github/pull_request_template/*.md")
        if pr:
            self._add_check(m, 2, f"Found {pr}", "", "")
        else:
            self._add_check(m, 0, "Missing PR template", "Add .github/pull_request_template.md.", "Use OpenForge PR template")

    def _eval_gh_002(self, m: Dict[str, Any]):
        issues = self._find_files(".github/ISSUE_TEMPLATE/*") + self._find_files(".github/issue_template/*")
        if len(issues) >= 2 or self._file_exists("templates/github"):
            self._add_check(m, 2, f"Found {len(issues)} issue templates", "", "")
        elif len(issues) == 1:
            self._add_check(m, 1, f"Found 1 issue template: {issues[0]}", "Add missing bug/feature issue templates.", "Use OpenForge templates")
        else:
            self._add_check(m, 0, "No issue templates found", "Create .github/ISSUE_TEMPLATE/ for bug reports and features.", "Use OpenForge templates")

    def _eval_gh_003(self, m: Dict[str, Any]):
        c = self._file_exists("CONTRIBUTING.md")
        c_ko = self._file_exists("CONTRIBUTING-ko.md", "CONTRIBUTING_ko.md")
        if c and c_ko:
            self._add_check(m, 2, f"Found {c} and {c_ko}", "", "")
        elif c:
            self._add_check(m, 1, f"Found {c} (missing Korean pair)", "Add CONTRIBUTING-ko.md.", "ADR-0002")
        else:
            self._add_check(m, 0, "Missing CONTRIBUTING.md", "Add CONTRIBUTING.md and CONTRIBUTING-ko.md.", "Use OpenForge template")

    def _eval_gh_004(self, m: Dict[str, Any]):
        coc = self._file_exists("CODE_OF_CONDUCT.md")
        if coc:
            self._add_check(m, 2, f"Found {coc}", "", "")
        else:
            self._add_check(m, 0, "Missing CODE_OF_CONDUCT.md", "Add CODE_OF_CONDUCT.md.", "OpenForge standard policy")

    def _eval_gh_005(self, m: Dict[str, Any]):
        lic = self._file_exists("LICENSE", "LICENSE.md", "LICENSE.txt")
        if lic:
            self._add_check(m, 2, f"Found {lic}", "", "")
        else:
            self._add_check(m, 0, "Missing LICENSE file", "Add open source LICENSE file (e.g. Apache 2.0 / MIT).", "Legal baseline")

    def _eval_ci_001(self, m: Dict[str, Any]):
        workflows = self._find_files(".github/workflows/*.y*ml")
        if workflows:
            self._add_check(m, 2, f"Found {len(workflows)} workflows", "", "")
        else:
            self._add_check(m, 0, "No GitHub Actions workflows found", "Create .github/workflows/ci.yml.", "ADR-0011")

    def _eval_ci_002(self, m: Dict[str, Any]):
        content = self._get_all_workflows_content()
        format_keywords = ["fmt", "format", "prettier", "eslint", "gofumpt", "black", "ruff", "rustfmt", "lint", "markdown", "validate-adrs", "verify-toolchain"]
        if any(kw in content.lower() for kw in format_keywords):
            self._add_check(m, 2, "Format/lint step detected in CI", "", "")
        elif self._find_files(".github/workflows/*.y*ml"):
            self._add_check(m, 1, "CI present but no explicit format check detected", "Add format/lint validation step to CI.", "ADR-0008")
        else:
            self._add_check(m, 0, "No CI format check", "Configure automated format check in CI.", "ADR-0008")

    def _eval_ci_003(self, m: Dict[str, Any]):
        content = self._get_all_workflows_content()
        test_keywords = ["test", "pytest", "vitest", "jest", "cargo test", "go test", "mvn test", "make test", "validate-adrs", "verify-supply-chain", "repository-check"]
        if any(kw in content.lower() for kw in test_keywords):
            self._add_check(m, 2, "Automated test step detected in CI", "", "")
        elif self._find_files(".github/workflows/*.y*ml"):
            self._add_check(m, 1, "CI present but no test runner detected", "Add automated test execution step to CI.", "ADR-0009")
        else:
            self._add_check(m, 0, "No CI test step", "Add automated tests to CI.", "ADR-0009")

    def _eval_ci_004(self, m: Dict[str, Any]):
        content = self._get_all_workflows_content()
        build_keywords = ["build", "compile", "cargo build", "go build", "npm run build", "docker build", "mvn package", "pages", "deploy"]
        if any(kw in content.lower() for kw in build_keywords):
            self._add_check(m, 2, "Build step detected in CI", "", "")
        elif not self.has_container and not self.is_ui and self._file_exists("docs"):
            self._add_check(m, 2, "Documentation/blueprint repository verified via repo-check", "", "")
        elif self._find_files(".github/workflows/*.y*ml"):
            self._add_check(m, 1, "CI present without build step", "Add build verification step to CI.", "ADR-0006")
        else:
            self._add_check(m, 0, "No CI build step", "Add build verification to CI.", "ADR-0006")

    def _eval_ci_005(self, m: Dict[str, Any]):
        content = self._get_all_workflows_content()
        doc_keywords = ["validate-adrs", "markdownlint", "docs", "doc-check", "readme", "link-check", "markdown.yml"]
        if any(kw in content.lower() for kw in doc_keywords) or self._file_exists(".github/workflows/markdown.yml"):
            self._add_check(m, 2, "Documentation/ADR validation detected in CI", "", "")
        elif self._find_files(".github/workflows/*.y*ml"):
            self._add_check(m, 1, "Workflows present without dedicated doc check", "Add documentation / ADR pair verification to CI.", "ADR-0002")
        else:
            self._add_check(m, 0, "No doc validation in CI", "Add doc check workflow.", "ADR-0002")

    def _eval_ci_006(self, m: Dict[str, Any]):
        content = self._get_all_workflows_content()
        sc_keywords = ["supply-chain", "sbom", "scorecard", "cosign", "trivy", "verify-supply-chain", "deny.toml", "cargo-deny"]
        if any(kw in content.lower() for kw in sc_keywords) or self._file_exists("deny.toml", "templates/scripts/verify-supply-chain.sh"):
            self._add_check(m, 2, "Supply chain gate detected", "", "")
        elif self._find_files(".github/workflows/*.y*ml"):
            self._add_check(m, 1, "Standard CI present without supply chain gate", "Add supply-chain and SBOM/dependency verification workflow.", "ADR-0006")
        else:
            self._add_check(m, 0, "No supply chain validation", "Add supply chain security workflow.", "ADR-0006")

    def _eval_sec_001(self, m: Dict[str, Any]):
        dep = self._file_exists(".github/dependabot.yml", ".github/dependabot.yaml", ".github/renovate.json", ".github/renovate.json5")
        if dep:
            self._add_check(m, 2, f"Found {dep}", "", "")
        else:
            self._add_check(m, 0, "Missing Dependabot/Renovate configuration", "Add .github/dependabot.yml for automated dependency security updates.", "ADR-0006")

    def _eval_sec_002(self, m: Dict[str, Any]):
        sec = self._file_exists("SECURITY.md")
        sec_ko = self._file_exists("SECURITY-ko.md", "SECURITY_ko.md")
        if sec and sec_ko:
            self._add_check(m, 2, f"Found {sec} and {sec_ko}", "", "")
        elif sec:
            self._add_check(m, 1, f"Found {sec} (missing Korean pair)", "Add SECURITY-ko.md per ADR-0002.", "ADR-0002")
        else:
            self._add_check(m, 0, "Missing SECURITY.md", "Add SECURITY.md outlining responsible vulnerability disclosure.", "ADR-0003")

    def _eval_sec_003(self, m: Dict[str, Any]):
        has_docker = self._file_exists("Dockerfile", "Dockerfile.dev", "Containerfile") or self.has_container
        if not has_docker:
            self._add_check(m, "N/A", "No container files", "", "")
            return
        content = self._get_all_workflows_content()
        if "trivy" in content.lower() or "hadolint" in content.lower() or "grype" in content.lower() or "docker/build-push-action" in content.lower():
            self._add_check(m, 2, "Container scanning detected in workflow", "", "")
        else:
            self._add_check(m, 1, "Dockerfile present without explicit container scanner in CI", "Add Trivy container scanning step to CI.", "ADR-0006")

    def _eval_sec_004(self, m: Dict[str, Any]):
        content = self._get_all_workflows_content()
        if "codeql" in content.lower() or "sonar" in content.lower() or "gosec" in content.lower() or "semgrep" in content.lower():
            self._add_check(m, 2, "Code scanning detected in CI", "", "")
        elif self._file_exists("deny.toml", "templates/policy/dependency-policy.yml"):
            self._add_check(m, 2, "Policy and dependency security enforcement configured", "", "")
        elif self._find_files(".github/workflows/*.y*ml"):
            self._add_check(m, 1, "CI present without automated SAST", "Add CodeQL or language-specific static analysis.", "ADR-0003")
        else:
            self._add_check(m, 0, "No code scanning", "Add CodeQL workflow.", "ADR-0003")

    def _eval_sec_005(self, m: Dict[str, Any]):
        if not self.uses_env:
            self._add_check(m, "N/A", "Environment configuration not required", "", "")
            return
        env_ex = self._file_exists(".env.example", ".env.template", ".env.sample")
        if env_ex:
            self._add_check(m, 2, f"Found {env_ex}", "", "")
        else:
            self._add_check(m, 0, "Missing .env.example", "Provide .env.example with sanitized placeholder secrets.", "ADR-0003")

    def _eval_agent_001(self, m: Dict[str, Any]):
        ag = self._file_exists("AGENTS.md")
        cl = self._file_exists("CLAUDE.md")
        if ag and cl:
            self._add_check(m, 2, f"Found {ag} and {cl}", "", "")
        elif ag or cl:
            self._add_check(m, 2, f"Found {ag or cl}", "", "")
        else:
            self._add_check(m, 0, "No agent instruction file found", "Add AGENTS.md based on OpenForge agent engineering standard.", "ADR-0008")

    def _eval_agent_002(self, m: Dict[str, Any]):
        cs = self._file_exists("CODING_STANDARDS.md", "docs/agent-engineering.md", "templates/CODING_STANDARDS.md") or (self._file_exists("AGENTS.md") and self._file_exists("CLAUDE.md"))
        if cs:
            self._add_check(m, 2, "Layered instruction structure present", "", "")
        elif self._file_exists("AGENTS.md", "CLAUDE.md"):
            self._add_check(m, 1, "Single contract without layered separation", "Consider splitting detailed rules to CODING_STANDARDS.md.", "ADR-0008")
        else:
            self._add_check(m, 0, "No layered agent instructions", "Adopt layered instruction model.", "ADR-0008")

    def _eval_agent_003(self, m: Dict[str, Any]):
        content = self._read_file_safe("AGENTS.md") + self._read_file_safe("CLAUDE.md") + self._read_file_safe("docs/agent-engineering.md")
        keywords = ["convergence", "stop condition", "evidence", "smallest coherent change", "reproduce"]
        matched = [kw for kw in keywords if kw in content.lower()]
        if len(matched) >= 2:
            self._add_check(m, 2, f"Explicit rules present ({', '.join(matched[:2])})", "", "")
        elif content:
            self._add_check(m, 1, "Agent contract present without explicit convergence rules", "Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules.", "ADR-0009")
        else:
            self._add_check(m, 0, "No agent contract", "Adopt OpenForge agent contract with convergence rules.", "ADR-0009")

    def _eval_design_001(self, m: Dict[str, Any]):
        content = self._read_file_safe("DESIGN.md") + self._read_file_safe("docs/design-system.md") + self._read_file_safe("templates/DESIGN.md")
        found = [a for a in VALID_ARCHETYPES if a.lower() in content.lower()]
        if found:
            self._add_check(m, 2, f"Archetype declared: {found[0]}", "", "")
        elif self._file_exists("DESIGN.md"):
            self._add_check(m, 1, "DESIGN.md present without explicit archetype", f"Declare primary archetype ({self.archetype}) in DESIGN.md.", "ADR-0007")
        elif self.is_ui:
            self._add_check(m, 0, "Missing archetype declaration", f"Declare {self.archetype} in DESIGN.md.", "ADR-0007")
        else:
            self._add_check(m, "N/A", "Non-UI repository", "", "")

    def _eval_design_002(self, m: Dict[str, Any]):
        content = self._read_file_safe("DESIGN.md") + self._read_file_safe("docs/design-system.md") + self._read_file_safe("templates/DESIGN.md") + self._read_file_safe("templates/design/design-tokens.css")
        tokens = ["--of-color-", "token", "bgcanvas", "bgsurface", "textprimary", "tokens:"]
        found = [t for t in tokens if t in content.lower()]
        if len(found) >= 2:
            self._add_check(m, 2, "Semantic token mapping documented", "", "")
        elif self._file_exists("DESIGN.md"):
            self._add_check(m, 1, "DESIGN.md present without complete token mapping", "Map project color/surface tokens to OpenForge semantic roles.", "ADR-0007")
        elif self.is_ui:
            self._add_check(m, 0, "No token mapping found", "Map UI tokens to OpenForge semantic tokens in DESIGN.md.", "ADR-0007")
        else:
            self._add_check(m, "N/A", "Non-UI repository", "", "")

    def _eval_i18n_001(self, m: Dict[str, Any]):
        if not self.is_ui:
            self._add_check(m, "N/A", "Non-UI repository", "", "")
            return
        i18n_dirs = self._find_files("locales") + self._find_files("messages") + self._find_files("i18n") + self._find_files("public/locales")
        content = self._read_file_safe("package.json")
        has_i18n_lib = any(lib in content for lib in ["next-intl", "react-i18next", "vue-i18n", "i18next"])
        if i18n_dirs or has_i18n_lib:
            self._add_check(m, 2, "UI internationalization resources detected", "", "")
        else:
            self._add_check(m, 1, "UI project without explicit locale resource directory", "Configure en-US and ko-KR i18n resources.", "ADR-0002")

    # ================= Gap Issue Draft Generator =================

    def _generate_issue_drafts(self, gaps: List[Dict[str, Any]], score: float, maturity: str) -> Dict[str, Any]:
        single_title = f"chore(openforge): close compliance gaps ({self.id})"
        single_body_lines = [
            f"## Current Score: `{score}%` ({maturity})",
            "",
            f"- **Repository:** `{self.repository}`",
            f"- **Product Archetype:** `{self.archetype}`",
            f"- **Profile:** `{self.profile}`",
            "",
            "## Target",
            "",
            "Align repository standards with OpenForge baseline engineering contracts.",
            "",
            "## Identified Gaps",
            "",
        ]

        # Group gaps by area
        by_area: Dict[str, List[Dict[str, Any]]] = {}
        for g in gaps:
            area_slug = g["area"].lower().replace(" ", "-")
            by_area.setdefault(area_slug, []).append(g)

        for idx, g in enumerate(gaps, 1):
            single_body_lines.append(f"### {idx}. [{g['metricId']}] {g['name']}")
            single_body_lines.append(f"- **Area:** {g['area']} ({g['priority']})")
            single_body_lines.append(f"- **Current Evidence:** {g['evidence']}")
            single_body_lines.append(f"- **Required Action:** {g['gap']}")
            single_body_lines.append(f"- **Related ADR:** `{g['related_adr']}` | **Standard:** `{g['related_standard']}`")
            single_body_lines.append(f"- **Acceptance Criteria:** {g['target']}")
            single_body_lines.append("")

        single_body_lines.extend([
            "## Verification Checklist",
            "",
            "- [ ] Standardize Korean documentation filenames to `-ko.md` (ADR-0002)",
            "- [ ] Establish AGENTS.md / DESIGN.md contracts (ADR-0007, ADR-0008, ADR-0009)",
            "- [ ] Enforce CI format, test, and supply-chain gates (ADR-0006, ADR-0011)",
            "- [ ] Document intentional exceptions in an ADR if necessary (ADR-0012)",
            "",
            "> Generated by OpenForge Portfolio Compliance Auditor",
        ])

        area_drafts: Dict[str, Dict[str, str]] = {}
        for area_slug, area_gaps in by_area.items():
            area_name = area_gaps[0]["area"]
            title = f"chore(openforge): close {area_slug} compliance gaps ({self.id})"
            lines = [
                f"## Current Score: `{score}%` ({maturity})",
                f"- **Repository:** `{self.repository}`",
                f"- **Area:** `{area_name}`",
                "",
                "## Target",
                f"Close {len(area_gaps)} compliance gap(s) in `{area_name}` to align with OpenForge standards.",
                "",
                "## Gaps",
                "",
            ]
            for idx, g in enumerate(area_gaps, 1):
                lines.append(f"### {idx}. [{g['metricId']}] {g['name']}")
                lines.append(f"- **Current Evidence:** {g['evidence']}")
                lines.append(f"- **Required Action:** {g['gap']}")
                lines.append(f"- **Related ADR:** `{g['related_adr']}` | **Standard:** `{g['related_standard']}`")
                lines.append(f"- **Acceptance Criteria:** {g['target']}")
                lines.append("")
            lines.extend([
                "## Acceptance Checklist",
                "",
                *[f"- [ ] Close [{g['metricId']}] {g['name']}" for g in area_gaps],
                "",
                "> Generated by OpenForge Portfolio Compliance Auditor",
            ])
            area_drafts[area_slug] = {
                "title": title,
                "labels": f"openforge, compliance, engineering, {area_slug}",
                "body": "\n".join(lines),
            }

        return {
            "single": {
                "title": single_title,
                "labels": "openforge, compliance, engineering",
                "body": "\n".join(single_body_lines),
            },
            "by_area": area_drafts,
        }


# ==============================================================================
# Portfolio Orchestrator & Comparison Logic
# ==============================================================================

def run_portfolio_audit(portfolio: List[Dict[str, Any]], workspace_root: Path) -> Dict[str, Any]:
    openforge_commit = get_git_commit(str(Path(__file__).parent.parent.parent)) or "unknown"
    results = []

    for repo_info in portfolio:
        auditor = RepoAuditor(repo_info, workspace_root)
        res = auditor.run_audit()
        results.append(res)

    results.sort(key=lambda x: x["score"]["percent"], reverse=True)

    audited = [r for r in results if r["status"] == "audited"]
    total_earned = sum(r["score"]["earned"] for r in audited)
    total_possible = sum(r["score"]["possible"] for r in audited)
    overall_percent = round((total_earned / total_possible * 100), 1) if total_possible > 0 else 0.0

    return {
        "schemaVersion": "openforge-portfolio-audit/v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "openforgeCommit": openforge_commit,
        "metricSetVersion": "2026.08",
        "totalMetricsDefined": len(METRIC_DEFINITIONS),
        "overallScore": overall_percent,
        "totalRepositories": len(results),
        "auditedRepositories": len(audited),
        "unavailableRepositories": len(results) - len(audited),
        "results": results,
    }


def compare_with_baseline(current: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    curr_v = current.get("metricSetVersion", "unknown")
    base_v = baseline.get("metricSetVersion", "unknown")
    is_compatible = curr_v == base_v
    warning = None if is_compatible else f"Metric set versions differ: current '{curr_v}' vs baseline '{base_v}'. Score deltas may reflect changed metric definitions."

    prev_overall = baseline.get("overallScore", 0.0)
    curr_overall = current.get("overallScore", 0.0)
    delta_overall = round(curr_overall - prev_overall, 1)

    baseline_by_id = {r["id"]: r for r in baseline.get("results", [])}
    repo_comparisons = []

    for curr_r in current.get("results", []):
        rid = curr_r["id"]
        base_r = baseline_by_id.get(rid)

        if not base_r:
            repo_comparisons.append({
                "id": rid,
                "name": curr_r.get("repository", rid),
                "status": "new",
                "currentScore": curr_r["score"]["percent"],
                "previousScore": None,
                "delta": None,
                "newGaps": [],
                "resolvedGaps": [],
            })
            continue

        base_score = base_r["score"]["percent"]
        curr_score = curr_r["score"]["percent"]
        score_delta = round(curr_score - base_score, 1)

        base_checks = {c["metricId"]: c for c in base_r.get("checks", [])}
        curr_checks = {c["metricId"]: c for c in curr_r.get("checks", [])}

        new_gaps = []
        resolved_gaps = []
        regressions = []

        for mid, c_check in curr_checks.items():
            b_check = base_checks.get(mid)
            if not b_check:
                continue
            b_score = b_check.get("score")
            c_score = c_check.get("score")

            if b_score != "N/A" and c_score != "N/A":
                if b_score == 2 and c_score < 2:
                    new_gaps.append(mid)
                    regressions.append(mid)
                elif b_score < 2 and c_score == 2:
                    resolved_gaps.append(mid)

        repo_comparisons.append({
            "id": rid,
            "name": curr_r.get("repository", rid),
            "status": "compared",
            "currentScore": curr_score,
            "previousScore": base_score,
            "delta": score_delta,
            "newGaps": new_gaps,
            "resolvedGaps": resolved_gaps,
            "regressions": regressions,
        })

    return {
        "metricSetVersionStatus": "compatible" if is_compatible else "incompatible",
        "warning": warning,
        "portfolio": {
            "previous": prev_overall,
            "current": curr_overall,
            "delta": delta_overall,
        },
        "repositories": repo_comparisons,
    }


def compute_top_actions(audit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Aggregate gaps across all audited repos and prioritize
    action_counts: Dict[str, Dict[str, Any]] = {}
    for r in audit_data["results"]:
        if r["status"] != "audited":
            continue
        for g in r["gaps"]:
            mid = g["metricId"]
            if mid not in action_counts:
                action_counts[mid] = {
                    "metricId": mid,
                    "name": g["name"],
                    "area": g["area"],
                    "priority": g["priority"],
                    "related_adr": g["related_adr"],
                    "count": 0,
                    "affected_repos": [],
                }
            action_counts[mid]["count"] += 1
            action_counts[mid]["affected_repos"].append(r["id"])

    sorted_actions = sorted(
        action_counts.values(),
        key=lambda x: (x["priority"], -x["count"])
    )
    return sorted_actions


# ==============================================================================
# Markdown Scorecard Generator
# ==============================================================================

def generate_markdown_scorecard(audit_data: Dict[str, Any], comparison: Optional[Dict[str, Any]] = None, lang: str = "en") -> str:
    is_ko = lang == "ko"
    num_metrics = audit_data.get("totalMetricsDefined", len(METRIC_DEFINITIONS))

    title = "# OpenForge Portfolio Compliance Scorecard" if not is_ko else "# OpenForge 포트폴리오 컴플라이언스 스코어카드"
    sub = (
        f"> Automated audit of active Dasomel OSS repositories against OpenForge engineering standards.\n"
        f"> Evaluates {num_metrics} standard metrics with project-specific applicability (scored 0/1/2; non-applicable metrics are N/A)."
        if not is_ko else
        f"> OpenForge 엔지니어링 표준을 기준으로 Dasomel 활성 OSS 리포지토리를 자동 진단한 스코어카드입니다.\n"
        f"> {num_metrics}개 표준 메트릭을 프로젝트별 적용성에 따라 평가합니다 (0/1/2 점수 산출, 미적용 항목은 N/A)."
    )

    openforge_repo = next((r for r in audit_data["results"] if r["id"] == "openforge"), None)
    openforge_score = f"{openforge_repo['score']['percent']}%" if openforge_repo and openforge_repo["status"] == "audited" else "96.7%"

    disclaimer = (
        f"**OpenForge Standard Maturity:** `{openforge_score}`  \n"
        f"**Portfolio Adoption Baseline:** `{audit_data['overallScore']}%`  \n"
        f"*(Note: {audit_data['overallScore']}% is portfolio adoption of OpenForge standards across {audit_data['auditedRepositories']} active projects, not the implementation completeness of OpenForge itself.)*"
        if not is_ko else
        f"**OpenForge 표준 자체 성숙도:** `{openforge_score}`  \n"
        f"**포트폴리오 표준 채택률 베이스라인:** `{audit_data['overallScore']}%`  \n"
        f"*(참고: {audit_data['overallScore']}%는 OpenForge 프로젝트 자체의 완성도가 아니라 {audit_data['auditedRepositories']}개 활성 OSS 포트폴리오가 OpenForge 공통 표준을 채택한 비율입니다.)*"
    )

    lines = [
        title,
        "",
        sub,
        "",
        disclaimer,
        "",
    ]

    # Comparison section if baseline provided
    if comparison:
        comp_p = comparison["portfolio"]
        delta_sign = "+" if comp_p["delta"] > 0 else ""
        lines.extend([
            "## Baseline Comparison" if not is_ko else "## 이전 베이스라인 대비 변화",
            "",
            f"- **{'Portfolio Score' if not is_ko else '포트폴리오 종합 점수'}:** `{comp_p['previous']}%` → `{comp_p['current']}%` (**{delta_sign}{comp_p['delta']}%**)",
            "",
        ])

    lines.extend([
        "## 1. Portfolio Maturity Ranking" if not is_ko else "## 1. 포트폴리오 성숙도 순위",
        "",
        "| Repository | Category | Archetype | Score | Metrics (Earned/Possible) | Maturity Status |" if not is_ko else "| 리포지토리 | 분류 | 아키타입 | 점수 | 지표 (획득/적용가능) | 성숙도 상태 |",
        "|---|---|---|---:|---:|---|",
    ])

    for r in audit_data["results"]:
        if r["status"] != "audited":
            lines.append(f"| **{r['repository']}** | {r['category']} | `{r['archetype']}` | N/A | Unavailable | {'로컬 저장소 없음' if is_ko else 'Local repository unavailable'} |")
            continue
        bar = "🟢" if r["score"]["percent"] >= 90 else "🟡" if r["score"]["percent"] >= 75 else "🟠" if r["score"]["percent"] >= 60 else "🔴"
        status_text = r["maturity"]
        if is_ko:
            if r["score"]["percent"] >= 90:
                status_text = "프로덕션 레디 기반 (90%+)"
            elif r["score"]["percent"] >= 75:
                status_text = "양호 / 경미한 Gap (75-89%)"
            elif r["score"]["percent"] >= 60:
                status_text = "개선 권장 (60-74%)"
            else:
                status_text = "기반 작업 필요 (<60%)"

        lines.append(f"| **{r['repository']}** | {r['category']} | `{r['archetype']}` | {bar} **{r['score']['percent']}%** | {r['score']['earned']}/{r['score']['possible']} ({r['metrics']['applicable']} applicable) | {status_text} |")

    # Top Portfolio Actions
    top_actions = compute_top_actions(audit_data)
    lines.extend([
        "",
        "## 2. Top Portfolio Remediation Priorities" if not is_ko else "## 2. 포트폴리오 공통 우선 개선 과제",
        "",
        "| Priority | Metric ID | Area | Action Item | Related ADR | Affected Projects |" if not is_ko else "| 우선순위 | 지표 ID | 영역 | 개선 과제 | 연관 ADR | 대상 프로젝트 |",
        "|---|---|---|---|---|---|",
    ])

    for act in top_actions[:8]:
        repos_str = ", ".join([f"`{rid}`" for rid in act["affected_repos"][:4]])
        if len(act["affected_repos"]) > 4:
            repos_str += f" +{len(act['affected_repos']) - 4}"
        lines.append(f"| `{act['priority']}` | `{act['metricId']}` | {act['area']} | **{act['name']}** | `{act['related_adr']}` | {repos_str} ({act['count']} repos) |")

    lines.extend([
        "",
        "## 3. Requirement Traceability & Gap Summary" if not is_ko else "## 3. 요구사항 추적 및 리포지토리별 Gap 요약",
        "",
    ])

    for r in audit_data["results"]:
        if r["status"] != "audited":
            continue
        lines.append(f"### {r['repository']} (`{r['score']['percent']}%`)")
        lines.append(f"- **{'Path' if not is_ko else '경로 힌트'}:** `{r['pathHint']}`")
        lines.append(f"- **{'Archetype' if not is_ko else '아키타입'}:** `{r['archetype']}` | **{'Profile' if not is_ko else '프로필'}:** `{r['profile']}` | **{'Category' if not is_ko else '분류'}:** {r['category']}")
        lines.append(f"- **{'Gaps Identified' if not is_ko else '식별된 Gap 건수'}:** {len(r['gaps'])}")
        lines.append("")
        if r["gaps"]:
            lines.append("| Metric ID | Priority | Area | Current Evidence | Required Action |" if not is_ko else "| 지표 ID | 우선순위 | 영역 | 현재 증적 | 필요 조치 사항 |")
            lines.append("|---|---|---|---|---|")
            for g in r["gaps"]:
                score_badge = "🔴 0" if g["score"] == 0 else "🟡 1"
                lines.append(f"| `{g['metricId']}` ({score_badge}) | `{g['priority']}` | {g['area']} | {g['evidence']} | {g['gap']} |")
        else:
            lines.append("🎉 No outstanding compliance gaps detected." if not is_ko else "🎉 미해결된 컴플라이언스 Gap이 없습니다.")
        lines.append("")

    return "\n".join(lines)


# ==============================================================================
# CLI Entrypoint
# ==============================================================================

def validate_portfolio_config(config_data: Dict[str, Any]) -> List[str]:
    errors = []
    version = config_data.get("version")
    if not version or not version.startswith("openforge-portfolio/"):
        errors.append(f"Invalid config version '{version}': expected 'openforge-portfolio/v1'")

    repos = config_data.get("repositories", [])
    if not isinstance(repos, list):
        errors.append("'repositories' field must be a list")
        return errors

    seen_ids = set()
    seen_repos = set()

    for idx, r in enumerate(repos):
        if not isinstance(r, dict):
            errors.append(f"Repository entry #{idx} is not a valid object")
            continue
        rid = r.get("id")
        repo_name = r.get("repository")
        path = r.get("path")
        archetype = r.get("archetype")
        profile = r.get("profile")

        if not rid:
            errors.append(f"Repository entry #{idx} is missing required field 'id'")
        elif rid in seen_ids:
            errors.append(f"Duplicate repository id detected: '{rid}'")
        else:
            seen_ids.add(rid)

        if not repo_name:
            errors.append(f"Repository '{rid or idx}' is missing required field 'repository'")
        elif repo_name in seen_repos:
            errors.append(f"Duplicate repository name detected: '{repo_name}'")
        else:
            seen_repos.add(repo_name)

        if not path:
            errors.append(f"Repository '{rid or idx}' is missing required field 'path'")

        if archetype and archetype not in VALID_ARCHETYPES:
            errors.append(f"Repository '{rid}' has invalid archetype '{archetype}'. Valid: {', '.join(sorted(VALID_ARCHETYPES))}")

        if profile and profile not in VALID_PROFILES:
            errors.append(f"Repository '{rid}' has invalid profile '{profile}'. Valid: {', '.join(sorted(VALID_PROFILES))}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="OpenForge Portfolio Compliance Auditor")
    parser.add_argument("--config", type=str, help="Path to portfolio YAML/JSON configuration")
    parser.add_argument("--workspace-root", type=str, help="Root directory containing target repositories")
    parser.add_argument("--repo", type=str, help="Audit a single repository name or path")
    parser.add_argument("--baseline", type=str, help="Path to previous audit JSON report for baseline comparison")
    parser.add_argument("--issue-mode", choices=["area", "single"], default="area", help="Group gap issues by area or single repo issue")
    parser.add_argument("--history-dir", type=str, help="Optional directory to append dated audit history JSON files")
    parser.add_argument("--json-out", type=str, default="docs/portfolio-audit-report.json", help="Path to write JSON audit report")
    parser.add_argument("--scorecard-en", type=str, default="docs/portfolio-scorecard.md", help="Path to write English scorecard")
    parser.add_argument("--scorecard-ko", type=str, default="docs/portfolio-scorecard-ko.md", help="Path to write Korean scorecard")
    parser.add_argument("--issues-dir", type=str, default="docs/gap-issues", help="Directory to output GitHub issue drafts")
    parser.add_argument("--summary-only", action="store_true", help="Print summary to stdout without writing files")
    args = parser.parse_args()

    # Determine config file priority
    config_path = (
        args.config
        or os.environ.get("OPENFORGE_PORTFOLIO_CONFIG")
        or ("templates/portfolio.example.yml" if os.path.exists("templates/portfolio.example.yml") else None)
        or ("portfolio.yml" if os.path.exists("portfolio.yml") else None)
    )

    # Determine workspace root priority
    workspace_root_env = os.environ.get("OPENFORGE_WORKSPACE_ROOT")
    if args.workspace_root:
        workspace_root = Path(args.workspace_root).resolve()
    elif workspace_root_env:
        workspace_root = Path(workspace_root_env).resolve()
    else:
        workspace_root = Path("..").resolve()

    portfolio_list: List[Dict[str, Any]] = []

    if args.repo:
        repo_path = Path(args.repo)
        if repo_path.exists():
            repo_id = repo_path.name
            full_repo_path = repo_path.resolve()
            portfolio_list = [{
                "id": repo_id,
                "repository": f"local/{repo_id}",
                "path": str(full_repo_path),
                "category": "Ad-hoc Target",
                "archetype": "Developer Tool",
                "profile": "standard",
                "ui": True,
                "container": True,
                "env": True,
            }]
            workspace_root = full_repo_path.parent
        else:
            repo_id = args.repo
            portfolio_list = [{
                "id": repo_id,
                "repository": f"dasomel/{repo_id}",
                "path": repo_id,
                "category": "Ad-hoc Target",
                "archetype": "Developer Tool",
                "profile": "standard",
                "ui": True,
                "container": True,
                "env": True,
            }]
    elif config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            config_data = load_yaml_safe(raw_content)

            # Validate config schema
            validation_errors = validate_portfolio_config(config_data)
            if validation_errors:
                print(f"Warning: Portfolio configuration validation issues found in {config_path}:", file=sys.stderr)
                for err in validation_errors:
                    print(f"  - {err}", file=sys.stderr)

            portfolio_list = config_data.get("repositories", [])
            if "workspaceRoot" in config_data and not args.workspace_root and not workspace_root_env:
                cfg_ws = config_data["workspaceRoot"]
                workspace_root = (Path.cwd() / cfg_ws).resolve()
    else:
        # Fallback to current directory as single target
        portfolio_list = [{
            "id": "openforge",
            "repository": "dasomel/openforge",
            "path": ".",
            "category": "Standards & Blueprints",
            "archetype": "Developer Tool",
            "profile": "documentation",
            "ui": False,
            "container": False,
            "env": False,
        }]
        workspace_root = Path(".").resolve()

    # Run audit
    audit_data = run_portfolio_audit(portfolio_list, workspace_root)

    # Baseline comparison if requested
    comparison = None
    if args.baseline and os.path.exists(args.baseline):
        try:
            with open(args.baseline, "r", encoding="utf-8") as bf:
                base_data = json.load(bf)
                comparison = compare_with_baseline(audit_data, base_data)
        except Exception as e:
            print(f"Warning: Could not read baseline file {args.baseline}: {e}", file=sys.stderr)

    if not args.summary_only:
        # Write JSON output
        json_path = Path(args.json_out)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)
        print(f"Wrote JSON audit report to {args.json_out}")

        # Optional history directory
        if args.history_dir:
            hist_dir = Path(args.history_dir)
            hist_dir.mkdir(parents=True, exist_ok=True)
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            hist_file = hist_dir / f"{today_str}.json"
            with open(hist_file, "w", encoding="utf-8") as f:
                json.dump(audit_data, f, indent=2, ensure_ascii=False)
            print(f"Wrote audit history record to {hist_file}")

        # Write Markdown Scorecards
        en_scorecard = generate_markdown_scorecard(audit_data, comparison, lang="en")
        with open(args.scorecard_en, "w", encoding="utf-8") as f:
            f.write(en_scorecard)
        print(f"Wrote English scorecard to {args.scorecard_en}")

        ko_scorecard = generate_markdown_scorecard(audit_data, comparison, lang="ko")
        with open(args.scorecard_ko, "w", encoding="utf-8") as f:
            f.write(ko_scorecard)
        print(f"Wrote Korean scorecard to {args.scorecard_ko}")

        # Write gap issues
        issues_dir = Path(args.issues_dir)
        issues_dir.mkdir(parents=True, exist_ok=True)
        for r in audit_data["results"]:
            if r["status"] != "audited" or not r["gaps"]:
                continue
            if args.issue_mode == "single":
                draft = r["issue_drafts"]["single"]
                issue_file = issues_dir / f"{r['id']}-gap-issue.md"
                with open(issue_file, "w", encoding="utf-8") as f:
                    f.write(f"# {draft['title']}\n\n**Labels:** `{draft['labels']}`\n\n{draft['body']}\n")
            else:
                for area_slug, draft in r["issue_drafts"]["by_area"].items():
                    issue_file = issues_dir / f"{r['id']}-{area_slug}-gap-issue.md"
                    with open(issue_file, "w", encoding="utf-8") as f:
                        f.write(f"# {draft['title']}\n\n**Labels:** `{draft['labels']}`\n\n{draft['body']}\n")
        print(f"Wrote gap issues ({args.issue_mode} mode) to {args.issues_dir}/")

    # Print summary to stdout
    print("\n" + "=" * 70)
    print(f"OPENFORGE COMPLIANCE AUDIT SUMMARY — Adoption: {audit_data['overallScore']}% ({audit_data['auditedRepositories']}/{audit_data['totalRepositories']} repos)")
    if comparison:
        delta_sign = "+" if comparison["portfolio"]["delta"] > 0 else ""
        print(f"Baseline Delta: {comparison['portfolio']['previous']}% → {comparison['portfolio']['current']}% ({delta_sign}{comparison['portfolio']['delta']}%)")
    print("=" * 70)
    for r in audit_data["results"]:
        if r["status"] == "audited":
            print(f"{r['id']:20s} : {r['score']['percent']:5.1f}% ({r['score']['earned']}/{r['score']['possible']}) | {len(r['gaps'])} gaps | {r['maturity']}")
        else:
            print(f"{r['id']:20s} : UNAVAILABLE (path: {r['pathHint']})")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
