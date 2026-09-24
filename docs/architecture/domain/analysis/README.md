# Analysis: 정적 분석 실행과 결과

> ID: `ANALYSIS` · 소유: `backend/app/domain/analysis` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 분석 접수·상태·결과 API를 변경할 때

## 책임

분석 접수, 불변 실행 Snapshot, 언어별 구조 추출, 규칙 평가, Finding 저장, 실행 상태/검사 범위를 소유한다. PR 동기화·GitHub 로그인·LLM 설명은 직접 수행하지 않는다.

```text
analysis/
├─ api.py                 AnalysisCommands·AnalysisQuery·공개 Snapshot
├─ router.py
├─ service.py             인가·멱등 접수·상태 조회
├─ repository.py          AnalysisRun/Result 저장
├─ models.py              ORM 전용
├─ dto.py                 내부 Command/Result
├─ contracts.py           AnalysisContext·Finding·RuleOutcome
├─ status.py              AnalysisStatus·CoverageStatus
├─ jobs/run_analysis.py   업무 handler
├─ pipeline.py            취득→파싱→규칙→결과 흐름
├─ detector/language.py
├─ analyzer/
│  ├─ base.py
│  ├─ python/{parser,extractor}.py
│  ├─ java/{parser,extractor}.py
│  ├─ javascript/{parser,extractor}.py
│  └─ typescript/{parser,extractor}.py
├─ rule/
│  ├─ base.py
│  ├─ registry.py
│  ├─ common/
│  ├─ python/
│  ├─ java/
│  ├─ javascript/
│  └─ typescript/
├─ exceptions.py
└─ schema/{request,response}.py
```

## 공개 계약

`request_analysis(actor, workspace_id, pr_id, expected_head_sha)`, `get_analysis(workspace_id, analysis_id)`, `list_findings(workspace_id, analysis_id)`를 공개한다. HTTP Response와 분리한 내부 DTO를 반환한다.

사용자가 화면에서 본 PR의 head SHA를 전달하면 서버 Snapshot과 일치하는지 확인한다. 메타데이터가 없으면 `PR_SYNC_REQUIRED`로 재동기화를 안내한다. 분석 접수에서 GitHub 전체 취득이나 LLM 호출을 기다리지 않는다.

## 접수·실행

인가 → 연결/PR Snapshot 검증 → 설정 버전 고정 → Analysis와 Job 원자적 기록 → commit → 202 응답 순서다. 동일 요청 키가 이미 있으면 기존 분석 ID를 반환한다. Worker는 실행 직전 권한/연결과 고정 Snapshot의 가용성을 다시 확인한다.

정적 분석 상태와 finding 수를 구분한다. 분석이 완료됐어도 오류 후보가 있을 수 있고, Finding 0개여도 미지원/누락 범위가 있을 수 있다. AI는 이 도메인의 상태를 변경하지 않는다.

## 세부 문서 선택

| 작업 | 추가 문서 |
|---|---|
| 상태·실행 키·결과 타입 | [CONTRACTS](CONTRACTS.md) |
| GitHub 소스 취득·Diff·한도 | [PIPELINE](PIPELINE.md) |
| 언어/Parser 추가 | [LANGUAGES](LANGUAGES.md) |
| Rule 추가·Severity | [RULE_ENGINE](RULE_ENGINE.md)와 해당 Rule 목록 |
| 재시도·복구·동시 실행 | [공통 Job](../../shared/jobs/README.md) |

## 금지와 테스트

Analyzer에서 DB commit·GitHub 댓글·LLM 호출을 하지 않는다. Rule에서 네트워크·현재 시각·환경변수에 의존하지 않는다. 원문 코드를 결과에 넣지 않는다. 다른 도메인도 Finding 모델을 shared로 옮기지 않는다.

혼합 언어 PR, no-supported-files, source unavailable, parser error, partial diff, 재배포 중단, 오래된 worker의 늦은 완료, 반복 재시도, 교차 테넌트 결과 조회를 검증한다.
