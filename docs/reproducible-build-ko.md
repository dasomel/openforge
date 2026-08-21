# 재현 가능한 Build 표준

Release-critical build는 immutable source, dependency, toolchain input으로 재현할 수 있어야 합니다.

## Build Identity

가능한 범위에서 다음을 연결합니다.

- source commit
- dependency lock/checksum state
- compiler/interpreter/runtime version
- build tool version
- base image/builder identity
- 환경/profile
- generated input version
- resulting artifact digest

## 통제

- release-critical input을 pin합니다.
- 가능한 경우 hermetic/isolated build를 사용합니다.
- runner에 우연히 설치된 tool에 의존하지 않습니다.
- timestamp와 비결정 metadata를 가능한 경우 normalize합니다.
- 중요한 artifact는 clean build를 반복해 비교합니다.
- offline/air-gap capability를 주장하는 경우 동일 환경에서 재현합니다.
- dependency와 builder context를 재구성할 수 있는 evidence를 보존합니다.

재현 가능한 build는 process와 input의 일관성을 보여주지만 source나 dependency가 안전하다는 보장은 아닙니다. Supply-chain/security 검사를 별도로 적용합니다.
