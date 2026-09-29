# AWS EC2 백엔드 배포 설계

> ID: `DEPLOYMENT` · 소유: `deployment` · 기준: `2026-09-30`
> 읽는 때: AWS·Docker·CI/CD·DB 호스팅을 변경할 때

## 확정과 미정

[ADR-DEPLOY-004](../adr/deployment/ADR-DEPLOY-004-ec2-runtime.md)에 따라 백엔드 실행 서비스는 AWS EC2다. [ADR-DEPLOY-005](../adr/deployment/ADR-DEPLOY-005-rds-initial-runtime.md)로 사용자 생성 자원을 구체화했다: 서울 ap-northeast-2, EC2 t3.small/Ubuntu 24.04.4 LTS, 별도 RDS PostgreSQL 17.11/db.t4g.micro/20GiB gp2/저장 암호화. 앱 DB prism과 전용 역할 prism_app의 실제 TLS 로그인을 확인했다. 서버 비밀은 초기에는 ubuntu 소유 700 디렉터리/600 파일로 주입한다. EC2 탄력적 IP 연결과 새 주소의 SSH 접속은 확인했으며 DNS·HTTPS·이미지 registry·운영 GitHub 키·백업 복원·알림/예산은 미완료다.

프론트는 Vue/Vercel을 유지하고 사용자 지정 주소는 `https://prismquest.p-e.kr`, 백엔드는 `https://api-prismquest.p-e.kr`이다. 두 주소의 DNS·Vercel·TLS·로그인 검증은 아직 하지 않았다. EC2/RDS 준비와 애플리케이션 배포를 구분하며 실제 백엔드 실행·migration은 아직 수행하지 않았다.

## 목표 구성

```text
브라우저 → Vercel(Vue + /api reverse proxy)
                   ↓
             EC2의 HTTPS 백엔드
             └─ Docker / FastAPI
                ├─ API + embedded Job dispatcher
                └─ 제한된 Parser subprocess
                   ↓
             Amazon RDS PostgreSQL 17

GitHub Webhook → EC2 백엔드의 직접 HTTPS endpoint
```

Dockerfile의 비root·단일 worker·PORT·health 구성을 기반으로 한다. 저장소 코드는 분석 데이터이며 실행하거나 의존성을 설치하지 않는다. 임시 로컬 파일에 Job/DB를 영속 보관하지 않는다. 컨테이너 중단·재시작 시 DB에 저장한 작업과 lease 복구를 검증한다. EC2 호스트와 컨테이너의 기동·재시작·업데이트·로그/디스크 관측을 준비한다. EC2 선택만으로 무중단·무료 운영·백그라운드 처리 지속성을 보장하지 않는다.

## production 계약

기존 동일 출처 계약에 적용할 운영 값은 `PUBLIC_APP_ORIGIN=https://prismquest.p-e.kr`, `PUBLIC_API_ORIGIN=https://prismquest.p-e.kr`이다. OAuth callback은 `https://prismquest.p-e.kr/api/v1/auth/github/callback`, GitHub App callback은 `https://prismquest.p-e.kr/api/v1/github-app/callback`이다. EC2 직접 주소와 Vercel rewrite 목적지는 `https://api-prismquest.p-e.kr`이며, 프론트 배포 설정 생성 시 `PRISM_API_ORIGIN`으로 전달한다. GitHub Webhook은 `https://api-prismquest.p-e.kr/webhooks/github`를 사용한다. 로컬 `.env`와 로컬 GitHub 앱 등록 값은 운영 주소 선택만으로 변경하지 않는다.

- 공개 앱과 API origin은 동일한 프론트 HTTPS origin이다. Vercel의 서버 측 rewrite 목적지에 AWS 백엔드 HTTPS 주소를 넣는다. 로그인 Callback과 GitHub Webhook 주소는 실제 동선에 맞춰 확정·등록한다.
- 쿠키는 Secure·HttpOnly·SameSite=Lax·host-only이며 삭제에도 동일 속성을 적용한다. CSRF는 정확한 frontend Origin과 전용 헤더를 검사한다. API는 브라우저/CDN no-store이며 운영 API 문서는 비활성화한다.
- DB는 PostgreSQL sslmode=verify-full 및 CA 검증을 유지한다. 비밀은 서버 실행 환경에서 주입하고 개발 키와 분리한다. Git·이미지·프론트 변수에 포함하지 않는다.
- AI 활성화는 운영 키·비용·동의 설정을 따르며 CI/CD 연결로 자동으로 켜지지 않는다. 자동 배포는 [ADR-DEPLOY-006](../adr/deployment/ADR-DEPLOY-006-private-ghcr-automatic-release.md)에 따라 최초 환경 준비 후 main의 CI 통과를 기점으로 실행한다. EC2 배포 설정은 준비 전 enabled=false다.

## 구현과 전환 범위

백엔드 Dockerfile 및 config/production.example은 기존 구현이다. deployment/render.example.yaml은 과거 Render 예시이며 현행 AWS 명세가 아니다. EC2 Docker Engine/Compose 설치와 설정 검증, 고정한 CI 통과 커밋 준비까지 완료했다. PostgreSQL은 별도 RDS에 배치했다. 현재 앱과 Alembic은 같은 DATABASE_URL을 사용하며 prism_app에 schema USAGE/CREATE를 부여한다. 앱/DDL 계정 추가 분리, HTTPS 진입점, 이미지 registry/digest, 운영 키 완성 및 백업/관측은 남아 있다. 비공개 `.pending` 설정을 실제 배포 파일로 간주하지 않는다.

`deployment/compose.ec2.yaml`은 EC2 Docker 실행 설정이다. 호스트 HTTPS 프록시 뒤의 127.0.0.1:8000만 열고, 비루트 이미지·읽기 전용 파일시스템·64MiB 임시 영역·권한 제거·1GiB/1CPU/128 PID 제한·45초 종료 대기·자동 재시작·준비 상태 healthcheck·30MiB 로그 회전을 적용한다. EC2 인스턴스 전체 요구 메모리를 1GiB로 정한 것은 아니며 OS/프록시 여유가 별도로 필요하다. 실행 파일·환경 변수·운영 순서는 [배포 전 실행 안내](../../../records/2026-09-29_ec2-release-runbook.md)에 있다.

`python -m app.shared.config.preflight --image <digest>`는 네트워크 접근 없이 운영 모드·불변 이미지·인증/앱/worker/AI 활성화·팀30회·CA 파일 존재·예시 값 미교체를 검사한다. 출력은 검사명과 참/거짓뿐이다. PASS는 설정 검사이며 실제 키 유효성·CA 신뢰·TLS/프록시/DB 연결·AWS 성능의 증거가 아니다. 기존 기본 OFF 설정은 유지하고 실제 전체 기능 출시의 최종 preflight에서만 활성화를 요구한다.

설계·리포트는 Prism-Architecture에서만 관리한다. 구현 저장소에는 실행 코드와 배포 설정만 둔다. [중앙 기록](../../../records/README.md)과 실제 테스트 결과로 구현·배포 상태를 확인한다.

## CI/CD와 복구

코드 CI의 lint/type/unit/PostgreSQL integration/Docker build를 거친 같은 이미지를 private GHCR에 게시하고 immutable digest로 배포한다. Actions는 저장소 production 환경의 AWS OIDC 역할로 지정 EC2/SSM 문서만 실행한다. 다운로드용 read:packages 토큰과 runtime.env는 EC2에만 둔다. main 이외 브랜치와 PR은 게시·배포하지 않는다. 문서 검증은 아키텍처 CI가 담당하며 운영 DB에서 PR 테스트를 실행하지 않는다.

호스트 root 전용 도구는 입력/권한 검사·잠금·image provenance·운영 preflight 이후 단일 migration → 컨테이너 교체 → 내부/공개 ready 검사를 실행한다. 실제 SSM 완료까지 기다리고 실패/타임아웃을 성공으로 간주하지 않는다. `/etc/prism/deploy.json`의 최초 활성화와 백업 복원 확인이 필요하다. 호스트 도구 자체의 업데이트는 별도 설치 단계다.

프론트 main CI 후 Vercel production build/prebuilt 배포와 로그인 페이지/API proxy 검사를 실행한다. 팀 Prism(prism-2139)에 실제 프로젝트 생성 및 Vercel 식별자/토큰 연결이 남았다. Vercel Git 기본 자동 배포와 중복 실행하지 않는다. 프론트 배포 후 검사가 실패하면 이전 Vercel 배포로 운영자가 복구한다. 자동 복구는 백엔드에서 아래 DB 조건을 만족할 때만 수행한다. 설정 목록과 최초 실행 순서는 [자동 배포 기록](../../../records/2026-09-30_automatic-deployment.md)에 있다.

migration 실패 시 rollout을 중단한다. schema 호환성이 확인된 이전 이미지로만 복귀하며 자동 DB downgrade는 하지 않는다. 백업은 별도 DB에 복원해 검증한 뒤 전환한다. 파괴적인 스키마 변경은 별도 이행·복구 설계가 필요하다.

## 배포 완료 전 검증

네 언어·상한 입력의 실제 피크 메모리/CPU, Parser timeout kill, 동시 HTTP 응답, 강제 재시작과 lease 복구, HMAC Webhook, OAuth/Set-Cookie 프록시, 두 계정 격리, DB 지속성/백업복원, 비밀·로그 노출과 사용 비용을 확인한다. 기존 로컬/CI 결과로 AWS 실연동 완료를 대신하지 않는다. 남은 선택은 [OPEN-ITEMS](../decisions/OPEN_ITEMS.md)를 따른다.
