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
- `fail`에는 finding, 예외, remediation 중 하나가 필요하고, `not-run`에는 finding이 없으며, `pass`에는 예외가 없습니다.
- `summary` 수치는 `signals`에서 파생되며 검증됩니다.
- 예외에는 `owner`, `rationale`, `expires`가 필수이고 `review_date`는 선택입니다.
- **만료 시 실패(fail-closed):** `expires`가 오늘보다 이전인 예외는 CI에서 경고가 아니라 검증 오류입니다. 새 근거로 갱신하거나 해결합니다. `--today YYYY-MM-DD`로 테스트를 결정적으로 만듭니다.
- 문자열은 비밀 패턴을 검사하며, 증거에는 참조만 두고 자격 증명은 두지 않습니다.

## 검증

```bash
python3 templates/scripts/validate-security-readiness.py            # portfolio/security-readiness/*.json
python3 templates/scripts/validate-security-readiness.py --today 2026-10-07 path/to/record.json
```

## 범위

첫 번째 조각으로 스키마, 검증기, 테스트, 관찰된 샘플 세 개(`narwhal`, `kubemetal`, `clusterdeck`)만 포함합니다. 포트폴리오 요약이나 `dashboard.json`에 준비도를 노출하는 것은 두 번째 조각으로 계획되어 있으며 `openforge-dashboard/v1` 버전 변경 없이 추가 키로 도입합니다. 업스트림 출력을 이 레코드로 자동 변환하는 어댑터는 이번 조각에 포함되지 않습니다.
