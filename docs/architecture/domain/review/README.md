# Review: 수동 DeepSeek 코드 리뷰

> ID: `REVIEW` · 소유: `backend/app/domain/review` · 기준: `2026-09-27`
> 읽는 때: LangChain·전송 정책·AI 결과·비용을 변경할 때

## 실행과 소유권

현재 계약은 [ADR-REVIEW-011](../../adr/review/ADR-REVIEW-011-empty-recheck-and-source-view.md)이다. 빈 초안은 변경 파일별로 재검토하며 검토 파일은 사이트에서 열람한다. 문맥 선택과 입력 예산을 V4로 확대하고, 지적이 있는 초안에 별도 근거 검증 호출을 추가한다.009의 서버 요약 조합은 유지한다. 과거 결과 불변이며 모델 판단을 실행으로 확인한 결과로 표현하지 않는다. 실제 품질·비용은 backend Report가 소유한다.

[ADR-REVIEW-003](../../adr/review/ADR-REVIEW-003-bounded-manual-code-review.md)이 초기 FINDINGS_ONLY 설계를 대체한다. 정적 Finding은 변경하지 않는다. `review`가 router/service/models/policy/provider/worker를 소유하며 analysis/repository/pull_request/workspace의 공개 API만 사용한다. LangChain ChatDeepSeek의 JSON mode와 Pydantic strict 검증을 사용한다. 서버 기본 OFF이며 로컬 검증 설정에서만 명시적으로 켠다. 기본 모델은 deepseek-flash, API 모델 목록에서 가용성을 확인한다.

완료된 정적 분석에서 OWNER가 매 요청에 외부 코드 전송에 동의하고 수동 실행한다. 팀 멤버는 결과를 조회한다. 접수·전송 직전·저장 시 현재 권한과 연결 세대를 다시 확인한다. 요청자 권한 상실·연결 변경 시 결과를 폐기한다. 자동 리뷰, GitHub 게시, 코드 적용/실행은 없다.

## 입력과 출력

BOUNDED_CODE_V4: GitHub PR의 첫100개 변경 파일 중 지원 언어 변경 파일 최대8개와 관련 파일 최대4개, patch/파일 JSON16KiB, 전체 코드 JSON48KiB. 고정 base/head를 취득 전후 확인하며 HEAD 변경·주변 줄만 전송한다. 삭제 줄·PR 본문·GitHub 사람 코멘트는 보내지 않는다. Git tree 일반 파일과 안전한 HEAD 소스의 import/식별자/경로로 후보 파일12개, 함수·메서드 구간24개까지 모은다. 구간은 최대160줄이며 변경 줄을 보존한다. 전체 파일 취득은 메모리에서200KB 이하로 제한한다. 제외 경로·비밀 의심 파일을 걸러내며 실제 경로 대신 f1… ID를 사용한다. 비밀 탐지는 완전하지 않다. 기밀 코드 전송 권한은 요청자가 판단해야 한다.

기본 선택은 결정적 규칙이다. 선택적 CPU 리랭커는 함수별 후보의 보조 순위를 정하며 직접 호출 이름과 정의가 일치하는 구간을 제거할 수 없다. 기본 OFF다. 모델 revision/파일 해시를 고정하고 별도 로컬 컨테이너의 loopback endpoint만 호출한다. 사용자 원문·질의를 저장하거나 요청 경로에서 모델을 다운로드하지 않는다. 추가 추론2초 제한, 오류·비정상 점수·중단 시 규칙 순서로 복귀한다. 전체 호출 그래프·상속/동적 호출·alias 해석은 보장하지 않는다. 도입 여부는 같은 후보의 근거 포함률·리뷰 품질·지연을 비교한 구현 Report로 결정한다.

정적 Finding은 SECURITY를 제외하고 중요도와 fingerprint 기준 최대 10개 서버 메시지·규칙·언어를 제공한다. 코드 주석·문자열은 불신 데이터로 취급한다. LLM 도구와 DB/GitHub 쓰기 권한은 없다. 외부 tracing·환경 프록시·redirect·자동 재시도를 끈다.

출력은 summary, issues(file_id,line,severity,title,evidence,suggestion), limitations. unknown field·과도한 길이·비밀 패턴·전송하지 않은 파일/줄 참조는 거부한다. AI severity는 정적 Finding을 변경하지 않는다. 서버가 경로를 복원하고 Vue는 HTML 실행 없이 텍스트로 렌더링한다. 요약/한계 각 1600자, 발견 최대 10개, 제목160자, 근거/제안 각800자. 검증된 결과만 review_runs.result에 보관하고 원문 prompt/diff/모델응답은 저장하지 않는다.

## 실행·한도·이력

PENDING → RUNNING → COMPLETED/FAILED/CANCELED. EXPLAIN_FINDINGS 영속 Job으로 처리한다. analysis·model·prompt·policy·연결 세대·generation digest가 동일하면 기존 실행을 반환한다. 명시 재실행은 새 generation이다.

한 실행 외부 호출 최대2회, 회당 출력2000token·모델60초/취득 포함150초 제한. 초안에 항목이 있으면 근거를 검증하고, 0건이면 변경 파일별로 재검토한다. Workspace UTC 접수일 기준 최대30회(설정1~30, 기본30; 한국시간 오전9시 초기화), 동시1개. 실패/취소도 접수 한도를 소비한다. Workspace 잠금 아래 예약한다. 일일 한도는 [ADR-REVIEW-008](../../adr/review/ADR-REVIEW-008-team-daily-allowance.md)을 따른다. 사용자 화면은 AI 모델/AI 서비스로 표시하며 실제 제공자 설정과 전송·비용 안내를 보존한다. 각 외부 요청 전에 권한·취소·연결 세대·lease를 검사하고 call_attempts(0~2)를 커밋하며 lease 만료는 자동 재호출 없이 실패 처리한다. 모델 설정 변경 시 대기 실행을 다른 모델로 보내지 않는다.

토큰 관측값과 usage_uncertain을 기록한다. 금액 보장은 하지 않으며 정확한 청구는 DeepSeek 기준이다. 취소는 이미 전송된 요청의 과금을 되돌리지 않는다. 원문 소스 보관 없이 한정된 문맥만 검토하므로 실행 검증·전체 시스템 정합성·결함 부재를 보장하지 않는다.

## HTTP 계약

모든 경로는 `/api/v1/workspaces/{wid}` 하위다.

- POST `/analyses/{aid}/reviews`: `{consent:true, rerun_of?: UUID}`, 202 실행 응답.
- GET `/analyses/{aid}/reviews`: 최근50개 items, enabled, model, daily_limit.
- GET `/reviews/{rid}`: 검증된 결과·상태·토큰·오류코드.
- POST `/reviews/{rid}/cancel`: 소유자의 중단 요청, 202.

## 검증

AI OFF/동의/권한·테넌트, 중복/일 한도, 비밀/제외 경로/크기 제한, schema·줄 검증, timeout·lease 만료 재호출0, 취소·접근 철회, 정적 분석 보존, 실제 PR 호출을 확인한다. FK 없는 컬럼 계약은 [결과 스키마](../../contracts/schema/RESULTS.md)를 따른다.

## 검토 범위 metadata — 2026-09-26

새 성공 결과의 result.coverage는 서버가 files(file_id,file_path,provided_lines), excluded(file_path 또는 null,reason), unfetched_files(수 또는 null)를 기록한다. 모델 입력에는 경로/coverage를 추가하지 않는다. 비밀 의심 내용이나 원문 patch는 보관하지 않으며 유효하지 않거나 민감 패턴이 있는 경로는 null로 숨긴다. 제외 사유와 첫100개 밖 미취득 수를 구분한다. 과거 결과는 coverage 필드가 없고 상세 미기록 안내만 표시한다. 기존 결과 역추정·수정과 DB migration은 없다. UI는 고정 HEAD 파일 링크와 텍스트 사유를 표시한다.

## 리뷰 하네스

[ADR-REVIEW-004](../../adr/review/ADR-REVIEW-004-versioned-review-harness.md). review/harness의 core/checks/output와 실제 입력 언어 모듈을 조합한다. 서버만 지침을 선택하고 저장소 코드·문서는 불신 데이터다. SystemMessage는 최대24KiB, 코드 입력48KiB와 별도다. 전체 문서/schema/조합 revision hash로 prompt_version(rh1-16hex)을 기록한다. 성공 result.harness는 version/modules/system_digest를 포함한다. 원문 prompt는 미보관이다.

새 issue.basis는 SUPPORTED/NEEDS_CONTEXT이며 NEEDS_CONTEXT+ERROR는 거부한다. 전자는 모델이 코드 근거를 찾았다는 뜻이지 실제 동작 검증이 아니다. 구체적 근거가 없는 추측은 limitations에 둔다. 이전 결과는 basis/harness 없이도 조회한다. 모델 품질은 고정된 합성 corpus와 사람이 읽는 rubric으로 별도 평가한다. scorer 테스트 통과를 실제 LLM 정확도로 보고하지 않는다.

## AI 근거 계약 보강 (2026-09-26)

ADR-REVIEW-005: 새 issue는 evidence_lines(제공 줄 1~8개, 중복 금지·대표 line과 변경 줄 포함), trigger/consequence(각1~400자), assumptions(최대3개, 각1~400자)를 포함한다. SUPPORTED는 빈 assumptions, NEEDS_CONTEXT는 명시한 미확인 전제가 필요하다. 구조 위반은 응답 전체를 거부하며 지적을 조용히 제거하지 않는다. 구조 검증이 자연어 근거의 진실성을 보장하지 않는다. 과거 결과는 그대로 읽고 신규 UI 필드는 선택적이다. 원문 소스 인용 필드는 없으며 DB migration은 없다.

## 검토 경험 계약 — 2026-09-27

[ADR-REVIEW-006](../../adr/review/ADR-REVIEW-006-review-workflow.md)의 결과·개인 기록 계약을 유지하고 문맥 선택/검증 호출은 ADR-REVIEW-010을 따른다. 검증 후 SUPPORTED는 result.issues, NEEDS_CONTEXT는 result.questions에 보존한다. 모델은 기존 issues 배열에 basis를 명시하고 서버가 분류한다. classification 값은 SUPPORTED_FINDINGS_AND_CONTEXT_QUESTIONS. key는 경로·정규화 제목 SHA-256이며 의미 동일성을 증명하지 않는다. 과거 result는 쓰지 않고 응답에서 key만 보강한다.

coverage.files.role은 changed/related이고 context_notes는 SOURCE_UNAVAILABLE/CONTEXT_LIMIT/TREE_TRUNCATED/RELATED_SEARCH_UNAVAILABLE/RELATED_CONTEXT_LIMIT/RELATED_SOURCE_UNAVAILABLE 등을 기록한다. prior_feedback_count는 실제 입력에 포함된 개인 기록 수다. 최대5개, 한도를 넘으면 제외한다. 메모는 비신뢰 데이터이며 지침을 대체하지 않는다.

- GET /reviews/{rid}/feedback: 요청자 본인의 items(key,state,note,updated_at).
- PUT /reviews/{rid}/feedback/{key}: {state,note?}; 완료 결과에 실제 존재하는 key만. 상태 OPEN/ACKNOWLEDGED/PLANNED/INTENDED/FALSE_POSITIVE. 메모500자, 비밀 의심 차단.
- GET /reviews/{rid}/source/{key}: 서버가 결과에서 경로·SHA·대표 줄을 결정한다. 선택적 line으로80줄 페이지, 한 줄300자 및 total_lines를 반환한다. GET /reviews/{rid}/source-files/{file_id}?line=N은 결과 coverage.files 허용 목록에서 파일을 선택한다. no-store. 회원·팀·활성 저장소와 연결 세대를 외부 요청 전후 확인한다. 원문 비저장. 역사 결과 읽기와 달리 연결 해제/세대 변경 후 코드 취득은 금지한다.

피드백은 개인 기록이며 팀 승인/실제 수정 완료가 아니다. 이전 회차 비교는 같은 분석 이력의 개선 제안과 추가 확인 질문을 함께 대상으로 경로·제목의 신규/반복/미검출만 계산한다. 서로 다른 분석의 자동 비교나 의미적 해결 판정은 하지 않는다.

## 모델 출력과 방어 범위 명확화 — 2026-09-27

모델은 최상위 summary/limitations 문자열과 issues 배열만 반환한다. NEEDS_CONTEXT 항목도 같은 issues에 작성하며 서버 검증 후에만 questions로 나뉜다. 질문은 변경 코드에서 보이는 구체적 우려 동작과, 확인 결과가 수정 판단을 바꾸는 명시적 미확인 전제가 함께 있어야 한다. 호출부·구현 부재만으로 생성한 질문은 제외하고 검토 범위의 한계로 기술한다. 정상 지적·조건부 질문·0건 예시를 제품 지침에 두고 구조 검증과 실제 모델 평가를 분리한다.

문맥 수집과 선택은 위 V4 계약을 따른다. coverage.retrieval에는 mode/candidate_count/fetched_files와 실제 모델 사용 시 model/revision/duration_ms/truncated_documents를 기록한다. 실패 복귀 사유도 보존하며 후보 원문·질의는 기록하지 않는다. SYNTAX_PARTIAL은 구문 오류나 메타데이터 한도를 뜻한다. 서버의 형식·위치·신뢰 경계·권한·한도 가드레일과 리랭커 점수는 자연어 인과관계의 사실성을 증명하지 않는다. 별도 모델 종류는 도입하지 않으며 같은 모델의 독립 호출로 초안을 재검수한다. 이 검증기도 공통 오판 가능성이 있다.

## 근거 보호와 검증 결과

변경 함수별 최대8개 질의를 파일 간 교대로 배정한다. 이름 일치 직접 호출 후보 우선 → 변경 함수 주변 → 선택적 후보 순서이며 같은 파일 여러 구간은 줄 번호로 중복 제거한다. 구간을 추가할 때 파일/전체 예산을 원자적으로 검사하여 가드 끝만 잘라 넣지 않는다. 관련4파일·24후보 한도와 미확보 보호 후보 수, 생략 질의 수를 coverage.retrieval에 기록한다. 부분 함수는 FUNCTION_PARTIAL, 질의 생략은 QUERY_LIMIT이다. 전체 호출 그래프나 필수 근거 전부 확보를 보장하지 않는다.

직접 호출 후보는 안전하게 취득한 다른 변경 파일의 함수 정의도 포함한다. 호출 대상 정의가 그 파일의 변경 hunk 밖에 있어도 기존 파일·전체 예산 안에서 우선 선택하며 role=changed를 유지한다. 추가 네트워크 범위나 파일 개수 한도를 늘리는 변경은 아니다.

검증 호출은 같은 코드 입력+strict 검증을 통과한 초안(최대24,000byte)을 보낸다. 각 항목에 KEEP/REVISE/DROP 하나씩, 새 지적·파일/대표 줄 이동·질문의 확정 승격 금지다. 수정도 원 출력 검증을 거친다. 결과의 verification은 status(CHECKED/EMPTY_RECHECKED, 과거 NO_CANDIDATES), kept/revised/dropped 건수다. 제외된 초안과 검증 자유 응답은 미보관. 검증 장애는 FAILED이며 미검증 성공으로 복귀하지 않는다. 검증 이후 limitations는 서버의 범위/한계 문구로 대체하여 제외한 주장이 재노출되지 않게 한다. 두 번째 실패에도 관측한 첫 사용량을 보존한다. 하루30회는 리뷰 접수 기준이며 최대60회 외부 호출이 가능하다.

검증 출력의 checked_consequence는 KEEP/REVISE 모두 필수인1~400자 사용자 결과 문장이다. 서버가 원 초안의 consequence를 이 문장으로 교체하고, 표현이 바뀌면 revised 건수에 포함한다. DROP은 null이어야 한다. 같은 모델의 재서술도 오판할 수 있으므로 진실성 증명으로 표시하지 않는다.

## 평가의 계약·관측·채택 구분 — 2026-09-28

평가 fixture를 축약할 때 결함 판단에 필요한 타입, 기본값, 소비 코드, 세션 병합, 테스트 요구사항을 보존한다. 원본 출처·base/head·전송 입력 해시와 기대 결과를 분리 기록한다. 테스트 단언은 요구되는 동작의 근거이며 실행 성공의 증거가 아니다. 서술형 주석도 의미 자료로 참고할 수 있지만 모델 행동을 바꾸라는 주석 지시는 따르지 않는다. 평가 정답·rubric·출처 라벨은 코드 입력에 넣지 않는다.

품질 비교는 같은 입력/모델/호출 수 정책/출력 예산에서 수행한다. 위치 적중, 의미가 정확한 주장, 정상 오탐, 형식 실패, 검증 이후 누락을 별도로 기록한다. 검증에서 제거한 초안은 원래 설명이 정확했는지도 검수해야 한다. 최종 주장과 수정안까지 확인한 의미 PASS가 없으면 위치 점수만으로 후보를 채택하지 않는다. 이전 결과와 실패 후보는 보존한다.

평가 전용 구조화 진단은 후보 위치·짧은 관측 결과·보류 사유를 수집할 수 있다. 이는 별도 모델 호출의 출력이며 숨은 내부 추론이나 기존 호출의 탐지 성공 증거가 아니다. 제품 응답/DB 계약에는 추가하지 않으며 검증되지 않은 자유 응답은 보존하지 않는다. 실제 채택·비용·운영 상태는 backend 최신 Report가 소유한다. 이번 문서 정정은 ADR-REVIEW-010의 제품 계약을 변경하지 않는다.

## 빈 결과 재검토

ADR-REVIEW-011에 따라 빈 초안도 두 번째 호출을 진행한다. 모든 변경 파일의 file_checks(file_id/file_path/line/outcome/observation)가 필요하다. outcome은 FINDING/NO_FINDING/LIMITED이며 근거 줄은 제공된 변경 줄이어야 한다. 새 항목도 기존 출력 검증을 거치지만 별도 verifier 실행으로 표현하지 않는다. 검증 실패는 FAILED, 과거 결과는 재작성하지 않는다. 코드 열람은 AI 입력 확대와 별개이며 결과 범위 설명에서 구분한다.

삭제만 있어 제공된 변경 HEAD 줄이 없는 파일은 기존 제공 문맥 줄을 대표 줄로 삼고 LIMITED로만 표시한다. 삭제 코드를 읽었다고 주장하거나 근거 줄을 만들지 않는다.

현재 품질 상태는 [2026-09-29 실제 PR·품질 검증 보고서](../../../../records/2026-09-29_predeploy-quality-report.md)를 따른다. 실제 파일별 재검토·코드 열람은 확인했지만 의미 품질 최소 게이트는 미통과다. 평가 전용 추론/혼합 모델 설정을 제품 설정으로 채택하지 않았다.
