# CI/CD Standard

CI should provide repeatable validation before merge, while CD should provide controlled and reproducible delivery.

## Minimum CI

```text
format → lint → typecheck → test → build
```

Add when applicable:

- integration tests
- E2E tests
- container build
- vulnerability scan
- license scan
- SBOM
- provenance/attestation
- Helm/Kubernetes validation
- dependency/version consistency checks
- documentation and bilingual filename checks

## Workflow contract

A repository build command is a contract with every workflow that invokes it.

When a dependency, runtime, package manager or build command changes, inspect **all** CI, CD and release workflows that may execute the affected command.

Each affected workflow MUST explicitly install or inherit required runtimes/tools. Do not rely on implicit runner-installed tools.

Prefer:

```text
setup runtime/toolchain
→ verify version
→ install dependencies deterministically
→ test
→ build/package/release
```

For Class C/D changes, follow `docs/change-management.md` and record workflow impact.

## Pull Requests

Required checks should be branch-protection candidates.

PRs should link the related Issue and explain tests, documentation impact, architectural impact and, for Class C/D changes, affected workflows and runtime/toolchain changes.

## Supply chain

For release-producing repositories, prefer:

```text
Source → Dependency/Provenance → Build → Test → Scan → SBOM/Provenance → Sign → Publish
```

Use workflow hardening and repository security controls where supported. Keep release permissions minimal.

See `docs/supply-chain.md` for cooling, immutable inputs, build-time trust boundaries, progressive adoption and rollback requirements.

## Regression knowledge

Known integration failures should become deterministic CI checks when practical. Keep the check linked to the corresponding Issue, incident/lesson record or ADR.

A historical CI failure should become a check against the failure class, not only a one-off fix.

## Release delivery

Release workflows should be deterministic, versioned and traceable to a commit. Every release-producing workflow should independently satisfy the repository build contract.

## Air-gapped / self-hosted projects

Avoid assuming public registries or internet access at runtime. Pin and document required artifacts when offline operation matters. Validate the complete offline asset set, not only container images.