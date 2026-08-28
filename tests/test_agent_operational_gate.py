import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDER = ROOT / "templates/scripts/record-agent-event.py"
GATE = ROOT / "templates/scripts/agent-eval-gate.py"
BASELINE = ROOT / "templates/agent-eval/baseline.eval.json"


class AgentOperationalGateTests(unittest.TestCase):
    def record(self, trace, *args):
        return subprocess.run(
            ["python3", str(RECORDER), "--trace", str(trace), *args],
            text=True,
            capture_output=True,
        )

    def test_recorder_builds_incremental_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp) / "trace.json"
            first = self.record(trace, "--trace-id", "t1", "--type", "scope_check", "--summary", "scope")
            second = self.record(trace, "--type", "task_outcome", "--summary", "done", "--state", "A")
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            data = json.loads(trace.read_text())
            self.assertEqual([e["id"] for e in data["events"]], ["e1", "e2"])
            self.assertEqual(data["events"][1]["state"], "A")

    def test_gate_accepts_reference_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    "python3", str(GATE),
                    "--trace", str(ROOT / "templates/agent-eval/trace.example.json"),
                    "--baseline", str(BASELINE),
                    "--current-out", str(Path(tmp) / "current.json"),
                    "--comparison-out", str(Path(tmp) / "comparison.json"),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_gate_rejects_true_to_false_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp) / "trace.json"
            trace.write_text(json.dumps({
                "schemaVersion": "openforge-agent-trace/v1",
                "traceId": "regressed",
                "events": [
                    {"id": "e1", "type": "bug_fix", "summary": "changed"},
                    {"id": "e2", "type": "completion_claim", "summary": "done"},
                    {"id": "e3", "type": "task_outcome", "state": "A", "summary": "done"}
                ]
            }))
            result = subprocess.run(
                [
                    "python3", str(GATE),
                    "--trace", str(trace),
                    "--baseline", str(BASELINE),
                    "--current-out", str(Path(tmp) / "current.json"),
                    "--comparison-out", str(Path(tmp) / "comparison.json"),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 1)
            comparison = json.loads((Path(tmp) / "comparison.json").read_text())
            self.assertGreaterEqual(comparison["summary"]["regressions"], 1)


if __name__ == "__main__":
    unittest.main()
