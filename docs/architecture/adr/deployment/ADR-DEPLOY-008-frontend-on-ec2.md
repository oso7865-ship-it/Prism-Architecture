# ADR-DEPLOY-008: 프론트 정적 파일을 기존 EC2에서 제공

> ID: `ADR-DEPLOY-008` · 소유: `DEPLOY` · 기준: `2026-09-30`
> 읽는 때: 프론트 호스팅·프록시·자동배포 대상을 변경할 때

- 상태: `SUPERSEDED`
- 기록일: `2026-09-30`
- 근거: 사용자가 프론트도 AWS로 전환하기로 선택하고 DNS를 연결했다.
- 대체하는 ADR: [ADR-DEPLOY-006](ADR-DEPLOY-006-private-ghcr-automatic-release.md), [ADR-FRONTEND-001](../frontend/ADR-FRONTEND-001-vue-vercel.md). Vercel 관련 결정만 변경한다.
- 대체한 ADR: [ADR-DEPLOY-009](ADR-DEPLOY-009-public-images.md). 공개 이미지 정책과 산출물 전송을 구체화하며 EC2 호스팅은 유지한다.

## 배경

기존 EC2/Caddy/API HTTPS를 준비한 상태에서 프론트도 같은 EC2에서 운영하기로 했다. 추가 인스턴스·탄력적 IP 없이 시작하고 외부 호스팅 설정을 줄인다.

## 결정

Vue 3·TypeScript·Vite·Vue Router를 유지한다. 빌드된 정적 파일은 /srv/prism-frontend/releases 아래 버전별로 저장하고 current 링크로 제공한다. Caddy가 prismquest.p-e.kr의 HTTPS·SPA fallback·정적 자원을 담당한다. /api와 /health 경로는 127.0.0.1:8000 백엔드로 먼저 전달하며 SPA fallback 대상에서 제외한다. api-prismquest.p-e.kr과 직접 GitHub Webhook은 유지한다. 두 도메인은 같은 탄력적 IP 52.79.50.98을 쓴다.

공개 프론트와 API origin, OAuth callback, host-only Secure 쿠키, CSRF, API no-store 계약은 유지한다. 기존 CSP/보안 헤더를 Caddy에 옮긴다. 백엔드 DB·private GHCR digest·OIDC/SSM·배포 잠금·migration 및 복구 Gate는 DEPLOY-006의 결정을 유지한다. Caddy 서비스와 인증서/로그 관리는 DEPLOY-007을 유지한다.

초기 프론트는 검증한 정적 산출물을 수동으로 배포한다. 목표 자동배포는 Actions에서 검증·빌드 후 동일 산출물을 EC2 버전 디렉터리에 배치하고 검증한 뒤 전환하는 방식이다. Vercel 전용 CI를 EC2로 교체하고 권한/복구를 검증하기 전에는 자동배포 완료로 보지 않는다.

## 대안

Vercel과 AWS Amplify는 별도 호스팅 연결이 필요하다. S3/CloudFront는 향후 정적 파일 트래픽과 장애 영역을 분리할 때 재검토한다. 이번에는 이미 준비한 Caddy와 EC2를 재사용한다.

## 영향과 한계

프론트용 상시 Node 서버와 서버 빌드가 필요하지 않다. 단일 EC2 장애는 양쪽에 영향을 주며 CDN 캐시가 없는 초기 구성이다. 정적 파일 배포 성공은 백엔드 준비·로그인·RDS migration·실사용 검증 성공이 아니다. 이전 버전과 Caddy 설정을 보존하여 초기 설정 실패 시 되돌린다.

## 소유 문서와 검증

[배포](../../operations/DEPLOYMENT.md), [프론트](../../frontend/README.md), [작업 및 검증 기록](../../../../records/2026-09-30_frontend-ec2.md)이 현재 범위와 증거를 소유한다. 프론트 deployment/Caddyfile은 실행 설정이다. 실제 TLS·SPA·자원·캐시/보안 헤더·API 오류 분리와 화면 검증을 수행하며 백엔드 및 자동배포 미완료를 구분한다.
