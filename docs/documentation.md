# Documentation Standard

OpenForge standardizes **project-owned, user-facing** documentation as separate English and Korean files.

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
- Keep README focused on purpose, features, quick start, architecture, status, documentation and license.
- Put detailed operational content under `docs/`.
- Record architecture decisions as ADRs.
- Record important operational failures as lessons/incidents/mistakes and connect them to tests when practical.
- Do not put secrets, private endpoints or credentials in documentation.
- Treat build, runtime, dependency and release contracts as documented engineering interfaces.
- Update relevant documentation when a change modifies those contracts.

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

## Filename exceptions

The `-ko.md` convention does **not** require renaming third-party, vendored, generated, or upstream-contract documentation. Preserve upstream names when changing them would make updates harder or break the upstream distribution contract.

For example, a project may keep a vendored chart's upstream `README.md` even when project-owned documentation uses the OpenForge bilingual naming convention.