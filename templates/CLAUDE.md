@AGENTS.md

# Claude adapter

Keep this file limited to Claude-specific behavior. Repository-wide engineering rules belong in `AGENTS.md`; repeatable project workflows belong in project skills; deterministic checks belong in scripts/tests/CI.

## Project skill routing

- Use the repository's project-scoped skills when their descriptions match the requested task.
- Do not duplicate a skill workflow here.

## Claude-only integration

- Put team-lane orchestration, slash-command behavior, hooks, or Claude-specific harness instructions in `.claude/rules/` and reference them here only when needed.
- Do not require personal absolute paths or a maintainer-specific global `~/.claude/CLAUDE.md` for repository correctness.
