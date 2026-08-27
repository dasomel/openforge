# ADR-0011: CI resilience가 무분별한 Security bypass를 유도하지 않게 설계

[English](0011-ci-resilience-must-not-encourage-security-bypass.md) | 한국어

- Status: Accepted
- Date: 2026-08-27

## Context

외부 Scanner, Registry, Runner, Package Service, CI Integration은 코드와 무관하게 장애가 발생할 수 있습니다. 하나의 외부 서비스에 Hard Dependency를 가지면 유지보수가 중단될 수 있지만 장애가 발생할 때마다 Security Gate를 우회하면 Availability 문제가 Security Risk로 전환됩니다.

## Decision

외부 장애가 발생해도 Maintainer가 Security/Quality Control을 무작정 비활성화하지 않도록 CI Resilience와 Fallback을 설계합니다. Code Failure, Policy Failure, Infrastructure/Service Failure를 구분하고 Risk에 맞는 대체 Evidence 또는 명시적인 Exception Path를 사용합니다.

## Alternatives Considered

- 모든 외부 Service Failure에서 무조건 Fail Closed
- CI 장애 시 Maintainer가 자유롭게 Gate 우회
- Security Check를 Informational로만 운영

## Rationale

Availability와 Security는 모두 Engineering Requirement입니다. Degraded State를 명확히 표시하면서 가능한 Assurance를 유지해야 합니다.

## Consequences

- CI는 Gate가 실패한 이유를 구분해 보여줘야 합니다.
- Risk에 따라 Alternate Check, Cached Evidence, Rerun 또는 문서화된 Exception을 사용할 수 있습니다.
- 동등한 Assurance를 확보할 수 없는 High-risk Release는 장애 해소까지 기다릴 수 있습니다.
