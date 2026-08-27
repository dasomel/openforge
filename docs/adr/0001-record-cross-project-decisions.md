# ADR-0001: Record cross-project decisions as ADRs

English | [한국어](0001-record-cross-project-decisions-ko.md)

- Status: Accepted
- Date: 2026-08-27

## Context

OpenForge defines standards and reusable defaults that can affect multiple OSS repositories. Standard documents describe the current rule well, but Git history and final documentation alone do not reliably preserve why a choice was made, what alternatives were rejected, or how a later change should supersede it.

## Decision

Use Architecture Decision Records for durable, cross-project engineering decisions. Keep standards normative and ADRs historical/rationale-oriented.

Material changes create a new ADR rather than rewriting an accepted ADR. The previous ADR is marked Superseded when appropriate.

## Alternatives considered

- Rely only on Git commit history.
- Put rationale only in Issues/PRs.
- Add rationale sections directly to every standard document.
- Record every repository change as an ADR.

## Rationale

Commits and issues are useful implementation history but are harder to discover as the standards corpus grows. Embedding all history into normative standards makes them harder to read. Recording every small change creates administrative noise.

A selective ADR layer preserves high-value reasoning while keeping standards concise.

## Consequences

- Important common decisions become discoverable and reviewable.
- Supersession is explicit.
- Maintainers must decide whether a change crosses the ADR threshold.
- ADRs must link to standards and adoption records to avoid becoming isolated documentation.

## Affected areas

- Change management
- Maintainer governance
- Repository/documentation standards
- Future OpenForge standards and templates
