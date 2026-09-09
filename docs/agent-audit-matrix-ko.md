# Agent Engineering Portfolio Audit Matrix

> 정확한 Git revision에 바인딩된 repository scan으로 생성합니다. 기계적으로 관찰 가능한 control은 자동 기록하고, 판단이 필요한 항목은 명시적인 review work로 남깁니다.

| Repository | Revision | Instructions | Verify / Build / Test / Lint | Deterministic controls | False-green | Manual review |
|---|---|---|---|---|---|---|
| `dasomel/narwhal` | `1b1e5c008259` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: —<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/narwhal-portal` | `316617dbed28` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: make build, npm run build<br>`test`: npm run test<br>`lint`: — | formatting, lint, tests, static-analysis, security-policy, generated-files | 1 | 4 review-required |
| `dasomel/beluga` | `6c5bdd1ad3e9` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: —<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/beluga-manager` | `3fd29f6a3b51` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: —<br>`test`: —<br>`lint`: — | tests | 1 | 4 review-required |
| `dasomel/kubemetal` | `829221e8c665` | AGENTS.md, CLAUDE.md | `verify`: make check, make verify<br>`build`: make build, npm run build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/clusterdeck` | `3b7c283f408b` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build, npm run build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, generated-files | 0 | 4 review-required |
| `dasomel/ldapium` | `438e2445e00a` | AGENTS.md, CLAUDE.md | `verify`: make check<br>`build`: —<br>`test`: —<br>`lint`: — | formatting, lint, tests, static-analysis, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/nfs-quota-agent` | `60aa69a15101` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: go build ./..., make build<br>`test`: go test ./..., make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | 1 | 4 review-required |
| `dasomel/egovframe-launcher` | `0d0ceae70b31` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build<br>`test`: make test<br>`lint`: — | formatting, tests | 1 | 4 review-required |
| `dasomel/kube-ready-box` | `a0c8d7e63688` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, generated-files | 0 | 4 review-required |
| `dasomel/siqoq` | `b71c68fbc077` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | lint, tests | 0 | 4 review-required |

## 해석

- control이 탐지됐다는 것은 repository tooling에 executable owner가 존재한다는 뜻이며 모든 경로가 올바르게 검증된다는 의미는 아닙니다.
- `false-green`은 지침이 deterministic verification을 요구하지만 대응되는 executable owner를 찾지 못한 상태입니다.
- high-risk boundary, 실제 경로 bug reproduction 가능성, prompt debt, architecture guidance 품질은 keyword로 추론하지 않고 maintainer review로 남깁니다.
- 각 행은 정확한 Git commit에 바인딩되어 이후 동일 시점의 scan을 재현할 수 있습니다.
