# ADR-0004: Treat AI instructions and external plugins as untrusted execution inputs

- Status: Accepted
- Date: 2026-08-27
- Retrospective: captures existing AI and plugin supply-chain standards

## Context

AI agents can execute repository-local instructions, shell commands, generated code, plugins, skills, and external automation. These inputs can alter code, CI, credentials, artifacts, or release behavior and therefore cross meaningful trust boundaries.

## Decision

Treat repository-local AI instructions and external plugins/skills as potentially untrusted execution inputs. External executable extensions require identity, integrity, provenance, permission, and behavioral review appropriate to their risk before they are trusted.

## Alternatives considered

- Treat AI instructions as documentation only.
- Trust plugins based on popularity or source URL.
- Rely solely on post-execution code review.

## Rationale

The relevant risk is executable influence, not file extension or branding. Pre-execution controls reduce the chance that malicious or compromised instructions become trusted build/development behavior.

## Consequences

- AI-assisted development is part of the security model.
- Plugin/skill intake should be explicit and auditable.
- Repository instructions should avoid requesting broad permissions without justification.

## Affected standards

- `docs/ai-engineering-security.md`
- `docs/plugin-supply-chain.md`
- `docs/developer-environment-security.md`
- `docs/supply-chain.md`
