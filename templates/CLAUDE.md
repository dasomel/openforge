@AGENTS.md

# Claude adapter

Keep this file limited to Claude-specific behavior. Repository-wide engineering rules belong in `AGENTS.md`; repeatable project workflows belong in project skills; deterministic checks belong in scripts/tests/CI.

Follow the model-agnostic instruction design standard when changing this adapter:
https://github.com/dasomel/openforge/blob/main/docs/model-agnostic-agent-instructions.md

## Project skill routing

- Use project-scoped skills only when their descriptions match the requested task.
- Load only the references/scripts needed for the selected workflow.
- Do not duplicate a skill workflow here.

## Claude-only integration

- Put team-lane orchestration, slash-command behavior, hooks, or Claude-specific harness instructions in `.claude/rules/` and reference them here only when needed.
- Do not require personal absolute paths or a maintainer-specific global `~/.claude/CLAUDE.md` for repository correctness.
- Do not add Claude/model-specific engineering-policy overrides unless a repeated observed failure is backed by evidence and the mitigation has a review/removal condition.
