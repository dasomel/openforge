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
    def write_skill(self, root: Path, maturity: str) -> None:
        skill = root / ".agents" / "skills" / "demo-task"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(f"""---
name: demo-task
description: Perform the demo workflow. Use when the demo path changes.
metadata:
  openforge-scope: project
  openforge-owner: owner/demo
  openforge-maturity: {maturity}
  openforge-version: "1"
---
# Demo
""", encoding="utf-8")

    def write_verification_evidence(self, root: Path) -> None:
        evidence_dir = root / ".agents" / "skill-evals"
        evidence_dir.mkdir(parents=True)
        (evidence_dir / "demo-task.json").write_text(json.dumps({
            "schemaVersion": "openforge-agent-skill-verification/v1", "skill": "demo-task", "skillVersion": "1",
            "freshSession": True, "agentRuntime": "test-runtime",
            "happyPath": {"status": "passed", "scenario": "representative happy path", "evidence": ["test:happy"]},
            "edgeCase": {"status": "passed", "scenario": "representative edge case", "evidence": ["test:edge"]},
            "deterministicChecks": [{"command": "make verify", "status": "passed", "scope": "repository"}],
            "runtimeEvidence": [], "unverified": [], "verifiedAt": "2026-09-09",
        }), encoding="utf-8")

    def test_detects_commands_and_deterministic_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("Run lint and tests. Preserve architecture boundaries.\n", encoding="utf-8")
            (root / "README.md").write_text("# demo\n", encoding="utf-8")
            (root / "package.json").write_text(json.dumps({"scripts": {"build": "next build", "test": "vitest", "lint": "eslint ."}}), encoding="utf-8")
            result = module.audit(root, "owner/demo")
            self.assertEqual(result["repository"], "owner/demo")
            self.assertEqual(result["canonical_commands"]["build"], ["npm run build"])
            self.assertTrue(result["deterministic_controls"]["lint"])
            self.assertTrue(result["deterministic_controls"]["tests"])
            self.assertEqual(result["false_green_findings"], [])

    def test_flags_instruction_only_false_green(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("Always run lint and tests.\n", encoding="utf-8")
            result = module.audit(root)
            self.assertIn("agent instructions exist but no deterministic control was detected", result["false_green_findings"])
            self.assertIn("agent instructions reference linting but no lint owner was detected", result["false_green_findings"])
            self.assertIn("agent instructions reference tests but no test owner was detected", result["false_green_findings"])

    def test_makefile_commands_are_discovered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Makefile").write_text("verify:\n\t@echo ok\n\ntest:\n\t@echo test\n", encoding="utf-8")
            result = module.audit(root)
            self.assertEqual(result["canonical_commands"]["verify"], ["make verify"])
            self.assertEqual(result["canonical_commands"]["test"], ["make test"])

    def test_flags_swallowed_markdownlint_in_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".github" / "workflows"
            workflow.mkdir(parents=True)
            (workflow / "docs.yml").write_text("run: npx markdownlint-cli2 '**/*.md' || true\n", encoding="utf-8")
            result = module.audit(root)
            self.assertTrue(any(".github/workflows/docs.yml:1" in finding for finding in result["false_green_findings"]))

    def test_flags_swallowed_shellcheck_in_agent_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            commands = root / ".claude" / "commands"
            commands.mkdir(parents=True)
            (commands / "verify.md").write_text("shellcheck scripts/*.sh || :\n", encoding="utf-8")
            result = module.audit(root)
            self.assertTrue(any(".claude/commands/verify.md:1" in finding for finding in result["false_green_findings"]))

    def test_allows_expected_probe_and_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / ".github" / "workflows"
            workflow.mkdir(parents=True)
            (workflow / "diagnostics.yml").write_text("run: |\n  grep -q optional file || true\n  kubectl get pods -A || true\n", encoding="utf-8")
            result = module.audit(root)
            self.assertFalse(any("validator failure" in finding for finding in result["false_green_findings"]))

    def test_validator_without_swallow_is_not_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Makefile").write_text("lint:\n\tshellcheck scripts/*.sh\n", encoding="utf-8")
            result = module.audit(root)
            self.assertFalse(any("validator failure" in finding for finding in result["false_green_findings"]))

    def test_agent_skills_summary_tracks_draft_canonical_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
            self.write_skill(root, "draft")
            skills = module.audit(root, "owner/demo")["agent_skills"]
            self.assertEqual(skills["canonical_count"], 1)
            self.assertEqual(skills["maturity_counts"]["draft"], 1)
            self.assertFalse(skills["canonical"][0]["evidence_present"])

    def test_verified_skill_without_evidence_is_false_green(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
            self.write_skill(root, "verified")
            result = module.audit(root, "owner/demo")
            self.assertGreater(result["agent_skills"]["error_count"], 0)
            self.assertTrue(any("Agent Skills audit reports" in finding for finding in result["false_green_findings"]))

    def test_verified_skill_with_fresh_session_evidence_is_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
            self.write_skill(root, "verified")
            self.write_verification_evidence(root)
            skills = module.audit(root, "owner/demo")["agent_skills"]
            self.assertEqual(skills["error_count"], 0)
            self.assertEqual(skills["maturity_counts"]["verified"], 1)
            self.assertEqual(skills["evidence_backed_mature_count"], 1)


if __name__ == "__main__":
    unittest.main()
