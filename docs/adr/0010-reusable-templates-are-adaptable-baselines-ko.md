# ADR-0010: Reusable Template은 adaptable baseline으로 제공

[English](0010-reusable-templates-are-adaptable-baselines.md) | 한국어

- Status: Accepted
- Date: 2026-08-27

## Context

OpenForge는 Workflow, Policy, Kubernetes Resource, GitOps Pattern, Design Template 등 재사용 가능한 구현을 제공합니다. 그러나 Version, Permission, Domain, Identity, Threat Model, Platform, 운영 요구는 프로젝트마다 다릅니다.

## Decision

Template은 보수적인 Implementation Starting Point이며 Universal Drop-in Configuration이 아닙니다. 프로젝트는 Version, Permission, Path, Command, Domain, Image, Identity, Platform Convention 및 Ecosystem-specific Control을 자신의 Context에 맞게 조정해야 합니다.

## Alternatives Considered

- 모든 Template을 Universal Drop-in으로 보장
- 재사용 구현 없이 Documentation만 제공
- Reference Project마다 별도의 Template Set Fork

## Rationale

Reusable Implementation은 Bootstrap을 빠르게 하지만 Context-specific Infrastructure를 보편적으로 옳다고 가정하면 Unsafe Default와 Hidden Coupling이 생깁니다.

## Consequences

- Template Consumer는 Project-specific Review 책임을 가집니다.
- OpenForge는 Assumption과 Placeholder를 명확히 문서화합니다.
- Reference Project는 Template에 경험을 제공하지만 rigid dependency가 되지 않습니다.
