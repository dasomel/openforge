# ADR-0002: Use English as canonical and Korean as a first-class translation

- Status: Accepted
- Date: 2026-08-27
- Retrospective: captures an existing OpenForge convention

## Context

OpenForge is intended to be reusable outside a single Korean-speaking project while also supporting Korean maintainers and users without treating Korean documentation as an afterthought.

Maintaining two independent authoritative versions would create drift and ambiguous source-of-truth behavior.

## Decision

Use English as the canonical project language and Korean as a first-class translation. User-facing Markdown follows `<name>.md` and `<name>-ko.md` where a Korean counterpart is provided.

## Alternatives considered

- Korean-only documentation.
- English-only documentation.
- Two equally authoritative independent documents.
- Automatic translation without maintained Korean files.

## Rationale

A canonical language gives deterministic source-of-truth behavior. Maintaining Korean as a first-class translation preserves accessibility for the primary contributor/community context while keeping the project globally consumable.

## Consequences

- Normative changes should land in English first or together with Korean updates.
- Translation drift should be treated as documentation debt.
- Korean text may adapt wording for clarity but must not silently change normative meaning.

## Affected standards

- `docs/documentation.md`
- `docs/i18n.md`
- repository README/documentation conventions
