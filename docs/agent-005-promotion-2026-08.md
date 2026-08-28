# AGENT-005 Promotion Record — 2026-08

## Decision

Promote **AGENT-005 — Operational Agent Evaluation Profile** into the canonical OpenForge portfolio metric set `2026.10`.

AGENT-005 is an adoption-level metric. It is `N/A` when the repository has not adopted `.agents/evals/` and is not explicitly configured with `agent_evals: true`.

## What AGENT-005 measures

AGENT-005 does **not** score directory or file presence alone. A passing repository must expose an executable operational contract consisting of:

- a canonical evaluator and trusted baseline;
- a regression gate;
- a live verification binder;
- at least one `consistencyMode: strict` trace;
- explicit verification status and typed evidence semantics;
- a completion claim and task outcome in the strict trace;
- CI wiring that runs live verification binding and the regression gate.

The metric intentionally does not inspect hidden reasoning or chain-of-thought.

## Promotion evidence

The promotion threshold required the same live-evidence contract to catch naturally occurring maintenance defects in two materially different domains.

### Evidence 1 — Narwhal

Narwhal PR #173 exposed an existing Kubernetes version source-of-truth drift:

- `VERSIONS.md`: `1.35.5`
- `Vagrantfile`: `1.35.7`

The real consistency command exited 1. The live binder recorded failed verification and the trusted baseline gate detected:

- `bug-fix-verification`: `true -> false`
- `evidence-before-claim`: `true -> false`
- `task-convergence`: `true -> false`

After the source-of-truth repair, the same command, evaluator and baseline passed without policy relaxation.

### Evidence 2 — nfs-quota-agent

nfs-quota-agent PR #86 used a different runtime boundary: the shipped container filesystem tools.

The compatibility matrix already recorded Btrfs as a known gap because the implementation invokes the `btrfs` CLI while the runtime image did not install `btrfs-progs`.

The live check built the actual shipped image and verified commands inside the container. `xfs_quota`, `setquota`, `chattr`, and `findmnt` were present; `btrfs` was missing. The binder recorded exit 1 and the same three Behavior regressions blocked the gate.

The repair added `btrfs-progs`, updated package-license evidence, and changed Btrfs compatibility from `known-gap` to `build-verified` only — not `verified`, because a real Btrfs filesystem E2E has not yet been performed. The same live image check then passed.

## Why promotion is justified

The two pilots differ in failure domain and verification mechanism:

- Narwhal: repository/runtime version consistency;
- nfs-quota-agent: built container runtime capability.

Both used the same observable-evidence semantics and both blocked false completion claims without collecting private reasoning. This demonstrates portability beyond a single repository-specific fixture.

## Guardrails

AGENT-005 remains structural/operational capability scoring, not a claim that every maintenance task is traced. Repositories should use traces selectively for agent-heavy or high-risk work. Baselines must not be weakened merely to make CI green, and compatibility evidence must distinguish build/runtime-tool verification from real infrastructure E2E evidence.
