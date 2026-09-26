# Review: 수동 DeepSeek 코드 리뷰

> ID: `REVIEW` · 소유: `backend/app/domain/review` · 기준: `2026-09-26`
> 읽는 때: LangChain·전송 정책·AI 결과·비용을 변경할 때

## 실행과 소유권

[ADR-REVIEW-003](../../adr/review/ADR-REVIEW-003-bounded-manual-code-review.md)이 초기 FINDINGS_ONLY 설계를 대체한다. 정적 Finding은 변경하지 않는다. `review`가 router/service/models/policy/provider/worker를 소유하며 analysis/repository/pull_request/workspace의 공개 API만 사용한다. LangChain ChatDeepSeek의 JSON mode와 Pydantic strict 검증을 사용한다. 서버 기본 OFF이며 로컬 검증 설정에서만 명시적으로 켠다. 기본 모델은 deepseek-flash, API 모델 목록에서 가용성을 확인한다.

완료된 정적 분석에서 OWNER가 매 요청에 외부 코드 전송에 동의하고 수동 실행한다. 팀 멤버는 결과를 조회한다. 접수·전송 직전·저장 시 현재 권한과 연결 세대를 다시 확인한다. 요청자 권한 상실·연결 변경 시 결과를 폐기한다. 자동 리뷰, GitHub 게시, 코드 적용/실행은 없다.

## 입력과 출력

BOUNDED_CODE_V1: GitHub PR의 첫 100개 변경 파일 중 지원 언어 최대 8개, patch당 8KiB, 전체 JSON 입력 24KiB. 고정 base/head를 취득 전후 확인하며 HEAD 변경·주변 줄만 전송한다. 삭제 줄·전체 파일·PR 본문·사람 코멘트는 보내지 않는다. 제외 경로·비밀 의심 파일을 걸러내며 실제 경로 대신 f1… ID를 사용한다. 비밀 탐지는 완전하지 않다. 기밀 코드 전송 권한은 요청자가 판단해야 한다.

정적 Finding은 SECURITY를 제외하고 중요도와 fingerprint 기준 최대 10개 서버 메시지·규칙·언어를 제공한다. 코드 주석·문자열은 불신 데이터로 취급한다. LLM 도구와 DB/GitHub 쓰기 권한은 없다. 외부 tracing·환경 프록시·redirect·자동 재시도를 끈다.

출력은 summary, issues(file_id,line,severity,title,evidence,suggestion), limitations. unknown field·과도한 길이·비밀 패턴·전송하지 않은 파일/줄 참조는 거부한다. AI severity는 정적 Finding을 변경하지 않는다. 서버가 경로를 복원하고 Vue는 HTML 실행 없이 텍스트로 렌더링한다. 요약/한계 각 1600자, 발견 최대 10개, 제목160자, 근거/제안 각800자. 검증된 결과만 review_runs.result에 보관하고 원문 prompt/diff/모델응답은 저장하지 않는다.

## 실행·한도·이력

PENDING → RUNNING → COMPLETED/FAILED/CANCELED. EXPLAIN_FINDINGS 영속 Job으로 처리한다. analysis·model·prompt·policy·연결 세대·generation digest가 동일하면 기존 실행을 반환한다. 명시 재실행은 새 generation이다.

한 실행 외부 호출1회, 출력2000token, 모델60초/취득 포함90초 제한. Workspace UTC 접수일 기준 최대5회(설정으로 축소 가능), 동시1개. 실패/취소도 접수 한도를 소비한다. Workspace 잠금 아래 예약한다. 외부 요청 전에 call_attempts를 커밋하며 lease 만료는 자동 재호출 없이 실패 처리한다. 모델 설정 변경 시 대기 실행을 다른 모델로 보내지 않는다.

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

[ADR-REVIEW-004](../../adr/review/ADR-REVIEW-004-versioned-review-harness.md). review/harness의 core/checks/output와 실제 입력 언어 모듈을 조합한다. 서버만 지침을 선택하고 저장소 코드·문서는 불신 데이터다. SystemMessage는 최대24KiB, 기존 코드 입력24KiB와 별도다. 전체 문서/schema/조합 revision hash로 prompt_version(rh1-16hex)을 기록한다. 성공 result.harness는 version/modules/system_digest를 포함한다. 원문 prompt는 미보관이다.

새 issue.basis는 SUPPORTED/NEEDS_CONTEXT이며 NEEDS_CONTEXT+ERROR는 거부한다. 전자는 모델이 코드 근거를 찾았다는 뜻이지 실제 동작 검증이 아니다. 구체적 근거가 없는 추측은 limitations에 둔다. 이전 결과는 basis/harness 없이도 조회한다. 모델 품질은 고정된 합성 corpus와 사람이 읽는 rubric으로 별도 평가한다. scorer 테스트 통과를 실제 LLM 정확도로 보고하지 않는다.
