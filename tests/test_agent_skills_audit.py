from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "templates" / "scripts" / "audit-agent-skills.py"
SPEC = importlib.util.spec_from_file_location("audit_agent_skills", SCRIPT)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
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


if __name__ == "__main__":
    unittest.main()
