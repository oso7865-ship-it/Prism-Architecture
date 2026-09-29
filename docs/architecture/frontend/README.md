# Frontend: 화면·API·로그인 경계

> ID: `FRONTEND` · 소유: `frontend` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 화면·프론트 API·Cookie 프록시를 변경할 때

[ADR-DEPLOY-009](../adr/deployment/ADR-DEPLOY-009-public-images.md)에 따라 Vue 3 + TypeScript + Vite + Vue Router를 유지하고 같은 EC2의 Caddy에서 빌드된 정적 파일을 제공한다. 프론트·백엔드 운영 배포, 실제 GitHub 로그인, 공개 GHCR/OIDC/SSM 자동배포를 완료했다. [최종 검증 기록](../../../records/2026-09-30_full-ec2-release.md)이 실제 확인 범위와 후속을 소유한다.

```text
frontend/src/
├─ app/                 router·앱 초기화
├─ features/
│  ├─ auth/
│  ├─ workspace/
│  ├─ repository/
│  ├─ pull-request/
│  ├─ analysis/
│  └─ review/
└─ shared/
   ├─ api/              HTTP client·오류 변환·refresh single-flight
   ├─ ui/               도메인 중립 표시 컴포넌트
   └─ types/            기술 공통 타입
```

각 feature에는 `api.ts`, `types.ts`, `components/`, `views/`를 필요한 만큼 둔다. 다른 feature의 내부 Store를 직접 수정하지 않는다. WorkspaceRole은 workspace feature 소유로 유지하고 사용 횟수 때문에 shared로 이동하지 않는다.

## 화면 흐름

로그인 → Workspace 선택 → 저장소 연결/목록 → PR 목록/상세 → 분석 접수 → 상태/검사 범위 → Finding 상세 → 선택적 AI 설명. GitHub 기존 리뷰와 우리 분석/AI 결과는 다른 영역으로 표시한다.

PENDING/RUNNING 중에는 3초 간격 상태 조회를 기본으로 하고 오류/대기 장기화 시 backoff한다. 탭이 숨겨지거나 terminal 상태가 되면 멈춘다. 서버를 깨워두기 위한 인위적 상시 polling은 만들지 않는다. WebSocket/SSE는 MVP 필수 기능이 아니다.

리뷰 이력 또는 팀이 바뀌면 열려 있던 파일별 코드 선택을 초기화한다. 문서 인용은 팀/저장소/문서/버전/섹션을 하나의 요청 키로 취급하고, 키 변경이나 컴포넌트 종료 후 늦게 도착한 응답은 버린다. 문서 본문을 편집하면 이전 섹션 연결을 무효화하되 규칙 값은 보존하고, 새 미리보기의 섹션에 명시적으로 다시 연결해야 저장할 수 있다.

## API 프록시

브라우저는 동일 출처 `/api/v1/...`를 호출하고 Caddy가 EC2의 `127.0.0.1:8000` 백엔드로 경로를 보존해 전달한다. API/health는 SPA fallback보다 먼저 분리하며 백엔드 오류를 HTML 200으로 변환하지 않는다.

OAuth Callback도 고정된 프론트 출처의 `/api/v1/auth/github/callback`을 프록시한다. Refresh 쿠키에는 backend 도메인을 Domain으로 지정하지 않는다. Set-Cookie 전달, path, Secure, SameSite, redirect, Origin 검증은 실제 배포 환경에서 확인한다. Preview URL마다 운영 OAuth callback을 넓게 허용하지 않는다.

인증/API 응답은 `Cache-Control: private, no-store`로 응답하고 Caddy 오류 응답도 no-store다. 팀 데이터가 다른 사용자에게 캐시로 재사용되지 않는지 두 계정으로 테스트한다. GitHub Webhook은 프론트가 아니라 AWS 백엔드의 직접 `/webhooks/github`로 보낸다.

## 금지와 표시 기준

GitHub Secret·LLM key·Refresh 원문을 localStorage 또는 프론트 env에 넣지 않는다. 버튼 숨김은 인가가 아니다. 모든 최종 권한은 백엔드가 검사한다.

외부 PR 본문/코멘트/AI 설명의 HTML은 그대로 실행하지 않는다. AI OFF·데이터 오래됨·PARTIAL·NONE·지원하지 않는 언어·재시도 대기를 명확히 표시한다. COMPLETED/Finding 0을 '이 코드는 안전하다'로 표시하지 않는다.

필수 E2E: 로그인과 refresh, 타 Workspace 접근 거부, PR 동기화 실패 표시, 분석 202 이후 polling, 부분 검사 표시, AI 실패 분리, CDN cache 비공유, 악성 Markdown/HTML 렌더링.

## 배포 설정 구현

[ADR-DEPLOY-009](../adr/deployment/ADR-DEPLOY-009-public-images.md)의 동일 출처 HTTPS 계약을 따른다. frontend deployment/Caddyfile은 API/health 프록시, SPA fallback, no-store와 보안 헤더를 제공한다. 숨김 파일/소스맵은 404이며 없는 정적 자원도 HTML로 대체하지 않는다. 해시 자원은 immutable 캐시, HTML은 재검증한다. Vercel CI를 EC2 자동배포로 교체했다. 실제 main CI가 게시한 정적 OCI 이미지의 파일을 원자적으로 배포하고 외부 해시·SPA·ready를 검사했다. 운영 OAuth 로그인과 쿠키 Secure/HttpOnly/SameSite=Lax/host-only 및 CSRF 거부를 확인했다. 두 계정 격리와 운영 PR 전체 흐름 검증은 이번 결과에 포함하지 않는다.

## 리뷰 탐색과 복원 (ADR-REVIEW-006)

PR 상세는 query.tab=overview/static/ai/activity로 복원한다. 키보드 화살표/Home/End, 선택 탭의 aria-selected를 제공한다. 결함·검토 질문은 별도 개수이며 긴 근거·원문·처리 기록은 펼쳐 확인한다. 기존 basis 없는 결과는 질문 영역에 보존한다.
로그인 복귀는 /app, /app/team, /app/repositories 내부 경로만 허용한다. query와 초대 fragment를 보존하며 OAuth 왕복 목적지는 탭 sessionStorage에 15분간 저장 후 성공/로그아웃에 삭제한다. 접근·refresh 토큰은 저장하지 않는다. 저장소 사용 불가 브라우저에서는 OAuth 왕복 복원이 제한된다. 새로고침 시 최신 서버 동기화 상태를 읽는다.

PR 상세 탭은 한눈에 보기 / 코드 점검 / 코드 리뷰 / 취약점 / 팀 규칙 / 변경 기록이다. 기존 tab=ai 링크는 코드 리뷰로 유지한다. 취약점은 보안 규칙 목록+전용 AI 검토, 팀 규칙은 문서 기반 AI 검토+결정적 규칙 결과+고정 버전 출처 열람이다. 저장소의 팀 문서 관리는 별도 패널로 열며, 문서 등록 자체로 외부 AI 호출하지 않는다. 원문은 일반 텍스트 렌더링, 원문 열람 종료 시 메모리에서 폐기한다. [팀 문서 계약](../domain/standards/README.md)을 따른다.

[ADR-REVIEW-013](../adr/review/ADR-REVIEW-013-recovery-and-evidence-checks.md)의 출력 복구·추가 발견·문맥 보충 상태는 사용자 문구로 표시한다. 수정 제안의 제한 검사에서 원래 성공값을 바꾸는 예시가 발견되면 결함 카드 안에 경고와 펼칠 수 있는 반례를 제공한다. 자연어에서 추출한 대안은 그 식만 검사했다는 범위를 표시하고 전체 수정 검증으로 표현하지 않는다. 별도 보안 신호는 AI 제안과 분리하며 AI 실패 때도 부분 결과임을 표시한다. 기존 결과에 새 필드가 없으면 과거 결과를 검증 완료로 승격하지 않는다.

[ADR-REVIEW-014](../adr/review/ADR-REVIEW-014-grounded-claims-and-repair-guards.md)의 origin=STATIC_PROJECTION은 ‘코드 계산에서 발견한 차이’로 표시한다. 원시 enum은 사용자 문구로 노출하지 않으며 본문에서 테스트 실행과 제한 계산을 구별한다. 기존/일반 AI 항목의 배지는 유지한다. 수정안이 차단되면 서버의 확인 안내와 기존 반례 UI를 표시하며 자동 수정 완료로 표현하지 않는다.
