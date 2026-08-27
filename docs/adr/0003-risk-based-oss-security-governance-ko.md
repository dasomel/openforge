# ADR-0003: OSS Security/Governance를 Risk 기반으로 적용

[English](0003-risk-based-oss-security-governance.md) | 한국어

- Status: Accepted
- Date: 2026-08-27
- Retrospective: 기존 OpenForge Security/Governance 방향을 소급 기록

## Context

OpenForge Reference Project에는 소규모 팀이나 단독 Maintainer가 운영하는 OSS도 많습니다. 대기업의 통제 절차를 그대로 복제하면 유지가 어렵지만 Maintainer가 적다는 이유로 Security Control을 제거하면 불필요한 위험이 생깁니다.

## Decision

Maintainer 수가 아니라 Risk, Trust Boundary, Release Impact, Privilege, Automation 가능성을 기준으로 Security/Governance 수준을 결정합니다. 가능한 경우 자동화를 우선하고 전체 Control 적용이 과도한 경우 문서화된 Exception을 사용합니다.

## Alternatives Considered

- 모든 OSS에 Enterprise Governance를 그대로 적용
- 단독 Maintainer 프로젝트는 Security Control 완화
- Security/Governance를 전적으로 각 프로젝트에 위임

## Rationale

Risk 기반 방식은 프로젝트 규모를 Security Requirement의 대리 지표로 사용하지 않으면서 실용적인 유지관리와 필요한 통제를 함께 확보합니다.

## Consequences

- 소규모 OSS에서도 Release, Identity, Secret, Supply Chain, Permission 변경은 강한 Control이 필요할 수 있습니다.
- 낮은 Risk의 절차 부담은 최소화합니다.
- Exception은 조용한 영구 기본값이 아니라 근거와 Review/Expiry를 가져야 합니다.
