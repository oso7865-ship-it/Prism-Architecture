# Review: 수동 DeepSeek 코드 리뷰

> ID: `REVIEW` · 소유: `backend/app/domain/review` · 기준: `2026-10-06`
> 읽는 때: LangChain·전송 정책·AI 결과·비용을 변경할 때

현재 계약은 [ADR-REVIEW-015](../../adr/review/ADR-REVIEW-015-review-modes.md)(설명 모드)·[ADR-REVIEW-014](../../adr/review/ADR-REVIEW-014-grounded-claims-and-repair-guards.md)·[ADR-REVIEW-012](../../adr/review/ADR-REVIEW-012-purpose-and-team-standards.md)(목적별 리뷰)와 아래 본문이다. 이 문서는 시간순 보강 절을 주제별로 압축한 것이며 압축 전 상세 원문은 [legacy](../../../../legacy/pre-compression-2026-10-06/review/README.md)에 보존한다. 결과 JSON 필드의 추가 이력은 [결과 스키마](../../contracts/schema/RESULTS.md)가 소유한다. 실제 품질·비용 기록은 [records](../../../../records/README.md)에서 관리한다.

## 소유권과 실행 정책

[ADR-REVIEW-003](../../adr/review/ADR-REVIEW-003-bounded-manual-code-review.md)이 초기 FINDINGS_ONLY 설계를 대체한다. `review`가 router/service/models/policy/provider/worker를 소유하고 analysis/repository/pull_request/workspace의 공개 API만 쓴다. LangChain ChatDeepSeek JSON mode와 Pydantic strict 검증을 사용한다. 서버 기본 OFF이며 로컬 검증 설정에서만 명시적으로 켠다. 기본 모델은 deepseek-flash이고 모델 목록에서 가용성을 확인한다.

완료된 정적 분석에서 OWNER가 **매 요청마다** 외부 코드 전송에 동의하고 수동 실행한다. 팀 멤버는 결과를 조회한다. 접수·전송 직전·저장 시 현재 권한과 연결 세대를 다시 확인하며 요청자 권한 상실·연결 변경 시 결과를 폐기한다. 자동 리뷰, GitHub 게시, 코드 적용·실행은 없다. 정적 Finding은 AI가 변경하지 않는다. LLM 도구와 DB/GitHub 쓰기 권한은 없고 외부 tracing·환경 프록시·redirect·자동 재시도를 끈다.

## 입력과 문맥 선택

**BOUNDED_CODE_V5.** PR의 첫 100개 변경 파일 중 지원 언어 변경 파일 최대 8개와 관련 파일 최대 4개, 파일 JSON 16KiB·전체 코드 JSON 48KiB. 고정 base/head를 취득 전후 확인하고 HEAD 변경·주변 줄만 전송한다. 삭제 줄·PR 본문·사람 코멘트는 보내지 않는다. 제외 경로·비밀 의심 파일은 걸러내며 실제 경로 대신 f1… ID를 쓴다. 비밀 탐지는 완전하지 않으므로 기밀 코드 전송 판단은 요청자 책임이다.

**후보 수집.** Git tree 일반 파일과 안전한 HEAD 소스의 import·식별자·경로로 후보 파일 12개, 함수·메서드 구간 24개(구간당 최대 160줄, 변경 줄 보존). 전체 파일 취득은 메모리에서 200KB 이하. 변경 함수별 최대 8개 질의를 파일 간 교대로 배정하며 순서는 이름 일치 직접 호출 → 변경 함수 주변 → 선택적 후보다. 같은 파일 여러 구간은 줄 번호로 중복 제거하고, 구간 추가 시 파일·전체 예산을 원자적으로 검사한다. 직접 호출 후보는 다른 변경 파일의 hunk 밖 함수 정의도 예산 안에서 우선 선택한다(role=changed 유지).

**선택 방식.** 기본은 결정적 규칙이다. 선택적 CPU 리랭커(기본 OFF)는 함수별 후보의 보조 순위만 정하고 직접 호출과 정의가 일치하는 구간을 제거할 수 없다. 모델 revision·파일 해시를 고정하고 별도 로컬 컨테이너의 loopback endpoint만 호출하며 원문·질의를 저장하거나 요청 경로에서 모델을 내려받지 않는다. 추론 2초 제한, 오류·비정상 점수는 규칙 순서로 복귀한다. 전체 호출 그래프·상속·동적 호출·alias 해석은 보장하지 않는다. coverage.retrieval에 mode·candidate_count·fetched_files(리랭커 사용 시 model/revision/duration_ms/truncated_documents), 복귀 사유, 미확보 보호 후보 수, 생략 질의 수(QUERY_LIMIT)·부분 함수(FUNCTION_PARTIAL)·SYNTAX_PARTIAL을 기록하고 후보 원문은 기록하지 않는다.

**정적 Finding 전달.** SECURITY 제외, 중요도·fingerprint 기준 최대 10개의 서버 메시지·규칙·언어. 코드 주석·문자열은 불신 데이터다.

**컨텍스트 보충.** 첫 출력의 context_requests는 제공된 file_id·보이는 symbol·need만 최대 2개 받아 4초 내 같은 저장소·SHA의 기존 제공 파일을 최대 160줄 전체로 보충한다. 임의 경로·다른 저장소·웹 검색은 없고 한도(파일 16KiB·코드 48KiB·팀 문서 별도 12KiB)를 유지하며 결과를 coverage.context_supplement에 남긴다. 보충 후 권한·취소·lease·원격 SHA를 다시 확인한다.

## 출력과 검증

**출력 계약.** 모델은 최상위 summary/limitations와 issues 배열만 반환한다. issue는 file_id·line·severity·title·evidence·suggestion에 더해 basis(SUPPORTED/NEEDS_CONTEXT), evidence_lines(1~8줄), trigger·consequence(각 1~400자), assumptions(최대 3개)를 가진다. 요약·한계 각 1600자, 지적 최대 10개, 제목 160자, 근거·제안 각 800자. unknown field·과도한 길이·비밀 패턴·전송하지 않은 파일/줄 참조·구조 위반은 응답 전체를 거부하며 지적을 조용히 제거하지 않는다. NEEDS_CONTEXT+ERROR는 거부한다. 서버가 경로를 복원하고 Vue는 HTML 실행 없이 텍스트로 렌더링한다. 모델이 싣는 `"type":"json_object"` 플래그만 서버가 제거한다(`model_output.strip_api_metadata`).

**분류.** 검증 후 SUPPORTED는 result.issues, NEEDS_CONTEXT는 result.questions에 보존한다(classification SUPPORTED_FINDINGS_AND_CONTEXT_QUESTIONS). 질문은 변경 코드에서 보이는 구체적 우려 동작과, 확인 결과가 수정 판단을 바꾸는 명시적 미확인 전제가 함께 있어야 한다. 호출부·구현 부재만으로 만든 질문은 제외하고 한계로 기술한다. 이미 제공된 계약·타입·기본값은 발생 조건에 쓰고 미확인 전제로 중복하지 않는다. summary는 서버가 검증된 건수와 우선 제목 최대 3개로 조합하며(ADR-REVIEW-009) 0건은 제공 범위의 지적 없음이다.

**검증 호출.** 지적이 있는 초안은 같은 코드 입력과 strict 검증을 통과한 초안(최대 24,000byte)을 두 번째 호출로 재검토한다. 각 항목은 KEEP/REVISE/DROP 하나이며 새 지적·파일/대표 줄 이동·질문의 확정 승격은 금지다. checked_consequence(1~400자)가 KEEP/REVISE에 필수이고 서버가 원 consequence를 교체한다. 수정도 원 출력 검증을 거친다. 검증 이후 limitations는 서버의 범위·한계 문구로 대체해 제외한 주장이 재노출되지 않게 한다. 검증 장애는 FAILED이며 미검증 성공으로 복귀하지 않는다. 같은 모델의 독립 호출이므로 공통 오판 가능성이 있고 진실성 증명이 아니다.

**빈 초안 재검토 (ADR-REVIEW-011).** 빈 초안도 두 번째 호출을 진행해 모든 변경 파일의 file_checks(file_id·path·line·outcome FINDING/NO_FINDING/LIMITED·observation)를 받는다. 대표 줄은 서버가 변경 줄(삭제만 있으면 문맥 줄, LIMITED)에서 정한다. 삭제 코드를 읽었다고 주장하지 않는다.

**출력 복구 (ADR-REVIEW-013).** 첫 출력이 schema·근거 검증에 실패하면 남은 한 호출로 원래 입력을 독립 재검토(OUTPUT_RECOVERED)한다. 두 번째 실패는 FAILED이며 정상 0건으로 치환하지 않는다. new_findings도 원래 위치·근거·기준 문서 검증을 거치며 정확히 같은 파일/줄/trigger/consequence만 중복 제거한다.

## 설명·수정안 방어 (ADR-REVIEW-013/014)

서버가 값을 계산해 모델 주장을 보정하는 **제한 범위 정적 계산**이다. 코드 생성·eval/exec/import·프로젝트 실행은 없고 지원 밖은 계산하지 않는다. 자연어 주장의 진실성을 자동 증명하지 않는다.

| 기능 | 범위·규칙 |
|---|---|
| 서버 계산 예시 | 작은 순수 Python 함수의 리터럴 단언·기본값·분기·반환(None/빈 값, 제한 산술·range, dict.get/or 순서)과 완전한 단일 Java 산술 반환식. Python은 16KiB·500 AST노드·160단계·깊이 4·인자 4·관측 6개/파일·4파일 |
| STATIC_PROJECTION | CODE에서 제공 단언과 계산이 변경 경로에서 불일치하면 최대 4개 서버 설명 후보를 만들어 같은 파일/대표 줄의 모델 설명만 교체. 10개가 가득 차면 추가하지 않고 누락 수 표시. 실행 테스트나 결함 증명이 아님 |
| expression_repair | 제공된 정확한 Python return 식만 최대 49개 예시로 비교해 기존 성공값 변화를 suggestion_check로 표시. 자연어의 명확한 range 대안은 inferred_from_text로 제한 비교. 변경된 성공값이 있어도 원래 결함은 보존. 식 원문은 저장하지 않음 |
| withheld | 최종 수정안이 기존 성공값을 바꾸면 제안을 확인 안내로 바꾸고 withheld=true. PRESERVES_SAMPLES는 수정안의 정답·계약 준수 인증이 아님 |
| contract_quote | 제공 범위의 정확한 짧은 인용(≤240자)인지 확인한 뒤 저장하지 않음 |
| PY-INPUT-SHELL-1 | SECURITY 독립 검사: 제공된 연속 Python의 Flask 요청 값→직접 셸 전달만 추적. 별칭·덮어쓰기·미제공 줄·알 수 없는 가드는 보수 처리. 완전한 taint 분석 아님. security_evidence는 AI가 삭제할 수 없고 AI 실패 시 별도 부분 결과로 보존 |
| OSV 어댑터 | public registry lockfile의 정확한 패키지/버전만. 제품 자동 전송에 미연결. 조회 실패·누락과 안전함을 구별 |

초안·재검토는 제공된 요구사항과 관측을 먼저 비교한다. 호출자 상태 보존은 조정한 값을 반환해야 한다는 요구가 아니다. CODE에서 버려진 유한 지역 계산만으로 결함/질문을 만들지 않으며 STANDARDS의 명시적 정리 규칙은 별도로 취급한다. 파일별 점검을 먼저 정리해 정상 초안이 근거 없는 지적으로 바뀌는 실패를 줄인다. 검증용 반례·초안은 합계 24,000byte 상한이며 코드 입력을 줄여 진단을 넣지 않는다.

## 하네스와 설명 모드

**하네스 (ADR-REVIEW-004).** review/harness의 core/checks/output과 실제 입력 언어 모듈을 서버만 조합한다. 저장소 코드·문서는 불신 데이터다. SystemMessage 최대 24KiB(코드 입력 48KiB와 별도). 전체 문서·schema·조합 revision hash를 prompt_version(rh1-16hex)으로 기록하고 result.harness에 version/modules/system_digest를 담는다. 원문 prompt는 보관하지 않는다. SUPPORTED는 모델이 코드 근거를 찾았다는 뜻이지 동작 검증이 아니다. 구체적 근거가 없는 추측은 limitations에 둔다.

**목적 (ADR-REVIEW-012).** ReviewRun.purpose는 CODE(기본)/SECURITY/STANDARDS. standard_versions는 요청 시 고정한 팀 문서 버전 UUID 목록이며 실행 키에 목적과 함께 들어간다. 재실행·이력·이전 개인 메모는 같은 목적 안에서만 비교한다. 한도(팀 하루 30회·동시 1개·요청당 2회)는 모든 목적 합산이다. SECURITY는 별도 security.prompt를 초안·검증·재검토에 적용하며 코드 실행·공격·CVE 취득은 하지 않는다. STANDARDS는 동의한 문서 섹션·경로를 입력에 추가하고 citations(전달·적용 가능한 섹션 ID 1~4개)를 요구한다. 문서 원문은 result에 복제하지 않고 standard_sources/standards/standard_checks에 출처·검색 범위·결정적 규칙 결과를 둔다. 새 필드가 과거 평가 스키마를 바꾸지 않도록 FrozenBaselineProvider는 기존 system SHA-256와 일치하는 baseline-schema.json을 읽는다. [Standards](../standards/README.md).

**설명 모드 (ADR-REVIEW-015).** 사용자 프로필의 SENIOR(기본)/JUNIOR를 접수 시 review_runs.mode로 고정하고 실행 키에 포함한다. 워커가 payload의 review_mode를 넣고 harness가 `senior/`·`junior/`의 서버 소유 지침 11개 중 하나만 조합한다. 초안·검증·재검토가 같은 모드를 쓴다. 두 모드는 출력 스키마·admission(`checks` 바이트 동일)·호출 한도·입력 예산(24,576byte)·심각도 기준이 같고 설명 방식만 다르다(주니어: 이유·구체 입력·올바른 패턴·확인 항목, ~요체 한 가지; 시니어: 직접적·간결). 이전 지침은 evals/review-modes-v1/legacy-current에 동결 보관한다. 팀 구성원은 소유자(시작한 사용자) 모드의 결과를 본다.

## 실행·한도·이력

PENDING → RUNNING → COMPLETED/FAILED/CANCELED, EXPLAIN_FINDINGS 영속 Job으로 처리한다. analysis·model·prompt·policy·연결 세대·generation·mode·purpose digest가 같으면 기존 실행을 반환하고 명시 재실행은 새 generation이다.

한 실행 외부 호출 최대 2회, 회당 출력 2000token·모델 60초(취득 포함 150초). Workspace UTC 접수일 기준 최대 30회(설정 1~30, 기본 30; 한국시간 오전 9시 초기화)·동시 1개이며 실패·취소도 접수 한도를 소비한다. Workspace 잠금 아래 예약한다([ADR-REVIEW-008](../../adr/review/ADR-REVIEW-008-team-daily-allowance.md)). 각 외부 요청 전에 권한·취소·연결 세대·lease를 검사하고 call_attempts(0~2)를 커밋하며 lease 만료는 자동 재호출 없이 실패 처리한다. 모델 설정 변경 시 대기 실행을 다른 모델로 보내지 않는다. 사용자 화면은 AI 모델/AI 서비스로 표시하며 실제 제공자 설정과 전송·비용 안내를 보존한다.

토큰 관측값과 usage_uncertain을 기록하며 금액을 보장하지 않는다(청구는 DeepSeek 기준). 취소는 이미 전송된 요청의 과금을 되돌리지 않는다. 두 번째 호출이 실패해도 관측한 첫 사용량을 보존한다. 하루 30회는 접수 기준이며 최대 60회 외부 호출이 가능하다. 한정된 문맥만 검토하므로 실행 검증·전체 정합성·결함 부재를 보장하지 않는다.

## HTTP 계약

모든 경로는 `/api/v1/workspaces/{wid}` 하위다.

| 요청 | 동작 |
|---|---|
| POST `/analyses/{aid}/reviews` | `{consent:true, purpose?, rerun_of?}`, 202 실행 응답 |
| GET `/analyses/{aid}/reviews` | 같은 purpose의 최근 50개 items, enabled, model, daily_limit |
| GET `/reviews/{rid}` | 검증된 결과·상태·토큰·오류코드 |
| POST `/reviews/{rid}/cancel` | 소유자의 중단 요청, 202 |
| GET `/reviews/{rid}/feedback` | 요청자 본인의 items(key,state,note,updated_at) |
| PUT `/reviews/{rid}/feedback/{key}` | `{state,note?}`. 완료 결과에 존재하는 key만. state OPEN/ACKNOWLEDGED/PLANNED/INTENDED/FALSE_POSITIVE, 메모 500자, 비밀 의심 차단 |
| GET `/reviews/{rid}/source/{key}` | 서버가 결과에서 경로·SHA·대표 줄 결정. 선택적 line으로 80줄 페이지·한 줄 300자·total_lines |
| GET `/reviews/{rid}/source-files/{file_id}?line=N` | coverage.files 허용 목록의 파일 열람 |

소스 열람은 no-store이며 회원·팀·활성 저장소·연결 세대를 외부 요청 전후 확인한다. 원문 비저장, 연결 해제·세대 변경 후 코드 취득은 금지한다(과거 결과 읽기는 허용). feedback key는 경로·정규화 제목 SHA-256이며 의미 동일성을 증명하지 않고, 피드백은 개인 기록이지 팀 승인·수정 완료가 아니다. 이전 회차 비교는 같은 분석 이력의 제안·질문에 대해 경로·제목의 신규/반복/미검출만 계산하며 의미적 해결 판정은 하지 않는다. coverage.files.role은 changed/related, context_notes는 SOURCE_UNAVAILABLE/CONTEXT_LIMIT/TREE_TRUNCATED/RELATED_* 등, prior_feedback_count는 입력에 포함된 개인 기록 수(최대 5개, 메모는 비신뢰 데이터)다.

## 평가와 검증

**평가 원칙.** 평가 fixture를 축약해도 결함 판단에 필요한 타입·기본값·소비 코드·테스트 요구사항을 보존하고 원본 출처·base/head·입력 해시와 기대 결과를 분리 기록한다. 정답·rubric·출처 라벨은 코드 입력에 넣지 않으며 모델 행동을 바꾸라는 주석 지시는 따르지 않는다. 비교는 같은 입력·모델·호출 수 정책·출력 예산에서 하고 위치 적중·의미 정확·정상 오탐·형식 실패·검증 이후 누락을 별도 기록한다. 최종 주장과 수정안까지 확인한 의미 PASS가 없으면 위치 점수만으로 채택하지 않는다. 이전 결과와 실패 후보는 보존한다. 평가 전용 구조화 진단은 별도 호출의 출력이며 숨은 추론이나 기존 호출의 탐지 증거가 아니고 제품 계약에 추가하지 않는다. scorer 테스트 통과를 LLM 정확도로 보고하지 않는다.

**현재 상태.** [2026-09-29 최종 검증 보고서](../../../../records/2026-09-29_final-validation-report.md)에서 실제 세 목적별 리뷰·문서 근거·코드 열람을 확인했고 합성 88평가의 위치·형식·정상 오탐 게이트를 통과했다. 독립 사람 검수와 범용 의미·수정안 품질은 미완료다. DeepSeek Responses json_schema·높은 추론은 평가용 어댑터만 준비했고 우월성이 입증되지 않아 제품은 ChatDeepSeek·Flash·추론 OFF·2,000토큰/회·최대 2회를 유지한다([보수 보고서](../../../../records/2026-09-29_quality-repair-report.md)).

**테스트 범위.** AI OFF·동의·권한·테넌트, 중복·일 한도, 비밀·제외 경로·크기 제한, schema·줄 검증, timeout·lease 만료 재호출 0, 취소·접근 철회, 정적 분석 보존, 실제 PR 호출. FK 없는 컬럼 계약은 [결과 스키마](../../contracts/schema/RESULTS.md)를 따른다.
