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

### GitHub Actions 과거 기록 백필

`templates/scripts/backfill-actions-evidence.py`를 공통 검증기 옆에 복사하거나 이 저장소에서 실행합니다. Python 3, `jsonschema`, 인증된 `gh` CLI, 전체 `origin/main` 이력이 필요합니다. 필터 없는 페이지 조회로 완료된 workflow 실행을 읽고 GitHub가 반환한 최신 attempt를 사용하며, `origin/main`에서 도달 가능한 revision만 포함합니다. 삭제·만료된 실행이나 API가 반환하지 않는 이전 attempt는 복구하지 못합니다. 제외 건수도 데이터셋에 포함해야 합니다. main 이력만 고른 표본을 전체 개발이나 PR 실패의 대표 표본으로 해석하면 안 됩니다.

```sh
python3 templates/scripts/backfill-actions-evidence.py --repo-root /path/to/project --output-dir /path/to/staging --dry-run
python3 templates/scripts/backfill-actions-evidence.py --repo-root /path/to/project --output-dir /path/to/staging
```

공개 전 staging 결과와 기존 증적을 합쳐 검토·검증합니다. staging 또는 checkout에 있는 `(gh_run_id, gh_run_attempt)`는 재실행 시 건너뜁니다. 기존 바이트를 보존하며 대상 파일 끝에 개행이 없으면 쓰기를 중단합니다. 별도 staging 디렉터리를 쓰면 과거 파일을 수정하지 않습니다. 출력 경로를 생략하면 checkout의 증적 디렉터리에 기록합니다. `--since YYYY-MM-DD`로 기간을 제한하며, 생략하면 조회 가능한 전체 이력을 사용합니다.

`duration_ms`는 API의 `updated_at - run_started_at` 간격이며 `metadata.duration_semantics=workflow_update_interval`로 표시합니다. 실행 후 갱신과 재실행의 영향을 받을 수 있어 job 실행 시간·CPU 시간·정확한 workflow 완료 시간으로 해석하지 않습니다. event 분류는 이름/경로로 추론하며 일치하지 않으면 `test`로 분류합니다. `attempt`와 `ci_retries`는 `run_attempt`에서 파생된 workflow 재실행 횟수이며 개별 job 재시도 횟수가 아닙니다. 사람 개입·리뷰 수정은 관측되지 않았습니다. v1이 정수를 요구해 0을 채우지만 metadata에 `human_interventions_observed=false`, `review_corrections_observed=false`를 명시합니다. 개입·수정 분석에서는 이 필드를 제외하고, 0을 실측 0으로 간주하지 않습니다.

### 주기적 백필

일회성 백필은 실행한 날 이후의 증거를 늘리지 못합니다. `templates/workflows/research-evidence-backfill.yml`은 이를 매주(월요일 00:17 UTC, 수동 `workflow_dispatch` 포함) 다시 실행합니다. workflow를 `.github/workflows/`에, `templates/scripts/backfill-actions-evidence.py`를 `scripts/research/`에 바이트 단위로 동일하게 복사합니다(가져오는 검증기 옆). 작업은 전체 이력을 가져와 `(gh_run_id, gh_run_attempt)`가 아직 없는 실행만 추가하고, 자기 workflow의 실행은 `--exclude-path`로 제외하며, `scripts/research/check-research-evidence.py`를 통과해야 하고, 변경이 없으면 커밋 없이 종료합니다. concurrency 그룹으로 실행이 겹치지 않습니다.

전달 방식은 자동 감지하지 않고 workflow `env`의 `EVIDENCE_DELIVERY`로 저장소마다 명시합니다.

- `push`: `main`이 보호되지 않았거나 필수 검사가 없을 때. `research/evidence` 변경만 `github-actions[bot]`으로 커밋해 `main`에 push합니다(non-fast-forward면 rebase 후 한 번 재시도).
- `pr`: `main`에 필수 검사가 있을 때. 고정 브랜치 `bot/research-evidence-backfill`을 매 실행마다 `main`에서 새로 만들어 force-push하고(force-push 대상은 이 봇 브랜치뿐), 열린 PR이 없으면 PR을 만듭니다. 이미 열려 있으면 push가 그 PR을 갱신합니다. 저장소 설정 "Allow GitHub Actions to create and approve pull requests"가 필요합니다(`gh api -X PUT repos/<owner>/<repo>/actions/permissions/workflow -f default_workflow_permissions=read -F can_approve_pull_request_reviews=true`).

한계: `GITHUB_TOKEN`으로 만든 push와 PR은 다른 workflow를 실행하지 않으므로 봇 PR에서는 필수 검사가 자동으로 돌지 않습니다. 소유자가 관리자 머지 또는 저장소의 리뷰 절차로 머지합니다. 개인 토큰 등으로 우회하지 않습니다. 브랜치 보호가 바뀌면 방식을 다시 정합니다.

### 포트폴리오 증적 관리 범위

[증적 관리 범위](../portfolio/research-evidence-scope.json)에 명시적 제외 대상을 기록합니다. `dasomel/cka-lab`은 소유자 요청에 따라 증적 수집·백필·완전성 감사에서 제외합니다. 기존 과거 산출물은 보존하며, 증적 관리 제외가 엔지니어링 포트폴리오에서의 삭제를 뜻하지는 않습니다. 수집·감사 담당자는 저장소를 선택하기 전에 이 범위를 확인합니다.
