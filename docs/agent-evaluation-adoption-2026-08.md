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

## Phase 6 — outcome/evidence consistency

A trace file and a verification event are no longer sufficient for high-risk completion.

Strict traces encode verification status structurally. A convergence state `A` requires a completion claim plus explicitly passed scoped verification. Failed, pending, unknown, skipped, unverified, or status-less relevant verification makes `task-convergence` false. A completion claim against failed/non-passed verification also makes `evidence-before-claim` false.

Strict bug-fix traces require `regression_verification` to be explicitly passed. States `B` and `C` support meaningful progress/stop, but require a next action and must not coexist with a completion claim in strict mode.

Historical traces remain compatible in legacy mode. The high-risk evidence-correlation gate requires strict mode only for traces relevant to the current high-risk diff, avoiding forced migration of unrelated historical evidence.

### Cross-project rollout

OpenForge, Narwhal, KubeMetal, and nfs-quota-agent evaluators implement the strict consistency semantics. The current operational maintenance trace in each repository was upgraded to `consistencyMode: strict` with explicit `status: passed` verification and regression-verification events.

The high-risk evidence checker additionally requires a relevant trace to be strict and to contain at least one explicitly passed verification event.

### Verification evidence

The strict implementation was exercised by the real stacked PRs. OpenForge CI/Markdown and the Agent Behavior workflows in Narwhal, KubeMetal, and nfs-quota-agent passed after the evaluator, evidence checker, and operational traces were upgraded. KubeMetal repository CI is reported separately, while Narwhal Version Check remains a separate evidence class.

## Findings

- Portable behavior names remain viable across the three domains.
- Evidence classes and high-risk path profiles must remain project-specific.
- Behavior CI and repository/runtime CI must remain separate evidence classes.
- Historical trace compatibility is important; only traces relevant to current high-risk work should be forced onto the newest operational contract.
- Completion semantics must be tied to actual verification state, not only to the presence of verification prose.

## AGENT-005 decision

Do **not** add `AGENT-005` yet.

The system can now deterministically map inconsistent completion claims into existing Behavior regressions (`true -> false`) without inventing a new score. The remaining strongest promotion evidence is a naturally occurring development regression that this strict baseline gate blocks before merge, rather than a synthetic negative fixture or governance-tool implementation defect.
