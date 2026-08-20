# Documentation Standard

OpenForge standardizes user-facing documentation as separate English and Korean files.

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
- Put user-facing documentation in Markdown.
- Keep README focused on purpose, features, quick start, architecture, status, documentation and license.
- Put detailed operational content under `docs/`.
- Record architecture decisions as ADRs.
- Do not put secrets, private endpoints or credentials in documentation.

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
```
