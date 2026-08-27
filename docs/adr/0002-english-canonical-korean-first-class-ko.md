# ADR-0002: English canonical + Korean first-class translation

[English](0002-english-canonical-korean-first-class.md) | 한국어

- Status: Accepted
- Date: 2026-08-27
- Retrospective: 기존 OpenForge 규칙을 소급 기록

## Context

OpenForge는 한국어 사용자와 Maintainer를 지원하면서도 특정 언어권에 한정되지 않는 재사용 가능한 OSS 표준을 목표로 합니다. 두 언어를 독립적인 Source of Truth로 운영하면 내용이 서로 달라질 수 있습니다.

## Decision

English를 canonical project language로 사용하고 Korean을 first-class translation으로 유지합니다. 한국어 문서가 제공되는 사용자 대상 Markdown은 `<name>.md` / `<name>-ko.md` 규칙을 사용합니다.

## Alternatives Considered

- Korean-only
- English-only
- 영문/한글을 서로 독립적인 authoritative document로 운영
- 유지관리되는 한국어 파일 없이 자동 번역만 제공

## Rationale

Canonical language는 명확한 Source of Truth를 제공합니다. 동시에 Korean first-class translation을 유지하면 글로벌 재사용성과 주요 Contributor/Community의 접근성을 함께 확보할 수 있습니다.

## Consequences

- Normative change는 English에 먼저 또는 한국어와 함께 반영합니다.
- Translation drift는 Documentation Debt로 관리합니다.
- 번역 시 표현은 자연스럽게 조정할 수 있지만 normative meaning을 변경해서는 안 됩니다.
