# Change Management and Impact Analysis Standard

OpenForge treats engineering changes as changes to a system contract, not only changes to source code.

A dependency, runtime, build command or developer-tool change can alter CI workflows, release workflows, deployment assumptions, generated artifacts and operational procedures even when application code remains compatible.

## Change impact

Every non-trivial change MUST consider:

- source/build commands
- package manager and dependency resolution
- runtime/toolchain version
- generated files and generators
- CI workflows
- CD/deployment workflows
- release/packaging workflows
- test/E2E environments
- containers/base images
- documentation and operational procedures
- offline/air-gapped assets
- security and supply-chain controls

A change is incomplete when the implementation is correct but a consuming workflow still relies on the old contract.

## Impact matrix

| Area | Question |
|---|---|
| Source | Which scripts, commands or APIs changed? |
| Dependencies | Did package manager, lockfile or version resolution change? |
| Runtime | Does the required runtime/toolchain change? |
| CI | Which workflows execute the changed command? |
| CD | Which deployment workflows execute it? |
| Release | Which packaging/publishing workflows are affected? |
| Generated output | Are RSS, docs, manifests or other artifacts regenerated? |
| Security | Are new executable/download/build inputs introduced? |
| Offline | Are new cached or mirrored artifacts required? |
| Documentation | Do setup, development or release instructions change? |

For dependency, runtime or toolchain changes, the impact matrix belongs in the PR or linked Issue.

## Workflow inventory rule

When a build or toolchain contract changes, search **all workflows** for the affected command, package manager and runtime before merge.

For example, changing a Node build command from a pure Node operation to:

```text
npm run build
  → bun <script>
```

requires inspection of every workflow that can execute the build, packaging scripts, release scripts or generated-output scripts.

Do not assume that a tool installed by one workflow exists in another workflow.

## Runtime/toolchain consistency

If a build or release contract requires a runtime/toolchain, every affected workflow MUST declare it explicitly or inherit it through a documented reusable workflow.

Examples include Node/npm/pnpm/Bun, Python/uv/Poetry, Go, Rust/Cargo, JDK/Maven/Gradle, Packer, Terraform, kubectl and Helm.

A workflow MUST NOT rely on an implicitly preinstalled tool.

Prefer:

```text
setup runtime
→ verify version
→ install dependencies deterministically
→ execute build/test/release
```

Where reproducibility matters, record the expected version.

## Workflow contract checks

Where practical, CI should verify the expected toolchain before doing expensive work:

```text
bun --version
node --version
pnpm --version
go version
rustc --version
java -version
```

Fail early on missing or incompatible tools instead of producing a later opaque error.

## Change classes

### Class A — Documentation-only

No executable or release contract changes.

The Issue/PR is the change record. A separate Change Package is not required.

### Class B — Internal implementation

Behavior changes without changing external build/release contracts.

The Issue MUST state acceptance criteria. A lightweight task checklist is recommended when the
implementation has multiple independently verifiable steps. A full Change Package is optional
unless the change is complex, crosses component boundaries or has material operational risk.

### Class C — Dependency/runtime/toolchain

Examples:

- Bun adoption
- Node/Python/Go/Rust/JDK upgrade
- package-manager migration
- CI action/tool upgrade
- build plugin or code-generator change

Class C MUST include change impact analysis.

Class C MUST use a Change Package before broad implementation begins.

### Class D — Release/deployment/security boundary

Changes that alter produced artifacts, deployment permissions, release inputs or security controls.

Class D MUST include change impact analysis and explicit security/release evidence.

Class D MUST use a Change Package before broad implementation begins. An ADR is also required when
the change crosses the threshold in `docs/decision-management.md`.

## Change Package

A Change Package is a short-lived, change-scoped contract that fixes intent, requirements,
acceptance scenarios and verification before implementation. It is not a second long-lived
description of the whole system.

Use the reusable [`CHANGE.md`](../templates/change/CHANGE.md) and
[`TASKS.md`](../templates/change/TASKS.md) templates for Class C, Class D and complex Class B work.
The package MAY be maintained directly in the Issue/PR when that is the clearest collaboration
surface. Temporary files MAY be used on a working branch, but they SHOULD NOT be merged as a
permanent `changes/` archive unless they remain useful operational documentation.

The Change Package MUST identify:

- problem, intent, scope and non-goals;
- testable requirements with stable identifiers;
- explicit acceptance scenarios, preferably `Given / When / Then` for behavior;
- relevant architecture decisions or an explanation that no ADR is required;
- change impact using the matrix in this standard;
- implementation tasks and dependencies;
- verification plan and expected evidence;
- rollout, rollback or recovery for changes that can affect users or operations;
- portfolio/downstream impact when a reusable contract changes.

Requirements, tasks and evidence SHOULD remain traceable. A reviewer should be able to map each
material requirement to an acceptance scenario, implementation task and verification result.

### Review gate

For Class C and D changes, the accountable maintainer MUST review and accept the Change Package
before broad implementation. Exploration, reproduction and reversible prototypes MAY occur before
acceptance, but they must not silently establish the final contract or mutate production/shared
environments.

Acceptance means the problem, intended outcome, boundaries and verification approach are clear
enough to implement. It does not require every implementation detail to be known in advance.
Material scope or requirement changes after acceptance MUST be reflected in the package and
re-reviewed.

### Lifecycle and source of truth

```text
Issue
  → classify change
  → create/review Change Package when required
  → implement tracked tasks
  → verify acceptance scenarios
  → capture evidence
  → synchronize durable truth
  → review and merge
```

At completion, promote durable truth to the artifact that owns it:

- behavior and invariants → code and tests;
- current operating contract → normative documentation;
- durable rationale → ADR;
- measured result → evidence record;
- cross-project state → portfolio status;
- change history → Issue, PR and Git history.

Do not create a parallel long-lived specification tree that duplicates code, tests, documentation
or ADRs. The merged Issue/PR is the default archive for the change intent and review history.

## Regression rule

When a change exposes an integration failure, convert the failure into a deterministic regression check where practical.

For example, when a build starts requiring Bun, every release-producing workflow that invokes the build contract should verify that the required Bun version is installed. The durable regression should prevent the whole class of workflow configuration drift, not only the historical failure.

## Supply-chain linkage

Class C and D changes MUST follow `docs/supply-chain.md`.

```text
Change request
  → compatibility
  → dependency/provenance review
  → change impact analysis
  → CI/CD contract validation
  → isolated build/test
  → evidence
  → progressive adoption
```

A compatible dependency upgrade that silently changes a build script, install hook, generated artifact or required CI runtime is not a low-risk change.

## PR requirements

A non-trivial change PR SHOULD state:

- change class
- affected contracts
- affected workflows
- runtime/toolchain changes
- dependency/lockfile changes
- documentation impact
- tests and workflow validation
- rollback or mitigation when release behavior changes

## Reusable workflow preference

When multiple workflows require the same runtime/toolchain setup, prefer a reusable workflow or shared setup action to reduce version drift.

If workflows intentionally use different runtime versions, document the reason and compatibility boundary.

## Release gate

Before release, confirm:

- source build succeeds in every release-producing workflow
- required runtimes/tools are explicitly installed and version-verified
- dependency lock/integrity checks pass
- SBOM/provenance includes relevant build inputs
- generated artifacts are refreshed when required
- release documentation matches implemented commands
- offline/air-gapped assets are complete where applicable

## Historical regression pattern

A build command can remain syntactically valid while changing its runtime requirements:

```text
package.json
  "build": "next build && bun scripts/generate-rss.js"
```

The CI step may still be only:

```text
npm run build
```

The command change therefore changes the build contract. Every workflow invoking it must be checked for Bun setup and version verification. A single workflow having Bun installed does not satisfy independent workflows.
