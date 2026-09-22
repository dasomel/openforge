import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates" / "scripts" / "generate-portfolio.py"
SPEC = importlib.util.spec_from_file_location("openforge_portfolio", SCRIPT)
assert SPEC and SPEC.loader
portfolio = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(portfolio)


class PortfolioControlPlaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projects = portfolio.load_json(ROOT / "portfolio" / "projects.json")
        cls.relationships = portfolio.load_json(ROOT / "portfolio" / "relationships.json")
        cls.milestones = portfolio.load_json(ROOT / "portfolio" / "milestones.json")
        cls.maintenance = portfolio.load_json(ROOT / "portfolio" / "maintenance.json")
        cls.agent_audit = portfolio.load_agent_audit(ROOT / "portfolio" / "agent-audit.json")

    def test_registry_is_valid(self):
        self.assertEqual(
            [],
            portfolio.validate_registry(self.projects, self.relationships, self.milestones),
        )

    def test_status_example_is_valid(self):
        path = ROOT / "templates" / "portfolio" / "status.example.json"
        self.assertEqual(
            [],
            portfolio.validate_status_payload(path, self.projects, self.milestones),
        )

    def test_unknown_relationship_target_fails_closed(self):
        relationships = json.loads(json.dumps(self.relationships))
        relationships["relationships"].append(
            {
                "source": "openforge",
                "target": "does-not-exist",
                "type": "standardizes",
                "impact": "high",
                "scope": "test",
            }
        )
        errors = portfolio.validate_registry(self.projects, relationships, self.milestones)
        self.assertTrue(any("unknown target" in error for error in errors))

    def test_new_project_with_unknown_architecture_category_fails_closed(self):
        projects = json.loads(json.dumps(self.projects))
        projects["projects"].append(
            {
                "id": "future-project",
                "repository": "dasomel/future-project",
                "name": "Future Project",
                "category": "Unregistered Architecture Category",
                "archetype": "Experiment",
                "development_status": "active",
                "adoption_percent": None,
                "role": "experiment",
                "domains": ["test"],
            }
        )
        errors = portfolio.validate_registry(projects, self.relationships, self.milestones)
        self.assertTrue(any("not assigned to any group" in error for error in errors))

    def test_architecture_category_cannot_belong_to_multiple_groups(self):
        projects = portfolio.project_map(self.projects)
        groups = {
            key: {
                "label": value["label"],
                "categories": set(value["categories"]),
            }
            for key, value in portfolio.ARCHITECTURE_GROUPS.items()
        }
        groups["Platform"]["categories"].add("Developer Tooling")
        _, errors = portfolio.architecture_assignments(projects, groups)
        self.assertTrue(any("belongs to multiple groups" in error for error in errors))
        self.assertTrue(any("egovframe-launcher" in error and "multiple groups" in error for error in errors))

    def test_status_repository_identity_mismatch_is_rejected(self):
        example = portfolio.load_json(ROOT / "templates" / "portfolio" / "status.example.json")
        example["repository"] = "someone/else"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "status.json"
            path.write_text(json.dumps(example), encoding="utf-8")
            errors = portfolio.validate_status_payload(path, self.projects, self.milestones)
        self.assertTrue(any("repository mismatch" in error for error in errors))

    def test_dashboard_and_graph_renderers_have_expected_sections(self):
        dashboard = portfolio.render_dashboard(self.projects, self.milestones, self.agent_audit)
        architecture = portfolio.render_architecture(self.projects, self.relationships)
        impact = portfolio.render_impact(self.projects, self.relationships)
        self.assertIn("OpenForge OSS Portfolio Dashboard", dashboard)
        self.assertIn("Narwhal Portal", dashboard)
        self.assertIn("flowchart TB", architecture)
        self.assertIn('siqoq["Siqoq\\nexperiment"]', architecture)
        self.assertIn("adr-0013-agent-execution-security", impact)

    def test_dashboard_exposes_revision_evidence_and_capability_verification(self):
        dashboard = portfolio.render_dashboard(self.projects, self.milestones, self.agent_audit)
        # A project with a recorded status/evidence gets a linked short-SHA revision
        # and a compact ci/security/runtime evidence summary.
        beluga = portfolio.project_map(self.projects)["beluga"]
        commit = beluga["status"]["evidence"]["commit"]
        revision = beluga["status"]["revision"]
        self.assertIn(f"[`{revision}`](https://github.com/{beluga['repository']}/commit/{commit})", dashboard)
        self.assertIn("ci: pass · security: pass · runtime: partial", dashboard)
        # Per-capability verification is rendered as a compact unit/integration/runtime/security summary.
        self.assertIn(
            "| Beluga Manager | `policy-compiler` | unit pass · integration pass · runtime pass · security pass |",
            dashboard,
        )
        # A project with no recorded status/evidence renders "—" rather than inventing a value.
        self.assertIn(
            "| [OpenForge](https://github.com/dasomel/openforge) | `portfolio-governance` | **active** | "
            "— | standards, governance, security, compliance, portfolio | — | — |",
            dashboard,
        )

    def test_fmt_revision_and_evidence_render_dash_when_absent(self):
        self.assertEqual(portfolio.fmt_revision({"repository": "org/repo"}), "—")
        self.assertEqual(portfolio.fmt_evidence({"repository": "org/repo"}), "—")
        self.assertEqual(portfolio.capability_verification_rows({"name": "X"}), [])

    def test_fmt_revision_without_commit_is_unlinked(self):
        project = {"repository": "org/repo", "status": {"revision": "abc1234"}}
        self.assertEqual(portfolio.fmt_revision(project), "`abc1234`")

    # -- agent_audit dashboard input (issue #39) --------------------------------------------

    @staticmethod
    def _agent_audit_fixture(repo_overrides=None):
        """A small synthetic agent-audit.json doc, shaped like portfolio/agent-audit.json."""
        repo_a = {
            "repository": "dasomel/repo-a",
            "revision": "a" * 40,
            "false_green_findings": ["stub test marked passing"],
            "deterministic_controls": {"formatting": True, "lint": True, "tests": False},
            "agent_skills": {
                "canonical_count": 2,
                "adapter_count": 1,
                "maturity_counts": {"draft": 1, "verified": 1, "stable": 0, "deprecated": 0, "unspecified": 0},
                "evidence_backed_mature_count": 1,
                "error_count": 1,
                "warning_count": 2,
            },
        }
        repo_b = {
            "repository": "dasomel/repo-b",
            "revision": "b" * 40,
            "false_green_findings": [],
            "deterministic_controls": {"formatting": True, "lint": True, "tests": True},
            "agent_skills": {
                "canonical_count": 1,
                "adapter_count": 0,
                "maturity_counts": {"draft": 0, "verified": 0, "stable": 1, "deprecated": 0, "unspecified": 0},
                "evidence_backed_mature_count": 1,
                "error_count": 0,
                "warning_count": 0,
            },
        }
        if repo_overrides:
            repo_a.update(repo_overrides.get("repo_a", {}))
            repo_b.update(repo_overrides.get("repo_b", {}))
        return {
            "schemaVersion": "openforge-agent-audit-matrix/v1",
            "priority_repositories": ["dasomel/repo-a", "dasomel/repo-b"],
            "repositories": [repo_a, repo_b],
        }

    def test_agent_audit_summary_matches_synthetic_fixture(self):
        view = portfolio.build_agent_audit_view(self._agent_audit_fixture())
        self.assertEqual(view["schema"], "openforge-agent-audit-matrix/v1")
        self.assertEqual(
            view["summary"],
            {
                "repositories": 2,
                "repositories_with_false_green": 1,
                "false_green_findings": 1,
                "canonical_skills": 3,
                "skill_maturity": {"draft": 1, "verified": 1, "stable": 1, "deprecated": 0, "unspecified": 0},
                "evidence_backed_mature_skills": 2,
                "skill_audit_errors": 1,
                "swallowed_failure_findings": None,
                "swallowed_failure_findings_measured_repositories": 0,
                "repositories_with_local_ci_gate": None,
                "local_ci_gate_measured_repositories": 0,
            },
        )
        self.assertEqual(
            [repo["repository"] for repo in view["repositories"]],
            ["dasomel/repo-a", "dasomel/repo-b"],
        )

    def test_repository_without_swallowed_failure_count_yields_null_not_zero(self):
        view = portfolio.build_agent_audit_view(self._agent_audit_fixture())
        for repo in view["repositories"]:
            self.assertIsNone(repo["swallowed_failure_count"])
        self.assertIsNone(view["summary"]["swallowed_failure_findings"])
        self.assertEqual(view["summary"]["swallowed_failure_findings_measured_repositories"], 0)

    def test_summary_sums_only_measured_repositories_and_reports_coverage(self):
        fixture = self._agent_audit_fixture()
        fixture["repositories"][0]["swallowed_failure_count"] = 3
        # repo-b deliberately left without the key: still unmeasured at this revision.
        view = portfolio.build_agent_audit_view(fixture)
        self.assertEqual(view["summary"]["swallowed_failure_findings"], 3)
        self.assertEqual(view["summary"]["swallowed_failure_findings_measured_repositories"], 1)
        self.assertEqual(view["repositories"][0]["swallowed_failure_count"], 3)
        self.assertIsNone(view["repositories"][1]["swallowed_failure_count"])

        gate = {"configured": True, "evidence": ".github/workflows/agent-contract-gate.yml", "reason": "gate-detected"}
        fixture["repositories"][1]["local_agent_ci_gate"] = gate
        view = portfolio.build_agent_audit_view(fixture)
        self.assertEqual(view["summary"]["repositories_with_local_ci_gate"], 1)
        self.assertEqual(view["summary"]["local_ci_gate_measured_repositories"], 1)
        self.assertIsNone(view["repositories"][0]["local_agent_ci_gate"])
        self.assertEqual(view["repositories"][1]["local_agent_ci_gate"], gate)

    def test_unconfigured_local_ci_gate_is_measured_but_not_counted(self):
        """A gate that was found and rejected must not count as a working gate.

        `local_agent_ci_gate` is an object, and every non-empty object is truthy -- including
        `{"configured": false}`, which is what the central audit emits for a workflow with no
        `pull_request` trigger or with its failure neutralized. Counting the object rather than
        its `configured` field would report a false green about false-green detection.
        """
        fixture = self._agent_audit_fixture()
        fixture["repositories"][0]["local_agent_ci_gate"] = {
            "configured": False,
            "evidence": ".github/workflows/ci.yml",
            "reason": "failure-neutralized",
        }
        fixture["repositories"][1]["local_agent_ci_gate"] = {
            "configured": True,
            "evidence": ".github/workflows/agent-contract-gate.yml",
            "reason": "gate-detected",
        }
        view = portfolio.build_agent_audit_view(fixture)
        self.assertEqual(view["summary"]["local_ci_gate_measured_repositories"], 2)
        self.assertEqual(view["summary"]["repositories_with_local_ci_gate"], 1)

    def test_declared_adr_count_matches_the_files_on_disk(self):
        """`adr_count` is published to the public dashboard, so it must be checkable.

        It was maintained by hand and read 13 while `docs/adr/` held 0001..0014. Counting the
        canonical files turns the next drift into a failing build instead of a wrong number on
        a public page.
        """
        self.assertEqual(
            self.projects["portfolio"]["adr_count"],
            portfolio.count_english_adrs(),
        )

    def test_adr_count_mismatch_is_a_registry_error(self):
        drifted = json.loads(json.dumps(self.projects))
        drifted["portfolio"]["adr_count"] = portfolio.count_english_adrs() + 1
        errors = portfolio.validate_registry(drifted, self.relationships, self.milestones)
        self.assertTrue(any("adr_count" in error for error in errors), errors)

    def test_dashboard_json_version_and_generated_from(self):
        output = json.loads(
            portfolio.render_dashboard_json(
                self.projects, self.relationships, self.milestones, self.maintenance, self.agent_audit
            )
        )
        self.assertEqual(output["version"], "openforge-dashboard/v1")
        self.assertEqual(
            output["generated_from"],
            [
                "portfolio/projects.json",
                "portfolio/relationships.json",
                "portfolio/milestones.json",
                "portfolio/maintenance.json",
                "portfolio/agent-audit.json",
            ],
        )
        self.assertIn("agent_audit", output)

    def test_missing_agent_audit_input_fails_loudly(self):
        with self.assertRaises(RuntimeError):
            portfolio.load_agent_audit(ROOT / "portfolio" / "does-not-exist.json")

    def test_unparseable_agent_audit_input_fails_loudly(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "agent-audit.json"
            path.write_text("{not valid json", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                portfolio.load_agent_audit(path)

    def test_checked_in_dashboard_json_round_trips(self):
        regenerated = portfolio.render_dashboard_json(
            self.projects, self.relationships, self.milestones, self.maintenance, self.agent_audit
        )
        checked_in = (ROOT / "portfolio" / "dashboard.json").read_text(encoding="utf-8")
        self.assertEqual(checked_in, regenerated)


if __name__ == "__main__":
    unittest.main()
