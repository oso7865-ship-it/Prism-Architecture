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

| 컬럼 | 타입 | NULL | 기본값·의미 |
|---|---|---|---|
| workspace_id / analysis_id / requested_by | uuid | N | 같은 팀 분석 및 요청 user 논리 참조 |
| provider | varchar(16) | N | DEEPSEEK CHECK |
| model | varchar(128) | N | 실제 설정 모델, 미정 기본값 없음 |
| prompt_version | varchar(64) | N | 정적 Prompt 버전 |
| policy_version | integer | N | > 0, 접수 당시 연결의 ai_policy_version |
| selected_finding_ids | jsonb | N | 검증·정렬된 내부 Finding UUID 배열 |
| review_key | H256 | N | 분석·Prompt·Provider/model·정책 버전 digest |
| status | varchar(16) | N | PENDING 기본; PENDING/RUNNING/COMPLETED/FAILED/CANCELED CHECK |
| call_count | smallint | N | 0 기본, 0~2 CHECK |
| input_tokens / output_tokens | integer | Y | 관측된 총 사용량 >=0, 모르면 NULL |
| budget_date | date | N | UTC 예산 예약일 |
| reserved_cost_usd | numeric(18,6) | N | >=0, 설정된 가격/상한으로 예약 |
| actual_cost_usd | numeric(18,6) | Y | >=0, 확인된 비용만 |
| cost_state | varchar(16) | N | RESERVED/CONFIRMED/UNKNOWN/RELEASED CHECK |
| started_at / finished_at | timestamptz | Y | 시작/terminal 시각 |
| error_code | varchar(64) | Y | 정제 실패 코드 |
| updated_at | timestamptz | N | now() |

UQ(review_key). IDX(workspace_id,analysis_id,created_at DESC,id DESC), IDX(workspace_id,budget_date), IDX(finished_at) WHERE finished_at IS NOT NULL. selected_finding_ids는 array 및 길이 1~10 CHECK, 원소 UUID·중복 없음·동일 analysis 소속은 서비스 검증. terminal↔finished_at CHECK.

MVP는 호출자가 Finding 부분집합을 지정하지 않는다. 서버가 Severity 내림차순→fingerprint 오름차순으로 Secret을 제외한 최대 10개를 선택·고정하며, 선택 대상이 없으면 run/외부 호출을 만들지 않는다. 따라서 기존 review_key에 선택 집합을 별도 추가하지 않는다. 선택 알고리즘 변경은 prompt_version을 올린다. Secret에는 저장된 LLM 설명 대신 서버의 고정 안내를 표시한다.

Workspace 잠금 아래 budget_date별 기존 예약/확정/불명 비용을 합산해 비용 상한을 검사하고 run+Job+예약을 원자적으로 만든다. RESERVED/UNKNOWN은 reserved_cost_usd, CONFIRMED는 actual_cost_usd, RELEASED는 0으로 집계한다. CONFIRMED일 때만 actual_cost_usd NOT NULL인 CHECK를 둔다. 예약은 최대 2회 호출과 입력/출력 상한을 포함한 보수적 비용이며 상한/모델/가격 설정 전 접수를 차단한다. 호출 전 call_count 증가를 commit하고, timeout 과금 미확인은 UNKNOWN으로 예약을 유지한다. 확정 후 실제 비용으로 정산하고 미호출 취소만 RELEASED로 반환한다. Provider와 내부 재시도를 합쳐 최대 2회이며 Job attempts만으로 LLM 호출 횟수를 계산하지 않는다. 예산은 UTC 접수일별 예약 기준이며 다음 날 실행해도 원 예약일로 계산한다. 외부 과금의 정확한 상한 보장은 Provider 한도 설정·통합 검증도 필요하다.

<a id="table-finding_explanations"></a>

## finding_explanations

| 컬럼 | 타입 | NULL | 기본값·의미 |
|---|---|---|---|
| workspace_id / review_run_id / finding_id | uuid | N | 동일 팀, 같은 analysis의 Review/Finding 논리 참조 |
| explanation / suggestion_text / limitations | text | N | 검증·마스킹된 결과, 각 1~8,000자 CHECK |

UQ(review_run_id,finding_id), IDX(finding_id,review_run_id), IDX(workspace_id,review_run_id,id). Review에 고정된 selected_finding_ids 안의 ID만 저장한다. 설명끼리 중복·미요청 ID·Secret ID를 거부한다. 결과 집합 검증 후 설명 insert와 Review/Job terminal을 같은 transaction에서 commit한다. 원본 response/prompt·코드 예시 컬럼은 없고 불변 결과다.
