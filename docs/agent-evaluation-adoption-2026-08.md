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

## Phase 3 — real maintenance longitudinal pilot

The operational model was then applied to real supply-chain maintenance rather than only representative fixtures.

Tracked work:

- OpenForge #25
- Narwhal #52 / #164
- KubeMetal #5 / #36
- nfs-quota-agent #26

The pilot added a deterministic mutable-input guard for protected release/build paths, removed remaining floating `actions/checkout@v4` references from the downstream Agent Behavior workflows, and recorded one canonical real-maintenance trace in each downstream repository.

The first OpenForge test run found a real defect in the new `:latest` detector. `test_rejects_latest_image` failed because the initial regex missed a normal image reference such as `aquasec/trivy:latest`. The detector was corrected and propagated downstream. Subsequent OpenForge CI/Markdown and all three downstream Agent Behavior workflows passed.

This was useful operational evidence because the governance control itself was tested, failed, repaired, and reverified instead of being assumed correct.

## Phase 4 — risk-based same-diff trace enforcement

Selective trace adoption was strengthened so that repositories no longer depend on maintainers remembering when to add a trace.

A repository-local `openforge-agent-risk-policy/v1` now classifies changed paths as `low`, `medium`, or `high`. For PRs, the highest matching risk wins. When the resulting risk is configured to require evidence, the PR must add or modify an operational trace in the same diff.

The gate therefore distinguishes:

- a trace that merely exists somewhere in repository history, and
- a trace that was actually updated for the current high-risk change.

Project-specific profiles preserve the common behavior model while allowing different high-risk boundaries:

- Narwhal: CI/release, air-gap, install/security scripts, GitOps desired state, version sources
- KubeMetal: CI/release, air-gap, Kubernetes mutation, MLX runtime, Tauri native code
- nfs-quota-agent: CI/release, controller code, privileged reconciliation, Helm/RBAC, image and compatibility tooling

OpenForge uses `templates/agent-eval/traces/` as its canonical trace path because it distributes reusable templates rather than only consuming the downstream `.agents/evals/` layout.

### Risk-gate rollout failure and recovery

The first OpenForge risk-gate run failed even though the unit tests passed. The initial policy expected downstream `.agents/evals/traces/` layout and therefore could not see an OpenForge template trace.

The failure was not bypassed. The repository profile was corrected to `templates/agent-eval/traces/`, a real trace for the risk-gate rollout was added, and OpenForge CI then passed. All three downstream Agent Behavior workflows also passed with both changed-path collection and the new `Require operational trace for high-risk changes` step executed successfully.

This provides concrete evidence for task convergence and recovery: the gate exposed a policy/layout mismatch, the cause was narrowed, the contract was corrected, and the same check was rerun successfully.

## Decision on a future AGENT-005

Do **not** add `AGENT-005` yet.

Cross-project portability, canonical trace/eval schemas, real maintenance traces, same-diff high-risk trace enforcement, and deterministic regression gates are now demonstrated.

The remaining high-value evidence target is still a naturally occurring agent-behavior regression that the baseline gate catches before merge. Synthetic negative fixtures and governance-tool implementation defects are valuable, but they should not be counted as proof that a portfolio-wide operational behavior metric has matured.

## Next evidence to collect

- at least one naturally occurring `true -> false`, `true -> na`, or `na -> false` behavior regression blocked before merge
- evidence that the same event vocabulary can be produced without exposing secrets, customer data, or hidden reasoning
- comparison of maintenance cost versus debugging/regression value under the new risk-based selective policy
- confirmation that repository-specific risk profiles remain understandable and do not grow into unreviewable path lists
- evidence that baseline changes remain deliberate and are not used to suppress inconvenient regressions
