# 외부 기여 레지스트리

English: [external-contributions.md](external-contributions.md)

OpenForge는 외부 개발자가 포트폴리오 저장소에 가져온 공개 논의와 기여를 기록합니다. 누가, 어느 스레드에서, 무엇을 했고, 현재 상태가 무엇인지입니다. 레지스트리는 `portfolio/external-contributions.json`의 검토 가능한 데이터이며 [포트폴리오 대시보드](portfolio-dashboard.md)에 렌더링됩니다. 관심과 기여를 기록하는 것이지 품질 평가, 보증, 채택 약속이 아닙니다.

## 외부의 기준

- 저장소 소유자도, 포트폴리오 메인테이너도 아닌 계정입니다.
- 봇이나 자동화(dependabot, CI 앱, 릴리스 도구)가 아닙니다.
- GitHub의 공개 스레드이며 계정이 GitHub에서 확인됩니다.

확인할 수 없는 계정은 제외합니다. 간접 요약에만 등장한 이름, GitHub에서 조회되지 않는 계정, 인용한 스레드에 흔적이 없는 계정은 기록하지 않습니다. 스레드 자체에서 기여가 확인된 뒤에만 다시 추가합니다.

## 파일

| 경로 | 역할 |
|------|------|
| `schemas/external-contributions-v1.schema.json` | 버전이 있는 계약(`openforge-external-contributions/v1`) |
| `portfolio/external-contributions.json` | 레지스트리: `schema_version`, `observed_at`, `entries[]` |
| `templates/scripts/validate-external-contributions.py` | 스키마와 의미 검증, CI에서 실행 |
| `tests/fixtures/external-contributions/` | 합성 픽스처 전용, `portfolio/`로 복사하지 않음 |

## 항목 필드

| 필드 | 규칙 |
|------|------|
| `id` | kebab-case, 고유 |
| `repository` | `portfolio/projects.json`에 있는 프로젝트의 `owner/name` |
| `kind` | `issue` 또는 `pull_request` |
| `number` | 스레드 번호, `(repository, number)`는 고유 |
| `url` | `issue`는 정확히 `https://github.com/<repository>/issues/<number>`, `pull_request`는 `.../pull/<number>` |
| `contributors` | `@` 없는 GitHub 핸들의 비어 있지 않은 목록, 중복 없이 대소문자 무시 정렬 |
| `contribution_type` | 아래 참조 |
| `summary` | 짧은 영어 설명, 최대 240자 |
| `state` | `open`, `closed`, `merged`(`merged`는 pull request에만) |
| `outcome` | 선택, 예: 무엇이 채택되었는지 |
| `observed_at` | UTC `YYYY-MM-DDTHH:MM:SSZ`, 미래일 수 없고 레코드의 `observed_at`보다 늦을 수 없음 |

항목은 `(repository, number)` 순으로 정렬합니다.

`contribution_type` 값:

| 값 | 의미 |
|----|------|
| `design` | 디자인 산출물 또는 디자인 레퍼런스 |
| `proposal` | 변경이나 기능 제안 |
| `design-review` | 기여자 자신의 관점에서 기존 설계를 검토 |
| `support-offer` | 관련 프로젝트의 지원·협업 제안 |
| `bug-report` | 결함 보고 |
| `docs` | 문서 기여 |

## 개인정보 규칙

- `@` 없이 GitHub 핸들만 저장합니다. 이메일, 실명, 기타 개인정보는 넣지 않으며 검증기는 핸들의 `@`를 거부합니다.
- 공개 스레드만 기록합니다. 비공개 보고, 보안 제보, 비공개 메시지는 요약하지 않습니다.

## 상태는 스냅샷

`state`와 `outcome`은 `observed_at` 시점의 스레드 상태이며 실시간이 아닙니다. 대시보드도 수치 옆에 이를 밝힙니다. 관찰 이후 스레드가 바뀔 수 있으므로 의존하기 전에 다시 확인합니다.

## 갱신

```bash
gh issue view <number> --repo <owner>/<repo> --json state,closedAt,url,author
gh pr view <number> --repo <owner>/<repo> --json state,mergedAt,url,author
gh issue view <number> --repo <owner>/<repo> --comments   # 실제 기여자 확인
```

`state`, `outcome`, 두 `observed_at`을 갱신한 뒤 재생성하고 검증합니다.

```bash
python3 templates/scripts/validate-external-contributions.py
python3 templates/scripts/generate-portfolio.py
python3 templates/scripts/generate-portfolio.py --check
```

`--now YYYY-MM-DDTHH:MM:SSZ`로 미래 타임스탬프 검사를 결정적으로 만들 수 있습니다.

## 대시보드

`generate-portfolio.py`는 `portfolio/dashboard.json`에 `external_contributions` 키(상태·유형·저장소별 집계와 URL이 있는 항목)를 추가하고 대시보드 페이지에 "External contributions" 섹션을 추가합니다. 키는 추가(additive)이므로 `openforge-dashboard/v1`은 그대로이며, 레지스트리 파일이 없으면 생략됩니다.
