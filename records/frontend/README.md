# PRism Frontend

Vue 3 / TypeScript / Vite / Vue Router 개발 기반입니다. GitHub 로그인·내 프로필·세션 복원·로그아웃 화면을 구현했습니다. 팀·저장소 연결, PR 목록·상세 화면을 제공합니다. PR 상세에서 정적 분석 요청·상태·취소·결과·이력·재분석을 제공합니다. Node 24와 npm을 사용하고 package-lock.json을 공유합니다.

## 실행

```bash
git clone https://github.com/oso7865-ship-it/Prism-Frontend.git prism-frontend
cd prism-frontend
npm ci
npm run dev
```

**http://localhost:5173** 에서 확인합니다. OAuth callback과 쿠키 호스트를 맞추기 위해 브라우저에서 127.0.0.1과 혼용하지 않습니다. 연결 확인 버튼은 `/health/ready`를 호출합니다. 기본 프록시 대상은 http://127.0.0.1:8000 이며 백엔드와 PostgreSQL이 준비됐을 때만 연결 완료를 표시합니다. `config/development.example`의 API_PROXY_TARGET으로 로컬 대상만 바꿀 수 있습니다. 실제 응답이 없으면 가짜 성공을 표시하지 않습니다.

## 검증

```bash
npm run build
npm test
npm audit
```

build는 vue-tsc 타입 검사와 production bundle 생성을 포함합니다. 테스트는 readiness와 refresh single-flight·만료 재시도·logout 실패/경쟁을 검증합니다. 현재 23개 통과(라우트 접근 제어·세션 만료 포함). 프록시는 Vite 개발 서버용이며 production Vercel rewrite와 도메인은 아직 구성하지 않았습니다. 서버 자격증명을 VITE_*에 넣지 않습니다.

src/app은 로그인·인증 후 공통 레이아웃·라우터, src/features는 인증과 작업 공간 기능, src/shared는 공통 API와 UI를 소유합니다.

## 하네스와 다른 PC에서 재개

이 저장소 루트의 AGENTS.md → PROJECT_HARNESS/00.PROJECT_CONTEXT.md → 작업별 문서 순서로 읽습니다. 공통 하네스는 [HARNESS](https://github.com/oso7865-ship-it/HARNESS)의 `0b7dcf9d567eaaa0c883eaee73620aa07cf60019` 사본입니다. 상위 폴더가 없어도 사용할 수 있습니다. 원본 유지보수 보고서는 출처 이력이며 현재 제품 상태는 GENERAL_HARNESS/05.WORKING_CONTEXT.md와 부착 프로젝트 최신 Report를 따릅니다.

[아키텍처 연결](docs/ARCHITECTURE.md)과 architecture.json으로 설계의 원본·기준 커밋을 추적합니다. 아키텍처를 바꾸면 원본 저장소에 ADR과 소유 문서를 갱신합니다. 각 저장소의 main이 통합 기준이며 이후 기능 작업은 별도 브랜치·PR·CI로 검증합니다. 초기 빈 저장소의 첫 커밋은 main으로 게시합니다. 브랜치 보호 설정 자체는 아직 적용하지 않았습니다.

작업 시작: git status로 로컬 변경 확인 → 깨끗한 상태에서 git pull --ff-only → 의존성 잠금 기준 설치 → 최신 Report의 미해결 항목 확인. 작업 종료: 검증 → Report/Working Context 갱신 → 커밋·푸시. 비밀 값과 가상환경·node_modules는 Git에 올리지 않습니다.

하네스 연결 검사: `node GENERAL_HARNESS/scripts/validate-project-adapter.mjs --project-root . --require-adapter --strict --json`.

## 확인된 검증 기록

[초기 구현 CI](https://github.com/oso7865-ship-it/Prism-Frontend/actions/runs/36039823516) 통과. production build·타입 검사·제품 테스트 3개 통과. 브라우저 준비 화면과 서버 연결 실패 안내도 확인했다.

## 로그인 테스트

백엔드도 함께 실행하고 AUTH_ENABLED·OAuth 키·JWT 서명키·DB를 설정해야 합니다. 기본 callback은 http://localhost:8000/api/v1/auth/github/callback 입니다. 프론트에 Secret이나 JWT 서명키를 넣지 않습니다.

1. localhost:5173에서 GitHub로 로그인 → 동의 → 이름/@login 확인.
2. 새로고침 → 로그인 유지 확인.
3. 로그아웃 → 새로고침 후에도 비로그인 확인.
4. GitHub 동의 취소 → 취소 안내와 다시 로그인 확인.

Access는 메모리, Refresh는 HttpOnly 쿠키입니다. single-flight는 한 탭 내에서 적용됩니다. 실제 로그인·새로고침 유지·로그아웃은 사용자 확인 완료입니다. [작업 리포트](reports/2026-09-25_github-login_report.md)에 자동 검증과 남은 항목을 구분해 기록했습니다.

## 팀·저장소 연결 (2026-09-26)

구현은 dev에서 진행한다. 팀/초대/권한·GitHub App 연결·PR 동기화 화면과 API를 추가했다. 실제 App 등록·실계정 연결 확인은 별도이며 최신 결과는 reports/_LATEST.md를 따른다. 로그인용 OAuth App과 저장소용 GitHub App은 서로 다른 설정이다.

등록/실행 상세는 Prism-Backend의 docs/TEAM_REPOSITORIES.md를 따른다. 개발 UI는 localhost:5173, API proxy는 localhost:8000이다.

## 페이지 구성과 화면 확인

| 주소 | 역할 |
|---|---|
| `/login` | GitHub 로그인, 실패 안내 및 재시도 |
| `/app` | 로그인 후 메인: 저장소·팀 현황과 기능 페이지 진입 |
| `/app/repositories` | 저장소 연결·선택, PR 동기화·검색·상세·GitHub 활동 |
| `/app/team` | 멤버·역할·초대 관리 |

로그인 상태를 복원한 뒤 보호 페이지에 진입합니다. 비로그인 또는 세션 만료 시 로그인으로 돌아갑니다. 기존 `/` OAuth callback은 메인으로, 저장소 연결 callback은 저장소 페이지로 전달합니다. 기능 페이지의 `team` 쿼리는 팀 선택을 유지합니다. 새 팀/초대 수락은 탐색 메뉴에서 펼치고, 계정/로그아웃은 우측 상단에 있습니다. 개발 연결 확인은 하단에 있습니다.

수동 확인: 로그인 → 메인 → 저장소와 PR → PR 선택/활동 조회 → 팀 설정 → 새로고침/뒤로 가기 → 로그아웃. 미로그인 상태에서 기능 주소 직접 접근 시 로그인 화면이어야 합니다. 초대 링크는 로그인 후 다시 열어 수락합니다. 검색은 가져온 PR에 한정됩니다. 역할 변경·연결 해제 등 데이터 변경은 테스트 대상 팀에서만 확인하세요.

2026-09-26 UI 개편 후 OAuth 설정을 수정했고 사용자가 실제 재로그인 성공을 확인했습니다. 개인·조직 저장소와 PR·정적 분석·AI 리뷰 화면을 확인했습니다. 세부 구현·검증 범위는 [최신 Report](reports/_LATEST.md)를 따릅니다.

배포 시 `/app/*`, `/login` 직접 접근을 `index.html`로 처리하는 SPA fallback이 필요합니다. Vite 개발 서버에서는 지원하며 운영 설정은 배포 주소 결정 후 구성합니다.

## 정적 분석 확인

저장소와 PR → 연결된 저장소 → PR 선택 → 현재 PR 분석. 완료 후 검사 범위, 파일별 평가 내역, 중요도·경로·줄·규칙을 확인합니다. 같은 커밋 재분석은 새 이력으로 남습니다. 서버 `ANALYSIS_RUNNER_ENABLED=true`와 0005 migration이 필요합니다. [구현·수동 검증 기록](reports/2026-09-26_static-analysis_report.md).

## 디자인 기준

[화면 설계·체크리스트](docs/DESIGN.md), [반응형·동작 검증](reports/2026-09-26_design-refinement_report.md). 로그인 → 홈 → 저장소·PR → 정적 분석 흐름을 제공하며 모바일에서는 PR 상세에 집중하고 목록으로 복귀할 수 있습니다.

## 수동 AI 리뷰

완료된 정적 분석에서 OWNER가 전송 안내를 확인하고 요청합니다. 결과·근거·검토 범위·토큰·이력을 표시합니다. 공개 배포 전 운영 검증과 리뷰 품질 보강은 남아 있으며 자동 댓글·자동 수정은 제공하지 않습니다.

## 배포 직전 준비

[배포 설정·운영 절차](deployment/README.md)를 확인하세요. production HTTPS·Secure cookie·프록시 설정과 Docker 이미지를 준비했으며 실제 공개 배포는 수행하지 않았습니다. 검증 결과와 남은 사용자 결정은 [최신 Report](reports/_LATEST.md)를 따릅니다.
