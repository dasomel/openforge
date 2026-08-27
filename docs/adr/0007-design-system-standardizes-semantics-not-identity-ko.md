# ADR-0007: Design System은 의미를 표준화하고 Product Identity는 보존

[English](0007-design-system-standardizes-semantics-not-identity.md) | 한국어

- Status: Accepted
- Date: 2026-08-27

## Context

OSS Portfolio에는 Platform Portal, Desktop Operator, Data Control Plane, Admin Console, Operations Dashboard, Developer Tool 등 서로 다른 UI가 있습니다. 하나의 Visual Theme을 강제하면 운영 문맥의 차이를 무시하게 되고 완전히 독립적으로 만들면 Accessibility, State, Token, Interaction 의사결정이 중복됩니다.

## Decision

Semantic Color, State Meaning, Accessibility, Focus, Core Interaction Intent, Foundation Token과 재사용 Pattern을 표준화합니다. Accent, Density, Navigation Composition, Data Visualization, Platform-native Convention은 프로젝트 특성에 따라 제한적으로 차별화합니다.

프로젝트는 `DESIGN.md`에 Archetype과 의도적인 Deviation을 기록합니다.

## Alternatives Considered

- 모든 OSS에 하나의 Visual Design 강제
- 각 Repository가 완전히 독립적인 Design System 사용
- Color Palette만 공유

## Rationale

Cross-project Consistency는 의미와 사용성에서 가장 큰 가치가 있습니다. Product Identity와 Operating Density는 Context에 따라 달라져야 합니다.

## Consequences

- Framework가 달라도 Shared Semantic을 구현할 수 있습니다.
- Design Review는 Pixel Identity보다 Intent/Accessibility를 먼저 봅니다.
- Project-specific Deviation은 가능하지만 명시적으로 추적합니다.
