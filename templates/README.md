# OpenForge Templates

OpenForge provides copyable implementation and design templates for projects that adopt the standards.

Templates are deliberately conservative. Adapt versions, permissions, paths, commands, domains, images, identities, and ecosystem-specific controls rather than treating them as universal drop-in configuration.

## Project-level contracts

- [`AGENTS.md`](AGENTS.md) — concise agent execution contract
- [`CODING_STANDARDS.md`](CODING_STANDARDS.md) — detailed coding/review rules
- [`DESIGN.md`](DESIGN.md) — project design-system contract
- [`ADR.md`](ADR.md) — canonical English architecture/engineering decision record
- [`ADR-ko.md`](ADR-ko.md) — Korean first-class ADR counterpart

A durable cross-project policy decision should be evaluated against the [Decision Management Standard](../docs/decision-management.md) before adopting a template change as a new OpenForge default.

## Structure

```text
templates/
├── AGENTS.md
├── CODING_STANDARDS.md
├── DESIGN.md
├── ADR.md
├── ADR-ko.md
├── github/          # PR / CODEOWNERS
├── workflows/       # CI / release / SBOM
├── scripts/         # toolchain / validation helpers
├── policy/          # dependency / engineering policy
├── container/       # Docker baseline
├── kubernetes/      # Kubernetes workload baseline
├── gitops/          # Argo CD / GitOps baseline
├── identity/        # OIDC / SSO integration contract
├── observability/   # health / metrics / traces / logs
├── backup/          # backup / restore
├── offline/         # air-gap bundle manifest
├── documentation/   # independent OSS documentation portal blueprint
└── design/          # README / landing page / architecture / status / tokens
```

## Adoption guidance

1. Start from the closest ecosystem template.
2. Replace placeholders and pin security-sensitive inputs.
3. Determine whether the change crosses the ADR threshold when changing a reusable OpenForge default.
4. Run the project's CI, security, and compatibility checks.
5. For OSS documentation, use `templates/documentation/blueprint.md` as the contract and expose the project through the shared `/oss/` hub.
6. Document intentional deviations from the baseline.
7. Keep derived assets (such as SVG exports) generated from source-controlled definitions when possible.
