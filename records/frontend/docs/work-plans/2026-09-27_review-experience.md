# 리뷰 경험 개선 작업 계약

- 규모 XL, frontend dev / backend dev / architecture main.
- 사용자 승인: 리뷰 품질·탐색·작업 복원 세 묶음 구현 및 재부팅 후 계속 진행.
- 범위: PR 개요/정적 분석/AI/활동 탭, 간결한 카드, 근거 코드, 개인 처리 기록, 이전 회차 비교, 로그인 목적지·동기화 복원, 멤버 식별·오류 범위·키보드.
- UI 설계: 기존 파란색 토큰 유지. 상단 탭을 고정된 탐색 기준으로 두고 질문·범위·세부 근거는 점진적으로 공개한다. 기본 텍스트 14px 이상, 320~1440 너비, 키보드 탭·화살표·Escape 지원.
- 근거: 2026-09-27 전체 점검 F01~F07 및 리뷰 품질 사용자 피드백.
- 적용 스킬: terminal-ops, ui-ux-design, vue-ui-polish
- 적용 Gate: Security Gate, UI/UX, API, 문서
- 위험: 로그인 목적지는 허용된 내부 경로만 사용. 15분 탭 저장소에 왕복 경로만 기록하며 접근 토큰 비저장. 원문 코드는 메모리·no-store로 조회. Vue 텍스트 바인딩만 사용.
- 상세 API/DB 설계: backend docs/work-plans/2026-09-27_review-experience.md 및 ADR-REVIEW-006.
- 제외: 유료 요청, GitHub 게시, 배포, 커밋·push.
- [x] 라우터·분류·비교·복원 회귀 테스트
- [x] 타입/빌드와 실제 브라우저·반응형·키보드
- [x] 보고서와 Working Context

검증 관측과 미검증 경계: [완료 보고서](../../reports/2026-09-27_review-experience_report.md). 모델 실제 품질 재평가와 피드백 동시 부하 검사는 포함하지 않는다.
