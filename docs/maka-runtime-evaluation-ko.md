# OpenForge 관점의 Apache Maka Runtime 평가

Apache Maka (Incubating)의 공개 문서와 repository를 **2026-09-09** 기준으로 검토했습니다.

결론: **아키텍처 패턴은 부분 차용하되, 현재 Maka를 OpenForge 핵심 Runtime dependency로 채택하지 않습니다.**

OpenForge는 runtime/model neutral을 유지합니다. Maka는 durable event log, 단일 execution authority, workspace instructions, permission boundary, Agent Graph, declarative multi-arm evaluation 측면에서 좋은 reference implementation과 optional evaluation harness입니다.

## OpenForge와 관련된 Maka 현재 구조

Maka는 **Runtime Host**를 하나의 execution authority로 정의합니다. Desktop/TUI/CLI/bot/Eval은 client이며 Runtime Host가 Session/Turn identity, agent lifecycle, continuation, tool, permission, runtime event를 소유합니다.

Runtime Event Log는 model message, tool call/result, permission decision, termination fact의 durable source이며 UI/context/recovery는 그 projection입니다.

현재 공개 surface에는 다음이 포함됩니다.

- Desktop workspace
- interactive TUI / `maka` CLI
- non-interactive `maka run`
- `maka eval run <spec> --out <directory>`
- Agent Graph
- Read/Write/Edit/Bash/Glob/Grep 등 local tool
- permission policy, watchdog/abort/error classification
- multiple model connections
- append-only/immutable evaluation attempt와 result artifact

참고:
- https://github.com/apache/maka
- https://github.com/apache/maka/blob/main/ARCHITECTURE.md
- https://github.com/apache/maka/blob/main/docs/architecture/runtime-host-architecture.md
- https://github.com/apache/maka/blob/main/packages/cli/README.md
- https://github.com/apache/maka/blob/main/packages/eval/README.md

## OpenForge mapping

| Maka concept | OpenForge mapping | 결정 |
|---|---|---|
| Runtime Host 단일 execution authority | Agent Execution Security request/runtime authority boundary | 패턴 차용 |
| Runtime Event Log | execution evidence / behavior trace / audit lineage | 패턴 차용 |
| Workspace instructions | `AGENTS.md` + linked standards | 이미 적용 |
| Permission engine | canonical resolved invocation + authorization/approval contract | 개념 차용, 구현은 프로젝트별 |
| Agent Graph | child-agent/task decomposition | optional |
| Eval Experiment/Cell/Attempt/Result | Agent Behavior / deterministic evaluation evidence | 호환 가능 |
| Model connection catalog | provider configuration | OpenForge core 밖 |
| Desktop/TUI | developer UX | baseline dependency 아님 |

## Security boundary 평가

Maka는 OpenForge와 다음 방향에서 잘 맞습니다.

1. client마다 authority를 복제하지 않고 하나의 runtime owner를 둠
2. dangerous tool을 permission boundary로 통과시킴
3. durable execution history로 recovery/audit을 지원함
4. Eval이 두 번째 runtime authority가 되지 않음
5. remote Runtime Host profile이 target/root/credential을 명시적으로 bind함

다만 side effect가 중요한 프로젝트에서 OpenForge는 추가 보장을 요구합니다.

- authorization은 fully resolved tool/target/arguments canonical artifact를 소비해야 함
- high-risk authority는 bounded/expiring이어야 함
- 필요한 human approval은 exact invocation digest에 bind되어야 함
- executor/sandbox handoff 전 request-side deny가 가능해야 함
- command success와 post-state/effective enforcement를 구분해야 함
- 실제 mutation boundary에서 recomputable evidence가 남아야 함

따라서 Maka의 permission/runtime model은 유용한 substrate/reference이지만 자체적으로 OpenForge execution-security profile 완료를 증명하지 않습니다.

## Credential / local data 고려

Maka released CLI의 agent turn은 configured model connection을 필요로 하며 first-run setup은 provider credential을 사용합니다. 공개 문서는 local credential/profile storage와 CLI beta 상태도 명시합니다.

OpenForge는 benchmark를 위해 사용자의 interactive provider login을 자동화하거나 browser/session credential을 복사하거나 provider control을 우회하지 않습니다. Model credential은 user/runtime-owned secret입니다.

## Optional repository PoC

Maka를 필수 dependency로 추가하지 않고도 repository 단위 평가가 가능합니다.

```bash
node --version
npm install --global maka-agent@next
maka --version
```

Target repository의 clean clone에서:

```bash
maka run "Read AGENTS.md and the linked engineering standards. Review one open issue, propose the smallest coherent implementation plan, list required verification, and do not mutate files."
```

다른 configured model connection/profile로 동일 task를 반복하고 다음을 기록합니다.

- repository revision
- Maka version
- model/provider identity
- exact task text
- permission decisions
- tool calls
- result status
- duration/usage
- AGENTS/security/evidence boundary 준수 여부

정식 비교는 서로 다른 수동 session 평균보다 Maka Eval의 declarative experiment와 immutable cell attempt를 우선합니다.

## Multi-model comparison 정책

#9은 GPT / Claude / Gemini 중 2개 이상 실행 비교를 제안했습니다. 이는 여전히 유효한 **optional experiment**지만 OpenForge architecture adoption의 필수조건으로 두지 않습니다.

- model credential은 외부 user/runtime state임
- OpenForge가 provider account를 소유하지 않음
- credential-dependent ad-hoc run은 reproducible CI evidence가 아님
- OpenForge에는 이미 model-neutral Agent Behavior와 repository별 execution-security evidence가 존재함
- Maka core adoption 판단은 1회 leaderboard보다 runtime stability와 operational value에 달려 있음

Maintainer가 비교를 수행할 경우 모든 arm에 동일한 frozen task/revision/budget/verifier를 사용해야 하며 실패/unmatched cell을 조용히 제외해서는 안 됩니다.

## 지금 차용하는 것

- runtime boundary당 하나의 explicit execution authority
- append-only/recomputable execution evidence
- model/provider configuration과 repository engineering policy 분리
- workspace-level instructions
- dangerous tool effect 전 explicit permission
- 가치가 있을 때만 graph orchestration 사용
- evaluation result를 screenshot/claim이 아니라 durable evidence로 취급

## 지금 차용하지 않는 것

- Maka를 모든 generated repository의 mandatory dependency로 만들기
- Maka-specific profile/data format을 OpenForge standard로 지정
- provider credential을 OpenForge가 관리
- Desktop/TUI mandatory workflow
- Maka permission 승인만으로 project-specific privileged mutation이 충분하다고 가정
- autonomous destructive execution

## 재검토 trigger

다음 중 하나가 발생하면 더 강한 integration을 재검토합니다.

- 2개 이상의 portfolio project가 공통 persistent agent runtime을 실제로 필요로 함
- Maka가 shared operational dependency로 적합한 안정성 단계에 도달
- 현재 Agent Behavior harness로 표현하기 어려운 cross-model benchmark가 필요
- Agent Graph가 evidence/permission boundary를 약화시키지 않으면서 측정 가능한 cycle-time 개선을 제공

그 전까지의 지속 가능한 결정은 **partial architectural adoption + optional PoC, no core dependency**입니다.