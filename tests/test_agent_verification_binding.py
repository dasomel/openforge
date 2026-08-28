import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

binder = load("bind_agent_verification", ROOT / "templates/scripts/bind-agent-verification.py")
evaluator = load("evaluate_agent_trace_binding", ROOT / "templates/scripts/evaluate-agent-trace.py")

class VerificationBindingTests(unittest.TestCase):
    def trace(self):
        return {
            "schemaVersion": "openforge-agent-trace/v1",
            "traceId": "live-check",
            "consistencyMode": "strict",
            "events": [
                {"id":"e1","type":"scope_check"},
                {"id":"e2","type":"reproduction"},
                {"id":"e3","type":"bug_fix"},
                {"id":"e4","type":"regression_verification","status":"pending","scope":"live check","evidence":["ci:live"]},
                {"id":"e5","type":"verification","status":"pending","scope":"live check","evidence":["ci:live"]},
                {"id":"e6","type":"completion_claim"},
                {"id":"e7","type":"task_outcome","state":"A"},
            ],
        }

    def outcomes(self, trace):
        return {item["behavior"]: item["outcome"] for item in evaluator.evaluate(trace)["results"]}

    def test_success_binds_passed_and_allows_completion(self):
        trace = self.trace()
        completed, status = binder.bind(trace, ["e4", "e5"], [sys.executable, "-c", "raise SystemExit(0)"])
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(status, "passed")
        self.assertEqual(trace["events"][3]["status"], "passed")
        outcomes = self.outcomes(trace)
        self.assertEqual(outcomes["evidence-before-claim"], "true")
        self.assertEqual(outcomes["bug-fix-verification"], "true")
        self.assertEqual(outcomes["task-convergence"], "true")

    def test_failure_binds_failed_and_blocks_completion(self):
        trace = self.trace()
        completed, status = binder.bind(trace, ["e4", "e5"], [sys.executable, "-c", "raise SystemExit(7)"])
        self.assertEqual(completed.returncode, 7)
        self.assertEqual(status, "failed")
        outcomes = self.outcomes(trace)
        self.assertEqual(outcomes["evidence-before-claim"], "false")
        self.assertEqual(outcomes["bug-fix-verification"], "false")
        self.assertEqual(outcomes["task-convergence"], "false")

    def test_rejects_non_verification_target(self):
        with self.assertRaises(ValueError):
            binder.bind(self.trace(), ["e1"], [sys.executable, "-c", "raise SystemExit(0)"])

    def test_rejects_legacy_trace(self):
        trace = self.trace(); trace.pop("consistencyMode")
        with self.assertRaises(ValueError):
            binder.bind(trace, ["e5"], [sys.executable, "-c", "raise SystemExit(0)"])

if __name__ == "__main__":
    unittest.main()
