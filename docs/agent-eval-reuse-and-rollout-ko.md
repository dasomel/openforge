# Agent Eval 재사용 및 롤아웃 정책

## 목적

AGENT-005는 Narwhal, KubeMetal, nfs-quota-agent 세 프로젝트에서 portability가 확인됐지만, OpenForge 구현이 아직 Draft stacked PR에 있으므로 pilot 저장소는 evaluator/binder/gate의 local copy를 유지합니다.

이 문서는 downstream CI가 미병합 OpenForge branch에 의존하지 않으면서 self-contained pilot 구조에서 안정적인 reusable runtime으로 전환하는 기준을 정의합니다.

## 현재 pilot 구조

각 pilot은 프로젝트별 live verification command와 risk/evidence policy를 소유합니다. Trace schema, evaluator 의미, trusted baseline comparison, AGENT-005 profile은 OpenForge의 canonical contract입니다.

현재 경계는 다음과 같습니다.

- repository-local: risk policy, live verification command, trace 선택, 프로젝트별 evidence boundary
- OpenForge canonical: trace/eval schema, outcome consistency, evaluator, comparator, AGENT-005 audit contract
- pilot 기간 중 중복 유지: downstream evaluator/gate/binder runtime 파일

## Reusable gate

OpenForge의 `.github/actions/agent-eval/action.yml`은 canonical reusable gate입니다. hydrated trace를 trusted baseline과 비교하며 OpenForge canonical evaluator/comparator를 실행합니다.

이 action은 임의의 프로젝트 verification command를 실행하지 않습니다. Kubernetes runtime, native/Tauri, privileged filesystem 검증은 실행 권한과 trust boundary가 서로 다르므로 live verification 자체는 프로젝트가 소유하는 것이 안전합니다.

향후 downstream workflow는 다음 순서를 권장합니다.

1. 프로젝트별 verification command 실행
2. 결과를 strict trace에 bind
3. immutable ref로 pin된 OpenForge Agent Eval Gate 호출
4. changed-path/risk/evidence correlation은 별도 stable reusable contract가 생기기 전까지 repository-local 유지

## Pinning 정책

production CI에서 `feat/agent-ops-pilot` 같은 feature branch나 `main` 같은 floating branch를 참조하지 않습니다.

OpenForge foundation/operational PR이 병합되고 reusable surface가 안정적인 immutable reference를 가진 뒤에만 downstream migration을 진행합니다. 첫 migration은 OpenForge full commit SHA pin을 권장합니다. 사람이 보는 문서에서는 release tag를 사용할 수 있지만 CI는 repository supply-chain 정책에 따라 immutable pin을 유지하는 것이 원칙입니다.

## Pilot portfolio 검증

`templates/agent-eval/portfolio.pilots.yml`은 세 AGENT-005 pilot을 정의하고, `.github/workflows/agent-005-pilot-portfolio.yml`은 OpenForge CI 내부에서만 pilot branch를 checkout해 다음을 확인합니다.

- metric set `2026.10`
- Narwhal `AGENT-005 == 2`
- KubeMetal `AGENT-005 == 2`
- nfs-quota-agent `AGENT-005 == 2`
- reusable gate가 실제 KubeMetal operational trace를 평가할 수 있음

이 workflow는 downstream production dependency가 아니라 OpenForge 내부의 cross-project validation infrastructure입니다.

## Downstream 중복 runtime 제거 조건

OpenForge reusable action이 Draft PR에 존재한다는 이유만으로 downstream의 `evaluate.py`, `gate.py`, `bind-verification.py`를 삭제하지 않습니다.

중복 evaluator/gate 코드는 다음 조건을 모두 만족한 뒤 제거합니다.

1. OpenForge foundation/operational 변경 병합
2. reusable action의 immutable stable commit 확보
3. downstream workflow가 해당 immutable ref로 전환
4. healthy trace와 regression fixture 또는 historical evidence에서 기존과 동일한 pass/fail 확인
5. 첫 migration 기간 동안 local runtime으로 쉽게 rollback 가능

Binder는 프로젝트별 실행/evidence 경계를 과도하게 일반화하지 않기 위해 evaluator/gate보다 더 오래 local로 유지할 수 있습니다.
