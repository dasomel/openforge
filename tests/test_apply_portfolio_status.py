#!/usr/bin/env python3
"""
Unit tests for templates/scripts/apply-portfolio-status.py.

Covers the revision-bound evidence/capability handling from issue #110:
- D1: evidence dimensions (security/runtime) present at an old revision but omitted from a
  payload at a new revision are downgraded to "not-run", never silently dropped (#106/#108)
  and never left showing the old revision's value as if it still applied (#107).
- D2: capabilities omitted from the payload at a new revision are retained with every
  verification field downgraded to "not-run" -- but only counted as a downgrade when there
  was a non-empty verification claim to actually escalate.
- D3: the --report change report flags downgrades and claims repeated verbatim at a new
  revision (the #107 carry-forward signal) for reviewer re-verification.
- Same-revision re-publish applies payload values with no downgrade logic.
- Tampered/invalid/missing evidence values are rejected.

All fixture data below is synthetic. Earlier revisions of this suite loaded the live
`portfolio/projects.json` beluga entry, which coupled tests to real registry data (the exact
pattern PR #112 removed elsewhere): the first real beluga re-publish after this fix lands
would set security/runtime to not-run and break this suite. Nothing here reads or writes
`portfolio/*.json`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates" / "scripts" / "apply-portfolio-status.py"
SPEC = importlib.util.spec_from_file_location("openforge_apply_portfolio_status", SCRIPT)
assert SPEC and SPEC.loader
apply_status = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(apply_status)

SYNTHETIC_ALLOWED_STATUSES = [
    "planned",
    "designing",
    "implementing",
    "verifying",
    "implemented",
    "adopted",
    "active",
    "maintenance",
    "blocked",
    "deprecated",
]


def make_milestones_doc() -> dict[str, Any]:
    return {"allowed_statuses": list(SYNTHETIC_ALLOWED_STATUSES)}


def make_old_status() -> dict[str, Any]:
    """A synthetic prior status shaped like #108's beluga scenario: security/runtime evidence
    plus two capabilities with verification claims, at revision 'oldrev01'."""
    return {
        "revision": "oldrev01",
        "updated_at": "2026-09-01",
        "milestone": "example-milestone",
        "progress_percent": 85,
        "capabilities": {
            "compliance-baseline": {
                "status": "implemented",
                "standard": "openforge/compliance-baseline",
                "verification": {"unit": "pass", "integration": "pass", "runtime": "not-applicable", "security": "pass"},
            },
            "stream-iceberg": {
                "status": "implemented",
                "standard": "openforge/data-platform",
                "verification": {"unit": "pass", "integration": "pass", "runtime": "partial", "security": "pass"},
            },
        },
        "evidence": {
            "issue": 1,
            "pull_request": None,
            "commit": "oldrev01oldrev01oldrev01oldrev01oldrev01",
            "ci": "pass",
            "security": "pass",
            "runtime": "partial",
        },
    }


def make_projects_doc() -> dict[str, Any]:
    return {
        "version": "openforge-portfolio-test/v1",
        "updated_at": "2026-09-01",
        "portfolio": {},
        "projects": [
            {
                "id": "widget",
                "repository": "dasomel/widget",
                "name": "Widget",
                "development_status": "active",
                "status": make_old_status(),
            },
            {
                "id": "gadget",
                "repository": "dasomel/gadget",
                "name": "Gadget",
                "development_status": "active",
            },
        ],
    }


def make_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "version": "openforge-project-status/v1",
        "project": "widget",
        "repository": "dasomel/widget",
        "revision": "deadbee",
        "updated_at": "2026-09-20",
        "development": {"status": "active", "milestone": "next-milestone", "progress_percent": 90},
        "capabilities": {},
        "evidence": {"commit": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef", "ci": "pass"},
    }
    payload.update(overrides)
    return payload


class ApplyStatusUpdateTests(unittest.TestCase):
    """Pure-function tests against apply_status_update() using only synthetic fixture data."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.old_status = make_old_status()

    def test_same_revision_republish_uses_payload_values_with_no_downgrade(self):
        payload = make_payload(
            revision=self.old_status["revision"],
            evidence={
                "commit": self.old_status["evidence"]["commit"],
                "ci": "pass",
                "security": "fail",
            },
        )
        status_update, report = apply_status.apply_status_update(self.old_status, payload)

        self.assertEqual(status_update["evidence"]["security"], "fail")
        self.assertNotIn("runtime", status_update["evidence"])
        self.assertFalse(report["revision_changed"])
        self.assertEqual(report["downgraded_evidence"], [])
        self.assertEqual(report["downgraded_capabilities"], [])
        self.assertEqual(report["unchanged_claims"], [])

    def test_revision_change_reproduces_issue_108_evidence_and_capability_downgrade(self):
        """Payload with only ci evidence at a new revision: security/runtime must become
        not-run, and both existing capabilities must be retained with not-run."""
        payload = make_payload(
            revision="newrev123",
            evidence={"commit": "newrev123newrev123newrev123newrev123newr", "ci": "pass"},
        )
        status_update, report = apply_status.apply_status_update(self.old_status, payload)

        self.assertEqual(status_update["evidence"]["security"], "not-run")
        self.assertEqual(status_update["evidence"]["runtime"], "not-run")
        self.assertTrue(report["revision_changed"])
        self.assertEqual(sorted(report["downgraded_evidence"]), ["runtime", "security"])

        for capability_id in ("compliance-baseline", "stream-iceberg"):
            self.assertIn(capability_id, status_update["capabilities"])
            verification = status_update["capabilities"][capability_id]["verification"]
            self.assertTrue(verification, f"{capability_id} verification should not be empty")
            self.assertTrue(all(value == "not-run" for value in verification.values()))
        self.assertEqual(
            sorted(report["downgraded_capabilities"]), ["compliance-baseline", "stream-iceberg"]
        )

    def test_capability_with_no_verification_is_retained_but_not_flagged_as_downgraded(self):
        """D2 fix: a capability with an empty/absent verification dict has nothing to escalate
        to not-run, so it must be retained as-is without appearing in downgraded_capabilities."""
        old_status = make_old_status()
        old_status["capabilities"]["undated-capability"] = {
            "status": "planned",
            "standard": "openforge/example-standard",
        }
        payload = make_payload(
            revision="newrev123",
            evidence={"commit": "newrev123newrev123newrev123newrev123newr", "ci": "pass"},
        )
        status_update, report = apply_status.apply_status_update(old_status, payload)

        self.assertIn("undated-capability", status_update["capabilities"])
        self.assertNotIn("verification", status_update["capabilities"]["undated-capability"])
        self.assertNotIn("undated-capability", report["downgraded_capabilities"])
        # The two capabilities that did have verification claims are still flagged.
        self.assertEqual(
            sorted(report["downgraded_capabilities"]), ["compliance-baseline", "stream-iceberg"]
        )

    def test_unchanged_claims_flagged_for_reviewer(self):
        """The #107 signal: security/runtime and a capability's verification repeated verbatim
        at a new revision must be flagged, not treated as fresh evidence."""
        payload = make_payload(
            revision="newrev123",
            evidence={
                "commit": "newrev123newrev123newrev123newrev123newr",
                "ci": "pass",
                "security": self.old_status["evidence"]["security"],
                "runtime": self.old_status["evidence"]["runtime"],
            },
            capabilities={"compliance-baseline": self.old_status["capabilities"]["compliance-baseline"]},
        )
        status_update, report = apply_status.apply_status_update(self.old_status, payload)

        self.assertIn("evidence.security", report["unchanged_claims"])
        self.assertIn("evidence.runtime", report["unchanged_claims"])
        self.assertIn("capabilities.compliance-baseline.verification", report["unchanged_claims"])
        # stream-iceberg was omitted from the payload entirely -> it's a downgrade, not a
        # repeated claim.
        self.assertNotIn("capabilities.stream-iceberg.verification", report["unchanged_claims"])
        self.assertIn("stream-iceberg", report["downgraded_capabilities"])
        # compliance-baseline was re-affirmed, not omitted, so it must not also show as dropped.
        self.assertNotIn("compliance-baseline", report["downgraded_capabilities"])

    def test_render_change_report_surfaces_downgrades_and_unchanged_claims(self):
        payload = make_payload(
            revision="newrev123",
            evidence={
                "commit": "newrev123newrev123newrev123newrev123newr",
                "ci": "pass",
                "security": self.old_status["evidence"]["security"],
            },
        )
        _, report = apply_status.apply_status_update(self.old_status, payload)
        markdown = apply_status.render_change_report(report)

        self.assertIn("Portfolio status change report: widget", markdown)
        self.assertIn("`oldrev01` -> `newrev123`", markdown)
        self.assertIn("evidence.runtime", markdown)
        self.assertIn("not carried forward", markdown)
        self.assertIn("evidence.security", markdown)

    def test_first_published_status_has_no_downgrades(self):
        payload = make_payload(project="gadget", repository="dasomel/gadget")
        status_update, report = apply_status.apply_status_update(None, payload)

        self.assertFalse(report["revision_changed"])
        self.assertEqual(report["downgraded_evidence"], [])
        self.assertEqual(report["downgraded_capabilities"], [])
        self.assertEqual(status_update["capabilities"], {})


class ApplyPortfolioStatusCliTests(unittest.TestCase):
    """Exercises main()/write() against temp copies of a synthetic registry (module globals
    are monkeypatched for the duration of each test) so nothing under portfolio/*.json is ever
    touched by the automated suite, and no test depends on live registry contents."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        tmp_root = Path(self.tmpdir.name)

        self.projects_path = tmp_root / "projects.json"
        self.milestones_path = tmp_root / "milestones.json"
        self.projects_path.write_text(json.dumps(make_projects_doc()), encoding="utf-8")
        self.milestones_path.write_text(json.dumps(make_milestones_doc()), encoding="utf-8")

        original_projects_path = apply_status.PROJECTS_PATH
        original_milestones_path = apply_status.MILESTONES_PATH
        apply_status.PROJECTS_PATH = self.projects_path
        apply_status.MILESTONES_PATH = self.milestones_path

        def restore() -> None:
            apply_status.PROJECTS_PATH = original_projects_path
            apply_status.MILESTONES_PATH = original_milestones_path

        self.addCleanup(restore)

    def _run_main(self, argv: list[str]) -> int:
        argv_backup = sys.argv
        sys.argv = ["apply-portfolio-status.py", *argv]
        try:
            return apply_status.main()
        finally:
            sys.argv = argv_backup

    def _write_payload(self, payload: dict[str, Any]) -> Path:
        payload_path = Path(self.tmpdir.name) / "payload.json"
        payload_path.write_text(json.dumps(payload), encoding="utf-8")
        return payload_path

    def test_report_written_on_successful_revision_change(self):
        payload_path = self._write_payload(
            make_payload(
                revision="newrev123",
                evidence={"commit": "newrev123newrev123newrev123newrev123newr", "ci": "pass"},
            )
        )
        report_path = Path(self.tmpdir.name) / "report.md"

        exit_code = self._run_main([str(payload_path), "--report", str(report_path)])

        self.assertEqual(exit_code, 0)
        self.assertTrue(report_path.exists())
        content = report_path.read_text(encoding="utf-8")
        self.assertIn("Portfolio status change report: widget", content)
        self.assertIn("Downgraded to not-run", content)
        self.assertIn("evidence.security", content)
        self.assertIn("evidence.runtime", content)

        updated_projects = json.loads(self.projects_path.read_text(encoding="utf-8"))
        widget = next(p for p in updated_projects["projects"] if p["id"] == "widget")
        self.assertEqual(widget["status"]["evidence"]["security"], "not-run")
        self.assertEqual(widget["status"]["evidence"]["runtime"], "not-run")

    def test_tampered_evidence_value_rejected(self):
        payload_path = self._write_payload(
            make_payload(
                revision="newrev123",
                evidence={
                    "commit": "newrev123newrev123newrev123newrev123newr",
                    "ci": "pass",
                    "security": "definitely-pass",
                },
            )
        )

        with self.assertRaises(SystemExit):
            self._run_main([str(payload_path)])

        # Rejection must happen before any registry write.
        untouched = json.loads(self.projects_path.read_text(encoding="utf-8"))
        widget = next(p for p in untouched["projects"] if p["id"] == "widget")
        self.assertEqual(widget["status"]["evidence"]["security"], "pass")

    def test_tampered_capability_verification_value_rejected(self):
        payload_path = self._write_payload(
            make_payload(
                revision="newrev123",
                evidence={"commit": "newrev123newrev123newrev123newrev123newr", "ci": "pass"},
                capabilities={
                    "compliance-baseline": {
                        "status": "implemented",
                        "standard": "openforge/compliance-baseline",
                        "verification": {"unit": "definitely-pass"},
                    }
                },
            )
        )

        with self.assertRaises(SystemExit):
            self._run_main([str(payload_path)])

    def test_missing_revision_rejected(self):
        payload = make_payload(
            evidence={"commit": "newrev123newrev123newrev123newrev123newr", "ci": "pass"},
        )
        del payload["revision"]
        payload_path = self._write_payload(payload)

        with self.assertRaises(SystemExit):
            self._run_main([str(payload_path)])

        untouched = json.loads(self.projects_path.read_text(encoding="utf-8"))
        widget = next(p for p in untouched["projects"] if p["id"] == "widget")
        self.assertEqual(widget["status"]["revision"], "oldrev01")

    def test_empty_revision_rejected(self):
        payload_path = self._write_payload(
            make_payload(
                revision="",
                evidence={"commit": "newrev123newrev123newrev123newrev123newr", "ci": "pass"},
            )
        )

        with self.assertRaises(SystemExit):
            self._run_main([str(payload_path)])


if __name__ == "__main__":
    unittest.main()
