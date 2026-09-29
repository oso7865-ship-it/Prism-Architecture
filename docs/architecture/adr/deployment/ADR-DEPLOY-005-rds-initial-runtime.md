# ADR-DEPLOY-005: RDS와 초기 EC2 운영 구성

> ID: `ADR-DEPLOY-005` · 소유: `DEPLOY` · 기준: `2026-09-30`
> 읽는 때: 운영 DB 배치·초기 EC2 사양·서버 비밀 주입을 변경할 때

- 상태: `ACCEPTED`
- 기록일: `2026-09-30`
- 근거: 사용자가 EC2 Ubuntu와 RDS PostgreSQL 17.11을 생성하고 초기 DB 설정을 실행했다. 직접 SSH와 RDS 로그인으로 확인했다.
- 대체하는 ADR: 없음. [ADR-DEPLOY-004](ADR-DEPLOY-004-ec2-runtime.md)의 EC2 선택을 구체화한다.
- 대체한 ADR: 없음.

## 배경

초기 AWS 구성은 서울 ap-northeast-2의 EC2 t3.small / Ubuntu 24.04.4 LTS와 별도 RDS PostgreSQL 17.11이다. 사용자가 생성한 RDS는 db.t4g.micro, 20GiB gp2, 저장 암호화 활성화, 단일 AZ다. EC2 IMDSv2에서 리전/종류를 확인했고 RDS 구성은 사용자 화면과 실제 PostgreSQL 접속으로 확인했다. 이 크기를 공개 서비스 처리량이나 고가용성 보장으로 해석하지 않는다.

## 결정

EC2의 Docker/FastAPI와 RDS를 분리하고, DB 클라이언트는 RDS CA와 sslmode=verify-full을 사용한다. DB `prism`의 관리 소유자는 `hoon`, 앱 로그인 역할은 `prism_app`이다. 현행 앱과 Alembic은 같은 DATABASE_URL을 읽으므로 앱 역할에 DB CONNECT와 public schema USAGE/CREATE를 부여한다. 새 DB의 PUBLIC CONNECT/CREATE를 제한하며 앱에 SUPERUSER·CREATEDB·CREATEROLE·REPLICATION·BYPASSRLS는 주지 않는다. 앱이 생성하는 테이블/인덱스의 소유권은 migration에 필요하다. 런타임/DDL 계정의 추가 분리는 후속 개선 대상이다.

초기 비밀 주입은 EC2의 ubuntu 소유 비공개 파일로 준비한다. 디렉터리는 700, 비밀 파일은 600이며 Compose의 raw env_file로 전달한다. 실제 비밀은 Git·이미지·도구 출력에 포함하지 않고 로컬 개발 키를 운영 키로 복사하지 않는다. 운영 GitHub OAuth/App 키는 아직 준비되지 않았다. 준비 파일은 `.pending` 상태로 두고 인증/worker/AI/운영 preflight의 필수 검증을 우회하지 않는다.

## 대안

EC2 내부 PostgreSQL은 사용자 RDS 선택에 따라 채택하지 않았다. 프론트 Vue/Vercel, 동일 프론트 origin의 API 프록시, Secure 쿠키·CSRF, 단일 API worker, 비루트 자원 제한 컨테이너, AI/자동 배포 기본 OFF, 단일 migration과 백업/복원 검증은 DEPLOY-004를 유지한다. 레지스트리·HTTPS 프록시·공개 비용 예산/알림은 별도로 정한다.

## 영향과 한계

RDS 분리로 EC2 재배치와 DB 수명을 구분하지만, 현재 단일 AZ와 작은 인스턴스 사양은 장애 대응이나 처리량을 보장하지 않는다. 앱 역할은 migration을 위해 자신이 만든 테이블의 DDL 권한을 유지한다. 운영 백업 복원과 부하 검증 전이며, 파일 기반 비밀 주입의 교체·복구 절차도 실제 배포 전에 확인한다.

## 소유 문서와 검증

`prism_app`의 RDS 17.11 로그인과 TLS 1.3, schema 생성 권한, 관리자 역할 속성 해제, PUBLIC DB 접속 제한을 확인했다. 앱 테이블은 0개이며 실제 migration·백엔드 실행은 아직 하지 않았다. Docker Engine 29.8.1/Compose 5.5.1 설치, 격리된 hello-world 실행, 기존 EC2 Compose 설정 검증은 통과했다.

현재 EC2 공개 IP는 자동 할당 주소다. Elastic IP/DNS/HTTPS, 운영 GitHub 설정, 이미지 registry/digest, 운영 백업 복원과 migration, 장애·비용 알림, 실제 앱 로그인/PR/AI 흐름 검증이 남았다. 상세 증거는 [EC2 접속·준비 기록](../../../../records/2026-09-30_ec2-access-report.md), 현재 계약은 [배포 설계](../../operations/DEPLOYMENT.md), 남은 결정은 [OPEN-ITEMS](../../decisions/OPEN_ITEMS.md)를 따른다.
