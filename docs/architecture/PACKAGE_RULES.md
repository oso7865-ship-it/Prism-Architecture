# 패키지 소유권과 의존성

> ID: `PACKAGE-RULES` · 소유: `architecture` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 파일 배치·import·공개 계약을 수정할 때

## 1. Global의 실제 이름

논리적인 구분은 **Domain / Global**을 유지한다. 실제 Python 폴더는 `app/domain/`와 `app/shared/`다. `global`은 예약어라 `from app.global.config import Settings`는 일반 import 문법으로 사용할 수 없다. 동적 import로 우회하지 않는다. [근거 S-PY-01](reference/SOURCES.md#s-py-01)

## 2. 배치 판단 순서

1. 특정 업무 개념·정책의 소유자가 있으면 그 도메인에 둔다. 재사용 횟수는 소유권을 바꾸지 않는다.
2. 도메인 중립이고 여러 도메인이 사용하는 기술 기능이면 `shared`에 둔다.
3. 한 도메인만 쓰는 기술 어댑터는 우선 그 도메인에 둔다. 앱 전체 초기화·DB 기반·관측처럼 횡단 책임 자체가 명확한 기능은 예외적으로 `shared` 소유다.
4. 애매하면 가까운 도메인에 두고 추출 근거가 생길 때 이동한다. '언젠가 쓸 것 같다'만으로 올리지 않는다.

| 코드 | 위치 | 이유 |
|---|---|---|
| WorkspaceRole·멤버 권한 | domain/workspace | 팀 권한 정책의 소유자 |
| AnalysisStatus·Finding·언어별 Parser | domain/analysis | 분석 업무의 의미 |
| PR 정렬·동기화 정책 | domain/pull_request | PR 이력 소유자 |
| 코드 설명 Prompt·출력 모델 | domain/review | AI 리뷰 업무 계약 |
| GitHub HTTP transport·재시도 헤더 | shared/github | 여러 도메인의 중립 연동 |
| Review만 쓰는 LLM factory | domain/review/provider.py | 지금은 한 업무만 사용 |
| DB Session·AppException·로그 마스킹 | shared | 횡단 기술 기반 |

**LLM 코드를 무조건 shared/llm으로 보내지 않는다.** 현재는 review만 LLM을 사용하므로 review 내부에 둔다. 실제 두 번째 도메인 소비자가 생기면 provider 연결만 추출하고 Prompt/업무 출력은 남긴다.

## 3. 의존 방향

```text
main / bootstrap / workflows   조립과 도메인 간 흐름 연결
            ↓
domain.<owner>.api             외부에 허용된 계약
            ↓
도메인 내부 Service → Repository / Policy / Parser
            ↓
shared                        기술 기반
```

`shared → domain` import는 금지한다. shared Job Runner는 handler registry를 주입받으며 도메인 상태·Job 종류를 하드코딩하지 않는다.

다른 도메인의 `api.py`만 import한다. `api.py`는 공개 DTO/Protocol과 안정된 진입 계약만 노출하고 ORM·DB 세션·HTTP Response를 반환하지 않는다. Protocol 구현체 조립은 bootstrap이 담당한다.

| 소비 도메인 | 허용하는 다른 도메인의 공개 계약 |
|---|---|
| user | 없음 |
| auth | user |
| workspace | user |
| repository | workspace |
| pull_request | repository, workspace |
| analysis | pull_request, repository, workspace |
| review | analysis, repository, pull_request, workspace, standards |
| standards | repository, workspace, analysis(구문 판독 API) |
| webhook | repository, pull_request, analysis |

위 표는 업무 의존성이다. 각 Router의 `auth.api` 인증 주체 타입 참조는 별도로 허용한다. FastAPI Depends alias는 해당 도메인의 dependencies.py에서 조립하며 auth 내부 구현을 import하지 않는다.

연결 직후 PR 동기화처럼 위 표와 반대 방향인 흐름은 [조립/흐름 문서](runtime/BOOTSTRAP.md)의 주입된 UseCase로 연결한다. 순환 import를 만들거나 shared로 업무를 밀어 넣지 않는다.

## 4. 각 파일 책임

| 파일/폴더 | 허용 | 금지 |
|---|---|---|
| router.py | 입력·인증 의존성·Service 호출·Response 변환 | SQL·LLM 직접 호출·업무 권한 판정 |
| service.py / service/ | 업무 조합·인가·트랜잭션 경계 | HTTPException·Request/Response 정의·직접 SQL |
| repository.py / persistence/ | ORM 조회/저장·원자적 조건 갱신 | 사용자 역할 판정·자율 commit |
| models.py | ORM 매핑·DB 제약 | 외부 HTTP·AI 호출 |
| schema/request.py | 입력 형식·길이 검증 | DB 기반 권한/존재 검사 |
| schema/response.py | 외부 응답 허용 필드 | 내부 토큰·원문 코드 |
| dto.py / contracts.py | 내부 Command/Result/값 타입 | FastAPI Request/Response 의존 |
| policy.py / permission.py | 순수 업무 결정 | DB 연결·HTTP 응답 |
| exceptions.py | AppException을 상속한 도메인 오류 | 모든 오류를 shared에 집중 |
| dependencies.py | 도메인 의존성 연결 | 권한 정책 복제·거대 전역 객체 생성 |

Service가 같은 도메인의 Repository를 호출하는 것은 정상이다. 선택한 계층 규칙에 따라 **Router→Repository 직접 접근**을 제한한다. 프로젝트마다 계층 매핑을 설정하며 클래스 이름만으로 아키텍처 위반을 확정하지 않는다.

## 5. 크기와 분리

작은 도메인은 파일형으로 시작한다. `service.py`가 서로 다른 UseCase를 많이 갖게 되면 `service/connect_repository.py`처럼 책임별로 나눈다. 줄 수만으로 자동 분할하지 않는다. 같은 이름의 `service.py`와 `service/`를 동시에 두지 않는다. 빈 폴더·한 클래스당 무조건 파일 생성·무의미한 Utils를 금지한다.

## 문서 게시 경계

[ADR-ARCH-003](adr/architecture/ADR-ARCH-003-central-documentation.md)에 따라 README/설계/작업기록/개발 하네스는 Prism-Architecture records에서 관리하고 구현 저장소에는 코드·설정·테스트·.prompt 실행 리소스만 게시한다. architecture.json의 고정 커밋과 복원 스크립트로 로컬 문서를 되살린다. 과거 이력은 재작성하지 않는다.

팀 문서·불변 버전·섹션 검색·적용 규칙은 [standards](domain/standards/README.md)가 소유한다. 공통 비밀 의심 정규식만 domain 중립 shared/content_safety.py에 둔다. 문서 원문을 review가 직접 ORM 조회하지 않는다.
