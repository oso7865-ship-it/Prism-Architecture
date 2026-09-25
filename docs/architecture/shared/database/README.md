# Database: 세션·트랜잭션 기반

> ID: `DATABASE` · 소유: `backend/app/shared/database` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: DB 세션·트랜잭션·Migration을 변경할 때

```text
shared/database/
├─ base.py             DeclarativeBase
├─ engine.py           engine 생성/종료
├─ session.py          async session factory
└─ unit_of_work.py     기술적 transaction scope
```

업무 ORM은 각 도메인 `models.py`가 소유한다. Alembic의 model import 등록은 bootstrap/migration entrypoint에서 한다. shared가 모든 domain ORM을 import하는 편법을 쓰지 않는다.

## 세션과 트랜잭션

UseCase 단위로 Session을 만들고 외곽 Service/Workflow에서 트랜잭션을 연다. 내부 Repository는 execute/add/flush까지만 하고 자율 commit하지 않는다. 동일 UseCase에서 조합한 도메인 변경은 같은 Session/UoW를 주입한다. 이미 트랜잭션을 연 Service가 다른 Service의 독립 commit을 호출하지 않는다.

HTTP request와 각 Job attempt는 다른 Session이다. 외부 API 대기와 CPU 분석 동안 DB 트랜잭션/row lock을 유지하지 않는다. '짧게 읽기 → DB 밖 처리 → 짧게 조건부 저장'으로 나눈다. 하나의 AsyncSession은 동시에 실행되는 여러 작업에 공유하지 않는다. [S-DB-01](../../reference/SOURCES.md#s-db-01)

Analysis+Job, WebhookDelivery+Job은 같은 PostgreSQL 트랜잭션에서 생성한다. 메모리 큐/외부 브로커에 나중에 넣는 이중 기록 문제를 MVP에서 만들지 않는다.

## 제약·조회

UUID 같은 내부 ID와 GitHub 외부 bigint ID를 분리한다. 생성/변경 시각은 timezone-aware UTC와 PostgreSQL timestamptz를 사용한다. API에는 ISO 8601로 반환한다.

리소스 쿼리는 workspace_id 스코프를 포함하고 유일성은 DB 제약으로 보장한다. 역할 확인은 도메인에서 따로 한다. SELECT-then-INSERT만으로 중복을 막지 않는다. 목록은 keyset pagination과 최대 page size 100을 기본 정책으로 제안한다.

물리 FK·참조 강제 트리거·자동 CASCADE는 사용하지 않는다. PK/UNIQUE/NOT NULL/행 내부 CHECK는 유지한다. 부모 존재·테넌트·세대 검증과 Workspace별 짧은 쓰기 직렬화, cleanup 잠금 순서는 [물리 스키마](../../contracts/schema/README.md)의 공통 규칙을 따른다. FOR KEY SHARE만으로 부모의 비키 상태 변경까지 차단한다고 가정하지 않는다. [ADR-DATA-003](../../adr/data/ADR-DATA-003-logical-relations-schema.md)

DB pool은 무료/저용량 환경에 맞춰 초기 `pool_size=2, max_overflow=1`로 제한하고 HTTP/worker 동시 세션 수를 측정한다. 이 값은 서비스 처리량 보장이 아니다. transaction pooler 사용 시 driver/session 기능 호환성을 확인한다.

## Migration

Alembic migration은 배포 전 단일 실행 지점에서 수행한다. API worker 각각의 startup에서 동시에 migration하지 않는다. `create_all()`을 운영 schema 변경 수단으로 사용하지 않는다. schema 변경은 nullable→backfill→제약 강화 등 롤백/호환성을 고려한다.

필수 테스트는 실제 PostgreSQL로 UNIQUE 경쟁, transaction rollback, cross-workspace query, job claim, fence update를 검증한다. SQLite 대체만으로 락/동시성 테스트를 통과했다고 하지 않는다.
