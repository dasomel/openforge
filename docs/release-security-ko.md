# Release 보안 표준

Release는 build와 distribution 사이의 별도 trust boundary입니다.

```text
Source
→ Build
→ Test
→ Security Gate
→ Artifact Freeze
→ Approval
→ Publish
→ Post-publish Verify
→ Monitor
```

## 요구사항

- build identity와 publish identity를 분리합니다.
- untrusted 또는 일반 CI job에서 직접 publish하지 않습니다.
- publish 전 exact artifact digest를 freeze합니다.
- 가능한 경우 publish 직전 artifact identity를 재검증합니다.
- registry가 지원하면 staged publishing/approval 기능을 우선합니다.
- release branch/tag와 publishing configuration을 보호합니다.
- published artifact가 승인된 artifact와 동일한지 검증합니다.
- last-known-good release와 rollback 절차를 유지합니다.
- compromised release의 quarantine/revocation 절차를 정의합니다.
- source, dependency, builder, artifact, approver를 연결하는 release evidence를 기록합니다.

## Trust 제한

- signature는 artifact가 benign하다는 증명이 아닙니다.
- provenance는 source/behavior가 의도되었다는 증명이 아닙니다.
- SBOM은 malware absence의 증명이 아닙니다.
- CI 성공은 release 안전성의 증명이 아닙니다.

이 정보들은 publish policy 판단을 위한 evidence이며 자동 publish authorization 자체가 아닙니다.
