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
5. 포트폴리오 수준 노출은 계획 단계입니다(범위 참고).

## 파일

| 경로 | 역할 |
|------|------|
| `schemas/security-readiness-evidence-v1.schema.json` | 버전 계약(`openforge-security-readiness-evidence/v1`) |
| `portfolio/security-readiness/<repo>.json` | 관찰된 증거, 저장소당 파일 하나, OpenForge에 중앙 보관 |
| `templates/scripts/validate-security-readiness.py` | 스키마 및 의미 검증, CI에서 실행 |
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

## 검증

```bash
python3 templates/scripts/validate-security-readiness.py            # portfolio/security-readiness/*.json
python3 templates/scripts/validate-security-readiness.py --today 2026-10-07 path/to/record.json
```

## 범위

첫 번째 조각은 스키마, 검증기, 테스트, 관찰된 샘플 세 개(`narwhal`, `kubemetal`, `clusterdeck`)를 정의했고, 재스캔 조각은 `rescan.resolved_findings`를 추가하고 `actions-pinning` 개선 후 `narwhal`과 `kubemetal`을 다시 관찰했습니다. 포트폴리오 요약이나 `dashboard.json`에 준비도를 노출하는 것은 두 번째 조각으로 계획되어 있으며 `openforge-dashboard/v1` 버전 변경 없이 추가 키로 도입합니다. 업스트림 출력을 이 레코드로 자동 변환하는 어댑터는 이번 조각에 포함되지 않습니다.
