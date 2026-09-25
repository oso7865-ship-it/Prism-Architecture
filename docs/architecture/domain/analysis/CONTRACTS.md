# 분석 실행·결과 계약

> ID: `ANALYSIS-CONTRACTS` · 소유: `backend/app/domain/analysis/contracts.py` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 상태·Finding·중간 모델·멱등 실행 키를 수정할 때

## 불변 Snapshot과 실행 키

`AnalysisRun`은 workspace_id, repository_connection_id, pr_id, requested_by 또는 system actor, base_sha, head_sha, optional merge_base_sha, rule_set_version, config_version, effective_config_digest, analyzer_build_digest, scope, generation을 고정한다. generation은 사용자가 명시적으로 재분석할 때만 증가한다.

기본 실행 키는 위 필드 중 대상/버전/범위/generation을 정규화하여 SHA256으로 계산한다. actor는 감사 정보이지 같은 snapshot 자동 분석을 중복 생성할 이유가 아니다. UNIQUE execution_key 충돌 시 기존 run을 반환한다. actor별 HTTP idempotency key를 쓸 경우 별도 요청→run 매핑을 둔다.

동일 Job의 내부 재시도는 새 AnalysisRun을 만들지 않는다. 같은 commit을 새 규칙/설정으로 평가하거나 명시적 재분석한 결과는 새 run이다. 과거 성공 결과를 덮어쓰지 않는다.

## 상태 계약

| AnalysisStatus | 의미 |
|---|---|
| PENDING | 영속 접수 완료, 실행 대기/재시도 대기 |
| RUNNING | 현재 유효 lease를 가진 worker가 처리 중 |
| COMPLETED | 결과와 검사 범위를 정상 저장함 |
| FAILED | 재시도 불가 또는 횟수 소진 |
| CANCELED | 사용자 취소/접근 철회/진행 불필요 등으로 종료 |

정상 전이: `PENDING → RUNNING → COMPLETED/FAILED/CANCELED`. 재시도 가능한 실패와 lease 만료는 `RUNNING → PENDING`을 허용하며 attempt 이력을 남긴다. terminal 결과를 늦게 도착한 이전 attempt가 다시 변경할 수 없다.

별도 `CoverageStatus = FULL_SCOPE / PARTIAL / NONE`. FULL_SCOPE는 **선택한 지원 파일·활성 규칙의 범위**를 검사했다는 뜻이며 저장소 전체·타입 안전성·보안 검증 완료가 아니다. no-supported-files는 COMPLETED + NONE + 명확한 사유를 반환한다.

각 파일에는 INCLUDED / EXCLUDED / SOURCE_UNAVAILABLE / PARSE_ERROR / LIMIT_EXCEEDED와 사유를 기록한다. 각 Rule 평가에는 EVALUATED / NOT_APPLICABLE / NOT_EVALUATED를 둔다. 필요한 구조 정보가 없는데 조용히 '0건'으로 처리하지 않는다.

## 메모리 내부 계약

```python
@dataclass(frozen=True)
class FileContext:
    path: str
    language: Language
    source_sha: str
    source_bytes: bytes  # 임시 메모리 전용. DB/Job/로그 직렬화 금지.
    functions: tuple[FunctionSymbol, ...]
    imports: tuple[ImportSymbol, ...]
    capabilities: frozenset[str]
    changed_ranges: tuple[LineRange, ...]
```

실제 구현에는 parser 진단·language-native tree handle을 추가할 수 있다. 공통 Rule은 capabilities를 확인하고, 언어 전용 Rule은 해당 언어 전용 context를 사용한다. 모든 언어 의미를 하나의 AST 모양으로 억지로 평탄화하지 않는다.

FunctionSymbol은 이름·1-based 시작/끝 줄·parameters·nesting metrics를 갖는다. ImportSymbol은 원문 모듈명과 `resolved_target: str | None`을 구분한다. CallSymbol의 메서드 이름만으로 호출 대상 타입을 확정하지 않는다.

## 영속 Finding

`id, analysis_id, rule_id, rule_version, category, severity, confidence, language, file_path, start_line, end_line, side, scope_location, message_code, sanitized_message, fingerprint`를 저장한다. Source snippet·AST·비밀 문자열·PR Diff는 저장하지 않는다.

줄은 1-based, end_line은 inclusive로 고정한다. side는 HEAD/BASE/FILE, scope_location은 CHANGED/CONTEXT/FILE이다. 제거된 파일이나 파일 경로 규칙처럼 줄을 특정할 수 없으면 nullable로 둔다. 임의로 0번 줄을 만들지 않는다.

fingerprint는 rule_id + normalized path + safe range/structural key로 만든다. 같은 run 내 dedupe 용도이며 서로 다른 commit에서 완벽히 동일 이슈를 추적하는 ID가 아니다. Secret 값을 fingerprint 입력으로 저장하거나 사용자에게 노출하지 않는다.

Severity = INFO/WARNING/ERROR/CRITICAL, Category와 confidence는 [Rule Engine](RULE_ENGINE.md)이 소유한다. UI는 이 세 축을 혼동하지 않는다.

Pipeline이 허용한 미지원 텍스트의 Secret 등 언어 중립 Finding은 language=NULL로 저장한다. 이를 네 언어 Parser 지원 확대로 해석하지 않는다. 파일별 Finding 상한에 도달하면 analysis_file_results.finding_limit_reached를 표시하고 coverage를 PARTIAL로 계산한다.

## 통계와 실패

발견 수뿐 아니라 검사 대상 수·제외 수·Parser 실패 수·미평가 Rule 수를 반환한다. 분석 실패 메시지는 공개 code와 trace_id만 포함한다. GitHub 404가 비공개 권한 부족일 수 있으므로 '존재하지 않음'을 단정하지 않는다.

필수 테스트는 상태 전이, execution_key 구성 필드 변경, 중복 동시 insert, run/attempt 분리, 1-based 위치, partial/none 표시, secret-free serialization이다.

물리 저장은 [분석 스키마](../../contracts/schema/RESULTS.md)를 따른다. config_version은 물리 컬럼 config_version_id로 불변 설정 행을 참조한다. 연결 세대도 execution_key에 포함하고, 기본 generation=0 및 명시적 재분석 증가를 Workspace 잠금 아래 처리한다. 파일별 RuleOutcome은 analysis_file_results의 제한 JSON 배열로 기록한다.
