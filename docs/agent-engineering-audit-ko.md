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

### 두 가지 false-green 유형

Owner가 없을 수도 있고, owner가 있는데 무시될 수도 있습니다. 초록색 빌드가 가장 잘 숨기는 쪽은 후자입니다.
`markdownlint ... || true`는 validator를 실행하고 오류를 출력한 뒤에도 성공으로 보고합니다. Narwhal의 Markdown
job이 정확히 그랬지만 이 matrix는 해당 repository의 false-green을 0으로 기록했고, 그것이 두 번째 detector를
만든 이유입니다.

이제 audit은 두 유형을 모두 보고하며, 무력화된 명령을 `swallowed_failures`에, 정확한 개수를
`swallowed_failure_count`에 기록합니다. Portfolio matrix의 `Swallowed` 열이 그 수를 보여주고, `—`는 해당
revision이 detector 도입 이전이라 측정되지 않았다는 뜻이며 0과 다릅니다.

탐지 대상: `|| true`, `|| :`, `|| exit 0`, `-`로 시작하는 make recipe, `continue-on-error: true`가 설정된
step 또는 job, 그리고 validator에 `set +e`가 적용된 상태에서 종료 상태를 한 번도 읽지 않는 경우입니다.

스캔 대상 표면: GitHub Actions workflow(`.github/workflows/*.yml`), Makefile, shell script, 루트 agent
instruction 파일(`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `CODING_STANDARDS.md`), Agent Skills
(`.agents/skills/` 또는 `.claude/skills/` 아래의 `SKILL.md`), 그리고 agent command recipe
(`.claude/commands/*.md`, `.agents/commands/*.md`)입니다. 마지막 항목은 repository가 skill 밖에 두는
agent-facing 검증 recipe로, SKILL.md와 같은 방식으로 스캔됩니다 — 코드 펜스 안쪽만 보므로, anti-pattern을
설명하는 prose는 스스로를 오탐하지 않습니다.

### `|| true`를 금지하지 않는 이유

`grep ... || true`는 올바른 사용입니다. grep의 non-zero exit은 "일치 없음"이라는 데이터이지 판정이 아닙니다.
따라서 detector는 관용구가 아니라 *프로그램*을 분류하며, 그 표의 포함 기준은 "non-zero exit이 코드에 대한
판정인가"입니다. 정리·탐색용 명령(`rm`, `docker rm`, `kubectl delete`, `curl`, `find`)은 보고하지 않고,
표에 없는 프로그램도 보고하지 않습니다.

이 비대칭은 의도된 것입니다. 놓친 finding의 비용은 보고되지 않은 false-green 하나지만, false positive는
downstream repository에 "이 matrix는 noise"라고 가르쳐 이후의 모든 finding을 잃게 만듭니다. 확장해야 할
부분은 validator 표입니다.

추가 예외 두 가지: 이미 감지된 실패 이후에만 실행되는 블록(`if [ $? -ne 0 ]`, `trap` handler,
`if: failure()` step) 안의 명령은 진단이지 무력화가 아니며, 해당 줄이나 바로 윗줄의
`# openforge: allow-swallow` 주석은 의도적 예외를 표시합니다. 주석에는 *이유*를 남겨 다음 사람이 침묵이
아니라 근거를 물려받게 하십시오.

이 도구는 shell parser가 아니라 heuristic scanner입니다. 줄 구조와 알려진 명령 형태를 읽습니다. third-party
action(`uses:`)으로 실행되는 validator는 분류하지 않으며, 변수로 런타임에 조립되는 명령도 해석하지 못합니다.
알려진 한계 두 가지가 더 있습니다: pipeline의 *소비자* 자리에 있는 validator(`find . -name '*.sh' | xargs
shellcheck || true`)는 분류되지 않는데, 분류가 pipeline의 첫 명령인 `find`를 기준으로 실행되어
`shellcheck`에는 닿지 않기 때문입니다. 또한 코드 펜스 밖 Markdown prose로 적힌 무력화된 validator는 스캔되지 않습니다 — 이는
의도된 것으로, "never write `shellcheck ... || true`"처럼 anti-pattern을 설명하는 prose가 보고되어서는 안
되며, 펜스 안쪽만 보는 방식이 그것을 안전하게 만듭니다. 루트 `package.json`의 `scripts` 값도 같은 방식으로
스캔되지만, `pyproject.toml`과 `Cargo.toml`은 의도적으로 스캔하지 않습니다 — 그 build/test 항목은
`scripts` 값과 달리 인라인 shell 한 줄이 아니기 때문입니다.

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
