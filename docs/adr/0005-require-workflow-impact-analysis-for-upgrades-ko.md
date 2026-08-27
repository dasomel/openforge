# ADR-0005: Upgrade 시 workflow 전체 영향 분석

[English](0005-require-workflow-impact-analysis-for-upgrades.md) | 한국어

- Status: Accepted
- Date: 2026-08-27

## Context

개별 Dependency나 Runtime이 직접적으로 호환되더라도 Packaging, CI, Deployment, Plugin, Generated Artifact, Platform Support 또는 운영 Workflow에서 문제가 발생할 수 있습니다.

## Decision

Direct Dependency Compatibility만으로 최신 버전을 채택하지 않습니다. Dependency, Runtime, Toolchain, Platform, Build 변경이 영향을 주는 End-to-End Workflow를 분석합니다.

## Alternatives Considered

- 항상 Latest Release 추적
- Dependency Resolver가 성공하면 Upgrade
- Security Issue가 없는 한 Version Freeze

## Rationale

Compatibility는 개별 Package가 아니라 System의 속성입니다. OpenForge는 최신성 자체보다 Evidence 기반 Upgrade를 우선하되 영구적인 정체도 피합니다.

## Consequences

- Upgrade Review에서 CI, Packaging, Runtime, Plugin, Deployment, Rollback Evidence가 필요할 수 있습니다.
- Latest가 자동으로 Best가 아니며 Old가 자동으로 Safe도 아닙니다.
- Evidence가 부족하면 Upgrade를 보류할 수 있습니다.
