# Agent Evaluation Adoption — 2026-08

This record captures the first cross-project application of the OpenForge Agent Behavior and trace/eval model.

## Scope

The baseline was applied to three OSS repositories with materially different runtime and risk profiles:

| Repository | Domain | Project-specific evidence boundary | Adoption PR |
| --- | --- | --- | --- |
| `dasomel/narwhal` | Kubernetes IDP / GitOps platform | unit/mock checks do not prove cluster, networking, storage, identity, or GitOps runtime behavior | `dasomel/narwhal#172` |
| `dasomel/kubemetal` | macOS/Tauri/MLX/Kubernetes desktop tooling | mocked adapters do not prove native host, Tauri, ML runtime, filesystem/process/network, or cluster behavior | `dasomel/kubemetal#51` |
| `dasomel/nfs-quota-agent` | privileged filesystem quota controller | stubbed command-runner tests do not prove quota enforcement on a real quota-enabled host/filesystem | `dasomel/nfs-quota-agent#85` |

Each adoption adds the five OpenForge baseline behaviors:

1. `evidence-before-claim`
2. `scope-discipline`
3. `bug-fix-verification`
4. `task-convergence`
5. `trust-and-provenance`

Each repository also adds:

- an `openforge-agent-trace/v1` representative bug-fix trace
- a deterministic local evaluator producing `openforge-agent-eval/v1`
- a GitHub Actions `Agent Behavior` workflow validating Behavior structure and evaluating the representative trace

## Initial results

The first PR-triggered `Agent Behavior` workflow completed successfully in all three repositories.

Existing repository CI remains a separate evidence class and must not be conflated with the Behavior-contract result:

- **KubeMetal** — existing `CI` and new `Agent Behavior` workflow both passed.
- **Narwhal** — new `Agent Behavior` workflow passed. Existing `Lint & Validate` failed in `Mistakes Log format` and `kubeconform` jobs. The immediately preceding `main` run on the unchanged base commit also failed, so these failures are pre-existing and are not caused by the behavior adoption patch.
- **nfs-quota-agent** — new `Agent Behavior` workflow passed; existing repository CI was still queued at the time of this record update.

## Findings

### 1. Portable behavior names are viable

The same five canonical behavior names apply across Kubernetes platform engineering, native desktop/ML engineering, and privileged filesystem tooling.

### 2. Evidence classes must remain project-specific

The portable behavior layer is useful only if projects can strengthen the evidence boundary. A generic `verification: success` event is insufficient to claim runtime correctness. Narwhal needs cluster-aware evidence, KubeMetal needs native/runtime evidence, and nfs-quota-agent needs real quota-enabled filesystem evidence when host semantics matter.

### 3. Scope discipline is domain-specific even when the behavior is portable

The behavior name remains shared, but design-level expansion differs by project: RBAC/GitOps/topology in Narwhal, native capabilities and credential scope in KubeMetal, and privileged host/filesystem/RBAC changes in nfs-quota-agent.

### 4. Deterministic trace evaluation is useful as a baseline, not semantic proof

The local evaluators reliably validate event structure, completion evidence references, reproduction/verification presence, convergence state, scope expansion markers, and external-input provenance markers. They intentionally do not infer semantic correctness from prose or inspect hidden reasoning.

### 5. Behavior CI should stay separate from repository CI

Cross-project adoption exposed an important reporting rule: a passing behavior-contract check must not mask unrelated repository CI failures, and an unrelated pre-existing CI failure must not be misreported as a behavior-evaluation regression. These are distinct evidence classes and should be surfaced independently.

## Phase 2 — operational regression gate pilot

The next stacked phase moved the model from reference evaluation to selective operational gating.

Operational PRs:

- `dasomel/narwhal#173`
- `dasomel/kubemetal#52`
- `dasomel/nfs-quota-agent#86`
- `dasomel/openforge#24`

The pilot added:

- canonical `schemaVersion`-based trace/eval artifacts across all three repositories
- incremental event recorders for real task traces
- reviewed `baseline.eval.json` artifacts
- regression gates using the ordering `false < na < true`
- selective `.agents/evals/traces/*.json` gating instead of mandatory traces for every change
- one committed operational pilot trace per downstream repository

### Operational verification

All three downstream `Agent Behavior` workflows executed the operational trace gate and passed at the job-step level.

OpenForge's own regression-gate tests, reference gate, compliance tests, repository checks, ADR validation, supply-chain checks, and Markdown workflow also passed in the stacked operational PR.

KubeMetal's existing repository CI additionally passed on the operational stacked PR. Narwhal and nfs-quota-agent operational stacked PR evidence remains scoped to the Agent Behavior workflow because unrelated repository workflows are tracked separately.

### New finding — schema portability matters

The first downstream evaluator implementations used a simplified local schema. The operational pilot exposed that this would make eval artifacts difficult to compare across repositories. Phase 2 therefore aligned downstream traces and eval results with the OpenForge canonical schemas before adding the regression gate.

This is a positive example of the pilot doing useful work before metric promotion: portability issues were found while the model was still optional and inexpensive to change.

### New finding — selective traces are preferable to universal logging

The pilot intentionally gates only committed operational traces. This avoids creating low-signal process artifacts for ordinary changes while still allowing high-risk or agent-heavy work to gain regression protection.

A future policy should preserve this risk-based adoption model unless evidence demonstrates that broader trace capture provides enough value to justify the cost.

## Decision on a future AGENT-005

Do **not** add `AGENT-005` yet.

Three repository adoptions plus the operational regression-gate pilot establish implementation portability and CI feasibility, but there is still not enough longitudinal evidence to make trace/eval adoption a portfolio-wide compliance metric.

Before promotion, collect representative traces from real maintenance work and observe whether the baseline detects useful regressions without creating ritualized or low-signal trace data.

A future metric should require operational evidence rather than the mere presence of `.agents/evals/` files.

## Next evidence to collect

- real bug-fix traces from at least two repositories
- at least one genuine failed/regressed behavior result that produces an actionable finding before merge
- evidence that the same event vocabulary can be produced without exposing secrets, customer data, or hidden reasoning
- comparison of maintenance cost versus debugging/regression value
- confirmation that project-specific runtime evidence classes can remain explicit without fragmenting the portable behavior names
- evidence that baseline changes remain deliberate and are not used to suppress inconvenient regressions
