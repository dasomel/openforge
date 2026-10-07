import datetime as dt
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates/scripts/validate-security-readiness.py"
FIXTURES = ROOT / "tests/fixtures/security-readiness"
spec = importlib.util.spec_from_file_location("validate_security_readiness", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

TODAY = dt.date(2026, 10, 7)


def fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def errors_for(doc, today=TODAY):
    return validator.validate(doc, today)


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
            self.assertEqual(validator.validate(json.loads(path.read_text(encoding="utf-8")), TODAY, path), [], path)

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
