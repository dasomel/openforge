# Agent Skills 표준

OpenForge는 Agent Skill을 범용 Prompt 모음이 아니라 **버전 관리되는 Engineering Workflow**로 봅니다. Skill은 반복 탐색을 줄이고, 모델이 안전하게 추론하기 어려운 프로젝트/도메인 절차를 저장하며, 필요할 때만 로드할 수 있을 만큼 작게 유지합니다.

이 표준은 Agent Skills의 `SKILL.md` 형식을 따르며 `docs/agent-engineering-ko.md`를 보완합니다.

## 지침 계층

```text
AGENTS.md
  -> 짧고 Agent-neutral한 저장소 실행 계약

CLAUDE.md / Tool별 Rule
  -> 해당 Runtime 전용 Adapter
  -> 일반 규칙을 복사하지 말고 AGENTS.md를 import/reference

SKILL.md
  -> 필요할 때 로드하는 반복 작업/도메인 Workflow

scripts / Makefile / tests / policy / CI
  -> 결정적 실행 및 강제
```

검증 가능한 규칙을 Prompt로 옮기지 않습니다. 동일한 Engineering Rule을 AGENTS.md, CLAUDE.md, 여러 Skill에 중복하지 않습니다.

## Skill Scope

| Scope | Owner | 용도 |
|---|---|---|
| `core` | OpenForge | 저장소와 무관한 Portfolio 공통 Workflow |
| `domain` | OpenForge 또는 Domain Owner | Kubernetes Platform, Go CLI, Next.js Portal, Packer/Vagrant, Identity 등 기술군 공통 Workflow |
| `project` | 각 Project Repository | 프로젝트 고유 Source of Truth, 운영 절차, 경계, 검증 |

프로젝트 Workflow는 최소 2개 이상의 저장소가 거의 동일한 절차를 공유할 때만 Domain/Core로 승격합니다. 공통화할 수 없는 내용을 복사하지 않습니다.

## Canonical Source와 Adapter

각 Skill에는 편집 가능한 원본이 **하나만** 있어야 합니다.

- Project Skill은 해당 Project Repository가 소유합니다.
- Core/Domain Template 및 Portfolio Guidance는 OpenForge가 소유합니다.
- `.claude/skills/`, `.agents/skills/`, Plugin 등 Runtime 전용 위치는 Adapter/Discovery 위치로 사용할 수 있습니다.
- Runtime이 복사나 Link를 요구하면 Canonical Source에서 생성합니다. 양쪽을 직접 편집하지 않습니다.
- `metadata`에 Scope와 Owner를 기록합니다.
- `/Users/name/...`, `/home/name/...` 같은 개인 절대경로에 의존하지 않습니다.

Migration 중에는 기존 Runtime 전용 경로를 Canonical Source로 유지할 수 있습니다. 핵심은 단일 원본과 Mirror Drift 방지입니다.

## `SKILL.md` 형식

모든 Skill Directory는 YAML Frontmatter가 있는 `SKILL.md`를 포함합니다.

```yaml
---
name: project-task
description: 프로젝트 고유 작업을 안전하게 수행합니다. ... 작업일 때 사용합니다.
license: Apache-2.0
compatibility: Repository checkout과 문서화된 Project Toolchain이 필요합니다.
metadata:
  openforge-scope: project
  openforge-owner: owner/repository
  openforge-maturity: draft
  openforge-version: "1"
---
```

Agent Skills 규격상 `name`과 `description`은 필수입니다. OpenForge Custom Metadata 값은 Portability를 위해 String으로 유지합니다. 새 Skill 또는 Material Change가 발생한 Skill은 `draft`에서 시작하며, 리뷰를 받았다는 이유만으로 `verified`를 부여하지 않습니다.

### Naming

- lowercase kebab-case를 사용합니다.
- Project Skill은 전역 설치 시 충돌을 막기 위해 기본적으로 `<project>-<task>` 형식을 사용합니다.
- Project Scope에서 `verification`, `build`, `deploy`, `debug` 같은 지나치게 일반적인 이름은 피합니다.
- Domain/Core Skill은 `kubernetes-platform-verification`처럼 Domain Prefix를 사용할 수 있습니다.

### Description

Description은 Routing Metadata입니다. 무엇을 하는지와 **언제 사용해야 하는지**를 모두 씁니다. `fix`, `version`, `install` 같은 광범위 Keyword 나열보다 실제 Path, Task Class, System Boundary를 사용합니다.

## 권장 본문 구조

```text
# Skill title
## Use When
## Do Not Use When
## Inputs
## Workflow
## Verification
## Stop / Escalate When
## References
```

결정적 절차는 `scripts/`, 긴 Project Knowledge는 `references/`, Template/Data는 `assets/`로 이동합니다. Reference Chain은 얕게 유지합니다.

OpenForge 권장 크기는 보통 250줄 미만이며 Agent Skills 호환 상한은 500줄 미만입니다.

## Skill에 넣을 것과 넣지 않을 것

좋은 Skill은 “이 프로젝트에서 X를 어떻게 하는가”로 표현할 수 있습니다. 예를 들면 Narwhal Component 추가, NFS Project Quota 검증, Beluga Integration Contract 변경, Kube Ready Box Build Matrix 검증입니다.

다음 내용은 다른 계층이 소유합니다.

- 일반 Model Advice -> 제거하거나 User/Runtime 설정
- 저장소 전체 Non-negotiable Boundary -> `AGENTS.md`
- Claude 전용 Team Lane/Slash Command/Hook/Model Routing -> `CLAUDE.md` / `.claude/rules/`
- Architecture와 안정적인 System Fact -> Architecture/Design 문서
- 과거 Incident -> Lessons/Mistakes Log
- Formatter/Linter/Test로 검사 가능한 규칙 -> 실행 도구/CI

## CLAUDE.md Adapter 표준

`CLAUDE.md`는 두 번째 Repository Constitution이 아니라 Adapter입니다.

건강한 CLAUDE.md는 보통 다음만 포함합니다.

1. `AGENTS.md` import/reference
2. Claude 전용 Harness/Routing/Command 동작
3. Workflow를 재작성하지 않고 Project Skill로 Routing
4. 개인 Machine 절대경로나 Maintainer의 Global `~/.claude/CLAUDE.md`에 필수 의존하지 않음
5. 일반 Engineering Rule은 AGENTS.md 또는 연결된 표준에 둠

기존의 큰 CLAUDE.md는 가치 있는 Project Knowledge를 지우지 않고 분리합니다. Stable Fact는 Docs, 반복 Workflow는 Skill, Incident는 Lessons Log, 결정적 Rule은 Script/CI로 이동합니다.

## Lifecycle

`metadata.openforge-maturity`는 다음 중 하나를 사용합니다.

- `draft`: Clean Context 재실행과 Evidence Artifact가 아직 완료되지 않음
- `verified`: 명시적 Machine-readable Evidence로 Fresh Session 재실행 성공
- `stable`: Verified 이후 반복 사용 성공, Trigger Ambiguity 없음
- `deprecated`: Migration을 위해 남김. Description에서 Replacement를 안내

Material Change 시 `metadata.openforge-version`을 증가시킵니다. Skill Version이 바뀌면 Verification Evidence의 `skillVersion`도 새 Version과 일치하기 전까지 기존 Verified Evidence는 유효하지 않습니다.

## 검증

Markdown이 그럴듯하거나 관련 없는 Repository CI가 Green이라는 이유로 Skill을 Verified로 보지 않습니다.

`verified`로 승격하기 전에:

1. 가능한 경우 `skills-ref validate`로 형식 검증
2. 생성 당시 Conversation Context가 없는 Fresh Session에서 재실행
3. 최소 1개의 과거 Failure/Edge Case 실행
4. 변경되어야 할 것과 변경되면 안 되는 것을 모두 확인
5. Repository가 소유한 결정적 검증 명령을 실행하고 결과 기록
6. Static/Unit/Stub Evidence와 실제 Cluster/Filesystem/Network/Browser/Device/Service Evidence를 구분
7. Portable하다고 주장하는 모든 Agent Runtime에서 확인
8. 아래 Machine-readable Verification Artifact 저장

Unit/Stub 성공을 실제 Cluster, Filesystem, Network, Identity, Cloud Runtime 검증처럼 표현하지 않습니다.

### Verification Evidence Artifact

`verified` 또는 `stable` Skill은 반드시 다음 파일을 가져야 합니다.

```text
.agents/skill-evals/<skill-name>.json
```

`templates/agent-skill-verification.json`을 시작점으로 사용합니다. 이 파일은 Transcript 전체를 복사하는 곳이 아니라 **Evidence Metadata**입니다. Project-local Trace, CI Run, Report, Test, Runtime Artifact를 Reference합니다.

필수 Contract 예시는 다음과 같습니다.

```json
{
  "schemaVersion": "openforge-agent-skill-verification/v1",
  "skill": "project-task",
  "skillVersion": "1",
  "freshSession": true,
  "agentRuntime": "runtime-and-version-or-channel",
  "happyPath": {
    "status": "passed",
    "scenario": "Representative workflow",
    "evidence": ["artifact:path/or-reference"]
  },
  "edgeCase": {
    "status": "passed",
    "scenario": "Known failure/edge regression",
    "evidence": ["artifact:path/or-reference"]
  },
  "deterministicChecks": [
    {"command": "make verify", "status": "passed", "scope": "repository baseline"}
  ],
  "runtimeEvidence": [],
  "unverified": [],
  "verifiedAt": "YYYY-MM-DD"
}
```

`unverified`가 비어 있지 않다고 해서 자동 실패는 아닙니다. 이것은 **검증 Claim의 경계**입니다. Skill이 검증하지 않은 Runtime Property를 성공했다고 주장하지 않는다면, 문서화된 범위에 대해서는 Verified일 수 있습니다.

`templates/scripts/audit-agent-skills.py`는 `openforge-maturity`가 `verified` 또는 `stable`인데 Evidence Artifact가 없거나 형식이 잘못된 경우 Error를 반환합니다. 따라서 Frontmatter만 수정해서 Verified로 보이게 할 수 없습니다.

이 규칙 이전에 존재했던 Skill도 자동 면제하지 않습니다. 기존 Skill도 동일한 Evidence Artifact를 만들기 전에는 `verified`/`stable`을 유지하지 않습니다.

## Security

Skill은 Guidance이며 Authorization Boundary가 아닙니다. `allowed-tools`는 Experimental이므로 Security Control로 간주하지 않습니다. Side Effect Tool은 `docs/agent-execution-security-ko.md`의 Capability, Approval, Sandbox, Evidence Control을 따라야 합니다.

## Review 및 정리

Active Project는 Major Agent/Runtime 변경 시 또는 최소 분기별로 Skill Inventory를 검토합니다.

다음 경우 Skill을 제거하거나 합칩니다.

- 더 이상 호출되지 않음
- Project Knowledge 없이도 현재 Model/Tool이 안정적으로 처리함
- Workflow가 Script/CI로 완전히 강제됨
- 다른 Skill과 Trigger/Body가 사실상 동일함
- 현재 Repository와 충돌하는 낡은 설명이 남음

Coverage를 늘리기 위해 Skill 개수 자체를 늘리지 않습니다. 적고 정확한 Skill을 우선합니다.
