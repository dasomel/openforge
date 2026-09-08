import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "templates" / "scripts" / "validate-doc-impact.py"
spec = importlib.util.spec_from_file_location("doc_impact", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class DocumentationImpactTest(unittest.TestCase):
    def test_updated_docs_must_be_in_changed_paths(self):
        payload = {
            "schemaVersion": "openforge-doc-impact/v1",
            "documentation": {"impact": "updated", "updated_paths": ["README.md"]},
            "blog_portfolio": {"impact": "none", "rationale": "internal refactor only"},
            "evidence": ["ci:test-pass"],
        }
        self.assertEqual(module.validate(payload, ["README.md", "src/main.go"]), [])
        errors = module.validate(payload, ["src/main.go"])
        self.assertTrue(any("not present in change" in error for error in errors))

    def test_follow_up_requires_tracking_issue(self):
        payload = {
            "schemaVersion": "openforge-doc-impact/v1",
            "documentation": {"impact": "follow-up-required"},
            "blog_portfolio": {"impact": "candidate", "candidate_topic": "runtime lesson"},
            "evidence": ["runtime:verified"],
        }
        errors = module.validate(payload, [])
        self.assertIn("documentation.tracking_issue is required for follow-up-required", errors)

    def test_none_requires_rationale_and_evidence(self):
        payload = {
            "schemaVersion": "openforge-doc-impact/v1",
            "documentation": {"impact": "none"},
            "blog_portfolio": {"impact": "none"},
            "evidence": [],
        }
        errors = module.validate(payload, [])
        self.assertIn("documentation.rationale is required when impact is none", errors)
        self.assertIn("blog_portfolio.rationale is required when impact is none", errors)
        self.assertIn("at least one evidence item is required", errors)


if __name__ == "__main__":
    unittest.main()
