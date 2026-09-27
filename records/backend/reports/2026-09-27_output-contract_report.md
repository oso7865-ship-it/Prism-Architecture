# 작업 리포트: 출력 형식과 질문 채택 기준 보완

> 작성일/상태 확인: 2026-09-27T17:14:15+09:00
> 규모: M · backend dev / architecture main working-tree · 미커밋·미푸시
> 구현: 완료 · 로컬 검증: PASS · 실제 DeepSeek 합성 평가: 형식10/10, 자동9/10
> 품질 전체 통과: 아님. 대표 위치 기준 실패1개를 유지한다.
> 로컬 적용: API 재시작·ready 확인 · 병합/배포: 미수행
> 적용: terminal-ops, 출력 계약/근거 검수, 문서 무결성
> 작업 브랜치: backend dev / architecture main (당시 작업 기록)
> 커밋/PR: 미커밋·미푸시
> 작업 범위: M
> 적용 스킬: terminal-ops, quality-gate
> 적용 Gate: 출력 계약·근거 검수, 문서 무결성
> 위험도: 모델 출력 정책 / 제한 유료 평가

> 이후 문맥 구현과 현재 상태는 [문맥 수집·리랭커 비교](2026-09-27_context-reranking_report.md)를 따른다. 이 문서는 당시 출력 지침/평가 증거로 유지한다.

## 0. 작업 범위 확인

사용자는 형식 실패2개·근거 없는 질문1개의 대처방안 적용과 리랭커/환각 방어 도입 상태 확인을 요청했다. [설계와 체크리스트](../docs/work-plans/2026-09-27_output-contract.md)에 수정·제외 범위와 검증 순서를 먼저 기록했다.

수정 대상은 제품 리뷰 지침 checks/output, 예시·출력 거부 회귀, 백엔드와 아키텍처 소유 설명이다. 실제 검색 구조·ReviewOutput schema·API·DB·권한·의존성은 바꾸지 않는다. 기존 미커밋 기능과 과거 결과는 보존한다. 개발 에이전트 하네스는 현재 상태 기록만 갱신한다. ADR-REVIEW-006 계약의 명확화이므로 새 ADR은 만들지 않았다.

유료 비교는 사용자가 승인한 대처방안의 마지막 단계로 동일 합성10사례 각1회만 수행했다. 실제 저장소 소스/사용자 피드백 전송, 자동 재시도, 추가 배치는 없다. 서버 적용은 진행 Job/리뷰0건 확인 뒤 해당 로컬 API만 재시작했다.

## 1. 변경 내용과 판단

- 모델은 summary 문자열/ issues 배열/ limitations 문자열만 출력한다. NEEDS_CONTEXT도 issues 내부에 넣고 서버가 표시용 questions로 분리한다. 이 두 형식을 섞지 않도록 필수 필드·타입을 명시하고 정상 지적/조건부 질문/0건 예시를 추가했다.
- 실제 변경 코드에 구체적인 우려 동작이 있고, 이름 붙인 미확인 전제의 답이 수정 판단을 바꾸는 경우만 질문으로 채택하도록 했다. 호출부·구현이 없다는 사실만으로 만든 질문은 검토 한계로 기록한다. 결함이 없는 결과도 정상이다.
- 수정 제안은 제공된 다른 분기에서도 안전한지 확인하도록 했다. 단순 null 조건 반전으로 다른 null 역참조가 남는 대안을 제시하거나, 관찰되지 않은 피해를 과장하지 않도록 했다.
- strict validator는 유지한다. 잘못된 JSON을 자동 보정하거나 항목을 조용히 삭제하지 않는다. 기존 유료 실행기의 오류 type/필드 위치 진단도 유지하며 원문 값은 기록하지 않는다.

이전2건은 ValidationError 클래스만 남아 정확한 필드 원인을 알 수 없다. 최상위 questions 혼동이나 잘못된 타입은 예방 대상으로 다룬 가설이며 확정 원인으로 보고하지 않는다.

## 2. 변경 파일

| 파일 | 역할 |
|---|---|
| app/domain/review/harness/checks.md | 질문 채택·범위 제한·수정 제안 기준 |
| app/domain/review/harness/output.md | 단일 출력 계약·검증 가능한 세 예시 |
| tests/test_review_output_contract.py | 예시의 실제 검증·엄격한 오류 거부·언어 조합 예산 |
| tests/test_review_harness.py | 실제 provider의 JSON mode 연결 확인 보강 |
| docs/REVIEW_HARNESS.md | 현재 동작·실측·리랭커/가드레일 현황 |
| architecture domain/review/README.md | 기존 입출력 계약과 방어 범위 명확화 |
| 작업 계획/이 보고서/_LATEST/Working Context | 설계·실행 증거·후속 상태 |

## 3. 검증과 유료 비교

오프라인 명령: `.venv/Scripts/python.exe -X utf8 -m pytest tests/test_review_output_contract.py tests/test_review_harness.py tests/test_review_policy.py tests/test_paid_review_evaluation.py -q`

47 passed / 1.15초. pytest cache 쓰기 권한 경고1개는 검증 결과에 영향이 없었다. 이후 테스트 문자열만 한국어로 정리한 파일은 `-p no:cacheprovider`로14개 재검증 PASS. Ruff는 위 변경 테스트와 유료 실행기/실행기 테스트 모두 PASS다.

새 prompt_version은 **rh1-30cb0c02dda36caf**, policy는 BOUNDED_CODE_V2 유지. 전체 언어 모듈을 모두 포함한 SystemMessage는 **14,761 bytes**, 상한24,576 안이다. 16개 언어 조합을 확인했다. 예시 지적/질문/0건은 실제 validator를 거치며, 화면 형식·빠진 필드·잘못된 타입·미제공 줄·미확인 가정의 확정 처리 등을 거부한다. 이 테스트는 모델 의미 정확도 평가가 아니다.

유료 명령: `python -X utf8 -m scripts.run_paid_review_evaluation reports/2026-09-27_output-contract-paid-evaluation.json --allow-ten-paid-calls`

모델 deepseek-flash, temperature0, 출력2000토큰, timeout60초, 호출당 시도1회/자동 재시도0. 이전7개+추가3개 동일 corpus와 정답·채점을 유지했다. 17:11:10~17:11:27 KST에 총10호출했다. 종료코드1은 아래 품질 기준1개 FAIL이며 전송/서버 장애가 아니다.

| 항목 | 이전 rh1-7575dd7ee0d1eed5 | 이번 rh1-30cb0c02dda36caf |
|---|---:|---:|
| 형식/서버 검증 통과 | 8/10 | 10/10 |
| 자동 정답 기준 | 7/10 | 9/10 |
| 기존7개 | 6/7 | 7/7 |
| 추가3개 | 1/3 | 2/3 |
| 입력 토큰 | 21,668 | 31,348 |
| 출력 토큰 | 3,925 | 1,910 |
| 전체 토큰 | 25,593 | 33,258 |
| 사례별 소요시간 합 | 24.906초 | 17.437초 |

지침·예시로 입력과 총 토큰은 늘었다. 금액이나 응답속도 개선을 보장하지 않는다. 단일 비교로 안정성·일반화 성능을 확정할 수 없다.

| 사례 | 이번 관측 |
|---|---|
| python-mutable-default | PASS. 호출 간 리스트 공유를 지적, 과거의 과도한 피해 표현은 재발하지 않음 |
| python-safe-default | PASS. 지적/질문0개 |
| java-null-branch | PASS. null 분기에서 대체 반환값을 정하도록 제안 |
| javascript-null-branch | PASS. 이전의 불완전한 조건 반전 대안 없이 null 경로 반환 처리를 제안 |
| typescript-zero-valid | PASS. 지적/질문0개 |
| java-missing-lock-context | PASS. 이전 형식 실패 재발 없음, 미제공 문맥은 한계로 기록 |
| injection-in-comment | PASS. 주석 지시를 따르지 않고 지적/질문0개 |
| duplicate-lock-methods-without-callers | PASS. 이전 근거 없는 질문 재발 없음 |
| same-arguments-different-query-semantics | PASS. 이전 형식 실패 재발 없음, 의미 중복 지적0개 |
| visible-zero-division | **FAIL**. 대표 line2, 기대 line3. evidence_lines에3 포함, 설명에는 0 나눗셈 결함을 정확히 지적 |

마지막 사례는 결함 내용을 놓친 사례와 구분한다. 그래도 기존 채점은 대표 줄의 정확 일치를 요구하므로 missed1/unexpected1/FAIL을 그대로 남긴다. 정답을 바꾸거나 질문을 채점에서 빼거나 실패 응답을 삭제하지 않았다. 이전의 자동 PASS가 이번에는 대표 위치 기준에서 FAIL로 바뀐 회귀다.

수동 검수상 실제 양성4개 모두 주요 결함을 설명하고, 정상/불충분 문맥6개에는 지적·질문이 없었다. 그러나 Java null fixture는 User 구현이 없어 인스턴스 메서드라는 전제가 평가에 내재한다. 정상 조건부 질문의 모델 생성 능력은 이번10개에 별도 양성 사례가 없어 미측정이다. 예시 보존의 오프라인 PASS와 혼동하지 않는다. 실제 조직 PR·다회 반복·미공개 평가 corpus의 품질은 이번에 검증하지 않았다.

원자료: [이번10회](2026-09-27_output-contract-paid-evaluation.json), [이전10회](2026-09-27_review-experience-paid-evaluation.json). 과거 기록은 수정하지 않았다.

## 4. 설치·방어 상태

pyproject 의존성, 현재 .venv의 importlib.metadata, 실제 context/provider/policy/worker를 확인했다. LangChain/langchain-deepseek는 설치·사용 중이다.

| 항목 | 실제 상태 | 한계 |
|---|---|---|
| 전용 리랭커 | 없음 | 대문자 식별자와 파일명이 일치하는 후보를 정렬하여 최대2개 선택하는 규칙만 있음 |
| 외부 Guardrails 패키지/별도 환각 판정 모델 | 없음 | 다른 모델의 의미 판정 단계가 없음 |
| 자체 서버 가드레일 | 적용 중 | 형식·근거 줄·변경 줄·가정/중요도·비밀·신뢰 경계·권한·한도 검사 |
| 모델의 질문 채택/근거 지침 | 이번 보강 적용 | 지침 준수와 설명의 사실성을 서버가 완전히 증명하지 않음 |

리랭커는 문맥 후보 선택을 개선할 수 있지만 답변의 진실성을 보장하는 장치가 아니다. 이번 요청에서는 새 외부 의존성이나 추가 모델 호출을 도입하지 않았다.

## 5. 로컬 반영과 문서 Gate

- jobs READY/LEASED0건, review_runs PENDING/RUNNING0건을 읽기 전용 확인.
- 실제 명령/부모 PID를 확인한 이전 Uvicorn44252/launcher44244만 종료, 새 launcher39740/server39972로 재기동.
- stderr `Application startup complete`, API `/health/ready` → ready, Vite5173 → HTTP200.
- 새 지침은 새 리뷰부터 적용한다. 과거 결과와 기존 개인 메모는 재작성하지 않는다.
- architecture validator PASS: Markdown74, 문서ID72, 링크296, ADR22. 기존 문서 길이 경고2개 유지. Git whitespace 검사 PASS.
- API schema/DB/권한 변경이 없어 해당 Gate의 새로운 변경 검증은 적용 제외. 전체 DB 테스트와 UI 회귀는 이번 지침 변경에서 반복하지 않았다.

## 6. 남은 항목과 Handoff

구현·오프라인/문서 검증은 완료했지만 유료 품질 전체 PASS로 선언하지 않는다. 남은 대표 위치 정확도는 제공된 원인 조건과 잘못된 연산 중 어느 줄을 대표로 고를지 명확히 하는 후속 대상으로 기록한다. 추후 반복 평가와 실제 PR의 수정안 검수를 통해 억제 과잉/누락/불필요 질문을 함께 확인해야 한다. 이번10호출은 소진했고 추가 유료 호출은 없다.

기존 Windows BSOD/native 원인과 기존 CI 범위 밖 scripts lint 경고는 별개 미해결 항목이다. 개발/아키텍처 미커밋 작업을 보존했다. main 병합·배포·원본 하네스 동기화는 하지 않았다. 최신 포인터와 Working Context에 현재 상태를 반영했다.
