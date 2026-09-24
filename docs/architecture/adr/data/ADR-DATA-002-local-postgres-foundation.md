# ADR-DATA-002: PostgreSQL 17 로컬 개발 기반

> ID: `ADR-DATA-002` · 소유: `DATA` · 기준: `2026-09-25`
> 읽는 때: 구현 저장소와 개발 기반 변경 시

- 상태: `ACCEPTED`
- 기록일: `2026-09-25`
- 근거: 사용자 요청과 위임된 개발 기반 구성
- 대체하는 ADR: 없음 (기존 결정 보완)
- 대체한 ADR: 없음

## 배경

사용자가 개발 기반 구성을 요청했고 PostgreSQL Docker 개발을 논의했다. 상세 개발 환경은 구현 판단 범위에서 선택했다.

## 결정

개발 기준은 PostgreSQL 17 Compose와 named volume이다. 포트는 루프백에만 노출한다. SQLAlchemy psycopg async와 Alembic 빈 기준선부터 시작하며 업무 테이블은 해당 기능에서 추가한다.

## 대안

Windows 직접 설치와 로컬 컨테이너를 비교해 재현 가능한 Compose 파일을 제공한다. 운영 호스팅과 백업은 이 선택으로 확정하지 않는다.

## 영향과 한계

로컬 Docker가 없으므로 현재 PC에서 컨테이너 검증은 미실행이다. PostgreSQL 17 GitHub Actions 서비스에서 migration·트랜잭션 검증을 수행한다. 기존 PostgreSQL 사용 결정은 유지된다.

## 소유 문서와 검증

[구현 현황](../../runtime/IMPLEMENTATION.md), [패키지 규칙](../../PACKAGE_RULES.md), [DB](../../shared/database/README.md)를 동기화한다. 실행 결과는 구현 저장소 Report와 CI에서 확인한다.
