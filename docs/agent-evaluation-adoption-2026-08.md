# Agent Evaluation Adoption — 2026-08

This record captures the cross-project application of the OpenForge Agent Behavior and trace/eval model.

## Scope

The baseline is applied to three OSS repositories with materially different runtime and risk profiles:

| Repository | Domain | Project-specific evidence boundary | Adoption PR |
| --- | --- | --- | --- |
| `dasomel/narwhal` | Kubernetes IDP / GitOps platform | unit/mock checks do not prove cluster, networking, storage, identity, or GitOps runtime behavior | `dasomel/narwhal#172` |
| `dasomel/kubemetal` | macOS/Tauri/MLX/Kubernetes desktop tooling | mocked adapters do not prove native host, Tauri, ML runtime, filesystem/process/network, or cluster behavior | `dasomel/kubemetal#51` |
| `dasomel/nfs-quota-agent` | privileged filesystem quota controller | stubbed command-runner tests do not prove quota enforcement on a real quota-enabled host/filesystem | `dasomel/nfs-quota-agent#85` |

## Phase summary

1. Baseline Behavior specs were adopted across all three repositories.
2. Canonical trace/eval schemas and trusted baseline regression gates were added.
3. Real supply-chain maintenance produced committed operational traces and immutable-input guards.
4. Repository risk policies began requiring same-diff traces for high-risk changes.
5. Trace/change evidence correlation required current high-risk paths, scoped verification, and typed evidence to agree.
6. Outcome/evidence consistency now requires current high-risk traces to use `consistencyMode: strict`.
7. Live command results are now bound into strict trace verification status and evaluated before completion claims are accepted.
8. Two naturally occurring maintenance defects in materially different runtime domains were blocked by the same Behavior regression contract.
9. AGENT-005 was promoted as an adoption-level executable operational profile in metric set `2026.10`.

## Phase 6 — outcome/evidence consistency

A trace file and a verification event are no longer sufficient for high-risk completion.

Strict traces encode verification status structurally. A convergence state `A` requires a completion claim plus explicitly passed scoped verification. Failed, pending, unknown, skipped, unverified, or status-less relevant verification makes `task-convergence` false. A completion claim against failed/non-passed verification also makes `evidence-before-claim` false.

Strict bug-fix traces require `regression_verification` to be explicitly passed. States `B` and `C` support meaningful progress/stop, but require a next action and must not coexist with a completion claim in strict mode.

Historical traces remain compatible in legacy mode. The high-risk evidence-correlation gate requires strict mode only for traces relevant to the current high-risk diff, avoiding forced migration of unrelated historical evidence.

### Cross-project rollout

OpenForge, Narwhal, KubeMetal, and nfs-quota-agent evaluators implement the strict consistency semantics. The current operational maintenance trace in each repository was upgraded to `consistencyMode: strict` with explicit verification status.

The high-risk evidence checker additionally requires a relevant trace to be strict and to contain at least one explicitly passed verification event.

## Phase 7 — live evidence and natural regressions

The next step replaced static verification prose with observable command results. A live verification binder executes a real maintenance/runtime command and writes its result into strict verification events as `status: passed|failed`, `commandExitCode`, and typed runtime evidence. The binder itself does not decide policy; the evaluator and trusted baseline gate do.

### Natural regression 1 — Narwhal

Narwhal PR #173 exposed an existing Kubernetes version source-of-truth drift: `VERSIONS.md` declared `1.35.5` while `Vagrantfile` pinned `1.35.7`. The shared consistency command exited 1, the trace was hydrated as failed, and the baseline gate detected three regressions before merge:

- `bug-fix-verification`: `true -> false`
- `evidence-before-claim`: `true -> false`
- `task-convergence`: `true -> false`

After the source-of-truth repair, the same command/evaluator/baseline path passed without weakening policy.

### Natural regression 2 — nfs-quota-agent

nfs-quota-agent PR #86 exercised a different runtime boundary: commands available inside the actual shipped container image. The repository already documented Btrfs as a known gap because `internal/quota/btrfs.go` invokes the `btrfs` CLI while the image did not install `btrfs-progs`.

The live check built the real image and verified commands in-container. `xfs_quota`, `setquota`, `chattr`, and `findmnt` were present while `btrfs` was missing. The binder recorded exit 1 and the same three Behavior regressions blocked the gate.

The repair added `btrfs-progs`, updated NOTICE/package-license evidence, and changed Btrfs compatibility from `known-gap` to `build-verified`. It was deliberately not promoted to `verified` because a real Btrfs filesystem E2E has not yet been performed. The same live image check passed after the repair.

## Findings

- Portable behavior names remain viable across the three domains.
- Evidence classes and high-risk path profiles must remain project-specific.
- Behavior CI and repository/runtime CI must remain separate evidence classes.
- Historical trace compatibility is important; only traces relevant to current high-risk work should be forced onto the newest operational contract.
- Completion semantics must be tied to actual verification state, not only to the presence of verification prose.
- Live command binding is portable across repository consistency and built-container runtime verification.
- Compatibility claims must preserve evidence strength; fixing an image dependency can justify `build-verified` without implying real filesystem E2E verification.

## AGENT-005 decision

**Promote AGENT-005.**

The previously required promotion evidence is now satisfied by two naturally occurring regressions in different runtime domains. AGENT-005 is included in canonical metric set `2026.10` as an adoption-level **Operational Agent Evaluation Profile**.

AGENT-005 does not score `.agents/evals/` directory presence. A passing profile requires an executable contract: evaluator, trusted baseline, regression gate, live verification binder, at least one strict trace with explicit status and typed evidence, completion/outcome semantics, and CI wiring that actually executes live binding and regression gating.

Repositories that have not adopted the profile remain `N/A`; `agent_evals: true` makes it required and `agent_evals: false` explicitly disables the optional profile.

See `docs/agent-005-promotion-2026-08.md` for the promotion evidence record.
