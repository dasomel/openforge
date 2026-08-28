# Agent Evaluation Adoption — 2026-08

This record captures the first cross-project application of the OpenForge Agent Behavior and trace/eval model.

## Scope

The baseline was applied to three OSS repositories with materially different runtime and risk profiles:

| Repository | Domain | Project-specific evidence boundary | Adoption PR |
| --- | --- | --- | --- |
| `dasomel/narwhal` | Kubernetes IDP / GitOps platform | unit/mock checks do not prove cluster, networking, storage, identity, or GitOps runtime behavior | `dasomel/narwhal#172` |
| `dasomel/kubemetal` | macOS/Tauri/MLX/Kubernetes desktop tooling | mocked adapters do not prove native host, Tauri, ML runtime, filesystem/process/network, or cluster behavior | `dasomel/kubemetal#51` |
| `dasomel/nfs-quota-agent` | privileged filesystem quota controller | stubbed command-runner tests do not prove quota enforcement on a real quota-enabled host/filesystem | `dasomel/nfs-quota-agent#85` |

Each adoption uses the five OpenForge baseline behaviors: `evidence-before-claim`, `scope-discipline`, `bug-fix-verification`, `task-convergence`, and `trust-and-provenance`.

## Phase 1 — portable Behavior and trace/eval contracts

The same five canonical Behavior names were viable across all three domains, while evidence classes remained project-specific. The first PR-triggered `Agent Behavior` workflow completed successfully in all three repositories.

A key reporting rule emerged: Behavior-contract CI and repository CI are separate evidence classes. A passing Behavior check must not mask unrelated repository failures, and a pre-existing repository failure must not be reported as a Behavior regression.

## Phase 2 — operational regression gate pilot

Stacked operational PRs moved the model from reference evaluation to selective operational gating:

- `dasomel/openforge#24`
- `dasomel/narwhal#173`
- `dasomel/kubemetal#52`
- `dasomel/nfs-quota-agent#86`

The pilot added canonical trace/eval schemas, incremental recorders, reviewed `baseline.eval.json` artifacts, regression gates using `false < na < true`, and selective `.agents/evals/traces/*.json` gating instead of mandatory traces for every change.

All three downstream `Agent Behavior` workflows executed the operational trace gate successfully. The pilot also exposed and corrected an early schema-portability gap in the downstream evaluators before any compliance-metric promotion.

## Phase 3 — real maintenance longitudinal pilot

OpenForge issue `#25` tracks the first pilot based on real maintenance scope rather than a reference fixture.

### Maintenance scope

The same supply-chain control was implemented against active backlog in three repositories:

- Narwhal `#52` / `#164` — immutable runtime/build inputs
- KubeMetal `#5` / `#36` — immutable air-gap and toolchain inputs
- nfs-quota-agent `#26` — hardened build and release inputs

The task was intentionally bounded to release-critical paths. Existing unrelated legacy debt outside those paths is not silently converted into a blocking failure.

### Reproduction

The operational Agent Behavior workflows themselves still used floating `actions/checkout@v4` references. This provided a concrete maintenance defect rather than an invented regression fixture.

The change:

- pinned `actions/checkout` to a reviewed 40-character commit SHA in all three downstream Agent Behavior workflows
- added a deterministic mutable-input guard that rejects `:latest`, `releases/latest/download`, and non-SHA GitHub Action references
- protected explicit CI/release/air-gap input files per repository
- committed a canonical real-task trace in each downstream repository

### CI finding and recovery

OpenForge's first validator test run found a defect in the new `:latest` detector: the initial regular expression failed to match a normal reference such as `aquasec/trivy:latest`.

This was actionable implementation evidence. The unit test failed before the validator was accepted, the expression was corrected, and the fix was propagated to all three downstream repositories.

After correction:

- OpenForge CI and Markdown passed
- OpenForge's mutable-input guard step passed
- Narwhal `Agent Behavior` passed, including immutable-input guard and operational trace gate
- KubeMetal `Agent Behavior` passed, including immutable-input guard and operational trace gate
- nfs-quota-agent `Agent Behavior` passed, including immutable-input guard and operational trace gate

Repository-specific CI remains independently reported. For example, Narwhal's separate `Version Check` is not reclassified as a Behavior failure.

### Longitudinal evidence gained

This phase satisfies the earlier requirement for real maintenance traces in at least two repositories: the same control was exercised with real task traces in three materially different projects.

It also demonstrates a useful failure/recovery cycle: deterministic testing found an implementation defect in the governance control itself before promotion. This is evidence for testability of the framework, but it is not yet evidence of a naturally occurring agent-behavior regression being blocked before merge.

## Decision on a future AGENT-005

Do **not** add `AGENT-005` yet.

The evidence now supports portability, selective operational adoption, real maintenance tracing, and deterministic gate execution. One important promotion criterion remains intentionally unmet: observe at least one genuine behavior regression from ordinary engineering work that the baseline detects and makes actionable before merge.

A future metric should require operational evidence, reviewed baseline governance, and useful regression detection rather than mere presence of `.agents/evals/` files.

## Next evidence to collect

- at least one naturally occurring behavior regression detected before merge
- maintenance-cost versus debugging/regression value over repeated real tasks
- evidence that baseline changes remain deliberate and are not lowered to suppress inconvenient findings
- continued proof that traces avoid secrets, customer data, and hidden reasoning
- confirmation that project-specific runtime evidence classes remain explicit without fragmenting portable Behavior names
