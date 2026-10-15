# 보안 준비도 증거 계약

English: [security-readiness-evidence.md](security-readiness-evidence.md)

OpenForge는 저장소의 보안·공급망 신호를 담는 도구 중립 레코드 하나를 정의합니다. 업스트림 도구가 보고한 내용을 정규화할 뿐 도구를 다시 구현하지 않습니다. **업스트림 도구(OpenSSF Scorecard, SBOM 생성기, Sigstore, SLSA 빌더, GitHub 자체)가 기반 점검의 출처이며, 이 레코드는 준수·인증 주장이 아닙니다.** 모든 레코드는 이 문장을 필수 `disclaimer`로 담습니다.

## 파이프라인

```text
upstream check -> normalized evidence -> gap/remediation or exception -> re-scan -> portfolio status
```

1. 업스트림 도구 또는 직접 관찰이 결과를 만듭니다.
2. 결과를 `portfolio/security-readiness/<repo>.json`의 신호로 기록하고, 정확한 명령·URL을 `source.ref`에 남깁니다.
3. 격차는 finding과 remediation 상태 또는 책임자가 있는 예외가 됩니다.
4. 재스캔은 이전 관찰을 가리키는 `rescan` 블록으로 추가하며 `improved`, `unchanged`, `regressed` 중 하나를 적습니다.
5. `generate-portfolio.py`가 저장소별 결과를 `portfolio/dashboard.json`과 대시보드 페이지에 노출하고 증거 파일로 연결합니다(포트폴리오 뷰 참고).

## 파일

| 경로 | 역할 |
|------|------|
| `schemas/security-readiness-evidence-v1.schema.json` | 버전 계약(`openforge-security-readiness-evidence/v1`) |
| `portfolio/security-readiness/<repo>.json` | 관찰된 증거, 저장소당 파일 하나, OpenForge에 중앙 보관 |
| `portfolio/security-readiness/scorecard/<repo>.json` | 수정하지 않은 `scorecard --format=json` 원본 출력, `scorecard` 신호의 원천 증거 |
| `templates/scripts/validate-security-readiness.py` | 스키마 및 의미 검증, CI에서 실행 |
| `templates/scripts/import-scorecard.py` | Scorecard v5 어댑터(Scorecard 어댑터 참고) |
| `tests/fixtures/security-readiness/` | 합성 fixture 전용, `portfolio/`로 복사 금지 |

## 신호

| 신호 id | 대응(OpenSSF Scorecard / OSPS Baseline 영역) | 일반적 업스트림 출처 |
|---------|---------------------------------------------|----------------------|
| `scorecard` | OpenSSF Scorecard 전체 결과 | Scorecard API 또는 action |
| `security-policy` | Scorecard `Security-Policy`, OSPS 취약점 신고 안내 | `SECURITY.md` 존재 |
| `actions-pinning` | Scorecard `Pinned-Dependencies`(워크플로 action) | 전체 커밋 SHA로 고정된 `uses:` 참조 |
| `sbom` | OSPS 릴리스 SBOM 기대 사항 | SBOM 생성 단계 또는 릴리스 자산 |
| `provenance` | SLSA 빌드 출처 증명 | `attest-build-provenance`, `slsa-github-generator` |
| `release-signing` | Scorecard `Signed-Releases`, Sigstore | `cosign` / 서명 자산 |

"대응"은 방향 안내이며 적합성 선언이 아닙니다. 상태는 `pass`, `fail`, `partial`, `not-run`, `not-applicable`로 `portfolio/status.schema.json`의 verification과 같은 어휘입니다. 측정하지 않은 신호는 `not-run`이며 `0`이나 `pass`로 기록하지 않습니다.

## 규칙

- `revision`은 실제 관찰한 전체 git SHA이고, `observed_at`과 `source.observed_at`은 UTC입니다.
- 타임스탬프는 유효한 UTC 일시여야 하며, `observed_at`은 미래일 수 없고 `source.observed_at`은 레코드의 `observed_at`보다 늦을 수 없습니다(`--now`로 결정적 검증).
- `fail`에는 finding, 예외, remediation 중 하나가 필요하고, `partial`에는 finding이 필요하며, `pass`에는 finding과 예외가 없고, `not-run`에는 finding도 예외도 없습니다.
- 예외와 재스캔의 `finding_ids`는 현재 유효한 finding을 가리키며 같은 레코드의 finding으로 해석되어야 합니다.
- **해결된 finding:** 개선 후 더 이상 존재하지 않는 finding은 `finding_ids`로 참조할 수 없습니다. 선택 필드 `rescan.resolved_findings[]`에 `{id, summary, resolved_by}`로 기록합니다(`resolved_by`는 수정한 PR 또는 커밋). `delta: improved`에는 항목이 하나 이상 필요하고, 그 id는 레코드의 활성 finding이나 예외와 같을 수 없으며 중복될 수 없습니다.
- `summary` 수치는 `signals`에서 파생되며 검증됩니다.
- 예외에는 `owner`, `rationale`, `expires`가 필수이고 `review_date`는 선택입니다.
- **만료 시 실패(fail-closed):** `expires`가 오늘보다 이전인 예외는 CI에서 경고가 아니라 검증 오류입니다. 새 근거로 갱신하거나 해결합니다. `--today YYYY-MM-DD`로 테스트를 결정적으로 만듭니다.
- 문자열은 비밀 패턴을 검사하며, 증거에는 참조만 두고 자격 증명은 두지 않습니다.

## 개선 후 재스캔

`resolved_findings`는 `openforge-security-readiness-evidence/v1`에 대한 추가(additive) 선택 확장이므로 스키마 버전은 그대로이며 기존 레코드는 계속 유효합니다. 새 의무는 `delta: improved`를 주장하는 레코드에만 적용되고, 이 변경 이전에 커밋된 레코드 중에는 해당하는 것이 없었습니다.

```json
"rescan": {
  "previous_ref": "<이전 revision>", "previous_observed_at": "<UTC>", "delta": "improved",
  "resolved_findings": [{"id": "narwhal-pin-1", "summary": "...", "resolved_by": "https://github.com/<owner>/<repo>/pull/<n>"}]
}
```

현재 레코드는 새 상태를 담고 수정된 항목의 finding은 두지 않으며, finding id는 `resolved_findings`로 계속 대응시킬 수 있습니다.

## Scorecard 어댑터

`templates/scripts/import-scorecard.py`는 OpenSSF Scorecard v5 원본 출력(`scorecard --format=json`)을 이 레코드로 변환합니다. 업스트림 결과를 정규화할 뿐 점검을 다시 구현하지 않습니다. **업데이트 모드**로 동작하여 기존 `portfolio/security-readiness/<repo>.json`을 다시 쓰며(스키마 버전과 스키마 모두 변경 없음), 결과가 `validate-security-readiness.py`를 통과하지 않으면 쓰기를 거부합니다. `--write` 없이 실행하면 결과만 출력하고 파일은 그대로 둡니다.

```bash
# 1. 공식 Scorecard CLI 실행(체크섬 검증한 릴리스 바이너리, GITHUB_AUTH_TOKEN은 환경에서 제공하고 커밋하지 않음)
scorecard --repo=github.com/<owner>/<repo> --format=json > portfolio/security-readiness/scorecard/<repo>.json
# 2. 드라이런 후 쓰기
python3 templates/scripts/import-scorecard.py --record portfolio/security-readiness/<repo>.json --scorecard portfolio/security-readiness/scorecard/<repo>.json
python3 templates/scripts/import-scorecard.py --write --record portfolio/security-readiness/<repo>.json --scorecard portfolio/security-readiness/scorecard/<repo>.json
# 3. 검증 및 포트폴리오 뷰 재생성
python3 templates/scripts/validate-security-readiness.py
python3 templates/scripts/generate-portfolio.py
```

원본 출력은 수정 없이 `portfolio/security-readiness/scorecard/<repo>.json`에 원천 증거로 보관합니다. `source.tool`은 `openssf-scorecard`이고 `version`, UTC `observed_at`, 정확한 명령·스캔한 커밋·원본 파일 경로·스캔 사실에 대한 SHA-256 점검 다이제스트(아래 참고)를 담은 `ref`가 함께 기록됩니다.

| Scorecard 점검(v5) | OpenForge 신호 | 적용 |
|--------------------|----------------|------|
| 모든 점검 | `scorecard` | 항상. 전체 점수가 상태를 정합니다: 모든 점검이 10이고 전체 10/10일 때만 `pass`, 0이면 `fail`, 그 외 `partial`. 10 미만인 확정 점검마다 finding `<repo>-scorecard-<check>` 하나가 생기며 심각도는 업스트림 위험 수준을 따릅니다(`Dangerous-Workflow`/`Webhooks`는 critical, 알 수 없는 새 점검은 `info`). |
| `Security-Policy` | `security-policy` | 해당 신호가 없거나 `not-run`일 때만 |
| `Pinned-Dependencies` | `actions-pinning` | 같은 규칙, Scorecard는 Actions 외 의존성도 포함 |
| `Signed-Releases` | `release-signing` | 같은 규칙, Scorecard는 provenance 파일도 인정 |
| `SBOM`(실험적, 기본 출력에 없음) | `sbom` | 같은 규칙 |
| 그 외 모든 점검 | `scorecard` finding만 | 전용 신호 없음 |
| (없음) | `provenance` | Scorecard에 대응 점검이 없어 채우지 않음 |

채워진 신호의 점검별 상태: `10` pass, `0` fail, `1-9` partial, `-1`(판정 불가) `not-run`. `-1`은 절대 `pass`가 아니며 전체 상태 판단에서 확정 점검으로 세지 않습니다. 직접 관찰한 신호(`pass`, `fail`, `partial`, `not-applicable`)는 덮어쓰지 않고 유지하며 `NOTE`를 출력합니다.

다음 경우 어댑터는 0이 아닌 종료 코드와 메시지로 실패하고 아무것도 쓰지 않습니다: Scorecard JSON이 아닌 입력, `checks` 누락 또는 빈 값, 5가 아닌 Scorecard 메이저 버전, -1..10 밖의 전체·점검 점수, `github.com/<레코드 repository>`와 다른 `repo.name`, 40자리 hex가 아닌 커밋, UTC 오프셋 없는 날짜, 중복 점검, 이미 측정된 `scorecard` 신호(재스캔 delta는 계산하지 않으므로 `rescan` 블록을 직접 추가). 유일한 예외는 동일한 입력을 다시 가져오는 경우로, `source.ref`에 저장된 점검 다이제스트가 입력의 다이제스트와 같으면 아무것도 바꾸지 않는 no-op입니다. 다이제스트가 없는 레코드는 거부합니다. 다이제스트는 전체 점수, 각 점검의 이름·점수·사유, Scorecard 버전과 실행 커밋, 스캔 날짜, 스캔한 커밋을 포함합니다.

레코드 필드: `revision`은 직접 관찰한 revision 그대로 두며, Scorecard가 스캔한 커밋은 각 `source.ref`에 있고 다를 수 있습니다. `observed_at`은 레코드에 담긴 가장 최근 관찰 시각이 됩니다.

## 포트폴리오 뷰

`python3 templates/scripts/generate-portfolio.py`는 `portfolio/dashboard.json`에 추가(additive) 최상위 키 `security_readiness`를 넣고(`openforge-dashboard/v1`과 기존 키는 변경 없음) `docs/portfolio-dashboard.md`에 "Security readiness" 섹션을 추가합니다. 저장소별로 종합 상태(`fail` > `partial`, 측정된 신호 옆의 `not-run`은 `pass`가 아니라 `partial`), 신호 상태별 개수, 원본 파일에서 읽은 Scorecard 점수·날짜·커밋, 증거 레코드와 Scorecard 원본 출력의 저장소 상대 경로를 담습니다. 레코드가 인용한 Scorecard 출력이 없거나 원본과 다르면(날짜, 버전, 스캔 커밋 또는 점검 다이제스트 불일치이므로 전체 점수나 점검 점수가 바뀌어도 빌드가 실패) 빌드가 실패합니다. 증거 디렉터리가 없으면 키를 생략합니다.

## 검증

```bash
python3 templates/scripts/validate-security-readiness.py            # portfolio/security-readiness/*.json
python3 templates/scripts/validate-security-readiness.py --today 2026-10-07 path/to/record.json
```

## 범위

첫 번째 조각은 스키마, 검증기, 테스트, 관찰된 샘플 세 개(`narwhal`, `kubemetal`, `clusterdeck`)를 정의했고, 재스캔 조각은 `rescan.resolved_findings`를 추가하고 `actions-pinning` 개선 후 `narwhal`과 `kubemetal`을 다시 관찰했습니다. Scorecard 조각은 어댑터를 추가하고, 세 샘플의 `not-run` Scorecard 신호를 실제 Scorecard v5.6.0 출력(2026-10-15 실행)으로 교체했으며, 추가(additive) 포트폴리오 요약 `security_readiness`를 도입했습니다. 다른 업스트림 도구(SBOM 생성기, Sigstore, SLSA)용 어댑터는 이번 조각에 포함되지 않습니다.
