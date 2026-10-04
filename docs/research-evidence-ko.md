# 연구 증거 수집 표준

OpenForge 프로젝트는 개발 중 발생한 재현 가능한 결과를 남겨야 합니다. 나중에 논문이나 기술 보고서를 작성할 때 과거 측정치를 추측해 복원하지 않기 위해서입니다.

## 수집 대상

가능하면 Git 이력, 테스트·빌드·배포의 결과와 소요 시간, 실패와 복구, 실행 중 자원 사용량, 에이전트 작업의 시도와 사람의 개입, 릴리스와 호환성 결과를 기계가 읽을 수 있는 형식으로 기록합니다. 성공뿐 아니라 실패·부분 성공·건너뜀도 보존합니다.

새 작업에서 생성한 측정치는 앞으로의 증거로 기록합니다. 작업 중 발견한 기존 QA 보고서, CI 결과, 벤치마크, 추적 자료 등은 원본을 보존하고 [기존 증거 목록](legacy-evidence-catalog.md)에 출처, 날짜, 증거 종류와 강도, 환경, 사실, 한계, 공개 검토 상태를 등록합니다. 기록되지 않은 시간이나 개입 횟수를 추정해 채우지 않습니다.

## 기록과 공개 안전

새 측정치에는 UTC 시각, 저장소와 Git 리비전, 테스트 또는 작업 이름, 환경, 스키마 버전, 실제 측정한 결과를 연결합니다. 메트릭 정의를 바꾸면 버전을 올립니다. 작은 영구 기록에는 추가 전용 JSONL을 사용하고, 오래된 줄은 결과를 개선하려고 다시 쓰지 않습니다. 정정은 가능하면 연결된 새 기록으로 남깁니다.

공개 저장소의 증거에는 실제 비밀번호, 토큰, 쿠키, 개인 키, 인증 헤더, 비밀이 담긴 kubeconfig, 개인 정보를 넣지 않습니다. 공개 프로젝트의 테스트 주소·호스트명·토폴로지·버전은 재현에 필요할 때 남길 수 있습니다. 외부 조직의 비공개 환경 자료는 공개 전에 별도로 검토합니다. 스키마 검사, 비밀 패턴 검사, 자유 형식 필드 검토를 거칩니다.

## 표준 스키마와 배치

표준 v1 스키마는 [`schemas/research-evidence-v1.schema.json`](../schemas/research-evidence-v1.schema.json)입니다. 필수 필드는 `schema_version`, `timestamp`, `repository`, `revision`, `event_type`, `task_or_test`, `result`, `duration_ms`, `environment`, `attempt`, `human_interventions`, `review_corrections`, `ci_retries`, `metadata`입니다. `duration_ms`는 실제 경과 시간을 측정했을 때만 수치로 기록합니다. `metadata`는 스키마가 허용하는 안전한 스칼라 값만 사용합니다.

```text
research/
  README.md
  evidence/YYYY-MM.jsonl
  experiments/<experiment-id>/
```

## 공통 기록기와 검증기

`templates/scripts/record-evidence.py`와 `templates/scripts/check-research-evidence.py`를 프로젝트의 `scripts/research/`에 복사합니다. Python 3과 `jsonschema`가 필요합니다. 기록기는 `origin`에서 저장소 이름을, `HEAD`에서 리비전을 가져오고 명령을 직접 실행합니다. 명령 인수·환경 변수·원시 출력은 기록하지 않으며 실제 경과 시간을 측정해 월별 JSONL에 추가합니다. 새 작업·환경 이름만 v1 문자 규칙에 맞게 정규화하고 기존 증거는 바꾸지 않습니다.

```sh
python3 -m pip install 'jsonschema>=4.18,<5'
python3 scripts/research/record-evidence.py --task 'make test' --event-type test -- make test
make research-check
```

`RESEARCH_EVIDENCE_DIR`로 체크아웃 밖에 임시 기록을 만들 수 있습니다. `agent_task`에는 실제 관찰한 `--human-interventions`와 `--review-corrections`를 지정해야 합니다. 검증기는 스키마, UTC 날짜, 비밀 패턴, 로컬 Git 커밋 존재 여부를 검사합니다. 얕은 체크아웃에서 오래된 리비전을 찾지 못하면 필요한 이력을 먼저 가져와야 합니다.

검증 실행은 `test` 이벤트로 기록합니다. 기록기가 기존 CLI 입력 `--event-type verification`을 받으면 저장할 때 `test`로 바꿉니다. `verification`은 v1 스키마의 이벤트 종류가 아닙니다.

### 과거 스키마 예외

기존의 부적합 줄은 수정하거나 삭제하지 않습니다. `research/evidence/known-invalid.json`에 각 줄의 `file`, `line`, `sha256`, `reason`을 배열 원소로 기록합니다. 해시는 줄바꿈을 포함한 원본 바이트로 계산합니다. 검증기는 해시가 일치하는 줄만 건너뛰고, 줄의 변경·삭제 또는 새 부적합 줄을 실패로 처리합니다. 새 기록에는 예외를 적용하지 않습니다. 연결된 정정 기록이 생긴 뒤에만 예외 항목을 제거합니다.

연구 분석에서는 가설, 비교 집단, 제외 기준을 별도로 정하고, 증거의 출처·버전·실패·한계를 함께 보존합니다.
