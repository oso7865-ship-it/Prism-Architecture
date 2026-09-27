# 품질 안정화 평가

2026-09-27 사용자가 승인한 총3,000회 범위의 합성 평가다. 실제 저장소 원문은 포함하지 않는다.

- 기존 문맥 corpus: ../context-retrieval/cases.json을 그대로 사용한다. 기존 Python guarded-null의 동적 입력 타입 계약은 불명확하므로 보편적인 오탐 정답으로 삼지 않는다.
- regression.json: 기존 review-harness/cases.json 7개 + experience-cases.json 3개의 입력과 라벨을 그대로 복사했다. 과거 단일 파일/락 선언 과잉 질문/주석 인젝션 회귀용이다.
- holdout.json: 프롬프트 수정 전 고정한16개(언어별4개, 안전8/결함8, 다중 파일8)다. SHA256 `ac84e441ebe2223194c8680028203ec06da1bb4275ad0ea6222831cf75414fca`. 이후 결과를 보고 프롬프트를 바꾸면 튜닝용으로 재분류해야 한다.
- rubric/expected_lines는 평가기에만 쓰며 모델에 전송하지 않는다. 모델 입력은 제품 prepare/enrich가 만든 코드 JSON이다. 관련 문맥 포함 여부도 별도로 기록한다.
- 구조 검사와 의미 검사를 분리한다. 자동 평가는 결함의 대표 줄 일치/추가 지적 수만 비교하므로 같은 줄의 틀린 설명을 잡지 못한다. 결과 문장을 수동 검수한다. TS의 숫자0 기본값 사례는 기본값을 '미설정일 때만 사용'하는 의도를 전제하므로 명세 불명확성도 수동 확인한다.
- 3회 반복은 작은 고정 사례의 관측 안정성일 뿐 실제 PR 정확도/통계적 신뢰구간/공개 출시 검증이 아니다.

실행: `.venv/Scripts/python.exe -X utf8 -m scripts.stabilize_review_quality evals/quality-stabilization/holdout.json unique-run-name --repeats 3 --allow-paid-calls 48`.

## 단계별 사용 이력

holdout와 confirmation의 결과를 보고 지침을 수정했으므로 최종 재평가에서는 회귀용 사례로 분류한다. 이름에 holdout이 남아 있어도 최종 지침의 독립 성능으로 합산하지 않는다. final-regression은 기존 문맥12개+단일 파일10개의 동일 입력/정답 복사본이다.

- confirmation.json:12개, 처음 고정 SHA `3c5a3cc001fe149cd0ecb97f254cfc72d8519a6f48e1831a12b0a57aca8bd3fe`. 일반 null 매개변수·미제공 함수 질문과 실제 HTML 질문 유지 검증. Java 반복문 결함의 기대5줄과 모델 대표4줄 차이는 정답을 바꾸지 않고 의미 검수에서 따로 설명한다.
- acceptance.json:12개, SHA `8c249edc2ab452ecf039d0c0b3024fd99b9f236d33c023b3e56bfc3279418103`. 최초35/36 자동 통과에도 잘못된 조건식 요약·배열0 경계 제안을 발견해 후속 지침 수정에 사용했다. 이후 semantics-fix의5회 반복은 독립 검증이 아닌 회귀다.
- acceptance-v2.json: 최종 `rh1-d927e0b9a90199c6`를 고정한 뒤 작성한 별도12개, SHA `15b71be11a2ef893b508227f49226623ad2506c1a5dca2d7ede3524896a4ae70`. Python/JS/TS/Java 단락 평가, 배열 길이0과 음수, Python range의 step0을3회씩 검증한다. 원본 입력/라벨을 유지했다. 후속 언어 계약 지침 수정에 사용되어 현재는 회귀로 재분류한다. 앞선 실패 유형에서 파생한 작은 검증집합이며 새로운 업무 도메인 전체에 대한 독립 정확도는 아니다.

분모에는 실패를 포함한다. 자동 채점이 놓친 요약과 제안 오류, 대표 줄 선택 차이, 입력 계약이 모호한 사례는 보고서에서 분리한다. 같은 줄 일치만으로 의미 품질을 통과 처리하지 않는다.

각 실행은100회 이하이며 정확한 사례 수×반복 수를 명시한다. reports/quality-stabilization/usage.json에 호출 직전 예약하고 전체3,000회를 강제한다. STARTED/실패도 소모한다. 자동 재시도는 없다. 연결/인증/요금제 장애가 관측되면 즉시 배치를 멈춘다. 동일 실행 이름/결과 덮어쓰기는 거절하고 동시 실행은 lock으로 막는다. 프로세스 강제 종료 뒤 lock이 남으면 프로세스가 종료됐는지 확인하고 사용 기록을 보존한 뒤 복구한다.

검증된 합성 결과만 저장한다. 실패는 허용된 오류 코드, schema 필드명/타입, 숫자 근거 위치만 기록한다. raw 응답/예외 메시지/API 키는 저장하지 않는다. 실제 제품 PR 평가에 이 합성 전용 도구를 사용하지 않는다.

## 최종 채택과 재평가

- thinking-comparison.json: 기존 사례에서12개를 고른 동일 입력 비교, 비추론/추론 low 각24회. 둘 다 자동22/24, 추론 오탐·요약 모순 때문에 제품에 채택하지 않았다. `--evaluation-thinking`은 scripts 전용이며 제품 설정을 바꾸지 않는다. 추론 원문은 저장하지 않는다.
- builtin-acceptance.json: 언어/표준 내장 규칙 구분 지침 c3ab를 고정한 뒤 새로 만든12개(정상6/결함6), 최초36/36. 문자→정수, 빈 min, JSON 파싱, Invalid Date, substring 경계를 검증한다.
- final-boundaries.json: acceptance-v2+builtin-acceptance의 원본24개 복사본. 서버 조합 요약 rh1-6ec65eef38a071f7에서72회 회귀한다. 이는 새 독립 평가가 아니다. 모델 자유 summary 대신 제품에 표시하는 검증 결과 요약을 평가 기록에 저장한다. 과거 파일을 새 형식으로 바꾸지 않는다.

최종 버전은 rh1-6ec65eef38a071f7. 언어 규칙 구분 후에도 JS 요약 모순1건이 재현되어 ADR-REVIEW-009로 서버 조합을 채택했다. 원래 모델 요약의 문제를 숨겨 모델 자체 정확도 개선이라고 주장하지 않는다.

고정 corpus SHA256:

- thinking-comparison.json: `d82269561d14948edc8cf4e939813c8b8c5b4cb69e6717144264b1eea1c4ef86`
- builtin-acceptance.json: `9a08beef21e16b556994d164d557c61596eec95154af571e5a25471f2cdaec66`
- final-boundaries.json: `42d3da76e0b578e0d47ced5c97be0d55f6f27fb1f84c3f1af1af9503f7b4ac34`
