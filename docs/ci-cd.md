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
- Helm/Kubernetes validation

## Pull Requests

Required checks should be branch-protection candidates.

## Release delivery

Release workflows should be deterministic, versioned and traceable to a commit.

## Air-gapped / self-hosted projects

Avoid assuming public registries or internet access at runtime. Pin and document required artifacts when offline operation matters.
