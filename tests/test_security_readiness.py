import datetime as dt
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates/scripts/validate-security-readiness.py"
FIXTURES = ROOT / "tests/fixtures/security-readiness"
spec = importlib.util.spec_from_file_location("validate_security_readiness", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

TODAY = dt.date(2026, 10, 7)
NOW = dt.datetime(2026, 10, 7, 12, 0, 0, tzinfo=dt.timezone.utc)


def fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def errors_for(doc, today=TODAY, now=NOW):
    return validator.validate(doc, today, None, now)


def cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


class SecurityReadinessTests(unittest.TestCase):
    def assertRejected(self, name, fragment):
        errors = errors_for(fixture(name))
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_valid_synthetic_fixture_passes(self):
        self.assertEqual(errors_for(fixture("valid-synthetic")), [])

    def test_committed_portfolio_samples_pass(self):
        files = sorted((ROOT / "portfolio/security-readiness").glob("*.json"))
        self.assertGreaterEqual(len(files), 3)
        for path in files:
            self.assertEqual(validator.validate(json.loads(path.read_text(encoding="utf-8")), TODAY, path, NOW), [], path)

    def test_expired_exception_is_hard_error(self):
        self.assertRejected("invalid-expired-exception", "EXPIRED")

    def test_exception_expiring_today_is_still_valid(self):
        doc = fixture("valid-synthetic")
        doc["signals"][2]["exceptions"][0]["expires"] = "2026-10-07"
        doc["signals"][2]["exceptions"][0].pop("review_date")
        self.assertEqual(errors_for(doc), [])

    def test_missing_owner_rejected(self):
        self.assertRejected("invalid-missing-owner", "owner")

    def test_missing_rationale_and_expires_rejected(self):
        for key in ("rationale", "expires"):
            doc = fixture("valid-synthetic")
            del doc["signals"][2]["exceptions"][0][key]
            self.assertTrue(any(key in error for error in errors_for(doc)), key)

    def test_bad_status_rejected(self):
        self.assertRejected("invalid-bad-status", "not in")

    def test_summary_mismatch_rejected(self):
        self.assertRejected("invalid-summary-mismatch", "summary.pass")

    def test_unknown_signal_rejected(self):
        self.assertRejected("invalid-unknown-signal", "codeql")

    def test_fail_without_evidence_rejected(self):
        self.assertRejected("invalid-fail-without-evidence", "status fail needs")

    def test_missing_disclaimer_rejected(self):
        self.assertRejected("invalid-missing-disclaimer", "disclaimer")

    def test_pass_with_exception_is_contradiction(self):
        doc = fixture("valid-synthetic")
        sig = doc["signals"][2]
        sig["status"] = "pass"
        doc["summary"].update({"pass": 2, "fail": 0})
        self.assertTrue(any("contradicts" in error for error in errors_for(doc)))

    def test_not_run_must_not_carry_findings(self):
        doc = fixture("valid-synthetic")
        doc["signals"][0]["findings"] = [{"id": "SYN-9", "summary": "x", "severity": "low"}]
        self.assertTrue(any("not-run must not carry findings" in error for error in errors_for(doc)))

    def test_rescan_correlates_with_original_finding(self):
        doc = fixture("valid-synthetic")
        sig = doc["signals"][2]
        self.assertIn(sig["rescan"]["finding_ids"][0], [f["id"] for f in sig["findings"]])
        self.assertEqual(errors_for(doc), [])
        sig["rescan"]["previous_observed_at"] = sig["source"]["observed_at"]
        self.assertTrue(any("previous_observed_at" in error for error in errors_for(doc)))

    def test_secret_in_string_rejected(self):
        doc = fixture("valid-synthetic")
        doc["signals"][2]["findings"][0]["summary"] = "token=ghp_abcdefghijklmnopqrstuvwxyz0123456789"
        self.assertTrue(any("secret-pattern" in error for error in errors_for(doc)))

    def test_empty_default_set_fails(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(validator, "DEFAULT_DIR", Path(tmp)), mock.patch.object(sys, "argv", ["validate"]):
            self.assertEqual(validator.main(), 1)

    def test_empty_signals_rejected(self):
        doc = fixture("valid-synthetic")
        doc["signals"] = []
        doc["summary"] = {"total": 0, "pass": 0, "fail": 0, "partial": 0, "not_run": 0, "not_applicable": 0}
        self.assertTrue(any("at least 1" in error for error in errors_for(doc)))

    def test_invalid_calendar_datetime_rejected(self):
        doc = fixture("valid-synthetic")
        doc["observed_at"] = "2026-13-45T99:99:99Z"
        self.assertTrue(errors_for(doc))
        doc = fixture("valid-synthetic")
        doc["signals"][0]["source"]["observed_at"] = "2026-02-30T00:00:00Z"
        self.assertTrue(any("not a valid" in error for error in errors_for(doc)))

    def test_future_observed_at_rejected(self):
        doc = fixture("valid-synthetic")
        doc["observed_at"] = "2026-10-08T00:00:00Z"
        self.assertTrue(any("future" in error for error in errors_for(doc)))

    def test_source_later_than_record_rejected(self):
        doc = fixture("valid-synthetic")
        doc["signals"][0]["source"]["observed_at"] = "2026-10-02T00:00:00Z"
        self.assertTrue(any("later than the record" in error for error in errors_for(doc)))

    def test_cli_source_after_record_fails(self):
        result = cli("--today", "2026-10-07", "--now", "2026-10-07T12:00:00Z", str(FIXTURES / "invalid-source-after-record.json"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("source.observed_at is later than the record observed_at", result.stderr)

    def test_trailing_newline_rejected(self):
        for mutate in (lambda d: d.__setitem__("repository", "example/synthetic-repo\n"), lambda d: d.__setitem__("observed_at", "2026-10-01T00:00:00Z\n")):
            doc = fixture("valid-synthetic")
            mutate(doc)
            self.assertTrue(errors_for(doc))

    def test_pass_with_findings_rejected(self):
        doc = fixture("valid-synthetic")
        doc["signals"][1]["findings"] = [{"id": "SYN-8", "summary": "x", "severity": "low"}]
        self.assertTrue(any("pass contradicts having findings" in error for error in errors_for(doc)))

    def test_partial_without_findings_rejected(self):
        doc = fixture("valid-synthetic")
        doc["signals"][1]["status"] = "partial"
        doc["summary"].update({"pass": 0, "partial": 1})
        self.assertTrue(any("partial needs" in error for error in errors_for(doc)))

    def test_not_run_with_exceptions_rejected(self):
        doc = fixture("valid-synthetic")
        doc["signals"][0]["exceptions"] = [{"id": "SYN-EXC-9", "owner": "o", "rationale": "r", "expires": "2099-01-01"}]
        self.assertTrue(any("not-run must not carry exceptions" in error for error in errors_for(doc)))

    def test_dangling_finding_ids_rejected(self):
        doc = fixture("valid-synthetic")
        doc["signals"][2]["exceptions"][0]["finding_ids"] = ["NOPE-1"]
        self.assertTrue(any("exception SYN-EXC-1 references unknown finding" in error for error in errors_for(doc)))
        doc = fixture("valid-synthetic")
        doc["signals"][2]["rescan"]["finding_ids"] = ["NOPE-2"]
        self.assertTrue(any("rescan references unknown finding" in error for error in errors_for(doc)))

    def test_cli_exit_codes(self):
        ok = cli("--today", "2026-10-07", str(FIXTURES / "valid-synthetic.json"))
        self.assertEqual(ok.returncode, 0, ok.stderr)
        bad = cli("--today", "2026-10-07", str(FIXTURES / "invalid-expired-exception.json"))
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("EXPIRED", bad.stderr)

    def test_cli_today_makes_expiry_deterministic(self):
        late = cli("--today", "2100-01-01", str(FIXTURES / "valid-synthetic.json"))
        self.assertNotEqual(late.returncode, 0)
        self.assertIn("EXPIRED", late.stderr)

    def test_default_run_validates_portfolio_samples(self):
        result = cli("--validate")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_no_synthetic_data_under_portfolio(self):
        for path in (ROOT / "portfolio/security-readiness").glob("*.json"):
            self.assertNotIn("SYNTHETIC", path.read_text(encoding="utf-8"), path)
            self.assertNotIn("example/synthetic", path.read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
