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

    def test_status_repository_identity_mismatch_is_rejected(self):
        example = portfolio.load_json(ROOT / "templates" / "portfolio" / "status.example.json")
        example["repository"] = "someone/else"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "status.json"
            path.write_text(json.dumps(example), encoding="utf-8")
            errors = portfolio.validate_status_payload(path, self.projects, self.milestones)
        self.assertTrue(any("repository mismatch" in error for error in errors))

    def test_dashboard_and_graph_renderers_have_expected_sections(self):
        dashboard = portfolio.render_dashboard(self.projects, self.milestones)
        architecture = portfolio.render_architecture(self.projects, self.relationships)
        impact = portfolio.render_impact(self.projects, self.relationships)
        self.assertIn("OpenForge OSS Portfolio Dashboard", dashboard)
        self.assertIn("Narwhal Portal", dashboard)
        self.assertIn("flowchart TB", architecture)
        self.assertIn("adr-0013-agent-execution-security", impact)


if __name__ == "__main__":
    unittest.main()
