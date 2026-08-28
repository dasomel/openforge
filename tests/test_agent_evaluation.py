#!/usr/bin/env python3

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parent.parent / "templates" / "scripts"


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, str(SCRIPTS / filename))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


evaluator = load("evaluate_agent_trace", "evaluate-agent-trace.py")
comparator = load("compare_agent_evals", "compare-agent-evals.py")


class TestAgentEvaluation(unittest.TestCase):
    def trace(self, events):
        return {"schemaVersion": evaluator.TRACE_SCHEMA, "traceId": "t1", "events": events}

    def by_behavior(self, result):
        return {r["behavior"]: r for r in result["results"]}

    def test_complete_verified_bugfix_passes_applicable_behaviors(self):
        trace = self.trace([
            {"id": "e1", "type": "scope_check"},
            {"id": "e2", "type": "reproduction", "evidence": ["failure"]},
            {"id": "e3", "type": "bug_fix"},
            {"id": "e4", "type": "regression_verification", "evidence": ["pass"]},
            {"id": "e5", "type": "verification", "scope": "regression", "evidence": ["pass"]},
            {"id": "e6", "type": "completion_claim"},
            {"id": "e7", "type": "task_outcome", "state": "A"},
        ])
        result = evaluator.evaluate(trace)
        checks = self.by_behavior(result)
        self.assertEqual(checks["evidence-before-claim"]["outcome"], "true")
        self.assertEqual(checks["scope-discipline"]["outcome"], "true")
        self.assertEqual(checks["bug-fix-verification"]["outcome"], "true")
        self.assertEqual(checks["task-convergence"]["outcome"], "true")
        self.assertEqual(checks["trust-and-provenance"]["outcome"], "na")
        self.assertEqual(result["summary"]["failed"], 0)

    def test_completion_without_scoped_evidence_fails(self):
        result = evaluator.evaluate(self.trace([
            {"id": "e1", "type": "completion_claim"},
            {"id": "e2", "type": "task_outcome", "state": "A"},
        ]))
        self.assertEqual(self.by_behavior(result)["evidence-before-claim"]["outcome"], "false")

    def test_bugfix_requires_reproduction_and_regression(self):
        result = evaluator.evaluate(self.trace([
            {"id": "e1", "type": "bug_fix"},
            {"id": "e2", "type": "task_outcome", "state": "A"},
        ]))
        self.assertEqual(self.by_behavior(result)["bug-fix-verification"]["outcome"], "false")

    def test_progress_or_stop_requires_next_blocker(self):
        result = evaluator.evaluate(self.trace([
            {"id": "e1", "type": "task_outcome", "state": "B"},
        ]))
        self.assertEqual(self.by_behavior(result)["task-convergence"]["outcome"], "false")
        result = evaluator.evaluate(self.trace([
            {"id": "e1", "type": "task_outcome", "state": "C", "next": "Need external credential"},
        ]))
        self.assertEqual(self.by_behavior(result)["task-convergence"]["outcome"], "true")

    def test_external_input_requires_provenance_and_review(self):
        result = evaluator.evaluate(self.trace([
            {"id": "e1", "type": "external_input", "provenance": "https://example.test/spec", "reviewed": False},
            {"id": "e2", "type": "task_outcome", "state": "A"},
        ]))
        self.assertEqual(self.by_behavior(result)["trust-and-provenance"]["outcome"], "false")

    def test_trace_validation_rejects_duplicate_ids(self):
        errors = evaluator.validate_trace(self.trace([
            {"id": "e1", "type": "change"},
            {"id": "e1", "type": "verification"},
        ]))
        self.assertTrue(any("duplicate event id" in e for e in errors))

    def test_regression_comparison_detects_true_to_false(self):
        baseline = {
            "schemaVersion": comparator.EVAL_SCHEMA,
            "traceId": "before",
            "results": [{"behavior": "evidence-before-claim", "outcome": "true"}],
        }
        current = {
            "schemaVersion": comparator.EVAL_SCHEMA,
            "traceId": "after",
            "results": [{"behavior": "evidence-before-claim", "outcome": "false"}],
        }
        report = comparator.compare(baseline, current)
        self.assertEqual(report["summary"]["regressions"], 1)
        self.assertEqual(report["regressions"][0]["behavior"], "evidence-before-claim")


if __name__ == "__main__":
    unittest.main()
