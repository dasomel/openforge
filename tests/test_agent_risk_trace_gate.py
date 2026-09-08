import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates" / "scripts" / "check-agent-trace-requirement.py"
spec = importlib.util.spec_from_file_location("risk_gate", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AgentRiskTraceGateTests(unittest.TestCase):
    def setUp(self):
        self.policy = {
            "schemaVersion": "openforge-agent-risk-policy/v1",
            "defaultRisk": "low",
            "traceRequiredAt": ["high"],
            "tracePathPrefix": ".agents/evals/traces/",
            "rules": [
                {"risk": "high", "pattern": ".github/workflows/**", "reason": "CI"},
                {"risk": "medium", "pattern": "docs/**", "reason": "docs"},
            ],
        }

    def test_low_risk_does_not_require_trace(self):
        risk, matches = mod.classify(["README.md"], self.policy)
        self.assertEqual("low", risk)
        self.assertEqual([], matches)

    def test_high_risk_requires_trace(self):
        risk, matches = mod.classify([".github/workflows/ci.yml"], self.policy)
        self.assertEqual("high", risk)
        self.assertEqual(1, len(matches))
        self.assertFalse(mod.trace_changed([".github/workflows/ci.yml"], ".agents/evals/traces/"))

    def test_trace_must_be_changed_in_same_diff(self):
        changed = [".github/workflows/ci.yml", ".agents/evals/traces/task-123.json"]
        self.assertTrue(mod.trace_changed(changed, ".agents/evals/traces/"))

    def test_non_trace_json_does_not_satisfy_gate(self):
        changed = [".github/workflows/ci.yml", "config/task-123.json"]
        self.assertFalse(mod.trace_changed(changed, ".agents/evals/traces/"))

    def test_highest_risk_wins(self):
        risk, _ = mod.classify(["docs/agent.md", ".github/workflows/ci.yml"], self.policy)
        self.assertEqual("high", risk)

    def test_rejects_unknown_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.json"
            path.write_text(json.dumps({"schemaVersion": "bad", "rules": []}))
            with self.assertRaises(ValueError):
                mod.load_policy(path)


if __name__ == "__main__":
    unittest.main()
