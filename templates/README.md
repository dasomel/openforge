# OpenForge Templates

OpenForge provides copyable implementation and design templates for projects that adopt the standards.

Templates are deliberately conservative. Adapt versions, permissions, paths, commands, domains, images, identities, and ecosystem-specific controls rather than treating them as universal drop-in configuration.

## Structure

```text
templates/
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
└── design/          # README / landing page / architecture / status / tokens
```

## Adoption guidance

1. Start from the closest ecosystem template.
2. Replace placeholders and pin security-sensitive inputs.
3. Run the project's CI, security, and compatibility checks.
4. Document deviations from the baseline.
5. Keep derived assets (such as SVG exports) generated from source-controlled definitions when possible.
