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
from pathlib import Path
from typing import Dict, List, Any, Optional

# Default repository paths in the Dasomel portfolio
DEFAULT_PORTFOLIO = [
    {
        "id": "openforge",
        "name": "OpenForge",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/openforge",
        "category": "Standards & Blueprints",
        "archetype": "Developer Tool",
        "is_ui": False,
        "has_container": False,
        "uses_env": False,
    },
    {
        "id": "narwhal",
        "name": "Narwhal",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/idp/narwhal",
        "category": "Internal Developer Platform",
        "archetype": "Platform Portal",
        "is_ui": False,
        "has_container": True,
        "uses_env": True,
    },
    {
        "id": "narwhal-portal",
        "name": "Narwhal Portal",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/idp/narwhal-portal",
        "category": "Internal Developer Platform",
        "archetype": "Platform Portal",
        "is_ui": True,
        "has_container": True,
        "uses_env": True,
    },
    {
        "id": "clusterdeck",
        "name": "ClusterDeck",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/clusterdeck",
        "category": "Kubernetes Operations",
        "archetype": "Operations Dashboard",
        "is_ui": True,
        "has_container": False,
        "uses_env": True,
    },
    {
        "id": "kubemetal",
        "name": "KubeMetal",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/kubemetal",
        "category": "Apple Silicon Hybrid MLOps",
        "archetype": "Desktop Operator",
        "is_ui": True,
        "has_container": False,
        "uses_env": True,
    },
    {
        "id": "nfs-quota-agent",
        "name": "NFS Quota Agent",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/nfs-quota-agent",
        "category": "Storage & Kubernetes Controllers",
        "archetype": "Developer Tool",
        "is_ui": False,
        "has_container": True,
        "uses_env": True,
    },
    {
        "id": "beluga",
        "name": "Beluga",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/beluga",
        "category": "Data Platform IaC",
        "archetype": "Data Control Plane",
        "is_ui": False,
        "has_container": False,
        "uses_env": True,
    },
    {
        "id": "beluga-manager",
        "name": "Beluga Manager",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/beluga-manager",
        "category": "Data Platform Management",
        "archetype": "Data Control Plane",
        "is_ui": True,
        "has_container": False,
        "uses_env": True,
    },
    {
        "id": "ldapium",
        "name": "ldapium",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/ldapium",
        "category": "Identity & Directory Service",
        "archetype": "Admin Console",
        "is_ui": True,
        "has_container": True,
        "uses_env": True,
    },
    {
        "id": "kube-ready-box",
        "name": "kube-ready-box",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/kube-ready-box",
        "category": "OS & VM Infrastructure",
        "archetype": "Developer Tool",
        "is_ui": False,
        "has_container": False,
        "uses_env": False,
    },
    {
        "id": "cka-lab",
        "name": "cka-lab",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/cka-lab",
        "category": "Certification & Lab Simulator",
        "archetype": "Developer Tool",
        "is_ui": False,
        "has_container": False,
        "uses_env": False,
    },
    {
        "id": "dasomel.github.io",
        "name": "dasomel.github.io",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/dasomel.github.io",
        "category": "Community Tech Blog",
        "archetype": "Platform Portal",
        "is_ui": True,
        "has_container": False,
        "uses_env": True,
    },
    {
        "id": "kairos",
        "name": "Kairos",
        "path": "/Users/m/Documents/IdeaProjects/20.dasomel/kairos",
        "category": "Automated Trading Bot",
        "archetype": "Developer Tool",
        "is_ui": False,
        "has_container": False,
        "uses_env": True,
    },
    {
        "id": "egovframe-launcher",
        "name": "eGovFrame Launcher",
        "path": "/Users/m/Documents/IdeaProjects/21.egov/egovframe-launcher",
        "category": "eGovFrame Developer Tooling",
        "archetype": "Developer Tool",
        "is_ui": True,
        "has_container": False,
        "uses_env": False,
    },
]

IGNORED_DIRS = {".git", "node_modules", "_workspace", ".omc", "dist", "vendor", ".venv", "__pycache__", "build", "target"}


class RepoAuditor:
    def __init__(self, repo_info: Dict[str, Any]):
        self.id = repo_info["id"]
        self.name = repo_info["name"]
        self.path = repo_info["path"]
        self.category = repo_info.get("category", "General OSS")
        self.archetype = repo_info.get("archetype", "Developer Tool")
        self.is_ui = repo_info.get("is_ui", False)
        self.has_container = repo_info.get("has_container", False)
        self.uses_env = repo_info.get("uses_env", False)
        self.exists = os.path.exists(self.path)

        self.checks: List[Dict[str, Any]] = []
        self.total_points = 0
        self.max_points = 0

    def run_audit(self) -> Dict[str, Any]:
        if not self.exists:
            return {
                "id": self.id,
                "name": self.name,
                "path": self.path,
                "category": self.category,
                "archetype": self.archetype,
                "exists": False,
                "score_percent": 0.0,
                "maturity": "Missing",
                "checks": [],
                "gaps": ["Repository path does not exist on disk."],
                "issue_draft": {"title": "Repository not found", "labels": "compliance", "body": "Path not found."},
            }

        # 1. Documentation
        self._check_english_readme()
        self._check_korean_readme()
        self._check_korean_filename_convention()
        self._check_architecture_doc()
        self._check_development_guide()
        self._check_release_guide()
        self._check_version_inventory()
        self._check_lessons_log()

        # 2. Architecture & Decisions
        self._check_adr_process()
        self._check_adr_bilingual_pairs()
        self._check_design_contract()

        # 3. GitHub Standards
        self._check_pr_template()
        self._check_issue_templates()
        self._check_contributing_guide()
        self._check_code_of_conduct()
        self._check_license()

        # 4. CI & Verification
        self._check_automated_ci()
        self._check_ci_format()
        self._check_ci_test()
        self._check_ci_build()
        self._check_ci_doc_validation()
        self._check_ci_supply_chain()

        # 5. Security & Supply Chain
        self._check_dependabot()
        self._check_security_policy()
        self._check_container_scan()
        self._check_code_scanning()
        self._check_env_example()

        # 6. Agent Engineering
        self._check_agent_contract()
        self._check_agent_layered_instructions()
        self._check_agent_convergence_rules()

        # 7. Design System Adoption
        self._check_design_archetype()
        self._check_design_token_mapping()
        self._check_ui_i18n()

        # Calculate final score
        applicable_checks = [c for c in self.checks if c["score"] != "N/A"]
        self.total_points = sum(c["score"] for c in applicable_checks)
        self.max_points = len(applicable_checks) * 2
        score_percent = round((self.total_points / self.max_points * 100), 1) if self.max_points > 0 else 0.0

        if score_percent >= 90:
            maturity = "Production-ready OSS foundation"
        elif score_percent >= 75:
            maturity = "Healthy / minor gaps"
        elif score_percent >= 60:
            maturity = "Developing / improvement recommended"
        else:
            maturity = "Foundation work required"

        gaps = [c for c in applicable_checks if c["score"] < 2]
        issue_draft = self._generate_issue_draft(gaps, score_percent, maturity)

        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "category": self.category,
            "archetype": self.archetype,
            "exists": True,
            "total_points": self.total_points,
            "max_points": self.max_points,
            "score_percent": score_percent,
            "maturity": maturity,
            "checks": self.checks,
            "gaps": gaps,
            "issue_draft": issue_draft,
        }

    def _add_check(self, area: str, metric: str, score: Any, target: str, evidence: str, gap: str, exception_hint: str):
        self.checks.append({
            "area": area,
            "metric": metric,
            "score": score,
            "target": target,
            "evidence": evidence,
            "gap": gap,
            "exception_hint": exception_hint
        })

    def _file_exists(self, *rel_paths: str) -> Optional[str]:
        for rp in rel_paths:
            full = os.path.join(self.path, rp)
            if os.path.exists(full):
                return rp
        return None

    def _find_files(self, pattern: str) -> List[str]:
        results = []
        for p in glob.glob(os.path.join(self.path, pattern), recursive=True):
            parts = Path(p).relative_to(self.path).parts
            if not any(ign in parts for ign in IGNORED_DIRS):
                results.append(os.path.relpath(p, self.path))
        return results

    def _read_file_safe(self, rel_path: str) -> str:
        full = os.path.join(self.path, rel_path)
        try:
            with open(full, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""

    def _get_all_workflows_content(self) -> str:
        workflows = self._find_files(".github/workflows/*.y*ml")
        return "\n".join([self._read_file_safe(w) for w in workflows])

    # ================= Check Implementations =================

    def _check_english_readme(self):
        f = self._file_exists("README.md")
        if f:
            self._add_check("Documentation", "English README", 2, "README.md present", f"Found {f}", "", "")
        else:
            self._add_check("Documentation", "English README", 0, "README.md present", "Missing README.md", "README.md is missing.", "Create canonical README.md per template.")

    def _check_korean_readme(self):
        f = self._file_exists("README-ko.md")
        if f:
            self._add_check("Documentation", "Korean README", 2, "README-ko.md present", f"Found {f}", "", "")
        else:
            legacy = self._file_exists("README_ko.md", "README.ko.md")
            if legacy:
                self._add_check("Documentation", "Korean README", 1, "README-ko.md present", f"Legacy filename: {legacy}", f"Rename {legacy} -> README-ko.md per ADR-0002.", "ADR-0002 / rename to -ko.md")
            else:
                self._add_check("Documentation", "Korean README", 0, "README-ko.md present", "Missing Korean README", "README-ko.md is missing.", "Translate canonical README into README-ko.md.")

    def _check_korean_filename_convention(self):
        legacy_files = []
        for root, dirs, files in os.walk(self.path):
            parts = Path(root).relative_to(self.path).parts
            if any(ign in parts for ign in IGNORED_DIRS):
                continue
            for f in files:
                if f.endswith("_ko.md") or (f.endswith(".ko.md") and not f.endswith("-ko.md")):
                    legacy_files.append(os.path.relpath(os.path.join(root, f), self.path))
        if not legacy_files:
            self._add_check("Documentation", "Korean Filename Standard", 2, "Use <name>-ko.md format", "All Korean docs adhere to *-ko.md", "", "")
        else:
            self._add_check("Documentation", "Korean Filename Standard", 0, "Use <name>-ko.md format", f"Found {len(legacy_files)} legacy files ({', '.join(legacy_files[:2])})", f"Migrate legacy Korean filenames ({len(legacy_files)} files) to *-ko.md.", "ADR-0002 naming standard")

    def _check_architecture_doc(self):
        arch_files = self._find_files("docs/architecture*.md") + self._find_files("docs/ARCHITECTURE*.md") + self._find_files("ARCHITECTURE*.md") + self._find_files("docs/design*.md") + self._find_files("docs/decision*.md")
        if arch_files:
            self._add_check("Documentation", "Architecture Document", 2, "docs/architecture*.md", f"Found {arch_files[0]}", "", "")
        elif self._file_exists("docs"):
            self._add_check("Documentation", "Architecture Document", 1, "docs/architecture*.md", "docs/ directory exists without dedicated architecture doc", "Add architecture documentation in docs/architecture.md.", "Document core architecture boundaries.")
        else:
            self._add_check("Documentation", "Architecture Document", 0, "docs/architecture*.md", "No architecture documentation", "Add architecture overview and diagram.", "Required for platform & operator archetypes.")

    def _check_development_guide(self):
        dev_files = self._find_files("docs/development*.md") + self._find_files("DEVELOPMENT*.md") + self._find_files("CONTRIBUTING*.md")
        if dev_files:
            self._add_check("Documentation", "Development Guide", 2, "docs/development.md / CONTRIBUTING.md", f"Found {dev_files[0]}", "", "")
        else:
            self._add_check("Documentation", "Development Guide", 0, "docs/development.md / CONTRIBUTING.md", "No development guide found", "Add local development and contribution instructions.", "Bootstrap from OpenForge CONTRIBUTING.md template.")

    def _check_release_guide(self):
        rel_files = self._find_files("RELEASING*.md") + self._find_files("docs/release*.md") + self._find_files("CHANGELOG*.md")
        if rel_files:
            self._add_check("Documentation", "Release Guide & Changelog", 2, "RELEASING.md / CHANGELOG.md", f"Found {rel_files[0]}", "", "")
        else:
            self._add_check("Documentation", "Release Guide & Changelog", 0, "RELEASING.md / CHANGELOG.md", "No release guide or changelog found", "Add CHANGELOG.md and release process guide.", "Follow Keep a Changelog format.")

    def _check_version_inventory(self):
        if self._file_exists("VERSIONS.md", "VERSIONS-ko.md", "VERSION.md"):
            self._add_check("Documentation", "Version Inventory", 2, "VERSIONS.md / manifest", "Found explicit VERSIONS.md", "", "")
        elif self._file_exists("package.json", "Cargo.toml", "go.mod", "pyproject.toml", "pom.xml"):
            self._add_check("Documentation", "Version Inventory", 2, "VERSIONS.md / manifest", "Version declared via project manifest", "", "")
        elif self._find_files("CHANGELOG*.md"):
            self._add_check("Documentation", "Version Inventory", 2, "VERSIONS.md / manifest", "Version tracked in CHANGELOG", "", "")
        else:
            self._add_check("Documentation", "Version Inventory", 1, "VERSIONS.md / manifest", "No explicit version file", "Add version inventory.", "N/A for minimal prototypes.")

    def _check_lessons_log(self):
        logs = self._find_files("*lesson*") + self._find_files("*mistake*") + self._find_files("docs/*lesson*") + self._find_files("docs/*mistake*")
        if logs:
            self._add_check("Documentation", "Lessons & Mistakes Log", 2, "lessons-log.md / mistakes-log.md", f"Found {logs[0]}", "", "")
        else:
            self._add_check("Documentation", "Lessons & Mistakes Log", 1, "lessons-log.md / mistakes-log.md", "No dedicated lessons log (optional)", "Maintain a lessons/mistakes log for operational retention.", "Optional reference practice.")

    def _check_adr_process(self):
        adr_dir = self._find_files("docs/adr/*.md") + self._find_files("adr/*.md")
        if adr_dir:
            self._add_check("Architecture", "ADR Process", 2, "docs/adr/ directory with records", f"Found {len(adr_dir)} ADR records", "", "")
        else:
            self._add_check("Architecture", "ADR Process", 0, "docs/adr/ directory with records", "No ADR records found", "Introduce docs/adr/ and record durable cross-cutting decisions.", "ADR-0001 adoption.")

    def _check_adr_bilingual_pairs(self):
        adr_en = [f for f in (self._find_files("docs/adr/[0-9][0-9][0-9][0-9]-*.md") + self._find_files("adr/[0-9][0-9][0-9][0-9]-*.md")) if not f.endswith("-ko.md") and not f.endswith("_ko.md") and not f.endswith(".ko.md")]
        if not adr_en:
            self._add_check("Architecture", "ADR Bilingual Pairs", "N/A", "100% paired ADRs", "No ADRs present", "", "")
            return

        unpaired = []
        for en in adr_en:
            base = en[:-3]
            ko = f"{base}-ko.md"
            if not self._file_exists(ko):
                unpaired.append(en)

        if not unpaired:
            self._add_check("Architecture", "ADR Bilingual Pairs", 2, "100% paired ADRs", f"All {len(adr_en)} ADRs paired with -ko.md", "", "")
        else:
            self._add_check("Architecture", "ADR Bilingual Pairs", 1 if len(unpaired) < len(adr_en) else 0, "100% paired ADRs", f"{len(unpaired)}/{len(adr_en)} ADRs missing Korean pair", f"Add Korean translations for {', '.join(unpaired[:3])}.", "ADR-0002 bilingual parity.")

    def _check_design_contract(self):
        design_file = self._file_exists("DESIGN.md", "docs/design-system.md", "docs/design.md", "templates/DESIGN.md")
        if design_file:
            content = self._read_file_safe(design_file)
            has_tokens = "token" in content.lower() or "var(--" in content
            has_archetype = "archetype" in content.lower()
            if has_tokens and has_archetype:
                self._add_check("Architecture", "DESIGN.md Contract", 2, "DESIGN.md with archetype & tokens", f"Found comprehensive {design_file}", "", "")
            else:
                self._add_check("Architecture", "DESIGN.md Contract", 1, "DESIGN.md with archetype & tokens", f"Found {design_file} (partial token/archetype declaration)", "Expand DESIGN.md with product archetype and OpenForge semantic token map.", "ADR-0007 adoption.")
        else:
            if self.is_ui:
                self._add_check("Architecture", "DESIGN.md Contract", 0, "DESIGN.md with archetype & tokens", "Missing DESIGN.md in UI project", "Create DESIGN.md using OpenForge template with archetype and token mapping.", "ADR-0007 required for UI.")
            else:
                self._add_check("Architecture", "DESIGN.md Contract", 1, "DESIGN.md with archetype & tokens", "No DESIGN.md in non-UI project", "Consider adding DESIGN.md declaring CLI/tool archetype.", "ADR-0007 optional for headless tools.")

    def _check_pr_template(self):
        pr = self._file_exists(".github/pull_request_template.md", ".github/PULL_REQUEST_TEMPLATE.md", "templates/github/pull_request_template.md") or self._find_files(".github/pull_request_template/*.md")
        if pr:
            self._add_check("GitHub", "PR Template", 2, ".github/pull_request_template.md", f"Found {pr}", "", "")
        else:
            self._add_check("GitHub", "PR Template", 0, ".github/pull_request_template.md", "Missing PR template", "Add .github/pull_request_template.md.", "Use OpenForge PR template baseline.")

    def _check_issue_templates(self):
        issues = self._find_files(".github/ISSUE_TEMPLATE/*") + self._find_files(".github/issue_template/*")
        if len(issues) >= 2:
            self._add_check("GitHub", "Issue Templates", 2, "Bug & Feature issue templates", f"Found {len(issues)} templates", "", "")
        elif len(issues) == 1:
            self._add_check("GitHub", "Issue Templates", 1, "Bug & Feature issue templates", f"Found 1 template: {issues[0]}", "Add missing bug/feature templates.", "Add standard issue forms.")
        elif self._file_exists("templates/github"):
            self._add_check("GitHub", "Issue Templates", 2, "Bug & Feature issue templates", "Issue template catalog provided in templates/github", "", "")
        else:
            self._add_check("GitHub", "Issue Templates", 0, "Bug & Feature issue templates", "No issue templates found", "Create .github/ISSUE_TEMPLATE/ for bug reports and features.", "Use OpenForge templates.")

    def _check_contributing_guide(self):
        c = self._file_exists("CONTRIBUTING.md")
        c_ko = self._file_exists("CONTRIBUTING-ko.md", "CONTRIBUTING_ko.md")
        if c and c_ko:
            self._add_check("GitHub", "Contributing Guide (en+ko)", 2, "CONTRIBUTING.md + CONTRIBUTING-ko.md", f"Found {c} and {c_ko}", "", "")
        elif c:
            self._add_check("GitHub", "Contributing Guide (en+ko)", 1, "CONTRIBUTING.md + CONTRIBUTING-ko.md", f"Found {c} (missing Korean pair)", "Add CONTRIBUTING-ko.md.", "ADR-0002 bilingual guidance.")
        else:
            self._add_check("GitHub", "Contributing Guide (en+ko)", 0, "CONTRIBUTING.md + CONTRIBUTING-ko.md", "Missing CONTRIBUTING.md", "Add CONTRIBUTING.md and CONTRIBUTING-ko.md.", "Use OpenForge template.")

    def _check_code_of_conduct(self):
        coc = self._file_exists("CODE_OF_CONDUCT.md")
        if coc:
            self._add_check("GitHub", "Code of Conduct", 2, "CODE_OF_CONDUCT.md", f"Found {coc}", "", "")
        else:
            self._add_check("GitHub", "Code of Conduct", 0, "CODE_OF_CONDUCT.md", "Missing CODE_OF_CONDUCT.md", "Add CODE_OF_CONDUCT.md.", "OpenForge standard policy.")

    def _check_license(self):
        lic = self._file_exists("LICENSE", "LICENSE.md", "LICENSE.txt")
        if lic:
            self._add_check("GitHub", "License", 2, "LICENSE file present", f"Found {lic}", "", "")
        else:
            self._add_check("GitHub", "License", 0, "LICENSE file present", "Missing LICENSE file", "Add open source LICENSE file (e.g. Apache 2.0 / MIT).", "Legal baseline.")

    def _check_automated_ci(self):
        workflows = self._find_files(".github/workflows/*.y*ml")
        if workflows:
            self._add_check("CI", "Automated CI Workflows", 2, ".github/workflows/*.yml", f"Found {len(workflows)} workflows ({', '.join([os.path.basename(w) for w in workflows[:3]])})", "", "")
        else:
            self._add_check("CI", "Automated CI Workflows", 0, ".github/workflows/*.yml", "No GitHub Actions workflows found", "Create .github/workflows/ci.yml.", "Core engineering standard.")

    def _check_ci_format(self):
        content = self._get_all_workflows_content()
        format_keywords = ["fmt", "format", "prettier", "eslint", "gofumpt", "black", "ruff", "rustfmt", "lint", "markdownlint", "verify-toolchain"]
        if any(kw in content.lower() for kw in format_keywords):
            self._add_check("CI", "Format & Lint Check in CI", 2, "Automated format/lint step", "Format/lint step detected in CI", "", "")
        elif self._find_files(".github/workflows/*.y*ml"):
            self._add_check("CI", "Format & Lint Check in CI", 1, "Automated format/lint step", "CI present but no explicit format check detected", "Add format/lint validation step to CI.", "Deterministic rule enforcement.")
        else:
            self._add_check("CI", "Format & Lint Check in CI", 0, "Automated format/lint step", "No CI format check", "Configure automated format check in CI.", "Required for reproducible quality.")

    def _check_ci_test(self):
        content = self._get_all_workflows_content()
        test_keywords = ["test", "pytest", "vitest", "jest", "cargo test", "go test", "mvn test", "make test", "validate-adrs", "verify-supply-chain", "repository-check"]
        if any(kw in content.lower() for kw in test_keywords):
            self._add_check("CI", "Automated Tests in CI", 2, "Automated test execution in CI", "Automated test step detected in CI", "", "")
        elif self._find_files(".github/workflows/*.y*ml"):
            self._add_check("CI", "Automated Tests in CI", 1, "Automated test execution in CI", "CI present but no test runner detected", "Add automated test execution step to CI.", "Verification before completion.")
        else:
            self._add_check("CI", "Automated Tests in CI", 0, "Automated test execution in CI", "No CI test step", "Add automated tests to CI.", "Required for regression prevention.")

    def _check_ci_build(self):
        content = self._get_all_workflows_content()
        build_keywords = ["build", "compile", "cargo build", "go build", "npm run build", "docker build", "mvn package", "pages", "deploy"]
        if any(kw in content.lower() for kw in build_keywords):
            self._add_check("CI", "Automated Build in CI", 2, "Build validation step in CI", "Build step detected in CI", "", "")
        elif not self.has_container and not self.is_ui and self._file_exists("docs"):
            # Pure docs / standards repo
            self._add_check("CI", "Automated Build in CI", 2, "Build validation step in CI", "Docs/blueprint repository verified via repo-check", "", "")
        elif self._find_files(".github/workflows/*.y*ml"):
            self._add_check("CI", "Automated Build in CI", 1, "Build validation step in CI", "CI present without build step", "Add build verification step to CI.", "Ensure artifact compilation succeeds.")
        else:
            self._add_check("CI", "Automated Build in CI", 0, "Build validation step in CI", "No CI build step", "Add build verification to CI.", "Prevent broken builds.")

    def _check_ci_doc_validation(self):
        content = self._get_all_workflows_content()
        doc_keywords = ["validate-adrs", "markdownlint", "docs", "doc-check", "readme", "link-check", "markdown.yml"]
        if any(kw in content.lower() for kw in doc_keywords) or self._file_exists(".github/workflows/markdown.yml"):
            self._add_check("CI", "Documentation & ADR Validation", 2, "Doc/ADR validation step in CI", "Documentation/ADR validation detected in CI", "", "")
        elif self._find_files(".github/workflows/*.y*ml"):
            self._add_check("CI", "Documentation & ADR Validation", 1, "Doc/ADR validation step in CI", "Workflows present without dedicated doc check", "Add documentation / ADR pair verification to CI.", "Prevent doc drift.")
        else:
            self._add_check("CI", "Documentation & ADR Validation", 0, "Doc/ADR validation step in CI", "No doc validation in CI", "Add doc check workflow.", "Recommended baseline.")

    def _check_ci_supply_chain(self):
        content = self._get_all_workflows_content()
        sc_keywords = ["supply-chain", "sbom", "scorecard", "cosign", "trivy", "verify-supply-chain", "deny.toml", "cargo-deny"]
        if any(kw in content.lower() for kw in sc_keywords) or self._file_exists("deny.toml", "templates/scripts/verify-supply-chain.sh"):
            self._add_check("CI", "Supply Chain & Security Gates", 2, "Supply chain / SBOM / Policy gate in CI", "Supply chain gate detected", "", "")
        elif self._find_files(".github/workflows/*.y*ml"):
            self._add_check("CI", "Supply Chain & Security Gates", 1, "Supply chain / SBOM / Policy gate in CI", "Standard CI present without supply chain gate", "Add supply-chain and SBOM/dependency verification workflow.", "ADR-0006 compliance.")
        else:
            self._add_check("CI", "Supply Chain & Security Gates", 0, "Supply chain / SBOM / Policy gate in CI", "No supply chain validation", "Add supply chain security workflow.", "Required for secure releases.")

    def _check_dependabot(self):
        dep = self._file_exists(".github/dependabot.yml", ".github/dependabot.yaml", ".github/renovate.json", ".github/renovate.json5")
        if dep:
            self._add_check("Security", "Dependency Update Automation", 2, "Dependabot/Renovate config", f"Found {dep}", "", "")
        else:
            self._add_check("Security", "Dependency Update Automation", 0, "Dependabot/Renovate config", "Missing Dependabot/Renovate configuration", "Add .github/dependabot.yml for automated dependency security updates.", "Continuous vulnerability management.")

    def _check_security_policy(self):
        sec = self._file_exists("SECURITY.md")
        sec_ko = self._file_exists("SECURITY-ko.md", "SECURITY_ko.md")
        if sec and sec_ko:
            self._add_check("Security", "SECURITY Policy (en+ko)", 2, "SECURITY.md + SECURITY-ko.md", f"Found {sec} and {sec_ko}", "", "")
        elif sec:
            self._add_check("Security", "SECURITY Policy (en+ko)", 1, "SECURITY.md + SECURITY-ko.md", f"Found {sec} (missing Korean pair)", "Add SECURITY-ko.md per ADR-0002.", "Vulnerability disclosure path.")
        else:
            self._add_check("Security", "SECURITY Policy (en+ko)", 0, "SECURITY.md + SECURITY-ko.md", "Missing SECURITY.md", "Add SECURITY.md outlining responsible vulnerability disclosure.", "OpenForge security standard.")

    def _check_container_scan(self):
        has_docker = self._file_exists("Dockerfile", "Dockerfile.dev", "Containerfile") or self.has_container
        if not has_docker:
            self._add_check("Security", "Container Security Scan", "N/A", "Trivy / Hadolint in CI", "No container files", "", "")
            return
        content = self._get_all_workflows_content()
        if "trivy" in content.lower() or "hadolint" in content.lower() or "grype" in content.lower() or "docker/build-push-action" in content.lower():
            self._add_check("Security", "Container Security Scan", 2, "Trivy / Hadolint in CI", "Container scanning detected in workflow", "", "")
        else:
            self._add_check("Security", "Container Security Scan", 1, "Trivy / Hadolint in CI", "Dockerfile present without explicit container scanner in CI", "Add Trivy container scanning step to CI.", "Container security standard.")

    def _check_code_scanning(self):
        content = self._get_all_workflows_content()
        if "codeql" in content.lower() or "sonar" in content.lower() or "gosec" in content.lower() or "semgrep" in content.lower():
            self._add_check("Security", "Code Scanning / SAST", 2, "CodeQL or SAST in CI", "Code scanning detected in CI", "", "")
        elif self._file_exists("deny.toml", "templates/policy/dependency-policy.yml"):
            self._add_check("Security", "Code Scanning / SAST", 2, "CodeQL or SAST in CI", "Policy and dependency security enforcement configured", "", "")
        elif self._find_files(".github/workflows/*.y*ml"):
            self._add_check("Security", "Code Scanning / SAST", 1, "CodeQL or SAST in CI", "CI present without automated SAST", "Add CodeQL or language-specific static analysis.", "Recommended public OSS practice.")
        else:
            self._add_check("Security", "Code Scanning / SAST", 0, "CodeQL or SAST in CI", "No code scanning", "Add CodeQL workflow.", "Static vulnerability prevention.")

    def _check_env_example(self):
        if not self.uses_env:
            self._add_check("Security", ".env.example Template", "N/A", ".env.example for configuration", "Environment configuration not required", "", "")
            return
        env_ex = self._file_exists(".env.example", ".env.template", ".env.sample")
        if env_ex:
            self._add_check("Security", ".env.example Template", 2, ".env.example present", f"Found {env_ex}", "", "")
        else:
            self._add_check("Security", ".env.example Template", 0, ".env.example present", "Missing .env.example", "Provide .env.example with sanitized placeholder secrets.", "Prevent accidental credential exposure.")

    def _check_agent_contract(self):
        ag = self._file_exists("AGENTS.md")
        cl = self._file_exists("CLAUDE.md")
        if ag and cl:
            self._add_check("Agent Engineering", "Agent Root Contract", 2, "AGENTS.md + CLAUDE.md", f"Found {ag} and {cl}", "", "")
        elif ag or cl:
            self._add_check("Agent Engineering", "Agent Root Contract", 2, "AGENTS.md / CLAUDE.md", f"Found {ag or cl}", "", "")
        else:
            self._add_check("Agent Engineering", "Agent Root Contract", 0, "AGENTS.md / CLAUDE.md", "No agent instruction file found", "Add AGENTS.md based on OpenForge agent engineering standard.", "ADR-0008 adoption.")

    def _check_agent_layered_instructions(self):
        cs = self._file_exists("CODING_STANDARDS.md", "docs/agent-engineering.md", "templates/CODING_STANDARDS.md") or (self._file_exists("AGENTS.md") and self._file_exists("CLAUDE.md"))
        if cs:
            self._add_check("Agent Engineering", "Layered Instructions Model", 2, "Concise root + CODING_STANDARDS.md", "Layered instruction structure present", "", "")
        elif self._file_exists("AGENTS.md", "CLAUDE.md"):
            self._add_check("Agent Engineering", "Layered Instructions Model", 1, "Concise root + CODING_STANDARDS.md", "Single contract without layered separation", "Consider splitting detailed rules to CODING_STANDARDS.md.", "ADR-0008 context efficiency.")
        else:
            self._add_check("Agent Engineering", "Layered Instructions Model", 0, "Concise root + CODING_STANDARDS.md", "No layered agent instructions", "Adopt layered instruction model.", "ADR-0008 compliance.")

    def _check_agent_convergence_rules(self):
        content = self._read_file_safe("AGENTS.md") + self._read_file_safe("CLAUDE.md") + self._read_file_safe("docs/agent-engineering.md")
        keywords = ["convergence", "stop condition", "evidence", "smallest coherent change", "reproduce"]
        matched = [kw for kw in keywords if kw in content.lower()]
        if len(matched) >= 2:
            self._add_check("Agent Engineering", "Evidence & Convergence Rules", 2, "Explicit stop conditions & evidence requirements", f"Explicit rules present ({', '.join(matched)})", "", "")
        elif content:
            self._add_check("Agent Engineering", "Evidence & Convergence Rules", 1, "Explicit stop conditions & evidence requirements", "Agent contract present without explicit convergence rules", "Update AGENTS.md with stop conditions (A/B/C) and evidence-first rules.", "ADR-0009 compliance.")
        else:
            self._add_check("Agent Engineering", "Evidence & Convergence Rules", 0, "Explicit stop conditions & evidence requirements", "No agent contract", "Adopt OpenForge agent contract with convergence rules.", "ADR-0009 compliance.")

    def _check_design_archetype(self):
        content = self._read_file_safe("DESIGN.md") + self._read_file_safe("docs/design-system.md") + self._read_file_safe("templates/DESIGN.md")
        archetypes = ["Platform Portal", "Data Control Plane", "Desktop Operator", "Operations Dashboard", "Admin Console", "Developer Tool"]
        found = [a for a in archetypes if a.lower() in content.lower()]
        if found:
            self._add_check("Design System", "Product Archetype Declaration", 2, "Archetype declared in DESIGN.md", f"Archetype declared: {found[0]}", "", "")
        elif self._file_exists("DESIGN.md"):
            self._add_check("Design System", "Product Archetype Declaration", 1, "Archetype declared in DESIGN.md", "DESIGN.md present without explicit archetype", f"Declare primary archetype ({self.archetype}) in DESIGN.md.", "ADR-0007 archetype standard.")
        else:
            if self.is_ui:
                self._add_check("Design System", "Product Archetype Declaration", 0, "Archetype declared in DESIGN.md", "Missing archetype declaration", f"Declare {self.archetype} in DESIGN.md.", "ADR-0007 design contract.")
            else:
                self._add_check("Design System", "Product Archetype Declaration", "N/A", "Archetype declared in DESIGN.md", "Non-UI repository", "", "")

    def _check_design_token_mapping(self):
        content = self._read_file_safe("DESIGN.md") + self._read_file_safe("docs/design-system.md") + self._read_file_safe("templates/DESIGN.md") + self._read_file_safe("templates/design/design-tokens.css")
        tokens = ["--of-color-", "token", "bgcanvas", "bgsurface", "textprimary"]
        found = [t for t in tokens if t in content.lower()]
        if len(found) >= 2:
            self._add_check("Design System", "Semantic Token Mapping", 2, "OpenForge token aliases in DESIGN.md", "Semantic token mapping documented", "", "")
        elif self._file_exists("DESIGN.md"):
            self._add_check("Design System", "Semantic Token Mapping", 1, "OpenForge token aliases in DESIGN.md", "DESIGN.md present without complete token mapping", "Map project color/surface tokens to OpenForge semantic roles.", "ADR-0007 design tokens.")
        else:
            if self.is_ui:
                self._add_check("Design System", "Semantic Token Mapping", 0, "OpenForge token aliases in DESIGN.md", "No token mapping found", "Map UI tokens to OpenForge semantic tokens in DESIGN.md.", "ADR-0007 semantic tokens.")
            else:
                self._add_check("Design System", "Semantic Token Mapping", "N/A", "OpenForge token aliases in DESIGN.md", "Non-UI repository", "", "")

    def _check_ui_i18n(self):
        if not self.is_ui:
            self._add_check("Localization", "UI i18n (en-US & ko-KR)", "N/A", "Locale resources for UI", "Non-UI repository", "", "")
            return
        i18n_dirs = self._find_files("locales") + self._find_files("messages") + self._find_files("i18n") + self._find_files("public/locales")
        content = self._read_file_safe("package.json")
        has_i18n_lib = any(lib in content for lib in ["next-intl", "react-i18next", "vue-i18n", "i18next"])
        if i18n_dirs or has_i18n_lib:
            self._add_check("Localization", "UI i18n (en-US & ko-KR)", 2, "Locale resources for UI", "UI internationalization resources detected", "", "")
        else:
            self._add_check("Localization", "UI i18n (en-US & ko-KR)", 1, "Locale resources for UI", "UI project without explicit locale resource directory", "Configure en-US and ko-KR i18n resources.", "ADR-0002 bilingual UI requirement.")

    def _generate_issue_draft(self, gaps: List[Dict[str, Any]], score: float, maturity: str) -> Dict[str, str]:
        title = f"chore(compliance): align with OpenForge standards ({score}% maturity)"
        body_lines = [
            f"## OpenForge Compliance Audit — {self.name}",
            "",
            f"**Current Score:** `{score}%` ({self.total_points}/{self.max_points} points)",
            f"**Maturity Status:** {maturity}",
            f"**Product Archetype:** {self.archetype}",
            "",
            "### Identified Gaps & Required Actions",
            "",
        ]

        for idx, g in enumerate(gaps, 1):
            body_lines.append(f"#### {idx}. [{g['area']}] {g['metric']}")
            body_lines.append(f"- **Current Evidence:** {g['evidence']}")
            body_lines.append(f"- **Target Standard:** {g['target']}")
            body_lines.append(f"- **Action Required:** {g['gap']}")
            if g["exception_hint"]:
                body_lines.append(f"- **Guidance / Exception Path:** `{g['exception_hint']}`")
            body_lines.append("")

        body_lines.extend([
            "### Verification Checklist",
            "",
            "- [ ] Update filenames to `-ko.md` format where applicable (ADR-0002)",
            "- [ ] Introduce/Update `AGENTS.md` and `DESIGN.md` contracts",
            "- [ ] Ensure CI runs format, test, and supply-chain verification",
            "- [ ] Document intentional exceptions in an ADR if required (ADR-0012)",
            "",
            "> Automated by OpenForge Portfolio Compliance Auditor",
        ])

        return {
            "title": title,
            "labels": "compliance, openforge, standard-gap",
            "body": "\n".join(body_lines),
        }


def run_portfolio_audit(portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = []
    for repo_info in portfolio:
        auditor = RepoAuditor(repo_info)
        res = auditor.run_audit()
        results.append(res)

    results.sort(key=lambda x: x["score_percent"], reverse=True)

    total_pts = sum(r["total_points"] for r in results if r["exists"])
    max_pts = sum(r["max_points"] for r in results if r["exists"])
    overall_percent = round((total_pts / max_pts * 100), 1) if max_pts > 0 else 0.0

    return {
        "overall_score": overall_percent,
        "total_repositories": len(results),
        "audited_repositories": len([r for r in results if r["exists"]]),
        "results": results,
    }


def generate_markdown_scorecard(audit_data: Dict[str, Any], lang: str = "en") -> str:
    is_ko = lang == "ko"
    title = "# OpenForge Portfolio Compliance Scorecard" if not is_ko else "# OpenForge 포트폴리오 컴플라이언스 스코어카드"
    sub = (
        "> Automated audit of active Dasomel OSS repositories against OpenForge engineering standards."
        if not is_ko else
        "> OpenForge 엔지니어링 표준을 기준으로 Dasomel 활성 OSS 리포지토리를 자동 진단한 스코어카드입니다."
    )

    lines = [
        title,
        "",
        sub,
        "",
        f"**{'Overall Portfolio Maturity' if not is_ko else '전체 포트폴리오 평균 완성도'}:** `{audit_data['overall_score']}%`",
        f"**{'Audited Repositories' if not is_ko else '진단 대상 리포지토리'}:** {audit_data['audited_repositories']} projects",
        "",
        "## 1. Portfolio Maturity Ranking" if not is_ko else "## 1. 포트폴리오 성숙도 순위",
        "",
        "| Repository | Category | Archetype | Score | Maturity Status |" if not is_ko else "| 리포지토리 | 분류 | 아키타입 | 점수 | 성숙도 상태 |",
        "|---|---|---|---:|---|",
    ]

    for r in audit_data["results"]:
        if not r["exists"]:
            continue
        bar = "🟢" if r["score_percent"] >= 90 else "🟡" if r["score_percent"] >= 75 else "🟠" if r["score_percent"] >= 60 else "🔴"
        status_text = r["maturity"]
        if is_ko:
            if r["score_percent"] >= 90:
                status_text = "프로덕션 레디 기반 (90%+)"
            elif r["score_percent"] >= 75:
                status_text = "양호 / 경미한 Gap (75-89%)"
            elif r["score_percent"] >= 60:
                status_text = "개선 권장 (60-74%)"
            else:
                status_text = "기반 작업 필요 (<60%)"

        lines.append(f"| **{r['name']}** | {r['category']} | `{r['archetype']}` | {bar} **{r['score_percent']}%** ({r['total_points']}/{r['max_points']}) | {status_text} |")

    lines.extend([
        "",
        "## 2. Requirement Traceability & Gap Summary" if not is_ko else "## 2. 요구사항 추적 및 리포지토리별 Gap 요약",
        "",
    ])

    for r in audit_data["results"]:
        if not r["exists"]:
            continue
        lines.append(f"### {r['name']} (`{r['score_percent']}%`)")
        lines.append(f"- **{'Path' if not is_ko else '경로'}:** `{r['path']}`")
        lines.append(f"- **{'Archetype' if not is_ko else '아키타입'}:** `{r['archetype']}` | **{'Category' if not is_ko else '분류'}:** {r['category']}")
        lines.append(f"- **{'Gaps Identified' if not is_ko else '식별된 Gap 건수'}:** {len(r['gaps'])}")
        lines.append("")
        if r["gaps"]:
            lines.append("| Area | Metric | Current Evidence | Action / Exception Path |" if not is_ko else "| 영역 | 지표 | 현재 증적 | 조치 사항 / 예외 경로 |")
            lines.append("|---|---|---|---|")
            for g in r["gaps"]:
                score_badge = "🔴 Missing (0)" if g["score"] == 0 else "🟡 Partial (1)"
                lines.append(f"| {g['area']} | **{g['metric']}** ({score_badge}) | {g['evidence']} | {g['gap']} `{g['exception_hint']}` |")
        else:
            lines.append("🎉 No outstanding compliance gaps detected." if not is_ko else "🎉 미해결된 컴플라이언스 Gap이 없습니다.")
        lines.append("")

    lines.extend([
        "## 3. Recommended Remediation Order" if not is_ko else "## 3. 권장 후속 개선 순서",
        "",
        "1. **Bilingual Filename Parity (ADR-0002)**: Migrate remaining legacy `_ko.md` and `.ko.md` files to `-ko.md` in `narwhal`, `narwhal-portal`, `kubemetal`, `nfs-quota-agent`, `ldapium`, `kube-ready-box`." if not is_ko else "1. **영한 파일명 표준화 (ADR-0002)**: `narwhal`, `narwhal-portal`, `kubemetal`, `nfs-quota-agent`, `ldapium`, `kube-ready-box` 내 레거시 `_ko.md` / `.ko.md`를 `-ko.md`로 정리.",
        "2. **DESIGN.md & Archetype Adoption (ADR-0007)**: Establish root `DESIGN.md` declaring semantic token mappings in `clusterdeck`, `beluga-manager`, `ldapium`, and `dasomel.github.io`." if not is_ko else "2. **DESIGN.md 및 아키타입 적용 (ADR-0007)**: `clusterdeck`, `beluga-manager`, `ldapium`, `dasomel.github.io`에 시맨틱 토큰 매핑 및 아키타입을 명시한 `DESIGN.md` 수립.",
        "3. **Root Agent Contract (ADR-0008, ADR-0009)**: Add concise `AGENTS.md` to `beluga-manager`, `cka-lab`, and `egovframe-launcher`." if not is_ko else "3. **에이전트 계약 수립 (ADR-0008, ADR-0009)**: `beluga-manager`, `cka-lab`, `egovframe-launcher`에 간결한 `AGENTS.md` 루트 계약 배치.",
        "4. **CI Supply Chain & Branch Protection (ADR-0003, ADR-0006)**: Configure required status checks on `main` and supply chain verification across all active repositories." if not is_ko else "4. **CI 공급망 게이트 및 Branch Protection (ADR-0003, ADR-0006)**: `main` 브랜치에 필수 상태 검사 및 공급망 검증 워크플로 구성.",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="OpenForge Portfolio Compliance Auditor")
    parser.add_argument("--repo", type=str, help="Audit a single repository path")
    parser.add_argument("--json-out", type=str, default="docs/portfolio-audit-report.json", help="Path to write JSON report")
    parser.add_argument("--scorecard-en", type=str, default="docs/portfolio-scorecard.md", help="Path to write English scorecard")
    parser.add_argument("--scorecard-ko", type=str, default="docs/portfolio-scorecard-ko.md", help="Path to write Korean scorecard")
    parser.add_argument("--issues-dir", type=str, default="docs/gap-issues", help="Directory to output per-project GitHub issue drafts")
    args = parser.parse_args()

    if args.repo:
        repo_path = os.path.abspath(args.repo)
        repo_name = os.path.basename(repo_path)
        portfolio = [{
            "id": repo_name,
            "name": repo_name,
            "path": repo_path,
            "category": "Ad-hoc Target",
            "archetype": "Developer Tool",
            "is_ui": True,
            "has_container": True,
            "uses_env": True,
        }]
    else:
        portfolio = DEFAULT_PORTFOLIO

    audit_data = run_portfolio_audit(portfolio)

    # Write JSON output
    json_path = Path(args.json_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2, ensure_ascii=False)
    print(f"Wrote JSON audit report to {args.json_out}")

    # Write Markdown Scorecards
    en_scorecard = generate_markdown_scorecard(audit_data, lang="en")
    with open(args.scorecard_en, "w", encoding="utf-8") as f:
        f.write(en_scorecard)
    print(f"Wrote English scorecard to {args.scorecard_en}")

    ko_scorecard = generate_markdown_scorecard(audit_data, lang="ko")
    with open(args.scorecard_ko, "w", encoding="utf-8") as f:
        f.write(ko_scorecard)
    print(f"Wrote Korean scorecard to {args.scorecard_ko}")

    # Write individual gap issues
    issues_dir = Path(args.issues_dir)
    issues_dir.mkdir(parents=True, exist_ok=True)
    for r in audit_data["results"]:
        if not r["exists"] or not r["gaps"]:
            continue
        issue_file = issues_dir / f"{r['id']}-gap-issue.md"
        with open(issue_file, "w", encoding="utf-8") as f:
            f.write(f"# {r['issue_draft']['title']}\n\n")
            f.write(f"**Labels:** `{r['issue_draft']['labels']}`\n\n")
            f.write(r['issue_draft']['body'])
            f.write("\n")
    print(f"Wrote gap issues to {args.issues_dir}/")

    # Print summary to stdout
    print("\n" + "=" * 60)
    print(f"OPENFORGE COMPLIANCE AUDIT SUMMARY — Overall: {audit_data['overall_score']}%")
    print("=" * 60)
    for r in audit_data["results"]:
        if r["exists"]:
            print(f"{r['name']:20s} : {r['score_percent']:5.1f}% ({r['total_points']}/{r['max_points']}) | {len(r['gaps'])} gaps | {r['maturity']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
