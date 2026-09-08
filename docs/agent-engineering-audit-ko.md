# Agent Engineering Audit

OpenForge는 repository agent 지침을 두 영역으로 분리합니다.

1. formatter, linter, test, policy, build, generated-file validation이 담당해야 하는 **기계적으로 관찰 가능한 engineering control**
2. architecture boundary, high-risk path, evidence 충분성, escalation 조건 같은 **사람의 판단이 필요한 guidance**

Audit은 단순 keyword scan으로 architecture 품질이나 risk ownership을 증명했다고 간주하지 않습니다.

## 실행형 Audit

로컬 repository에 대해 실행합니다.

```bash
python3 templates/scripts/audit-agent-engineering.py --repo /path/to/repository --repository owner/name
```

출력은 `openforge-agent-audit/v1`을 사용하며 다음을 기록합니다.

- root instruction file
- 알려진 source-of-truth 문서
- 발견 가능한 build/test/lint/verify entrypoint
- repository tooling에서 확인되는 deterministic control owner
- deterministic rule과 중복될 가능성이 있는 prompt text
- false-green finding
- 명시적인 maintainer review가 필요한 judgment field

## Rule ownership

| Rule class | 권장 owner | Prompt 역할 |
|---|---|---|
| formatting / braces | formatter | 비명시적 invariant만 설명 |
| tooling이 지원하는 import order / naming | linter / compiler | 중복 지침 지양 |
| static analysis | linter / SAST | 필요한 evidence만 명시 |
| tests | test runner / CI | 필요한 evidence class 식별 |
| dependency / security policy | policy / scanner | risk와 exception boundary 설명 |
| generated-file freshness | generator `--check` / CI | source-of-truth 명시 |
| architecture boundary | human review + 가능한 targeted test | 짧고 명시적으로 유지 |
| high-risk path / destructive scope | repository policy + human review | 명시적으로 유지 |
| evidence sufficiency | CI + human judgment | unit과 real runtime evidence 구분 |

## False-green 규칙

“항상 lint/test를 실행한다” 같은 지침 자체는 executable control이 아닙니다. Repository 지침이 deterministic verification을 요구하지만 audit이 대응되는 tooling owner를 찾지 못하면 false-green finding을 보고합니다.

이 검사는 의도적으로 보수적입니다. Keyword가 발견됐다고 control이 완전하다고 주장하지 않으며, executable owner의 존재만 확인합니다. 실제 동작의 정확성은 repository-specific CI가 계속 담당합니다.

## Judgment field

다음 항목은 maintainer 또는 repository-specific policy가 근거를 제공할 때까지 `review-required`로 유지합니다.

- high-risk path
- 실제 failure path에서 bug reproduction을 자동화할 수 있는지 여부
- duplicated / obsolete prompt rule
- architecture/access-boundary guidance 품질

Dashboard를 완성해 보이게 하기 위해 이러한 항목을 임의의 점수로 변환하지 않습니다.

## Portfolio workflow

```text
repository
  -> executable audit
  -> machine-observable facts
  -> judgment field maintainer review
  -> portfolio audit record
  -> 근거가 있는 gap만 remediation issue 생성
```

이는 OpenForge #14의 executable 영역을 구현하고 #15에 필요한 reusable audit mechanism을 제공합니다. Portfolio 전체의 reviewed record는 다음 단계이며 scanner가 임의로 추론하지 않습니다.
