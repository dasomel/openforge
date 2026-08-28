#!/usr/bin/env python3
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "templates" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
spec = importlib.util.spec_from_file_location("audit_portfolio_agent_ops", str(SCRIPTS_DIR / "audit-portfolio.py"))
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)


class TestAgentOperationalPortfolioAudit(unittest.TestCase):
    def _repo_info(self, path: Path, agent_evals=None):
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
        if agent_evals is not None:
            info["agent_evals"] = agent_evals
        return info

    def _check(self, path: Path, agent_evals=None):
        result = audit.RepoAuditor(self._repo_info(path, agent_evals), path.parent).run_audit()
        return next(c for c in result["checks"] if c["metricId"] == "AGENT-005")

    def _write_valid_contract(self, repo: Path, workflow=True):
        root = repo / ".agents" / "evals"
        traces = root / "traces"
        traces.mkdir(parents=True)
        for name in ("evaluate.py", "gate.py", "bind-verification.py"):
            (root / name).write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        (root / "baseline.eval.json").write_text(json.dumps({
            "schemaVersion": "openforge-agent-eval/v1",
            "traceId": "baseline",
            "results": []
        }), encoding="utf-8")
        (traces / "live.json").write_text(json.dumps({
            "schemaVersion": "openforge-agent-trace/v1",
            "traceId": "live",
            "consistencyMode": "strict",
            "events": [
                {"id": "e1", "type": "verification", "scope": "runtime", "status": "pending", "evidence": ["runtime:command"]},
                {"id": "e2", "type": "regression_verification", "scope": "runtime", "status": "pending", "evidence": ["test:runtime-check"]},
                {"id": "e3", "type": "completion_claim", "scope": "runtime", "evidence": ["runtime:command"]},
                {"id": "e4", "type": "task_outcome", "state": "A", "scope": "runtime", "evidence": ["policy:strict"]}
            ]
        }), encoding="utf-8")
        if workflow:
            wf = repo / ".github" / "workflows"
            wf.mkdir(parents=True)
            (wf / "agent.yml").write_text(
                "run: python3 .agents/evals/bind-verification.py --trace .agents/evals/traces/live.json -- python3 check.py\n"
                "run: python3 .agents/evals/gate.py --trace .agents/evals/traces/live.json\n",
                encoding="utf-8",
            )

    def test_not_adopted_is_na(self):
        with tempfile.TemporaryDirectory() as td:
            check = self._check(Path(td))
            self.assertEqual(check["score"], "N/A")

    def test_required_but_missing_fails(self):
        with tempfile.TemporaryDirectory() as td:
            check = self._check(Path(td), True)
            self.assertEqual(check["score"], 0)
            self.assertIn("required", check["evidence"].lower())

    def test_directory_presence_alone_fails(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / ".agents" / "evals").mkdir(parents=True)
            check = self._check(repo)
            self.assertEqual(check["score"], 0)
            self.assertIn("incomplete", check["evidence"].lower())

    def test_valid_executable_contract_passes(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self._write_valid_contract(repo)
            check = self._check(repo)
            self.assertEqual(check["score"], 2)
            self.assertIn("live binder", check["evidence"])

    def test_missing_ci_wiring_fails(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self._write_valid_contract(repo, workflow=False)
            check = self._check(repo)
            self.assertEqual(check["score"], 0)
            self.assertIn("CI does not wire", check["evidence"])

    def test_agent_evals_config_must_be_boolean(self):
        errors = audit.validate_portfolio_config({"repositories": [self._repo_info(Path("fixture")) | {"agent_evals": "yes"}]})
        self.assertTrue(any("agent_evals" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
