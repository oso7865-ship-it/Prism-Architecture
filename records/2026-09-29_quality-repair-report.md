# 품질 보수 구현과 496회 비교 평가

> 작성일: 2026-09-29 · 상태 확인: 2026-09-29T19:41:15+09:00
> 규모: XL · architecture/main, backend/dev, frontend/dev · 미커밋·미푸시
> 구현: 완료(추론/Responses는 평가 전용, OSV는 어댑터만)
> 로컬 기능 검증: PASS · 전체 모델 의미 품질: 미통과
> 병합/배포: 이번 작업에서 수행하지 않음
> 실제 연동: 공개·합성 DeepSeek API 호출496회. 새 비공개 PR E2E와 OSV 실통신은 범위 밖
> 적용: Terminal Ops, Verification Loop, UI UX/Browser QA, 출력·권한·외부 전송 경계 검사

## 0. 작업 범위 확인

| 항목 | 내용 |
|---|---|
| 요청/근거 | 추천 순서로 보수. [후보6개](2026-09-29_quality-improvement-proposal.md), [사전 계약](2026-09-29_quality-repair-plan.md) |
| 순서 | 1+3 발견·전달 복구 → 2 연산·수정안 → 4/5 문맥·독립 근거 → 6 조건부 추론 |
| 수정 | Review 작업자/검증/문맥/제한 의미 검사, 결과 UI, 평가 도구, ADR·소유 계약 |
| 제외 | DDL, 사용자 코드 실행·설치, 무제한 탐색, 자동 수정/댓글/병합, EC2 배포 |
| 위험 경계 | 최대2회 예약, 권한·연결 세대·취소·lease·고정 SHA, 비밀 필터, 원문 비저장, 전송 예산 |
| 읽은 계약 | CORE, REVIEW, STANDARDS, PRIVACY, FRONTEND, RESULTS, ADR-REVIEW-010/011/012, PACKAGE_RULES, CODE_CONVENTIONS |
| 한계 | 고정 소규모 재현 평가. 독립 사람 라벨·전체 설명 의미·대규모 PR 품질 보증 아님 |

## 1. 적용 결과

| 문제 | 보수 | 화면 변화 |
|---|---|---|
| 기존 오판을 삭제한 뒤 실제 결함 미복구 | 검증 호출의 new_findings와 전체 file_checks 검사 | 새로 찾은 항목 수·파일별 범위 |
| 첫 응답 오류로 검토 종료 | 남은 한 호출로 원래 입력 독립 재검토, 잘못된 초안 재전송 금지 | 복구 성공 표시, 두 번째 실패를 정상0건으로 치환하지 않음 |
| 점검 대표 위치와 결함 근거 혼합 | 대표 줄만 서버가 제공된 변경 줄에서 선택 | 소비 코드의 유효 근거를 점검 줄 오류로 거부하지 않음 |
| 연산 순서/빈 값 해석 오류 | 제한 Python 연산·정확한 builtin dict.get/or 예시 | 지원 범위의 값 차이를 입력에 보충 |
| 수정안이 정상 동작까지 변경 | 선택적 expression_repair/명확한 range 대안을 제한 비교 | 반례 경고, 결함 자체는 유지 |
| 같은 파일의 문맥 부족 | 보이는 심볼·기존 제공 파일·같은 SHA의 작은 파일 보충 | 추가 범위와 미확보 이유 |
| AI가 보안 근거 누락/호출 실패 | 좁은 Flask 입력→셸 흐름을 독립 보존 | AI 제안과 별도 신호, 실패 시 부분 결과 |

기본 **ChatDeepSeek·Flash·추론OFF·2,000 출력 토큰/회·최대2회·팀30회/일·동시1개**를 유지한다. 정책은 BOUNDED_CODE_V5이며 계약/스키마가 하네스 버전 해시에 반영된다. 기능 보수 채택과 전체 품질 승인은 구별한다.

문맥은 최대2요청·각4초·기존 제공 파일 전체160줄 이하만 보충한다. 파일16KiB/코드48KiB/팀 문서 별도12KiB를 유지한다. 변경 근거를 제거하거나 큰 파일의 임의 조각을 더 붙이지 않는다. 전체 호출 그래프 검색은 아니다.

식 검사는 서버가 구현한 AST 화이트리스트 해석이다. 분석 소스 eval/exec/import/build는 없다. 최대160자·40노드·깊이12·2변수·49입력·range32개이며 지원 밖 식/객체/언어는 미검증이다. 원본/수정 소스 식은 결과에 저장하지 않는다. PRESERVES_SAMPLES도 전체 수정안 정답을 증명하지 않는다.

PY-INPUT-SHELL-1은 연속 Python 구간의 알려진 Flask 입력과 os.system/subprocess(shell=True)만 다룬다. 이름 가림·재할당·미제공 줄·알 수 없는 호출에서 보수적으로 중단한다. 전체 taint 분석이나 공격 성공 증명이 아니다.

## 2. 주요 변경 파일

다음은 저장소 기준 경로다. 문서와 실행 기록은 Prism-Architecture에만 둔다.

| 저장소/파일 | 변경 |
|---|---|
| backend app/domain/review/{worker,verification,empty_review,empty_schema,refinement,output_schema}.py | 복구·새 발견·점검·예약·부분 결과 |
| backend app/domain/review/{semantics,dictionary_observations,supplement}.py | 제한 의미/반례·고정 SHA 문맥 |
| backend app/domain/review/{security_evidence,dependency_evidence}.py | 독립 신호·공개 의존성 어댑터 |
| backend app/domain/review/{policy.py,harness/} | V5·컨텍스트 요청·스키마 표현 압축·지침 예산 |
| backend scripts/quality_repair_*.py | 대조·후보·새 사례·집계·로컬 재검증 |
| backend tests/{test_quality_repair,test_empty_review,test_review_verification_worker,test_standards}.py | 계약/한도/상태/위치 회귀 |
| backend .gitignore | 테스트 환경 파일·로컬 감사 임시물 제외 |
| frontend src/features/analysis/{ReviewSuggestionCheck,IndependentSecurityEvidence,ReviewVerification,AIReviewCoverage,AIReviewPanel,ReviewIssueCard}.vue, reviewModel.ts | 경고·범위·복구·신호·기존 결과 호환 |
| frontend tests/quality-repair.test.ts | 안전한 렌더링·문구·상태 회귀 |
| architecture ADR-REVIEW-013, REVIEW/RESULTS/PRIVACY/FRONTEND, 결정/문서 맵 | 계약·결정·표시/반출 범위 |

## 3. 유료 비교

근거: [집계](quality-evaluations/quality-repair-20260929/summary.json), [설정](quality-evaluations/quality-repair-20260929/config.json), [R2](quality-evaluations/quality-repair-20260929/config-r2.json), [R3](quality-evaluations/quality-repair-20260929/config-r3.json), [동결 기준](quality-evaluations/quality-repair-20260929/baseline.json), [새 사례](quality-evaluations/quality-repair-20260929/fresh-cases.json).

248평가·496호출. 기존42사례=결함20/정상22, 어려운 부분집합14사례=결함6/정상8. 사례·후보당1회이며 분산/유의성을 측정하지 않았다. ‘결함 도달’은 기대 위치와 확정 항목의 전달 기준으로, 모든 원인·영향·수정안이 옳다는 뜻은 아니다.

| 후보 | 사례 | 유효 전달 | 결함 도달 | 정상 오탐 | API 중앙 / p95 |
|---|---:|---:|---:|---:|---:|
| B0 동결 기준 |42|40|18/20|0/22|3.062 / 3.969초|
| R1 복구·검증 확장 |42|41|18/20|1/22|3.227 / 4.000초|
| R2 일반 연산 관측 |42|41|19/20|1/22|3.289 / 5.203초|
| **R3 정확한 dict 관측 포함** |42|41|**19/20**|**0/22**|3.305 / 4.032초|
| J1 Responses json_schema |14|13|5/6|0/8|3.961 / 7.938초|
| T0 비추론·출력4,000 |14|14|5/6|1/8|3.492 / 4.437초|
| T1 조건부 높은 추론·출력4,000 |14|12|4/6|1/8|5.070 / 19.046초|
| T2 조건부 높은 추론·출력2,000 |14|10|4/6|0/8|4.344 / 11.266초|

R3의 입력/검증 계약을 구현에 반영했다. 결함 도달1건 증가, 정상 오탐은 기준과 같았다. R1/R2 정상 nested-copy 오탐이 R3에서 사라졌지만 dict 관측의 단독 효과로 단정하지 않는다. 확률적 변동이 가능하다. 시간은 Provider 호출 합이며 GitHub·대기·화면 전체 지연이 아니다.

새12사례는 await 저장, 테넌트 SQL, 배열 경계, 스트림 오류 정리, 정렬 상태 변경, 인증 실패 허용의 결함/정상6쌍이다. **B0/R3 모두 결함6/6·정상 오탐0/6·유효12/12**였다. 에이전트 작성 합성이며 독립 사람 라벨이 아니다. 이 결과로 R3의 일반화 우월성을 주장하지 않는다. 관찰 후에는 회귀셋이다.

Responses의 실제 API 호환성은 확인했지만 근거 분류 오류가 남았다. 높은 추론은 공급자 실패와 지연이 늘어 둘 다 기본 채택을 보류했다. 숨은 추론 필드는 저장하지 않았다. [DeepSeek 공식 Responses 계약](https://api-docs.deepseek.com/api/create-response/).

공급자 실패4호출(T1 1/T2 3). 관측 입력2,130,131·출력111,952토큰이며 실패4회의 사용량은 미확인이라 하한이다. 확정 청구 금액으로 환산하지 않았다.

## 4. 의미 검수와 남은 실패

| 사례 | 관측 | 판정/조치 |
|---|---|---|
| e039b4bf0e2d CA 빈 문자열 | 실제 결함 전달. session 기본 True 입력 설명에 `session_value is None` 경로를 섞음 | 탐지 회복, 인과 설명 일부 오류 |
| 4c612348a604 range0 step | n=0 ValueError는 맞지만 range(n)/step1 대안이 기존 성공값을 변경 | n=3의 [0]→[0,1,2] 및 음수 반례 경고. 결함 보존 |
| 0c47bb65c1ee 내부 dict 얕은 복사 | 호출자 상태 변경/결과9, 내부 복사·deepcopy 제안 | 선택 사례 검수에서 타당 |
| 898c474a9d7d 정상 내부 복사 | R1/R2 오탐, R3 없음 | 회귀 보존, 입력 보강의 단독 효과로 단정 금지 |
| 90900a02e0f4 null 분기 | null 역참조/non-null 빈 문자열, 분기 반전 | 선택 사례 검수에서 타당 |
| 65d1d2fad0d4 comparator overflow | 감산 overflow, Integer.compare | 선택 사례 검수에서 타당 |
| 2cdf3efa43ff int overflow | SUPPORTED인데 assumptions 존재 | **전달 실패1건**. 전제를 삭제하거나 확정으로 강제 승격하지 않음 |

248출력 전수 의미 검수가 아닌 선택 사례의 정적 검수다. 정상 오탐0과 모든 설명/수정안 정확은 별개다. **전체 의미 품질 게이트는 미통과다.**

최종 수정안 경고 보강은 추가 유료 요청 없이 R3 원응답54개를 재검증했다. [재검증](quality-evaluations/quality-repair-20260929/postprocessing-replay.json): 유효53, 기존 분류 실패1. 유효53개 모두 현재1차 입력/시스템 지침 해시가 원호출과 일치했다. range 반례 경고를 확인했다. 후처리 경고는 모델 원수정안이 옳았다는 증거가 아니다.

## 5. 검증 결과

| 검사 | 결과/범위 |
|---|---|
| Linux Docker backend 전체 | **452 passed**, Pydantic cursor alias 경고1 |
| 위치 회귀1개 추가 후 관련 검사 | **38 passed**. 전체를 다시 돌렸다는 뜻은 아님 |
| mypy | **137 source files passed** |
| 변경 대상 Ruff | app/tests/quality_repair 스크립트 PASS |
| 전체 scripts 린트 잔여 | 기존 check_backup_restore.py 3건·check_container.py 2건 E501 |
| frontend Vitest | **131 passed** |
| vue-tsc/Vite build | PASS |
| 출력/범위 | 새 발견·중복·누락 파일·위치·스키마 property title 보존·4언어×3목적 지침 예산 |
| 권한/상태 | 실패 초안·취소·철회·lease·문맥 보충 중 취소·최대2회 예약 |
| 외부 경계 | 제공 심볼/파일·고정 SHA·입력 일치·한도, OSV 동의/사설 registry 거부·모의 응답 |
| UI | 합성 경고 펼침·복구·별도 신호·escaping·기존 필드 호환 |
| 문서/Git | 문서108개·로컬 링크483개·ADR32개 검사 PASS, diff --check 통과. 긴 문서5개 분할 검토 경고 |

UI320/375/414/768/1280px의 DOM client/scroll 폭은305/305,360/360,399/399,753/753,1265/1265로 가로 넘침이 없었고 버튼 최소 높이44px였다. 상세 펼침과 캡처를 확인했다. 합성 미리보기 검증이며 실제 로그인·원문 열람·새 유료 리뷰의 E2E 증거로 확대하지 않는다.

```text
backend Linux /workspace (read-only source mount)
/app/.venv/bin/python -m pytest -q --tb=short -p no:cacheprovider
backend Windows (pytest 실행하지 않음)
.venv/Scripts/ruff.exe check app tests scripts/quality_repair*.py
.venv/Scripts/mypy.exe app
.venv/Scripts/python.exe -X utf8 -m scripts.quality_repair_report --root ../prism/records/quality-evaluations
frontend
npm test -- --run
npm run build
architecture
../prism-backend/.venv/Scripts/python.exe -X utf8 scripts/validate_docs.py
```

## 6. 장애·후속 조치

| 위치/증상 | 원인 | 해결 | 후속 |
|---|---|---|---|
| 혼합 언어·문서 지침24KiB 초과 | 새 스키마·반복 문구 증가 | 스키마 표현/예시 반복 축소, 실제 title 필드 보존 | 4언어×3목적 예산 회귀 |
| ‘좋은’ 수정안 검사 실패 | max(n,1)이 음수 성공값 변경 | 원동작 보존 테스트 대안으로 정정 | 의도 대신 예시값 비교 |
| file_checks 소비 코드 위치 실패 | 대표 줄/실제 근거 역할 혼합 | 대표 줄만 서버 결정 | 변경 줄2·근거 줄6 회귀 |
| JSON 유효해도 전달 실패 | SUPPORTED/assumptions 계약 충돌 | 실패 명시, 정상 결과로 위장 금지 | 전제 손실 없는 분류·전달 계약 설계 |
| test.env Git 미제외 | 기존 `.env` 이름 패턴 불일치 | `*.env`·audit-artifacts 제외 | 커밋 전 비밀/임시물 선별 |
| 새 ADR 문서 검증 실패 | 필수 항목 제목 누락 | 배경·대안·영향과 한계·소유 문서와 검증 보완 후 PASS | 새 ADR은 지정 형식으로 검증 |

OSV는 public PyPI uv.lock/public npm package-lock v2/3의 패키지·정확한 버전만 취급하는 어댑터다. 최대256KiB/100개·고정 endpoint·5초·응답256KiB·redirect/proxy 차단, withdrawn/페이지 누락을 처리한다. **제품 자동 전송 미연결·실통신 미검증**이며 기존 AI 동의로 새 공급자에 전송하지 않는다. 버전 일치는 취약 코드 도달 가능성 확인이 아니다. [OSV 공식 query 계약](https://google.github.io/osv.dev/post-v1-query/).

## 7. 사용량·기록·최종 판정

사전 상한600 중**496회**. 현재 캠페인1,431+479+496=**2,406/5,000회**, 잔여2,594회. 과거1,563 포함 전체3,969/절대상한6,563회. [공통 원장](quality-evaluations/usage.json)이 기준이며 실패도 집계한다. 최소1,000회는 앞선 실험에서 이미 충족했다.

원호출/평가 결과는 architecture의 quality-evaluations/quality-repair-20260929에 보관한다. 공개·합성 평가 출력과 메타데이터이며 비공개 PR 원문·키·숨은 추론은 포함하지 않는다. 이전 산출물은 소급 변경하지 않았다. baseline.json은 동결 프롬프트/스키마이고 신뢰된 기존 서버 코드 임시 사본은 backend의 Git 제외 audit-artifacts다. 다른 PC에서 기준 실행기를 재현하려면 해당 서버 스냅샷 복원이 필요하다. 결과/해시/동결 지침은 architecture 기록으로 검수할 수 있다.

기능 보수와 경계 검증은 완료했다. 관측한 품질 상향은 제한된 회귀의 결함 도달1건 증가다. **전체 의미 품질은 미통과이며 누락0·배포 준비 완료를 선언하지 않는다.** 다음 순서는 전제를 숨기지 않는 분류·전달 계약, 인과 설명/수정안 별도 검수, 독립 사람 라벨과 더 큰 실제 PR이다. LATEST와 Working Context를 갱신했다.
