# ADR-0008: Layer agent instructions and keep root context small

- Status: Accepted
- Date: 2026-08-27
- Related adoption record: `docs/agent-engineering-adoption-2026-08.md`

## Context

Always-loaded agent instruction files can improve AI-generated code, but large files mix high-value architecture constraints with generic coding advice, historical notes, model-routing guidance, and rules already enforced by tooling. Long prompt context can dilute the instructions that matter most.

## Decision

Use a layered model:

```text
AGENTS.md
  -> concise execution contract
CODING_STANDARDS.md
  -> detailed coding/review guidance
CONTRIBUTING / DESIGN / architecture docs
  -> project context
CLAUDE / GEMINI / tool-specific files
  -> tool-specific behavior and high-value gotchas
formatter / linter / tests / CI
  -> deterministic enforcement
```

Preserve valuable project-specific gotchas rather than replacing them with a generic template.

## Alternatives considered

- Put all rules in root `AGENTS.md`.
- Generate AGENTS automatically from the codebase for every session.
- Keep separate full copies for every AI tool.
- Avoid repository agent instructions entirely.

## Rationale

The root file should spend prompt budget on judgment that cannot be inferred or enforced mechanically. Linked detail remains available when a task needs it.

## Consequences

- Root instructions require periodic size/signal review.
- Lintable rules should migrate toward deterministic tooling.
- Existing high-value `CLAUDE.md` or similar project files may remain authoritative for project gotchas.
- Large legacy instruction files should be split without deleting useful operational history.

## Affected standards

- `docs/agent-engineering.md`
- `templates/AGENTS.md`
- `templates/CODING_STANDARDS.md`
- active OSS agent-instruction files
