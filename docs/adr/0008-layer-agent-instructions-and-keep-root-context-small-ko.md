# ADR-0008: Agent instruction을 계층화하고 root context를 작게 유지

[English](0008-layer-agent-instructions-and-keep-root-context-small.md) | 한국어

- Status: Accepted
- Date: 2026-08-27

## Context

항상 로드되는 Agent Instruction은 생성 코드 품질을 높일 수 있지만 지나치게 큰 파일은 중요한 Architecture Constraint와 일반 Coding Advice, 과거 기록, Model Routing, 이미 Tool이 강제하는 규칙을 섞어 Context Dilution을 일으킬 수 있습니다.

## Decision

다음 계층을 사용합니다.

```text
AGENTS.md -> 짧은 실행 계약
CODING_STANDARDS.md -> 상세 Coding/Review 지침
CONTRIBUTING / DESIGN / Architecture -> Project Context
CLAUDE / GEMINI / Tool-specific -> Tool Behavior 및 중요한 Gotcha
formatter / linter / tests / CI -> deterministic enforcement
```

Generic Template으로 기존 Project-specific Gotcha를 덮어쓰지 않습니다.

## Alternatives Considered

- 모든 규칙을 root AGENTS.md에 배치
- 매 Session마다 Codebase에서 AGENTS 자동 생성
- AI Tool마다 전체 규칙 복사본 유지
- Repository Agent Instruction을 사용하지 않음

## Rationale

Root File의 Prompt Budget은 Code만으로 추론하거나 Tool로 강제하기 어려운 Engineering Judgment에 사용해야 합니다. 상세 정보는 필요할 때 연결 문서에서 불러올 수 있습니다.

## Consequences

- Root Instruction의 크기와 Signal을 주기적으로 검토합니다.
- Lint 가능한 규칙은 deterministic tooling으로 이동합니다.
- 기존 CLAUDE.md 등에 실제 운영 Gotcha가 있다면 유지할 수 있습니다.
- 큰 Legacy Instruction은 정보를 삭제하지 않고 Playbook/History로 분리합니다.
