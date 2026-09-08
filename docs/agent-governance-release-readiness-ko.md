# Agent Governance 릴리스 준비 계획

OpenForge Agent Behavior / Agent Evaluation stack을 안전하게 병합하고 배포하기 위한 순서를 정의합니다.

## 현재 stack

### OpenForge

1. PR #19 — `feat/agent-behaviors` → `main`
   - AGENT-004 / Behavior specification
   - trace/eval foundation
   - metric set `2026.09`
2. PR #24 — `feat/agent-ops-pilot` → `feat/agent-behaviors`
   - operational trace와 risk/evidence gate
   - live verification binding
   - AGENT-005
   - metric set `2026.10`
   - pilot portfolio와 reusable gate action

### Downstream pilot

| Repository | Foundation | Operational |
| --- | --- | --- |
| Narwhal | #172 | #173 |
| KubeMetal | #51 | #52 |
| nfs-quota-agent | #85 | #86 |

모든 operational PR은 각 repository의 foundation branch 위에 stacked되어 있습니다.

## 필수 병합 순서

Operational PR이 아직 foundation feature branch를 base로 하는 상태에서는 먼저 merge하지 않습니다. 그렇게 하면 operational layer가 foundation branch에 합쳐져 이후 foundation merge에 두 단계가 한꺼번에 들어갈 수 있습니다.

안전한 순서는 다음과 같습니다.

1. required check 통과 후 OpenForge #19를 `main`에 merge합니다.
2. OpenForge #24의 base를 `feat/agent-behaviors`에서 `main`으로 변경합니다.
3. #24 diff가 operational layer만 포함하는지 확인하고 required checks와 AGENT-005 Pilot Portfolio를 다시 실행합니다.
4. retarget된 diff가 깨끗할 때만 #24를 `main`에 merge합니다.
5. 각 downstream에서는 foundation PR을 먼저 merge합니다.
6. 같은 repository의 operational PR base를 `main`으로 변경합니다.
7. retarget된 operational diff를 확인하고 repository CI와 Agent Behavior CI를 다시 실행합니다.
8. repository별 blocker가 해소된 뒤 operational PR을 merge합니다.

각 repository 내부에서는 foundation → operational 순서가 필수지만, 세 downstream repository 사이의 순서는 고정할 필요가 없습니다. 첫 canary rollout은 Agent Behavior와 기존 repository CI가 모두 green인 KubeMetal이 가장 안전합니다. Narwhal은 unrelated repository-CI failure를 Agent Behavior evidence와 계속 분리해야 합니다.

## Merge 전 체크

Foundation PR:

- 최신 `main`을 포함하거나 GitHub merge state가 clean일 것
- required repository check 완료
- Behavior spec validation 성공
- operational-only 파일이 foundation diff에 섞이지 않을 것

Operational PR:

- foundation merge 후 base가 `main`일 것
- `consistencyMode: strict` trace 유효
- live verification binder가 실제 repository-owned 검증을 실행
- high-risk diff / trace / typed evidence correlation 성공
- trusted baseline comparison 성공
- 적용된 repository에서는 immutable-input guard 성공
- repository/runtime CI는 Agent Behavior와 별도 evidence class로 보고

## Stable reusable action rollout

Downstream CI가 아직 merge되지 않은 OpenForge branch를 직접 의존하게 만들지 않습니다.

OpenForge #24 merge 후:

1. `.github/actions/agent-eval/action.yml`을 포함하는 immutable OpenForge `main` SHA를 기록합니다.
2. 해당 SHA의 action을 세 pilot repository에 대해 검증합니다.
3. 먼저 KubeMetal 한 곳에 canary migration합니다.
4. local gate와 reusable gate를 병렬 실행해 pass/fail equivalence를 확인합니다.
5. equivalence가 확인된 뒤에만 local evaluator/comparator 중복을 제거합니다.
6. live verification command, risk policy, evidence boundary, binder semantics는 repository에 남깁니다.
7. canary가 안정되면 Narwhal과 nfs-quota-agent로 확대합니다.

Rollback은 remote reusable gate 호출을 마지막 known-good local gate로 되돌리는 방식입니다.

## 현재 readiness snapshot

- OpenForge #19는 최신 `main`과 동기화됐고 CI / Markdown이 성공했습니다.
- OpenForge #24는 갱신된 #19 ancestry를 포함하며 CI, Markdown, AGENT-005 Pilot Portfolio가 성공했습니다.
- Narwhal #172/#173은 Draft / mergeable 상태이며 repository-CI evidence는 별도로 판단해야 합니다.
- KubeMetal #51/#52는 Draft / mergeable 상태이고 최신 operational head에서 Agent Behavior와 repository CI가 모두 성공했습니다.
- nfs-quota-agent #85/#86은 Draft / mergeable 상태이며 operational layer에는 shipped container의 Btrfs runtime dependency 수정과 live filesystem evidence gate가 포함됩니다.

실제 merge 시점에는 이 문서의 snapshot이 아니라 최신 GitHub check와 현재 base/head SHA를 다시 확인합니다.