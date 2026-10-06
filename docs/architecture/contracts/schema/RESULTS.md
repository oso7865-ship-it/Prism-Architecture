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

실행 키에는 workspace·연결 ID/세대·PR·base/head·nullable merge_base·rule_set·config ID/digest·analyzer digest·scope·generation을 포함한다. actor는 제외한다. 자동/일반 요청의 generation=0, 명시적 재분석은 Workspace 잠금 아래 같은 기본 입력의 최대 generation+1을 배정한다. run/Job 재시도는 같은 행을 사용한다. HTTP idempotency key별 별도 매핑은 이번 설계에 포함하지 않으며 지원한다고 광고하지 않는다.

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

## result JSON 확장 이력 (DDL 변경 없는 것은 명시)

review_runs.result는 아래 필드를 추가형으로 확장해 왔다. 과거 결과는 필드가 없을 수 있고 소급 수정하지 않으며 신규 UI 필드는 선택적이다. 코드·diff·prompt·응답 원문은 저장하지 않는다. 결정 배경은 각 ADR을 따른다. 압축 전 상세 원문: [legacy](../../../../legacy/pre-compression-2026-10-06/schema/RESULTS.md).

| ADR | 추가된 result 필드와 규칙 |
|---|---|
| REVIEW-003/004 | coverage(files·excluded·unfetched_files, 경로가 유효하지 않거나 민감하면 null), harness(version·modules·system_digest), issues.basis(SUPPORTED/NEEDS_CONTEXT). prompt_version은 하네스+스키마 digest |
| REVIEW-005 | issue.evidence_lines(1~8줄), trigger/consequence(각 1~400자), assumptions(최대 3개). SUPPORTED는 assumptions 비어야 함. 구조 위반은 응답 전체 거부 |
| REVIEW-009 | summary는 검증된 issues/questions 건수와 우선 제목 최대 3개로 서버가 조합(모델 요약 미사용). 0건은 "제공 범위의 지적 없음" |
| REVIEW-010 | verification(CHECKED/NO_CANDIDATES, kept/revised/dropped). call_attempts CHECK 0..2(migration 0008). 검증 장애는 FAILED, 초안 미보관 |
| REVIEW-011 | 빈 초안은 두 번째 호출 필수. verification.status=EMPTY_RECHECKED, file_checks(file_id·path·line·outcome FINDING/NO_FINDING/LIMITED·observation ≤240자) |
| REVIEW-012 (0009) | purpose CODE/SECURITY/STANDARDS(기본 CODE), standard_versions JSONB(고정 버전 UUID 목록), 실행 키에 포함. 결과에 standards/standard_sources/standard_checks, citations는 문서·버전·섹션 제목 메타데이터만. downgrade는 CODE 외 리뷰가 있으면 거부 |
| REVIEW-013 | verification.added·file_checks, OUTPUT_RECOVERED, issue.suggestion_check(status·samples·counterexamples ≤2·scope), coverage.context_supplement, 독립 security_evidence. AI 실패 시 FAILED와 별도 보안 신호 부분 결과 가능, 실패를 정상 0건으로 표시 금지 |
| REVIEW-014 | contract_quote(≤240자)는 제공 입력과 대조 후 저장 전 제거, suggestion_check.withheld, issue.origin=STATIC_PROJECTION, result.grounding(status=BOUNDED·findings·omitted). 값 원문·문자열 값 미저장 |
| REVIEW-015 (0010) | review_runs.mode(SENIOR 기본/JUNIOR, 실행 키 포함), result.harness.mode. 출력 스키마는 두 모드 동일, 구형은 SENIOR로 읽음. downgrade는 JUNIOR 데이터가 있으면 거부. 0011과 함께 2026-10-06 운영 적용 |

