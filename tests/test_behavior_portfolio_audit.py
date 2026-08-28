#!/usr/bin/env python3

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "templates" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
spec = importlib.util.spec_from_file_location("audit_portfolio_behaviors", str(SCRIPTS_DIR / "audit-portfolio.py"))
audit_portfolio = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit_portfolio
spec.loader.exec_module(audit_portfolio)


class TestBehaviorPortfolioAudit(unittest.TestCase):
    def _repo_info(self, path: Path, agent_behaviors=None):
        info = {
            "id": "fixture",
            "repository": "fixture/repo",
            "path": str(path),
            "category": "Test Fixtures",
            "archetype": "Developer Tool",
            "profile": "standard",
            "ui": False,
            "container": False,
            "env": False,
        }
        if agent_behaviors is not None:
            info["agent_behaviors"] = agent_behaviors
        return info

    def _agent_004(self, path: Path, agent_behaviors=None):
        result = audit_portfolio.RepoAuditor(
            self._repo_info(path, agent_behaviors), path.parent
        ).run_audit()
        return next(c for c in result["checks"] if c["metricId"] == "AGENT-004")

    def test_metric_is_registered_canonically(self):
        ids = [m["id"] for m in audit_portfolio.METRIC_DEFINITIONS]
        self.assertIn("AGENT-004", ids)
        self.assertEqual(len(ids), 36)
        self.assertEqual(len(ids), len(set(ids)))

    def test_profile_not_adopted_is_na(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "README.md").write_text("# Fixture\n", encoding="utf-8")
            check = self._agent_004(repo)
            self.assertEqual(check["score"], "N/A")
            self.assertIn("not adopted", check["evidence"].lower())

    def test_profile_explicitly_disabled_is_na_even_if_directory_exists(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            behavior = repo / ".agents" / "behaviors" / "verify-evidence"
            behavior.mkdir(parents=True)
            (behavior / "BEHAVIOR.md").write_text(
                "---\nname: verify-evidence\ndescription: Verify evidence.\n---\n",
                encoding="utf-8",
            )
            check = self._agent_004(repo, False)
            self.assertEqual(check["score"], "N/A")
            self.assertIn("disabled", check["evidence"].lower())

    def test_profile_required_but_missing_fails(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            check = self._agent_004(repo, True)
            self.assertEqual(check["score"], 0)
            self.assertIn("required", check["evidence"].lower())

    def test_valid_behavior_profile_passes(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            behavior = repo / ".agents" / "behaviors" / "verify-evidence"
            behavior.mkdir(parents=True)
            (behavior / "BEHAVIOR.md").write_text(
                "---\nname: verify-evidence\ndescription: Verify evidence before completion claims.\n---\n\n# Verify Evidence\n",
                encoding="utf-8",
            )
            check = self._agent_004(repo)
            self.assertEqual(check["score"], 2)
            self.assertIn("Validated 1 behavior specs", check["evidence"])

    def test_invalid_behavior_profile_fails(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            behavior = repo / ".agents" / "behaviors" / "verify-evidence"
            behavior.mkdir(parents=True)
            (behavior / "BEHAVIOR.md").write_text(
                "---\nname: different-name\n---\n\n# Broken\n",
                encoding="utf-8",
            )
            check = self._agent_004(repo)
            self.assertEqual(check["score"], 0)
            self.assertIn("structurally invalid", check["evidence"])
            self.assertIn("description", check["evidence"])

    def test_empty_adopted_profile_fails(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / ".agents" / "behaviors").mkdir(parents=True)
            check = self._agent_004(repo)
            self.assertEqual(check["score"], 0)
            self.assertIn("contains no BEHAVIOR.md", check["evidence"])

    def test_audit_report_declares_2026_09_metric_set(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            result = audit_portfolio.run_portfolio_audit(
                [self._repo_info(repo)], repo.parent
            )
            self.assertEqual(result["metricSetVersion"], "2026.09")
            self.assertEqual(result["metricSetChange"]["added"], ["AGENT-004"])


if __name__ == "__main__":
    unittest.main()
