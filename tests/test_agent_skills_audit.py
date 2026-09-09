from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "templates" / "scripts" / "audit-agent-skills.py"
SPEC = importlib.util.spec_from_file_location("audit_agent_skills", SCRIPT)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class AgentSkillsAuditTests(unittest.TestCase):
    def make_repo(self, maturity: str = "draft") -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")
        (root / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        skill = root / ".agents" / "skills" / "demo-task"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"""---
name: demo-task
description: Perform the demo workflow. Use when the demo path changes.
metadata:
  openforge-scope: project
  openforge-owner: owner/repo
  openforge-maturity: {maturity}
  openforge-version: "1"
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
            "happyPath": {
                "status": "passed",
                "scenario": "happy",
                "evidence": ["artifact:happy"],
            },
            "edgeCase": {
                "status": "passed",
                "scenario": "edge",
                "evidence": ["artifact:edge"],
            },
            "deterministicChecks": [
                {"command": "make verify", "status": "passed", "scope": "baseline"}
            ],
            "runtimeEvidence": [],
            "unverified": [],
            "verifiedAt": date.today().isoformat(),
        }
        evidence.update(overrides)
        path = root / ".agents" / "skill-evals"
        path.mkdir(parents=True)
        (path / "demo-task.json").write_text(json.dumps(evidence), encoding="utf-8")

    def error_codes(self, root: Path) -> set[str]:
        _, findings = AUDIT.audit(root)
        return {finding.code for finding in findings if finding.severity == "error"}

    def test_draft_does_not_require_evidence(self):
        root = self.make_repo("draft")
        self.assertEqual(set(), self.error_codes(root))

    def test_verified_requires_evidence(self):
        root = self.make_repo("verified")
        self.assertIn("SKILL-VERIFICATION-EVIDENCE", self.error_codes(root))

    def test_verified_accepts_complete_evidence(self):
        root = self.make_repo("verified")
        self.write_evidence(root)
        self.assertEqual(set(), self.error_codes(root))

    def test_verified_rejects_non_fresh_replay(self):
        root = self.make_repo("verified")
        self.write_evidence(root, freshSession=False)
        self.assertIn("SKILL-VERIFICATION-FRESH", self.error_codes(root))

    def test_verified_rejects_version_drift(self):
        root = self.make_repo("verified")
        self.write_evidence(root, skillVersion="2")
        self.assertIn("SKILL-VERIFICATION-VERSION", self.error_codes(root))

    def test_runtime_symlink_alias_is_audited_once(self):
        root = self.make_repo("draft")
        target = root / ".claude" / "skills" / "verification"
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text(
            """---
name: verification
description: Legacy runtime adapter for verification.
metadata:
  openforge-scope: project
  openforge-owner: owner/repo
  openforge-maturity: deprecated
  openforge-version: "2"
---
# Adapter
""",
            encoding="utf-8",
        )
        aliases = root / ".agents" / "skills"
        aliases.mkdir(parents=True, exist_ok=True)
        (aliases / "verification").symlink_to(Path("../../.claude/skills/verification"))

        skills, findings = AUDIT.audit(root)
        verification = [skill for skill in skills if skill.name == "verification"]
        self.assertEqual(1, len(verification))
        self.assertEqual(".claude/skills/verification/SKILL.md", verification[0].path)
        self.assertNotIn("SKILL-DUP-NAME", {finding.code for finding in findings})

    def test_one_physical_skill_file_reached_twice_is_audited_once(self):
        """Discovery globs both `SKILL.md` and `skill.md`.

        A case-insensitive filesystem (macOS, Windows) answers both globs with the same
        physical file under two spellings; a hard link reproduces that on a case-sensitive
        one. Either way the skill must be audited once, not reported as a duplicate name.
        """
        root = self.make_repo("draft")
        canonical = root / ".agents" / "skills" / "demo-task" / "SKILL.md"
        alias = canonical.with_name("skill.md")
        if not alias.exists():
            os.link(canonical, alias)

        skills, findings = AUDIT.audit(root)
        self.assertEqual([("demo-task", ".agents/skills/demo-task/SKILL.md")], [(s.name, s.path) for s in skills])
        self.assertNotIn("SKILL-DUP-NAME", {finding.code for finding in findings})

    def test_lowercase_skill_filename_is_discovered_and_reported(self):
        """A lowercase `skill.md` must be audited under its real name.

        Discovery used to match the glob pattern `*/SKILL.md`, which a case-insensitive
        filesystem answers with this file under the pattern's spelling — silently suppressing
        SKILL-CASE on macOS and Windows while Linux CI still reported it.
        """
        root = self.make_repo("draft")
        canonical = root / ".agents" / "skills" / "demo-task" / "SKILL.md"
        canonical.rename(canonical.with_name("renamed.tmp"))
        canonical.with_name("renamed.tmp").rename(canonical.with_name("skill.md"))

        skills, findings = AUDIT.audit(root)
        self.assertEqual([".agents/skills/demo-task/skill.md"], [skill.path for skill in skills])
        self.assertIn("SKILL-CASE", {finding.code for finding in findings})


if __name__ == "__main__":
    unittest.main()
