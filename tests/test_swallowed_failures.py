"""Regression tests for swallowed-validator detection (issue #71).

The detector's value is its precision: it must find `markdownlint ... || true` and must not
find `grep ... || true`. Every legitimate case below was taken from a real repository in the
portfolio, so a change that starts flagging one of them is a regression against evidence, not
against a hypothetical.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "templates" / "scripts" / "swallowed_failure_detector.py"
SPEC = importlib.util.spec_from_file_location("swallowed_failure_detector", SCRIPT)
assert SPEC and SPEC.loader
DETECTOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DETECTOR
SPEC.loader.exec_module(DETECTOR)


class DetectorTestCase(unittest.TestCase):
    def repo(self) -> Path:
        return Path(tempfile.mkdtemp())

    def write(self, root: Path, relative: str, content: str) -> Path:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def scan(self, root: Path) -> list:
        return DETECTOR.scan_repository(root)

    def assertNoFindings(self, root: Path) -> None:
        findings = self.scan(root)
        self.assertEqual([], findings, f"unexpected findings: {[f.command for f in findings]}")


class WorkflowDetectionTests(DetectorTestCase):
    def test_markdownlint_or_true_is_detected(self):
        """The shape issue #71 was opened for, as it appears in narwhal's lint.yml."""
        root = self.repo()
        self.write(
            root,
            ".github/workflows/lint.yml",
            "name: Lint\n"
            "jobs:\n"
            "  markdown:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - name: Lint Markdown files\n"
            "        run: |\n"
            "          markdownlint '**/*.md' --config .markdownlint.json || true\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual(".github/workflows/lint.yml", findings[0].path)
        self.assertEqual(8, findings[0].line)
        self.assertEqual("or-true", findings[0].pattern)
        self.assertIn("markdownlint", findings[0].command)

    def test_neutralizer_on_a_continuation_line_is_detected_at_the_validator(self):
        """narwhal's real shape: the `|| true` sits four lines below the command it kills."""
        root = self.repo()
        self.write(
            root,
            ".github/workflows/lint.yml",
            "name: Lint\n"
            "jobs:\n"
            "  markdown:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - name: Lint Markdown files\n"
            "        run: |\n"
            "          markdownlint \\\n"
            "            --config .markdownlint.json \\\n"
            "            'docs/**/*.md' \\\n"
            "            || true\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual(8, findings[0].line, "should point at the validator, not the neutralizer")

    def test_pipeline_ending_in_or_true_is_detected(self):
        """A pipeline's status is its last element, so `| tee` does not save the verdict."""
        root = self.repo()
        self.write(
            root,
            ".github/workflows/ci.yml",
            "jobs:\n  a:\n    steps:\n      - run: |\n"
            "          markdownlint docs | tee lint.log || true\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertIn("markdownlint", findings[0].command)

    def test_step_continue_on_error_is_detected(self):
        root = self.repo()
        self.write(
            root,
            ".github/workflows/ci.yml",
            "jobs:\n  a:\n    steps:\n"
            "      - name: Tests\n"
            "        continue-on-error: true\n"
            "        run: |\n"
            "          pytest -q\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual("continue-on-error", findings[0].pattern)

    def test_job_level_continue_on_error_covers_every_step(self):
        """ldapium marks a whole advisory job non-blocking, not an individual step."""
        root = self.repo()
        self.write(
            root,
            ".github/workflows/ci.yml",
            "jobs:\n"
            "  advisory:\n"
            "    continue-on-error: true\n"
            "    steps:\n"
            "      - name: Lint\n"
            "        run: |\n"
            "          yamllint .\n"
            "  blocking:\n"
            "    steps:\n"
            "      - name: Test\n"
            "        run: |\n"
            "          pytest -q\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings), [f.command for f in findings])
        self.assertIn("yamllint", findings[0].command)

    def test_continue_on_error_does_not_leak_to_neighbouring_steps(self):
        """kube-ready-box's informational benchmark step sits beside two blocking ones.

        An earlier implementation probed a fixed window of lines around each `run:` and
        attributed this step's `continue-on-error` to its neighbours.
        """
        root = self.repo()
        self.write(
            root,
            ".github/workflows/validate.yml",
            "jobs:\n  contract:\n    steps:\n"
            "      - name: Syntax\n"
            "        run: |\n"
            "          bash -n tools/*.sh\n"
            "      - name: Build\n"
            "        run: |\n"
            "          cargo build --release\n"
            "      - name: Benchmark (informational, non-blocking)\n"
            "        continue-on-error: true\n"
            "        run: |\n"
            "          bash tools/bench-verifier.sh\n",
        )
        self.assertNoFindings(root)

    def test_if_failure_step_is_diagnostics(self):
        root = self.repo()
        self.write(
            root,
            ".github/workflows/ci.yml",
            "jobs:\n  a:\n    steps:\n"
            "      - name: Diagnostics\n"
            "        if: failure()\n"
            "        run: |\n"
            "          kubectl get pods || true\n"
            "          pytest --collect-only || true\n",
        )
        self.assertNoFindings(root)


class LegitimateNeutralizationTests(DetectorTestCase):
    def test_grep_finding_nothing_is_data(self):
        root = self.repo()
        self.write(root, "scripts/check.sh", "#!/usr/bin/env bash\ngrep -r \"TODO\" . || true\n")
        self.assertNoFindings(root)

    def test_grep_inside_command_substitution_is_data(self):
        """Verbatim from narwhal lint.yml:35, the counterpart to the true positive above."""
        root = self.repo()
        self.write(
            root,
            ".github/workflows/lint.yml",
            "jobs:\n  a:\n    steps:\n      - run: |\n"
            "          width=$(grep -o '^ \\+' \"$f\" 2>/dev/null | awk '{print length}' | sort -n | head -1 || true)\n",
        )
        self.assertNoFindings(root)

    def test_cleanup_and_probe_commands_are_not_validators(self):
        root = self.repo()
        self.write(
            root,
            "scripts/teardown.sh",
            "#!/usr/bin/env bash\n"
            "rm -f /tmp/state.json || true\n"
            "docker rm -f runner || true\n"
            "kubectl delete ns demo || true\n"
            "curl -fsS http://localhost:8080/healthz || true\n"
            "find . -name '*.tmp' -delete || true\n",
        )
        self.assertNoFindings(root)

    def test_unknown_program_is_never_flagged(self):
        """kubemetal neutralizes a bespoke `codegraph` report; the detector must not guess."""
        root = self.repo()
        self.write(root, "Makefile", "analyze-code:\n\tcodegraph impact get_cluster_status || true\n")
        self.assertNoFindings(root)

    def test_diagnostics_after_a_detected_failure_are_not_flagged(self):
        root = self.repo()
        self.write(
            root,
            "scripts/run.sh",
            "#!/usr/bin/env bash\n"
            "pytest -q\n"
            "if [ $? -ne 0 ]; then\n"
            "  kubectl get pods || true\n"
            "  pytest --last-failed --collect-only || true\n"
            "fi\n",
        )
        self.assertNoFindings(root)


class SetPlusETests(DetectorTestCase):
    def test_unchecked_set_plus_e_is_detected(self):
        root = self.repo()
        self.write(
            root,
            "scripts/check.sh",
            "#!/usr/bin/env bash\nset +e\npytest -q\necho done\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual("unchecked-set-plus-e", findings[0].pattern)

    def test_checked_status_is_not_flagged(self):
        """nfs-quota-agent's licence check: `set +e`, capture `rc`, then act on it."""
        root = self.repo()
        self.write(
            root,
            "scripts/check.sh",
            "#!/usr/bin/env bash\n"
            "set +e\n"
            "pytest -q\n"
            "rc=$?\n"
            "set -e\n"
            "if [ \"$rc\" -ne 0 ]; then exit \"$rc\"; fi\n",
        )
        self.assertNoFindings(root)


class MakefileTests(DetectorTestCase):
    def test_dash_prefixed_validator_recipe_is_detected(self):
        root = self.repo()
        self.write(root, "Makefile", "lint:\n\t-markdownlint .\n")
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual("or-true", findings[0].pattern)
        self.assertIn("make", findings[0].reason)

    def test_dash_prefixed_cleanup_recipe_is_not_detected(self):
        root = self.repo()
        self.write(root, "Makefile", "clean:\n\t-rm -f tmp\n")
        self.assertNoFindings(root)


class MarkdownTests(DetectorTestCase):
    def test_validator_in_a_fenced_block_is_detected(self):
        root = self.repo()
        self.write(
            root,
            "AGENTS.md",
            "# Agents\n\nVerify with:\n\n```bash\nshellcheck scripts/*.sh || true\n```\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual("AGENTS.md", findings[0].path)
        self.assertEqual(6, findings[0].line)

    def test_the_same_text_in_prose_is_not_detected(self):
        """A standard that describes the anti-pattern must not report itself."""
        root = self.repo()
        self.write(
            root,
            "AGENTS.md",
            "# Agents\n\nNever write `shellcheck scripts/*.sh || true`; it hides real findings.\n",
        )
        self.assertNoFindings(root)

    def test_skill_files_are_scanned(self):
        root = self.repo()
        self.write(
            root,
            ".agents/skills/demo/SKILL.md",
            "---\nname: demo\n---\n\n```bash\npytest -q || true\n```\n",
        )
        self.assertEqual(1, len(self.scan(root)))

    def test_claude_command_recipes_are_scanned(self):
        """#71's acceptance criteria: a verification recipe under .claude/commands/ counts."""
        root = self.repo()
        self.write(
            root,
            ".claude/commands/verify.md",
            "# Verify\n\n```bash\nshellcheck scripts/*.sh || true\n```\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual(".claude/commands/verify.md", findings[0].path)

    def test_agents_command_recipes_are_scanned(self):
        """.agents/commands/ is the canonical form the .claude/ adapter mirrors."""
        root = self.repo()
        self.write(
            root,
            ".agents/commands/verify.md",
            "# Verify\n\n```bash\nshellcheck scripts/*.sh || true\n```\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual(".agents/commands/verify.md", findings[0].path)

    def test_command_recipe_data_grep_is_not_flagged(self):
        """The classify-the-program guarantee must survive the new command-recipe path."""
        root = self.repo()
        self.write(
            root,
            ".claude/commands/verify.md",
            "# Verify\n\n```bash\ngrep -q foo file || true\n```\n",
        )
        self.assertNoFindings(root)

    def test_non_command_markdown_elsewhere_is_not_scanned(self):
        """The widening is bounded: an arbitrary doc outside the command directories is untouched."""
        root = self.repo()
        self.write(
            root,
            "docs/whatever.md",
            "# Whatever\n\n```bash\nshellcheck scripts/*.sh || true\n```\n",
        )
        self.assertNoFindings(root)


class NamespacedCommandTests(DetectorTestCase):
    def test_nested_command_namespace_is_scanned(self):
        """Claude Code namespaces slash commands with subdirectories, so a recipe at
        `.claude/commands/db/migrate.md` is a verification recipe like any other."""
        root = self.repo()
        self.write(
            root,
            ".claude/commands/db/migrate.md",
            "# migrate\n\n```bash\nshellcheck scripts/*.sh || true\n```\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual(".claude/commands/db/migrate.md", findings[0].path)
        self.assertEqual("shellcheck scripts/*.sh", findings[0].command)

    def test_sibling_directory_is_not_mistaken_for_commands(self):
        """The prefix carries a trailing slash, so `.claude/commandsfoo/` stays out."""
        root = self.repo()
        self.write(
            root,
            ".claude/commandsfoo/verify.md",
            "# verify\n\n```bash\nshellcheck scripts/*.sh || true\n```\n",
        )
        self.assertNoFindings(root)


class PackageJsonTests(DetectorTestCase):
    def test_swallowed_npm_script_is_detected_grep_and_plain_scripts_are_not(self):
        """`grep ... || true` is data, and `eslint .` alone doesn't swallow anything -- only
        the unconditionally-neutralized `vitest` script should be reported."""
        root = self.repo()
        self.write(
            root,
            "package.json",
            json.dumps({"scripts": {
                "test": "vitest || true",
                "find": "grep -r TODO . || true",
                "lint": "eslint .",
            }}),
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual("package.json", findings[0].path)
        self.assertEqual("vitest", findings[0].command)

    def test_non_object_manifest_does_not_raise(self):
        """A bare array/null/number decodes fine but has no `.get`. The audit runs over
        third-party repositories, so one odd manifest must not take the whole scan down."""
        for body in ("[]", "null", "42", '"a string"'):
            with self.subTest(body=body):
                root = self.repo()
                self.write(root, "package.json", body)
                self.assertEqual([], self.scan(root))

    def test_line_number_ignores_a_dependency_of_the_same_name(self):
        """`"test"` appears in devDependencies above `scripts`; the finding must point at
        the script, not at the dependency that happens to share its name."""
        root = self.repo()
        body = (
            '{\n'
            '  "devDependencies": {\n'
            '    "test": "^1.0.0"\n'
            '  },\n'
            '  "scripts": {\n'
            '    "test": "vitest || true"\n'
            '  }\n'
            '}\n'
        )
        self.write(root, "package.json", body)
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual(6, findings[0].line)


class EscapeHatchTests(DetectorTestCase):
    def test_marker_on_the_same_line_suppresses(self):
        root = self.repo()
        self.write(
            root,
            "scripts/check.sh",
            "#!/usr/bin/env bash\nmarkdownlint . || true  # openforge: allow-swallow -- tracked in #187\n",
        )
        self.assertNoFindings(root)

    def test_marker_on_the_previous_line_suppresses(self):
        root = self.repo()
        self.write(
            root,
            "scripts/check.sh",
            "#!/usr/bin/env bash\n# openforge: allow-swallow -- migration in progress\nmarkdownlint . || true\n",
        )
        self.assertNoFindings(root)


class EchoBranchFalseGreenTests(DetectorTestCase):
    """Issue #91: both branches of a conditional report a validator's result but exit 0."""

    def test_narwhal_pre_fix_validate_target_is_detected(self):
        """narwhal's original `validate:` (PR #197's diff) -- `make validate` always exits 0."""
        root = self.repo()
        self.write(
            root,
            "Makefile",
            "validate:\n"
            "\t@for f in gitops/apps/*.yaml gitops/resources/*.yaml; do \\\n"
            '\t\tyq eval \'.\' "$$f" > /dev/null && echo "OK: $$f" || echo "FAIL: $$f"; \\\n'
            "\tdone\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual("echo-branch", findings[0].pattern)
        self.assertIn("yq eval", findings[0].command)

    def test_exit_fail_propagation_after_the_loop_is_not_flagged(self):
        """narwhal's fix: `fail=1` inside the `else` branch, `exit $fail` after the loop."""
        root = self.repo()
        self.write(
            root,
            "Makefile",
            "validate:\n"
            "\t@fail=0; \\\n"
            "\tfor f in gitops/apps/*.yaml gitops/resources/*.yaml; do \\\n"
            "\t\tif yq eval '.' \"$$f\" > /dev/null; then echo \"OK: $$f\"; "
            'else echo "FAIL: $$f"; fail=1; fi; \\\n'
            "\tdone; \\\n"
            "\texit $$fail\n",
        )
        self.assertNoFindings(root)

    def test_plain_shell_script_and_or_echo_form_is_detected(self):
        """Same idiom, no Makefile involved -- a standalone `validate.sh`."""
        root = self.repo()
        self.write(
            root,
            "validate.sh",
            "#!/bin/bash\n"
            "for f in *.yaml; do\n"
            "  yq eval '.' \"$f\" > /dev/null && echo \"OK: $f\" || echo \"FAIL: $f\"\n"
            "done\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual("echo-branch", findings[0].pattern)

    def test_plain_shell_script_exit_var_propagation_is_not_flagged(self):
        root = self.repo()
        self.write(
            root,
            "validate.sh",
            "#!/bin/bash\n"
            "fail=0\n"
            "for f in *.yaml; do\n"
            "  if yq eval '.' \"$f\" > /dev/null; then echo \"OK: $f\"; "
            'else echo "FAIL: $f"; fail=1; fi\n'
            "done\n"
            "exit $fail\n",
        )
        self.assertNoFindings(root)

    def test_unrelated_later_target_exit_var_does_not_suppress_finding(self):
        """Bug report: an unrelated later target's `exit $$rc` must not suppress an earlier
        target's echo-branch false-green -- the forward search for propagation has to stay
        bounded to the enclosing recipe block, not run to the end of the file."""
        root = self.repo()
        self.write(
            root,
            "Makefile",
            "validate:\n"
            "\t@for f in gitops/apps/*.yaml gitops/resources/*.yaml; do \\\n"
            '\t\tyq eval \'.\' "$$f" > /dev/null && echo "OK: $$f" || echo "FAIL: $$f"; \\\n'
            "\tdone\n"
            "\n"
            "deploy:\n"
            "\t@rc=0; \\\n"
            "\techo deploying; \\\n"
            "\texit $$rc\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual("echo-branch", findings[0].pattern)
        self.assertIn("yq eval", findings[0].command)

    def test_unrelated_later_shell_function_exit_var_does_not_suppress_finding(self):
        """Same bug, shell-function flavor: an unrelated function's `exit $rc` must not reach
        back into an earlier, unrelated function's echo-branch finding."""
        root = self.repo()
        self.write(
            root,
            "validate.sh",
            "#!/bin/bash\n"
            "check() {\n"
            "  for f in *.yaml; do\n"
            "    yq eval '.' \"$f\" > /dev/null && echo \"OK: $f\" || echo \"FAIL: $f\"\n"
            "  done\n"
            "}\n"
            "\n"
            "deploy() {\n"
            "  rc=0\n"
            "  echo deploying\n"
            "  exit $rc\n"
            "}\n",
        )
        findings = self.scan(root)
        self.assertEqual(1, len(findings))
        self.assertEqual("echo-branch", findings[0].pattern)

    def test_unknown_program_in_echo_branches_is_not_flagged(self):
        """Same discipline as `|| true`: an unrecognized program is never reported."""
        root = self.repo()
        self.write(
            root,
            "check.sh",
            "#!/bin/sh\n"
            'codegraph impact get_cluster_status && echo "OK" || echo "FAIL"\n',
        )
        self.assertNoFindings(root)


class ContractTests(DetectorTestCase):
    def test_or_noop_forms_are_detected(self):
        root = self.repo()
        self.write(root, "a.sh", "#!/bin/sh\nshellcheck a.sh || :\n")
        self.write(root, "b.sh", "#!/bin/sh\nyamllint . || exit 0\n")
        patterns = {finding.pattern for finding in self.scan(root)}
        self.assertEqual({"or-noop"}, patterns)

    def test_results_are_deterministic_and_sorted(self):
        root = self.repo()
        self.write(root, "b.sh", "#!/bin/sh\npytest || true\n")
        self.write(root, "a.sh", "#!/bin/sh\nmypy . || true\n")
        first = self.scan(root)
        second = self.scan(root)
        self.assertEqual(first, second)
        self.assertEqual(["a.sh", "b.sh"], [finding.path for finding in first])

    def test_unreadable_and_binary_files_do_not_raise(self):
        root = self.repo()
        (root / "blob.sh").write_bytes(b"\xff\xfe\x00\x00binary")
        self.write(root, "ok.sh", "#!/bin/sh\necho fine\n")
        self.assertNoFindings(root)


if __name__ == "__main__":
    unittest.main()
