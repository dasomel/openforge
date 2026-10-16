import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates/scripts/import-scorecard.py"
FIXTURES = ROOT / "tests/fixtures/security-readiness"
EVIDENCE = ROOT / "portfolio/security-readiness"
spec = importlib.util.spec_from_file_location("import_scorecard", SCRIPT)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
validator = adapter.load_validator()
REPO = "example/synthetic-repo"


def synthetic_raw():
    return json.loads((FIXTURES / "synthetic-scorecard-v5.json").read_text(encoding="utf-8"))


def synthetic_record():
    return json.loads((FIXTURES / "valid-synthetic.json").read_text(encoding="utf-8"))


def apply(raw=None, record=None):
    return adapter.apply_scorecard(record or synthetic_record(), adapter.parse_scorecard(raw or synthetic_raw(), REPO), "raw.json")


def signal(record, signal_id):
    return next(s for s in record["signals"] if s["id"] == signal_id)


def cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


class ParseRejectionTests(unittest.TestCase):
    def assertRejected(self, raw, fragment, repository=REPO):
        with self.assertRaises(adapter.ScorecardError) as ctx:
            adapter.parse_scorecard(raw, repository)
        self.assertIn(fragment, str(ctx.exception))

    def test_synthetic_input_parses(self):
        parsed = adapter.parse_scorecard(synthetic_raw(), REPO)
        self.assertEqual(parsed["observed_at"], "2026-10-02T00:00:00Z")
        self.assertEqual(parsed["version"], "v5.6.0")

    def test_wrong_format_rejected(self):
        self.assertRejected([], "not Scorecard JSON")
        self.assertRejected({"version": "2.1.0", "runs": []}, "not Scorecard JSON")

    def test_missing_or_empty_checks_rejected(self):
        raw = synthetic_raw()
        del raw["checks"]
        self.assertRejected(raw, "not Scorecard JSON")
        raw["checks"] = []
        self.assertRejected(raw, "non-empty list")
        raw["checks"] = "nope"
        self.assertRejected(raw, "non-empty list")

    def test_unsupported_major_version_rejected(self):
        for version in ("v4.13.1", "v6.0.0", "5.6.0", "latest"):
            raw = synthetic_raw()
            raw["scorecard"]["version"] = version
            self.assertRejected(raw, "version" if version in ("5.6.0", "latest") else "unsupported Scorecard major")

    def test_overall_score_out_of_range_rejected(self):
        for score in (10.5, -2, True, "7", None, float("nan")):
            raw = synthetic_raw()
            raw["score"] = score
            self.assertRejected(raw, "outside -1..10")

    def test_check_score_out_of_range_rejected(self):
        for score in (11, -2, 4.5, True, "3", None):
            raw = synthetic_raw()
            raw["checks"][0]["score"] = score
            self.assertRejected(raw, "check Code-Review")

    def test_repo_mismatch_rejected(self):
        self.assertRejected(synthetic_raw(), "does not match the record repository", repository="example/other-repo")
        raw = synthetic_raw()
        raw["repo"]["name"] = "gitlab.com/example/synthetic-repo"
        self.assertRejected(raw, "does not match the record repository")

    def test_bad_commit_and_date_rejected(self):
        raw = synthetic_raw()
        raw["repo"]["commit"] = "abc123"
        self.assertRejected(raw, "40-hex")
        raw = synthetic_raw()
        raw["date"] = "2026-10-02T09:00:00"
        self.assertRejected(raw, "no UTC offset")
        raw["date"] = "yesterday"
        self.assertRejected(raw, "not ISO 8601")

    def test_duplicate_or_unnamed_check_rejected(self):
        raw = synthetic_raw()
        raw["checks"].append(dict(raw["checks"][0]))
        self.assertRejected(raw, "duplicate check")
        raw = synthetic_raw()
        raw["checks"][0].pop("name")
        self.assertRejected(raw, "has no name")


class MappingTests(unittest.TestCase):
    def test_result_passes_validator(self):
        record, _ = apply()
        self.assertEqual(validator.validate(record, validator.parse_date("2026-10-15")), [])

    def test_overall_status_and_findings(self):
        record, _ = apply()
        scorecard = signal(record, "scorecard")
        self.assertEqual(scorecard["status"], "partial")
        self.assertEqual(scorecard["source"]["tool"], "openssf-scorecard")
        self.assertEqual(scorecard["source"]["version"], "v5.6.0")
        self.assertEqual(scorecard["source"]["observed_at"], "2026-10-02T00:00:00Z")
        self.assertIn("scanned commit fedcba9876543210fedcba9876543210fedcba98", scorecard["source"]["ref"])
        self.assertIn("scorecard commit 0123456", scorecard["source"]["ref"])
        ids = {f["id"]: f for f in scorecard["findings"]}
        self.assertEqual(set(ids), {f"synthetic-repo-scorecard-{n}" for n in ("code-review", "pinned-dependencies", "sbom", "synthetic-future-check", "vulnerabilities")})
        self.assertEqual(ids["synthetic-repo-scorecard-code-review"]["severity"], "high")
        self.assertEqual(ids["synthetic-repo-scorecard-synthetic-future-check"]["severity"], "info")

    def test_record_revision_untouched_and_observed_at_monotonic(self):
        record, _ = apply()
        self.assertEqual(record["revision"], synthetic_record()["revision"])
        self.assertEqual(record["observed_at"], "2026-10-02T00:00:00Z")
        older = synthetic_raw()
        older["date"] = "2026-09-01T00:00:00+00:00"
        later_record = synthetic_record()
        later_record["observed_at"] = "2026-10-01T00:00:00Z"
        record, _ = apply(older, later_record)
        self.assertEqual(record["observed_at"], "2026-10-01T00:00:00Z")

    def test_inconclusive_is_never_pass(self):
        record, _ = apply()
        sign = signal(record, "release-signing")  # absent from the synthetic record, Signed-Releases is -1
        self.assertEqual(sign["status"], "not-run")
        self.assertNotIn("findings", sign)
        self.assertIn("Inconclusive", signal(record, "scorecard")["note"])
        raw = synthetic_raw()
        raw["score"] = -1
        for check in raw["checks"]:
            check["score"] = -1
        record, _ = apply(raw)
        self.assertEqual(signal(record, "scorecard")["status"], "not-run")
        self.assertEqual(signal(record, "security-policy")["status"], "pass")  # directly observed, untouched
        self.assertEqual(validator.validate(record, validator.parse_date("2026-10-15")), [])

    def test_overall_minus_one_with_scored_checks_is_not_run(self):
        raw = synthetic_raw()
        raw["score"] = -1
        record, _ = apply(raw)
        self.assertEqual(signal(record, "scorecard")["status"], "not-run")

    def test_inconsistent_overall_score_rejected(self):
        raw = synthetic_raw()
        raw["checks"] = [c for c in raw["checks"] if c["score"] == 10]
        with self.assertRaises(adapter.ScorecardError):
            apply(raw)
        raw["checks"] = [{"name": "License", "score": -1, "reason": "x"}]
        with self.assertRaises(adapter.ScorecardError):
            apply(raw)

    def test_pass_only_when_everything_is_ten(self):
        raw = synthetic_raw()
        raw["checks"] = [c for c in raw["checks"] if c["score"] == 10]
        raw["score"] = 10
        self.assertEqual(signal(apply(raw)[0], "scorecard")["status"], "pass")
        raw["checks"].append({"name": "Fuzzing", "score": 9, "reason": "almost"})
        self.assertEqual(signal(apply(raw)[0], "scorecard")["status"], "partial")
        raw["score"] = 0
        self.assertEqual(signal(apply(raw)[0], "scorecard")["status"], "fail")

    def test_overall_ten_with_an_inconclusive_check_is_not_pass(self):
        raw = synthetic_raw()
        raw["score"] = 10
        raw["checks"] = [
            {"name": "License", "score": 10, "reason": "ok"},
            {"name": "Fuzzing", "score": -1, "reason": "internal error"},
        ]
        record, _ = apply(raw)
        sign = signal(record, "scorecard")
        self.assertEqual(sign["status"], "partial")
        self.assertEqual([f["id"] for f in sign["findings"]], ["synthetic-repo-scorecard-fuzzing"])
        self.assertIn("inconclusive", sign["findings"][0]["summary"])
        self.assertEqual(validator.validate(record, validator.parse_date("2026-10-15")), [])

    def test_directly_observed_signals_are_kept(self):
        record, notes = apply()
        original = synthetic_record()
        for signal_id in ("security-policy", "actions-pinning", "sbom"):
            self.assertEqual(signal(record, signal_id), signal(original, signal_id))
        self.assertEqual(len(notes), 3)

    def test_not_run_signal_is_filled_from_mapped_check(self):
        original = synthetic_record()
        signal(original, "security-policy").update(status="not-run")
        original["summary"].update({"pass": 0, "not_run": 2})
        record, notes = apply(record=original)
        filled = signal(record, "security-policy")
        self.assertEqual(filled["status"], "pass")
        self.assertIn("Derived from Scorecard Security-Policy 10/10", filled["note"])
        self.assertEqual(validator.validate(record, validator.parse_date("2026-10-15")), [])
        self.assertFalse(any("security-policy" in n for n in notes))

    def test_identical_reimport_is_a_noop(self):
        record, _ = apply()
        again, notes = apply(record=record)
        self.assertEqual(again, record)
        self.assertTrue(any("record unchanged" in n for n in notes))

    def test_legacy_signal_without_digest_is_refused(self):
        record, _ = apply()
        source = signal(record, "scorecard")["source"]
        source["ref"] = source["ref"].split("; checks digest")[0] + ")"
        with self.assertRaises(adapter.ScorecardError) as ctx:
            apply(record=record)
        self.assertIn("refusing to overwrite", str(ctx.exception))

    def test_measured_scorecard_signal_is_not_overwritten_by_a_different_input(self):
        record, _ = apply()
        changes = {
            "date": lambda raw: raw.update(date="2026-10-16T00:00:00Z"),
            "commit": lambda raw: raw["repo"].update(commit="f" * 40),
            "version": lambda raw: raw["scorecard"].update(version="v5.5.0"),
            "scorecard executable commit": lambda raw: raw["scorecard"].update(commit="e" * 40),
            "score": lambda raw: raw.update(score=10),
            "failing check": lambda raw: raw["checks"][1].update(score=0),
            "passing-check reason": lambda raw: raw["checks"][1].update(reason="changed"),
            "passing-check name": lambda raw: raw["checks"][1].update(name="Renamed"),
        }
        for label, change in changes.items():
            with self.subTest(change=label):
                raw = synthetic_raw()
                change(raw)
                with self.assertRaises(adapter.ScorecardError) as ctx:
                    apply(raw=raw, record=record)
                self.assertIn("refusing to overwrite", str(ctx.exception))

    def test_summary_is_recomputed(self):
        record, _ = apply()
        self.assertEqual(record["summary"], {"total": 5, "pass": 1, "fail": 1, "partial": 1, "not_run": 1, "not_applicable": 1})

    def test_signal_order_follows_contract(self):
        order = [s["id"] for s in apply()[0]["signals"]]
        self.assertEqual(order, [k for k in adapter.SIGNAL_ORDER if k in order])


class RealOutputTests(unittest.TestCase):
    """The committed samples are the adapter's output for the committed raw Scorecard files."""

    def reset_scorecard(self, name):
        record = json.loads((EVIDENCE / f"{name}.json").read_text(encoding="utf-8"))
        placeholder = {"id": "scorecard", "status": "not-run", "note": "placeholder", "source": {"tool": "curl", "observed_at": "2026-10-07T04:00:00Z", "ref": "placeholder"}}
        record["signals"] = [placeholder if s["id"] == "scorecard" else s for s in record["signals"]]
        # Latest non-Scorecard observation, e.g. a later direct re-scan of another signal.
        record["observed_at"] = max(s["source"]["observed_at"] for s in record["signals"] if s["id"] != "scorecard")
        return record

    def test_committed_samples_reproduce_from_raw_output(self):
        for name in ("narwhal", "kubemetal", "clusterdeck"):
            raw = json.loads((EVIDENCE / "scorecard" / f"{name}.json").read_text(encoding="utf-8"))
            parsed = adapter.parse_scorecard(raw, f"dasomel/{name}")
            self.assertEqual(parsed["version"], "v5.6.0")
            updated, _ = adapter.apply_scorecard(self.reset_scorecard(name), parsed, f"portfolio/security-readiness/scorecard/{name}.json")
            self.assertEqual(updated, json.loads((EVIDENCE / f"{name}.json").read_text(encoding="utf-8")), name)
            self.assertEqual(signal(updated, "scorecard")["status"], "partial")

    def test_real_inconclusive_checks_are_not_pass(self):
        raw = json.loads((EVIDENCE / "scorecard/narwhal.json").read_text(encoding="utf-8"))
        record = self.reset_scorecard("narwhal")
        record["signals"] = [s for s in record["signals"] if s["id"] != "release-signing"]
        record["summary"].update({"total": 5, "fail": 2})
        updated, _ = adapter.apply_scorecard(record, adapter.parse_scorecard(raw, "dasomel/narwhal"), "x.json")
        self.assertEqual(signal(updated, "release-signing")["status"], "not-run")  # Signed-Releases is -1 upstream
        self.assertIn("Packaging", signal(updated, "scorecard")["note"])

    def test_real_output_rejected_for_the_wrong_repository(self):
        raw = json.loads((EVIDENCE / "scorecard/narwhal.json").read_text(encoding="utf-8"))
        with self.assertRaises(adapter.ScorecardError):
            adapter.parse_scorecard(raw, "dasomel/kubemetal")


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.record = Path(self.tmp.name) / "record.json"
        self.record.write_text((FIXTURES / "valid-synthetic.json").read_text(encoding="utf-8"), encoding="utf-8")
        self.scorecard = Path(self.tmp.name) / "scorecard.json"
        self.scorecard.write_text((FIXTURES / "synthetic-scorecard-v5.json").read_text(encoding="utf-8"), encoding="utf-8")

    def test_dry_run_prints_and_does_not_write(self):
        before = self.record.read_text(encoding="utf-8")
        result = cli("--record", str(self.record), "--scorecard", str(self.scorecard))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout[result.stdout.index("{"):])["signals"][0]["status"], "partial")
        self.assertEqual(self.record.read_text(encoding="utf-8"), before)

    def test_write_updates_record_and_it_validates(self):
        result = cli("--write", "--record", str(self.record), "--scorecard", str(self.scorecard))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.record.read_text(encoding="utf-8"))["signals"][0]["status"], "partial")
        check = subprocess.run([sys.executable, str(ROOT / "templates/scripts/validate-security-readiness.py"), str(self.record)], capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stderr)

    def test_rejection_exits_nonzero_and_leaves_record_alone(self):
        raw = synthetic_raw()
        raw["scorecard"]["version"] = "v4.9.9"
        self.scorecard.write_text(json.dumps(raw), encoding="utf-8")
        before = self.record.read_text(encoding="utf-8")
        result = cli("--write", "--record", str(self.record), "--scorecard", str(self.scorecard))
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported Scorecard major version", result.stderr)
        self.assertEqual(self.record.read_text(encoding="utf-8"), before)

    def test_unreadable_input_exits_nonzero(self):
        self.scorecard.write_text("{not json", encoding="utf-8")
        result = cli("--record", str(self.record), "--scorecard", str(self.scorecard))
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot read JSON", result.stderr)

    def test_result_that_fails_validation_is_not_written(self):
        record = copy.deepcopy(synthetic_record())
        record["observed_at"] = "2099-01-01T00:00:00Z"  # future record: validator rejects, adapter must not write
        self.record.write_text(json.dumps(record), encoding="utf-8")
        before = self.record.read_text(encoding="utf-8")
        result = cli("--write", "--record", str(self.record), "--scorecard", str(self.scorecard))
        self.assertEqual(result.returncode, 1)
        self.assertIn("result would be invalid", result.stderr)
        self.assertEqual(self.record.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
