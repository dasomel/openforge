# ADR-0012: 의도적인 예외는 문서화하고 review/expiry 적용

[English](0012-document-and-time-bound-intentional-exceptions.md) | 한국어

- Status: Accepted
- Date: 2026-08-27

## Context

재사용 가능한 Standard가 모든 Repository, Platform, Offline Environment, Maintainer Constraint, Migration 상황을 미리 예측할 수는 없습니다. 그러나 영구적이고 조용한 Exception이 쌓이면 공통 Standard 자체의 의미가 사라집니다.

## Decision

정당한 이유가 있으면 의도적인 Deviation을 허용하되 Scope, Rationale, Risk/Impact, 필요한 경우 Owner, Review 또는 Expiry Condition을 기록합니다. Exception이 문서화되지 않은 영구 기본값이 되지 않도록 다시 검토합니다.

이 원칙은 Security뿐 아니라 Design System Deviation, Compatibility Constraint, CI Fallback, Project-specific Engineering Rule에도 적용할 수 있습니다.

## Alternatives Considered

- Standard에 어떠한 Exception도 허용하지 않음
- Repository-local Deviation을 문서 없이 허용
- 모든 Deviation에 중앙 승인 절차 요구

## Rationale

Explicit Exception은 현실적인 유연성을 유지하면서 Standard로 돌아갈 경로를 제공합니다. Exception을 완전히 금지하면 숨겨진 Workaround를 만들고 무제한 허용하면 Consistency를 잃습니다.

## Consequences

- Standard는 Universal Configuration이 아니라 Default 역할을 합니다.
- Maintainer는 누적된 Divergence를 확인할 수 있습니다.
- 만료된 Exception은 제거, Evidence를 통한 갱신 또는 재설계를 검토합니다.
