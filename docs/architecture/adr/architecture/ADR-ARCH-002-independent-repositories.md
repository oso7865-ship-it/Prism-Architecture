# ADR-ARCH-002: 독립 저장소와 프로젝트별 하네스

> ID: `ADR-ARCH-002` · 소유: `ARCH` · 기준: `2026-09-25`
> 읽는 때: 구현 저장소와 개발 기반 변경 시

- 상태: `ACCEPTED`
- 기록일: `2026-09-25`
- 근거: 사용자 요청과 위임된 개발 기반 구성
- 대체하는 ADR: 없음 (기존 결정 보완)
- 대체한 ADR: 없음

## 배경

사용자가 백엔드·프론트 개별 공개 저장소와 기존 HARNESS 부착을 요청했다.

## 결정

Prism-Architecture, Prism-Backend, Prism-Frontend를 독립 저장소로 관리한다. 구현 저장소마다 원본 HARNESS의 지정 커밋 사본과 PROJECT_HARNESS 어댑터를 둔다. 상위 작업 폴더 하네스에 의존하지 않는다. architecture.json으로 설계 기준 커밋과 논리 경로를 매핑한다.

## 대안

공통 하네스를 상위 폴더 한 곳에만 두면 개별 clone 재개가 불완전하므로 사용하지 않는다. 실시간 사본 동기화 대신 원본 커밋 기준 수동 반입을 따른다.

## 영향과 한계

각 저장소의 lock·실행·검증·진행 기록을 공유한다. 하네스 원본 이력은 제품 상태가 아니며 Working Context와 최신 프로젝트 Report를 따로 초기화한다.

## 소유 문서와 검증

[구현 현황](../../runtime/IMPLEMENTATION.md), [패키지 규칙](../../PACKAGE_RULES.md), [DB](../../shared/database/README.md)를 동기화한다. 실행 결과는 구현 저장소 Report와 CI에서 확인한다.
