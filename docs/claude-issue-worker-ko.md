# Claude 이슈 worker: WIF 시범 변경 패키지

상태: Draft, Class D(CI 쓰기 권한·외부 모델 인증). 활성화 전 검토한다. OpenForge 한 저장소만 대상이며 downstream 표준·템플릿은 변경하지 않는다.

목표: 관리자가 지정한 이슈 하나를 수동 실행으로 처리해 최소 수정·실제 테스트·Draft PR을 남기고 merge 권한은 사람에게 유지한다.

## 설정

Claude Console Workload identity에 issuer https://token.actions.githubusercontent.com 등록. audience https://api.anthropic.com, subject repo:dasomel/openforge:ref:refs/heads/main으로 제한하고 규칙/서비스 계정을 사용할 workspace에 연결한다. 저장소 Actions 변수 ANTHROPIC_FEDERATION_RULE_ID와 ANTHROPIC_ORGANIZATION_ID를 지정한다. ANTHROPIC_SERVICE_ACCOUNT_ID와 ANTHROPIC_WORKSPACE_ID는 필요시 지정한다. 식별자는 비밀 키가 아니다. workflow에 정적 API/OAuth 키를 추가하지 않는다.

검토·merge 뒤 ai-ready 라벨을 생성하고 좁은 이슈에 붙여 Claude issue worker (WIF)를 수동 실행한다. 처음 100개 후보 중 가장 오래된 하나를 선택한다. 대상이 없으면 모델 호출이 없다. 기존 worker PR이 있으면 중복 제안을 막고 다른 이슈로 진행하려면 라벨을 제거한다. 실패 시 브랜치/라벨이 남을 수 있으므로 재실행 전에 확인한다.

## 영향과 경계

- 소스/런타임/빌드/릴리스: 앱 코드·기존 명령은 변경 없음. 새 Ubuntu Actions job은 SHA 고정 공식 Claude Action을 실행하며 Action이 자체 Bun/Claude runtime을 설치한다.
- CI/보안: 읽기 전용 선택 job과 저장소 쓰기·id-token 권한 worker를 분리한다. GitHub runner의 gh CLI를 사용하며 시범 실행에서 버전을 확인한다. 생산 자격증명·공유 배포·workflow/auth 변경·자동 merge/close는 모델에 허용하지 않는다.
- 문서: 영문/한국어 패키지에 설정·합격 기준·위험·rollback 기록.
- 폐쇄망/downstream: 선택적 온라인 workflow이며 기본 scanner/air-gap 산출물/downstream template 변경 없음.

## 합격 기준과 증거

- [x] actionlint 문법·표현식 검사 통과.
- [x] Python tests 289개 OK(7.961s), agent-skills strict/instruction-debt audits 0 findings, exit 0.
- [ ] 설계 패키지 검토, WIF 식별자와 subject 제한 확인.
- [ ] ai-ready 없는 실행에서 모델 미호출 확인.
- [ ] 좁은 이슈 하나의 인증·실제 테스트·최대 한 개 Draft PR 생성 확인.
- [ ] 실제 run URL/token 비용/CI 상태 기록. 미확인 증거는 unknown.

## 위험과 rollback

20턴/$2 CLI budget/25분은 시범 제한이며 계정 지출 강제 상한이 아니다. Console workspace limit과 auto-reload OFF를 별도로 설정한다. 이 Action의 Max 혜택 크레딧 적용은 미확인이다. 이슈 텍스트는 비신뢰 입력이며 prompt 제한은 강제 sandbox가 아니다. worker에는 저장소 쓰기 권한이 있다. GITHUB_TOKEN 생성 PR은 보통 PR CI를 자동 호출하지 않으므로 수동 검증 또는 후속 제한된 GitHub App token 구성이 필요하다. 실제 증거 없이 merge하지 않는다. 저장소 Actions의 PR 생성 권한이 필요하다. 라벨 제거는 모델 완료에 의존한다. workflow 비활성/삭제 및 federation rule 폐기로 중단하고 생성된 브랜치는 따로 점검한다.
