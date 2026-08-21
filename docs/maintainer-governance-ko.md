# OSS Maintainer Governance 표준

OpenForge는 단독 maintainer와 multi-maintainer 프로젝트를 모두 지원합니다. 사람 수를 기준으로 한 강제 요건이 작은 OSS의 운영 장벽이 되어서는 안 됩니다.

## 1. Maintainer 모델

프로젝트는 최소한 다음을 문서화해야 합니다.

- 현재 repository owner/maintainer
- merge 권한 주체
- 필요 시 release/package publish 권한 주체
- security report contact
- recovery/contact 경로

단독 maintainer는 정상적으로 허용되는 프로젝트 상태입니다.

## 2. 위험 기반 review

Review 요구 수준은 maintainer 수가 아니라 변경 위험도로 결정합니다.

| 변경 | 기본 통제 |
|---|---|
| 문서만 변경 | 자동 CI; 프로젝트 정책상 self-review 허용 |
| 저위험 code/test 변경 | CI + 프로젝트 정책에 따른 maintainer review |
| dependency/runtime/toolchain 변경 | CI + dependency/change-impact 증적 |
| `.github/workflows`, OIDC, publishing, security/IAM 변경 | 다른 qualified reviewer가 있으면 강화 review 권장; 단독 maintainer라면 명시적 self-approval + 자동 security gate + 예외 기록 |
| 긴급 보안 변경 | emergency path + 가능한 경우 사후 독립 review |

## 3. 2인 review

High-impact change의 2인 승인은 **권장 통제**이며 모든 프로젝트에 대한 강제 요건이 아닙니다.

활성 maintainer가 한 명뿐이면:

- mandatory automated checks 적용
- 다른 qualified contributor가 있을 때 CODEOWNERS/보호 경로 사용
- change classification과 impact analysis 명시
- release/security evidence 생성
- 가능한 경우 high-impact release의 staged rollout 적용
- 긴급 변경 후 retrospective review 수행

## 4. Maintainer 계정 보안

단독 프로젝트라도 다음을 권장합니다.

- MFA/passkey
- 가능한 경우 short-lived credential
- GitHub 최소 권한
- release/publish credential 분리
- protected release branch/tag
- 비공개 security reporting
- credential recovery 문서화

## 5. Succession / Recovery

영구적인 두 번째 maintainer를 요구하지 않고도 repository ownership, package publishing, release credential을 복구할 수 있는 절차를 문서화하는 것을 권장합니다.

## 6. Governance 원칙

목표는 **가능한 경우 독립된 통제력을 확보하는 것**이며 인위적인 인력 요건을 만드는 것이 아닙니다.

```text
small project
→ strong automation
→ explicit risk classification
→ protected security-sensitive paths
→ independent review when available
```
