# Agent Engineering Portfolio Audit Matrix

> Generated from revision-bound repository scans. Machine-observable controls are recorded automatically; judgment fields remain explicit review work.

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

## Interpretation

- A detected control means the repository exposes an executable owner in its tooling; it does not prove that every path is correctly covered.
- `false-green` means instructions require deterministic verification but no corresponding executable owner was detected.
- High-risk boundaries, real-path bug reproduction feasibility, prompt debt, and architecture guidance quality are not inferred from keywords and remain maintainer-reviewed fields.
- Every row is bound to an exact Git commit so later reviews can reproduce what was scanned.
