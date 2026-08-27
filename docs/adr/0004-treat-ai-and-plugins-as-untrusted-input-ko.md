# ADR-0004: AI instruction과 외부 Plugin을 untrusted execution input으로 취급

[English](0004-treat-ai-and-plugins-as-untrusted-input.md) | 한국어

- Status: Accepted
- Date: 2026-08-27

## Context

AI Agent는 Repository-local instruction, Shell Command, 생성 코드, Plugin, Skill 및 외부 Automation을 실행할 수 있습니다. 이러한 입력은 Code, CI, Credential, Artifact, Release 동작에 영향을 줄 수 있으므로 중요한 Trust Boundary를 통과합니다.

## Decision

Repository-local AI instruction과 외부 Plugin/Skill을 잠재적인 untrusted execution input으로 취급합니다. 외부 실행 확장은 신뢰하기 전에 Risk에 맞는 Identity, Integrity, Provenance, Permission 및 Behavioral Review를 수행합니다.

## Alternatives Considered

- AI instruction을 일반 문서로만 취급
- Popularity 또는 Source URL만으로 Plugin 신뢰
- 실행 후 Code Review에만 의존

## Rationale

Risk를 결정하는 것은 파일 확장자나 제품 이름이 아니라 실행에 영향을 미치는 능력입니다. Pre-execution Control은 악성 또는 침해된 Instruction이 신뢰된 개발/빌드 동작이 되는 위험을 줄입니다.

## Consequences

- AI-assisted development도 Security Model의 일부입니다.
- Plugin/Skill intake는 명시적이고 감사 가능해야 합니다.
- Repository instruction에서 근거 없이 광범위한 권한을 요구하지 않습니다.
