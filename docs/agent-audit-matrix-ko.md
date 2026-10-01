# Agent Engineering Portfolio Audit Matrix

> 정확한 Git revision에 바인딩된 repository scan으로 생성합니다. 기계적으로 관찰 가능한 control은 자동 기록하고, 판단이 필요한 항목은 명시적인 review work로 남깁니다.

| Repository | Revision | Instructions | Verify / Build / Test / Lint | Deterministic controls | Local gate | Swallowed | False-green | Manual review |
|---|---|---|---|---|---|---|---|---|
| `dasomel/narwhal` | `6bf756eba1f1` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: —<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | no | 0 | 1 | 4 review-required |
| `dasomel/narwhal-portal` | `a37968600b97` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: make build, npm run build<br>`test`: npm run test<br>`lint`: npm run lint | formatting, lint, tests, static-analysis, security-policy, generated-files | yes | 0 | 0 | 4 review-required |
| `dasomel/beluga` | `d7436eb8faec` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: —<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | no | 0 | 1 | 4 review-required |
| `dasomel/beluga-manager` | `f25b4c96056b` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: npm run build<br>`test`: make test, npm run test<br>`lint`: make lint | lint, tests, static-analysis, security-policy, generated-files | no | 0 | 1 | 4 review-required |
| `dasomel/kubemetal` | `7269a101c01c` | AGENTS.md, CLAUDE.md | `verify`: make check, make verify<br>`build`: make build, npm run build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | no | 0 | 2 | 4 review-required |
| `dasomel/clusterdeck` | `2540f95f077f` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build, npm run build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | no | 0 | 2 | 4 review-required |
| `dasomel/ldapium` | `e2c00a46a3b9` | AGENTS.md | `verify`: make check<br>`build`: —<br>`test`: —<br>`lint`: — | formatting, lint, tests, static-analysis, security-policy, generated-files | no | 0 | 2 | 4 review-required |
| `dasomel/nfs-quota-agent` | `5d8f079cb1ca` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: go build ./..., make build<br>`test`: go test ./..., make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | no | 0 | 1 | 4 review-required |
| `dasomel/egovframe-launcher` | `638706b23120` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | no | 0 | 2 | 4 review-required |
| `dasomel/kube-ready-box` | `fbaca4bc619d` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, generated-files | yes | 0 | 0 | 4 review-required |
| `dasomel/siqoq` | `0c4ee549b2a3` | AGENTS.md | `verify`: make verify<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | lint, tests | no | 0 | 2 | 4 review-required |

## 해석

- control이 탐지됐다는 것은 repository tooling에 executable owner가 존재한다는 뜻이며 모든 경로가 올바르게 검증된다는 의미는 아닙니다.
- `false-green`은 지침이 deterministic verification을 요구하지만 대응되는 executable owner를 찾지 못한 상태입니다.
- `Local gate`는 agent instruction/skill 변경이 repository-local CI(예: `agent-contract-gate.yml`)를 실제로 실행시키는지를 나타내며, `no`는 중앙 portfolio audit가 계약 위반을 처음 발견하는 지점이 되고 있다는 뜻입니다.
- `Swallowed`는 validator가 실행되지만 종료 상태가 무조건 폐기되는 지점의 수입니다(`markdownlint ... || true` 등). `owner 존재`만으로는 충분하지 않다는 뜻이며, 정당한 사례는 `# openforge: allow-swallow` 주석으로 예외 처리합니다. `—`는 해당 revision이 탐지기 도입 이전이라 측정되지 않았다는 뜻이고 0과 다릅니다.
- high-risk boundary, 실제 경로 bug reproduction 가능성, prompt debt, architecture guidance 품질은 keyword로 추론하지 않고 maintainer review로 남깁니다.
- 각 행은 정확한 Git commit에 바인딩되어 이후 동일 시점의 scan을 재현할 수 있습니다.
