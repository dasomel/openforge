import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates/scripts/inventory-legacy-evidence.py"
spec = importlib.util.spec_from_file_location("inventory_legacy_evidence", SCRIPT)
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


def entry(**overrides):
    value = {
        "repository": "example",
        "path": "docs/report.md",
        "evidence_date": "2026-06-10",
        "evidence_class": "verification-quality",
        "evidence_strength": "measured",
        "environment_scope": "ci",
        "metrics_or_facts": "Recognized metrics extracted: 57 routes checked.",
        "limitations": "One historical snapshot.",
        "future_paper_use": "Verification snapshot.",
        "privacy_review": "public-ok",
        "availability": "committed",
    }
    value.update(overrides)
    return value


class LegacyEvidenceCatalogTests(unittest.TestCase):
    def test_schema_validation_accepts_good_entry(self):
        self.assertEqual(inventory.validate({"schema_version": "openforge-legacy-evidence-catalog/v1", "entries": [entry()], "pending_repositories": []}), [])

    def test_schema_validation_rejects_bad_enum(self):
        errors = inventory.validate({"schema_version": "openforge-legacy-evidence-catalog/v1", "entries": [entry(evidence_strength="invented")], "pending_repositories": []})
        self.assertTrue(any("invalid evidence_strength" in error for error in errors))

    def test_schema_validation_rejects_missing_required_field(self):
        value = entry()
        del value["limitations"]
        errors = inventory.validate({"schema_version": "openforge-legacy-evidence-catalog/v1", "entries": [value], "pending_repositories": []})
        self.assertIn("entries[0] missing limitations", errors)

    def test_prose_numbers_are_not_measured(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "docs" / "report.md"
            path.parent.mkdir()
            path.write_text("A qualitative standards note from 2014 discusses three design principles.", encoding="utf-8")
            found = inventory.discover(Path(directory), "example")
        self.assertEqual(len(found), 1)
        self.assertNotEqual(found[0]["evidence_strength"], "measured")

    def test_bare_body_year_is_not_evidence_date(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "docs" / "client-compatibility.md"
            path.parent.mkdir()
            path.write_text("This compatibility note dates from 2014 and contains no dated measurement.", encoding="utf-8")
            found = inventory.discover(Path(directory), "example")
        self.assertIsNone(found[0]["evidence_date"])

    def test_trace_without_recognized_metric_is_observed_with_fact(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".agents" / "evals" / "traces" / "pilot-001.json"
            path.parent.mkdir(parents=True)
            path.write_text('{"events":[{"summary":"completed step 1"}]}', encoding="utf-8")
            found = inventory.discover(Path(directory), "example")
        self.assertEqual(found[0]["evidence_strength"], "observed")
        self.assertIn("no recognized metric", found[0]["metrics_or_facts"])

    def test_pending_repositories_are_represented(self):
        catalog = json.loads((ROOT / "portfolio/legacy-evidence-catalog.json").read_text(encoding="utf-8"))
        pending = {
            entry["repository"]
            for entry in catalog["pending_repositories"]
        }
        # beluga, beluga-manager and siqoq were scanned once cloned locally (issue #89);
        # no repositories remain pending.
        self.assertEqual(pending, set())

    def test_output_is_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "docs" / "z-report.md").write_text("QA report: 2 checks passed.", encoding="utf-8")
            (root / "docs" / "a-report.md").write_text("QA report: 1 check passed.", encoding="utf-8")
            first = inventory.discover(root, "example")
            second = inventory.discover(root, "example")
        self.assertEqual(first, second)
        self.assertEqual([item["path"] for item in first], ["docs/a-report.md", "docs/z-report.md"])

    def test_issue_templates_are_excluded(self):
        self.assert_excluded(".github/ISSUE_TEMPLATE/bug_report.yml", "Bug report template")

    def test_workflow_definitions_are_excluded_from_both_locations(self):
        self.assert_excluded(".github/workflows/ci.yml", "QA workflow: 3 checks passed.")
        self.assert_excluded("templates/workflows/ci.yml", "QA workflow: 3 checks passed.")

    def test_dotfiles_are_excluded_even_inside_results(self):
        self.assert_excluded("results/.gitignore", "*.json\n")

    def test_fixture_and_testdata_paths_are_excluded(self):
        self.assert_excluded("tests/fixtures/compliance/good/docs/report.md", "QA report: 2 checks passed.")
        self.assert_excluded("component/testdata/report.md", "QA report: 2 checks passed.")

    def test_application_source_is_excluded(self):
        self.assert_excluded("src/components/BenchmarkCard.tsx", "Benchmark latency: 12 ms")
        self.assert_excluded("lib/benchmark.ts", "Benchmark latency: 12 ms")

    def test_tracked_file_is_committed_and_ignored_file_is_local_only(self):
        """A reader has to be able to tell an artifact they can fetch from one that exists
        only on the machine that scanned it."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
            (root / "results").mkdir()
            (root / ".gitignore").write_text("results/local-*.md\n", encoding="utf-8")
            (root / "results" / "shared-report.md").write_text("QA report: 6 pass; 4 fail.\n", encoding="utf-8")
            (root / "results" / "local-report.md").write_text("QA report: 6 pass; 4 fail.\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "results/shared-report.md"], check=True)
            found = {item["path"]: item for item in inventory.discover(root, "example")}
            self.assertEqual("committed", found["results/shared-report.md"]["availability"])
            self.assertEqual("local-only", found["results/local-report.md"]["availability"])
            self.assertIn("lost if discarded", found["results/local-report.md"]["limitations"])
            self.assertNotIn("lost if discarded", found["results/shared-report.md"]["limitations"])

    def test_non_git_directory_yields_unknown_availability(self):
        """Guessing `committed` outside a repository would be a claim nothing supports."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "results").mkdir()
            (root / "results" / "report.md").write_text("QA report: 6 pass; 4 fail.\n", encoding="utf-8")
            found = inventory.discover(root, "example")
            self.assertEqual(["unknown"], [item["availability"] for item in found])

    def test_validator_rejects_missing_or_unknown_availability(self):
        missing = entry()
        del missing["availability"]
        self.assertTrue(any("availability" in error for error in inventory.validate(
            {"schema_version": "openforge-legacy-evidence-catalog/v1", "entries": [missing], "pending_repositories": []})))
        self.assertTrue(any("availability" in error for error in inventory.validate(
            {"schema_version": "openforge-legacy-evidence-catalog/v1", "entries": [entry(availability="maybe")], "pending_repositories": []})))

    def test_enumerated_headings_are_not_metrics(self):
        """`Check 1` is a section heading. Counting it as a measurement is the same error as
        counting digits, one level down."""
        self.assertEqual([], inventory.recognised_metrics("Check 1\nCheck 2\nCheck 3\n", Path("qa.md")))
        self.assertEqual(["6 pass", "4 fail"], inventory.recognised_metrics("6 pass; 4 fail", Path("qa.md")))
        self.assertEqual(["checks: 23"], inventory.recognised_metrics("checks: 23", Path("qa.md")))

    def assert_excluded(self, relative_path, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / relative_path
            path.parent.mkdir(parents=True)
            path.write_text(text, encoding="utf-8")
            self.assertEqual(inventory.discover(Path(directory), "example"), [])


if __name__ == "__main__":
    unittest.main()
