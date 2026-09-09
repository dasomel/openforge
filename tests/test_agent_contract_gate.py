"""Tests for the issue #72 repository-local agent-contract gate.

Covers: audit-agent-skills.py --strict escalation (D1), SKILL-MATURITY-MISSING (D2),
SKILL-VERIFICATION-COMMAND-OWNER (D3), and audit-agent-engineering.py's
detect_local_agent_gate second-line detection (D6).
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

SKILLS_SCRIPT = Path(__file__).resolve().parents[1] / "templates" / "scripts" / "audit-agent-skills.py"
SKILLS_SPEC = importlib.util.spec_from_file_location("audit_agent_skills_gate", SKILLS_SCRIPT)
assert SKILLS_SPEC and SKILLS_SPEC.loader
AUDIT = importlib.util.module_from_spec(SKILLS_SPEC)
sys.modules[SKILLS_SPEC.name] = AUDIT
SKILLS_SPEC.loader.exec_module(AUDIT)

ENGINEERING_SCRIPT = Path(__file__).resolve().parents[1] / "templates" / "scripts" / "audit-agent-engineering.py"
ENGINEERING_SPEC = importlib.util.spec_from_file_location("audit_agent_engineering_gate", ENGINEERING_SCRIPT)
assert ENGINEERING_SPEC and ENGINEERING_SPEC.loader
ENGINEERING = importlib.util.module_from_spec(ENGINEERING_SPEC)
sys.modules[ENGINEERING_SPEC.name] = ENGINEERING
ENGINEERING_SPEC.loader.exec_module(ENGINEERING)


class SkillsGateFixtureMixin:
    def make_repo(
        self,
        maturity: str | None = "draft",
        claude_text: str = "@AGENTS.md\n",
        include_skill: bool = True,
    ) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
        (root / "CLAUDE.md").write_text(claude_text, encoding="utf-8")
        if not include_skill:
            return root
        skill = root / ".agents" / "skills" / "demo-task"
        skill.mkdir(parents=True)
        maturity_line = f"  openforge-maturity: {maturity}\n" if maturity else ""
        (skill / "SKILL.md").write_text(
            f"""---
name: demo-task
description: Perform the demo workflow. Use when the demo path changes.
metadata:
  openforge-scope: project
  openforge-owner: owner/repo
{maturity_line}  openforge-version: "1"
---
# Demo
""",
            encoding="utf-8",
        )
        return root

    def write_evidence(self, root: Path, **overrides) -> None:
        evidence = {
            "schemaVersion": "openforge-agent-skill-verification/v1",
            "skill": "demo-task",
            "skillVersion": "1",
            "freshSession": True,
            "agentRuntime": "test-runtime",
            "happyPath": {"status": "passed", "scenario": "happy", "evidence": ["artifact:happy"]},
            "edgeCase": {"status": "passed", "scenario": "edge", "evidence": ["artifact:edge"]},
            "deterministicChecks": [{"command": "make verify", "status": "passed", "scope": "baseline"}],
            "runtimeEvidence": [],
            "unverified": [],
            "verifiedAt": date.today().isoformat(),
        }
        evidence.update(overrides)
        path = root / ".agents" / "skill-evals"
        path.mkdir(parents=True, exist_ok=True)
        (path / "demo-task.json").write_text(json.dumps(evidence), encoding="utf-8")

    def findings_by_code(self, root: Path) -> dict[str, list]:
        _, findings = AUDIT.audit(root)
        result: dict[str, list] = {}
        for finding in findings:
            result.setdefault(finding.code, []).append(finding)
        return result


class MalformedSkillGateTest(SkillsGateFixtureMixin, unittest.TestCase):
    def test_bad_name_format_fails_gate_in_both_modes(self):
        root = self.make_repo("draft")
        skill = root / ".agents" / "skills" / "demo-task"
        (skill / "SKILL.md").write_text(
            """---
name: Demo_Task
description: Bad name format.
metadata:
  openforge-scope: project
  openforge-owner: owner/repo
  openforge-maturity: draft
  openforge-version: "1"
---
# Demo
""",
            encoding="utf-8",
        )
        _, findings = AUDIT.audit(root)
        codes = {finding.code for finding in findings}
        self.assertIn("SKILL-NAME-FORMAT", codes)
        self.assertTrue(AUDIT.gate_failed(findings, strict=False))
        self.assertTrue(AUDIT.gate_failed(findings, strict=True))


class MaturityMissingGateTest(SkillsGateFixtureMixin, unittest.TestCase):
    def test_missing_maturity_is_detected_as_warn(self):
        # Assert by membership/severity, not exact count: on a case-insensitive filesystem
        # (macOS default) the pre-existing skill_files() SKILL.md/skill.md glob overlap (fixed
        # in a later commit not present in this worktree - see AGENTS.md note) can surface the
        # same physical skill twice. That is an unrelated, already-known issue; this assertion
        # is written to stay correct regardless of it.
        root = self.make_repo(maturity=None)
        _, findings = AUDIT.audit(root)
        matches = [f for f in findings if f.code == "SKILL-MATURITY-MISSING"]
        self.assertGreaterEqual(len(matches), 1)
        self.assertTrue(all(f.severity == "warn" for f in matches))

    def test_gate_failed_escalates_maturity_missing_only_under_strict(self):
        # Pure unit test of the exit-code contract for SKILL-MATURITY-MISSING, decoupled from
        # filesystem/glob fixture concerns.
        findings = [AUDIT.Finding("warn", "SKILL-MATURITY-MISSING", "demo/SKILL.md", "missing maturity")]
        self.assertFalse(AUDIT.gate_failed(findings, strict=False))
        self.assertTrue(AUDIT.gate_failed(findings, strict=True))

    def test_missing_maturity_not_flagged_for_adapter_root(self):
        root = self.make_repo(maturity="draft")
        adapter = root / ".claude" / "skills" / "adapter-task"
        adapter.mkdir(parents=True)
        (adapter / "SKILL.md").write_text(
            """---
name: adapter-task
description: Adapter skill mirrors canonical, no maturity of its own.
metadata:
  openforge-scope: project
  openforge-owner: owner/repo
  openforge-version: "1"
---
# Adapter
""",
            encoding="utf-8",
        )
        _, findings = AUDIT.audit(root)
        adapter_findings = [f for f in findings if f.path.startswith(".claude/skills/")]
        self.assertNotIn("SKILL-MATURITY-MISSING", {f.code for f in adapter_findings})


class VerifiedWithoutEvidenceGateTest(SkillsGateFixtureMixin, unittest.TestCase):
    def test_verified_without_evidence_fails_in_both_modes(self):
        root = self.make_repo("verified")
        _, findings = AUDIT.audit(root)
        self.assertIn("SKILL-VERIFICATION-EVIDENCE", {f.code for f in findings})
        self.assertTrue(AUDIT.gate_failed(findings, strict=False))
        self.assertTrue(AUDIT.gate_failed(findings, strict=True))


class ClaudeAdapterGateTest(SkillsGateFixtureMixin, unittest.TestCase):
    def test_claude_without_agents_reference_fails_only_under_strict(self):
        root = self.make_repo(
            "draft",
            claude_text="# Claude adapter\nNo canonical reference here.\n",
            include_skill=False,
        )
        _, findings = AUDIT.audit(root)
        self.assertIn("CLAUDE-NO-AGENTS", {f.code for f in findings})
        self.assertFalse(AUDIT.gate_failed(findings, strict=False))
        self.assertTrue(AUDIT.gate_failed(findings, strict=True))


class VerificationCommandOwnerTest(SkillsGateFixtureMixin, unittest.TestCase):
    def test_make_target_missing_is_flagged(self):
        root = self.make_repo("verified")
        self.write_evidence(root, deterministicChecks=[{"command": "make verify", "status": "passed", "scope": "x"}])
        _, findings = AUDIT.audit(root)
        self.assertIn("SKILL-VERIFICATION-COMMAND-OWNER", {f.code for f in findings})

    def test_make_target_present_is_not_flagged(self):
        root = self.make_repo("verified")
        (root / "Makefile").write_text("verify:\n\t@echo ok\n", encoding="utf-8")
        self.write_evidence(root, deterministicChecks=[{"command": "make verify", "status": "passed", "scope": "x"}])
        _, findings = AUDIT.audit(root)
        self.assertNotIn("SKILL-VERIFICATION-COMMAND-OWNER", {f.code for f in findings})

    def test_script_path_present_is_not_flagged(self):
        root = self.make_repo("verified")
        script = root / "scripts" / "custom-thing"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text("#!/bin/sh\n", encoding="utf-8")
        self.write_evidence(
            root,
            deterministicChecks=[
                {"command": "./scripts/custom-thing --weird", "status": "passed", "scope": "x"}
            ],
        )
        _, findings = AUDIT.audit(root)
        self.assertNotIn("SKILL-VERIFICATION-COMMAND-OWNER", {f.code for f in findings})

    def test_script_path_missing_is_flagged(self):
        root = self.make_repo("verified")
        self.write_evidence(
            root,
            deterministicChecks=[
                {"command": "./scripts/custom-thing --weird", "status": "passed", "scope": "x"}
            ],
        )
        _, findings = AUDIT.audit(root)
        self.assertIn("SKILL-VERIFICATION-COMMAND-OWNER", {f.code for f in findings})

    def test_unrecognizable_command_form_is_not_flagged(self):
        root = self.make_repo("verified")
        self.write_evidence(
            root,
            deterministicChecks=[{"command": "gh workflow run verify.yml", "status": "passed", "scope": "x"}],
        )
        _, findings = AUDIT.audit(root)
        self.assertNotIn("SKILL-VERIFICATION-COMMAND-OWNER", {f.code for f in findings})


class VerificationCommandFailQuietTest(unittest.TestCase):
    """Forms the resolver must report as unknown rather than missing.

    A false positive here becomes a wrong red build in every repository that adopts --strict,
    so anything the resolver cannot settle confidently must return None.
    """

    def make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "package.json").write_text(json.dumps({"scripts": {"test": "vitest"}}), encoding="utf-8")
        (root / "Makefile").write_text("include mk/common.mk\n\nbuild:\n\techo hi\n", encoding="utf-8")
        (root / "mk").mkdir()
        (root / "mk" / "common.mk").write_text("verify:\n\techo verify\n", encoding="utf-8")
        return root

    def test_yarn_builtin_is_not_a_missing_script(self):
        root = self.make_repo()
        # `yarn audit` is a real verification command built into yarn, not a package.json script.
        self.assertIsNone(AUDIT.resolve_verification_command(root, "yarn audit"))
        self.assertIsNone(AUDIT.resolve_verification_command(root, "yarn install"))

    def test_yarn_script_still_resolves(self):
        root = self.make_repo()
        self.assertIs(True, AUDIT.resolve_verification_command(root, "yarn test"))

    def test_make_target_behind_an_include_is_unknown(self):
        root = self.make_repo()
        # `verify:` lives in an included fragment; resolving that means implementing make.
        self.assertIsNone(AUDIT.resolve_verification_command(root, "make verify"))
        self.assertIs(True, AUDIT.resolve_verification_command(root, "make build"))

    def test_missing_target_without_include_is_still_reported(self):
        root = Path(tempfile.mkdtemp())
        (root / "Makefile").write_text("build:\n\techo hi\n", encoding="utf-8")
        self.assertIs(False, AUDIT.resolve_verification_command(root, "make missing"))


class CliExitCodeTest(SkillsGateFixtureMixin, unittest.TestCase):
    def run_cli(self, argv: list[str]) -> tuple[int, str]:
        buffer = io.StringIO()
        with patch.object(sys, "argv", ["audit-agent-skills.py", *argv]), contextlib.redirect_stdout(buffer):
            code = AUDIT.main()
        return code, buffer.getvalue()

    def test_claude_no_agents_cli_exit_codes(self):
        # No skill fixture involved, so this end-to-end main() exercise is unaffected by the
        # pre-existing macOS case-insensitive skill_files() duplication issue noted above.
        root = self.make_repo(
            "draft",
            claude_text="# Claude adapter\nNo canonical reference here.\n",
            include_skill=False,
        )
        default_code, _ = self.run_cli([str(root)])
        strict_code, strict_output = self.run_cli([str(root), "--strict"])
        self.assertEqual(0, default_code)
        self.assertNotEqual(0, strict_code)
        self.assertIn("CLAUDE-NO-AGENTS", strict_output)


class DetectLocalAgentGateTest(unittest.TestCase):
    def make_repo(self) -> Path:
        return Path(tempfile.mkdtemp())

    def write_workflow(self, root: Path, name: str, text: str) -> None:
        workflows = root / ".github" / "workflows"
        workflows.mkdir(parents=True, exist_ok=True)
        (workflows / name).write_text(text, encoding="utf-8")

    def test_configured_true_with_reusable_workflow_and_pull_request_trigger(self):
        root = self.make_repo()
        self.write_workflow(
            root,
            "agent-contract-gate.yml",
            "on:\n  pull_request:\njobs:\n  gate:\n"
            "    uses: dasomel/openforge/.github/workflows/agent-contract-gate.yml@main\n",
        )
        result = ENGINEERING.detect_local_agent_gate(root)
        self.assertTrue(result["configured"])
        self.assertEqual(".github/workflows/agent-contract-gate.yml", result["evidence"])

    def test_continue_on_error_neutralizes_the_gate(self):
        root = self.make_repo()
        self.write_workflow(
            root,
            "agent-contract-gate.yml",
            "on:\n  pull_request:\njobs:\n  gate:\n"
            "    uses: dasomel/openforge/.github/workflows/agent-contract-gate.yml@main\n"
            "    continue-on-error: true\n",
        )
        result = ENGINEERING.detect_local_agent_gate(root)
        self.assertFalse(result["configured"])
        self.assertEqual("failure-neutralized", result["reason"])

    def test_push_only_trigger_is_not_configured(self):
        root = self.make_repo()
        self.write_workflow(
            root,
            "agent-contract-gate.yml",
            "on:\n  push:\n    branches: [main]\njobs:\n  gate:\n"
            "    uses: dasomel/openforge/.github/workflows/agent-contract-gate.yml@main\n",
        )
        result = ENGINEERING.detect_local_agent_gate(root)
        self.assertFalse(result["configured"])
        self.assertEqual("missing-pull-request-trigger", result["reason"])

    def test_no_workflows_directory(self):
        root = self.make_repo()
        result = ENGINEERING.detect_local_agent_gate(root)
        self.assertFalse(result["configured"])
        self.assertIsNone(result["evidence"])
        self.assertEqual("no-workflows", result["reason"])

    def test_direct_script_invocation_also_counts_as_a_gate(self):
        root = self.make_repo()
        self.write_workflow(
            root,
            "local-audit.yml",
            "on:\n  pull_request:\njobs:\n  audit:\n    steps:\n"
            "      - run: python3 templates/scripts/audit-agent-skills.py . --strict\n",
        )
        result = ENGINEERING.detect_local_agent_gate(root)
        self.assertTrue(result["configured"])


class EngineeringAuditIntegrationTest(unittest.TestCase):
    def test_local_agent_ci_gate_key_and_false_green_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
            result = ENGINEERING.audit(root, "owner/demo")
            self.assertIn("local_agent_ci_gate", result)
            self.assertFalse(result["local_agent_ci_gate"]["configured"])
            self.assertTrue(
                any(
                    finding.startswith("agent contract changes have no repository-local CI gate")
                    for finding in result["false_green_findings"]
                )
            )

    def test_local_agent_ci_gate_configured_true_removes_false_green_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (workflows / "agent-contract-gate.yml").write_text(
                "on:\n  pull_request:\njobs:\n  gate:\n"
                "    uses: dasomel/openforge/.github/workflows/agent-contract-gate.yml@main\n",
                encoding="utf-8",
            )
            result = ENGINEERING.audit(root, "owner/demo")
            self.assertTrue(result["local_agent_ci_gate"]["configured"])
            self.assertFalse(
                any(
                    finding.startswith("agent contract changes have no repository-local CI gate")
                    for finding in result["false_green_findings"]
                )
            )


if __name__ == "__main__":
    unittest.main()
