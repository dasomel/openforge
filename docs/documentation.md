# Documentation Standard

OpenForge standardizes **project-owned, user-facing** documentation as separate English and Korean files.

Documentation is not considered complete merely because files exist. For an OSS project, the documentation set must help a new user move through the adoption path:

```text
Discover -> Understand -> Install -> Verify -> Operate -> Troubleshoot -> Contribute
```

The primary quality question is therefore: **can someone who is not the maintainer reach a verified first success without private context?**

## File naming

```text
README.md
README-ko.md

docs/architecture.md
docs/architecture-ko.md
```

English is the canonical filename. Korean uses the `-ko.md` suffix.

## Rules

- Keep English and Korean semantically synchronized.
- Use relative links between language versions.
- Put project-owned user-facing documentation in Markdown unless another format is required by the ecosystem.
- Keep README focused on purpose, scope, current status, prerequisites, quick start, first-success verification, architecture, documentation navigation, support/contribution and license.
- Put detailed operational content under `docs/`.
- Separate **verified behavior** from plans, targets and unverified claims.
- Make the shortest supported installation path obvious; do not force first-time users to reconstruct it from design documents.
- Provide an explicit verification step after installation. A successful render, build or pod start is not automatically a successful product outcome.
- Document known limitations and supported environments close to the Quick Start.
- Provide troubleshooting for the failures a new adopter is most likely to hit.
- Record architecture decisions as ADRs.
- Record important operational failures as lessons/incidents/mistakes and connect them to tests when practical.
- Do not put secrets, private endpoints or credentials in documentation.
- Treat build, runtime, dependency and release contracts as documented engineering interfaces.
- Update relevant documentation when a change modifies those contracts.
- Prefer evidence links to marketing claims: tests, release artifacts, compatibility matrices, measured baselines and reproducible examples.
- Do not infer adoption from stars, forks or raw contributor counts. Document external adoption only when a source or user report exists.

## Documentation set

Recommended minimum:

```text
README.md / README-ko.md
CONTRIBUTING.md / CONTRIBUTING-ko.md
SECURITY.md / SECURITY-ko.md
CODE_OF_CONDUCT.md / CODE_OF_CONDUCT-ko.md
CHANGELOG.md / CHANGELOG-ko.md
docs/architecture.md / docs/architecture-ko.md
docs/development.md / docs/development-ko.md
docs/change-management.md
```

For projects seeking external adoption, the minimum user journey should additionally be visible from README:

```text
Prerequisites
Quick Start
Verify the installation / First success
Known limitations / Compatibility
Troubleshooting
Where to ask for help or report a problem
How to contribute
```

These may be README sections or links to existing detailed documents. Do not create duplicate documents solely to satisfy the structure.

Add when applicable:

```text
RELEASING.md / RELEASING-ko.md
VERSIONS.md / VERSIONS-ko.md
docs/supply-chain.md / docs/supply-chain-ko.md
NOTICE / THIRD-PARTY-LICENSES.md
docs/common/
docs/<deployment-target>/
```

Supply-chain and change-management standards are canonical portfolio guidance; repository-specific documents should link to them rather than define conflicting policies.

## Documentation freshness

Documentation freshness is part of release correctness. Review at least these surfaces when behavior changes:

| Change | Documentation to re-check |
|---|---|
| Install/deploy flow | README Quick Start, prerequisites, verification, troubleshooting |
| Runtime/component version | VERSIONS/compatibility documentation and any README summaries |
| CLI/API/config contract | User guide, examples, migration notes |
| Security/identity behavior | SECURITY, deployment guide, credentials/SSO documentation |
| Release artifact | README install commands, CHANGELOG, release notes |
| Architecture boundary | Architecture document and ADR when durable |
| UI workflow | User guide/screenshots only after the behavior is implemented |

Avoid hard-coded activity counters or version claims in multiple documents when a single authoritative source can be linked instead.

## Adoption evidence

Keep project documentation honest about usage outside the maintainer's own environment.

Recommended states:

- **Candidate** — an external reference was discovered but has not been reviewed.
- **Reported** — an external user/source explicitly reports use.
- **Verified** — the source and project relationship were reviewed.
- **Rejected** — the reference was reviewed and is not valid adoption evidence.

Candidate references must not be presented as adopters. Stars, forks, downloads and repository contributor totals can be useful discovery signals, but are not deployment/adoption evidence by themselves.

## Portfolio documentation review

For a multi-project portfolio, review documentation in two dimensions:

1. **Repository completeness** — README, architecture, contribution, security, release/change documentation and localization exist where applicable.
2. **Adoption usability** — a new user can identify the supported path, install it, verify first success, understand limitations, troubleshoot and report feedback.

A repository can score highly on file presence while still having weak adoption usability. Portfolio audits should therefore report missing evidence and concrete next actions rather than collapse documentation quality into a single synthetic maturity score.

## Filename exceptions

The `-ko.md` convention does **not** require renaming third-party, vendored, generated, or upstream-contract documentation. Preserve upstream names when changing them would make updates harder or break the upstream distribution contract.

Existing project-owned files using legacy forms such as `README_ko.md` should be migrated when touched as part of a normal documentation change, with links updated in the same change. Do not perform a high-risk mass rename only to improve a documentation score.

For example, a project may keep a vendored chart's upstream `README.md` even when project-owned documentation uses the OpenForge bilingual naming convention.