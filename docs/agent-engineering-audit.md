# Agent Engineering Audit

OpenForge separates repository agent guidance into two classes:

1. **machine-observable engineering controls** that should be owned by formatter, linter, tests, policy, build, or generated-file validation; and
2. **human-judgment guidance** such as architecture boundaries, high-risk paths, evidence sufficiency, and escalation conditions.

The audit must not pretend that a keyword scan can prove architecture quality or risk ownership.

## Executable audit

Run against a local repository:

```bash
python3 templates/scripts/audit-agent-engineering.py --repo /path/to/repository --repository owner/name
```

The output uses `openforge-agent-audit/v1` and records:

- root instruction files
- known source-of-truth documentation
- discoverable build/test/lint/verify entrypoints
- deterministic control owners visible in repository tooling
- prompt text that may duplicate deterministic rules
- false-green findings
- judgment fields that still require explicit maintainer review

## Rule ownership

| Rule class | Preferred owner | Prompt role |
|---|---|---|
| formatting / braces | formatter | explain only non-obvious invariant |
| import order / naming supported by tooling | linter / compiler | avoid duplication |
| static analysis | linter / SAST | state expected evidence only |
| tests | test runner / CI | identify the relevant evidence class |
| dependency / security policy | policy / scanner | describe risk and exception boundary |
| generated-file freshness | generator `--check` / CI | identify source-of-truth |
| architecture boundary | human review + targeted tests where possible | keep concise and explicit |
| high-risk path / destructive scope | repository policy + human review | keep explicit |
| evidence sufficiency | CI plus human judgment | distinguish unit vs real runtime evidence |

## False-green rule

An instruction such as “always run lint/tests” is not an executable control by itself. If repository instructions claim deterministic verification but the audit cannot find a corresponding tooling owner, the audit reports a false-green finding.

This check is deliberately conservative. It does not claim that a detected keyword proves the control is complete; it only establishes that an executable owner is present. Repository-specific CI still owns behavioral correctness.

### Two false-green classes

An owner can be missing, and an owner can be present and ignored. The second is the one a green
build hides best: `markdownlint ... || true` runs the validator, prints its errors, and reports
success anyway. Narwhal's Markdown job did exactly that while this matrix recorded zero
false-green findings for the repository, which is what motivated the second detector.

The audit therefore reports both, and records the neutralized commands under
`swallowed_failures` with an exact `swallowed_failure_count`. The `Swallowed` column in the
portfolio matrix shows the count; `—` there means the revision predates the detector and was not
measured, which is not the same as zero.

Detected neutralizations: `|| true`, `|| :`, `|| exit 0`, a make recipe prefixed with `-`, a step
or job carrying `continue-on-error: true`, and `set +e` in effect over a validator whose exit
status is never read.

### Why `|| true` is not banned

`grep ... || true` is correct: grep's non-zero exit means "no match", which is data, not a
verdict. So the detector classifies the *program*, not the idiom, against a table whose inclusion
rule is that a non-zero exit is a judgement about the code. Cleanup and probe commands (`rm`,
`docker rm`, `kubectl delete`, `curl`, `find`) are never reported, and neither is a command whose
program the table does not recognize.

That asymmetry is deliberate. A missed finding costs one unreported false-green; a false positive
teaches a downstream repository that the matrix is noise, which costs every finding after it. The
validator table is the part that grows.

Two more suppressions: a command inside a block guarded by a prior failure (`if [ $? -ne 0 ]`, a
`trap` handler, a step with `if: failure()`) is diagnostics, not a swallowed verdict; and
`# openforge: allow-swallow` on the offending line, or alone on the line above, annotates a
deliberate exception. Use the comment to record *why*, so the next reader inherits the reasoning
rather than the silence.

This is a heuristic scanner, not a shell parser. It reads line structure and known command
shapes. It does not classify validators invoked through a third-party action (`uses:`), and it
cannot resolve a command built at runtime from variables.

## Judgment fields

The following fields remain `review-required` until a maintainer or repository-specific policy supplies evidence:

- high-risk paths
- whether bug reproduction can be automated on the real failure path
- duplicated or obsolete prompt rules
- architecture/access-boundary guidance quality

OpenForge should not convert these into arbitrary scores solely to make the dashboard look complete.

## Portfolio workflow

```text
repository
  -> executable audit
  -> machine-observable facts
  -> maintainer review of judgment fields
  -> portfolio audit record
  -> remediation issue only for evidenced gaps
```

This implements the executable portion of OpenForge #14 and provides the reusable audit mechanism required by #15. Portfolio-wide reviewed records are the next layer; the scanner itself does not silently infer them.
