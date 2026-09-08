# Agent Engineering Portfolio Audit Matrix

> 정확한 Git revision에 바인딩된 repository scan으로 생성합니다. 기계적으로 관찰 가능한 control은 자동 기록하고, 판단이 필요한 항목은 명시적인 review work로 남깁니다.

| Repository | Revision | Instructions | Verify / Build / Test / Lint | Deterministic controls | False-green | Manual review |
|---|---|---|---|---|---|---|
| `dasomel/narwhal` | `813ccb0cbeb7` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: —<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/narwhal-portal` | `011890f8c8c2` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: make build, npm run build<br>`test`: npm run test<br>`lint`: — | formatting, lint, tests, static-analysis, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/beluga` | `74197bde7e7f` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: —<br>`test`: make test<br>`lint`: make lint | lint, tests | 0 | 4 review-required |
| `dasomel/beluga-manager` | `7a34f33bd304` | AGENTS.md | `verify`: —<br>`build`: —<br>`test`: —<br>`lint`: — | tests | 1 | 4 review-required |
| `dasomel/kubemetal` | `fa6b60babe26` | AGENTS.md, CLAUDE.md | `verify`: make check, make verify<br>`build`: make build, npm run build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/clusterdeck` | `d5023a31b362` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build, npm run build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, generated-files | 0 | 4 review-required |
| `dasomel/ldapium` | `dfd3fbfe2b9f` | AGENTS.md, CLAUDE.md | `verify`: make check<br>`build`: —<br>`test`: —<br>`lint`: — | formatting, lint, tests, static-analysis, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/nfs-quota-agent` | `d5ba45b2e23d` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: go build ./..., make build<br>`test`: go test ./..., make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/egovframe-launcher` | `b762dabc88be` | AGENTS.md | `verify`: —<br>`build`: —<br>`test`: —<br>`lint`: — | tests | 1 | 4 review-required |
| `dasomel/kube-ready-box` | `7c62e309ebd0` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, generated-files | 0 | 4 review-required |

## 해석

- control이 탐지됐다는 것은 repository tooling에 executable owner가 존재한다는 뜻이며 모든 경로가 올바르게 검증된다는 의미는 아닙니다.
- `false-green`은 지침이 deterministic verification을 요구하지만 대응되는 executable owner를 찾지 못한 상태입니다.
- high-risk boundary, 실제 경로 bug reproduction 가능성, prompt debt, architecture guidance 품질은 keyword로 추론하지 않고 maintainer review로 남깁니다.
- 각 행은 정확한 Git commit에 바인딩되어 이후 동일 시점의 scan을 재현할 수 있습니다.
