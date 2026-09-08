import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates/scripts/check-agent-trace-evidence.py"
spec = importlib.util.spec_from_file_location("trace_evidence", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AgentTraceEvidenceTests(unittest.TestCase):
    def policy(self):
        return {"traceRequiredAt": ["high"], "rules": [{"risk": "high", "pattern": ".github/workflows/**"}, {"risk": "high", "pattern": "src/security/**"}]}

    def trace(self):
        return {
            "schemaVersion": "openforge-agent-trace/v1",
            "consistencyMode": "strict",
            "traceId": "t1",
            "task": "test",
            "changeContext": {"paths": [".github/workflows/**"]},
            "events": [
                {"id": "e1", "type": "verification", "scope": "workflow behavior", "status": "passed", "evidence": ["ci:workflow-pass"]},
                {"id": "e2", "type": "completion_claim", "summary": "complete"},
            ],
        }

    def test_high_risk_classification(self):
        self.assertEqual(mod.classify_high_risk(["README.md", ".github/workflows/ci.yml"], self.policy()), [".github/workflows/ci.yml"])

    def test_trace_glob_covers_changed_path(self):
        self.assertTrue(mod.trace_covers(self.trace(), ".github/workflows/ci.yml"))

    def test_rejects_missing_change_context(self):
        trace = self.trace(); trace.pop("changeContext")
        self.assertTrue(any("changeContext" in item for item in mod.validate_trace(trace, [".github/workflows/ci.yml"])))

    def test_rejects_untyped_verification_evidence(self):
        trace = self.trace(); trace["events"][0]["evidence"] = ["some-note"]
        self.assertTrue(any("typed evidence" in item for item in mod.validate_trace(trace, [".github/workflows/ci.yml"])))

    def test_rejects_unscoped_verification(self):
        trace = self.trace(); trace["events"][0].pop("scope")
        self.assertTrue(any("declare scope" in item for item in mod.validate_trace(trace, [".github/workflows/ci.yml"])))

    def test_rejects_uncovered_high_risk_path(self):
        self.assertTrue(any("uncovered high-risk paths" in item for item in mod.validate_trace(self.trace(), ["src/security/policy.py"])))

    def test_rejects_legacy_mode_for_relevant_high_risk_trace(self):
        trace = self.trace(); trace.pop("consistencyMode")
        self.assertTrue(any("consistencyMode" in item for item in mod.validate_trace(trace, [".github/workflows/ci.yml"])))

    def test_rejects_pending_verification(self):
        trace = self.trace(); trace["events"][0]["status"] = "pending"
        self.assertTrue(any("explicit passed status" in item for item in mod.validate_trace(trace, [".github/workflows/ci.yml"])))

    def test_unrelated_historical_trace_is_not_applicable(self):
        legacy = {"schemaVersion": "openforge-agent-trace/v1", "traceId": "legacy", "task": "old pilot", "events": []}
        results, failures = mod.assess_traces(["current.json", "legacy.json"], [self.trace(), legacy], [".github/workflows/ci.yml"])
        self.assertEqual(failures, [])
        self.assertEqual(results[1]["status"], "not-applicable")

    def test_valid_trace_passes(self):
        self.assertEqual(mod.validate_trace(self.trace(), [".github/workflows/ci.yml"]), [])


if __name__ == "__main__":
    unittest.main()
