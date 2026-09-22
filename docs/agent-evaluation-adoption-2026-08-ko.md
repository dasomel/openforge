# Agent Evaluation 적용 기록 — 2026-08

OpenForge Agent Behavior 및 Trace/Eval 모델의 cross-project 적용 기록입니다.

## 적용 범위

Narwhal, KubeMetal, nfs-quota-agent에 동일한 Behavior 기반을 적용하되 runtime evidence 경계는 프로젝트별로 유지합니다.

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
7. 실제 command 결과를 strict trace verification status에 바인딩
8. 서로 다른 두 runtime domain의 자연 발생 maintenance defect를 동일 Behavior regression contract가 차단
9. metric set `2026.10`에서 AGENT-005를 adoption-level operational profile로 승격

## Phase 6 — Outcome/Evidence 일관성

이제 high-risk 작업에서 trace 파일과 verification event가 존재하는 것만으로 완료를 인정하지 않습니다.

`consistencyMode: strict` trace의 `A` 완료 상태는 `completion_claim`, scope와 typed evidence를 가진 verification, 그리고 명시적 성공 status를 요구합니다. failed/pending/unknown/skipped/unverified 또는 status 미지정 relevant verification이 있으면 `task-convergence`가 `false`가 되고, 실패 또는 미확정 verification 상태에서 완료를 주장하면 `evidence-before-claim`도 `false`가 됩니다.

strict bug fix에서는 `regression_verification`도 명시적으로 성공해야 합니다. `B/C` 상태는 next action이 있으면 유효하지만 strict mode에서는 `completion_claim`과 동시에 존재할 수 없습니다.

과거 historical trace는 legacy mode로 유지합니다. 현재 high-risk diff와 실제로 관련된 trace만 strict 계약을 요구하므로 불필요한 과거 trace migration을 피합니다.

## Phase 7 — Live Evidence와 자연 발생 Regression

live verification binder가 실제 maintenance/runtime command를 실행하고 결과를 `status: passed|failed`, `commandExitCode`, typed runtime evidence로 strict trace에 기록합니다. binder 자체는 정책 결정을 하지 않고 evaluator와 trusted baseline gate가 최종 판단합니다.

### 자연 발생 Regression 1 — Narwhal

Narwhal PR #173에서 기존 Kubernetes version source-of-truth drift가 발견됐습니다. `VERSIONS.md`는 `1.35.5`, `Vagrantfile`은 `1.35.7`이었습니다.

실제 consistency command가 exit 1을 반환했고 trace가 failed로 바인딩되면서 다음 세 Behavior regression이 merge 전에 검출됐습니다.

- `bug-fix-verification`: `true -> false`
- `evidence-before-claim`: `true -> false`
- `task-convergence`: `true -> false`

source-of-truth를 수정한 뒤 evaluator나 baseline을 완화하지 않고 동일 검증 경로가 통과했습니다.

### 자연 발생 Regression 2 — nfs-quota-agent

nfs-quota-agent PR #86에서는 실제 shipped container 내부 filesystem tooling을 검증했습니다. 기존 compatibility matrix에는 Btrfs 구현이 `btrfs` CLI를 사용하지만 image에 `btrfs-progs`가 없어 런타임 실패한다는 known gap이 이미 기록돼 있었습니다.

live check가 실제 image를 빌드하고 container 내부에서 확인한 결과 `xfs_quota`, `setquota`, `chattr`, `findmnt`는 존재했지만 `btrfs`는 누락돼 있었습니다. binder는 exit 1을 기록했고 동일한 세 Behavior regression이 gate를 차단했습니다.

수정에서는 `btrfs-progs`를 image에 추가하고 NOTICE/package-license evidence를 갱신했습니다. Btrfs compatibility는 실제 Btrfs filesystem E2E가 아직 없으므로 `verified`가 아니라 `build-verified`로만 승격했습니다. 동일 live image check는 수정 후 통과했습니다.

## 주요 발견

- Behavior 이름과 regression semantics는 서로 다른 runtime domain에도 이식 가능합니다.
- evidence class와 high-risk path는 프로젝트 특성에 맞게 유지해야 합니다.
- Behavior CI와 기존 repository/runtime CI는 별도 evidence class로 구분해야 합니다.
- 완료 주장은 verification 문구 존재가 아니라 실제 verification 상태에 연결해야 합니다.
- live command binding은 repository consistency와 built-container runtime 검증 양쪽에서 재사용 가능합니다.
- compatibility claim은 evidence 강도를 유지해야 하며, image dependency 수정만으로 실제 filesystem E2E까지 검증됐다고 주장하면 안 됩니다.

## AGENT-005 판단

**AGENT-005를 승격합니다.**

서로 다른 두 runtime domain에서 자연 발생 regression이 실제로 차단되어 승격 기준을 충족했습니다. AGENT-005는 canonical metric set `2026.10`의 **Operational Agent Evaluation Profile**입니다.

AGENT-005는 `.agents/evals/` 디렉터리 존재만 점수화하지 않습니다. 통과하려면 evaluator, trusted baseline, regression gate, live verification binder, explicit status와 typed evidence를 가진 strict trace, completion/outcome semantics, 그리고 live binding과 regression gate를 실제 실행하는 CI wiring이 필요합니다.

프로필을 도입하지 않은 저장소는 `N/A`입니다. `agent_evals: true`는 필수 적용, `agent_evals: false`는 명시적 비활성화로 처리합니다.

상세 승격 근거는 `docs/agent-005-promotion-2026-08-ko.md`를 참조합니다.
