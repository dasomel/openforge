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

### 실제 재현

세 downstream Agent Behavior workflow에 `actions/checkout@v4` floating ref가 남아 있었습니다.

이번 변경에서:

- checkout을 40자리 commit SHA로 고정
- `:latest` 차단
- `releases/latest/download` 차단
- SHA가 아닌 GitHub Action ref 차단
- repository별 release-critical path만 명시적으로 보호
- 세 저장소 모두 실제 maintenance trace 기록

### CI에서 발견한 실제 결함

OpenForge의 첫 validator 테스트에서 `:latest` detector 정규식이 `aquasec/trivy:latest`를 탐지하지 못하는 결함이 발견됐습니다.

`test_rejects_latest_image`가 실패했고, 정규식을 수정한 뒤 세 downstream에 동일하게 반영했습니다. 수정 후 OpenForge CI/Markdown과 세 downstream Agent Behavior workflow가 통과했습니다.

각 downstream에서 다음 단계가 실제로 성공했습니다.

- `Guard immutable build and release inputs`
- `Gate operational traces against trusted baseline`

이 결과는 framework 자체도 deterministic test로 회귀 검증할 수 있음을 보여줍니다.

## AGENT-005 판단

아직 `AGENT-005`는 추가하지 않습니다.

현재까지 확보한 증거:

- cross-project portability
- canonical trace/eval schema
- selective operational adoption
- 실제 유지보수 trace 3건
- trusted baseline gate
- governance control 자체의 실제 test failure 및 복구

남은 핵심 조건은 일반 개발 과정에서 발생한 **자연스러운 Agent Behavior regression을 merge 전에 실제로 차단하는 사례**입니다. 이 증거가 확보되기 전에는 trace/eval 파일 존재 자체를 portfolio compliance metric으로 승격하지 않습니다.
