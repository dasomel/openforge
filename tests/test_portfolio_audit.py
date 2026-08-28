#!/usr/bin/env python3
"""
Unit and integration tests for OpenForge Portfolio Compliance Auditor.
Tests compliance scoring, stable metric IDs, fixture evaluation,
legacy detection, baseline comparison, config validation, false-positive resistance,
and fallback YAML parser safety.
"""

import os
import sys
import unittest
import json
from pathlib import Path
import tempfile
import shutil

# Add templates/scripts to Python path
SCRIPTS_DIR = Path(__file__).parent.parent / "templates" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import importlib.util
spec = importlib.util.spec_from_file_location("audit_portfolio", str(SCRIPTS_DIR / "audit-portfolio.py"))
audit_portfolio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_portfolio)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "compliance"


class TestPortfolioAuditor(unittest.TestCase):

    def setUp(self):
        self.workspace_root = FIXTURES_DIR

    def test_stable_metric_ids_integrity(self):
        """Verify all 37 standard metrics have unique, uppercase stable IDs with required fields and weight=1."""
        metrics = audit_portfolio.METRIC_DEFINITIONS
        self.assertEqual(len(metrics), 37, f"Expected exactly 37 metrics, got {len(metrics)}")

        seen_ids = set()
        for m in metrics:
            mid = m["id"]
            self.assertNotIn(mid, seen_ids, f"Duplicate metric ID: {mid}")
            seen_ids.add(mid)
            self.assertTrue(mid.isupper() or any(c.isdigit() for c in mid))
            self.assertIn("area", m)
            self.assertIn("name", m)
            self.assertIn("target", m)
            self.assertIn("priority", m)
            self.assertIn(m["priority"], {"P0", "P1", "P2", "P3"})
            self.assertEqual(m.get("default_weight", 1), 1, f"Metric {mid} weight should be 1")

    def test_good_fixture_scores_high(self):
        """Good fixture repository should score above 90% (Production-ready)."""
        repo_info = {
            "id": "good-repo",
            "repository": "fixture/good-repo",
            "path": "good",
            "category": "Test Fixtures",
            "archetype": "Developer Tool",
            "profile": "standard",
            "ui": False,
            "container": False,
            "env": False,
        }
        auditor = audit_portfolio.RepoAuditor(repo_info, self.workspace_root)
        res = auditor.run_audit()

        self.assertTrue(res["exists"])
        self.assertEqual(res["status"], "audited")
        self.assertGreaterEqual(res["score"]["percent"], 90.0)
        self.assertEqual(res["maturity"], "Production-ready OSS foundation")

        self.assertIn("earned", res["score"])
        self.assertIn("possible", res["score"])
        self.assertIn("percent", res["score"])
        self.assertEqual(res["metrics"]["totalDefined"], 37)

        self.assertNotIn("/Users/", res["pathHint"])
        self.assertNotIn("/home/", res["pathHint"])
        self.assertIn("<workspace>", res["pathHint"])

    def test_legacy_korean_filename_detection(self):
        repo_info = {
            "id": "partial-repo", "repository": "fixture/partial-repo", "path": "partial",
            "category": "Test Fixtures", "archetype": "Developer Tool", "profile": "standard",
            "ui": True, "container": True, "env": True,
        }
        res = audit_portfolio.RepoAuditor(repo_info, self.workspace_root).run_audit()
        checks_by_id = {c["metricId"]: c for c in res["checks"]}
        self.assertEqual(checks_by_id["DOC-002"]["score"], 1)
        self.assertEqual(checks_by_id["DOC-003"]["score"], 0)

    def test_unpaired_adr_detection(self):
        repo_info = {
            "id": "partial-repo", "repository": "fixture/partial-repo", "path": "partial",
            "category": "Test Fixtures", "archetype": "Developer Tool", "profile": "standard",
            "ui": False, "container": False, "env": False,
        }
        res = audit_portfolio.RepoAuditor(repo_info, self.workspace_root).run_audit()
        checks_by_id = {c["metricId"]: c for c in res["checks"]}
        self.assertEqual(checks_by_id["ARCH-002"]["score"], 0)

    def test_missing_design_in_ui_project(self):
        repo_info = {
            "id": "minimal-ui", "repository": "fixture/minimal-ui", "path": "minimal",
            "category": "Test Fixtures", "archetype": "Operations Dashboard", "profile": "desktop",
            "ui": True, "container": False, "env": False,
        }
        res = audit_portfolio.RepoAuditor(repo_info, self.workspace_root).run_audit()
        checks_by_id = {c["metricId"]: c for c in res["checks"]}
        self.assertEqual(checks_by_id["ARCH-004"]["score"], 0)
        self.assertEqual(checks_by_id["DESIGN-001"]["score"], 0)
        self.assertEqual(checks_by_id["DESIGN-002"]["score"], 0)

    def test_unavailable_repository_handling(self):
        repo_info = {
            "id": "nonexistent-repo", "repository": "fixture/nonexistent", "path": "does-not-exist-dir",
            "category": "Test Fixtures", "archetype": "Developer Tool", "profile": "standard",
            "ui": False, "container": False, "env": False,
        }
        res = audit_portfolio.RepoAuditor(repo_info, self.workspace_root).run_audit()
        self.assertFalse(res["exists"])
        self.assertEqual(res["status"], "unavailable")
        self.assertEqual(res["maturity"], "Unavailable")

    def test_malformed_config_validation(self):
        bad_config = {
            "version": "invalid-version-string",
            "repositories": [
                {"id": "duplicate-id", "repository": "r1", "path": "p1"},
                {"id": "duplicate-id", "repository": "r2", "path": "p2"},
                {"id": "missing-fields"},
                {"id": "bad-archetype", "repository": "r3", "path": "p3", "archetype": "NonexistentArchetype"},
                {"id": "bad-profile", "repository": "r4", "path": "p4", "profile": "unknown-profile"},
                {"id": "bad-behavior-flag", "repository": "r5", "path": "p5", "agent_behaviors": "yes"},
            ]
        }
        errors = audit_portfolio.validate_portfolio_config(bad_config)
        self.assertGreaterEqual(len(errors), 6)
        self.assertTrue(any("agent_behaviors" in error for error in errors))

    def test_baseline_comparison_and_deltas(self):
        baseline = {
            "metricSetVersion": "2026.09", "overallScore": 50.0,
            "results": [{
                "id": "repo-1", "repository": "fixture/repo-1", "score": {"percent": 50.0},
                "checks": [
                    {"metricId": "DOC-001", "score": 2},
                    {"metricId": "DOC-002", "score": 0},
                    {"metricId": "SEC-001", "score": 2},
                ]
            }]
        }
        current = {
            "metricSetVersion": "2026.09", "overallScore": 65.0,
            "results": [{
                "id": "repo-1", "repository": "fixture/repo-1", "score": {"percent": 65.0},
                "checks": [
                    {"metricId": "DOC-001", "score": 2},
                    {"metricId": "DOC-002", "score": 2},
                    {"metricId": "SEC-001", "score": 0},
                    {"metricId": "DOC-003", "score": 0},
                ]
            }]
        }
        comparison = audit_portfolio.compare_with_baseline(current, baseline)
        self.assertEqual(comparison["portfolio"]["delta"], 15.0)
        self.assertEqual(comparison["metricSetVersionStatus"], "compatible")
        self.assertIsNone(comparison["warning"])
        repo_comp = comparison["repositories"][0]
        self.assertEqual(repo_comp["delta"], 15.0)
        self.assertIn("DOC-002", repo_comp["resolvedGaps"])
        self.assertIn("SEC-001", repo_comp["newGaps"])
        self.assertIn("SEC-001", repo_comp["regressions"])

    def test_additive_2026_08_baseline_compatibility(self):
        baseline = {"metricSetVersion": "2026.08", "overallScore": 60.0, "results": []}
        current = {"metricSetVersion": "2026.09", "overallScore": 60.0, "results": []}
        comparison = audit_portfolio.compare_with_baseline(current, baseline)
        self.assertEqual(comparison["metricSetVersionStatus"], "additive-compatible")
        self.assertIn("AGENT-004", comparison["warning"])

    def test_baseline_incompatible_version_warning(self):
        baseline = {"metricSetVersion": "2025.01", "overallScore": 50.0, "results": []}
        current = {"metricSetVersion": "2026.09", "overallScore": 60.0, "results": []}
        comparison = audit_portfolio.compare_with_baseline(current, baseline)
        self.assertEqual(comparison["metricSetVersionStatus"], "incompatible")
        self.assertIsNotNone(comparison["warning"])

    def test_fallback_yaml_parser_subset_and_safety(self):
        valid_yaml = """
version: openforge-portfolio/v1
workspaceRoot: ".."
repositories:
  - id: test-repo
    repository: org/test-repo
    path: test-repo
    category: Developer Tool
    archetype: Developer Tool
    profile: standard
    ui: false
    container: false
    env: false
    agent_behaviors: true
"""
        parsed = audit_portfolio.load_yaml_safe(valid_yaml, force_fallback=True)
        self.assertEqual(parsed["version"], "openforge-portfolio/v1")
        self.assertEqual(len(parsed["repositories"]), 1)
        self.assertEqual(parsed["repositories"][0]["id"], "test-repo")
        self.assertTrue(parsed["repositories"][0]["agent_behaviors"])

        unsupported_anchor = """
version: openforge-portfolio/v1
defaults: &defaults
  profile: standard
repositories:
  - id: r1
    <<: *defaults
"""
        with self.assertRaises(ValueError):
            audit_portfolio.load_yaml_safe(unsupported_anchor, force_fallback=True)

        tab_yaml = "version: openforge-portfolio/v1\nrepositories:\n\t- id: r1\n"
        with self.assertRaises(ValueError):
            audit_portfolio.load_yaml_safe(tab_yaml, force_fallback=True)

    def test_false_positive_agents_evidence_detection(self):
        temp_dir = tempfile.mkdtemp()
        try:
            repo_path = Path(temp_dir) / "test-repo"
            repo_path.mkdir()
            (repo_path / "AGENTS.md").write_text("# Instructions\nPlease provide evidence in discussions.\n")
            repo_info = {"id": "test-repo", "path": "test-repo", "profile": "standard"}
            res = audit_portfolio.RepoAuditor(repo_info, Path(temp_dir)).run_audit()
            checks = {c["metricId"]: c for c in res["checks"]}
            self.assertEqual(checks["AGENT-003"]["score"], 1)

            (repo_path / "AGENTS.md").write_text(
                "# AGENTS.md\n- Evidence before completion.\n- Stop condition: A (Complete), B (Progress), C (Stop).\n- Smallest coherent change.\n"
            )
            res = audit_portfolio.RepoAuditor(repo_info, Path(temp_dir)).run_audit()
            checks = {c["metricId"]: c for c in res["checks"]}
            self.assertEqual(checks["AGENT-003"]["score"], 2)
        finally:
            shutil.rmtree(temp_dir)

    def test_false_positive_design_tokens_detection(self):
        temp_dir = tempfile.mkdtemp()
        try:
            repo_path = Path(temp_dir) / "test-repo"
            repo_path.mkdir()
            (repo_path / "DESIGN.md").write_text("# Design\nWe pass authentication tokens via headers.\n")
            repo_info = {"id": "test-repo", "path": "test-repo", "profile": "desktop", "ui": True}
            res = audit_portfolio.RepoAuditor(repo_info, Path(temp_dir)).run_audit()
            checks = {c["metricId"]: c for c in res["checks"]}
            self.assertEqual(checks["ARCH-004"]["score"], 1)
            self.assertEqual(checks["DESIGN-002"]["score"], 1)

            (repo_path / "DESIGN.md").write_text(
                "# DESIGN.md\n## Product archetype\narchetype: Operations Dashboard\n## Token mapping\ntokens:\n  bgCanvas: var(--of-color-bg-canvas)\n  textPrimary: var(--of-color-text-primary)\n"
            )
            res = audit_portfolio.RepoAuditor(repo_info, Path(temp_dir)).run_audit()
            checks = {c["metricId"]: c for c in res["checks"]}
            self.assertEqual(checks["ARCH-004"]["score"], 2)
            self.assertEqual(checks["DESIGN-002"]["score"], 2)
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
