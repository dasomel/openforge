# Documentation Freshness Standard

OpenForge는 문서 freshness를 나중에 처리하는 publishing 작업이 아니라 implementation evidence의 일부로 취급합니다.

## Lifecycle

```text
implementation
  -> executable evidence
  -> documentation impact review
  -> 필요한 user/operations/security docs 갱신
  -> blog/project-story impact review
  -> merge / release
```

변경이 merge되었다고 해서 planned behavior를 implemented로 설명할 수 있는 것은 아닙니다. 사용자에게 노출하는 설명은 참조하는 main/release 상태에 실제 존재하는 동작과 연결되어야 합니다.

## Status language

일반 제공 상태가 아닌 capability는 명시적인 lifecycle 용어를 사용합니다.

- `planned` — 방향은 합의됐지만 아직 구현되지 않음
- `experimental` — 평가 목적으로 구현됐으며 support contract가 안정적이지 않음
- `implemented` — 참조 main/release에 존재하고 적절한 executable evidence가 있음
- `deprecated` — 아직 존재하지만 제거/교체 예정

## Documentation-impact review가 필요한 변경

다음을 변경하면 같은 변경 단위에서 문서 영향을 검토합니다.

- 사용자 기능 또는 명령
- architecture, component ownership, data flow
- authentication, authorization, RBAC, secret, security boundary
- configuration, Helm value, flag, environment variable, API, schema
- 지원 runtime/platform/filesystem/Kubernetes version
- install, upgrade, rollback, backup, restore, incident procedure
- 외부에 드러나는 failure mode 또는 recovery
- metric이나 공개된 정량 수치

Dependency-only bump, formatting-only 변경, 외부 contract가 바뀌지 않는 internal refactor는 보통 `none`으로 선언할 수 있습니다.

## Evidence requirements

문서의 현재 기능 설명은 다음 중 하나 이상으로 확인 가능해야 합니다.

- implementation path / committed configuration
- automated test / regression test
- CI/build/package evidence
- 해당 claim에 필요한 real integration/runtime verification
- release artifact, checksum, SBOM, provenance
- 동작을 재현하는 명령

실제 cluster, filesystem, browser, identity provider, VM, hardware, external service에 의존하는 claim을 unit test만으로 증명하지 않습니다.

## Numeric / version claim

Test count, supported version, incident, compatibility, adoption metric은 가능한 한 하나의 canonical source에서 관리합니다. Generated view는 값을 prose에 반복 복사하지 않고 source를 소비해야 합니다.

중복이 불가피하면 deterministic freshness check를 추가하거나 어느 값이 authoritative한지 명확히 표시합니다.

## Blog / portfolio synchronization

`dasomel.github.io`의 project/docs/post는 downstream presentation state이며 upstream OSS repository가 implementation source of truth입니다.

다음 변경은 blog/project 갱신 후보입니다.

- 새 사용자 기능
- 중요한 architecture 변경
- 운영/incident lesson
- 새 platform/runtime/filesystem 지원
- 중요한 security/supply-chain 개선
- real runtime 또는 production-like evidence로 검증된 reusable engineering lesson

Blog는 현재 기능과 roadmap/experiment를 구분해야 하며 가능한 경우 upstream project/revision 또는 release를 기록합니다.

## PR contract

Substantive PR은 다음을 답해야 합니다.

- Documentation impact: `none`, `updated`, `follow-up-required`
- Blog / portfolio impact: `none`, `candidate`, `updated`
- 현재 상태 claim을 뒷받침하는 evidence
- 의도적으로 남긴 stale document와 tracking issue

`follow-up-required`는 조용한 예외가 아닙니다. 같은 변경에서 문서를 안전하게 갱신할 수 없는 이유와 후속 tracking 위치를 명시해야 합니다.

## Human judgment boundary

Link checker는 link가 존재함을 증명할 수 있지만 architecture 설명이 정확한지는 증명하지 못합니다. Generated version table은 copy drift를 줄일 수 있지만 migration warning이 필요한지는 판단하지 못합니다.

따라서 OpenForge는 deterministic freshness check와 의미·사용성·architecture coherence·운영 명확성에 대한 maintainer review를 분리합니다.

## Portfolio audit snapshot

Portfolio audit configuration에서 `documentation_freshness: true`를 선택한 저장소는 `docs/IMPLEMENTATION-STATUS.md`를 유지해야 합니다. Status snapshot에는 아래의 기계 검증 가능한 형식이 필요합니다.

```text
Last verified: YYYY-MM-DD against `main`.
```

Auditor는 `(?m)^Last verified:[ \t]+(?P<date>\d{4}-\d{2}-\d{2})[ \t]+against[ \t]+`main`\.?[ \t]*$`를 사용하고 `date`를 ISO calendar date로 검증합니다. 파일과 날짜가 있는 `main` 바인딩만 검사하며, 이 표준은 freshness interval을 정의하지 않으므로 경과 시간만으로 semantic accuracy, blog 동기화, stale 여부를 추론하지 않습니다.
