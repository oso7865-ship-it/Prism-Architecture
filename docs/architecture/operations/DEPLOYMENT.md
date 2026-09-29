# AWS EC2 백엔드 배포 설계

> ID: `DEPLOYMENT` · 소유: `deployment` · 기준: `2026-09-29`
> 읽는 때: AWS·Docker·CI/CD·DB 호스팅을 변경할 때

## 확정과 미정

[ADR-DEPLOY-004](../adr/deployment/ADR-DEPLOY-004-ec2-runtime.md)에 따라 백엔드 실행 서비스는 AWS EC2로 확정했다. 리전·인스턴스 종류/크기/OS·저장 공간·네트워크·DB 호스팅·비밀 주입 방식·예산·공개 도메인은 미정이다. 프론트는 Vue/Vercel을 유지한다. 실제 배포는 아직 수행하지 않았으며 현재 목표는 배포 전 준비다.

## 목표 구성

```text
브라우저 → Vercel(Vue + /api reverse proxy)
                   ↓
             EC2의 HTTPS 백엔드
             └─ Docker / FastAPI
                ├─ API + embedded Job dispatcher
                └─ 제한된 Parser subprocess
                   ↓
             PostgreSQL (호스팅 미정)

GitHub Webhook → EC2 백엔드의 직접 HTTPS endpoint
```

Dockerfile의 비root·단일 worker·PORT·health 구성을 기반으로 한다. 저장소 코드는 분석 데이터이며 실행하거나 의존성을 설치하지 않는다. 임시 로컬 파일에 Job/DB를 영속 보관하지 않는다. 컨테이너 중단·재시작 시 DB에 저장한 작업과 lease 복구를 검증한다. EC2 호스트와 컨테이너의 기동·재시작·업데이트·로그/디스크 관측을 준비한다. EC2 선택만으로 무중단·무료 운영·백그라운드 처리 지속성을 보장하지 않는다.

## production 계약

- 공개 앱과 API origin은 동일한 프론트 HTTPS origin이다. Vercel의 서버 측 rewrite 목적지에 AWS 백엔드 HTTPS 주소를 넣는다. 로그인 Callback과 GitHub Webhook 주소는 실제 동선에 맞춰 확정·등록한다.
- 쿠키는 Secure·HttpOnly·SameSite=Lax·host-only이며 삭제에도 동일 속성을 적용한다. CSRF는 정확한 frontend Origin과 전용 헤더를 검사한다. API는 브라우저/CDN no-store이며 운영 API 문서는 비활성화한다.
- DB는 PostgreSQL sslmode=verify-full 및 CA 검증을 유지한다. 비밀은 서버 실행 환경에서 주입하고 개발 키와 분리한다. Git·이미지·프론트 변수에 포함하지 않는다.
- AI와 자동 배포는 기본 OFF다. EC2 실행 설정·도메인·비밀·비용 정책이 정해지기 전 자동으로 켜지 않는다.

## 구현과 전환 범위

백엔드 Dockerfile 및 config/production.example은 기존 구현이다. deployment/render.example.yaml은 과거 Render 예시이며 현행 AWS 명세가 아니다. EC2 실행 자원, 최소 권한, HTTPS 진입점, 비밀 주입, 이미지 전달·배포 방식과 호스트/컨테이너 운영 설정을 준비한다. PostgreSQL을 동일 EC2, 별도 인스턴스, 관리형 DB 중 어디에 배치할지는 별도 결정이다.

`deployment/compose.ec2.yaml`은 EC2 Docker 실행 설정이다. 호스트 HTTPS 프록시 뒤의 127.0.0.1:8000만 열고, 비루트 이미지·읽기 전용 파일시스템·64MiB 임시 영역·권한 제거·1GiB/1CPU/128 PID 제한·45초 종료 대기·자동 재시작·준비 상태 healthcheck·30MiB 로그 회전을 적용한다. EC2 인스턴스 전체 요구 메모리를 1GiB로 정한 것은 아니며 OS/프록시 여유가 별도로 필요하다. 실행 파일·환경 변수·운영 순서는 [배포 전 실행 안내](../../../records/2026-09-29_ec2-release-runbook.md)에 있다.

`python -m app.shared.config.preflight --image <digest>`는 네트워크 접근 없이 운영 모드·불변 이미지·인증/앱/worker/AI 활성화·팀30회·CA 파일 존재·예시 값 미교체를 검사한다. 출력은 검사명과 참/거짓뿐이다. PASS는 설정 검사이며 실제 키 유효성·CA 신뢰·TLS/프록시/DB 연결·AWS 성능의 증거가 아니다. 기존 기본 OFF 설정은 유지하고 실제 전체 기능 출시의 최종 preflight에서만 활성화를 요구한다.

설계·리포트는 Prism-Architecture에서만 관리한다. 구현 저장소에는 실행 코드와 배포 설정만 둔다. [중앙 기록](../../../records/README.md)과 실제 테스트 결과로 구현·배포 상태를 확인한다.

## CI/CD와 복구

코드 CI의 lint/type/unit/PostgreSQL integration/Docker build를 거쳐 배포할 커밋을 정한다. 문서 검증은 아키텍처 CI가 담당한다. 배포 절차는 단일 migration → EC2 컨테이너 갱신 → health/auth/Job smoke test 순서이며 실행·접속 방식 확정 후 구체화한다. 운영 DB에서 PR 테스트를 실행하지 않는다.

migration 실패 시 rollout을 중단한다. schema 호환성이 확인된 이전 이미지로만 복귀하며 자동 DB downgrade는 하지 않는다. 백업은 별도 DB에 복원해 검증한 뒤 전환한다. 파괴적인 스키마 변경은 별도 이행·복구 설계가 필요하다.

## 배포 완료 전 검증

네 언어·상한 입력의 실제 피크 메모리/CPU, Parser timeout kill, 동시 HTTP 응답, 강제 재시작과 lease 복구, HMAC Webhook, OAuth/Set-Cookie 프록시, 두 계정 격리, DB 지속성/백업복원, 비밀·로그 노출과 사용 비용을 확인한다. 기존 로컬/CI 결과로 AWS 실연동 완료를 대신하지 않는다. 남은 선택은 [OPEN-ITEMS](../decisions/OPEN_ITEMS.md)를 따른다.
