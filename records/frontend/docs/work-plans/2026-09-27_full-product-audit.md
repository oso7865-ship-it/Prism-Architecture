# PRism 전체 기능·UI/UX 재점검 작업 계약

- 날짜: 2026-09-27
- 규모: L / 제품 코드 읽기 전용 감사
- 대상: backend dev 1f9f298, frontend dev fda82a5, architecture main c9275e6
- 목표: 로그인, 홈, 팀, 저장소, PR, 정적 분석, AI 리뷰 흐름의 실제 동작과 반응형·접근성 문제를 재현하고 우선순위를 정한다.
- 수정 대상: 점검 기록, 검증 증거, Working Context. 제품 코드 수정·배포·Git 커밋/push는 범위 밖이다.
- 제외: 신규 유료 AI 요청, 실제 멤버 권한 변경/초대 발송/저장소 해제, 공개 HTTPS 배포, 다른 사용자 계정의 실제 로그인.
- 근거: 현재 소스, 새 브라우저 관찰과 원본 캡처, 격리된 prism_test DB 테스트. 이전 실행 결과는 이번 PASS 증거로 사용하지 않는다.
- 적용 스킬: terminal-ops, vue-ui-polish, browser-qa, verification-loop
- 화면 감사에는 외부 product-design:audit도 적용한다.
- 적용 Gate: UI/UX P0–P6, 기능/API·인증·권한 회귀 검증. DB Gate 적용 제외: 스키마·명세 변경 없이 기존 격리 테스트 fixture만 실행한다. 감사 산출물 완료와 제품의 미해결 결함을 별도로 판정한다.
- 위험도: 읽기/화면 조작 LOW, 격리 테스트 DB 검증 MEDIUM. 실제 로컬 DB의 데이터 삭제 없음.
- 확인 문서: AGENTS, PROJECT_HARNESS context, QUICK_REF, GateGuard §6-1, 최신 보고서와 Working Context, Vue 감사 참고 문서, browser-qa, verification-loop, product-design 감사 프레임워크.

## 시나리오

- [x] A01 로그인·로그아웃·보호 경로·복귀 — 로그인 성공, 목적지 복원 결함 F01
- [x] A02 홈과 메뉴, 연결 상태 — 실제 API/DB 확인
- [x] A03 팀 선택·팀 설정·폼 검증 — 실제 팀 1개, 사용자 조회 성공. 다인원 변경은 격리 테스트/소스 검토
- [x] A04 저장소 선택·PR 목록·검색/상태 필터·빈 결과 — 조직30/개인1개, 동기화 상태 복원 F02
- [x] A05 PR 상세·뒤로/앞으로·새로고침·GitHub 활동 — 실제 커밋 조회, 나머지 종류는 자동 테스트 범위
- [x] A06 정적 분석 이력·중요도 필터·범위 표시 — 새 분석13파일/11발견 포함
- [x] A07 AI 기존 결과·동의와 한도·근거·과거 결과 호환 — 유료 호출0
- [x] A08 320/375/414/768/1440 너비·키보드·포커스·콘솔 — 실제 기기/200% 확대/스크린리더 미실행
- [x] A09 frontend 테스트·타입/빌드, backend 전체 격리 DB 테스트 — 51/225 PASS, native3회 경고·확장 lint5건 실패
- [x] A10 문제 재현과 소스 위치·개선 우선순위·검증 제한 보고 — reports/2026-09-27_full-product-audit_report.md

스크린샷은 workspace 루트의 `audit-artifacts/2026-09-27/`에 저장한다. 로딩/크기 변경 전 프레임은 증거로 채택하지 않고 저장된 이미지를 직접 확인한다. 체크 완료는 감사 수행을 뜻하며 제품 결함 해결을 뜻하지 않는다.
