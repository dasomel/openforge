# AGENT-005 승격 기록 — 2026-08

## 결정

**AGENT-005 — Operational Agent Evaluation Profile**을 OpenForge canonical portfolio metric set `2026.10`으로 승격한다.

AGENT-005는 adoption-level metric이다. 저장소가 `.agents/evals/`를 도입하지 않았고 `agent_evals: true`로 명시하지 않았다면 `N/A`로 처리한다.

## AGENT-005가 측정하는 것

AGENT-005는 디렉터리나 파일 존재 여부만으로 점수를 주지 않는다. 통과하려면 다음 실행 가능한 operational contract가 필요하다.

- canonical evaluator와 trusted baseline
- regression gate
- live verification binder
- 최소 하나의 `consistencyMode: strict` trace
- 명시적인 verification status와 typed evidence semantics
- strict trace 내 completion claim과 task outcome
- live verification binding과 regression gate를 실제 실행하는 CI wiring

숨겨진 reasoning이나 chain-of-thought는 검사하지 않는다.

## 승격 근거

승격 기준은 서로 성격이 다른 두 runtime domain에서 동일한 live-evidence contract가 실제 maintenance defect를 자연스럽게 검출하는 것이었다.

### 근거 1 — Narwhal

Narwhal PR #173에서 기존 Kubernetes version source-of-truth drift가 발견됐다.

- `VERSIONS.md`: `1.35.5`
- `Vagrantfile`: `1.35.7`

실제 consistency command가 exit 1을 반환했고 live binder가 verification failure를 기록했다. trusted baseline gate는 다음 세 회귀를 검출했다.

- `bug-fix-verification`: `true -> false`
- `evidence-before-claim`: `true -> false`
- `task-convergence`: `true -> false`

source-of-truth를 수정한 뒤 evaluator나 baseline을 완화하지 않고 동일 검증 경로가 통과했다.

### 근거 2 — nfs-quota-agent

nfs-quota-agent PR #86에서는 완전히 다른 runtime boundary인 실제 배포 container의 filesystem tooling을 검증했다.

기존 compatibility matrix에는 Btrfs 구현이 `btrfs` CLI를 호출하지만 shipped container에는 `btrfs-progs`가 없어 런타임에서 실패한다는 known gap이 이미 기록되어 있었다.

live check는 실제 shipped image를 빌드하고 container 내부 명령을 직접 확인했다. `xfs_quota`, `setquota`, `chattr`, `findmnt`는 존재했지만 `btrfs`는 누락되어 있었다. binder가 exit 1을 기록했고 동일한 세 Behavior regression이 gate를 차단했다.

수정에서는 `btrfs-progs`를 image에 추가하고 package/license evidence를 갱신했다. Btrfs compatibility 상태는 실제 Btrfs filesystem E2E가 아직 없으므로 `verified`가 아니라 `build-verified`로만 올렸다. 동일 live image check는 수정 후 통과했다.

## 승격 판단

두 pilot은 실패 원인과 검증 방식이 다르다.

- Narwhal: repository/runtime version consistency
- nfs-quota-agent: built container runtime capability

두 경우 모두 같은 observable-evidence contract가 false completion claim을 차단했고 private reasoning을 수집하지 않았다. 따라서 특정 저장소 fixture에 종속되지 않은 portability가 확인되었다.

## Guardrail

AGENT-005는 모든 maintenance task를 trace로 남기라는 의미가 아니다. agent-heavy 또는 high-risk 변경에 선택적으로 적용한다. baseline은 CI를 통과시키기 위해 낮추지 않으며, build/runtime-tool verification과 실제 infrastructure E2E evidence는 계속 구분한다.
