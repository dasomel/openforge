# Agent Evaluation 적용 기록 — 2026-08

이 문서는 OpenForge Agent Behavior 및 Trace/Eval 모델을 실제 OSS와 유지보수 작업에 적용한 증거를 기록합니다.

## Phase 1 — Cross-project 적용

Narwhal, KubeMetal, nfs-quota-agent에 동일한 5개 Behavior를 적용했습니다. Behavior 이름은 공통으로 유지할 수 있었지만 runtime evidence는 프로젝트별로 구분해야 했습니다.

- Narwhal: Kubernetes/GitOps/RBAC/cluster runtime
- KubeMetal: macOS/Tauri/MLX/native runtime
- nfs-quota-agent: quota/filesystem/privileged host

Behavior CI와 기존 repository CI는 서로 다른 evidence class로 유지합니다.

## Phase 2 — Operational Regression Gate

다음 stacked PR에서 선택적 operational trace와 trusted baseline regression gate를 적용했습니다.

- OpenForge #24
- Narwhal #173
- KubeMetal #52
- nfs-quota-agent #86

모든 변경에 Trace를 강제하지 않고 Agent-heavy 또는 고위험 작업에만 `.agents/evals/traces/*.json`을 남깁니다.

## Phase 3 — 실제 유지보수 Longitudinal Pilot

OpenForge #25에서 실제 supply-chain 유지보수 작업을 pilot으로 수행했습니다.

연결된 실제 backlog:

- Narwhal #52 / #164
- KubeMetal #5 / #36
- nfs-quota-agent #26

세 downstream Agent Behavior workflow에 남아 있던 `actions/checkout@v4` floating ref를 commit SHA로 고정하고, `:latest`, `releases/latest/download`, SHA가 아닌 GitHub Action ref를 차단하는 deterministic guard를 추가했습니다.

세 저장소 모두 실제 maintenance trace를 기록했습니다.

OpenForge의 첫 validator 테스트에서는 `aquasec/trivy:latest`를 탐지하지 못하는 정규식 결함이 발견됐습니다. `test_rejects_latest_image` 실패를 근거로 detector를 수정하고 세 downstream에 다시 반영한 뒤 CI가 통과했습니다.

## Phase 4 — 위험도 기반 same-diff trace 강제

선택적 trace 정책을 한 단계 더 강화했습니다. 이제 maintainer가 고위험 변경에서 trace 추가를 기억하는 것에 의존하지 않습니다.

저장소별 `openforge-agent-risk-policy/v1` 정책이 PR 변경 파일을 `low`, `medium`, `high`로 분류하고 가장 높은 위험도를 적용합니다. `high`로 분류된 변경은 **같은 PR diff에서 operational trace가 추가 또는 수정되어야** 합니다.

즉 저장소에 과거 trace가 존재하는 것만으로는 통과하지 않습니다.

프로젝트별 주요 high-risk 범위:

- Narwhal: CI/release, air-gap, install/security script, GitOps desired state, version source
- KubeMetal: CI/release, air-gap, Kubernetes mutation, MLX runtime, Tauri native code
- nfs-quota-agent: CI/release, controller code, privileged quota reconciliation, Helm/RBAC, image/compatibility tooling

OpenForge는 reusable template 저장소이므로 downstream `.agents/evals/traces/` 대신 `templates/agent-eval/traces/`를 canonical trace 경로로 사용합니다.

### 실제 rollout 실패와 복구

첫 OpenForge risk-gate 실행은 실패했습니다. unit test는 모두 통과했지만 초기 policy가 downstream layout인 `.agents/evals/traces/`를 기대하고 있어 OpenForge template trace를 찾지 못했습니다.

이를 예외로 우회하지 않고 repository profile 문제로 처리했습니다.

1. 실패 결과 확인
2. policy/layout 불일치로 원인 축소
3. OpenForge trace 경로를 `templates/agent-eval/traces/`로 수정
4. risk-gate 구현 자체의 실제 operational trace 추가
5. 동일 CI 재실행 및 성공

세 downstream에서도 `Collect PR changed paths`와 `Require operational trace for high-risk changes` 단계가 실제 실행되어 성공했습니다.

## 현재 결론

현재까지 확보한 증거:

- cross-project Behavior portability
- canonical trace/eval schema
- selective operational trace
- trusted baseline regression gate
- 실제 유지보수 trace 3건 이상
- mutable input deterministic guard
- repository별 high-risk path classification
- same-diff trace requirement
- governance control 자체의 실패/복구 증거

## AGENT-005 판단

아직 `AGENT-005`는 추가하지 않습니다.

남은 핵심 조건은 일반 개발 과정에서 자연스럽게 발생한 **Agent Behavior regression을 merge 전에 실제로 차단하는 사례**입니다. synthetic fixture나 governance-tool 구현 버그는 중요한 증거이지만 portfolio-wide compliance metric 승격의 최종 근거로 계산하지 않습니다.
