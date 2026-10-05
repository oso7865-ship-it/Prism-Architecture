# 정적 분석·AI 결과 테이블 5개

> ID: `DB-RESULTS` · 소유: `data-contracts` · 기준: `2026-09-25`
> 읽는 때: 분석 snapshot·파일별 평가·Finding·AI 저장을 구현할 때

[공통 타입·관계 규칙](README.md)을 적용하며 공통 id/created_at을 더한다. 의미는 [Analysis Contracts](../../domain/analysis/CONTRACTS.md), [Rule Engine](../../domain/analysis/RULE_ENGINE.md), [Review](../../domain/review/README.md)가 소유한다.

<a id="table-analysis_runs"></a>

## analysis_runs

| 컬럼 | 타입 | NULL | 기본값·의미 |
|---|---|---|---|
| workspace_id / repository_connection_id / pr_id | uuid | N | 같은 팀의 부모 논리 참조 |
| connection_generation | integer | N | > 0, 연결 세대 snapshot |
| actor_type | varchar(16) | N | USER/SYSTEM CHECK |
| requested_by | uuid | Y | USER일 때만 users 논리 참조 |
| base_sha / head_sha | GitSHA | N | 불변 입력 |
| merge_base_sha | GitSHA | Y | 접수 시 확인된 경우 고정, 사후 입력 변경 금지 |
| rule_set_version | varchar(64) | N | 서버 Rule 집합 버전 |
| config_version_id | uuid | N | rule_config_versions 논리 참조 |
| effective_config_digest / analyzer_build_digest | H256 | N | 불변 입력 digest |
| scope | varchar(24) | N | PR_CHANGED_FILES CHECK, MVP 범위 |
| generation | integer | N | 0 기본, >= 0; 명시적 재분석 때 증가 |
| execution_key | H256 | N | 버전·snapshot·범위·세대 정규화 해시 |
| status | varchar(16) | N | PENDING 기본; PENDING/RUNNING/COMPLETED/FAILED/CANCELED |
| coverage_status | varchar(16) | Y | terminal 결과 확정 전 NULL; FULL_SCOPE/PARTIAL/NONE |
| coverage_reason | varchar(64) | Y | 범위 누락·지원 파일 없음 코드 |
| total_files / included_files / excluded_files / failed_files / not_evaluated_rules / finding_count | integer | N | 각각 0 기본, >= 0 |
| started_at / finished_at | timestamptz | Y | 시작/terminal 시각 |
| error_code | varchar(64) | Y | 공개 실패 코드 |
| updated_at | timestamptz | N | now() |

UQ(execution_key). IDX(workspace_id,pr_id,created_at DESC,id DESC), IDX(repository_connection_id,status,id), IDX(config_version_id), IDX(finished_at) WHERE finished_at IS NOT NULL. CHECK actor/requested_by 대응, status/coverage 허용 목록, terminal↔finished_at, COMPLETED이면 coverage_status NOT NULL.

실행 키에는 workspace·연결 ID/세대·PR·base/head·nullable merge_base·rule_set·config ID/digest·analyzer digest·scope·generation을 포함한다. actor는 제외한다. 자동/일반 요청의 generation=0, 명시적 재분석은 Workspace 잠금 아래 같은 기본 입력의 최대 generation+1을 배정한다. run/Job 재시도는 같은 행을 사용한다. HTTP idempotency key별 별도 매핑은 이번 17개 설계에 포함하지 않으며 지원한다고 광고하지 않는다.

완료 결과 묶음은 한 transaction에 저장하고 terminal 전이와 Job fence를 함께 검사한다. 기본 통계 분할은 included+excluded+failed=total이며 source/parse/limit 실패는 failed에 집계한다. 규칙 평가 실패 수는 파일 실패 수와 별도다. 소스/AST/diff 컬럼은 없다.

<a id="table-analysis_file_results"></a>

## analysis_file_results

| 컬럼 | 타입 | NULL | 기본값·의미 |
|---|---|---|---|
| workspace_id / analysis_id | uuid | N | 같은 팀 analysis_runs 논리 참조 |
| file_path | text | N | 저장소 내 정규화 경로 |
| path_digest | H256 | N | 정규화 경로 UTF-8 SHA256 |
| side | varchar(8) | N | HEAD/BASE/FILE CHECK |
| language | varchar(16) | Y | JAVA/JAVASCRIPT/TYPESCRIPT/PYTHON, 미지원은 NULL |
| source_sha | GitSHA | Y | 확인된 파일 blob ID, 원문 아님 |
| status | varchar(24) | N | INCLUDED/EXCLUDED/SOURCE_UNAVAILABLE/PARSE_ERROR/LIMIT_EXCEEDED CHECK |
| reason_code | varchar(64) | Y | 상태 이유 |
| finding_limit_reached | boolean | N | false 기본, 파일별 Finding 상한으로 결과가 잘린 경우 true |
| rule_outcomes | jsonb | N | [] 기본, array CHECK |

UQ(analysis_id,side,path_digest), IDX(workspace_id,analysis_id,status,id). 경로 최대 UTF-8 4,096 bytes를 CHECK(octet_length(file_path) BETWEEN 1 AND 4096)로 제한한다. 큰 text 전체를 UNIQUE 인덱스 키로 사용하지 않는다. digest 충돌 시 원 경로를 비교하고 불일치하면 실패 처리한다.

rule_outcomes 요소는 {rule_id,rule_version,status,reason_code}만 허용한다. status는 EVALUATED/NOT_APPLICABLE/NOT_EVALUATED, 같은 파일의 (rule_id,rule_version)는 중복 불가, 서버 활성 Rule 수 이하이며 정규화 JSON 64 KiB 이하로 검증한다. 별도 Rule 결과 테이블 대신 범위 표시를 위한 작은 불변 결과 배열이다. error 원문·구조 트리·코드 수치는 무제한으로 넣지 않는다. terminal 결과는 수정하지 않는다.

<a id="table-findings"></a>

## findings

| 컬럼 | 타입 | NULL | 기본값·의미 |
|---|---|---|---|
| workspace_id / analysis_id | uuid | N | 같은 팀 분석 논리 참조 |
| rule_id / rule_version | varchar(64) | N | 검출 규칙 |
| category | varchar(24) | N | ARCHITECTURE/SECURITY/RELIABILITY/MAINTAINABILITY/STYLE/PERFORMANCE CHECK |
| severity | varchar(16) | N | INFO/WARNING/ERROR/CRITICAL CHECK |
| confidence | varchar(8) | N | HIGH/MEDIUM/LOW CHECK |
| language | varchar(16) | Y | JAVA/JAVASCRIPT/TYPESCRIPT/PYTHON CHECK, 미지원 텍스트의 Secret 등 언어 중립 Finding은 NULL |
| file_path | text | N | 비공개 경로, 1~4,096 UTF-8 bytes |
| start_line / end_line | integer | Y | 1-based inclusive 위치 |
| side | varchar(8) | N | HEAD/BASE/FILE CHECK |
| scope_location | varchar(8) | N | CHANGED/CONTEXT/FILE CHECK |
| message_code | varchar(64) | N | 서버 메시지 식별자 |
| sanitized_message | varchar(2000) | N | 정제된 설명, source/secret 포함 금지 |
| fingerprint | H256 | N | run 안의 중복 제거 |

UQ(analysis_id,fingerprint). IDX(workspace_id,analysis_id,id), IDX(analysis_id,severity,id). CHECK 두 line 모두 NULL 또는 둘 다 NOT NULL이고 start_line>=1 및 end_line>=start_line. severity 문자열 사전순을 중요도 순서로 사용하지 않는다. 우선순위 정렬은 명시적 CASE 매핑을 사용한다. 불변 결과이며 다른 commit의 동일 이슈 ID로 해석하지 않는다. 언어 중립 Rule만 language NULL을 허용하도록 registry와 서비스에서 확인한다.

<a id="table-review_runs"></a>

## review_runs

ADR-REVIEW-003에 따른 0006 구현 계약. 공통 id/created_at 및 updated_at을 갖는다. 물리 FK 없음.

| 컬럼 | 타입 | NULL | 의미 |
|---|---|---|---|
| workspace_id / analysis_id / requested_by | uuid | N | 팀·완료 분석·요청 사용자 논리 참조 |
| pr_id / repository_connection_id | uuid | N | 분석과 동일한 PR·연결 논리 참조 |
| connection_generation | integer | N | 접수 당시 연결 세대 >0 |
| head_sha | varchar(40) | N | 검증된 40자리 HEAD SHA |
| model | varchar(80) | N | 실제 DeepSeek 모델 |
| prompt_version / policy_version | varchar(32) | N | rh1-16hex 하네스 digest / 신규 BOUNDED_CODE_V2 (과거 V1 보존) |
| generation | integer | N | 0 기본, 명시 재실행 세대 >=0 |
| mode | varchar(8) | N | 'SENIOR' 기본, SENIOR/JUNIOR CHECK(ck_review_mode). 접수 시 요청자 프로필 모드를 고정하며 execution_key에 포함, migration 0010 |
| execution_key | varchar(64) | N | 실행 입력 digest UNIQUE |
| status | varchar(16) | N | PENDING 기본; RUNNING/COMPLETED/FAILED/CANCELED |
| consented_at | timestamptz | N | 소유자의 이번 요청 동의 시각 |
| started_at / finished_at | timestamptz | Y | 시작/종료 시각 |
| call_attempts | integer | N | 0 기본, 0~2 CHECK; 매 외부 호출 전 commit |
| input_tokens / output_tokens | integer | N | 0 기본, 관측 사용량 >=0; 미확인은 usage_uncertain과 함께 읽음 |
| usage_uncertain | boolean | N | false 기본; 호출 후 실패/취소 때 청구 미확인 |
| error_code | varchar(64) | Y | 정제된 실패 코드 |
| result | jsonb | Y | 검증된 summary/issues/limitations/scope/reviewed_files/omitted_files |
| updated_at | timestamptz | N | now(), 애플리케이션 갱신 |

terminal↔finished_at, COMPLETED이면 result 존재, SHA/digest 형식 CHECK. IDX(workspace_id,analysis_id,created_at,id), IDX(workspace_id,created_at). API/worker가 JSON strict schema와 파일·줄을 검증한다. 금액 예약/정산 대신 UTC 접수일별 최대30회와 출력 상한을 적용한다. 실패·취소도 한도를 소비한다. 원문 코드·diff·prompt·응답 원문은 저장하지 않는다.

<a id="table-finding_explanations"></a>

## finding_explanations — 초기 구현에서 제외

ADR-REVIEW-003에서 검증된 review_runs.result JSON으로 대체했다. 별도 테이블이나 Finding 외래 참조를 만들지 않는다. 정적 findings는 불변이며 AI 실패와 독립적이다.

## 검토 범위 metadata — 2026-09-26

새 성공 결과의 result.coverage는 서버가 files(file_id,file_path,provided_lines), excluded(file_path 또는 null,reason), unfetched_files(수 또는 null)를 기록한다. 모델 입력에는 경로/coverage를 추가하지 않는다. 비밀 의심 내용이나 원문 patch는 보관하지 않으며 유효하지 않거나 민감 패턴이 있는 경로는 null로 숨긴다. 제외 사유와 첫100개 밖 미취득 수를 구분한다. 과거 결과는 coverage 필드가 없고 상세 미기록 안내만 표시한다. 기존 결과 역추정·수정과 DB migration은 없다. UI는 고정 HEAD 파일 링크와 텍스트 사유를 표시한다.

ADR-REVIEW-004: 새 result.harness는 version/modules/system_digest를 포함한다. issues.basis는 SUPPORTED/NEEDS_CONTEXT이며 서버 schema와 중요도 조합을 검증한다. 기존 JSON에는 없을 수 있다. prompt_version에 하네스 패키지+schema digest를 사용하므로 DB 컬럼 추가는 없다.

ADR-REVIEW-009: 새 result.summary는 검증된 issues/questions 건수와 우선 제목 최대3개로 서버가 조합하는 문자열이다. 모델 자유 요약은 strict 검증 후 사용하지 않으며 별도 저장하지 않는다. 질문을 확정 결함으로 바꾸지 않고0건은 제공 범위의 지적 없음으로 표시한다. 기존 문자열 타입/1600자 상한과 과거 결과는 유지하며 migration은 없다.

## AI 근거 계약 보강 (2026-09-26)

ADR-REVIEW-005: 새 issue는 evidence_lines(제공 줄 1~8개, 중복 금지·대표 line과 변경 줄 포함), trigger/consequence(각1~400자), assumptions(최대3개, 각1~400자)를 포함한다. SUPPORTED는 빈 assumptions, NEEDS_CONTEXT는 명시한 미확인 전제가 필요하다. 구조 위반은 응답 전체를 거부하며 지적을 조용히 제거하지 않는다. 구조 검증이 자연어 근거의 진실성을 보장하지 않는다. 과거 결과는 그대로 읽고 신규 UI 필드는 선택적이다. 원문 소스 인용 필드는 없으며 DB migration은 없다.

<a id="table-review_feedback"></a>

## review_feedback — 0007

개인별 지적 처리 기록. 공통 id UUID PK와 created_at timestamptz NOT NULL DEFAULT now()를 사용한다.

| 컬럼 | 타입 | NULL | 의미 |
|---|---|---|---|
| workspace_id | uuid | N | workspaces.id 논리 참조; review의 팀과 일치 |
| review_id | uuid | N | review_runs.id 논리 참조; 완료 결과만 |
| user_id | uuid | N | users.id 논리 참조; 현재 요청자 본인 |
| issue_key | varchar(64) | N | 결과의 경로·정규화 제목 SHA-256 |
| state | varchar(20) | N | OPEN/ACKNOWLEDGED/PLANNED/INTENDED/FALSE_POSITIVE |
| note | varchar(500) | N | DEFAULT ''; 비밀 의심 메모 거부 |
| updated_at | timestamptz | N | DEFAULT now(); 애플리케이션 갱신 |

UNIQUE(review_id,user_id,issue_key), CHECK state 및 64자리 소문자 hex. INDEX(workspace_id,user_id,updated_at). Workspace와 review 잠금 아래 부모·팀·작성자·key를 검증한다. 물리 FK 없음. 자신의 상태를 언제든 덮어쓸 수 있으며 동일 회차 동시 쓰기는 직렬화한다. 결과 JSON은 수정하지 않는다. Review/사용자 영구 삭제 시 보관 정책에 따라 먼저 이 자식 기록을 명시적으로 삭제한다. MVP에 영구 삭제 API는 없다. 금액/수량 컬럼 없음.

ADR-REVIEW-006 이후 result는 issues/questions/classification 및 확장 coverage를 제공한다. 원문 코드는 DB에 저장하지 않는다.

ADR-REVIEW-010: call_attempts CHECK를0..2로 완화하는 migration0008. result.verification은 CHECKED/NO_CANDIDATES와 kept/revised/dropped 집계다. 검증 장애는 FAILED, 초안은 미보관. 관측 사용량은 두 호출 합계이며 실패 시 첫 호출의 관측값을 보존한다. 이전 결과에 필드가 없으면 재검증으로 표시하지 않는다.

ADR-REVIEW-011: 신규 빈 초안은 두 번째 호출을 필수로 하며 result.verification.status=EMPTY_RECHECKED와 file_checks 배열을 보관한다. 각 항목은 file_id/file_path/line/outcome(FINDING/NO_FINDING/LIMITED)/observation(최대240자)다. 이는 간단한 검토 결과이며 소스나 숨은 추론은 보관하지 않는다. CHECKED의 집계는 유지하고 과거 NO_CANDIDATES는 소급 변경하지 않는다. DB DDL 변경은 없다.

## 목적별 리뷰 — migration0009

ReviewRun.purpose varchar16 NOT NULL DEFAULT CODE, CHECK(CODE/SECURITY/STANDARDS). ReviewRun.standard_versions JSONB NOT NULL DEFAULT []는 고정한 StandardVersion UUID 문자열 목록이며 물리 FK는 없다. 목적/문서 버전 목록을 실행 키에 포함한다. 과거 row/result의 내용은 변경하지 않고 CODE 기본값만 제공한다. 새 결과는 purpose, 팀 규칙 결과는 standards/standard_sources/standard_checks를 추가한다. AI 항목 citations는 허용된 문서/버전/섹션 제목 메타데이터이며 원문은 넣지 않는다.

[팀 문서](../../domain/standards/README.md)의 스키마가 신규 두 테이블을 정의한다. 다운그레이드는 새 문서나 CODE 이외의 리뷰가 남으면 원자적으로 거부하여 데이터 손실을 막는다.


## ADR-REVIEW-013 — 결과 보강, DDL 변경 없음

verification.CHECKED는 added와 file_checks를 추가한다. 첫 출력 형식 실패를 독립 재검토로 복구하면 OUTPUT_RECOVERED, 빈 초안 재검토는 EMPTY_RECHECKED다. file_checks.line은 서버가 선택한 대표 변경 줄이며 issue.evidence_lines와 별개다. 구형 필드는 그대로 읽고 결과를 소급 변경하지 않는다.

issue.suggestion_check는 status(NOT_VERIFIED/SOURCE_MISMATCH/PRESERVES_SAMPLES/CHANGES_SUCCESSFUL_SAMPLES), samples, 선택 counterexamples(inputs/before/after 최대2개), scope, inferred_from_text를 갖는다. 이는 서버가 작성한 제한 예시의 값 비교이며 대상 프로그램 실행 결과가 아니다. 파일 원문과 before/after 소스 식은 저장하지 않는다.

coverage.context_supplement는 file_id/symbol/status(ADDED/ALREADY_PROVIDED/UNAVAILABLE/SYMBOL_NOT_PROVIDED/SOURCE_MISMATCH/FILE_TOO_LARGE/BUDGET_LIMIT)다. 독립 security_evidence는 rule_id/file_id/file_path/line/source_line/evidence_lines/severity/title/detail. AI 실패 시에도 권한이 유지되면 FAILED 상태와 별도 보안 신호 부분 결과를 제공할 수 있다. 부분 결과의 summary·limitations는 AI 미완료를 명시한다. UI가 실패를 정상0건으로 표현하면 안 된다.

## ADR-REVIEW-014 — 설명 출처와 제안 차단, DDL 변경 없음

공급자 출력의 선택적 contract_quote(최대240자)는 제공된 코드/문서/평가 계약과 정확히 대조하며 result 저장 전에 제거한다. SUPPORTED/NEEDS_CONTEXT와 assumptions·severity 관계는 기존 런타임 검증 외에 JSON Schema 조건으로도 게시한다.

issue.suggestion_check.withheld=true는 제한 예시에서 기존 성공값 변경을 찾아 suggestion을 안전한 확인 안내로 바꿨음을 뜻한다. 반례/결함은 보존한다. 필드가 없다고 제안이 검증된 것은 아니다.

issue.origin=STATIC_PROJECTION은 제공된 순수 코드와 단언의 제한 계산 차이를 서버가 설명한 항목이다. 일반 AI 항목에는 이 필드가 없다. result.grounding은 status=BOUNDED, findings(추가/교체한 항목 수), omitted(결과 공간 부족으로 표시하지 못한 후보 수)다. 이는 전체 파일·입력의 검사율이 아니며 계산의 다른 상한에서 제외한 범위를 모두 세지는 않는다. verification의 kept/revised/dropped/added는 모델 검증 단계 집계이고 grounding과 별개다. 코드 원문·단언 인자·비어 있지 않은 문자열 값은 저장하지 않고 값의 유형/빈 값/정수·불리언과 줄·분기만 표시한다. 과거 결과 필드 부재를 그대로 허용한다.

## ADR-REVIEW-015 — 설명 모드, migration 0010

review_runs.mode는 접수 시 고정되며 리뷰 응답·이력에 mode로 노출된다. result.harness.mode에 생성에 쓴 하네스 모드를 남긴다. prompt_version은 두 모드 지침 전체의 해시다. 출력 스키마와 result 필드는 두 모드가 같고 구형 결과(mode 없음)는 SENIOR로 읽는다. 추가형 DDL이며 기존 행은 기본값을 갖는다. 0010 downgrade는 JUNIOR 데이터가 있으면 거부한다. 이 migration은 파일 작성만 완료했고 어떤 DB에도 적용하지 않았다.
