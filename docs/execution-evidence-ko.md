# OpenForge 실행 증거 진단

OpenForge L2 Execution Evidence는 repository에 파일이나 설정이 존재하는지만 보는 대신, 선택된 engineering control이 실제로 실행되는지 확인합니다.

실행 진단은 명시적 opt-in입니다.

```bash
openforge . --run-execution
```

기본 진단은 계속 정적 진단이며 대상 repository의 코드를 실행하지 않습니다.

## 보안 모델

Execution probe는 OpenForge 바이너리에 포함된 신뢰 가능한 built-in probe만 사용합니다. 외부 ruleset은 shell command를 추가할 수 없습니다. 따라서 다운로드한 ruleset이나 repository-local rule이 임의 명령 실행 수단으로 바뀌는 것을 막습니다.

`--run-execution`은 명확한 trust boundary입니다. Build/test 과정은 build script, test fixture, generator, compiler plugin 등 대상 repository의 코드를 실행할 수 있으므로 신뢰하는 repository에서만 사용하고 가능하면 격리된 CI job이나 disposable environment에서 실행해야 합니다.

## 초기 프로필

`Cargo.toml`이 있는 Rust 프로젝트:

- `cargo check --all-targets --all-features`
- `cargo test --all-targets --all-features`
- `cargo clippy --all-targets --all-features -- -D warnings`

`go.mod`가 있는 Go 프로젝트:

- `go build ./...`
- `go test ./...`
- `go vet ./...`

Execution이 비활성화되어 있으면 적용 가능한 항목은 `SKIP`으로 출력하고 점수 분모에서도 제외합니다. 지원하는 실행 프로필이 감지되지 않으면 Execution finding 자체를 추가하지 않습니다.

## Evidence

각 실행 finding은 command, exit code, stdout/stderr의 제한된 마지막 부분을 evidence로 기록합니다. 성공한 probe는 `Execution` category 점수에 반영하고 실패한 probe는 해당 점수를 0으로 계산하면서 remediation을 제공합니다.

Execution evidence는 static declaration보다 강한 evidence지만 runtime verification을 대체하지 않습니다.

```text
Declared < Configured < Executed < Runtime Verified
```

다음 L3 단계에서는 Kubernetes/runtime evidence를 별도 dimension으로 추가합니다.
