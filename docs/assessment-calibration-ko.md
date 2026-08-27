# Assessment Calibration

OpenForge Calibration은 프로젝트 점수를 임의의 기대값에 맞추는 기능이 아니라, **진단 규칙 자체의 품질**을 실제 프로젝트 증거와 비교해 검증하는 기능입니다.

## 왜 Calibration이 필요한가

결정론적인 규칙도 실제 프로젝트에서는 잘못 판단할 수 있습니다. Calibration은 결과를 다음과 같이 구분합니다.

- `true_finding` — 보고된 FAIL이 실제 성숙도 Gap입니다.
- `false_positive` — 탐지 범위가 좁거나 불완전해서 발생한 오탐입니다.
- `not_applicable` — 해당 프로젝트/Profile에는 적용하면 안 되는 규칙입니다.
- `accepted` — PASS 결과가 검토된 증거와 일치하며 규칙 수정이 필요하지 않습니다.

Calibration Report는 Classification Coverage와 Failure Precision을 제공해 규칙 보정을 감이 아니라 증거로 수행하도록 합니다.

분류와 Assessment 상태의 일관성도 검증합니다. `true_finding`과 `false_positive`는 `FAIL`, `accepted`는 `PASS`여야 하며, `not_applicable`은 잘못 적용된 `FAIL` 또는 이미 보정된 `NOT_APPLICABLE` 상태에서 사용할 수 있습니다.

## 실행 흐름

먼저 진단 결과를 생성합니다.

```bash
openforge assess ../narwhal \
  --profile kubernetes-platform \
  --format json \
  --output narwhal-assessment.json
```

그 다음 실제 증거를 사람이 확인한 항목만 expectation으로 기록합니다.

```json
{
  "project": "dasomel/narwhal",
  "profile": "kubernetes-platform",
  "expectations": {
    "DOC-001": {
      "classification": "accepted",
      "rationale": "Canonical README가 존재하고 충분한 내용을 포함한다."
    }
  }
}
```

Calibration을 실행합니다.

```bash
openforge calibrate \
  narwhal-assessment.json \
  examples/calibration/narwhal.json
```

자동화에서는 JSON을 사용할 수 있습니다.

```bash
openforge calibrate \
  narwhal-assessment.json \
  examples/calibration/narwhal.json \
  --format json \
  --output narwhal-calibration.json
```

`--require-complete`는 **실제 점수 계산에 참여하는 PASS/FAIL 규칙** 가운데 미분류 항목이 있으면 exit code `2`를 반환합니다. `SKIP`, `NOT_APPLICABLE`, `WAIVED` 등 비점수 finding은 inactive로 보고되지만 Coverage 분모에는 포함하지 않습니다.

## 지표

`classification_coverage_percent`는 다음 비율입니다.

```text
분류 완료된 활성 PASS/FAIL rule / 전체 활성 PASS/FAIL rule
```

`failure_precision_percent`는 다음과 같습니다.

```text
true_findings / (true_findings + false_positives)
```

`inactive_rules`는 현재 Assessment에서 점수화되지 않은 finding 수입니다. 감사 가능성을 위해 Report에는 유지하지만 활성 규칙 Coverage와 섞지 않습니다.

추측으로 높은 Coverage를 만드는 것보다 검증된 낮은 Coverage가 더 가치 있습니다.

## 첫 Reference: Narwhal

`examples/calibration/narwhal.json`을 첫 Reference Calibration Manifest로 사용합니다. `Calibration` GitHub Actions Workflow는 OpenForge와 Narwhal을 함께 checkout하고 `kubernetes-platform` static assessment를 실행한 뒤 검토된 expectation을 적용하며, 현재는 모든 활성 static rule의 분류 완료를 Gate로 검증합니다. 두 JSON report는 workflow artifact로 저장합니다.

첫 Narwhal 실행에서는 프로젝트 Gap이 아니라 진단기 Gap도 실제로 발견됐습니다. Shell 기반 regression test가 `CI-002`에서 인식되지 않았고, `gitops/` manifest가 `PLT-002~005` 검색 경로에서 빠져 있었으며, README badge와 문서 screenshot이 Web Application image asset으로 점수화되고 있었습니다. 이 사례들은 regression test로 고정해 같은 오탐이 다시 생기지 않도록 했습니다.

Runtime rule은 실제 cluster evidence가 확보되기 전까지 static calibration 범위에 포함하지 않습니다.

## 규칙 개선 Loop

```text
실제 프로젝트
    ↓
assessment
    ↓
증거 검토
    ↓
calibration classification
    ↓
false-positive / applicability 분석
    ↓
작은 rule 수정 + regression test
    ↓
재진단
```

OpenForge 점수를 높이기 위해 대상 프로젝트를 억지로 수정해서는 안 됩니다. 규칙이 잘못됐다면 OpenForge 규칙을 고치고, 프로젝트에 실제 Gap이 있다면 finding을 유지한 채 프로젝트 개선을 별도로 진행합니다.
