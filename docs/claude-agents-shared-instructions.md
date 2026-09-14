# Shared project instructions for Codex and Claude Code

OpenForge uses `AGENTS.md` as the canonical repository-wide instruction contract.

## Canonical layout

```text
AGENTS.md      # portable repository-wide rules (Codex reads this directly)
CLAUDE.md      # thin Claude Code adapter
```

Recommended `CLAUDE.md` baseline:

```markdown
@AGENTS.md

# Claude Code

Add only Claude Code-specific hooks, commands, harness behavior, or narrow runtime guidance here.
```

Claude Code officially supports `@path/to/import` in `CLAUDE.md`. A repository that already uses `AGENTS.md` for other coding agents can therefore import it instead of copying the same rules. The import can appear anywhere in `CLAUDE.md`; OpenForge recommends keeping it at the top for visibility and drift resistance.

Codex reads `AGENTS.md` as repository instructions and supports hierarchical instruction discovery, including more specific nested `AGENTS.md`/`AGENTS.override.md` files. Keep portable project policy in `AGENTS.md`; do not make `CLAUDE.md` the source of truth for rules that Codex or other agents also need.

## Ownership rule

- `AGENTS.md`: portable invariants, architecture/safety boundaries, canonical verification/completion expectations.
- `CLAUDE.md`: Claude Code adapter only. Import `AGENTS.md`; add only Claude-specific behavior.
- `.claude/rules/`: Claude-specific path-scoped or harness rules when required.
- `.agents/skills/`: portable task-specific workflows.
- scripts/tests/CI/policy: deterministic enforcement.

Do not copy the full contents of `AGENTS.md` into `CLAUDE.md`. Duplication creates two mutable policy owners and allows silent drift.

## Validation

A compliant repository with both files should satisfy all of the following:

1. `AGENTS.md` exists and owns the repository-wide contract.
2. `CLAUDE.md` contains an active `@AGENTS.md` import outside code fences/code spans.
3. Generic engineering policy is not duplicated in the adapter.
4. Claude-only additions do not weaken or contradict the canonical contract.
5. Repository correctness does not depend on personal `~/.claude/CLAUDE.md` state.

For large repositories, use nested `AGENTS.md` files for narrower Codex/project scope and Claude Code path-scoped `.claude/rules/` where appropriate rather than growing the root adapter.

## References

- Claude Code documentation: `CLAUDE.md` imports and the explicit `AGENTS.md` interoperability pattern.
- OpenAI Codex documentation: persistent repository context via `AGENTS.md` and hierarchical instruction discovery.
- OpenForge: `docs/model-agnostic-agent-instructions.md` and `docs/agent-skills.md`.
