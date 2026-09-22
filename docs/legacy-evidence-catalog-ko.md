# 레거시 증거 카탈로그

`portfolio/legacy-evidence-catalog.json`은 대상 OSS 저장소에 이미 존재하는 증거를 기록한 카탈로그입니다. 각 항목은 역사적 파일 경로를 참조하며 원본 증거를 이동하거나 다시 쓰거나 정규화하지 않습니다. `portfolio/`에 둔 이유는 기존 포트폴리오 레지스트리와 함께 포트폴리오 전체 산출물임을 분명히 하기 위해서입니다.

항목 필드는 `repository`, `path`, `evidence_date`, `evidence_class`, `evidence_strength`, `environment_scope`, `metrics_or_facts`, `limitations`, `future_paper_use`, `privacy_review`, `availability`입니다. 클래스는 `verification-quality`, `deployment-reproducibility`, `reliability-recovery`, `runtime-performance`, `agent-assisted-engineering`, `release-adoption-evolution`, `architecture-requirements`입니다. 강도는 `measured`, `observed`, `derived`, `contextual`, 환경 범위는 `local-test`, `ci`, `simulation`, `live-test`, `unknown`, 개인정보 검토 상태는 `public-ok`, `secret-check-required`, `exclude`입니다. `availability`는 해당 경로가 저장소에 tracked이면 `committed`, 스캔한 작업 트리에는 있지만 git이 추적하지 않으면 `local-only`, 스캔 대상 루트가 git 저장소가 아니면 `unknown`이며, 저장소당 한 번 `git ls-files`로 판정합니다. `local-only` 항목은 삭제하지 않고 남깁니다 -- 커밋되지 않은 부하 테스트 결과처럼 실제 측정치가 섞여 있기 때문입니다 -- 다만 clone에서는 접근할 수 없으므로 `limitations`에 그 사실을 적습니다. 보존하려면 의도적으로 커밋하거나 아카이브해야 합니다. 접근할 수 없었던 저장소는 `pending_repositories`의 `not-scanned` 상태로 따로 기록합니다.

후보 목록은 `python3 templates/scripts/inventory-legacy-evidence.py --repo PATH --repository SLUG`로 생성하고, 검토 후 `--refresh --catalog portfolio/legacy-evidence-catalog.json`을 붙여 해당 저장소 항목을 갱신합니다. 커밋된 카탈로그는 `python3 templates/scripts/inventory-legacy-evidence.py --validate`로 검증합니다. 검색 결과는 결정적이고 보수적입니다. 카운트, 단위가 있는 시간·자원·백분율, 구조화 레코드의 알려진 숫자 키처럼 인식 가능한 메트릭을 실제로 추출한 경우에만 `measured`를 내보냅니다. 그 밖의 기계 생성 레코드는 `observed`, 서술·설계 문서는 `contextual`입니다. 날짜는 경로/파일명의 ISO 날짜나 명시적 구조화 필드에서만, 환경 범위는 산출물의 명시적 필드에서만 읽습니다.

로컬에 없는 저장소는 `pending_repositories`의 `not-scanned` 항목으로 남겼습니다. 없는 수치, 실패, 부분 결과, 건너뛴 결과를 만들어내지 않으며 원본에 있는 결과는 보존합니다. 공개 전에 비밀값을 검토하고 모든 레거시 산출물은 원래 위치와 형식에 둡니다.

검색에서는 증거가 아닌 산출물을 제외합니다. `.github/ISSUE_TEMPLATE/**`, `.github/workflows/**`와 `templates/workflows/**` 아래의 워크플로 정의, 숨김 점 파일, `fixtures/` 또는 `testdata/` 디렉터리 아래의 경로, `src/**`와 일반적인 언어 소스 확장자를 사용하는 애플리케이션 소스가 대상입니다. 저장소에 커밋된 워크플로 실행 결과가 정의 파일 경로 밖에 있으면 증거가 될 수 있지만, 워크플로 도구 자체는 포함하지 않습니다. 합성 컴플라이언스 fixture와 UI·소스 파일은 역사적 측정값을 기록하지 않으므로 제외합니다.
