# 공개 PR 파생 gold v1

> 2026-09-28 정정: 이 v1은 계약 축약의 의미 손상으로 **채택용 평가에서 제외**한다. CA 세션 병합 제거와 길이 소비 계약의 부재를 확인했다. 과거 실행은 삭제하지 않으며 당시 자동 점수를 원본 PR 결함 탐지율로 해석하지 않는다. 복원 과정과 새 평가는 [recall-repair](../recall-repair/README.md)를 따른다.

실제 제품 평가의 시작점이다. [Requests #6589](https://github.com/psf/requests/pull/6589)의 문자열 바이트 길이와 [Requests #6074](https://github.com/psf/requests/pull/6074)의 빈 CA 환경 설정 결함/수정을 읽고 최소 재현6사례로 재작성했다. 원 PR 전체를 실행하거나 복제한 데이터가 아니다. cases-v1.json에 출처·고정 base/head SHA·근거 테스트 이름·변환 종류를 기록했다. 소스/테스트는 읽기만 했고 실행하지 않았다.

결함2·정상4. 원본 테스트의 의도와 분기를 에이전트가 대조해 라벨을 작성했다. **독립 사람 검수는 아직 없으므로 잠정 gold**다. Python/두 PR의 좁은 표본이며 Java/프론트/사용자 조직 PR의 정확도로 일반화하지 않는다. 실제 조직 원문은 포함하지 않는다. JSON의 provenance/rubric/expected 값은 모델 입력에 포함하지 않는다.

자동 위치 평가는 대표 줄 하나 대신 허용 구간과 결함 개수를 사용한다. 같은 결함 중복은 실패다. 이후 각 결과의 발생 조건·결과·정상 반례·추가 부연·불필요 질문을 rubric과 대조해 수동 의미 판정을 별도 기록한다. 자동 위치 통과를 의미 통과라고 보고하지 않는다. 검수 기록에 판정자 종류(agent/human), 근거, 원본 실행ID를 포함한다.

실제 유료 실행은 `python -m scripts.stabilize_review_quality evals/real-pr-gold/cases-v1.json <unique-run> --repeats 3 --verify --allow-paid-calls 36`. 최대36회 예약 가능 범위이나 초안0건은 검증 생략하므로 실제 사용은 더 적다. 공유3,000회 ledger에서 각 호출을 전송 전에 차감한다. 반환된 검증 원문은 보관하지 않고 strict 검증을 통과한 합성/공개 파생 결과만 보관한다. 기존 비용 기록을 지우거나 초기화하지 않는다.
