# 근거 보존·16KiB 문맥·리뷰 재검증

> 작성일: 2026-09-28
> 작업 브랜치: backend dev / frontend dev / architecture main
> 커밋/PR: 미커밋·미푸시 working tree, 기존 변경 보존
> 상태 기록 버전: 1
> 상태 확인 시각: 2026-09-28T00:40:05+09:00
> 구현 상태: 완료
> 구현 근거: context_plan/context_selection·verification·worker·migration0008·프론트 안내와 평가기 변경
> 로컬 검증 상태: 완료
> 로컬 검증 대상: 이번 backend/frontend/architecture working tree
> 로컬 검증 근거: Linux330 tests, 후속 worker7/순수52 tests, 프론트112 tests·타입·빌드·Ruff/mypy PASS; 모델 의미 품질은 별도 FAIL
> 병합 상태: 미수행
> 병합 대상: origin/main
> 병합 근거: 이번 요청 범위에 Git 게시/병합 없음
> 배포 상태: 미수행
> 배포 근거: 로컬 개발 API·DB 적용만 수행
> 실제 연동 상태: 완료
> 실제 연동 근거: 합성/공개 PR 파생 DeepSeek302회·실제 로컬 리랭커 비교·ready200·로그인한 UI 안내 확인; 새 조직 PR 제품 호출은 미수행
> 작업 범위: L
> 적용 스킬: terminal-ops, verification-loop, ui-ux-design, vue-ui-polish
> 적용 Gate: DB Gate, Security Gate, 코드·문서·UI/UX 및 비용 검증
> 위험도: 구조 변경, 제한된 유료 외부 호출, 로컬 비파괴 migration·API 재시작
> 위험 작업 여부: 예; 사용자1~5 구현과 총3000회 승인 범위

## 결과와 범위

[사전 설계](../docs/work-plans/2026-09-27_evidence-first-review.md)에 따라 다섯 개선과 파일당16KiB/전체 코드48KiB를 적용했다. 구현 및 회귀 검증은 완료했지만 **모델 의미 품질의 완전 통과는 아니다**. 최종 공개 PR 파생 평가18회 중11회 통과, 결함 누락6회·정상 코드 오탐1회가 남았다. 이 사례들은 튜닝에 사용했으며 독립 holdout이나 전체 정확도를 뜻하지 않는다.

현재 정책 `BOUNDED_CODE_V4`, 지침 `rh1-d634ca5b77229914`, DB revision0008. 리랭커 기본 OFF·팀당 하루30개 리뷰·자동 재시도0 유지. 하루30은 접수 횟수이며 검증을 포함한 외부 호출은 리뷰당 최대2회다. 과거 결과는 바꾸지 않는다.

## 변경 이력

| 요청 | 변경 | 한계/검증 |
|---|---|---|
| 1 필수 근거 보호 | 구문상 직접 호출 이름과 정의가 일치하는 구간을 선택적 순위보다 먼저 배정 | alias·상속·동적 호출의 의미 연결은 미지원. 바이트/파일 제한을 우회하지 않고 미확보 수를 기록 |
| 2 같은 파일 여러 구간 | 줄 번호 기준 병합·중복 제거, 함수 구간을 중간에서 잘라 추가하지 않음 | 파일 JSON16KiB, 전체48KiB, 관련 파일4개. 긴 함수는 여전히 일부만 포함될 수 있음 |
| 3 함수별 검색 | 최대8개 변경 함수별 질의, 파일·함수별 교대 배정 | 후보 파일12·구간24 상한, 질의 제한/부분 함수를 화면에 안내 |
| 4 리뷰 주장 검증 | 초안 뒤 KEEP/REVISE/DROP 검증, 예상 결과를 별도로 다시 작성하고 원래 근거와 재대조 | 새 항목/근거 이동/누락 판정 거부. 검증 실패 시 초안을 성공으로 노출하지 않음. 같은 모델의 판단 오류는 가능 |
| 5 실제 PR 기반 평가 | 공개 Requests PR2건에서 결함2·정상4 최소 재현, 줄 범위 자동 점수와 의미 rubric 분리 | 원본 전체 PR 평가가 아닌 공개 PR 파생 잠정 gold. 독립 사람 라벨 검수 미완료 |
| 비용·안정성 | 각 호출 전 영속 예약·권한/취소/세대/lease 재확인, 최대2회·회당60초·전체150초 | 관측 토큰을 누적 보존. 사용자 코드 실행·자동 재호출 없음 |
| 화면 | 전송 범위·2단계 호출 동의, AI 근거 재검토 결과와 제외 사유 표시 | 과거 결과는 재검증 완료로 표시하지 않음 |

주요 파일: `app/domain/review/{context_plan,context_selection,retrieval,syntax_entry,verification,worker,provider,policy}.py`, `harness/verification.md`, `migrations/versions/0008_review_verification.py`, `scripts/{evaluate_context_retrieval,stabilize_review_quality}.py`, 대응 tests/evals/docs. 프론트는 AIReviewPanel/AIReviewCoverage 및 문구 테스트다. 원본 설계에는 [ADR-REVIEW-010](../../prism/docs/architecture/adr/review/ADR-REVIEW-010-evidence-first-verified-review.md)과 context-map/DECISIONS/소유 문서를 반영했다. architecture.json은 마지막 게시 SHA를 유지한다.

## 8KiB와16KiB 비교

[긴 함수 합성 비교](quality-stabilization/evidence-budget.json)는 같은91줄 함수에서 한도만 달리했다. 8KiB에서는 함수 구간 전체가 들어가지 않아 변경1줄·142byte만 남았고, 16KiB에서는91줄·약12.4KB가 들어갔다. 결함 사례는8KiB에서0/3,16KiB에서3/3 탐지; 정상 사례는 양쪽3/3 오탐 없음이었다. 작은 통제 실험의 결과이며 모든 저장소의 개선율이 아니다.

정상 사례 첫 호출 입력 토큰 예시는4634→7235(약56% 증가)였다. 한도는 항상 채우는 목표량이 아니며 실제 비용은 선택 코드·언어·검증 호출 여부에 따라 달라진다. 16KiB 결함 사례는 두 호출 합산 약12.8K 입력 토큰을 사용했다. system 지침24KiB는 코드48KiB와 별도다. GitHub 원본 파일 취득 상한200KB는 그대로다.

[실제 리랭커 비교](2026-09-28_evidence-context-comparison-2.json)에서는 규칙12/12·리랭커12/12로 필요한 근거를 보존했다. 이전9/12 누락은 이번 보호/병합으로 재현되지 않았지만 규칙 대비 추가 이득이 없어 채택 게이트는 여전히 불통과, 기본 OFF다. 첫 실행은12개 비교 후 진단 duration_ms 누락으로 집계에 실패했고 첫 artifact를 보존했다. 진단 호환성을 수정한 동일 비교는 완료했다.

## 품질 평가와 비용

| 최종 평가 | 결과 | 해석 |
|---|---|---|
| 일반 합성+언어 경계 | 자동46/46, 구조46/46 | 결과의 발생 조건·예상 결과·제안도 에이전트가 검수. 독립 사람 검수는 아님 |
| 기존 잘못된 주장3종×3 | 의미9/9 교정 | 정상 가드/가상 계약 오탐 제거, 실제 null 결함 보존과 잘못된 빈배열 설명 정정 |
| 공개 PR 파생 잠정 gold6종×3 | 자동11/18, 구조18/18 | 결함2종×3회 누락, 정상 명시적False 사례1회 오탐. 품질 FAIL |
| 응답/근거 검증 | 이번222평가 전부 구조 검증 완료 | 구조 통과가 의미의 정확성은 아님 |

첫 검증 지침은 알려진 잘못된 부연을 유지했다. 자동 위치 점수는 통과했지만 의미 검수에서 발견했고, 검증기가 `checked_consequence`를 별도로 작성하도록 변경한 뒤 같은9개를 다시 확인했다. 실패 이력은 지우지 않았다. 최종 gold의 0건 초안은 두 번째 검증을 생략하므로 놓친 결함을 되찾지 못한다. 같은 모델의 두 번째 판단도 가상의 반환 계약을 승인할 수 있었다.

이번 추가302회, 공유 승인 누적1059/3000·잔여1941회. 관측 입력1,306,888/출력39,734토큰이며 청구액은 아니다. 추가 자동 실행 예약 없음. [집계](quality-stabilization/evidence-summary.json), [의미 검수](quality-stabilization/evidence-manual-review.json), [승인 기록](../docs/PAID_EVALUATION_AUTHORIZATION.md)을 따른다. 공개 PR 파생/합성만 전송했고 조직 PR49의 이전1회 승인을 재사용하지 않았다. 제품에는 원문·초안·검증 응답을 저장하지 않는다. 평가 artifact는 검증된 합성/공개 파생 초안·결과만 보존하며 raw invalid 응답은 미보관이다.

## 구현 검증

- Linux 격리 PostgreSQL17에서 전체330 tests PASS. Pydantic body alias 관련 경고1개는 실패와 구분한다. 최종 토큰 보존 변경 후 worker7 tests 재검증 PASS.
- 구문/문맥/검증/평가 관련 순수 Python52 tests PASS. Windows DB tests는 기존 native/BSOD 미해결로 재실행하지 않았다.
- Ruff check·format163 files·mypy119 source files PASS. frontend112 tests·vue-tsc·Vite build PASS.
- 문서 검증78문서/320링크/26ADR PASS, 기존 문서 길이WARN2. backend 작업 기록42개·frontend30개 PASS. 비밀값 패턴 검사도 추적+미추적(무시 파일 제외) backend481개·frontend255개 PASS; 미지의 키 형식/과거 이력은 범위 밖이다.
- 실제 로그인한 PR 화면에서16/48KiB·관련4파일·최대2회·하루30회·새 동의 안내를 DOM으로 확인했다. 동의/새 리뷰 버튼을 누르지 않았고 새 조직 PR의 최종2단계 제품 흐름은 실호출 미검증이다.

프론트 최종112개에는 CHECKED/검증 생략/과거 필드 없음/미래 상태를 구분해 추가 검토를 허위 표시하지 않는4개 회귀를 포함한다. 최초 sandbox 실행은 esbuild 상위 경로 접근 거부로 시작하지 못했고 동일 명령을 정상 권한으로 재실행해112개 PASS였다.

회귀는 근거 누락·UTF8 직렬화 크기·악성/잘못된 검증 응답·두 번째 실패/취소/권한 철회/만료·예약/관측 사용량 보존을 확인했다. 의미 품질 FAIL을 이유로 schema·위치 검증을 완화하지 않았다.

## 로컬 적용과 복구

유휴 Job0을 확인하고 스키마만 `%TEMP%/prism-schema-before-0008-20260928.sql`에 백업했다. Alembic offline SQL을 Linux psql의 트랜잭션에서 적용해 revision0008과 기존 세대/토큰 조건을 포함한 CHECK를 확인했다. 기존 행 삭제/수정 없이 call_attempts 허용 범위만0..2로 확대했다. API 숨김 재시작 후 ready200, Vite200, AI ON·하루30·리랭커 OFF를 확인했다. 임시 테스트 DB/네트워크는 정리했고 평가용 리랭커는 중지했다.

롤백은 새 리뷰 접수를 중지하고 진행 Job을 확인한 뒤 이전 앱을 복원한다. 2회 호출 이력이 생겼다면 CHECK 완화를 유지하며 이력을 삭제/변조하지 않는다. 하향 migration은2회 행이 있을 때 명시 실패한다. 기존 저장 결과는 그대로 보존한다.

## 남은 판단

품질 안정화 완료로 선언하지 않는다. 공개 PR의 실제 호출부·전송 계약을 포함한 평가 확대와 독립 사람의 잠정 gold 라벨 검수가 우선이다. 0건 초안의 누락 평가와 별도 검증 모델/규칙의 비용 대비 효과는 후속 설계 대상이다. 새로운 조직 코드 전송·추가 기능·공개 배포·Git 게시·원본 하네스 동기화는 이번에 수행하지 않았다.
