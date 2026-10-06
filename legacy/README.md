# 레거시 보존 자료

현재 설계 문서를 압축하면서 **원문을 한 글자도 바꾸지 않고** 따로 보존한 폴더다. 현재 계약은 `docs/architecture`가 소유하며, 여기 문서는 당시 사실과 결정 경위를 확인할 때만 읽는다. 문서 검증(`validate_docs.py`)은 이 폴더를 검사하지 않는다. 내부 링크와 문서 ID는 원래 위치 기준이라 여기서는 동작하지 않는다.

## 압축 전 원문 (2026-10-06)

| 보존 원문 | 현재 문서 | 압축 내용 |
|---|---|---|
| [review/README.md](pre-compression-2026-10-06/review/README.md) | [Review](../docs/architecture/domain/review/README.md) | 시간순 보강 절을 주제별로 통합. 결과 JSON 필드 이력은 결과 스키마로 일원화 |
| [schema/RESULTS.md](pre-compression-2026-10-06/schema/RESULTS.md) | [결과 스키마](../docs/architecture/contracts/schema/RESULTS.md) | ADR별 보강 절을 표 한 장으로 압축. 테이블 컬럼 정의는 그대로 유지 |
| [schema/RELATIONS.md](pre-compression-2026-10-06/schema/RELATIONS.md) | [관계 안내](../docs/architecture/contracts/schema/RELATIONS.md) | 관계 표를 문단으로 압축하고 17개로 적혀 있던 테이블을 실제 20개로 정정(standard_documents·standard_versions 추가) |

## 이전 작업 기록

2026-09-28~30 개발 기록·하네스·평가 결과(39MB)는 [records](../records/README.md)에 있다. 파일 해시를 `records/manifest.json`으로 검증하고, 백엔드·프론트엔드 저장소의 `restore-docs.mjs`가 이 경로를 직접 읽으므로 위치를 옮기지 않았다.

## 이전 구현 저장소 README (2026-10-06)

백엔드·프론트엔드 README를 면접·외부 공개용으로 다시 쓰면서 이전 README를 [backend](pre-readme-2026-10-06/backend/README.md)·[frontend](pre-readme-2026-10-06/frontend/README.md)로 보존했다. 이 파일들은 Git에 올라간 적이 없는 로컬 파일이었고 백업 없이 덮어써서, 같은 세션에서 읽은 내용으로 복원했다(내용은 같고 줄바꿈 형식은 원본과 다를 수 있다). 링크는 구현 저장소 기준이라 여기서는 동작하지 않는다. 개발 절차·검증 이력은 [records](../records/README.md)와 각 저장소의 `reports/`를 따른다.
