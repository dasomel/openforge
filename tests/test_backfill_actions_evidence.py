"""Regression coverage for the GitHub Actions research evidence backfill (fixture JSON, no network)."""

import datetime as dt
import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "templates/scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def make_repo(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "remote", "add", "origin", "https://github.com/example/project.git")
    (tmp_path / "README.md").write_text("fixture\n")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "-qm", "main commit")
    main_sha = git(tmp_path, "rev-parse", "HEAD")
    git(tmp_path, "update-ref", "refs/remotes/origin/main", main_sha)
    git(tmp_path, "checkout", "-qb", "side")
    (tmp_path / "side.txt").write_text("side\n")
    git(tmp_path, "add", "side.txt")
    git(tmp_path, "commit", "-qm", "side commit")
    return main_sha, git(tmp_path, "rev-parse", "HEAD")


def run(sha, run_id, conclusion="success", **extra):
    base = {"id": run_id, "name": "CI", "path": ".github/workflows/ci.yml", "head_sha": sha,
            "head_branch": "main", "event": "push", "status": "completed", "conclusion": conclusion,
            "run_attempt": 1, "run_started_at": "2026-08-03T10:00:00Z", "updated_at": "2026-08-03T10:01:30Z"}
    base.update(extra)
    return base


class TestBackfillActionsEvidence(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.tmp_path = pathlib.Path(self.temporary.name) / "repo"
        self.main_sha, self.side_sha = make_repo(self.tmp_path)
        self.backfill = load("backfill-actions-evidence")

    def convert(self, runs, since=None, known=frozenset()):
        return self.backfill.convert(runs, self.tmp_path, "example/project", since, set(known),
                                     backfilled_at="2026-11-05T00:00:00Z")

    def test_mapping_and_exclusions(self):
        runs = [
            run(self.main_sha, 1),
            run(self.main_sha, 2, "failure", run_attempt=3, name="Release: v1 #2", path=".github/workflows/release.yml"),
            run(self.main_sha, 3, "cancelled", name="Deploy Pages", updated_at="2026-08-03T09:00:00Z"),
            run(self.main_sha, 4, "action_required"),
            run(self.main_sha, 5, None),
            run(self.side_sha, 6),
            run(self.main_sha, 7, status="in_progress"),
            run(self.main_sha, 8, "neutral", name="Docker image"),
        ]
        records, stats = self.convert(runs)
        self.assertEqual((stats["fetched"], stats["included"], stats["excluded_other"],
                          stats["excluded_not_on_main"]), (7, 4, 2, 1))
        first, second, third, fourth = records
        self.assertEqual((first["result"], first["duration_ms"], first["event_type"], first["task_or_test"]),
                         ("pass", 90000, "test", "gha:CI"))
        self.assertEqual((second["result"], second["attempt"], second["ci_retries"], second["event_type"]),
                         ("fail", 3, 2, "release"))
        self.assertEqual(second["task_or_test"], "gha:Release: v1 -2")
        self.assertEqual((third["result"], third["duration_ms"], third["event_type"]), ("cancelled", None, "deploy"))
        self.assertEqual((fourth["result"], fourth["event_type"]), ("skipped", "build"))
        self.assertEqual(first["metadata"]["gh_run_id"], 1)
        self.assertIs(first["metadata"]["head_branch_is_default"], True)

    def test_since_and_idempotence(self):
        runs = [run(self.main_sha, 1), run(self.main_sha, 2, run_started_at="2026-07-01T00:00:00Z")]
        records, stats = self.convert(runs, since=dt.date(2026, 8, 1))
        self.assertEqual((len(records), stats["excluded_since"]), (1, 1))
        records, stats = self.convert(runs, known={(1, 1)})
        self.assertEqual((len(records), stats["skipped_existing"]), (1, 1))

    def test_write_groups_by_month_and_appends(self):
        runs = [run(self.main_sha, 1, run_started_at="2026-09-02T00:00:00Z"),
                run(self.main_sha, 2, run_started_at="2026-08-02T00:00:00Z")]
        records, _ = self.convert(runs)
        out = self.tmp_path / "out"
        out.mkdir()
        (out / "2026-08.jsonl").write_text("legacy\n")
        self.backfill.write_records(records, out)
        self.assertEqual(sorted(path.name for path in out.glob("*.jsonl")), ["2026-08.jsonl", "2026-09.jsonl"])
        lines = (out / "2026-08.jsonl").read_text().splitlines()
        self.assertEqual(lines[0], "legacy")
        self.assertEqual(json.loads(lines[1])["metadata"]["gh_run_id"], 2)

    def test_unknown_counters_are_explicitly_unobserved(self):
        records, _ = self.convert([run(self.main_sha, 1)])
        meta = records[0]["metadata"]
        self.assertIs(meta.get("human_interventions_observed"), False)
        self.assertIs(meta.get("review_corrections_observed"), False)
        self.assertEqual(meta.get("duration_semantics"), "workflow_update_interval")

    def test_duplicate_run_in_response_is_written_once(self):
        records, stats = self.convert([run(self.main_sha, 1), run(self.main_sha, 1)])
        self.assertEqual(len(records), 1)
        self.assertEqual(stats["skipped_existing"], 1)

    def test_missing_main_ref_aborts_instead_of_excluding_every_run(self):
        git(self.tmp_path, "update-ref", "-d", "refs/remotes/origin/main")
        with self.assertRaises(subprocess.CalledProcessError):
            self.convert([run(self.main_sha, 1)])

    def test_unterminated_file_is_rejected_without_changing_any_file(self):
        out = self.tmp_path / "out"
        out.mkdir()
        legacy = out / "2026-09.jsonl"
        legacy.write_bytes(b'{"legacy":true}')
        records, _ = self.convert([
            run(self.main_sha, 1, run_started_at="2026-08-01T00:00:00Z"),
            run(self.main_sha, 2, run_started_at="2026-09-01T00:00:00Z"),
        ])
        with self.assertRaises(ValueError):
            self.backfill.write_records(records, out)
        self.assertEqual(legacy.read_bytes(), b'{"legacy":true}')
        self.assertFalse((out / "2026-08.jsonl").exists())

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "jsonschema not installed")
    def test_generated_records_pass_validator(self):
        validation = self.backfill.checker()
        runs = [run(self.main_sha, 1), run(self.main_sha, 2, "timed_out", name="a" * 300)]
        records, _ = self.convert(runs)
        self.assertEqual(len(records), 2)
        for record in records:
            self.assertEqual(validation.record_errors(record, self.tmp_path, "example/project"), [])
        bad = dict(records[0], environment="bad env")
        self.assertTrue(validation.record_errors(bad, self.tmp_path, "example/project"))
        self.assertEqual(self.backfill.existing_keys(self.tmp_path), set())


if __name__ == "__main__":
    unittest.main()
