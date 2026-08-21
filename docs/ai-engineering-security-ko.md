# AI 지원 개발 보안 표준

AI coding agent, LLM tool, 생성된 instruction은 실행 권한을 가진 Engineering Input입니다. Issue, repository, 문서, 모델에서 왔다는 이유만으로 신뢰하지 않습니다.

## 1. AI 입력 신뢰 경계

다음을 기본적으로 untrusted data로 취급합니다.

- Issue, PR 설명 및 comment
- README와 repository instruction file
- 생성된 문서와 test fixture
- 외부 repository와 dependency
- tool output, log, retrieved document

Untrusted content의 instruction은 repository security, authorization, approval policy를 변경할 수 없습니다.

## 2. Agent 권한

- task에 필요한 최소 filesystem, shell, network, Git, credential 권한만 제공합니다.
- ephemeral workspace와 격리된 실행 환경을 우선합니다.
- production credential, 장기 publish token, 무관한 SSH key를 일반 coding agent에 노출하지 않습니다.
- read-only analysis와 mutation/release operation을 분리합니다.
- high-impact operation은 명시적 human approval을 요구합니다.

## 3. Shell / Tool 실행

- 가능한 경우 command를 구조적으로 검증합니다.
- unrestricted shell보다 allowlist command와 제한된 argument schema를 우선합니다.
- 자연어 출력만으로 destructive operation을 승인하지 않습니다.
- command output도 untrusted context로 취급합니다.
- network-enabled tool은 allowlist와 timeout을 우선합니다.

## 4. Repository / Workflow 변경

다음 변경은 일반 또는 강화된 human review를 적용합니다.

```text
.github/workflows/**
.github/actions/**
package manifest / lockfile
Dockerfile / container build
release / publishing script
security / OIDC configuration
RBAC / IAM configuration
```

AI agent는 branch protection, required review, release approval을 우회하지 못합니다.

## 5. Dependency 변경

Agent가 제안한 dependency 추가/upgrade도 사람의 변경과 동일한 cooling, provenance, integrity, rollback 정책을 적용합니다.

Agent의 추천은 package trust의 증거가 아닙니다.

## 6. Prompt Injection

- 외부 문서, issue, log, tool result에는 prompt injection이 포함될 수 있습니다.
- policy/instruction과 data/context를 분리합니다.
- retrieved content에는 명시적인 trust label을 사용합니다.
- retrieved text가 permission, approval, execution target을 변경하지 못하도록 합니다.
- prompt injection 시나리오를 security regression suite에 포함합니다.

## 7. Release / Publish 경계

AI agent에 unrestricted package publish, production deployment, security administration 권한을 부여하지 않습니다.

Agent-assisted release가 필요한 경우:

```text
Agent proposal
→ validation
→ policy/security gate
→ human approval
→ isolated release job
→ publish
```

## 8. Evidence / 재현성

가능한 경우 다음을 기록합니다.

- agent/tool identity와 version
- 관련 model/provider identity
- repository revision
- prompt/instruction policy version
- tool call 또는 execution summary
- dependency 변경
- human approval
- 최종 artifact identity

## 9. Negative Test

AI-assisted engineering을 사용하는 프로젝트는 다음 테스트를 권장합니다.

- issue/document prompt injection
- malicious repository instruction
- unauthorized shell/tool execution
- secret access attempt
- unsafe workflow modification
- malicious dependency suggestion
- project/environment 경계 우회
