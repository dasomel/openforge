# Agent Evaluation 적용 기록 — 2026-08

OpenForge Agent Behavior 및 Trace/Eval 모델의 cross-project 적용 기록입니다.

## 적용 범위

Narwhal, KubeMetal, nfs-quota-agent에 동일한 5개 Behavior를 적용하되 runtime evidence 경계는 프로젝트별로 유지합니다.

- Narwhal: Kubernetes/GitOps/RBAC/cluster runtime
- KubeMetal: macOS/Tauri/MLX/native runtime
- nfs-quota-agent: quota/filesystem/privileged host

## Phase 요약

1. 공통 Behavior spec 적용
2. canonical trace/eval schema와 trusted baseline regression gate 적용
3. 실제 supply-chain 유지보수 trace와 immutable-input guard 적용
4. high-risk 변경에 same-diff trace 강제
5. changed path ↔ trace ↔ scoped/typed evidence correlation 적용
6. outcome/evidence strict consistency 적용

## Phase 6 — Outcome/Evidence 일관성

이제 high-risk 작업에서 trace 파일과 verification event가 존재하는 것만으로 완료를 인정하지 않습니다.

`consistencyMode: strict` trace의 `A` 완료 상태는 `completion_claim`, scope와 typed evidence를 가진 verification, 그리고 `passed`, `success`, `ok`, `verified` 등 명시적 성공 status를 요구합니다. failed/pending/unknown/skipped/unverified 또는 status 미지정 relevant verification이 있으면 `task-convergence`가 `false`가 되고, 실패 또는 미확정 verification 상태에서 완료를 주장하면 `evidence-before-claim`도 `false`가 됩니다.

strict bug fix에서는 `regression_verification`도 명시적으로 성공해야 합니다. `B/C` 상태는 next action이 있으면 유효하지만 strict mode에서는 `completion_claim`과 동시에 존재할 수 없습니다.

과거 historical trace는 legacy mode로 유지합니다. 현재 high-risk diff와 실제로 관련된 trace만 strict 계약을 요구하므로 불필요한 과거 trace migration을 피합니다.

## Cross-project 반영

OpenForge, Narwhal, KubeMetal, nfs-quota-agent evaluator에 동일한 strict consistency 의미를 반영했습니다. 각 저장소의 현재 operational maintenance trace도 `consistencyMode: strict`와 `status: passed` verification/regression-verification으로 승격했습니다.

High-risk evidence checker도 관련 trace에 strict mode와 최소 하나의 명시적 passed verification을 요구합니다.

## 검증

OpenForge CI/Markdown과 세 downstream의 Agent Behavior workflow가 strict contract 적용 상태에서 통과했습니다. KubeMetal repository CI와 Narwhal Version Check 등 기존 workflow는 Agent Behavior와 별도 evidence class로 계속 관리합니다.

## AGENT-005 판단

아직 `AGENT-005`는 추가하지 않습니다.

이제 잘못된 완료 주장을 기존 Behavior의 `true → false` regression으로 구조적으로 변환할 수 있습니다. 다음 최종 근거는 synthetic fixture나 governance tool 자체 결함이 아니라, 일반 개발 과정에서 자연스럽게 발생한 Agent Behavior regression을 strict baseline gate가 merge 전에 실제 차단한 사례입니다.
