# Shared: Global의 실제 Python 패키지

> ID: `SHARED` · 소유: `backend/app/shared` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: Global/Shared 코드의 위치를 판단할 때

이 문서는 기술 공통 코드의 입구다. 업무 개념은 [패키지 소유권 규칙](../PACKAGE_RULES.md)에 따라 domain에 남는다. `shared`는 domain을 import하지 않는다.

| 실제 패키지 | 소유 내용 | 해당 문서 |
|---|---|---|
| shared/config | 설정 로딩·시작 시 유효성 검증 | [Config](config/README.md) |
| shared/database | Engine·Session·UoW 기반·ORM Base | [Database](database/README.md) |
| shared/exception | 공통 예외 부모·HTTP 오류 변환 | [Exception](exception/README.md) |
| shared/security | token codec·해시·비밀 값 처리 기반 | [Security](security/README.md) |
| shared/github | HTTP adapter·설치 token·rate limit | [GitHub](github/README.md) |
| shared/jobs | 영속 큐·lease·재시도·handler registry | [Jobs](jobs/README.md) |
| shared/observability | 로그·trace ID·masking·metrics | [Observability](observability/README.md) |

WorkspaceRole, AnalysisStatus, Finding, PR Sync 정책, Review Prompt는 여기 넣지 않는다. `shared/llm`은 아직 만들지 않는다. 현재 LangChain을 사용하는 도메인은 review 하나이므로 그 내부에 둔다.

범용 `utils/`, `common/models.py`, 모든 도메인 ORM을 끌어오는 `database/models.py`도 만들지 않는다. ORM의 Alembic 등록은 조립 계층이 수행한다. 순수 UTC 함수처럼 작은 공통 코드가 필요하면 `shared/clock.py` 같이 책임이 드러나는 파일을 둔다.

Shared 공개 API 변경은 실제 소비 도메인의 문서·테스트까지 확인한다. 사용하지 않는 추상 factory·plugin system을 미래를 이유로 미리 만들지 않는다.
