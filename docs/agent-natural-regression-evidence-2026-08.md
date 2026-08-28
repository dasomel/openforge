# Natural Agent Behavior Regression Evidence — 2026-08

## Status

OpenForge now has its first non-synthetic example of a repository failure being converted into a Behavior regression and blocked before merge.

Repository: `dasomel/narwhal`
Operational PR: `#173`
Failure commit: `bb81d27b5187dcba736f8ed032f0ff4360e3353c`
Repair commit: `2ed07160014a1bb97c0c0d783101d0fa2b0a11b6`

## Natural failure

Narwhal's existing Version Check reported a real source-of-truth drift:

- `VERSIONS.md`: Kubernetes `1.35.5`
- `Vagrantfile`: Kubernetes `1.35.7`

This was not introduced as a negative fixture and was already failing in the repository's normal CI evidence class.

## Live evidence binding

The version consistency logic was extracted into one deterministic command used by both the dedicated Version Check workflow and the Agent Behavior workflow.

`bind-agent-verification.py` executes a real verification command and hydrates strict trace verification events with:

- `status: passed|failed`
- `commandExitCode`
- `runtime:command-exit-<code>` evidence

The binder itself does not hide a failed command behind a tool error. A failed verification is written as structured evidence and the strict evaluator owns the policy decision.

## Behavior regression observed

On failure commit `bb81d27...`:

1. the live version command exited `1`;
2. trace events were hydrated as `status=failed`;
3. the strict behavior gate compared the hydrated trace with the trusted baseline;
4. three real regressions were detected:
   - `bug-fix-verification`: `true -> false`
   - `evidence-before-claim`: `true -> false`
   - `task-convergence`: `true -> false`
5. the Agent Behavior workflow failed before merge.

This is the evidence target that earlier phases intentionally waited for: a normal repository consistency defect, not a synthetic fixture or a bug in the governance implementation itself.

## Repair

The Narwhal Kubernetes source-of-truth rows were aligned to the repository's verified runtime pin (`1.35.7`). The same shared command is then expected to hydrate the trace as `passed`, allowing the unchanged strict evaluator and baseline comparison to succeed.

## Why this matters

The operational chain is now executable end-to-end:

`real repository check -> command exit status -> strict trace -> Behavior outcome -> baseline comparison -> merge gate`

No hidden reasoning, chain-of-thought, secret, or customer data is required. Only observable command results and repository-scoped evidence are recorded.

## AGENT-005 decision

Do not promote AGENT-005 from this single repository result alone.

This event satisfies the previously missing natural-regression criterion, but portfolio-level compliance should demonstrate portability of live evidence binding in at least one additional domain before becoming canonical. KubeMetal native/runtime verification or nfs-quota-agent filesystem/quota verification are suitable next candidates.

Until then, treat this as **promotion evidence 1/2**, not as a portfolio score.
