# 조립 계층과 실행 배치

> ID: `BOOTSTRAP` · 소유: `backend/app/main.py|bootstrap.py|workflows.py|worker.py` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 앱 조립·도메인 흐름 연결·Worker 배치를 변경할 때

## 앱 파일 책임

최상위 **업무/공통 패키지**는 domain/shared 두 개만 둔다. 진입·조립용 파일은 app 바로 아래에 둘 수 있다.

```text
app/
├─ main.py          FastAPI 생성·router/handler/middleware 연결
├─ bootstrap.py     settings·client·UoW·공개 facade·Job registry 조립
├─ workflows.py     도메인 간 순서 연결, 업무 판정 자체는 위임
├─ worker.py        같은 Job handler를 쓰는 독립 실행 entrypoint
├─ domain/
└─ shared/
```

main에 업무 조건을 쓰지 않는다. bootstrap은 도메인 구현체를 import해 연결할 수 있다. shared와 domain 내부는 main/bootstrap/workflows를 import하지 않는다.

## 도메인 간 Workflow

연결 성공→PR 동기화는 repository→pull_request→repository 순환 import를 만들기 쉬운 사례다. repository `api.py`의 `ConnectRepositoryUseCase` Protocol을 router가 주입받고, root workflows의 구현체가 다음 순서를 조합한다.

```text
외부 설치 권한 확인 (DB transaction 밖)
  → 같은 UoW 안에서 repository의 연결 기록
  → pull_request의 초기 SyncRun + Job 기록
  → commit
```

각 도메인의 기록 함수는 자체 commit하지 않는다. workflow는 순서/원자성만 책임지며 OWNER 판정은 workspace, 저장소 연결 조건은 repository, 동기화 내용은 pull_request에 위임한다. 반복적인 업무 if를 bootstrap에 넣지 않는다.

Webhook Job은 webhook handler에서 공개 계약을 순서대로 호출한다. PR 동기화→새 snapshot 분석 접수까지 처리하되, 네트워크 취득과 DB 변경을 짧은 단계로 분리한다. AI는 MVP에서 별도 사용자 요청이므로 analysis→review 직접 의존성이 없다.

## Embedded와 External

개발/무료 데모는 `JOB_RUNNER_MODE=embedded`: FastAPI lifespan에 bounded runner 한 개를 등록하고 종료 시 claim을 멈추며 진행 중 작업 정리를 시도한다. 갑작스러운 종료는 lease 회수로 복구한다. lifespan은 앱 시작/종료 자원 관리를 위한 공식 연결 지점이다. [S-FASTAPI-LIFE](../reference/SOURCES.md#s-fastapi-life)

상시 운영은 `JOB_RUNNER_MODE=external`: web은 HTTP만, `python -m app.worker`는 동일 PostgreSQL 큐를 처리한다. 도메인 코드를 다시 쓰지 않는다. 이 전환 때문에 Kafka가 필요한 것은 아니다.

Registry 기본 handler는 `webhook.process`, `pull_request.sync`, `analysis.execute`, `review.explain`이다. handler factory는 attempt마다 새 세션/UseCase를 구성한다. shared Runner가 이 이름들을 알고 분기하지 않도록 bootstrap에서 등록한다.

## 검증

의존성 import cycle 없음, shared→domain 없음, bootstrap 없이 domain unit test 가능, 동일 handler의 embedded/external 실행, shutdown 중 접수 방지, 재기동 lease 복구, workflow rollback을 확인한다.
