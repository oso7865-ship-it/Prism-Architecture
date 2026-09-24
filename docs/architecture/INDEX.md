# 아키텍처 문서 지도

> ID: `INDEX` · 소유: `documentation` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 작업에 맞는 문서를 찾거나 읽기 경로를 수정할 때

## 1. 가장 작은 진입 경로

처음은 [AGENTS](../../AGENTS.md)와 [CORE](CORE.md). 그다음 아래 표에서 **작업 대상만** 읽는다. 코드 변경 시 [패키지 규칙](PACKAGE_RULES.md)·[컨벤션](CODE_CONVENTIONS.md)을 추가한다. 같은 세션에서 이미 읽고 변경되지 않은 공통 문서를 매번 다시 로딩하지 않는다.

```bash
python scripts/context_select.py --task webhook
python scripts/context_select.py --task java-rule --mode edit
python scripts/context_select.py --path backend/app/domain/review/provider.py
```

선택기는 여러 `--task`/`--path`를 함께 받아 합집합을 만들고 중복을 제거한다. 매핑 안 된 경로에는 전체 문서를 대신 읽히지 않고 오류를 낸다. 사람이 대상 패키지를 확인해 매핑을 추가한다.

## 2. 패키지별 입구

| 작업 | 기본 문서 | 필요할 때만 추가 |
|---|---|---|
| 로그인/세션 | [Auth](domain/auth/README.md) | security·github·frontend |
| 사용자 프로필 | [User](domain/user/README.md) | auth |
| 팀/RBAC | [Workspace](domain/workspace/README.md) | database |
| 저장소 연결/규칙 설정 | [Repository](domain/repository/README.md) | github·bootstrap |
| 기존 PR/사람 리뷰 | [Pull Request](domain/pull_request/README.md) | sync·github |
| PR 동기화 | [Sync](domain/pull_request/SYNC_POLICY.md) | jobs·webhook |
| 분석 상태/결과 | [Analysis](domain/analysis/README.md) | contracts·jobs |
| 소스 취득/Diff | [Pipeline](domain/analysis/PIPELINE.md) | languages·privacy |
| 언어 Parser | [Languages](domain/analysis/LANGUAGES.md) | contracts·pipeline |
| Rule 엔진 | [Rule Engine](domain/analysis/RULE_ENGINE.md) | 해당 언어 Rule 목록 |
| 공통 Rule | [Common](domain/analysis/rules/COMMON.md) | languages |
| Java Rule | [Java](domain/analysis/rules/JAVA.md) | rule-engine·languages |
| Python Rule | [Python](domain/analysis/rules/PYTHON.md) | rule-engine·languages |
| JS/TS Rule | [JS/TS](domain/analysis/rules/JS_TS.md) | rule-engine·languages |
| LangChain/AI | [Review](domain/review/README.md) | privacy |
| Webhook | [Webhook](domain/webhook/README.md) | sync·jobs |
| 기술 공통 코드 | [Shared](shared/README.md) | 해당 shared 패키지 문서 |

## 3. 횡단 문서는 관련 작업에만

| 문서 | 읽는 이유 |
|---|---|
| [DIRECTORY_MAP](DIRECTORY_MAP.md) | 전체 소스 scaffold/패키지 이동 |
| [BOOTSTRAP](runtime/BOOTSTRAP.md) | 조립·Workflow·Worker 배치 |
| [HTTP_API](contracts/HTTP_API.md) | 외부 API/Response 변경 |
| [DATA_MODEL](contracts/DATA_MODEL.md) | DB 관계/FK/유일성 변경 |
| [FRONTEND](frontend/README.md) | 화면·Cookie/API 프록시 |
| [RENDER](operations/RENDER.md) | 배포·무료 환경 한계 |
| [PRIVACY](operations/SECURITY_PRIVACY.md) | 소스 반출·보관·삭제 |
| [TESTING](quality/TESTING.md) | 테스트/릴리스·구현 순서 |
| [DECISIONS](decisions/DECISIONS.md) | 선택 배경과 이전 설명 정정 |
| [OPEN_ITEMS](decisions/OPEN_ITEMS.md) | 아직 정하지 않은 외부 선택 |
| [SOURCES](reference/SOURCES.md) | 외부 기술 사실 재검증 |
| [PACKAGE_TEMPLATE](templates/PACKAGE_TEMPLATE.md) | 문서 분할/추가 |

## 4. 주제의 유일한 기준

역할/Permission → Workspace. PR event 정책 → PR Sync. Run/Finding 필드 → Analysis Contracts. 자원 상한 → Pipeline. 기술 queue/lease → Shared Jobs. AI 모델 입력/출력 → Review. 보관/삭제 → Privacy. 외부 endpoint → HTTP_API.

다른 문서는 위 정의를 복제하지 않는다. 구현 중 계약이 바뀌면 소유 문서 + 직접 소비자 + 테스트만 함께 갱신한다. `context-map.json`은 읽기 경로의 기계용 지도이며 비즈니스 정책을 정의하지 않는다.

## 5. 읽기 확대 조건

다른 domain의 api.py 변경, Shared 공개 API 변경, 상태/DB/API schema 변경, 보안 반출 경계 변경일 때 관련 소유 문서를 추가한다. 단순 함수/문구 수정 때문에 전체 아키텍처를 읽지 않는다. 단, 아직 모르는 필수 계약을 토큰 절약 이유로 생략하지 않는다.

검증: `python scripts/validate_docs.py`. 문서 글자 수와 선택 묶음의 크기는 재현 가능한 참고값이며 모델별 실제 토큰 사용량과 동일하지 않다.

## ADR 선택 경로

아키텍처 변경은 [ADR 규칙](adr/README.md)과 [영역 맵](decisions/DECISIONS.md)을 확인한다. `--task adr`는 작성 안내, `--task adr-review`·`--task adr-data` 등은 해당 영역의 이력만 선택한다. ADR 파일 경로도 영역별 작업으로 연결한다.
