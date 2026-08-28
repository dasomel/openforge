# Agent Evaluation 운영 표준

OpenForge Agent Behavior Trace/Eval을 실제 개발 작업에 적용하기 위한 운영 기준입니다. 모든 변경에 Trace 작성을 강제하지 않고, Agent-heavy 또는 고위험 작업에 선택적으로 적용합니다.

## 운영 흐름

```text
선택된 Agent-heavy / 고위험 작업
  → Structured Event를 점진적으로 기록
  → .agents/evals/traces/ 아래 Trace 저장
  → Deterministic Eval
  → Trusted Baseline과 비교
  → Behavior Regression일 때만 Gate 실패
```

## Trace를 남길 작업

다음과 같은 경우 Trace 작성을 권장합니다.

- AI Agent가 다단계 Bug Fix, Migration, Release, Incident 작업을 수행하는 경우
- Unit/Mock Evidence와 실제 Runtime Evidence가 명확히 다른 경우
- Permission, Credential, Privileged Host Access, GitOps Ownership, Destructive Operation 등 Design-level Boundary를 다루는 경우
- 기존 Agent 실패를 재현하거나 Regression Guard를 추가하는 경우
- Merge 이후 Behavior Regression 분석 비용이 큰 경우

Hidden Reasoning, Chain-of-Thought, Credential, Token, Customer Data, Raw Secret, 불필요한 Prompt 원문은 Trace에 기록하지 않습니다.

## Event 기록

`record-agent-event.py` 또는 저장소의 `record.py`를 사용해 관찰 가능한 Event만 추가합니다. Evidence는 Test 이름, CI Check, Sanitized Log, Issue/PR Reference, Runtime Verification Identifier처럼 참조 가능한 형태를 사용합니다.

일반적인 Bug Fix Trace는 `scope_check → reproduction → bug_fix → regression_verification → verification → completion_claim → task_outcome` 순서를 사용합니다.

## Trusted Baseline

Baseline Eval은 자동 갱신 Snapshot이 아니라 Review된 기대값입니다. Behavior 정의가 의도적으로 변경되거나, 적용 가능성이 달라지거나, 더 강한 Evidence 기준을 영구화할 때만 수정합니다.

**Gate를 통과시키기 위해 Baseline을 낮추는 변경은 허용하지 않습니다.**

## CI Regression Gate

Outcome 순서는 다음과 같습니다.

```text
false < na < true
```

따라서 `true → false`, `true → na`, `na → false`는 Regression입니다.

현재 Trace에 실패한 Behavior가 있더라도 Baseline에 이미 동일한 Known Limitation이 기록되어 있다면 Regression Gate 자체는 실패하지 않을 수 있습니다. Absolute Weakness와 새롭게 발생한 Degradation을 구분하기 위한 설계입니다.

## 초기 운영 Pilot

- Narwhal — Kubernetes/GitOps/RBAC 및 Cluster Runtime Evidence
- KubeMetal — macOS/Tauri/MLX 및 Native Capability Evidence
- nfs-quota-agent — Quota/Filesystem/Privileged Host Evidence

세 저장소는 동일한 Canonical Behavior 이름과 Trace/Eval Schema를 유지하면서 프로젝트별 Evidence Boundary만 강화합니다.

## AGENT-005 승격 기준

파일 존재만으로 새로운 Compliance Metric을 만들지 않습니다. 다음 운영 증거가 누적된 뒤 `AGENT-005` 승격을 검토합니다.

- 실제 개발 작업에서 Trace가 과도한 절차 없이 유용하게 생성됨
- 실제 Behavior Regression을 Merge 전에 최소 1회 탐지함
- False Positive 및 유지 비용이 허용 가능한 수준임
- Privacy/Provenance 기준이 여러 저장소에서 유지됨
- Baseline 변경이 형식적인 Rubber Stamp가 되지 않음
- 프로젝트별 Evidence Class가 Portable Behavior Vocabulary를 파편화하지 않음
