import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates/scripts/generate-portfolio.py"
EVIDENCE = ROOT / "portfolio/security-readiness"
spec = importlib.util.spec_from_file_location("openforge_portfolio_security", SCRIPT)
portfolio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(portfolio)

REPOS = ("clusterdeck", "kubemetal", "narwhal")
INPUTS = ("projects", "relationships", "milestones", "maintenance", "agent-audit")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def render(security_readiness):
    docs = [portfolio.load_json(ROOT / "portfolio" / f"{name}.json") for name in INPUTS]
    return json.loads(portfolio.render_dashboard_json(*docs, security_readiness))


class SecurityReadinessDashboardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.directory = self.root / "portfolio/security-readiness"
        shutil.copytree(EVIDENCE, self.directory)

    def view(self):
        return portfolio.build_security_readiness_view(self.directory, self.root)

    def test_committed_dashboard_has_per_repository_summary(self):
        block = load(ROOT / "portfolio/dashboard.json")["security_readiness"]
        self.assertEqual([r["repository"] for r in block["repositories"]], [f"dasomel/{n}" for n in REPOS])
        self.assertEqual(block["summary"]["repositories"], 3)
        for repo in block["repositories"]:
            name = repo["repository"].split("/")[1]
            self.assertEqual(repo["evidence"], {"record": f"portfolio/security-readiness/{name}.json", "scorecard": f"portfolio/security-readiness/scorecard/{name}.json"})
            for rel in repo["evidence"].values():
                self.assertTrue((ROOT / rel).is_file(), rel)
            raw = load(ROOT / repo["evidence"]["scorecard"])
            self.assertEqual(repo["scorecard"]["score"], raw["score"])
            self.assertEqual(repo["scorecard"]["commit"], raw["repo"]["commit"])
            self.assertEqual(repo["scorecard"]["tool_version"], raw["scorecard"]["version"])
            record = load(ROOT / repo["evidence"]["record"])
            self.assertEqual(repo["signal_counts"], {"total": len(record["signals"]), **{k: v for k, v in record["summary"].items() if k != "total"}})
            self.assertEqual(repo["signal_status"], {s["id"]: s["status"] for s in record["signals"]})
        totals = block["summary"]["signals"]
        self.assertEqual(totals["total"], sum(v for k, v in totals.items() if k != "total"))
        self.assertEqual(sum(block["summary"]["overall"].values()), 3)

    def test_existing_dashboard_keys_are_unchanged(self):
        committed = load(ROOT / "portfolio/dashboard.json")
        without = render(None)
        self.assertNotIn("security_readiness", without)
        self.assertEqual(without["version"], "openforge-dashboard/v1")
        self.assertEqual(committed["version"], "openforge-dashboard/v1")
        with_block = {k: v for k, v in committed.items() if k not in ("security_readiness", "external_contributions")}
        self.assertEqual(with_block, without)
        self.assertEqual(set(committed) - set(without), {"security_readiness", "external_contributions"})

    def test_no_evidence_omits_the_key(self):
        shutil.rmtree(self.directory)
        self.assertIsNone(self.view())

    def test_markdown_section_links_to_sources(self):
        text = (ROOT / "docs/portfolio-dashboard.md").read_text(encoding="utf-8")
        self.assertIn("## Security readiness", text)
        for name in REPOS:
            self.assertIn(f"(../portfolio/security-readiness/scorecard/{name}.json)", text)
        bare = portfolio.render_dashboard(*[portfolio.load_json(ROOT / "portfolio" / f"{n}.json") for n in ("projects", "milestones", "agent-audit")])
        self.assertNotIn("## Security readiness", bare)

    def test_not_run_scorecard_has_null_score_and_no_raw_link(self):
        record = load(self.directory / "narwhal.json")
        scorecard = next(s for s in record["signals"] if s["id"] == "scorecard")
        scorecard.clear()
        scorecard.update({"id": "scorecard", "status": "not-run", "note": "n", "source": {"tool": "curl", "observed_at": "2026-10-07T04:58:44Z", "ref": "x"}})
        (self.directory / "narwhal.json").write_text(json.dumps(record), encoding="utf-8")
        (self.directory / "scorecard/narwhal.json").unlink()
        repo = next(r for r in self.view()["repositories"] if r["repository"].endswith("narwhal"))
        self.assertIsNone(repo["scorecard"]["score"])
        self.assertEqual(repo["scorecard"]["status"], "not-run")
        self.assertIsNone(repo["evidence"]["scorecard"])

    def test_raw_scorecard_drift_fails_loudly(self):
        raw_path = self.directory / "scorecard/kubemetal.json"
        raw = load(raw_path)
        raw["date"] = "2026-10-16T00:00:00+00:00"
        raw_path.write_text(json.dumps(raw), encoding="utf-8")
        with self.assertRaises(RuntimeError) as ctx:
            self.view()
        self.assertIn("does not match", str(ctx.exception))

    def mutate_raw(self, name, change):
        raw_path = self.directory / f"scorecard/{name}.json"
        raw = load(raw_path)
        change(raw)
        raw_path.write_text(json.dumps(raw), encoding="utf-8")

    def test_raw_scorecard_score_drift_fails_loudly(self):
        for name in REPOS:
            with self.subTest(name=name):
                shutil.copyfile(EVIDENCE / f"scorecard/{name}.json", self.directory / f"scorecard/{name}.json")
                self.mutate_raw(name, lambda raw: raw.update(score=10))
                with self.assertRaises(RuntimeError) as ctx:
                    self.view()
                self.assertIn("does not match", str(ctx.exception))

    def test_raw_scorecard_check_drift_fails_loudly(self):
        changes = {
            "score to 0": lambda check: check.update(score=0),
            "score to -1": lambda check: check.update(score=-1),
            "rename": lambda check: check.update(name=check["name"] + "-X"),
        }
        for label, change in changes.items():
            with self.subTest(change=label):
                shutil.copyfile(EVIDENCE / "scorecard/kubemetal.json", self.directory / "scorecard/kubemetal.json")
                self.mutate_raw("kubemetal", lambda raw: change(next(c for c in raw["checks"] if c["score"] == 10)))
                with self.assertRaises(RuntimeError) as ctx:
                    self.view()
                self.assertIn("does not match", str(ctx.exception))

    def test_missing_raw_scorecard_fails_loudly(self):
        (self.directory / "scorecard/clusterdeck.json").unlink()
        with self.assertRaises(RuntimeError) as ctx:
            self.view()
        self.assertIn("is missing", str(ctx.exception))

    def test_stray_raw_scorecard_fails_loudly(self):
        record = load(self.directory / "narwhal.json")
        next(s for s in record["signals"] if s["id"] == "scorecard")["source"]["tool"] = "curl"
        (self.directory / "narwhal.json").write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaises(RuntimeError):
            self.view()

    def test_score_out_of_range_and_bad_record_fail_loudly(self):
        raw_path = self.directory / "scorecard/narwhal.json"
        raw = load(raw_path)
        raw["score"] = 11
        raw_path.write_text(json.dumps(raw), encoding="utf-8")
        with self.assertRaises(RuntimeError):
            self.view()
        shutil.copyfile(EVIDENCE / "scorecard/narwhal.json", raw_path)
        record = load(self.directory / "kubemetal.json")
        record["schema_version"] = "other/v9"
        (self.directory / "kubemetal.json").write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaises(RuntimeError):
            self.view()

    def test_overall_rollup_never_calls_not_run_a_pass(self):
        base = {"pass": 0, "fail": 0, "partial": 0, "not_run": 0, "not_applicable": 0}
        cases = [
            ({"pass": 3}, "pass"), ({"pass": 2, "not_run": 1}, "partial"), ({"pass": 1, "partial": 1}, "partial"),
            ({"pass": 5, "fail": 1}, "fail"), ({"not_run": 2}, "not-run"), ({"not_applicable": 1}, "not-applicable"),
            ({"pass": 1, "not_applicable": 2}, "pass"),
        ]
        for counts, expected in cases:
            self.assertEqual(portfolio.security_overall({**base, **counts}), expected, counts)

    def test_generated_outputs_are_current(self):
        files = portfolio.generated_files(*[portfolio.load_json(ROOT / "portfolio" / f"{n}.json") for n in INPUTS[:4]], portfolio.load_agent_audit(ROOT / "portfolio/agent-audit.json"))
        for path, content in files.items():
            self.assertEqual(path.read_text(encoding="utf-8"), content, path)


if __name__ == "__main__":
    unittest.main()
