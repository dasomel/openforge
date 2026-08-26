# OpenForge OSS 디자인 시스템

OpenForge 디자인 시스템은 모든 OSS를 똑같이 보이게 만드는 UI 테마가 아니라, **공통 Engineering 품질과 상호작용 의미를 표준화하면서 프로젝트별 성격을 유지하기 위한 계약**입니다.

**Figma 원본:** https://www.figma.com/design/Y1JpRSOwctAKSwPjDNbe1g

## 1. 목표

- Semantic Color, Spacing, Radius, Typography, State, Focus, Accessibility 표준화
- Platform Portal, Desktop Operator, Operations Dashboard, Admin Console, Data Control Plane, Developer Tool 간 패턴 재사용
- Accent, Density, Navigation, Visualization은 프로젝트 특성에 맞게 제한적으로 차별화
- Figma Token과 코드의 CSS Variable 및 `DESIGN.md`를 연결하여 Design-to-Code 추적성 확보

## 2. 핵심 원칙

1. **장식보다 명확성** — 상태, 영향, 다음 행동을 먼저 보여줍니다.
2. **업무 특성에 따른 밀도** — 하나의 Density를 강제하지 않습니다. Desktop Operator는 더 조밀하고 Portal은 더 많은 문맥을 제공합니다.
3. **Semantic 일관성** — Success, Warning, Serious, Danger, Info, Focus, Selected, Disabled의 의미를 OSS 전체에서 통일합니다.
4. **Accessibility 기본 적용** — Keyboard, Focus, Contrast, 비색상 상태 표현을 Release Gate로 봅니다.
5. **Progressive Disclosure** — YAML, Log, Raw ID, Topology Detail, Advanced Option은 필요할 때 노출합니다.
6. **OSS 친화적 Handoff** — Token은 코드와 연결하고 예외는 문서화합니다.

## 3. Foundation

### Semantic Color

컴포넌트에서 Raw Hex를 직접 사용하는 대신 다음 역할을 사용합니다.

- `color/bg/canvas`, `surface`, `subtle`, `inverse`
- `color/text/primary`, `secondary`, `muted`, `inverse`
- `color/border/default`
- `color/action/primary`, `hover`
- `color/focus/ring`
- `color/status/success`, `warning`, `serious`, `danger`, `info`

Figma Semantic Color는 Light/Dark Mode를 지원합니다. Web 구현에서는 `--of-*` CSS Custom Property로 연결하거나 기존 프로젝트 Token이 이를 Alias하도록 합니다.

### Spacing / Radius

Spacing 기준: `4, 8, 12, 16, 24, 32, 48, 64px`

Radius 기준: `6, 10, 14, 20px`, full/pill

기본 Layout은 8px Rhythm을 사용하고 Icon/Text처럼 매우 가까운 관계에서 4px을 사용합니다. 운영용 Desktop/Table UI는 Portal보다 의도적으로 조밀하게 구성할 수 있습니다.

### Typography

- Display 40/48 Bold
- H1 28/36 Semi Bold
- H2 22/30 Semi Bold
- Body 14/21 Regular
- Small 12/18 Regular
- Label 12/16 Medium

Path, YAML, Command, Raw Byte, DN, Resource ID 등 기술 식별자는 Monospace 사용을 권장합니다.

### Data Visualization

- Categorical: Blue → Green → Pink → Amber
- Magnitude: Sequential Blue
- Status Color는 상태 표현 전용이며 일반 Chart Series 색으로 재사용하지 않습니다.
- Chart도 UI와 동일한 Surface/Text Semantic을 사용하며 색상만으로 정보를 전달하지 않습니다.

## 4. 공통 컴포넌트

Figma에 1차 공통 계약을 구현했습니다.

- **Button** — Primary / Secondary / Danger × Default / Disabled
- **Status Badge** — Healthy / Warning / Serious / Critical / Info
- **Stat Tile** — 핵심 수치 + Label + Limit/Remaining Context
- **Data Row** — Identifier → State → Quantity → Recency/Action

각 OSS가 다른 Framework로 구현하더라도 Intent와 State의 의미는 유지합니다.

## 5. 공통 패턴

### Resource Explorer
Sidebar → Filter/Search → Resource Table → Detail Drawer

### Topology & Dependency
Health Summary → Graph → Selected Detail → Events/Logs. Graph만 제공하지 않고 List/Detail 대안을 유지합니다.

### Operator Dashboard
Hero Metrics → Capacity/State → Ranked Resources → Trends. 사용량과 함께 Remaining/Limit를 제공하여 사용자가 직접 계산하지 않게 합니다.

### Guided Workflow
Prerequisite → Configuration → Execution → Progress → Recovery. 장시간 작업은 Log, Retry/Cancel, 복구 방법을 제공합니다.

### Desktop Control Surface
Compact Sidebar/Toolbar → Focused Workspace → Status Footer. Keyboard, Split View, Native Dialog, Local Action Safety를 우선합니다.

## 6. 프로젝트별 가이드

### Narwhal — Platform Portal
Multi-cluster 문맥, Topology/Health, Role-aware Action, YAML/Log Progressive Disclosure. Portal 수준의 Comfortable Density를 사용합니다.

### Beluga Manager — Data Control Plane
Pipeline, Data Asset, Service, Operations 중심 IA. 서비스 간 관계가 핵심이며 추론된 관계는 확정 사실처럼 표시하지 않습니다. 전문 작업은 Upstream OSS UI로 Context를 유지해 연결합니다.

### ClusterDeck — Desktop Operator
macOS/Desktop에 맞춘 Compact Density, Keyboard-first, Persistent Cluster Context, Split View를 사용합니다. Web Portal처럼 과도한 여백을 사용하지 않습니다.

### KubeMetal — Desktop ML Infrastructure
Hardware/Runtime 상태를 명확히 표시하고 설치/학습/서빙 등의 긴 Workflow에서 Progress, Log, Recovery를 핵심으로 합니다.

### ldapium — Admin Console
Form/Table 품질을 우선하고 DN/Identifier는 Monospace로 표현합니다. Bulk Action과 Delete는 명확한 대상 및 영향 확인이 필요합니다.

### NFS Quota Agent — Operations Dashboard
기존 `DESIGN.md`의 Metrics-first 방향을 유지합니다. Self-contained UI, Capacity+Remaining, Status와 Chart Palette 분리, Dense Resource Table을 표준에 반영합니다.

### eGovFrame Launcher — Developer Tool
Wizard/Checklist, Prerequisite Validation, Command/Log Transparency, Copy 가능한 해결 방법을 제공합니다. 완료 화면은 다음 개발 행동을 명확히 안내합니다.

## 7. Accessibility Release Gate

- 일반 텍스트 Contrast 4.5:1 이상, Large Text 3:1 이상
- Keyboard만으로 전체 기능 사용 가능
- 명확한 Focus Indicator
- 상태는 Color-only 금지
- Persistent Form Label과 해결 가능한 Error Message
- Destructive Action은 대상과 결과 명시
- Reduced Motion 존중
- Dense Table에서도 Header/Sort/Focus/Truncation Recovery/Copy 지원

## 8. 적용 절차

1. 기존 Project Token을 OpenForge Semantic Role에 Mapping
2. 프로젝트 `DESIGN.md`에 Archetype 선언
3. 공통 Interaction/State Semantic 적용
4. Accent, Density, Navigation, Data Visualization을 프로젝트 특성에 맞게 적용
5. 의도적인 예외는 이유와 Accessibility 영향을 기록
6. Review에서 Light/Dark, Keyboard/Focus, Status, Loading/Error/Empty/Disabled 상태 확인

## 9. Design Review Checklist

- [ ] Ad-hoc Color 대신 Semantic Token 사용
- [ ] 지원하는 경우 Light/Dark 검토
- [ ] Keyboard/Focus 검토
- [ ] Status에 비색상 Cue 존재
- [ ] Loading/Empty/Error/Success/Disabled 상태 정의
- [ ] Destructive Action의 영향 명확
- [ ] 긴 Resource ID에서도 Table 사용 가능
- [ ] Project Archetype 및 예외 문서화
- [ ] Figma와 구현 코드의 추적성 유지
