# AGENTS.md

OpenForge defines reusable engineering standards. Inspect the issue/spec and repository guidance relevant to the current task before editing; load detailed standards, templates, and references only when they are needed.

- Make the smallest coherent change that solves the requested problem.
- Do not auto-fix unrelated findings; report them separately.
- Preserve the separation between declarative standards, executable checks, and human-judgment guidance.
- Prefer formatter/linter/test/policy enforcement over prose when a rule can be enforced reliably.

## Instruction routing

- `AGENTS.md` is the canonical portable repository contract.
- Load detailed documents and `.agents/skills/` only when they are relevant to the current task; do not preload them by default.
- Tool-specific adapters must contain only runtime-specific behavior and must not duplicate this contract.
- Deterministic requirements belong in scripts, tests, linters, policy, or CI when they can be enforced reliably.

- Keep canonical guidance model-agnostic; tool/model-specific files are thin adapters unless measured failure evidence justifies a narrow compatibility override.
- Use `AGENTS.md` as the canonical portable repository contract. Claude Code adapters should import it with `@AGENTS.md` instead of copying shared rules; keep only Claude-specific integration below that import.
- Treat template changes as portfolio-wide API changes: consider downstream repositories and backward compatibility.
- Classify non-trivial work with `docs/change-management.md`. Class C/D and complex Class B work require an accepted Change Package that fixes requirements, acceptance scenarios, tasks, verification, rollback/recovery and expected evidence before broad implementation.
- For bugs in templates/scripts, prefer reproduce -> failing test/evidence -> minimal fix -> same evidence passes -> relevant regression checks.
- Preserve reproducible, privacy-safe engineering measurements during normal development according to `docs/research-evidence.md`; prefer structured machine-generated evidence and retain failures as well as successes.
- Run verification appropriate to the change's risk and user impact. Safe local build/test/fix/retest work within the requested scope may proceed without repeated approval.
- Do not claim completion without stating the checks run and their scope.
- End substantive work as A) complete/verified, B) meaningful verified progress with the next blocker isolated, or C) stop with evidence when further work requires unjustified scope, fragile patches, unsupported assumptions, or unacceptable risk.

Detailed standards:
- `docs/agent-engineering.md`
- `docs/model-agnostic-agent-instructions.md`
- `docs/claude-agents-shared-instructions.md`
- `docs/research-evidence.md`


## Risk-scaled change workflow

- Class A documentation-only changes use the Issue/PR as the change record.
- Class B internal behavior changes require explicit acceptance criteria; use a Change Package when the work is complex, cross-component, or operationally risky.
- Class C dependency/runtime/toolchain/build-contract changes and Class D release/deployment/security-boundary changes require an accepted Change Package before broad implementation.
- For Class C/D or complex Class B work, load `.agents/skills/change-package-workflow/SKILL.md` and use `templates/change/CHANGE.md` plus `templates/change/TASKS.md` when a versioned working artifact is useful.
- Keep requirement → acceptance scenario → task → evidence traceability. Material scope changes require package update and re-review.
- At completion, synchronize durable truth into code/tests, normative docs, ADRs, evidence, and portfolio/status records; do not maintain a duplicate long-lived specification tree.
