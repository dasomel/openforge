# AGENTS.md

OpenForge defines reusable engineering standards. Inspect the issue/spec and repository guidance relevant to the current task before editing; load detailed standards, templates, and references only when they are needed.

- Make the smallest coherent change that solves the requested problem.
- Do not auto-fix unrelated findings; report them separately.
- Preserve the separation between declarative standards, executable checks, and human-judgment guidance.
- Prefer formatter/linter/test/policy enforcement over prose when a rule can be enforced reliably.
- Keep canonical guidance model-agnostic; tool/model-specific files are thin adapters unless measured failure evidence justifies a narrow compatibility override.
- Treat template changes as portfolio-wide API changes: consider downstream repositories and backward compatibility.
- For bugs in templates/scripts, prefer reproduce -> failing test/evidence -> minimal fix -> same evidence passes -> relevant regression checks.
- Run verification appropriate to the change's risk and user impact. Safe local build/test/fix/retest work within the requested scope may proceed without repeated approval.
- Do not claim completion without stating the checks run and their scope.
- End substantive work as A) complete/verified, B) meaningful verified progress with the next blocker isolated, or C) stop with evidence when further work requires unjustified scope, fragile patches, unsupported assumptions, or unacceptable risk.

Detailed standards:
- `docs/agent-engineering.md`
- `docs/model-agnostic-agent-instructions.md`
