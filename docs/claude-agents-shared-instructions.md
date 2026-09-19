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

Claude Code v2.1.277 added native `AGENTS.md` support, but its release contract is a **fallback**: when a project has no `CLAUDE.md`, Claude Code reads `AGENTS.md` instead. When both files exist, do not assume Claude Code also loads `AGENTS.md`. A dual-file repository should therefore keep the explicit `@AGENTS.md` import at the top of `CLAUDE.md`.

This makes the OpenForge layout intentionally asymmetric: `AGENTS.md` is the shared contract; `CLAUDE.md` is optional. Keep `CLAUDE.md` only when Claude-specific hooks, commands, rules, harness behavior, or compatibility guidance is actually needed. If no Claude-specific adapter is needed, remove `CLAUDE.md` and let Claude Code v2.1.277+ fall back to `AGENTS.md` directly. Bedrock, Vertex, and Foundry were excluded from the initial v2.1.277 AGENTS.md support, so repositories that must support those runtimes should retain the explicit adapter until their support is verified.

`.claude/` and `.agents/` are not treated as interchangeable directories. Keep portable Agent Skills/workflows under `.agents/`; keep Claude-only commands, hooks, rules, agents, and runtime configuration under `.claude/`.

Codex reads `AGENTS.md` as repository instructions and supports hierarchical instruction discovery, including more specific nested `AGENTS.md`/`AGENTS.override.md` files. Keep portable project policy in `AGENTS.md`; do not make `CLAUDE.md` the source of truth for rules that Codex or other agents also need.

## Ownership rule

- `AGENTS.md`: portable invariants, architecture/safety boundaries, canonical verification/completion expectations.
- `CLAUDE.md`: optional Claude Code adapter. If present, import `AGENTS.md`; add only Claude-specific behavior. Remove it when there is no Claude-only content and all supported Claude runtimes can use the native fallback.
- `.claude/rules/`: Claude-specific path-scoped or harness rules when required.
- `.agents/skills/`: portable task-specific workflows.
- scripts/tests/CI/policy: deterministic enforcement.

Do not copy the full contents of `AGENTS.md` into `CLAUDE.md`. Duplication creates two mutable policy owners and allows silent drift.

## Validation

A compliant repository with both files should satisfy all of the following:

1. `AGENTS.md` exists and owns the repository-wide contract.
2. If `CLAUDE.md` exists, it contains an active `@AGENTS.md` import outside code fences/code spans; if it does not exist, the repository has no required Claude-only instructions and its supported Claude runtime set is verified to use the native `AGENTS.md` fallback.
3. Generic engineering policy is not duplicated in the adapter.
4. Claude-only additions do not weaken or contradict the canonical contract.
5. Repository correctness does not depend on personal `~/.claude/CLAUDE.md` state.

For large repositories, use nested `AGENTS.md` files for narrower Codex/project scope and Claude Code path-scoped `.claude/rules/` where appropriate rather than growing the root adapter.

## References

- Claude Code documentation: `CLAUDE.md` imports and the explicit `AGENTS.md` interoperability pattern.
- OpenAI Codex documentation: persistent repository context via `AGENTS.md` and hierarchical instruction discovery.
- OpenForge: `docs/model-agnostic-agent-instructions.md` and `docs/agent-skills.md`.
