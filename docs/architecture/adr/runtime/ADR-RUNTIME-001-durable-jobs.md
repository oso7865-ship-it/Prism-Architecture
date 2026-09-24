# ADR-RUNTIME-001: PostgreSQL 영속 Job과 복구

> ID: `ADR-RUNTIME-001` · 소유: `RUNTIME` · 기준: `2026-09-25`
> 읽는 때: 이 영역의 결정 배경이나 대체 여부를 검토할 때

- 상태: `BASELINE`
- 기록일: `2026-09-25`
- 근거: C-002
- 대체하는 ADR: 없음
- 대체한 ADR: 없음

## 배경

기존 문서의 설계 기본값을 이관하며 사용자 개별 승인·실행 검증으로 간주하지 않는다. 아래 대안은 기존 기록과의 대비이며 실제 벤치마크나 당시의 상세 논의를 재구성한 것이 아니다.

## 결정

핵심 Job은 PostgreSQL에 업무 레코드와 함께 저장한다. lease·fencing·멱등 저장으로 재시도와 오래된 Worker 완료를 처리한다.

## 대안

BackgroundTasks만으로 영속성을 대신하지 않는다. Redis/Kafka/MSA는 현재 MVP에 넣지 않는다.

## 영향과 한계

embedded runner 한 개는 초기 설계 기본값이다. external Worker 전환을 허용하며 무료 호스팅의 상시 실행은 보장하지 않는다.

## 소유 문서와 검증

- [소유 문서: shared/jobs/README.md](../../shared/jobs/README.md)
- [소유 문서: runtime/BOOTSTRAP.md](../../runtime/BOOTSTRAP.md)

문서 이관의 링크·ID·영역 매핑을 검증한다. 애플리케이션 구현·연동·성능 검증은 각 소유 문서의 테스트 기준을 적용하며 이 ADR 작성으로 완료 처리하지 않는다.
