# ADR-DEPLOY-004: 백엔드 실행 서비스로 EC2 선택

> ID: `ADR-DEPLOY-004` · 소유: `DEPLOY` · 기준: `2026-09-29`
> 읽는 때: EC2 실행 구성과 배포 설정을 변경할 때

- 상태: `SUPERSEDED`
- 기록일: `2026-09-29`
- 근거: 사용자 “aws는 ec2로 진행할 예정이야” 결정.
- 대체하는 ADR: [ADR-DEPLOY-003](ADR-DEPLOY-003-aws-backend.md).
- 대체한 ADR: [ADR-DEPLOY-006](ADR-DEPLOY-006-private-ghcr-automatic-release.md). EC2와 production 계약을 유지하며 자동 배포 정책을 구체화한다.

## 배경

AWS 공급자 선택 이후 실행 서비스는 미정이었다. 사용자가 EC2를 선택했으므로 실행 대상을 구체화한다. 현재 작업 목표는 실제 배포 전 준비다.

## 결정

백엔드는 AWS EC2에서 기존 Docker/FastAPI 애플리케이션을 운영하는 방향으로 준비한다. 프론트 Vue/Vercel, PostgreSQL, 단일 Uvicorn worker와 embedded Job dispatcher, 제한된 parser subprocess 구성은 유지한다. EC2 선택으로 DB의 동일 인스턴스 배치나 RDS 사용을 자동 확정하지 않는다.

DEPLOY-003의 production 계약을 유지한다. HTTPS 프론트 origin을 통한 API 프록시, 정확한 Origin/CSRF 검사, Secure·HttpOnly·SameSite=Lax·host-only 쿠키, API no-store, 운영 API 문서 비활성화, PostgreSQL TLS/CA 검증, 비root 컨테이너, 개발/운영 비밀 분리, 원문·키 비저장, 자동 배포와 AI 기본 OFF가 기준이다. migration은 배포 단계에서 한 번 실행하고 실패 시 중단하며, 호환되는 이전 이미지로만 복구하고 자동 DB downgrade는 하지 않는다. 백업은 별도 DB 복원 검증 후 전환한다.

리전, 인스턴스 종류·크기·OS, 저장 공간, 네트워크·HTTPS 진입점, PostgreSQL 호스팅·백업, 비밀 주입, 이미지 전달·배포 방식, 도메인, 비용 예산·알림은 미정이다. 실제 EC2 생성과 계정/결제/배포 작업은 이번 결정 기록에 포함하지 않는다.

## 대안

다른 AWS 실행 서비스와의 가격·성능 비교로 선택한 것이 아니라 사용자의 EC2 결정을 반영한다. 특정 인스턴스, 관리형 DB, 로드밸런서 또는 컨테이너 레지스트리를 추가 채택하지 않는다.

## 영향과 한계

EC2 호스트와 컨테이너의 기동·재시작·업데이트·접근 관리 및 로그/디스크/비용 관측을 배포 설정에 포함해야 한다. 기존 Dockerfile과 운영 설정은 기반이며 EC2 실연동 완료를 의미하지 않는다. 선택한 크기에서 자원 사용량과 Job 복구를 확인해야 하며 무료 운영·무중단·고가용성을 보장하지 않는다.

## 소유 문서와 검증

[배포 설계](../../operations/DEPLOYMENT.md), [미정사항](../../decisions/OPEN_ITEMS.md), [공통 기준](../../CORE.md), 결정 맵과 context-map.json을 동기화한다. 이번에는 문서 링크·ID·대체 관계를 검증한다. 코드 CI, EC2 재시작/자원, OAuth 쿠키 프록시, Webhook, DB 지속성과 복구는 구성 확정·실행 후 별도로 확인한다.
