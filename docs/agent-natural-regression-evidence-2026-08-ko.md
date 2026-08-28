# 자연 발생 Agent Behavior 회귀 차단 증거 — 2026-08

## 상태

OpenForge에서 synthetic fixture가 아닌 실제 저장소 실패가 Behavior 회귀로 변환되어 merge 전에 차단된 첫 사례를 확보했습니다.

- 저장소: `dasomel/narwhal`
- Operational PR: `#173`
- 실패 커밋: `bb81d27b5187dcba736f8ed032f0ff4360e3353c`
- 수정 커밋: `2ed07160014a1bb97c0c0d783101d0fa2b0a11b6`

## 실제 실패

Narwhal의 기존 Version Check에서 실제 source-of-truth drift가 발견됐습니다.

- `VERSIONS.md`: Kubernetes `1.35.5`
- `Vagrantfile`: Kubernetes `1.35.7`

이 실패는 회귀 테스트를 위해 인위적으로 만든 negative fixture가 아니라 기존 repository CI에서 실제 발생하던 문제입니다.

## Live evidence binding

버전 일관성 검증을 하나의 deterministic command로 추출하고 전용 Version Check와 Agent Behavior가 같은 명령을 사용하도록 했습니다.

`bind-agent-verification.py`는 실제 명령을 실행한 뒤 strict trace의 verification event에 다음 observable evidence를 기록합니다.

- `status: passed|failed`
- `commandExitCode`
- `runtime:command-exit-<code>`

명령이 실패해도 binder 자체의 도구 오류로 숨기지 않습니다. 실패 결과를 구조화된 evidence로 기록하고 strict evaluator가 최종 정책 판정을 내립니다.

## 실제 Behavior regression

실패 커밋 `bb81d27...`에서 다음 흐름이 실행됐습니다.

1. 실제 버전 일관성 명령이 exit code `1` 반환
2. strict trace의 verification이 `status=failed`로 hydration
3. trusted baseline과 현재 trace 비교
4. 다음 세 Behavior가 실제 `true -> false` 회귀로 판정
   - `bug-fix-verification`
   - `evidence-before-claim`
   - `task-convergence`
5. Agent Behavior workflow가 merge 전에 실패

이는 지금까지 의도적으로 기다려 온 핵심 증거입니다. synthetic fixture나 governance-tool 자체 구현 버그가 아니라 일반 repository maintenance에서 발생한 실제 실패가 Behavior gate까지 전달됐습니다.

## 수정

Narwhal Kubernetes source-of-truth를 repository에서 실제 검증한 runtime pin `1.35.7`에 맞췄습니다. 동일한 shared command가 이후 `passed`를 기록하며, evaluator나 baseline을 낮추지 않고 같은 gate가 통과해야 합니다.

## 의미

이제 다음 운영 체인이 end-to-end executable 상태입니다.

`실제 repository check -> command exit status -> strict trace -> Behavior outcome -> baseline comparison -> merge gate`

Hidden reasoning, chain-of-thought, 고객 데이터나 secret은 필요하지 않습니다. 명시적인 command result와 repository-scoped evidence만 사용합니다.

## AGENT-005 판단

이번 한 건만으로 AGENT-005를 canonical metric으로 승격하지 않습니다.

기존에 부족했던 natural regression criterion은 충족했지만 portfolio compliance로 승격하려면 최소 한 개 다른 도메인에서 live evidence binding의 portability를 추가로 확인하는 편이 안전합니다. KubeMetal의 native/runtime 검증 또는 nfs-quota-agent의 filesystem/quota 검증이 다음 후보입니다.

현재 상태는 **승격 증거 1/2**로 기록합니다.
