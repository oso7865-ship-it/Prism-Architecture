# ADR-DATA-003: 물리 FK 없는 17개 테이블과 무결성 계약

> ID: `ADR-DATA-003` · 소유: `DATA` · 기준: `2026-09-25`
> 읽는 때: 물리 스키마·관계 강제·동시성 정책을 변경할 때

- 상태: `ACCEPTED`
- 기록일: `2026-09-25`
- 근거: 사용자의 물리 FK 비선호와 DB 설계 구체화 작업 진행 요청. 상세 타입·인덱스·서비스 무결성 방식은 해당 범위의 설계 판단.
- 대체하는 ADR: 없음 (기존 PostgreSQL·개발 기반 결정 유지, DATA-MODEL의 FK 허용 계약 변경)
- 대체한 ADR: 없음

## 배경

기존 논리 모델은 17개 테이블과 주요 유일성만 명시했고 DB FK를 허용했다. 사용자는 물리 FK를 선호하지 않으며 하네스 동기화를 보류하고 DB 컬럼·타입·인덱스 구체화를 요청했다. 아직 업무 테이블은 구현하지 않아 기존 데이터 이관은 필요하지 않다.

## 결정

1. [물리 스키마](../../contracts/schema/README.md)에 17개 테이블의 컬럼·NULL·기본값·PK·UNIQUE·CHECK·인덱스를 정의한다. 실제 migration은 기능별로 도입한다.
2. 물리 FK·참조 강제 트리거·자동 CASCADE는 사용하지 않는다. 관계 ID는 유지하고 PK/UNIQUE/NOT NULL/행 내부 CHECK를 DB가 강제한다.
3. 부모 존재·Workspace 일치·최신 권한·연결 세대는 공개 도메인 계약과 같은 UoW에서 검증한다. 초기에는 Workspace 행 잠금으로 짧은 쓰기를 직렬화한다. 외부 호출 동안 잠금을 유지하지 않는다.
4. cleanup·관리 작업도 같은 잠금 순서와 자식 우선 삭제를 따른다. 고아/교차 팀 참조 점검과 실제 PostgreSQL 경쟁 테스트를 구현 게이트로 둔다.
5. 테이블을 늘리지 않고 설치 state는 목적별 LoginAttempt, 시도 이력은 Job 제한 JSON, 파일별 RuleOutcome은 FileResult 제한 JSON으로 보관한다. Refresh는 계열 절대 만료를 사용한다.
6. SUSPENDED 연결도 저장소 배정을 유지한다. Review 선택은 서버가 결정해 기존 review_key를 유지하고, 호출 횟수·예산 예약 metadata를 ReviewRun에 둔다. 세부 비용/모델은 미정 상태로 유지한다.

## 대안

- 물리 FK/복합 FK: DB에서 참조 관계를 직접 강제할 수 있지만 사용자의 선택에 맞추어 채택하지 않는다.
- 존재 SELECT만 한 뒤 insert: 삭제·권한 변경과의 경쟁을 막지 못하므로 제외한다.
- 전역 SERIALIZABLE 또는 참조별 정교한 락: 현 단계에서 요구하지 않는다. Workspace 직렬화의 병목이 측정되면 별도 ADR로 검토한다.
- 관계·시도별 추가 테이블: 필요성이 생기면 확장한다. 현재는 한 행과 함께 읽는 작은 불변/제한 배열만 JSON으로 둔다.

## 영향과 한계

임의 SQL이나 프로토콜을 우회한 코드가 고아 데이터를 만들 수 있다. 애플리케이션 검증을 FK와 동등한 DB 강제 보장으로 표현하지 않는다. 한 Workspace의 쓰기 동시성은 제한되며 운영·cleanup도 소유 계약을 따라야 한다. 데이터 영구 삭제 자동화, 실제 모델·예산, 운영 호스팅은 이번에 확정하지 않는다.

이 변경은 설계 문서다. SQLAlchemy 모델·Alembic 업무 migration·실제 DB 적용·부하/동시성 검증은 미수행이다. 기존 빈 기준선 migration을 17개 구현 완료로 표현하지 않는다. 하네스·구현 저장소의 출처 pin·원격 Git은 이번 작업에서 변경하지 않는다.

## 소유 문서와 검증

[DATA_MODEL](../../contracts/DATA_MODEL.md), [DB-SCHEMA](../../contracts/schema/README.md), [Database](../../shared/database/README.md), [Testing](../../quality/TESTING.md)와 변경된 업무 세부 소유 문서를 연결한다. 문서 ID/링크/영역 매핑 및 선택기 회귀를 검증한다. 실행 단계에는 FK 0개·UNIQUE 경쟁·교차 테넌트 insert 거부·생성/삭제 경쟁·fence·rollback 테스트를 수행한다.
