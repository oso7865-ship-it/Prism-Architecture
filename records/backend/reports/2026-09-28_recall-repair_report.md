# 작업 리포트: 평가 계약 복원·누락 진단·프롬프트 비교

> 작성일: 2026-09-28
> 패키징/배포일: 해당 없음
> 작업 브랜치: dev
> 커밋/PR: 미커밋
> 상태 기록 버전: 1
> 상태 확인 시각: 2026-09-28T02:16:03+09:00
> 구현 상태: 완료
> 구현 근거: scripts/recall_evaluation.py, scripts/stabilize_review_quality.py, evals/recall-repair, 관련 테스트·문서의 working-tree 변경
> 로컬 검증 상태: 실패
> 로컬 검증 대상: 이번 평가 도구·고정 corpus·실험 후보 v1~v5 및 복원한 런타임 지침 working-tree
> 로컬 검증 근거: Linux359 tests PASS, Ruff/mypy PASS와 별개로 후보의 의미 품질·회귀 채택 게이트 FAIL. 아래 실행별 기록 참조
> 병합 상태: 미수행
> 병합 대상: origin/main
> 병합 근거: 이번 요청에 Git 게시·병합 포함 없음
> 배포 상태: 미수행
> 배포 근거: 품질 게이트 실패로 후보 미채택, 공개 배포 없음
> 실제 연동 상태: 완료
> 실제 연동 근거: DeepSeek 합성·공개 PR 파생 최소 재현293회 실제 시도. 조직 PR 제품 경로는 이번에 호출하지 않음
> 작업 범위: L
> 적용 스킬: terminal-ops, verification-loop, troubleshooting-report
> 적용 Gate: 코드·문서·Security·의미 품질 채택 게이트
> 위험도: 외부 유료 실행·환경 변경(비파괴적)
> 위험 작업 여부: 예

## 0. 작업 범위 확인

| 항목 | 내용 |
|---|---|
| 요청 | 사용자 승인한1~5 수정·평가·리포트 |
| 설계 | [작업 계획](../docs/work-plans/2026-09-28_recall-repair.md)을 먼저 작성 |
| 수정 | 평가 fixture/언어 oracle, 고정 기준선, 후보 지침, 구조화 진단, 단계별 지표·채택 게이트 |
| 보존 | 기존 working-tree, 과거 평가/리뷰, V4 16/48KiB·2회/리뷰·하루30리뷰·리랭커 OFF |
| 제외 | 조직 코드 새 전송, 대상 코드 실행, DB migration, 프론트 변경, Git 게시, 배포, 하네스 원본 동기화 |
| 한계 | 소수의 수동 재현·자체 합성 사례. 독립 사람 라벨 검수 미완료, 전체 실제 PR 성능이 아님 |

## 1. 결과와 채택 결정

**평가·진단 수정은 완료했지만, 리뷰 품질 안정화는 완료하지 못했다.** 최종 후보는 결함 위치6/6을 맞혔으나 발생 조건·실제 값·개선안까지 맞는 결함 응답은3/6이었다. 신규 사례24/24 통과도 이 실패를 상쇄하지 않는다. 기존 경계 회귀에서는 `range(0, 0, 0)` 예외를 빈 리스트로 잘못 설명하며 누락했다.

최종 후보 `rh1-5288a4f4de305498`은 [candidate-v5](../evals/recall-repair/candidate-v5)로 보존하고 **제품 지침은 작업 시작 전 스냅샷과 바이트 단위로 동일하게 복원**했다. 런타임은 `rh1-d634ca5b77229914`를 유지하며 API 재시작 없이 ready/Vite HTTP200을 확인했다. 기존 지침도 품질 문제가 있으므로 안정화 완료나 출시 가능 판정이 아니다.

| 요청 작업 | 수행 결과 |
|---|---|
| 1. 평가 계약 복원 | Requests 두 공개 PR의 소비 코드·세션 병합·테스트 요구사항을 보존한 core-v2 6사례. 과거 v1은 채택 근거에서 제외 |
| 2. 검토 지침 수정 | 계약→구체 입력→실제 동작→판정 순서, 언어 값 추적, 증거와 지시 분리, 출력 축약 등을 단계적으로 비교. 실패 후보 보존·제품 미채택 |
| 3. 원인 진단 | 평가 전용 후보 위치/관측 결과/REPORT·DEFER·REJECT/누락 계약 schema, 위치·크기·비밀 검증. 이후 실행은 verifier의 index/action/reason도 보존 |
| 4. 통제 비교 | 동일 입력·모델·temperature0·출력2000·60초·재시도0. 1단계 및 양쪽 모두2단계인 비교를 구분. 미사용4언어 사례와 기존 회귀 실행 |
| 5. 분리 판정·기록 | 위치 탐지/정상 오탐/형식/검증 삭제/의미 검수를 분리. 의미 검수 부재·실패·결과 해시 불일치 시 채택 불가 |

## 2. 실제 평가 결과

### 동일 두 단계 비교

| 지표 | 기존 지침+기존 검증 | 최종 후보+후보 검증 |
|---|---:|---:|
| 복원한 결함2종×3회 위치 탐지 | 3/6 | 6/6 |
| 설명·개선안까지 정확한 결함 응답 | 3/6 | 3/6 |
| 정상 사례에 남은 오탐 | 0/12 | 0/12 |
| 최종 형식/위치 검증 실패 | 0/18 | 0/18 |
| 위치가 맞던 초안의 검증 후 누락 | 0 | 0 |
| 유료 시도(검증 호출 포함) | 21 | 28 |
| 채택 판정 | FAIL | FAIL |

근거: [기존 양단계](quality-stabilization/recall-baseline-verified.json), [후보 양단계](quality-stabilization/recall-core-operators.json), [결과 해시에 연결한 의미 검수](quality-stabilization/recall-semantic-assessments.json). 의미 검수자는 Codex이며 독립 사람 검수가 아니다. 반복은 같은 사례의 안정성 관측이지 독립 결함6개 표본이 아니다. 위치 점수 개선을 정확한 리뷰 개선으로 표현하지 않는다.

### 전체 실험 이력

| 실행 | 시도 | 자동 통과/리뷰 | 핵심 관측 |
|---|---:|---:|---|
| recall-core-baseline | 18 | 15/18 | 기존 단일 생성, CA결함3회 누락 |
| recall-core-candidate | 18 | 15/18 | checks/output 정리, 결함5/6·정상 오탐2/12 |
| recall-core-diagnostic | 6 | 채점 제외 | 별도 진단도 Python 값·분기를 오해. 이전 생성의 내부 사고를 보여주는 기록이 아님 |
| recall-core-values | 18 | 15/18 | 언어 값 지침 추가, 위치6/6·정상 오탐3/12 |
| recall-core-verified | 27 | 18/18 | 검증 후 정상 오탐0, CA의 잘못된 조건/설명 잔존 |
| recall-core-witness | 26 | 16/18 | 구체 입력 지침 추가. 위치 삭제1·중복1. 삭제된 초안 설명도 틀렸으므로 올바른 주장 삭제로 단정하지 않음 |
| recall-core-compact | 24 | 11/18 | 출력 예시6→1 축약. 실패5: schema3·위치1·출력 종료1. 축약안 폐기 |
| recall-core-operators | 28 | 18/18 | v2에 연산값 예시 추가. 위치는 모두 맞지만 CA 의미3/3 실패 |
| recall-holdout | 36 | 24/24 | 신규 Python/Java/JS/TS 결함4종×3회 탐지12/12, 정상 오탐0/12, 의미 검수도24/24 |
| recall-regression | 36 | 22/22 | 기존 합성 회귀 자동 통과. 전체 자연어 의미를 별도 PASS로 인증하지 않음 |
| recall-boundaries | 35 | 23/24 | `range(0,0,0)` 미탐1, 초안0건으로 검증 미호출 |
| recall-baseline-verified | 21 | 15/18 | 이전 생성·검증 지침 모두 동결하여 최종 후보와 같은2단계 비교 |

모든 산출물은 [집계 JSON](quality-stabilization/recall-summary.json)에 연결했다. 원 실행 결과를 후속 성공으로 덮어쓰지 않았다. 신규 holdout-v1의 Python 변경 위치가 `pass`였던 문제는 **첫 모델 실행 전** 실제 `return zip(...)` 위치로 수정해 holdout-v2로 새로 동결했다. v1 파일/해시를 보존했고 v1은 호출하지 않았다. 이후 holdout 결과로 프롬프트를 수정하지 않았다.

## 3. 변경 파일

| 위치 | 변경 |
|---|---|
| scripts/build_recall_cases.py, evals/recall-repair | 원본 출처·소비 계약·고정 corpus/hash, 기존/후보 지침 보관 |
| scripts/recall_evaluation.py | 기준선 생성·검증 provider, 진단 schema/검증, 분리 지표, 결과 해시와 의미 채택 게이트 |
| scripts/stabilize_review_quality.py | --baseline/--diagnose, payload hash, 검증 결정 metadata, 기존 비용 예약·잠금·상한 유지 |
| tests/test_recall_oracles.py | 명시값 oracle: UTF-8 길이·빈 문자열/None·명시 True/False·세션 우선순위·corpus 무결성 |
| tests/test_recall_evaluation.py | 진단 거절·유료 예약·기준선 변조 차단·채택 시 의미 검수 강제 |
| tests/test_review_output_contract.py | 보존 예시와 실제 런타임 예시 모두 원 strict validator로 검사 |
| evals/real-pr-gold/README.md | v1 축약 오류와 기존 숫자의 적용 범위 정정 |
| architecture REVIEW/TESTING, 상태·비용 문서 | 평가 근거·신뢰 경계·현재 미채택 상태 동기화. 제품 계약 변경이 아니므로 새 ADR 없음 |

## 4. 검증과 비용

| 검사 | 결과/범위 |
|---|---|
| Linux 전체 pytest | **359 PASS**, 58.61초. 임시 PostgreSQL17·분리 내부망, 원문/.env/제품 DB 미사용 |
| 경고 | Pydantic authorization alias 경고1. webhook 동시성 테스트는 통과했으며 경고 원인 수정은 이번 범위 밖 |
| Ruff check / format --check | app/tests/migrations 및 신규·수정3개 평가 스크립트 PASS |
| mypy app | 119 source files PASS |
| API ready / Vite | 02:16 KST HTTP200/200, 재시작·사용자 새 AI 리뷰 없음 |
| 임시 자원 | 이번 테스트 DB의 고정 ID/tmpfs 확인 후 컨테이너·내부 network 정리, 개발 DB 유지 |
| 문서·기록 검사 | work-records strict44건, report-consistency, 이번 문서 상대 링크 PASS. architecture 문서78개/링크320개·helper 조합90개 PASS |
| 비밀 검사 | 기존 검사기를 메모리에서 tracked+non-ignored untracked로 확장해560개 파일 PASS. 원 검사기 파일은 수정하지 않음 |

초기 Ruff 장문/형식 오류와 테스트 삽입 위치 오류는 수정 후 같은 검사에서 PASS했다. 테스트 실행 성공을 LLM 의미 정확도로 대체하지 않았다. Windows native DB 테스트는 기존 BSOD 회피 지침에 따라 실행하지 않았다. 프론트 코드와 브라우저 UI는 이번 변경 대상이 아니다.

재현 명령: Linux 격리 환경에서 `python -m pytest -q -p no:cacheprovider`, `ruff check app tests migrations scripts/stabilize_review_quality.py scripts/recall_evaluation.py scripts/build_recall_cases.py`, 같은 경로의 `ruff format --check`, `mypy app`. 기록 검사는 `node GENERAL_HARNESS/scripts/validate-work-records.mjs --project-root . --plans docs/work-plans --reports reports --strict`, 아키텍처는 `python scripts/validate_docs.py`와 `python scripts/check_helpers.py`다.

문서 크기 경고3건(RELATIONS/RESULTS/REVIEW)은 자동 실패가 아닌 읽기 부담 안내로 남겼다. Git global ignore 읽기 권한 경고가 있었으나 저장소의 tracked/non-ignored 파일 검사는 완료했다. 패턴 검사가 모든 비밀 형식을 탐지한다는 뜻은 아니다. Git diff --check는 backend/architecture 모두 통과했고 줄바꿈 정규화 안내만 있었다. 최종 런타임 문서8개는 기준선 SHA-256과 일치했다.

이번 **293회**, 승인 누적 **1,352/3,000**, 잔여 **1,648회**. 검증 두 번째 호출·실패도 각1회 차감, 재시도/자동 예약 없음. 관측 토큰 입력1,147,951·출력53,812이며 실패 시 미관측 사용량이 있을 수 있어 청구 확정값이 아니다. 제품 팀 하루30개와 별도인 승인이다. [사용량 원장](quality-stabilization/usage.json)·[승인 문서](../docs/PAID_EVALUATION_AUTHORIZATION.md).

## 5. 트러블슈팅: 위치 적중을 리뷰 품질로 오인했던 문제

- 사건 상태: 평가 결함 수정 완료 / 모델 의미 오류 미해결
- 원인 상태: 축약/지표 오류 확인, 모델 내부 원인 미확인
- 선행 기록: [근거 보존·재검증 보고서](2026-09-28_evidence-first-review_report.md). 그 문서의 v1 잠정11/18은 과거 측정 기록이며 실제 공개 PR recall로 사용하지 않는다.

### 어디서 발생했나

2026-09-28 로컬 평가기·real-pr-gold v1·review 지침·두 단계 모델 검증. `deepseek-flash`, 비추론, 출력2000token, temperature0.

### 어떤 문제가 있었나

평가자가 알고 있던 원본 계약을 모델에 충분히 주지 않고 결함 탐지를 채점했다. 계약을 복원한 뒤에도 모델이 `None or ""`의 값, 함수 기본값, `range` 생성 시 예외를 오해했다. 위치 정답과 최종 구조 검증만으로는 이를 막지 못했다.

### 어떻게 발생했나

1. v1 축약에서 세션 fallback/UTF-8 소비 계약을 생략했다.
2. 모델 출력에 기대 줄이 있으면 자동 점수는 PASS였다.
3. 최종 후보 CA응답은 기대10줄을 적어도 빈 문자열을 None이라고 설명하거나 제공 테스트의 session 기본값True를 None으로 바꿨다.
4. 같은 모델의 검증이 이 설명을 KEEP했다. 별도 진단 역시 정확성 보증이 아니었다.

### 왜 발생했나

- **확인:** 축약 입력의 계약 손실과 위치 중심 채점이 평가 오류를 만들었다. v2에서 누락 계약을 복원하고 명시 기대값 oracle로 검증했다.
- **확인:** 이번 CA·길이 입력은 전체 제공됐다. 관련성이 낮다고 리랭커가 지운 사례가 아니며 16KiB 예산 부족도 아니다.
- **확인:** 모델이 생성한 관측 결과에 연산값·기본값·예외 시점 오류가 있다. 재검증은 독립된 결정적 실행 증명이 아니다.
- **미확인:** 학습 데이터, attention, 내부 추론 등 모델 내부 원인은 관측하지 않았다. “프롬프트 길이 때문에 생겼다”도 입증하지 못했으며 축약 실험은 오히려 형식이 악화됐다.

### 어떻게 해결했나

평가 계약 복원·정상 반례·원본/후보 해시·별도 구조화 진단·초안/검증 분리·최종 의미 검수 게이트를 구현했다. 주장 원인/효과/수정안이 틀리면 줄이 맞아도 FAIL이다. 원본 출력 해시와 일치하는 PASS 검수가 없으면 채택하지 않는다. 반복된 지침 실험은 위 표대로 보존했고, 기준을 충족하지 못한 후보를 제품에 적용하지 않았다. 이는 **평가와 채택 절차의 수정**이며 모델의 누락/환각 근본 해결은 아니다.

### 앞으로 어떻게 대응하나

| 조치 | 담당/실행 조건 | 완료 기준 | 상태 |
|---|---|---|---|
| 값·분기·예외의 정확한 주장 검수 | 다음 품질 작업 | 복원 핵심 결함6/6 의미 통과, 새 정상 오탐0, 기존 경계 누락0 | 미해결 |
| 프롬프트 추가 전에 모델 추론 설정/검증 방식 통제 비교 | 후속 담당 미정; 비용·지연 계약도 설계 후 | 동일 입력·동일 출력 예산으로 원인 분리, 정답 주입 없는 새 사례 확인 | 제안 |
| 공개 원본과 수정본 라벨 독립 검수 | 사람 검수자 미정 | 실제 계약·출처·허용 위치와 반례 재확인 | 대기 |
| 조직 실제 PR 종단 평가 | 새 전송 범위 동의 및 품질 후보 선정 후 | 제품 경로·권한·출력의 별도 검증 | 미수행 |

## 6. 인계

다음 작업자는 [최신 상태](../docs/PROJECT_STATUS.md), [평가 사용법](../evals/recall-repair/README.md), [의미 검수](quality-stabilization/recall-semantic-assessments.json)를 먼저 확인한다. core-v2와 holdout-v2는 이제 본 사례이므로 후속 튜닝 후에는 새 미사용 사례가 필요하다. 잔여 승인 횟수를 초기화하지 않는다. Git 커밋·푸시·배포는 수행하지 않았다.
