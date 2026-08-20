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

## Pull Requests

Required checks should be branch-protection candidates.

PRs should link the related Issue and explain tests, documentation impact and architectural impact.

## Supply chain

For release-producing repositories, prefer:

```text
Source → Build → Test → Scan → SBOM/Provenance → Sign → Publish
```

Use workflow hardening and repository security controls where supported. Keep release permissions minimal.

## Regression knowledge

Known integration failures should become deterministic CI checks when practical. Keep the check linked to the corresponding Issue, incident/lesson record or ADR.

## Release delivery

Release workflows should be deterministic, versioned and traceable to a commit.

## Air-gapped / self-hosted projects

Avoid assuming public registries or internet access at runtime. Pin and document required artifacts when offline operation matters. Validate the complete offline asset set, not only container images.
