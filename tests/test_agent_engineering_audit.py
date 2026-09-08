import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "templates" / "scripts" / "audit-agent-engineering.py"
spec = importlib.util.spec_from_file_location("agent_audit", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class AgentEngineeringAuditTest(unittest.TestCase):
    def test_detects_commands_and_deterministic_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text(
                "Run lint and tests. Preserve architecture boundaries.\n", encoding="utf-8"
            )
            (root / "README.md").write_text("# demo\n", encoding="utf-8")
            (root / "package.json").write_text(
                json.dumps({"scripts": {"build": "next build", "test": "vitest", "lint": "eslint ."}}),
                encoding="utf-8",
            )
            result = module.audit(root, "owner/demo")
            self.assertEqual(result["repository"], "owner/demo")
            self.assertIn("AGENTS.md", result["instructions"])
            self.assertEqual(result["canonical_commands"]["build"], ["npm run build"])
            self.assertTrue(result["deterministic_controls"]["lint"])
            self.assertTrue(result["deterministic_controls"]["tests"])
            self.assertEqual(result["false_green_findings"], [])
            self.assertEqual(result["manual_review"]["high_risk_paths"], "review-required")

    def test_flags_instruction_only_false_green(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("Always run lint and tests.\n", encoding="utf-8")
            result = module.audit(root)
            self.assertIn(
                "agent instructions exist but no deterministic control was detected",
                result["false_green_findings"],
            )
            self.assertIn(
                "agent instructions reference linting but no lint owner was detected",
                result["false_green_findings"],
            )
            self.assertIn(
                "agent instructions reference tests but no test owner was detected",
                result["false_green_findings"],
            )

    def test_makefile_commands_are_discovered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Makefile").write_text("verify:\n\t@echo ok\n\ntest:\n\t@echo test\n", encoding="utf-8")
            result = module.audit(root)
            self.assertEqual(result["canonical_commands"]["verify"], ["make verify"])
            self.assertEqual(result["canonical_commands"]["test"], ["make test"])


if __name__ == "__main__":
    unittest.main()
