# 계약 보존 평가와 누락 진단

이 데이터는 제품 DB/사용자 조직 원문과 분리한 평가 전용이다. 제품의 권한·16/48KiB·최대2회·출력 schema는 변경하지 않는다. 직접 작성한 최소 재현이며 원본 전체 PR이나 독립 사람 승인 gold가 아니다.

## v1 정정과 v2

이전 `../real-pr-gold/cases-v1.json`은 이력으로 보존하지만 채택용 점수에서 제외한다. CA 원본의 `merge_setting(None, session)`을 없애고 반환값을 곧바로 bool로 바꿔, '없음'과 '빈 문자열'의 효과를 혼동했다. 길이 사례는 Content-Length 소비자/테스트 대신 짧은 주석만 남겼다. 기존11/18·누락6은 그 잠정 기준의 관측이며 원 PR 탐지율이 아니다.

`core-v2.json`: 공개 Requests #6589/#6074에서 소비자·비매핑 세션 병합·관련 테스트 계약을 보존한6개 수동 재현. 결함2/정상4, 세 번 반복은 서로 다른 결함6개가 아니다. 정답은 `expected_locations` 및 rubric에 있으며 네트워크에 보내지 않는다. patch의 실제 테스트 코드는 요구 동작의 근거로 보내되 실행했다고 주장하지 않는다.

`tests/test_recall_oracles.py`는 직접 작성한 참조 연산으로 없는 env와 빈 문자열, 명시적False, UTF8/bytes의 예상값을 검사한다. corpus 문자열이나 원격 소스를 exec/eval/import하지 않는다. 변경 줄·문맥 줄을 구분하며 오류 원인은 구현의 변경 줄에 고정한다. 정상 코드를 오탐한 뒤 정답을 바꿔 통과시키지 않는다.

## 동결과 비교

`baseline-*`는 수정 전 지침의 동결 사본. Python system 전체와 각 파일 SHA를 검증하고 제품과 같은 모델/temperature0/비추론/2000출력/60초/재시도0으로 호출한다. `candidate-v1/`은 계약 순서만 정리한 첫 후보다. `corpus-manifest.json`은 첫 평가 전에 core와 holdout을 함께 동결했다. 현재 제품 입력과 같은 prepare를 거치며 payload SHA를 각 실행에 남긴다.

`holdout-v1.json`은 수정 결과를 보기 전에 작성한 Java/Python/JS/TS의4쌍8사례다. 입력/정답은 만든 에이전트가 알고 있으므로 완전한 blind benchmark가 아니다. 출력에 따라 지침을 튜닝하면 후속에는 회귀 집합으로 재분류한다. 실제 PR 전체나 운영 분포의 성능으로 일반화하지 않는다.

```sh
python -m scripts.stabilize_review_quality evals/recall-repair/core-v2.json unique-baseline --repeats 3 --baseline --allow-paid-calls 18
python -m scripts.stabilize_review_quality evals/recall-repair/core-v2.json unique-candidate --repeats 3 --allow-paid-calls 18
python -m scripts.stabilize_review_quality evals/recall-repair/core-v2.json unique-final --repeats 3 --verify --allow-paid-calls 36
```

지적0건이면 검증을 생략하므로 실제 사용량은 예약 가능한 최대보다 작을 수 있다. 각각 전송 직전 공유 usage.json에 차감하고 기존 출력 덮어쓰기와 동시 실행을 거절한다. 평가 시도는 실패도 차감한다.

## 진단과 지표

`--diagnose`는 별도 소규모 호출이다. 파일/줄·관측 효과·REPORT/DEFER/REJECT·보류 계약만 반환한다. 긴 사고과정을 요구하지 않으며 이전 호출 내부에서 어떤 생각을 했는지 증명하지 않는다. 진단 응답도 환각할 수 있다. 근거 줄·비밀·크기·enum을 검증한 합성 결과만 보관한다. 제품 점수에 합산하지 않는다.

자동 지표는 결함 위치 재현율·정상 오탐·질문 수·형식 실패·초안 누락·검증 후 추가 누락을 분리한다. 올바른 줄을 찍고 틀린 동작을 설명할 수도 있으므로 최종 원인·입력·결과·정상 반례·제안의 의미를 별도 검수해야 한다. 에이전트와 사람 검수를 구분한다. 최신 결과는 `../../reports/_LATEST.md`가 가리키는 Report를 따른다.

## 이번 실행 결과와 재개

[전체 보고서](../../reports/2026-09-28_recall-repair_report.md)와 [집계](../../reports/quality-stabilization/recall-summary.json)를 따른다. 최종 candidate-v5는 rh1-5288a4f4de305498, 위치6/6·의미3/6으로 미채택했다. app의 제품 지침은 baseline과 동일하게 복원했다. candidate-v1은 checks/output 정리, v2는 Python 값 지침, v3는 구체 입력 결합, v4는 출력 예시 축약, v5는 v2에 연산값 예시 추가다. 실험 후보를 실행 중인 제품에 복사하지 않는다. 후보 재현은 별도 checkout에서 해당8개 문서를 배치하고 해당 결과에 기록된 구현/schema hash와 비교한 뒤 실행한다.

holdout-v1의 Python pass 앵커는 첫 모델 실행 전에 실제 return 앵커로 고쳐 holdout-v2에 새로 동결했다. v1/원 manifest 보존, v1 유료 실행0회. v2는 최초 실험24/24 통과했지만 이제 공개된 회귀 자료이며 새로운 튜닝의 독립 holdout이 아니다. 독립 사람 라벨 검수는 아직 없다.

동결 기준선 양단계 실행 예: `python -m scripts.stabilize_review_quality evals/recall-repair/core-v2.json <새-run-name> --baseline --verify --repeats 3 --allow-paid-calls 36`. --diagnose는 verify/baseline과 섞지 않는다. 현재 기본 실행은 복원된 제품 지침이다. 유료 승인 잔여/실행명 충돌/잠금 검사는 항상 유지한다.

`quality_metrics`의 위치 탐지율과 `verifier_removed_expected`는 자연어 정답을 의미하지 않는다. 후자는 정답 위치가 있던 초안이 최종에서 사라진 수이며, 초안 설명 자체가 틀렸다면 올바른 주장 삭제로 볼 수 없다. format/provider/evidence validation 실패를 별도로 집계한다. 진단 결과는 별도 호출의 관측이며 실제 생성의 숨은 추론 기록이 아니다.

`adoption_gate`는 자동 채점 PASS 외에 각 응답의 result_digest와 일치하는 의미 검수 PASS를 요구한다. 실제 원인·효과·수정안이 틀린 지적, 누락, 오래된 검수나 미검수는 채택 실패다. [이번 의미 검수](../../reports/quality-stabilization/recall-semantic-assessments.json)는 Codex 검수이며 독립 사람 검수로 표시하지 않는다.
