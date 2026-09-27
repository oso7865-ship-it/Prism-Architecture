# 작업 리포트: 문맥 수집 개선과 실제 리랭커 비교

> 작성일: 2026-09-27
> 작업 브랜치: backend dev / architecture main
> 커밋/PR: 미커밋·미푸시; 기준 backend 1f9f298 / architecture c9275e6
> 상태 기록 버전: 1
> 상태 확인 시각: 2026-09-27T18:29:53+09:00
> 구현 상태: 완료
> 구현 근거: BOUNDED_CODE_V3 문맥 수집, 선택적 로컬 모델/실패 복귀, 동일 후보 평가 코드와 ADR-REVIEW-007 working-tree
> 로컬 검증 상태: 완료
> 로컬 검증 대상: 이번 backend/architecture working-tree 및 기존 기능 회귀
> 로컬 검증 근거: Linux 277 tests/47.11초, Ruff·format·mypy, 문서 검사 PASS; 아래 증거 파일
> 병합 상태: 미수행
> 병합 대상: origin/main
> 병합 근거: 이번 요청에 Git 쓰기/병합 포함 안 됨
> 배포 상태: 미수행
> 배포 근거: 로컬 API 재시작만 수행
> 실제 연동 상태: 완료
> 실제 연동 근거: 로컬 ONNX 추론·장애 복귀와 DeepSeek 합성24회 호출 확인; 실제 PR의 V3 리뷰는 미수행
> 작업 범위: L
> 적용 스킬: terminal-ops, quality-gate, troubleshooting-report
> 적용 Gate: 구조·의존성, 비밀/신뢰 경계, 제한/실패 복귀, 코드/문서 검증
> 위험도: 구조 / 외부 실행 / 환경 변경 / 제한 유료 평가
> 위험 작업 여부: 예; 사용자 1~3단계 전체 위임 및 도구 승인 범위에서 수행

## 0. 작업 범위 확인

사용자는 문맥 수집 개선, 동일 후보의 규칙/리랭커 비교, 효과 확인 후 채택을 모두 지시했다. [사전 설계·채택 기준](../docs/work-plans/2026-09-27_context-reranking.md)을 먼저 작성했다. 제품 기본값은 규칙 선택이며 모델을 설치했다고 자동 활성화하지 않는다.

원문 영속 인덱스/벡터 DB, 외부 리랭커 API, 전체 호출 그래프, DB/API schema 변경, 프론트 재설계, Git 게시와 실제 배포는 제외했다. 기존 미커밋 기능·환경 비밀·사용자 결과는 보존했다. 실제 조직 코드를 평가에 전송하지 않았다.

## 1. 결과와 채택 결정

**문맥 수집 V3는 로컬 적용했고 리랭커는 기본 OFF를 유지한다.** 설치한 실험 모델의 품질 게이트는 FAIL이며 예외로 통과시키지 않았다. 기본 활성화 대신 검증된 규칙 선택을 사용한다. 이번 변경이 AI 리뷰의 전체 품질 문제를 해결했다는 뜻은 아니다.

| 지표 | 규칙 | 로컬 리랭커 |
|---|---:|---:|
| 필요한 근거가 후보에 있음 | 12/12 | 12/12 |
| 정답 근거가 있는 파일 자체를 선택 | 12/12 | 12/12 |
| 필요한 근거가 최종 입력에 있음 | 12/12 | 9/12 |
| DeepSeek 응답 검증 완료 | 6/12 | 7/12 |
| 기대 결과 자동 통과, 실패도 분모 포함 | 5/12 | 3/12 |
| 검증 거절(ValueError) | 6 | 5 |
| 검증된 응답의 예상 밖 지적/질문 | 1 | 2 |
| 검증된 응답의 기대 결함 누락 | 0 | 2 |
| 입력 토큰 | 40,156 | 40,808 |
| 출력 토큰 | 3,463 | 3,585 |

검증 거절 응답은 내용 점수를 산출할 수 없으며 '결함 누락0'으로 취급하지 않는다. 합계24회, 입력80,964·출력7,048토큰, 재시도0이다. 정확한 청구액은 산출하지 않았다. 작업 승인 범위24회를 소진했고 후속 유료 호출은0회다.

양쪽 모두 전체24개 선택 파일 중12개가 정답 근거 파일 이외의 파일이었다. 차이는 Java 정답 파일 안의 **구간 선택**에서 났다. 파일명을 맞혔다고 근거를 포함한 것은 아니다. 최종 입력 최대치는 규칙1,220byte·리랭커2,068byte로 이번 근거 누락은24KiB 예산 부족으로 발생하지 않았다.

측정 전 기준은 최종 근거 포함 사례2개 이상 개선, 기존 성공 손실0, warm 추가 추론 p95≤2초, 안전성 PASS, 응답 실패/불필요 질문/기대 결함 누락의 비악화였다. 근거 포함12→9, Java3사례 회귀로 명백히 미달했다. 이번 corpus에서 규칙이 이미12/12이므로 개선2개 조건을 만족할 여지도 없었다. 이 평가는 모델의 보편적 무용성을 증명하지 않으며 이 구성의 기본 도입을 정당화하지 못한다.

## 2. 구현과 변경 파일

| 위치 | 변경 내용 |
|---|---|
| app/domain/review/context.py | 고정 HEAD·일반 파일·200KB·비밀/경로 검사 유지 |
| retrieval.py / syntax_entry.py / context_selection.py | 구문 메서드/함수·import·식별자·경로 후보12파일/24구간, 최종 관련2파일/전체24KiB |
| reranker.py / worker.py / app/main.py / settings.py | loopback 모델 어댑터, 기본 OFF 주입,2초·응답8KiB 제한, 장애 시 원래 규칙 순서 |
| tools/reranker / compose.reranker.yaml | 공식 ONNX 고정 revision/hash, 의존성 lock, non-root/read-only CPU 컨테이너 |
| policy.py | 입력 정책 BOUNDED_CODE_V3; prompt rh1-30cb0c02dda36caf 유지 |
| evals/context-retrieval / scripts/evaluate_context_retrieval.py | 고정12사례, 동일 후보 digest, 최대24 유료 호출·재시도0·기존 출력 보호 |
| tests/test_context_retrieval.py / test_context_evaluation.py | 문맥·정보보호·장애·대응 모델·평가 비용 경계29개 |
| architecture ADR-REVIEW-007 / Review / Privacy / maps | 계약·대체 관계·실제 방어 한계 |
| README / docs/CONTEXT_RETRIEVAL.md / 상태 문서 | 실행 방법·채택 결정·남은 품질 과제 |

변경 줄은 제거하지 않으며 후보 구간은 최대80줄이다. 짧은 메서드/함수와 긴 함수의 선언부·변경 주변을 선택한다. 관련 구현이 파일 뒤쪽에 있는12사례를 확인했다. 전체 호출 그래프·Java static import·Python 상대 import·alias·동적 호출을 완전히 해석하지 않는다.

서버 요청은 기존 권한/세대/취소/lease·원문 비저장·DeepSeek1호출 제한을 유지한다. 로컬 리랭커 실패는 리뷰 실패로 올리지 않고 metadata에 사유를 남긴다. 문맥 전체20초 제한에 걸리면 안전한 원래 diff로 돌아간다.

## 3. 실제 평가 증거와 해석

- [선택 비교](2026-09-27_context-selection-evaluation-2.json): 로컬 추론12회, 유료0. 규칙12/12·리랭커9/12, 작은4후보의 관측 p95 94ms.
- [리뷰 비교](2026-09-27_context-review-comparison.json): 고정12사례×2방식24회, 동일 후보 digest 확인. 작은4후보의 관측 p95 78ms. 모든 유료 응답에 토큰 사용량 관측.
- [실행·경계 확인](2026-09-27_reranker-runtime-check.json): 긴 후보24개/각5,900byte는24개 모두 token 절단, 직접 요청2.047초·제한 클라이언트1.922초. 잘못된 개수/문서400, 초과 body413. 중단 후 규칙 복귀 RERANK_TIMEOUT 약2.015초, 재시도0.
- [초기 실패 기록](2026-09-27_context-selection-evaluation.json): 호스트 연결 실패에서 중단한 비교. 유료0이며 성공 데이터와 섞지 않는다.

코퍼스는 Python/Java/JS/TS 각3개(방어된 null, 실제 nullable 반환, 0 또는 음수 길이)이며 관련 구현을100줄 뒤에 뒀다. 원본 SHA256 `59eff6055cefa472c171ff30b7c3bfe361bf0bd550ba987ef8a8d3d52bb24e42`는 결과 관측 후 바꾸지 않았다. 모델 질의에는 기대 결함·정답 줄·개인 피드백이 없다. 동일 후보4개/최종2파일 비교이므로24후보 일반 부하나 대규모 저장소 정확도 결과가 아니다.

수동 검수에서 Java는 필요한 구현이 빠지며 정상 방어에도 null 여부 질문이 생겼고, nullable/0 반환의 실제 결함도 조건부 질문에 머물렀다. TypeScript 방어 사례에서는 의도된 예외 전파를 경고로 처리했다. Python 방어 사례의 속성 검사는 입력 계약이 fixture에 충분히 명시되지 않아 오탐 판정에 논쟁 여지가 있다. 자동5/12 대3/12를 일반 정확도로 제시하지 않는다. 단일 실행이며 표본·확률 변동과11개 검증 거절 때문에 인과적 품질 향상 주장도 하지 않는다.

선택 모델은 영어 검색용 [cross-encoder/ms-marco-MiniLM-L6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2), revision `233902d25c440f23af6f7d6e94d2946bac0bee0a`다. 학습 용도와 코드 검토 적합성은 다르다. ONNX·tokenizer 약92MB를 고정 hash로 검증했고 원격 Python 코드는 실행하지 않았다. idle memory395.5MiB/768MiB를 관측했으며 peak 측정값은 아니다. 컨테이너는 평가 후 중지했고 이미지와 재현 설정은 보존했다.

## 4. 검증·Checklist

| 확인 | 결과 | 근거 |
|---|---|---|
| 전체 백엔드 회귀 | PASS | 임시 Linux DB/테스트 컨테이너 `python -m pytest -q -p no:cacheprovider`,277 passed/47.11초 |
| 새 문맥/모델/평가 경계 | PASS | Windows 비DB29 passed/5.79초; Linux 전체에 포함 |
| 코드 검사 | PASS | Ruff check/format: app/tests/migrations/이번 scripts/tools/evals, mypy app117 source files |
| 소스/프롬프트 경계 | PASS | 비밀/제외 파일 미전송, 원본 변경 줄 보존, 관련 파일만의 대표 근거 거절, 구문 실행 없음 |
| 실패 복귀 | PASS | timeout/503/비정상·NaN·bool·다른 revision·초과 streaming 응답/실제 모델 중단 |
| 비용·평가 공정성 | PASS | 최대24·재시도0·파일 덮어쓰기 금지; 향후 후보 불일치 확인은 유료 전송 이전 |
| 모델 기본 활성화 | FAIL → OFF 유지 | Java3건 근거 누락과 품질 개선 증거 부족 |
| 문서 무결성 | PASS |75문서·302링크·23 ADR; 기존 길이 WARN2개 유지 |
| 작업 기록 형식 | PASS | 계획16개/Report20개 검사; 직전 Report의 기존 요약 헤더를 명시 필드로 보강 |
| 실제 제품 PR 품질/UI | 미수행 | 합성 외 새 실제 PR 호출이나 UI 변경 없음 |

Windows에서 DB 전체 회귀를 반복하지 않고 Linux를 사용했다. 기존 BSOD/native 원인 해결을 주장하지 않는다. `test_review_harness.py`의 기존 혼합 줄끝만 포맷 정규화했고 의미 변경은 없다. API 재시작 직전 READY/LEASED Job0, PENDING/RUNNING review0을 확인했다. 18:28 API launcher25956으로 재시작, 18:29 `/health/ready`200·Vite200·AI ON·reranker OFF 확인. 로컬 PostgreSQL 데이터는 그대로이며 임시 테스트 DB 컨테이너/네트워크만 정리했다.

## 5. 발견된 문제와 트러블슈팅

### 모델은 healthy지만 호스트에서 연결되지 않음

- 사건 상태: 해결 검증 완료. 원인 상태: 해당 Docker Desktop 구성에서 포트 미공개 확인.
- 어디서: compose.reranker.yaml의 최초 internal network 설정,2026-09-27 로컬 Docker Desktop. 상세 최초 발견 시각은 초기 실패 JSON의 started_at 참조.
- 무엇: 컨테이너 내부 health는 정상이지만 호스트8091 추론은2초 timeout. 초기 모델 비교는 첫 사례에서 중단, 유료0회.
- 어떻게: 내부 네트워크에만 연결한 구성에서 inspect의8091 HostPort 매핑이 비어 있었고 실제 호스트 요청이 실패했다.
- 왜: 관측한 Docker Desktop의 internal network/호스트 공개 조합에서 요청 경로를 만들지 못했다. 모든 Docker 버전의 일반 결함으로 단정하지 않는다.
- 해결: 기본 bridge와127.0.0.1 포트 바인딩으로 변경·재기동 후 health200, 실제12+12회 비교와 최대 입력 추론 성공. 외부 리랭커 API는 사용하지 않지만 물리적인 egress 차단은 보장하지 않는 구성으로 한계를 문서화했다.
- 후속: 다른 호스트에서 실행 시 host health와 실제 scoring 모두 확인. 공개 배포용 namespace/네트워크 통제는 별도 설계·검증. 담당 미정, 해당 배포 검토 때 실행.

### 다중 파일 리뷰11회가 검증에서 거절됨

- 사건 상태: 미해결 종료. 원인 상태: 세부 원인 미확인.
- 어디서: 새 평가기 run의 provider 응답 이후 validate_result,24회 비교 JSON. 토큰 필드가 모두 기록되어 응답 취득 이후 ValueError임을 확인했다.
- 무엇: 규칙6회·리랭커5회가 거절됐고 실제 원문을 저장하지 않아 잘못된 근거 줄/가정/기타 조건 중 무엇인지 구분할 수 없다. JSON 형식 오류11건으로 단정하지 않는다.
- 어떻게: 다중 파일 합성 입력을 기존 prompt/strict validator로 검토했다. 한 사례·방식당1회만 호출했으며 결과 오류 클래스만 저장하는 새 평가기의 진단 한계가 드러났다.
- 왜: 응답 계약 검증 거절은 확인했지만 구체적 필드 원인은 미확인이다. 파일 간 근거 참조 혼동은 가능한 가설일 뿐 확정 원인이 아니다.
- 해결: 실제 모델 품질은 해결하지 못했다. 평가기에 provider/validation 단계와 허용 목록의 오류코드만 기록하도록 보완하고 비밀 예외 문자열 미기록 회귀를 추가했다. 기존 guardrail을 완화하거나 결과를 소급 수정하지 않았다. 추가 유료0회.
- 후속: 다음 승인된 평가에서 코드별 실패를 관측하고 원인별 회귀·지침 보완 후 동일 corpus를 비교한다. 담당 미정, 별도 평가 승인 시 실행. 성공 기준은 검증 완료율 회복과 의미 오탐/누락 비악화이며 진단 기능 추가 자체를 해결로 보지 않는다.

## 6. 남은 항목과 다음 작업

1. 다중 파일 응답 검증 거절11회 원인 특정 및 의미 품질 개선. 이전 단일 파일10사례의 형식10/10을 이번 입력으로 일반화하지 않는다.
2. 실제 PR·더 어려운 후보·언어별 호출 계약이 명확한 holdout으로 문맥 품질을 평가한다. 이번12사례를 본 뒤 조정한 모델로 같은 corpus 점수를 올리는 것을 독립 검증으로 취급하지 않는다.
3. 리랭커 재도입은 다른 모델/구성이 사전 기준을 통과할 때만 검토한다. 현재 설치 모델은 중지 상태, 서비스 기본 OFF다. 추가 결제 없이 재현 가능한 로컬 선택 비교는 제공했다.
4. Windows native 근본 원인, 공개 다사용자/HTTPS/Webhook 검증, 운영 결정은 기존 열린 항목이다. 사용자 목표는 배포 전 단계다.

## 7. 기록과 공식 반영

설계 체크리스트·README·Review 소유 문서·ADR/맵과 현재 상태를 동기화했다. 이전 출력 계약 보고서는 당시 증거로 유지하고 최신 포인터를 이 보고서로 전환한다. 이전 Working Context 요약은 history로 그대로 이관한다. 구현은 backend dev와 architecture main working-tree에만 있으며 커밋·push·main 병합·배포·원본 HARNESS 동기화는 수행하지 않았다. architecture.json은 마지막 게시 SHA를 유지한다.
