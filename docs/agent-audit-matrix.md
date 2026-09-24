# Agent Engineering Portfolio Audit Matrix

> Generated from revision-bound repository scans. Machine-observable controls are recorded automatically; judgment fields remain explicit review work.

| Repository | Revision | Instructions | Verify / Build / Test / Lint | Deterministic controls | Local gate | Swallowed | False-green | Manual review |
|---|---|---|---|---|---|---|---|---|
| `dasomel/narwhal` | `72102a7d7c70` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: —<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | no | 2 | 3 | 4 review-required |
| `dasomel/narwhal-portal` | `816e958c75e6` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: make build, npm run build<br>`test`: npm run test<br>`lint`: — | formatting, lint, tests, static-analysis, security-policy, generated-files | yes | 0 | 0 | 4 review-required |
| `dasomel/beluga` | `d7023516422f` | AGENTS.md | `verify`: —<br>`build`: —<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, security-policy, generated-files | no | 0 | 1 | 4 review-required |
| `dasomel/beluga-manager` | `df5378b0e42d` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: npm run build<br>`test`: make test, npm run test<br>`lint`: make lint | lint, tests, security-policy, generated-files | no | 0 | 1 | 4 review-required |
| `dasomel/kubemetal` | `8de686fcbf20` | AGENTS.md, CLAUDE.md | `verify`: make check, make verify<br>`build`: make build, npm run build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | no | 0 | 2 | 4 review-required |
| `dasomel/clusterdeck` | `ec0b454e3a8c` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build, npm run build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | no | 0 | 2 | 4 review-required |
| `dasomel/ldapium` | `9f033fb56ee1` | AGENTS.md | `verify`: make check<br>`build`: —<br>`test`: —<br>`lint`: — | formatting, lint, tests, static-analysis, security-policy, generated-files | no | 0 | 2 | 4 review-required |
| `dasomel/nfs-quota-agent` | `984f6f14c80f` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: go build ./..., make build<br>`test`: go test ./..., make test<br>`lint`: make lint | formatting, lint, tests, static-analysis, security-policy, generated-files | no | 0 | 1 | 4 review-required |
| `dasomel/egovframe-launcher` | `e30597f58816` | AGENTS.md, CLAUDE.md | `verify`: make verify<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests | no | 0 | 1 | 4 review-required |
| `dasomel/kube-ready-box` | `b4d3256de9c0` | AGENTS.md, CLAUDE.md | `verify`: —<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | formatting, lint, tests, generated-files | yes | 0 | 0 | 4 review-required |
| `dasomel/siqoq` | `a916914b336b` | AGENTS.md | `verify`: make verify<br>`build`: make build<br>`test`: make test<br>`lint`: make lint | lint, tests | no | 0 | 2 | 4 review-required |

## Interpretation

- A detected control means the repository exposes an executable owner in its tooling; it does not prove that every path is correctly covered.
- `false-green` means instructions require deterministic verification but no corresponding executable owner was detected.
- `Local gate` shows whether agent instruction/skill changes actually trigger a repository-local CI check (for example `agent-contract-gate.yml`); `no` means the central portfolio audit remains the first place an invalid contract is discovered.
- `Swallowed` counts validators that run but whose exit status is unconditionally discarded (`markdownlint ... || true` and similar), the second false-green class: an owner exists and its verdict is thrown away. A legitimate case is annotated with `# openforge: allow-swallow`. A `—` means the revision predates the detector and was not measured, which is not the same as zero.
- High-risk boundaries, real-path bug reproduction feasibility, prompt debt, and architecture guidance quality are not inferred from keywords and remain maintainer-reviewed fields.
- Every row is bound to an exact Git commit so later reviews can reproduce what was scanned.
