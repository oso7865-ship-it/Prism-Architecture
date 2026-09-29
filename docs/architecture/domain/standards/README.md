# 팀 문서와 규칙 검색

> ID: `STANDARDS` · 소유: `backend/app/domain/standards` · 기준: `2026-09-29`
> 읽는 때: 팀 컨벤션·패키지 문서, 섹션 검색, 문서 기반 리뷰를 바꿀 때

[ADR-REVIEW-012](../../adr/review/ADR-REVIEW-012-purpose-and-team-standards.md)이 결정 기준이다. 상세 구현/검증은 [작업 계획](../../../../records/2026-09-29_review-modes-plan.md)이 추적한다.

## 소유와 권한

standards는 문서·버전·인덱스·적용 경로·구조화 규칙의 소유자다. router는 HTTP, service는 권한/잠금/버전 정책, repository는 SQL, index는 순수 검증·분할·검색, api는 review에 공개하는 고정 버전 스냅샷과 규칙 평가다. import 구문 판독은 analysis.api를 사용하고 업무 설정을 shared로 옮기지 않는다.

팀 owner만 저장/비활성화/삭제하며 member는 읽는다. 문서는 workspace와 연결된 repository에 귀속한다. 모든 조회가 양쪽을 확인한다. 변경은 기존 Workspace 잠금 프로토콜을 재사용한다. snapshot API는 인가한 review service/worker 내부 전용이며 외부 HTTP에 직접 노출하지 않는다.

## 저장과 버전

원문은 UTF-8 Markdown/텍스트 최대64KiB, 요청 JSON 최대256KiB. 8문서/저장소, 20버전/문서, 구조화 규칙20개/버전. 비밀 의심 내용과 제어 문자·절대/상위 경로를 거부한다. HTML은 실행/렌더링하지 않고 텍스트로 표시한다. PDF·Word·URL 원격 취득은 제공하지 않는다.

| 테이블 | 컬럼 | 의미와 관계 |
|---|---|---|
| standard_documents | id(UUID PK), workspace_id, repository_connection_id, created_by | 소유 팀/저장소/생성자 논리 참조. 물리 FK 없음 |
| standard_documents | current_version(int >0), active(bool), created_at/updated_at(timestamptz) | 최신 버전과 리뷰 사용 여부. 팀/저장소 복합 인덱스 |
| standard_versions | id(UUID PK), workspace_id, document_id, version(int >0), created_at | 불변 버전. document_id+version UNIQUE, 팀+문서 조회 인덱스 |
| standard_versions | title(varchar120), kind(CONVENTION/STRUCTURE), content(text), digest(varchar64) | 제목/종류/원문/내용과 설정의 SHA-256 |
| standard_versions | config(JSONB), sections(JSONB) | 적용·제외 패턴/전체 필수 여부/규칙, 섹션 ID/제목/본문/어휘 인덱스 |

expected_version이 최신과 다르면409로 덮어쓰기 경쟁을 막는다. 이전 버전을 선택해 저장하면 새 버전으로 복원한다. 사용 중지는 원문을 지우지 않는다. DELETE는 모든 버전 원문/인덱스를 같은 트랜잭션에서 삭제한다. 과거 리뷰의 출처 메타데이터와 판단은 유지하며 삭제된 원문은 다시 열 수 없다. 백업 사본은 운영 보관 정책을 따른다.

## 검색과 검사

헤더를 따라 최대1200자 섹션으로 나누고 저장 시 토큰 빈도를 계산한다. 영어 코드 식별자의 camel case와 한글 어절/2글자 조각을 사용한다. 코드블록 안의 #는 제목으로 해석하지 않는다. 문서 수정 때만 이 인덱스를 다시 만든다.

적용 경로/예외를 먼저 검사한다. 필수 문서 섹션 전체를 보호하고 나머지는 BM25 순서로 선택한다. 선택 문서는 코드 입력과 합쳐60KiB 이내, 문서 섹션은 최대12KiB이며 파일 경로/메타데이터가 남는 예산을 사용한다. 선택적 섹션은 최대12개, 필수 섹션에는 이 개수 제한을 적용하지 않는다. 필수 섹션이 넘치면 STANDARDS_REQUIRED_TOO_LARGE, 관련 섹션이 없으면 STANDARDS_NO_MATCH로 외부 호출 전 중단한다. 요청 접수 자체는 팀 하루 횟수에 포함된다.

임베딩/벡터 DB/리랭커 없이 어휘 검색을 사용한다. 필수 섹션도 양수 점수의 섹션도 없으면, 이미 적용 경로를 통과한 문서에서 원래 순서로 같은 예산 안의 섹션을 선택한다. 한국어 문서와 영문 코드의 단어 불일치에 대한 제한적 대안이며 scope_fallback=true로 표시한다. 의미상 유사하지만 다른 표현을 사용하는 규칙은 여전히 누락될 수 있다. 후보/미포함 섹션 수·버전·선택된 출처를 결과에 명시하며 전체 문서 검토라고 표시하지 않는다.

NAME_SUFFIX는 파일명 끝, PATH_PREFIX는 지정 폴더 아래 위치, FORBIDDEN_IMPORT는 해당 패키지 또는 하위 패키지의 정적 import를 검사한다. 후자는 제공된 변경 줄만 판독하고 동적 import·보이지 않는 import를 확인하지 않는다. CHECKED는 경로 조건 확인, LIMITED는 import 검사 범위 제한, VIOLATION은 지정 조건 불일치다. LLM 판단·취약점 확정과 별개다. 전체 적용 규칙을 검사하여 검색 순위로 규칙을 제거하지 않는다.

## 리뷰 연결과 인용

리뷰 요청 시 활성 버전 ID를 고정하여 이력/멱등 키에 넣는다. 새 버전 저장은 실행 중 입력을 바꾸지 않는다. 비활성화/삭제는 이후 예약·전송/결과 확정을 차단한다. 읽고 실행하는 동안 사용자가 동시에 삭제하면 이미 외부에 전달한 호출을 회수할 수는 없다.

팀 규칙 출력에는 전달된 섹션 ID 1~4개와 적용 파일·코드 줄을 요구한다. 존재하지 않거나 그 파일에 적용되지 않는 인용은 거부한다. 코드와 문서는 모두 비신뢰 입력이며 시스템 지시로 합치지 않는다. 문서 인용의 존재 검증은 의미적 일치 증명이 아니므로 동일 제공자 검증 호출도 규칙 적용과 개선안의 타당성을 다시 확인하도록 요청한다.

## HTTP와 화면

기본 경로 `/api/v1/workspaces/{wid}/repositories/{repo}/standards`:

| 요청 | 동작 |
|---|---|
| GET / | 현재 문서 목록 |
| POST /preview | 저장/외부 호출 없이 섹션 확인 |
| POST /, PUT /{id} | 등록/새 버전 저장 |
| GET /{id}/versions, GET /{id}/versions/{number} | 버전 목록/고정 버전 원문 |
| PATCH /{id} | active+expected_version 사용 중지/재개 |
| DELETE /{id}?expected_version=N | 전체 버전 삭제 |

저장소의 ‘팀 문서 관리’에서 등록/편집/버전 열람/규칙 추가, PR의 ‘팀 규칙’에서 요청과 결과를 본다. 출처 버튼은 해당 문서 버전의 해당 섹션을 사이트 안에서 텍스트로 연다. 문서 추가만으로 유료 호출하지 않는다.

본문 편집/파일 교체 시 기존 섹션 목록과 규칙의 섹션 선택을 무효화한다. 규칙 값·적용 경로는 보존하며 새 섹션 확인 후 각 근거를 재선택해야 저장할 수 있다. 섹션 번호는 본문 순서에 따라 달라지므로 이전 번호를 자동 승계하지 않는다. 인용의 팀/저장소/문서/버전/섹션 변경 시 열린 본문을 지우고 이전 지연 응답을 무시한다. Markdown 코드 펜스는 같은 구분자와 길이 이상의 닫힘만 인정해 내부 예제를 제목으로 분리하지 않는다. 저장된 과거 버전은 다시 인덱싱하지 않는다.
