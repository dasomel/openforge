# 위험도 기반 Operational Trace 정책

## 목적

Operational Trace는 모든 변경에 강제하는 절차 로그가 아니라 고위험 변경에 선택적으로 요구하는 검증 증거입니다. OpenForge는 저장소별 정책에서 `high`로 분류된 경로가 변경될 때만 trace를 요구합니다.

기존 trace 파일이 저장소에 존재하는 것만으로는 통과하지 않습니다. 고위험 PR은 **같은 PR diff에서 trace를 추가하거나 수정**해야 합니다.

## 정책 계약

정책 스키마:

`openforge-agent-risk-policy/v1`

결과 스키마:

`openforge-agent-risk-result/v1`

정책은 다음을 정의합니다.

- 기본 위험도 `defaultRisk`
- trace가 필요한 위험도 `traceRequiredAt`
- trace 경로 `tracePathPrefix`
- 저장소 경로별 위험도와 이유

현재 위험도는 `low`, `medium`, `high`이며 여러 규칙이 일치하면 가장 높은 위험도가 적용됩니다.

## CI 흐름

```text
PR 변경 파일
  -> 저장소별 risk policy
  -> 최고 위험도 결정
  -> trace 필요 여부
  -> 같은 diff에서 trace 변경 여부
  -> trusted baseline regression gate
  -> 기존 repository CI는 별도 evidence class
```

고위험 변경에 같은 diff의 trace가 없으면 baseline 비교 이전 단계에서 CI가 실패합니다.

## 저장소별 적용

### OpenForge

주요 high-risk 경로:

- `.github/workflows/**`
- `templates/scripts/**`
- `templates/agent-eval/**`
- `.agents/**`

OpenForge는 downstream 소비 저장소가 아니라 재사용 template을 배포하므로 canonical operational trace 위치를 `templates/agent-eval/traces/`로 사용합니다.

### Narwhal

CI/release workflow, air-gap 도구, install/security script, GitOps desired state, version source-of-truth, Agent evidence contract를 high-risk로 분류합니다.

### KubeMetal

CI/release workflow, air-gap tooling, Kubernetes mutation script, MLX runtime script, Tauri native code, Agent evidence contract를 high-risk로 분류합니다.

### nfs-quota-agent

CI/release workflow, controller/command code, privileged quota reconciliation, Helm/RBAC, image build input, compatibility tooling, Agent evidence contract를 high-risk로 분류합니다.

## Evidence class 경계

이 gate는 고위험 변경이 검토 가능한 operational trace를 포함하고 trusted behavior baseline 아래로 회귀하지 않았다는 것만 증명합니다.

Kubernetes runtime, macOS/MLX native runtime, 실제 quota filesystem, integration/release/security 검증 등은 별도의 evidence class입니다.

## 적용 중 발견한 실패

첫 OpenForge 실행은 실패했습니다. 초기 정책이 downstream 경로인 `.agents/evals/traces/`를 기대했지만 OpenForge 자체는 reusable template을 `templates/agent-eval/` 아래에 유지하기 때문입니다.

이를 예외 처리로 우회하지 않고 정책과 저장소 레이아웃의 불일치로 기록했습니다. OpenForge 전용 trace 경로를 `templates/agent-eval/traces/`로 수정하고 실제 risk-gate 구현 trace를 추가한 뒤 CI가 통과했습니다.

즉 실패를 숨이지 않고 `불일치 노출 -> 원인 축소 -> 계약 수정 -> 재검증` 순서로 처리합니다.

## AGENT-005 상태

이번 구현으로 operational evidence 수집은 강화됐지만 아직 portfolio-wide 신규 metric을 만들지는 않습니다. 실제 개발 중 자연스럽게 발생한 Agent Behavior regression을 merge 전에 유용하게 차단하는 사례와 유지비용 데이터가 더 필요합니다.
