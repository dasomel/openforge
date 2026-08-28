#!/usr/bin/env python3

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "templates" / "scripts"
spec = importlib.util.spec_from_file_location("audit_agent_behaviors", str(SCRIPTS_DIR / "audit-agent-behaviors.py"))
audit_agent_behaviors = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit_agent_behaviors
spec.loader.exec_module(audit_agent_behaviors)
core = audit_agent_behaviors.core


class TestBehaviorPortfolioAudit(unittest.TestCase):
    def _repo_info(self, path: Path):
        return {
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

    def _agent_004(self, path: Path):
        result = core.RepoAuditor(self._repo_info(path), path.parent).run_audit()
        return next(c for c in result["checks"] if c["metricId"] == "AGENT-004")

    def test_metric_is_registered(self):
        ids = [m["id"] for m in core.METRIC_DEFINITIONS]
        self.assertIn("AGENT-004", ids)
        self.assertEqual(len(ids), len(set(ids)))

    def test_profile_not_adopted_is_na(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "README.md").write_text("# Fixture\n", encoding="utf-8")
            check = self._agent_004(repo)
            self.assertEqual(check["score"], "N/A")
            self.assertIn("not adopted", check["evidence"].lower())

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


if __name__ == "__main__":
    unittest.main()
