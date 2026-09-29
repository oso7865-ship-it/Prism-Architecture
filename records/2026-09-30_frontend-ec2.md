# 프론트 EC2 전환과 도메인 연결

이 기록은 초기 수동 배포 단계의 결과다. 이후 공개 GHCR/OIDC/SSM 자동배포와 운영 로그인 완료는 [전체 출시 결과](2026-09-30_full-ec2-release.md)를 따른다.

## 작업 계약과 설계

- 근거: 사용자가 Vercel 대신 AWS EC2 프론트를 선택하고 prismquest.p-e.kr의 A 레코드를 입력했다고 알렸다.
- 읽은 문서: CORE, DEPLOYMENT, FRONTEND, CONFIG, BOOTSTRAP, ADR-GUIDE, ADR-DEPLOY-006/007, ADR-FRONTEND-001. Terminal Ops와 Security Gate를 적용한다.
- 범위: 기존 단일 EC2와 탄력적 IP 52.79.50.98을 재사용한다. Caddy에 프론트 정적 파일·SPA 경로·동일 출처 API 프록시·HTTPS를 추가한다. 문서는 아키텍처 저장소에서만 관리한다.
- 제외: DB migration, 백엔드 앱 시작, 운영 로그인·AI 리뷰 성공 주장, 새 IP/인스턴스 발급. 자동배포는 EC2용 전환과 권한 연결이 필요한 별도 후속이며 이번 수동 초기 배포와 구분한다.
- 변경 전 사전 확인: 프론트 작업 트리는 깨끗하며 e6fdbd0 커밋이다. 서버 /srv/prism-frontend는 비어 있고 Caddy 기존 파일 SHA-256은 df21f809049f3884a989d7ef3c6e2360843dc6a2de121858acaa6a798510da06이다. Docker 앱은 없다. DNS A 52.79.50.98 확인.
- 배포 설계: 검증한 dist만 전송한다. 비밀·원본 코드·node_modules를 보내지 않는다. SHA-256으로 전송 무결성을 확인하고 새 버전 디렉터리로 풀어 current 링크를 전환한다. Caddy 이전 설정을 보존하고 validate 후 reload하며 실패 시 복구한다.
- 보안 기준: API/health와 SPA fallback을 분리해 API 오류를 HTML 200으로 숨기지 않는다. API no-store, CSP 등 기존 보안 헤더, 로그 request 필드 삭제를 유지한다. 숨김 파일·소스맵을 제공하지 않는다. GitHub callback·쿠키·CSRF origin 계약은 변경하지 않는다.
- 검증: 타입·Vite 빌드·프론트 테스트, 실제 Caddy validate, 외부 TLS 신뢰/호스트명·HTTP 전환·SPA 경로·JS/CSS·보안/캐시 헤더·비공개 파일 차단, 브라우저 화면 확인. 백엔드 미기동은 별도 미완료로 표시한다.

## 결과

- 프론트 배포 완료: https://prismquest.p-e.kr/login. 실제 브라우저에서 Vue 화면·로그인 링크·백엔드 연결 실패 안내를 확인했다. 로그인/AI 기능이 동작한다고 보고하지 않는다.
- 배포 소스: e6fdbd0b23e5cc55e334d92552c88eb29e2af46d. 제품 소스 변경 없이 로컬에서 빌드했고 untracked deployment/Caddyfile을 별도 설정으로 설치했다. dist의 HTML/JS/CSS 3개만 전송했으며 외부 다운로드 SHA-256이 원본과 모두 일치한다.
- 서버: /srv/prism-frontend/releases/e6fdbd0b23e5cc55e334d92552c88eb29e2af46d, current 링크, root 소유 파일 644/디렉터리 755. /srv/prism-frontend/bootstrap.json에 파일 해시/설정 백업 경로를 기록했다.
- Caddy 설정 SHA-256: d1842ea3e43037ed4fb9f615c38326bae4f0e91adecb8e781c40d97bfe08d303. 이전 설정은 /var/lib/prism-bootstrap/caddy/Caddyfile.before-frontend-1790709608177665196에 보존했다. validate 및 reload 성공.
- TLS 1.3 신뢰/호스트명 검증 PASS. Let's Encrypt YE1, 인증서 만료 2026-12-28 18:21:42 UTC. HTTP→HTTPS 308, 로그인/SPA 직접 접근 200, 정적 파일 해시/타입/캐시, 숨김 파일·소스맵·없는 JS 404 확인.
- API/health 경로는 백엔드 미기동으로 502 및 no-store를 반환한다. SPA HTML 200으로 오류를 숨기지 않는다. 실제 백엔드·로그인·Webhook·AI는 미완료다.
- 타입 검사·Vite 빌드와 15개 파일/136개 테스트 PASS. 최초 제한 환경 실행은 esbuild 상위 경로 접근 거부로 실패했으나 승인된 정상 권한 재실행은 PASS였다. 새 의존성 설치는 없다.
- 검증 데이터/화면은 저장소 밖 audit-artifacts/ec2-bootstrap-20260930/frontend-verification.json 및 frontend-login.png에 기록했다. 외부 유료 AI 호출·DB 변경·앱 시작·Git 커밋/푸시 없음.
- 최종 문서 검사 PASS: Markdown 124개, 문서 ID 89개, 링크 559개, ADR 37개. 기존 문서 길이 경고 6개는 비차단이다. diff whitespace 검사 PASS. Cloudflare/Google DNS 모두 52.79.50.98, 서버 Caddy active/enabled 및 root 소유·파일 644/디렉터리 755를 재확인했다.

## 후속과 복구

1. 백엔드 초기 배포 Gate: private GHCR 읽기 권한, 초기 스키마·백업/복원 절차, 실제 release preflight와 앱 시작, 운영 로그인/웹훅 확인.
2. 프론트 Vercel CI를 EC2 자동배포로 전환하고 검증된 산출물 전송·원자적 버전 전환·배포 실패 복구를 연결한다. 현재 수동 초기 배포를 자동배포 완료로 간주하지 않는다.
3. 이번 Caddy 전환 복구는 위 설정 백업을 별도 후보 파일로 복사하여 validate 후 /etc/caddy/Caddyfile에 설치하고 reload한다. 프론트 release와 키/DB는 삭제하지 않는다. 앱이 실행되기 전이므로 서비스 전체 준비 검사는 FAIL/미완료로 남긴다.
