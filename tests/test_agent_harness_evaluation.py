#!/usr/bin/env python3

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "templates" / "scripts" / "compare-agent-harness-runs.py"
EXAMPLE = ROOT / "templates" / "agent-eval" / "harness-dataset.example.json"
SCHEMA = ROOT / "schemas" / "agent-harness-dataset-v1.schema.json"


def load_module():
    spec = importlib.util.spec_from_file_location("compare_agent_harness_runs", str(SCRIPT))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


comparator = load_module()


class TestAgentHarnessEvaluation(unittest.TestCase):
    def setUp(self):
        self.dataset = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_schema_and_example_are_version_aligned(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(
            schema["properties"]["schemaVersion"]["const"],
            comparator.DATASET_SCHEMA,
        )
        self.assertEqual(comparator.validate_dataset(self.dataset), [])

    def test_example_produces_neutral_deterministic_summary(self):
        report = comparator.compare_datasets([self.dataset])
        self.assertEqual(report["schemaVersion"], comparator.COMPARISON_SCHEMA)
        self.assertEqual([item["harness"]["name"] for item in report["harnesses"]], ["harness-a", "harness-b"])
        self.assertEqual(report["harnesses"][0]["correctness"]["attempts"], 3)
        self.assertEqual(report["harnesses"][0]["correctness"]["successRate"], 0.666667)
        self.assertFalse(report["interpretation"]["winnerSelected"])
        self.assertNotIn("winner", report)

    def test_missing_metric_remains_null_with_zero_coverage(self):
        for run in self.dataset["runs"]:
            run["usage"]["reasoningTokens"] = None
        report = comparator.compare_datasets([self.dataset])
        for harness in report["harnesses"]:
            metric = harness["efficiency"]["reasoningTokens"]
            self.assertIsNone(metric["mean"])
            self.assertEqual(metric["observedRuns"], 0)
            self.assertEqual(metric["totalRuns"], 3)

    def test_mixed_cohorts_are_rejected(self):
        other = copy.deepcopy(self.dataset)
        other["datasetId"] = "other-dataset"
        other["cohort"]["repositoryRevision"] = "abcdef0123456789abcdef0123456789abcdef01"
        other["runs"] = []
        with self.assertRaisesRegex(ValueError, "does not match the controlled cohort"):
            comparator.compare_datasets([self.dataset, other])

    def test_invalid_tool_counts_are_rejected(self):
        self.dataset["runs"][0]["usage"]["failedToolCalls"] = 14
        errors = comparator.validate_dataset(self.dataset)
        self.assertTrue(any("cannot exceed toolCalls" in error for error in errors))

    def test_cost_requires_pricing_date(self):
        self.dataset["runs"][0]["usage"]["pricingDate"] = None
        errors = comparator.validate_dataset(self.dataset)
        self.assertTrue(any("pricingDate is required" in error for error in errors))

    def test_unknown_fields_and_invalid_revision_are_rejected(self):
        self.dataset["cohort"]["model"]["temperature"] = 0
        self.dataset["cohort"]["repositoryRevision"] = "main"
        errors = comparator.validate_dataset(self.dataset)
        self.assertTrue(any("temperature is not allowed" in error for error in errors))
        self.assertTrue(any("lowercase git SHA" in error for error in errors))

    def test_cli_accepts_example_and_rejects_invalid_input(self):
        valid = subprocess.run(
            [sys.executable, str(SCRIPT), str(EXAMPLE)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertEqual(json.loads(valid.stdout)["schemaVersion"], comparator.COMPARISON_SCHEMA)

        with tempfile.TemporaryDirectory() as directory:
            invalid_path = Path(directory) / "invalid.json"
            invalid = copy.deepcopy(self.dataset)
            invalid["schemaVersion"] = "unknown"
            invalid_path.write_text(json.dumps(invalid), encoding="utf-8")
            rejected = subprocess.run(
                [sys.executable, str(SCRIPT), str(invalid_path)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("schemaVersion", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
