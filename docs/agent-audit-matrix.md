# Agent Engineering Portfolio Audit Matrix

> Generated from revision-bound repository scans. Machine-observable controls are recorded automatically; judgment fields remain explicit review work.

| Repository | Revision | Instructions | Verify / Build / Test / Lint | Deterministic controls | False-green | Manual review |
|---|---|---|---|---|---|---|
| `dasomel/narwhal` | `1b1e5c008259` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: —<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/narwhal-portal` | `0730430d1dc4` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: make build, npm run build<br>`test`: npm run test<br>`lint`: — | formatting, lint, tests, static-analysis, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/beluga` | `6c5bdd1ad3e9` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: —<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/beluga-manager` | `0e7a49506023` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: —<br>`test`: make test<br>`lint`: make lint | lint, tests | 0 | 4 review-required |
| `dasomel/kubemetal` | `829221e8c665` | AGENTS.md, CLAUDE.md | `verify`: make check, make verify<br>`build`: make build, npm run build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/clusterdeck` | `3b7c283f408b` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build, npm run build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, generated-files | 0 | 4 review-required |
| `dasomel/ldapium` | `438e2445e00a` | AGENTS.md, CLAUDE.md | `verify`: make check<br>`build`: —<br>`test`: —<br>`lint`: — | formatting, lint, tests, static-analysis, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/nfs-quota-agent` | `60aa69a15101` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: go build ./..., make build<br>`test`: go test ./..., make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | 0 | 4 review-required |
| `dasomel/egovframe-launcher` | `73cf9225a39a` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests | 0 | 4 review-required |
| `dasomel/kube-ready-box` | `a0c8d7e63688` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, generated-files | 0 | 4 review-required |
| `dasomel/siqoq` | `b71c68fbc077` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | lint, tests | 0 | 4 review-required |

## Interpretation

- A detected control means the repository exposes an executable owner in its tooling; it does not prove that every path is correctly covered.
- `false-green` means instructions require deterministic verification but no corresponding executable owner was detected.
- High-risk boundaries, real-path bug reproduction feasibility, prompt debt, and architecture guidance quality are not inferred from keywords and remain maintainer-reviewed fields.
- Every row is bound to an exact Git commit so later reviews can reproduce what was scanned.
