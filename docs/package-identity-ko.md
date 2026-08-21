# Package 및 Artifact Identity 표준

Package name, namespace, publisher identity는 supply-chain trust model의 일부입니다.

## 위협

- typosquatting
- dependency confusion
- namespace squatting
- evil-twin package/extension
- ownership transfer
- unexpected publisher change
- suspicious low-age dependency

## 요구사항

- 신규 dependency의 source와 publisher/namespace identity를 확인합니다.
- 내부/private dependency가 public registry와 이름이 같다고 public source를 자동 선택하지 않습니다.
- ownership/namespace/publisher 변경을 security-impact change로 검토합니다.
- 가능한 경우 신규 package에 cooling/review를 적용합니다.
- immutable package identity와 integrity metadata를 기록합니다.
- release build에서는 approved registry/mirror를 우선합니다.
- known-malicious/withdrawn package를 quarantine합니다.

IDE extension, agent plugin, CLI tool도 동일한 정책을 적용합니다.
