# AGENTS.md

OpenForge defines reusable engineering standards. Inspect the issue/spec and repository guidance relevant to the current task before editing; load detailed standards, templates, and references only when they are needed.

- Make the smallest coherent change that solves the requested problem.
- Do not auto-fix unrelated findings; report them separately.
- Preserve the separation between declarative standards, executable checks, and human-judgment guidance.
- Prefer formatter/linter/test/policy enforcement over prose when a rule can be enforced reliably.

## Instruction routing

- `AGENTS.md` is the canonical portable repository contract. Claude Code adapters import it with `@AGENTS.md` and keep only Claude-specific integration below that import.
- Keep canonical guidance model-agnostic; tool/model-specific files are thin adapters that do not duplicate this contract, unless measured failure evidence justifies a narrow compatibility override.
- Load detailed documents and skills only when they are relevant to the current task.
- Deterministic requirements belong in scripts, tests, linters, policy, or CI when they can be enforced reliably.
- Treat template changes as portfolio-wide API changes: consider downstream repositories and backward compatibility.
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

Classify non-trivial work with `docs/change-management.md`. A Change Package fixes requirements, acceptance scenarios, tasks, verification, rollback/recovery and expected evidence.

- Class A documentation-only changes use the Issue/PR as the change record.
- Class B internal behavior changes require explicit acceptance criteria; use a Change Package when the work is complex, cross-component, or operationally risky.
- Class C dependency/runtime/toolchain/build-contract changes and Class D release/deployment/security-boundary changes require an accepted Change Package before broad implementation.
- For Class C/D or complex Class B work, follow `docs/change-management.md` and use `templates/change/CHANGE.md` plus `templates/change/TASKS.md` when a versioned working artifact is useful.
- Keep requirement → acceptance scenario → task → evidence traceability. Material scope changes require package update and re-review.
- At completion, synchronize durable truth into code/tests, normative docs, ADRs, evidence, and portfolio/status records; do not maintain a duplicate long-lived specification tree.
