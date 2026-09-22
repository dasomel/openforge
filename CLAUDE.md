@AGENTS.md

> OpenForge retains this adapter as the reference example for repositories that need Claude-specific integration; downstream repositories without a real Claude-specific delta should rely on native `AGENTS.md` fallback instead.

# OpenForge Claude adapter

Repository-wide engineering rules are canonical in `AGENTS.md`. Keep this file limited to Claude Code-specific integration guidance; do not duplicate portable policy here.

## Claude Code

- Use project skills and references only when their trigger/scope matches the task.
- Keep deterministic validation in scripts/tests/CI rather than restating it here.
- Put Claude-only hooks, commands, or harness behavior under `.claude/` when needed.
- Do not require maintainer-global `~/.claude/CLAUDE.md` state for repository correctness.

Canonical instruction design:
- `docs/model-agnostic-agent-instructions.md`
- `docs/agent-skills.md`
