# Current Implementation Status

Last verified: 2026-08-28 against `main`.

OpenForge is no longer only a collection of prose standards. The repository now contains executable portfolio-governance machinery, reusable engineering templates, ADR discipline, design-system guidance and adoption evidence from active OSS repositories.

## Implemented standards

OpenForge currently documents shared standards for:

- repository and documentation structure
- development and engineering tooling
- CI/CD and CI resilience
- security and supply-chain security
- dependency / package / artifact identity
- change impact and upgrade compatibility
- AI-assisted engineering and agent engineering
- container / Kubernetes / IaC security
- secrets and machine identity
- vulnerability and incident response
- release security and exception governance
- localization
- OSS compliance
- UI/UX design-system contracts
- maintainer governance

## ADR and decision governance

Durable cross-project decisions are recorded as ADRs and linked to standards/templates rather than being buried in implementation history.

```text
ADR -> Standard -> Template / CI / Policy -> Adoption record / Issue / PR
```

English is canonical and Korean is maintained as a first-class translation for user-facing policy where provided.

## Executable compliance assessment

A portable portfolio audit engine is implemented under the reusable template/scripts area. It supports:

- portfolio-wide repository assessment
- single-repository assessment
- stable metric identifiers
- historical baseline comparison
- scorecard generation
- delta analysis
- actionable gap-issue generation
- parser/false-positive regression fixtures

The reference scorecard currently covers 14 repositories and 35 engineering/maturity metrics. After the first adoption wave the portfolio scorecard records 61.6% adoption; that value is an evidence snapshot, not a permanent target.

## Branch / repository governance

Implemented governance includes:

- branch-protection standard
- GitHub issue/PR templates
- AGENTS.md execution-contract template
- coding-standards template
- design-system contract template
- security-policy baseline
- reusable CI/release/SBOM patterns

## Design system

OpenForge includes an OSS design-system standard plus a Figma design-system reference. The rule is to share semantics, accessibility and common tokens while allowing each project to retain its own density, platform convention and visual personality.

## Agent engineering

Agent context is treated as engineering input, not free-form prompt text. Implemented guidance covers concise repository contracts, executable checks, context dilution, risky tool/plugin intake and evidence-first review.

## Portfolio adoption

OpenForge standards have already been applied to active repositories including Narwhal, nfs-quota-agent and ldapium through documentation naming, security/GitHub templates and design-system/engineering contracts.

## Documentation freshness rule

Implementation status should flow through:

```text
Implementation -> Evidence -> OSS documentation -> Blog / storytelling
```

Capabilities must not be described as implemented until they exist on the target repository's default branch with a reproducible evidence path. Issue-only or design-only work must remain labeled as planned/experimental.

## Related evidence

- `README.md`
- `docs/adr/README.md`
- `docs/agent-engineering.md`
- `docs/design-system.md`
- `docs/oss-compliance.md`
- `docs/reference-metrics.md`
- `docs/portfolio-scorecard.md`
- `docs/branch-protection.md`
- `templates/`
- `templates/scripts/audit-portfolio.py`

Refresh this file after meaningful standards, audit-engine or portfolio-adoption changes.