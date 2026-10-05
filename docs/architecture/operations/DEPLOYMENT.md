# AWS EC2 프론트·백엔드 배포 설계

> ID: `DEPLOYMENT` · 소유: `deployment` · 기준: `2026-09-30`
> 읽는 때: AWS·Docker·CI/CD·DB 호스팅을 변경할 때

## 확정과 미정

[ADR-DEPLOY-004](../adr/deployment/ADR-DEPLOY-004-ec2-runtime.md)에 따라 백엔드 실행 서비스는 AWS EC2다. [ADR-DEPLOY-005](../adr/deployment/ADR-DEPLOY-005-rds-initial-runtime.md)로 서울 ap-northeast-2, EC2 t3.small/Ubuntu 24.04.4 LTS, 별도 RDS PostgreSQL 17.11/db.t4g.micro/20GiB gp2/저장 암호화를 확정했다. 앱 DB prism과 전용 역할 prism_app은 TLS verify-full로 연결한다. 서버 비밀은 ubuntu 소유 700 디렉터리/600 파일에서 주입한다. 프론트·백엔드 배포, 실제 GitHub 로그인, GitHub ping 수신, 공개 GHCR/OIDC/SSM 자동배포, 논리 백업과 격리 DB 복원을 완료했다. 알림/예산·정기 백업 운영·상한 부하와 재해 복구 검증은 남아 있다.

[ADR-DEPLOY-009](../adr/deployment/ADR-DEPLOY-009-public-images.md)에 따라 Vue 프론트도 기존 EC2/Caddy에서 제공한다. 두 도메인 prismquest.p-e.kr/api-prismquest.p-e.kr은 같은 탄력적 IP 52.79.50.98을 쓴다. 운영 Alembic head는 0011(2026-10-06 리뷰 모드 0010과 저장소 후보 목록 0011 적용, 이전에는 0009)이며 두 도메인의 ready=200과 공개 프론트 로그인 성공을 확인했다. 실제 운영 PR의 전체 분석·AI 리뷰는 이번 배포 검증에 포함하지 않았다. [전체 출시 기록](../../../records/2026-09-30_full-ec2-release.md)이 최종 커밋·실행 결과·검증 한계를 소유한다.

[ADR-DEPLOY-007](../adr/deployment/ADR-DEPLOY-007-caddy-https.md)에 따라 Caddy가 TCP 80/443과 자동 인증서 발급·갱신을 담당한다. `/etc/caddy/Caddyfile`에서 `127.0.0.1:8000`으로 전달하며 관리 포트는 localhost 전용이다. 서비스는 비루트·부팅 자동 시작, 인증서 상태는 호스트의 영속 디렉터리에 유지한다. 오류 로그에서 request 필드를 제외한다. HTTP→HTTPS 308과 두 인증서의 신뢰 체인을 확인했다. 실제 만료 전 갱신과 호스트 재부팅 시험은 수행하지 않았다. [초기 HTTPS 기록](../../../records/2026-09-30_ec2-https.md)은 앱 기동 전 시점의 이력이다.

2026-09-30 사용자 지정 .env의 GitHub/DeepSeek 값과 기존 서버 DB/JWT/Webhook 값을 합쳐 `/home/ubuntu/.config/prism/runtime.env`를 600으로 생성했다. 인증/worker/AI 활성화와 팀30회를 구성하고 GitHub App 개인 키·앱 식별자, DeepSeek 모델 조회, RDS TLS 및 Compose 파싱을 확인했다. App slug는 prismrequest다. 이후 release preflight·migration·실제 OAuth code 교환을 통과해 배포 enabled=true로 전환했다. [환경값 반영 기록](../../../records/2026-09-30_production-runtime.md)은 최초 준비 단계의 이력이며 비밀값은 기록하지 않는다.

## 목표 구성

```text
브라우저 → EC2 Caddy (prismquest.p-e.kr)
           ├─ Vue 정적 파일 /srv/prism-frontend/current
           └─ /api 및 /health → 127.0.0.1:8000
                                └─ Docker / FastAPI + embedded dispatcher
                                   └─ RDS PostgreSQL 17
GitHub Webhook → api-prismquest.p-e.kr → Caddy → FastAPI
```

Dockerfile의 비root·단일 worker·PORT·health 구성을 기반으로 한다. 저장소 코드는 분석 데이터이며 실행하거나 의존성을 설치하지 않는다. 임시 로컬 파일에 Job/DB를 영속 보관하지 않는다. 컨테이너 중단·재시작 시 DB에 저장한 작업과 lease 복구를 검증한다. EC2 호스트와 컨테이너의 기동·재시작·업데이트·로그/디스크 관측을 준비한다. EC2 선택만으로 무중단·무료 운영·백그라운드 처리 지속성을 보장하지 않는다.

## production 계약

기존 동일 출처 계약에 적용할 운영 값은 `PUBLIC_APP_ORIGIN=https://prismquest.p-e.kr`, `PUBLIC_API_ORIGIN=https://prismquest.p-e.kr`이다. OAuth callback은 `https://prismquest.p-e.kr/api/v1/auth/github/callback`, GitHub App callback은 `https://prismquest.p-e.kr/api/v1/github-app/callback`이다. EC2 직접 API 주소는 `https://api-prismquest.p-e.kr`이며, 같은 호스트의 프론트 Caddy는 `127.0.0.1:8000`으로 프록시한다. 과거 Vercel용 `PRISM_API_ORIGIN` 설정 생성은 EC2 프론트의 운영 경로에서 사용하지 않는다. GitHub Webhook은 `https://api-prismquest.p-e.kr/webhooks/github`를 사용한다. 로컬 `.env`와 로컬 GitHub 앱 등록 값은 운영 주소 선택만으로 변경하지 않는다.

- 공개 앱과 API origin은 동일한 프론트 HTTPS origin이다. Caddy가 프론트 API 경로를 같은 EC2의 loopback 백엔드로 전달한다. 로그인 Callback과 GitHub Webhook 주소는 실제 동선에 맞춰 확정·등록한다.
- 쿠키는 Secure·HttpOnly·SameSite=Lax·host-only이며 삭제에도 동일 속성을 적용한다. CSRF는 정확한 frontend Origin과 전용 헤더를 검사한다. API는 브라우저/CDN no-store이며 운영 API 문서는 비활성화한다.
- DB는 PostgreSQL sslmode=verify-full 및 CA 검증을 유지한다. 비밀은 서버 실행 환경에서 주입하고 개발 키와 분리한다. Git·이미지·프론트 변수에 포함하지 않는다.
- AI 활성화는 운영 키·비용·동의 설정을 따른다. 팀 UTC 하루 30회 제한을 적용하며 이번 배포 확인에서는 유료 추론을 실행하지 않았다. [ADR-DEPLOY-009](../adr/deployment/ADR-DEPLOY-009-public-images.md)에 따라 main CI 통과를 기점으로 자동 배포한다. 최초 준비 전 enabled=false, 실제 준비 검증 후에만 true로 전환한다.

## 구현과 전환 범위

백엔드 Dockerfile 및 config/production.example은 기존 구현이다. deployment/render.example.yaml은 과거 Render 예시이며 현행 AWS 명세가 아니다. EC2 Docker Engine/Compose와 Caddy로 CI 통과 digest를 배포했다. PostgreSQL은 별도 RDS에 배치했고 앱과 Alembic은 같은 DATABASE_URL을 사용하며 prism_app에 schema USAGE/CREATE를 부여한다. 앱/DDL 계정 추가 분리와 운영 관측은 후속이다. 비공개 `.pending` 설정을 실제 배포 파일로 간주하지 않는다.

`deployment/compose.ec2.yaml`은 EC2 Docker 실행 설정이다. 호스트 HTTPS 프록시 뒤의 127.0.0.1:8000만 열고, 비루트 이미지·읽기 전용 파일시스템·64MiB 임시 영역·권한 제거·1GiB/1CPU/128 PID 제한·45초 종료 대기·자동 재시작·준비 상태 healthcheck·30MiB 로그 회전을 적용한다. EC2 인스턴스 전체 요구 메모리를 1GiB로 정한 것은 아니며 OS/프록시 여유가 별도로 필요하다. 실행 파일·환경 변수·운영 순서는 [배포 전 실행 안내](../../../records/2026-09-29_ec2-release-runbook.md)에 있다.

`python -m app.shared.config.preflight --image <digest>`는 네트워크 접근 없이 운영 모드·불변 이미지·인증/앱/worker/AI 활성화·팀30회·CA 파일 존재·예시 값 미교체를 검사한다. 출력은 검사명과 참/거짓뿐이다. PASS는 설정 검사이며 실제 키 유효성·CA 신뢰·TLS/프록시/DB 연결·AWS 성능의 증거가 아니다. 기존 기본 OFF 설정은 유지하고 실제 전체 기능 출시의 최종 preflight에서만 활성화를 요구한다.

설계·리포트는 Prism-Architecture에서만 관리한다. 구현 저장소에는 실행 코드와 배포 설정만 둔다. [중앙 기록](../../../records/README.md)과 실제 테스트 결과로 구현·배포 상태를 확인한다.

## CI/CD와 복구

코드 CI의 lint/type/unit/PostgreSQL integration/Docker build를 거친 같은 이미지를 공개 GHCR에 게시하고 immutable digest로 배포한다. Actions는 저장소 production 환경의 AWS OIDC 역할로 지정 EC2/SSM 문서만 실행한다. EC2는 익명으로 이미지를 내려받으며 runtime.env만 서버에 둔다. [ADR-DEPLOY-009](../adr/deployment/ADR-DEPLOY-009-public-images.md)로 비공개 이미지 결정을 대체했다. main 이외 브랜치와 PR은 게시·배포하지 않는다. 문서 검증은 아키텍처 CI가 담당하며 운영 DB에서 PR 테스트를 실행하지 않는다.

호스트 root 전용 도구는 입력/권한 검사·잠금·image provenance·운영 preflight 이후 스키마 검사 → 허용된 migration → 컨테이너 교체 → 내부/공개 ready 검사를 실행한다. 실제 SSM 완료까지 기다리고 실패/타임아웃을 성공으로 간주하지 않는다. `/etc/prism/deploy.json`은 enabled=true, migration_policy=unchanged다. 따라서 현재 head와 같은 일반 코드 변경은 자동 배포되지만 새 migration은 신선한 백업·복원 및 별도 이행 승인 후 설정을 변경해야 한다. 호스트 도구 자체의 업데이트는 별도 설치 단계다.

프론트 Vercel 전용 CI를 GHCR 정적 OCI·OIDC/SSM·EC2 원자적 배포 흐름으로 교체했고 실제 main 실행이 성공했다. CI가 검증한 dist만 이미지로 전달하며 상시 Node 컨테이너는 없다. 현재 링크 전환 후 모든 공개 자원 해시·SPA·API 준비 상태를 검사하고 실패하면 이전 링크로 복구한다. 복구 분기는 Linux 테스트로 확인했으며 운영 장애를 일부러 유발한 실험은 하지 않았다. 초기 로컬 dist와 CI dist의 파일명이 달라 최종 외부 해시 검사는 실제 배포 이미지에서 추출한 파일을 기준으로 수행했다.

GitHub production 환경은 각 저장소 main만 허용한다. AWS의 prism-backend-deploy/prism-frontend-deploy 역할은 실제 production OIDC subject와 sts.amazonaws.com audience를 신뢰하며, 각각 PrismDeployBackend/PrismDeployFrontend 문서와 지정 EC2만 SendCommand할 수 있다. 두 실제 Actions 실행에서 OIDC 발급과 SSM 완료를 확인했다. 장기 AWS 키와 GHCR PAT를 EC2에 보관하지 않는다.

migration 실패 시 rollout을 중단한다. schema 호환성이 확인된 이전 이미지로만 복귀하며 자동 DB downgrade는 하지 않는다. 초기 빈 DB와 migration 이후 public 테이블 20개의 논리 백업을 각각 격리 PostgreSQL에 복원해 확인했다. 백업 파일과 검증 기록은 /var/lib/prism-backups의 root 전용 파일이다. 이 호스트 내부 보관만으로 호스트 유실 복구를 보장하지 않으며 정기 RDS 백업·별도 보관 정책과 목표 복구 시간은 후속이다. 파괴적인 스키마 변경은 별도 이행·복구 설계가 필요하다.

## 배포 완료 전 검증

완료: 실제 OAuth 로그인·세션 생성, GitHub ping HMAC 수신 204, 인증 쿠키 속성, CSRF 없는 refresh 403/인증 없는 refresh 401, API 문서 비활성, 비공개 파일 404, TLS/SPA/정적 파일 해시, 두 자동 배포와 백업 복원. 남은 범위는 운영 PR 전체 분석/AI 흐름, 두 계정 격리의 운영 E2E, 네 언어·상한 입력의 실제 피크 자원, 강제 재시작/lease 복구, 알림/예산과 호스트 유실 복구다. 기존 로컬/CI 결과로 AWS 실연동 완료를 대신하지 않는다. [OPEN-ITEMS](../decisions/OPEN_ITEMS.md)를 따른다.
