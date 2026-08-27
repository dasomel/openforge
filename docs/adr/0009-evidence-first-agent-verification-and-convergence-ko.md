# ADR-0009: Agent 작업에 evidence-first verification과 convergence 적용

[English](0009-evidence-first-agent-verification-and-convergence.md) | 한국어

- Status: Accepted
- Date: 2026-08-27

## Context

Coding Agent는 실제 Runtime Path를 증명하지 않은 채 그럴듯한 Patch와 완료 보고를 만들 수 있으며 작업이 더 이상 수렴하지 않는데도 Patch 생성을 반복할 수 있습니다.

## Decision

Bug Fix는 가능하면 Reproduction부터 시작합니다: failing regression test 또는 executable evidence → smallest coherent fix → 동일 Evidence의 성공 → 관련 Regression Verification 순서입니다.

완료 보고는 Evidence Class를 구분하며 실질적인 작업은 다음 A/B/C 중 하나로 수렴해야 합니다.

- **A — Complete:** 의도한 기능이 동작하고 적절한 검증을 통과
- **B — Meaningful progress:** 하나의 검증된 Blocker를 제거하고 다음 Blocker를 Evidence와 함께 격리
- **C — Stop:** 추가 작업이 부당한 Scope Expansion, Fragile Patch, Unsupported Assumption 또는 허용할 수 없는 Risk를 요구

## Alternatives Considered

- Patch를 먼저 만들고 Test를 나중에 추가
- Unit Test 성공을 모든 Runtime Property의 증거로 간주
- Agent가 성공했다고 할 때까지 반복 수정

## Rationale

Evidence는 Hallucination 범위를 줄이고 Partial Progress도 재사용 가능하게 만듭니다. Convergence Model은 단순 활동을 Engineering Progress로 오인하는 것을 막습니다.

## Consequences

- Cluster/Device/Filesystem/Browser 등은 실제 Runtime Evidence가 필요할 수 있습니다.
- Mock/Stub 결과를 상위 Runtime 동작의 증명으로 표현하지 않습니다.
- 취약한 Workaround를 누적하는 대신 Evidence를 가지고 중단할 수 있습니다.
