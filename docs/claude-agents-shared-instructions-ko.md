# Codex와 Claude Code의 프로젝트 공통 지침 관리

OpenForge는 `AGENTS.md`를 저장소 전역 공통 지침의 단일 기준으로 사용합니다.

## 표준 구조

```text
AGENTS.md      # 이식 가능한 저장소 공통 규칙(Codex가 직접 읽음)
CLAUDE.md      # 얇은 Claude Code 어댑터
```

권장 `CLAUDE.md` 기본형:

```markdown
@AGENTS.md

# Claude Code

Claude Code 전용 hook, command, harness 동작 또는 좁은 런타임 지침만 여기에 추가합니다.
```

Claude Code는 `CLAUDE.md`의 `@path/to/import` 구문을 공식 지원합니다. 따라서 다른 코딩 에이전트를 위해 이미 `AGENTS.md`를 사용하는 저장소에서는 동일 규칙을 복사하지 않고 import할 수 있습니다. import는 `CLAUDE.md` 어디에 있어도 동작하지만, OpenForge는 가시성과 drift 방지를 위해 파일 상단에 두는 방식을 권장합니다.

Codex는 `AGENTS.md`를 저장소 지침으로 읽으며 더 구체적인 하위 `AGENTS.md`/`AGENTS.override.md`를 포함한 계층적 지침 탐색을 지원합니다. 여러 에이전트가 함께 사용하는 프로젝트 정책은 `AGENTS.md`에 두고, Codex에도 필요한 규칙의 기준을 `CLAUDE.md`로 만들지 않습니다.

## 소유권 규칙

- `AGENTS.md`: 공통 불변조건, 아키텍처/보안 경계, 검증·완료 기준.
- `CLAUDE.md`: Claude Code 어댑터만 담당. `AGENTS.md`를 import하고 Claude 전용 동작만 추가.
- `.claude/rules/`: 필요한 경우 Claude 전용 경로별 규칙이나 harness 지침.
- `.agents/skills/`: 이식 가능한 작업별 워크플로.
- scripts/tests/CI/policy: 결정론적으로 검증 가능한 규칙의 실행 소유자.

`AGENTS.md` 전체 내용을 `CLAUDE.md`에 복사하지 않습니다. 복사는 동일 정책의 수정 가능한 소유자를 두 개 만들고 조용한 drift를 허용합니다.

## 검증 기준

두 파일을 모두 사용하는 저장소는 다음을 만족해야 합니다.

1. `AGENTS.md`가 존재하고 저장소 공통 계약을 소유합니다.
2. `CLAUDE.md`에 코드 블록/코드 스팬 밖의 실제 `@AGENTS.md` import가 존재합니다.
3. 공통 엔지니어링 정책을 어댑터에 중복 작성하지 않습니다.
4. Claude 전용 추가 지침은 canonical 계약을 약화하거나 모순시키지 않습니다.
5. 저장소의 정상 동작이 개인 `~/.claude/CLAUDE.md`에 의존하지 않습니다.

대규모 저장소에서는 루트 어댑터를 계속 키우기보다 더 좁은 범위의 nested `AGENTS.md`와 Claude Code의 path-scoped `.claude/rules/`를 사용합니다.

## 관련 문서

- Claude Code 공식 문서: `CLAUDE.md` import 및 `AGENTS.md` 상호운용 패턴.
- OpenAI Codex 공식 문서: `AGENTS.md` 기반 지속 컨텍스트와 계층적 지침 탐색.
- OpenForge: `docs/model-agnostic-agent-instructions.md`, `docs/agent-skills.md`.
