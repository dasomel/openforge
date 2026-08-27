# AGENTS.md

OpenForge defines reusable engineering standards. Read `README.md`, the relevant standard in `docs/`, templates affected by the change, and the issue/spec before editing.

- Make the smallest coherent change that solves the requested problem.
- Do not auto-fix unrelated findings; report them separately.
- Preserve the separation between declarative standards, executable checks, and human-judgment guidance.
- Do not add a prose rule to AGENTS/CODING_STANDARDS when formatter/linter/test/policy can enforce it reliably; prefer executable enforcement.
- Avoid vendor-specific agent behavior in canonical standards unless it is explicitly scoped as an example or integration note.
- Treat template changes as portfolio-wide API changes: consider downstream repositories and backward compatibility.
- Comments and guidance explain why, invariants, risks, and trade-offs rather than restating obvious behavior.
- For bugs in templates/scripts, prefer reproduce -> failing test/evidence -> minimal fix -> same test passes -> regression checks.
- Do not claim completion without stating the checks run and their scope.
- End substantive work as A) complete/verified, B) meaningful verified progress with the next blocker isolated, or C) stop with evidence when further work requires unjustified scope, fragile patches, unsupported assumptions, or unacceptable risk.

Detailed standard: `docs/agent-engineering.md`
