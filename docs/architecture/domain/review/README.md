# Review: LangChain 기반 선택적 설명

> ID: `REVIEW` · 소유: `backend/app/domain/review` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: LangChain·Provider·Prompt·AI 결과를 변경할 때

## 소유권과 구조

정적 Finding을 설명하고 사람이 판단할 수 있는 개선 방향을 제시한다. AI는 규칙 엔진의 판정자나 자동 수정 실행기가 아니다.

```text
review/
├─ api.py
├─ router.py                 설명 요청/조회
├─ service.py                동의·예산·중복 검사 및 Job 접수
├─ repository.py
├─ models.py                 ReviewRun·FindingExplanation
├─ provider.py               LangChain 모델 생성; 현재 review 전용
├─ policy.py                 전송 허용·예산·대상 선택
├─ jobs/explain_findings.py
├─ chain/explain.py          Prompt → model → 구조 검증
├─ prompt/explain.py         업무 Prompt
├─ output.py                 FindingExplanationOutput
├─ dto.py
├─ exceptions.py
└─ schema/{request,response}.py
```

현재 소비 도메인이 review뿐이므로 provider factory도 여기 둔다. 다수 Chain이 쓴다는 이유로 shared로 이동하지 않는다.

LLM Provider는 사용자 선택에 따라 **DeepSeek**를 사용한다. 세부 모델과 API 비용 상한은 아직 미정이며, 설정과 검증을 마치기 전에는 실제 호출하지 않는다.

## 실행 정책

AI 기본 상태는 `OFF`. OWNER가 저장소 단위로 외부 전송 Provider와 범위를 승인한 뒤 멤버가 명시적으로 요청한다. MVP는 정적 분석 완료 후 별도의 `POST .../analyses/{id}/reviews`로 요청하며 자동 AI 실행은 하지 않는다. analysis → review 의존성을 만들지 않는다.

`ReviewRun.status = PENDING / RUNNING / COMPLETED / FAILED / CANCELED`. 분석 자체의 상태와 완전히 분리한다. 외부 요청 직전 현재 멤버십·저장소 동의·예산을 재확인한다. 동의 철회로 이미 외부에 전송된 요청을 소급 취소할 수는 없다는 한계를 표시한다.

## LLM 입력/출력

MVP 전송 모드는 `FINDINGS_ONLY`다. 원문 코드·Diff·PR 본문·사람 리뷰·실제 파일 경로·조직명·개인정보는 보내지 않는다. rule_id, 정제된 규칙 설명, 언어, Severity, 검증된 비민감 구조 수치와 익명 Finding ID만 전송한다. Secret Finding은 원문/일부분도 보내지 않고 별도 고정 보안 안내로 대체한다.

코드 문맥이 없으므로 답변의 구체성에는 한계가 있다. 결과 화면에 '일반 개선 설명이며 코드 실행/타입 검증 결과가 아님'을 표시한다. 최소 코드 조각 전송은 별도 동의/반출 통제 후 확장 후보로만 둔다. 마스킹만으로 기업 코드 기밀 문제가 해결됐다고 주장하지 않는다.

출력 모델은 `{finding_id, explanation, suggestion_text, limitations}`이다. 입력에 없던 finding_id·unknown field·과도한 길이는 거부한다. Severity/Rule 변경 필드는 받지 않는다. Prompt는 정적 서버 템플릿으로만 구성한다. LLM에게 실행 도구·DB·GitHub 쓰기 권한을 주지 않는다.

LangChain의 모델/구조화 출력 기능을 사용하되 선택 Provider의 지원 여부를 테스트한다. JSON처럼 보인다는 이유만으로 유효한 업무 결과로 저장하지 않는다. [S-LC-MODEL](../../reference/SOURCES.md#s-lc-model), [S-LC-STRUCTURED](../../reference/SOURCES.md#s-lc-structured)

## 비용과 보관 — 설계 기본값

한 요청당 최대 Finding 10개, 출력 2,000 token 상한, 모델 호출 30초 timeout을 초기값으로 제안한다. Provider tokenizer/limit와의 호환성은 구현 시 검증한다. 재시도 최대 총 2회, Provider 자체 재시도는 끄거나 같은 예산에 포함한다. 429/일시 장애만 재시도하고 잘못된 출력은 1회 보정 범위 안에서 제한한다. 전체 호출 횟수는 항상 총 2회 이하다.

실제 API 호출은 Provider 선택·예산 상한 설정 전 차단한다. `review_key = analysis_id + prompt_version + provider/model + policy_version`으로 중복을 제어한다. timeout 후 실제 외부 과금이 발생했는지 알 수 없는 경우가 있으므로 정확히 한 번 과금을 보장하지 않는다.

MVP의 설명 대상은 서버가 Secret을 제외하고 Severity 내림차순·fingerprint 오름차순으로 최대 10개를 고정한다. 요청자가 임의 부분집합을 지정하지 않으며 선택 방식 변경 시 prompt_version을 올린다. 비용 예약·실제 호출 횟수·과금 미확인 상태 및 결과 컬럼은 [분석·AI 스키마](../../contracts/schema/RESULTS.md)를 따른다. Workspace 잠금 아래 예산 검사와 예약을 처리하고 실제 외부 호출 전에 현재 권한·동의를 다시 확인한다.

DB에는 검증·마스킹된 설명과 실행 metadata만 저장한다. Prompt/응답 원문 trace와 외부 tracing은 기본 OFF다. 예시 코드 생성은 MVP 출력에서 제외하고 텍스트 개선 방향만 제공한다.

## 검증

AI OFF에서 외부 호출 0회, Secret 전송 금지, 입력 ID 밖 결과 거부, timeout/429/출력 오류, 결과 속 악성 HTML, 중복 요청, 예산 초과, 사용자 권한 철회, AI 실패 후 정적 Finding 유지가 필수다.
