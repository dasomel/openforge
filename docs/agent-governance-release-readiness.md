# Agent Governance Release Readiness

This document defines the safe merge and rollout sequence for the OpenForge Agent Behavior / Agent Evaluation stack.

## Current stack

### OpenForge

1. PR #19 — `feat/agent-behaviors` → `main`
   - AGENT-004 / Behavior specifications
   - trace/eval foundation
   - metric set `2026.09`
2. PR #24 — `feat/agent-ops-pilot` → `feat/agent-behaviors`
   - operational traces and risk/evidence gates
   - live verification binding
   - AGENT-005
   - metric set `2026.10`
   - pilot portfolio and reusable gate action

### Downstream pilots

| Repository | Foundation | Operational |
| --- | --- | --- |
| Narwhal | #172 | #173 |
| KubeMetal | #51 | #52 |
| nfs-quota-agent | #85 | #86 |

Every operational PR is stacked on its repository foundation branch.

## Mandatory merge order

Do not merge an operational PR while it still targets its feature foundation branch. Doing so would fold the operational layer into the foundation branch and make the later foundation merge include both layers unintentionally.

Use this sequence:

1. Merge OpenForge #19 to `main` after required checks pass.
2. Retarget OpenForge #24 from `feat/agent-behaviors` to `main`.
3. Confirm #24 diff contains only the operational layer and re-run all required checks plus AGENT-005 Pilot Portfolio.
4. Merge #24 to `main` only after the retargeted diff is clean.
5. For each downstream repository, merge the foundation PR first.
6. Retarget that repository's operational PR to `main`.
7. Confirm the retargeted operational diff and re-run repository CI / Agent Behavior CI.
8. Merge operational PR only after repository-specific blockers are resolved.

The three downstream repositories do not need to be merged in a fixed order after their own foundation has landed. KubeMetal is the lowest-risk first rollout because both Agent Behavior and existing repository CI are green. Narwhal must continue to keep unrelated repository-CI failures separate from Agent Behavior evidence.

## Pre-merge checks

For every foundation PR:

- branch contains current `main` or GitHub reports a clean merge state;
- required repository checks complete;
- Behavior spec validation succeeds;
- no operational-only files accidentally appear in the foundation diff.

For every operational PR:

- base is `main` after foundation merge;
- `consistencyMode: strict` traces remain valid;
- live verification binding executes a real repository-owned check;
- high-risk diff / trace / typed evidence correlation passes;
- trusted baseline comparison passes;
- immutable-input guard passes where adopted;
- repository/runtime CI is reported as a separate evidence class.

## OpenForge stable reusable action rollout

Do not make downstream CI depend on an unmerged branch.

After OpenForge #24 is merged:

1. Record the immutable OpenForge `main` commit SHA containing `.github/actions/agent-eval/action.yml`.
2. Validate the action from that immutable SHA against all three pilot repositories.
3. Migrate one downstream repository first, preferably KubeMetal.
4. Run local and reusable gates in parallel and require pass/fail equivalence.
5. Remove the local evaluator/comparator only after equivalence is demonstrated.
6. Keep repository-owned live verification commands, risk policy, evidence boundaries, and binder semantics local.
7. Roll out to Narwhal and nfs-quota-agent after the canary migration remains stable.

Rollback is always replacing the remote reusable gate invocation with the last known-good local gate implementation.

## Current readiness snapshot

- OpenForge #19 is synchronized with current `main` and its CI / Markdown checks pass.
- OpenForge #24 includes the refreshed #19 ancestry; CI, Markdown, and AGENT-005 Pilot Portfolio pass.
- Narwhal #172/#173 remain Draft and mergeable; repository-CI evidence must continue to be evaluated separately.
- KubeMetal #51/#52 remain Draft and mergeable; both Agent Behavior and repository CI passed at the latest operational head.
- nfs-quota-agent #85/#86 remain Draft and mergeable; the operational layer includes the repaired shipped-container Btrfs runtime dependency and live filesystem evidence gate.

No PR should be merged solely because this document says it is ready; use the latest GitHub checks and current base/head SHAs at merge time.