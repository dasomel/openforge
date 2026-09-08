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
