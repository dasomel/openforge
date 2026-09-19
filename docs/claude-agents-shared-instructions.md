# Shared project instructions for Codex and Claude Code

OpenForge uses `AGENTS.md` as the canonical **portable baseline**, not as the only instruction file.

> Compatibility note (2026-09): Claude Code 2.1.277-era tooling can consume the shared `AGENTS.md` contract. That interoperability does **not** mean `CLAUDE.md`, `.claude/`, and `.agents/` should be collapsed into one structure. OpenForge deliberately preserves a shared baseline plus harness-specific overlays.

## Canonical layout

```text
AGENTS.md      # portable repository-wide baseline shared by Codex/Claude-capable harnesses
CLAUDE.md      # Claude Code overlay/adapter; may import AGENTS.md for compatibility
.agents/       # portable skills/behaviors and cross-harness workflows
.claude/       # Claude-specific agents, rules, hooks, commands, settings, team/model routing
```

Recommended `CLAUDE.md` baseline:

```markdown
@AGENTS.md

# Claude Code

Add only Claude Code-specific hooks, commands, subagent/team routing, harness behavior,
permission/runtime guidance, or narrow compatibility overrides here.
```

If the installed Claude Code version reads `AGENTS.md` directly, the import is a compatibility adapter rather than a reason to duplicate policy. Repositories may keep it while supporting mixed versions; removing it is a repository-level migration decision and must not silently drop the portable baseline for older/other harnesses.

## Why the files remain separate

Codex and Claude Code share many repository invariants, but their harnesses are not identical.

- Shared architecture, safety boundaries, source-of-truth rules, and completion expectations belong in `AGENTS.md`.
- Claude subagents, hooks, commands, permission behavior, model/team routing, and Claude-only runtime conventions belong in `CLAUDE.md` or `.claude/`.
- Portable task workflows that can be replayed by multiple harnesses belong in `.agents/skills/` or other OpenForge portable contracts.
- Deterministic rules belong in scripts/tests/CI/policy, not in either prompt file.

Therefore **do not symlink `CLAUDE.md` to `AGENTS.md` when meaningful Claude-specific behavior exists**, and do not migrate `.claude/` into `.agents/` merely because both harnesses understand `AGENTS.md`.

## Ownership rule

- `AGENTS.md`: portable baseline — invariants, architecture/safety boundaries, canonical verification/completion expectations.
- `CLAUDE.md`: Claude Code overlay/adapter. It may import `AGENTS.md`; keep Claude-specific behavior here.
- `.claude/rules/`, `.claude/agents/`, `.claude/hooks/`, `.claude/commands/`, settings: Claude-specific harness assets.
- `.agents/skills/` and portable behaviors: cross-harness task workflows.
- scripts/tests/CI/policy: deterministic enforcement.

Do not copy the full contents of `AGENTS.md` into `CLAUDE.md`. Separation means **shared baseline + distinct overlay**, not two independent copies of the same rules.

## Validation

A compliant repository should satisfy all of the following:

1. `AGENTS.md` exists and owns the portable repository-wide baseline.
2. Claude-specific rules remain separately owned by `CLAUDE.md`/`.claude/`; they are not forced into the portable contract.
3. If `CLAUDE.md` imports `AGENTS.md`, the adapter does not duplicate the baseline.
4. If a repository removes the import because its minimum Claude Code version reads `AGENTS.md` directly, CI/audit evidence must prove both shared baseline loading and Claude-specific overlay loading before the migration is considered complete.
5. Claude-only additions do not weaken or contradict the portable baseline.
6. Repository correctness does not depend on personal `~/.claude/CLAUDE.md` state.
7. `.claude/` and `.agents/` are not treated as interchangeable directories.

For large repositories, use nested `AGENTS.md` for portable scope and Claude path-scoped `.claude/rules/` where appropriate rather than growing one universal instruction file.

## Portfolio decision

OpenForge's default is intentionally conservative:

**Keep `AGENTS.md` + `CLAUDE.md`/`.claude/` separate. Share the common baseline; preserve harness-specific structure.**

This allows Codex and Claude Code to converge on common project policy without pretending that their orchestration, subagent, permission, hook, and runtime semantics are identical.

## References

- Claude Code 2.1.277 bundled CLI version is published in Anthropic's Agent SDK.
- Claude Code supports project-scoped subagents under `.claude/agents/`; those remain Claude-specific harness assets.
- OpenForge: `docs/model-agnostic-agent-instructions.md` and `docs/agent-skills.md`.
