# ADR-0006: Security와 Supply Chain Control을 lifecycle에 내재화

[English](0006-build-security-into-release-supply-chain.md) | 한국어

- Status: Accepted
- Date: 2026-08-27

## Context

개발 마지막 단계에서만 Security Check를 수행하면 Dependency, CI Permission, Build Provenance, Artifact Identity, Secret Exposure, Release Process의 위험을 늦게 발견하게 됩니다.

## Decision

Security와 Supply Chain Control을 최종 Release Checklist로만 취급하지 않고 Development, CI, Build, Packaging, Release, Incident/Maintenance Workflow에 포함합니다.

## Alternatives Considered

- Release 직전에만 Vulnerability Scan 수행
- Hosting Platform 기본 설정에 의존
- 소규모 OSS에서는 Supply Chain Security를 선택 사항으로 취급

## Rationale

Risk가 유입되는 지점에서 Control을 적용하는 것이 더 효과적이며 Lifecycle에 통합된 Evidence는 Release와 Incident Response에서도 재사용할 수 있습니다.

## Consequences

- CI Permission, Dependency, SBOM/Provenance, Artifact Identity, Release Verification, Secret이 핵심 Engineering 관심사가 됩니다.
- 반복 Maintainer 부담을 줄일 수 있는 경우 Automation을 우선합니다.
- Security Gate를 조용히 비활성화하지 않고 Exception을 명시적으로 관리합니다.
