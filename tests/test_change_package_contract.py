import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ChangePackageContractTests(unittest.TestCase):
    def test_change_template_preserves_required_contract_sections(self):
        template = (ROOT / "templates/change/CHANGE.md").read_text(encoding="utf-8")

        required = (
            "## Problem",
            "## Intent",
            "## Scope",
            "## Non-goals",
            "## Requirements",
            "## Acceptance scenarios",
            "## Architecture and decisions",
            "## Change impact",
            "## Verification plan",
            "## Rollout, rollback and recovery",
            "## Evidence and durable synchronization",
            "## Review record",
            "`REQ-001`",
            "`AC-001`",
        )

        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, template)

    def test_task_template_keeps_requirement_and_evidence_traceability(self):
        template = (ROOT / "templates/change/TASKS.md").read_text(encoding="utf-8")

        for marker in ("(`REQ-___`)", "(`AC-___`)", "## Verify", "## Completion review"):
            with self.subTest(marker=marker):
                self.assertIn(marker, template)

    def test_workflow_surfaces_link_to_the_change_contract(self):
        standard = (ROOT / "docs/change-management.md").read_text(encoding="utf-8")
        pull_request = (ROOT / ".github/pull_request_template.md").read_text(encoding="utf-8")
        feature_issue = (ROOT / ".github/ISSUE_TEMPLATE/feature_request.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("Class C MUST use a Change Package", standard)
        self.assertIn("Class D MUST use a Change Package", standard)
        self.assertIn("Change Package:", pull_request)
        self.assertIn("Acceptance scenarios verified:", pull_request)
        self.assertIn("id: requirements", feature_issue)
        self.assertIn("id: verification", feature_issue)


if __name__ == "__main__":
    unittest.main()
