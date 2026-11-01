import copy
import datetime as dt
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates/scripts/validate-external-contributions.py"
GENERATOR = ROOT / "templates/scripts/generate-portfolio.py"
FIXTURES = ROOT / "tests/fixtures/external-contributions"
REGISTRY = ROOT / "portfolio/external-contributions.json"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_module("validate_external_contributions", SCRIPT)
portfolio = load_module("openforge_portfolio_external", GENERATOR)

NOW = dt.datetime(2026, 10, 23, 12, 0, 0, tzinfo=dt.timezone.utc)
REPOS = {"example-org/example-repo"}


def fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def errors_for(doc, now=NOW, repos=REPOS):
    return validator.validate(doc, repos, now)


class ExternalContributionsTests(unittest.TestCase):
    def assertRejected(self, doc, fragment, **kwargs):
        errors = errors_for(doc, **kwargs)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def mutated(self, **changes):
        doc = fixture("valid-synthetic")
        doc["entries"][0].update(changes)
        return doc

    def test_valid_synthetic_fixture_passes(self):
        self.assertEqual(errors_for(fixture("valid-synthetic")), [])

    def test_committed_registry_is_valid(self):
        doc = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(doc["entries"]), 1)
        # Real clock: refreshing the committed snapshot must not require editing a pinned date.
        self.assertEqual(validator.validate(doc, None, dt.datetime.now(dt.timezone.utc)), [])

    def test_unknown_repository(self):
        self.assertRejected(self.mutated(repository="example-org/unknown", url="https://github.com/example-org/unknown/issues/7"), "not a portfolio project")

    def test_url_number_mismatch(self):
        self.assertRejected(self.mutated(number=8), "must equal")

    def test_url_kind_mismatch(self):
        self.assertRejected(self.mutated(kind="pull_request"), "must equal")

    def test_issue_cannot_be_merged(self):
        self.assertRejected(self.mutated(state="merged"), "cannot be merged")

    def test_bad_handle(self):
        for handle in ("-bad", "bad-", "do--uble", "has space", "x" * 40):
            with self.subTest(handle=handle):
                self.assertRejected(self.mutated(contributors=[handle]), "does not match")

    def test_email_and_at_prefix_rejected(self):
        for handle in ("someone@example.com", "@someone"):
            with self.subTest(handle=handle):
                self.assertRejected(self.mutated(contributors=[handle]), "store the bare GitHub handle")

    def test_empty_contributors(self):
        self.assertRejected(self.mutated(contributors=[]), "at least 1")

    def test_duplicate_id(self):
        doc = fixture("valid-synthetic")
        doc["entries"][1]["id"] = doc["entries"][0]["id"]
        self.assertRejected(doc, "duplicate id")

    def test_duplicate_thread(self):
        doc = fixture("valid-synthetic")
        second = copy.deepcopy(doc["entries"][0])
        second["id"] = "synthetic-duplicate"
        doc["entries"].insert(1, second)
        self.assertRejected(doc, "duplicate thread")

    def test_unsorted_entries(self):
        doc = fixture("valid-synthetic")
        doc["entries"].reverse()
        self.assertRejected(doc, "sorted")

    def test_future_record_observed_at(self):
        self.assertRejected(fixture("valid-synthetic"), "in the future", now=dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc))

    def test_entry_later_than_record(self):
        self.assertRejected(self.mutated(observed_at="2026-10-23T11:00:00Z"), "later than the record")

    def test_bad_enums(self):
        for field, value in (("kind", "discussion"), ("contribution_type", "praise"), ("state", "stale")):
            with self.subTest(field=field):
                self.assertRejected(self.mutated(**{field: value}), "not in")

    def test_unexpected_property_rejected(self):
        self.assertRejected(self.mutated(email="someone@example.com"), "unexpected property email")

    def test_cli_default_and_invalid_now(self):
        ok = subprocess.run([sys.executable, str(SCRIPT), str(FIXTURES / "valid-synthetic.json"), "--now", "2026-10-23T12:00:00Z"], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 1, ok.stdout)  # synthetic repo is not a portfolio project
        self.assertIn("not a portfolio project", ok.stderr)
        bad = subprocess.run([sys.executable, str(SCRIPT), "--now", "yesterday"], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)


class ExternalContributionsDashboardTests(unittest.TestCase):
    def test_committed_dashboard_block_matches_registry(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        block = json.loads((ROOT / "portfolio/dashboard.json").read_text(encoding="utf-8"))["external_contributions"]
        self.assertEqual(block["observed_at"], registry["observed_at"])
        self.assertEqual(block["summary"]["entries"], len(registry["entries"]))
        self.assertEqual(sum(block["summary"]["by_state"].values()), len(registry["entries"]))
        self.assertEqual([e["url"] for e in block["entries"]], [e["url"] for e in registry["entries"]])

    def test_existing_dashboard_keys_are_unchanged(self):
        committed = json.loads((ROOT / "portfolio/dashboard.json").read_text(encoding="utf-8"))
        names = ("projects", "relationships", "milestones", "maintenance", "agent-audit")
        docs = [portfolio.load_json(ROOT / "portfolio" / f"{n}.json") for n in names]
        security = portfolio.build_security_readiness_view()
        without = json.loads(portfolio.render_dashboard_json(*docs, security))
        self.assertEqual(without["version"], "openforge-dashboard/v1")
        self.assertEqual(committed["version"], "openforge-dashboard/v1")
        self.assertEqual({k: v for k, v in committed.items() if k != "external_contributions"}, without)

    def test_absent_registry_omits_key(self):
        self.assertIsNone(portfolio.build_external_contributions_view(ROOT / "portfolio/does-not-exist.json"))


    def test_table_cells_escape_pipes_and_newlines(self):
        view = portfolio.build_external_contributions_view()
        entry = copy.deepcopy(view["entries"][0])
        entry["summary"] = "a | b\nc"
        entry["outcome"] = "x|y"
        rows = [line for line in portfolio.render_external_contributions({**view, "entries": [entry]}) if line.startswith("| [")]
        self.assertEqual(len(rows), 1)
        self.assertIn("a \\| b c — outcome: x\\|y", rows[0])
    def test_wrong_contract_fails_loudly(self):
        bad = FIXTURES / "invalid-wrong-contract.json"
        with self.assertRaises(RuntimeError):
            portfolio.build_external_contributions_view(bad, ROOT)

    def test_markdown_section_states_snapshot_and_handles_only(self):
        text = (ROOT / "docs/portfolio-dashboard.md").read_text(encoding="utf-8")
        self.assertIn("## External contributions", text)
        self.assertIn("State is a snapshot as of", text)
        self.assertNotIn("@", text.split("## External contributions", 1)[1].split("## Status publication workflow", 1)[0])


if __name__ == "__main__":
    unittest.main()
