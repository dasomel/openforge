# GitHub 표준

OpenForge 기반 프로젝트는 협업과 변경 관리를 위한 기본 시스템으로 GitHub를 사용합니다.

## Issue

권장 유형:

- Bug
- Feature
- Architecture
- Documentation
- Dependency
- Security

큰 변경은 구현 전에 요구사항, 결정, 범위를 Issue로 기록합니다.

## Pull Request

협업이나 리뷰가 필요한 의미 있는 변경은 Pull Request를 통해 반영합니다.

PR에는 다음을 포함합니다.

- 문제와 해결 방법
- 관련 Issue
- 테스트 방법
- 필요한 문서 변경
- 집중된 commit 구성

## Branch

짧은 수명의 Branch를 권장합니다.

```text
feat/<name>
fix/<name>
refactor/<name>
chore/<name>
docs/<name>
```

## Commit

Conventional Commits를 권장합니다.

```text
feat: add unified service API
fix: handle stale metadata
chore: update dependencies
docs: add architecture guide
```
