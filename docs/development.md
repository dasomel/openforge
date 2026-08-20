# Development Standard

Projects should keep implementation changes small, testable and reviewable.

## Architecture

- Define boundaries before implementation.
- Record important decisions as ADRs.
- Prefer stable domain models over UI-specific APIs.
- Avoid unnecessary coupling to external components.
- Keep architecture information reproducible from source code and configuration.

## Code quality

- Apply language-specific formatters consistently in local development and CI.
- Prefer `gofumpt` over direct `gofmt` usage for Go projects.
- Use static analysis appropriate to the language.
- Keep formatting, linting, testing and building reproducible in CI.
- Treat generated code and generated analysis artifacts as derived outputs.
- Prefer deterministic command entry points through a Makefile or equivalent when the project benefits from one.

See [Engineering Tooling Standard](tooling.md) for preferred tools and examples.

## Code intelligence

For medium and large repositories, use code graph or code intelligence tooling when it improves architecture understanding, review and change-impact analysis. Examples include `codegraph`, `graphify`, or an equivalent tool that supports the project stack.

Generated graphs must be reproducible and must not replace source code or ADRs as the authoritative architecture record.

## AI-assisted development

When AI-assisted development is used, version concise repository guidance such as `AGENTS.md`, `CLAUDE.md`, or an equivalent file. It should define important commands, architecture boundaries, testing rules, safety constraints and documentation conventions.

AI-generated changes remain subject to the same tests, review, security and license requirements as human-authored changes.

## Testing

Use the lowest appropriate test level and add end-to-end tests for critical user journeys.

```text
Unit → Component → Integration → E2E
```

For infrastructure projects, add reproducible verification or regression checks for known integration failures.

## Operational knowledge

When an operational failure or unexpected integration behavior teaches a reusable lesson:

```text
Incident → Discriminator → Fix → Regression test → Documentation
```

Keep the record concise, dated where useful, and actionable.

## Configuration

- Keep environment-specific configuration explicit.
- Commit safe examples such as `.env.example`, not secrets.
- Fail clearly when required configuration is missing.

## Dependencies

- Pin or constrain critical dependencies.
- Review dependency updates.
- Remove unused dependencies.
- Check compatibility when one dependency is represented in multiple manifests or packaging systems.

## Localization

All user-facing strings must use translation keys when the application supports multiple languages.
APIs and domain objects must remain locale-neutral.
