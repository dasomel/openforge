#!/usr/bin/env python3
"""
Unit and integration tests for OpenForge Portfolio Compliance Auditor.
Tests compliance scoring, stable metric IDs, fixture evaluation,
legacy detection, baseline comparison, and config validation.
"""

import os
import sys
import unittest
import json
from pathlib import Path

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
        """Verify all standard metrics have unique, uppercase stable IDs with required fields."""
        metrics = audit_portfolio.METRIC_DEFINITIONS
        self.assertGreaterEqual(len(metrics), 30)

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

        # Verify no local user path leaked in output
        self.assertNotIn("/Users/", res["pathHint"])
        self.assertIn("<workspace>", res["pathHint"])

    def test_legacy_korean_filename_detection(self):
        """Partial fixture with README_ko.md should be flagged under DOC-002 and DOC-003."""
        repo_info = {
            "id": "partial-repo",
            "repository": "fixture/partial-repo",
            "path": "partial",
            "category": "Test Fixtures",
            "archetype": "Developer Tool",
            "profile": "standard",
            "ui": True,
            "container": True,
            "env": True,
        }
        auditor = audit_portfolio.RepoAuditor(repo_info, self.workspace_root)
        res = auditor.run_audit()

        checks_by_id = {c["metricId"]: c for c in res["checks"]}
        self.assertEqual(checks_by_id["DOC-002"]["score"], 1)  # partial for legacy name
        self.assertEqual(checks_by_id["DOC-003"]["score"], 0)  # failed filename standard

    def test_unpaired_adr_detection(self):
        """Partial fixture with unpaired ADR should be flagged under ARCH-002."""
        repo_info = {
            "id": "partial-repo",
            "repository": "fixture/partial-repo",
            "path": "partial",
            "category": "Test Fixtures",
            "archetype": "Developer Tool",
            "profile": "standard",
            "ui": False,
            "container": False,
            "env": False,
        }
        auditor = audit_portfolio.RepoAuditor(repo_info, self.workspace_root)
        res = auditor.run_audit()

        checks_by_id = {c["metricId"]: c for c in res["checks"]}
        self.assertEqual(checks_by_id["ARCH-002"]["score"], 0)

    def test_missing_design_in_ui_project(self):
        """Minimal fixture marked as UI should fail DESIGN-001 and DESIGN-002."""
        repo_info = {
            "id": "minimal-ui",
            "repository": "fixture/minimal-ui",
            "path": "minimal",
            "category": "Test Fixtures",
            "archetype": "Operations Dashboard",
            "profile": "desktop",
            "ui": True,
            "container": False,
            "env": False,
        }
        auditor = audit_portfolio.RepoAuditor(repo_info, self.workspace_root)
        res = auditor.run_audit()

        checks_by_id = {c["metricId"]: c for c in res["checks"]}
        self.assertEqual(checks_by_id["ARCH-004"]["score"], 0)
        self.assertEqual(checks_by_id["DESIGN-001"]["score"], 0)
        self.assertEqual(checks_by_id["DESIGN-002"]["score"], 0)

    def test_unavailable_repository_handling(self):
        """Nonexistent repository path should result in status=unavailable without throwing exception."""
        repo_info = {
            "id": "nonexistent-repo",
            "repository": "fixture/nonexistent",
            "path": "does-not-exist-dir",
            "category": "Test Fixtures",
            "archetype": "Developer Tool",
            "profile": "standard",
            "ui": False,
            "container": False,
            "env": False,
        }
        auditor = audit_portfolio.RepoAuditor(repo_info, self.workspace_root)
        res = auditor.run_audit()

        self.assertFalse(res["exists"])
        self.assertEqual(res["status"], "unavailable")
        self.assertEqual(res["maturity"], "Unavailable")

    def test_malformed_config_validation(self):
        """Config validator should catch invalid version, missing fields, and duplicate IDs."""
        bad_config = {
            "version": "invalid-version-string",
            "repositories": [
                {"id": "duplicate-id", "repository": "r1", "path": "p1"},
                {"id": "duplicate-id", "repository": "r2", "path": "p2"},
                {"id": "missing-fields"},
                {"id": "bad-archetype", "repository": "r3", "path": "p3", "archetype": "NonexistentArchetype"},
            ]
        }
        errors = audit_portfolio.validate_portfolio_config(bad_config)
        self.assertGreaterEqual(len(errors), 4)

    def test_baseline_comparison_and_deltas(self):
        """Baseline comparison should compute accurate portfolio deltas, new gaps, and resolved gaps."""
        baseline = {
            "overallScore": 50.0,
            "results": [
                {
                    "id": "repo-1",
                    "repository": "fixture/repo-1",
                    "score": {"percent": 50.0},
                    "checks": [
                        {"metricId": "DOC-001", "score": 2},
                        {"metricId": "DOC-002", "score": 0},
                    ]
                }
            ]
        }
        current = {
            "overallScore": 65.0,
            "results": [
                {
                    "id": "repo-1",
                    "repository": "fixture/repo-1",
                    "score": {"percent": 65.0},
                    "checks": [
                        {"metricId": "DOC-001", "score": 2},
                        {"metricId": "DOC-002", "score": 2},  # Resolved!
                        {"metricId": "DOC-003", "score": 0},  # New check/gap
                    ]
                }
            ]
        }
        comparison = audit_portfolio.compare_with_baseline(current, baseline)
        self.assertEqual(comparison["portfolio"]["delta"], 15.0)
        self.assertEqual(comparison["repositories"][0]["delta"], 15.0)
        self.assertIn("DOC-002", comparison["repositories"][0]["resolvedGaps"])


if __name__ == "__main__":
    unittest.main()
