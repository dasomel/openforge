# Security 및 Supply-Chain Incident Response 표준

Compromised dependency, artifact, credential, workflow 또는 maintainer account가 의심되면 사실 확인 전까지 supply-chain incident로 취급합니다.

## 대응 lifecycle

```text
Detect
→ Contain
→ Quarantine
→ Revoke/Rotate
→ Blast Radius 확인
→ Rebuild
→ Verify
→ Recover
→ Notify
→ Regression Control 추가
```

## 최소 대응

1. 영향 version/artifact promotion을 중지합니다.
2. dependency, artifact, workflow, credential을 quarantine합니다.
3. 노출 가능 credential, 특히 publish/cloud identity를 revoke/rotate합니다.
4. 영향을 받은 commit, build, release, downstream consumer를 찾습니다.
5. last-known-good dependency/artifact를 복원합니다.
6. clean approved environment에서 rebuild합니다.
7. artifact identity, provenance, SBOM, security result를 검증합니다.
8. 증적을 남기고 detection/regression control을 추가합니다.

Emergency release는 reason, scope, risk, owner/reviewer, verification evidence, rollback plan이 있어야 routine cooling을 예외 처리할 수 있습니다.
