# OpenForge Agent Behaviors

Behavior specifications describe recurring conduct that should be visible across long-running agent work. They are evaluation targets, not runtime prompts.

OpenForge uses the interoperable layout:

```text
.agents/behaviors/<name>/BEHAVIOR.md
```

Each file uses YAML frontmatter with `name` and `description`. The Markdown body is intentionally flexible; OpenForge recommends the following sections where useful:

- Intent
- Evidence to inspect
- Decision
- Execution
- Recovery
- Failure modes

Behavior specs complement, but do not replace, `AGENTS.md`, skills, tests, policy-as-code, traces, or evals.

Initial reference behaviors:

- `evidence-before-claim`
- `scope-discipline`
- `bug-fix-verification`
- `task-convergence`
- `trust-and-provenance`
