# 코드 컨벤션과 좋은/나쁜 예시

> ID: `CONVENTIONS` · 소유: `architecture` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 백엔드 코드를 작성·리뷰할 때

## 기본 스타일

설계 기본값은 Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic 2.x다. 의존성의 정확한 버전은 설치 검증 후 lockfile에 고정한다. 검증하지 않은 '최신 버전'을 고정값처럼 적지 않는다.

모듈·함수·변수는 `snake_case`, 클래스는 `PascalCase`, 상수는 `UPPER_SNAKE_CASE`. 공개 함수의 인수·반환값은 타입 힌트를 붙인다. `Any`는 외부 JSON 수신 경계에서만 잠시 허용하고 즉시 검증된 모델로 바꾼다. ORM 타입과 외부 Response 타입을 분리한다.

Ruff format/check, 정적 타입 검사, pytest를 CI 기본 도구로 둔다. 도구 버전과 룰은 구현 시작 때 고정한다. 함수 길이 60줄·파일 길이 500줄은 검토 신호이지 무조건 실패 규칙이 아니다. 가독성을 희생해서 줄을 합치지 않는다.

## 1. Router에서 내부 DTO로 변환

```python
# 좋은 예: 프로젝트 계약을 보여주는 축약 예시이며 실행 완성본이 아니다.
@router.post("", status_code=202, response_model=AnalysisAcceptedResponse)
async def request_analysis(body: AnalysisCreateRequest,
                           principal: CurrentPrincipal,
                           service: AnalysisServiceDep) -> AnalysisAcceptedResponse:
    command = RequestAnalysis(principal=principal, pr_id=body.pr_id)
    result = await service.request(command)
    return AnalysisAcceptedResponse(analysis_id=result.analysis_id,
                                    status=result.status)
```

```python
# 나쁜 예: SQL·GitHub·AI·HTTP를 하나의 함수에서 처리한다.
@router.post("")
async def request_analysis(body: dict):
    row = await session.get(PullRequest, body["pr_id"])
    source = await github.fetch(row.url)
    explanation = await model.ainvoke(source)
    await session.commit()
    return {"source": source, "explanation": explanation}
```

Service는 Pydantic Response를 만들지 않는다. `RequestAnalysis`/`AnalysisAccepted`는 `domain/analysis/dto.py`에, HTTP 스키마는 `schema/`에 둔다. 직렬화 형식을 변경해도 분석 업무 로직을 고치지 않는 것이 목적이다.

## 2. 도메인 간 접근

```python
# 좋음: 소유자의 공개 계약을 가져온다.
from app.domain.workspace.api import WorkspaceAccess

# 나쁨: 다른 도메인의 저장 방식에 직접 의존한다.
from app.domain.workspace.repository import WorkspaceMemberRepository
from app.domain.workspace.models import WorkspaceMember
```

## 3. 권한 검사와 DB 스코프

```python
# 좋음: ID 존재 확인과 접근 권한 확인은 별개다.
await workspace_access.require_permission(principal, workspace_id,
                                          "analysis:run")
pr = await pull_requests.get_in_workspace(pr_id, workspace_id)
```

```python
# 나쁨: UUID라서 추측하기 어렵다는 이유로 인가를 생략한다.
pr = await session.get(PullRequest, request.pr_id)
```

Repository의 `WHERE workspace_id = ...`는 방어용 스코프이지 멤버십 검사의 대체가 아니다. user_id/workspace_id는 외부 JSON 값을 그대로 신뢰하지 않는다.

## 4. Job 접수와 실행 분리

```python
# 좋음: 같은 DB 트랜잭션에서 업무 레코드와 Job을 함께 기록한다.
async with unit_of_work.begin():
    result = await analysis_service.record_request(command)
    await job_store.enqueue(kind="analysis.execute", aggregate_id=result.id,
                            dedupe_key=result.execution_key)
# 이 commit 뒤에만 Router가 202를 보낸다.
```

```python
# 나쁨: 메모리 작업만 예약하면 프로세스 종료 시 접수 사실이 사라진다.
background_tasks.add_task(run_analysis, request_session, entire_source)
return {"status": "PENDING"}
```

Job에는 ID만 전달한다. Request의 Session·ORM 객체·원문 소스를 넘기지 않는다. Worker는 자기 세션을 연다. SQLAlchemy AsyncSession을 여러 동시 작업이 공유하지 않는다. [S-DB-01](reference/SOURCES.md#s-db-01)

## 5. async와 CPU 작업

`async def`는 CPU 분석을 자동으로 병렬화하지 않는다. HTTP/DB I/O는 async client로, 구문 분석은 시간·메모리 제한이 있는 별도 실행 프로세스로 격리한다. 락을 잡거나 DB 트랜잭션을 연 채 GitHub/LLM 응답을 기다리지 않는다. `sleep` 재시도 대신 Job `available_at`을 사용한다.

## 6. 예외와 로그

```python
# 좋음: 업무 실패를 표현하고 기술 원인은 체이닝한다.
def propagate_failure(exc: Exception) -> None:
    raise RepositoryAccessUnavailable() from exc

# 나쁨: 실패를 성공/빈 결과로 위장한다.
def hide_failure() -> list[object]:
    try:
        return read_findings()
    except Exception:
        return []
```

`except Exception`은 Runner·외부 어댑터 같은 최외곽 실패 경계에서만 제한적으로 쓰며 실패 상태를 기록하고 원인을 마스킹한다. 전역 Handler는 사용자에게 trace_id와 공개 메시지만 반환한다. 토큰·요청 본문·소스·Diff·LLM Prompt·전체 예외 객체를 로그에 남기지 않는다.

## 7. 정책은 테스트 가능한 함수로

DB 연결 없이 역할과 상태를 받아 Permission을 판단하는 함수를 둔다. 'if/elif는 무조건 나쁘다'는 규칙은 없다. 작은 분기는 허용하고 이벤트가 늘어날 때 registry로 옮긴다. 추상화는 교체점·테스트 경계가 있을 때 만든다.

수정한 코드에는 정상·실패·권한 없음·중복 입력 테스트를 최소 단위로 붙인다. 라이브러리의 기능, 프로젝트가 정한 정책, 예제의 단순화를 구별한다.
