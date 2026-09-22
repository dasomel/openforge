# Agent Eval Reuse and Rollout

## Purpose

AGENT-005 is now portable across Narwhal, KubeMetal, and nfs-quota-agent, but the pilot repositories intentionally keep local evaluator/binder/gate copies while the OpenForge implementation remains on Draft stacked PRs.

This document defines the transition from self-contained pilots to a stable reusable OpenForge runtime without making downstream CI depend on an unmerged branch.

## Current pilot architecture

Each pilot owns its repository-specific live verification command and risk/evidence policy. The trace schema, evaluator semantics, trusted-baseline comparison, and operational profile are OpenForge contracts.

The current split is intentional:

- repository-local: risk policy, live verification command, trace selection, project-specific evidence boundaries;
- OpenForge canonical: trace/eval schemas, outcome consistency semantics, evaluator, comparator, AGENT-005 audit contract;
- duplicated during pilot: evaluator/gate/binder runtime files in downstream repositories.

## Reusable gate surface

OpenForge now provides `.github/actions/agent-eval/action.yml` as the canonical reusable gate surface. It evaluates a hydrated trace against a trusted baseline by invoking the canonical OpenForge evaluator and comparator.

The action deliberately does **not** execute arbitrary project verification commands. Live verification remains repository-owned because Kubernetes runtime checks, native/Tauri checks, and privileged filesystem checks have materially different trust and execution boundaries.

A future downstream workflow should therefore have this shape:

1. run the repository-specific verification command;
2. bind its result into a strict trace;
3. invoke the pinned OpenForge Agent Eval Gate action;
4. keep changed-path/risk/evidence correlation local or move it only after a separate stable reusable contract exists.

## Pinning policy

Do not reference `feat/agent-ops-pilot`, another feature branch, or a floating branch such as `main` from downstream production CI.

Migration is allowed only after the stacked OpenForge foundation and operational PRs are merged and the reusable surface has a stable immutable reference. The first downstream adoption should pin the action to a full OpenForge commit SHA. A release tag may be used for human-facing documentation, but CI should retain an immutable pin according to the repository supply-chain policy.

## Pilot portfolio validation

`templates/agent-eval/portfolio.pilots.yml` defines the three AGENT-005 pilots. `.github/workflows/agent-005-pilot-portfolio.yml` checks out the pilot branches only inside OpenForge CI and verifies:

- metric set `2026.10`;
- `AGENT-005 == 2` for Narwhal;
- `AGENT-005 == 2` for KubeMetal;
- `AGENT-005 == 2` for nfs-quota-agent;
- the reusable gate action can evaluate a real KubeMetal operational trace.

This pilot workflow is validation infrastructure, not a production dependency from downstream repositories.

## Removal of duplicated downstream runtime

Do not delete downstream `evaluate.py`, `gate.py`, or `bind-verification.py` merely because the reusable action exists in a Draft OpenForge PR.

Remove duplicated evaluator/gate code only when all of the following are true:

1. OpenForge foundation and operational changes are merged;
2. the reusable action is available at an immutable stable commit;
3. the downstream workflow is changed to that immutable reference;
4. equivalent pass/fail behavior is demonstrated on at least one healthy trace and one regression fixture or historical evidence case;
5. rollback to the self-contained local runtime remains straightforward during the first migration.

The binder may remain local longer than the evaluator/gate because project-specific execution and evidence boundaries are intentionally not over-generalized.
