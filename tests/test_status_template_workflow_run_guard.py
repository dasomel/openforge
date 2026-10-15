import unittest
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "templates/workflows/publish-openforge-status.yml"


class StatusTemplateWorkflowRunGuardTests(unittest.TestCase):
    """workflow_run matches the upstream workflow by name only; a fork PR can define a workflow
    with the same name. The template's workflow_run guidance must bind the run to this repository
    and a push, or downstream copies hand OPENFORGE_STATUS_TOKEN to fork runs (narwhal#397)."""

    def test_workflow_run_guidance_requires_push_from_same_repository(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for condition in (
            "github.event.workflow_run.conclusion == 'success'",
            "github.event.workflow_run.event == 'push'",
            "github.event.workflow_run.head_repository.full_name == github.repository",
        ):
            self.assertIn(condition, text)


if __name__ == "__main__":
    unittest.main()
