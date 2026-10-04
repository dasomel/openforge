# Agent Engineering Portfolio Audit Matrix

> Generated from revision-bound repository scans. Machine-observable controls are recorded automatically; judgment fields remain explicit review work.

| Repository | Revision | Instructions | Verify / Build / Test / Lint | Deterministic controls | Local gate | Swallowed | False-green | Manual review |
|---|---|---|---|---|---|---|---|---|
| `dasomel/narwhal` | `c4080aa76f49` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: —<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | no | 2 | 3 | 4 review-required |
| `dasomel/narwhal-portal` | `c0f03fb89844` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: make build, npm run build<br>`test`: npm run test<br>`lint`: npm run lint | formatting, lint, tests, static-analysis, security-policy, generated-files | yes | 0 | 0 | 4 review-required |
| `dasomel/beluga` | `6d0111e37d1a` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: —<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | no | 0 | 1 | 4 review-required |
| `dasomel/beluga-manager` | `bcc97a5f66b5` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: npm run build<br>`test`: make test, npm run test<br>`lint`: make lint | lint, tests, static-analysis, security-policy, generated-files | no | 0 | 1 | 4 review-required |
| `dasomel/kubemetal` | `4e48a5e2a67a` | AGENTS.md, CLAUDE.md | `verify`: make check, make verify<br>`build`: make build, npm run build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | no | 0 | 2 | 4 review-required |
| `dasomel/clusterdeck` | `2540f95f077f` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build, npm run build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | no | 0 | 2 | 4 review-required |
| `dasomel/ldapium` | `593c1d218ecc` | AGENTS.md, CLAUDE.md | `verify`: make check<br>`build`: —<br>`test`: —<br>`lint`: — | formatting, lint, tests, static-analysis, security-policy, generated-files | no | 0 | 2 | 4 review-required |
| `dasomel/nfs-quota-agent` | `e9e9ad6a323f` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: go build ./..., make build<br>`test`: go test ./..., make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | no | 0 | 1 | 4 review-required |
| `dasomel/egovframe-launcher` | `638706b23120` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | no | 0 | 2 | 4 review-required |
| `dasomel/kube-ready-box` | `5e1c467ff1b6` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, generated-files | yes | 0 | 0 | 4 review-required |
| `dasomel/siqoq` | `82112116609f` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | lint, tests | no | 0 | 2 | 4 review-required |

## Interpretation

- A detected control means the repository exposes an executable owner in its tooling; it does not prove that every path is correctly covered.
- `false-green` means instructions require deterministic verification but no corresponding executable owner was detected.
- `Local gate` shows whether agent instruction/skill changes actually trigger a repository-local CI check (for example `agent-contract-gate.yml`); `no` means the central portfolio audit remains the first place an invalid contract is discovered.
- `Swallowed` counts validators that run but whose exit status is unconditionally discarded (`markdownlint ... || true` and similar), the second false-green class: an owner exists and its verdict is thrown away. A legitimate case is annotated with `# openforge: allow-swallow`. A `—` means the revision predates the detector and was not measured, which is not the same as zero.
- High-risk boundaries, real-path bug reproduction feasibility, prompt debt, and architecture guidance quality are not inferred from keywords and remain maintainer-reviewed fields.
- Every row is bound to an exact Git commit so later reviews can reproduce what was scanned.
