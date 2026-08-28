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

At the first PR-triggered execution, the new `Agent Behavior` workflow completed successfully in all three repositories.

Existing repository CI remains a separate evidence class and must not be conflated with the Behavior-contract result. At the time this adoption record was created, existing CI was still running or queued in the three downstream PRs.

## Findings

### 1. Portable behavior names are viable

The same five canonical behavior names apply across Kubernetes platform engineering, native desktop/ML engineering, and privileged filesystem tooling.

### 2. Evidence classes must remain project-specific

The portable behavior layer is useful only if projects can strengthen the evidence boundary. A generic `verification: success` event is insufficient to claim runtime correctness. Narwhal needs cluster-aware evidence, KubeMetal needs native/runtime evidence, and nfs-quota-agent needs real quota-enabled filesystem evidence when host semantics matter.

### 3. Scope discipline is domain-specific even when the behavior is portable

The behavior name remains shared, but design-level expansion differs by project: RBAC/GitOps/topology in Narwhal, native capabilities and credential scope in KubeMetal, and privileged host/filesystem/RBAC changes in nfs-quota-agent.

### 4. Deterministic trace evaluation is useful as a baseline, not semantic proof

The local evaluators reliably validate event structure, completion evidence references, reproduction/verification presence, convergence state, scope expansion markers, and external-input provenance markers. They intentionally do not infer semantic correctness from prose or inspect hidden reasoning.

## Decision on a future AGENT-005

Do **not** add `AGENT-005` yet.

Three repository adoptions provide meaningful implementation evidence, but not enough longitudinal evidence to make trace/eval adoption a portfolio-wide compliance metric. Before promotion, collect representative traces from real maintenance work and observe whether the baseline detects useful regressions without creating ritualized or low-signal trace data.

A future metric should require operational evidence rather than the mere presence of `.agents/evals/` files.

## Next evidence to collect

- real bug-fix traces from at least two repositories
- at least one failed/regressed behavior result that produces an actionable finding
- evidence that the same event vocabulary can be produced without exposing secrets, customer data, or hidden reasoning
- comparison of maintenance cost versus debugging/regression value
- confirmation that project-specific runtime evidence classes can remain explicit without fragmenting the portable behavior names
