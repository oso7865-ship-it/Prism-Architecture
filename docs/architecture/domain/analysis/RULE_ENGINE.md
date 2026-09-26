# Rule Engine: 관찰과 정책 판단

> ID: `RULE-ENGINE` · 소유: `backend/app/domain/analysis/rule` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: Rule 계약·등록·Severity·규칙 버전을 변경할 때

## 책임

Rule은 이미 취득한 파일/구조와 불변 설정만 받아 `RuleOutcome`을 반환하는 결정론적 평가 단위다. 입력 코드 실행, 네트워크, DB, LLM은 금지한다. 분석한 구문 사실과 그 구문을 금지한 프로젝트 정책을 구분한다.

## 계약

```python
class AnalysisRule(Protocol):
    rule_id: str
    version: str
    required_capabilities: frozenset[str]

    def supports(self, language: Language) -> bool: ...
    def evaluate(self, context: FileContext,
                 config: RuleConfig) -> RuleOutcome: ...
```

RuleOutcome에는 status, findings, reason_code를 둔다. capability가 없으면 NOT_EVALUATED다. `supports=True`라고 모든 언어에서 평가 가능하다고 간주하지 않는다. Rule registry는 서버 배포물에 명시 등록하며 사용자 저장소의 플러그인을 동적 import하지 않는다.

공통 Rule은 언어별 extractor가 제공한 공통 구조를 사용한다. 언어 전용 Rule은 native context를 사용할 수 있지만 언어 외 영역으로 침범하지 않는다. 같은 구문에 포괄 Rule과 구체 Rule이 중복되면 구체 Rule 우선으로 dedupe한다.

## 결과 축

| 축 | 값 | 뜻 |
|---|---|---|
| Severity | INFO / WARNING / ERROR / CRITICAL | 프로젝트 정책상 중요도 |
| Category | ARCHITECTURE / SECURITY / RELIABILITY / MAINTAINABILITY / STYLE / PERFORMANCE | 문제 종류 |
| Confidence | HIGH / MEDIUM / LOW | 이 Finding 근거의 확실성 |

CRITICAL은 실행 가능한 공격이나 유효한 비밀키를 입증했다는 의미가 아니다. Secret pattern은 외부에 토큰을 보내 유효성을 시험하지 않는다. ERROR라고 배포를 자동 차단하지도 않는다. MVP는 advisory report이며 CI merge gate는 확장 후보다.

## 규칙 버전과 사용자 설정

rule_id는 안정된 식별자로 유지한다. 검출 의미가 바뀌면 rule_version과 rule_set_version을 올린다. threshold/enable/severity/layer mapping 변경은 Repository RuleConfigVersion을 새로 만든다. 실행 시작 때 effective config digest를 고정한다.

아키텍처 Rule은 고객 프로젝트의 계층/경로 매핑을 사용한다. 분석 플랫폼 자체의 `domain/shared` 규칙을 고객 저장소에 강요하지 않는다. 동일 플랫폼 코드에 대해서는 별도 CI import-boundary test로 구조를 강제한다.

초기 Rule 제안은 공통 10 + Java 8 + Python 8 + JavaScript 계열 6 + TypeScript 전용 6 = **38개 정의**다. 구현 완료 개수가 아니며 각 Rule의 fixture/정확도 검증 후 활성화한다. JavaScript 계열 중 구문이 공통인 Rule은 TypeScript에도 재사용한다.

## 초기 목록의 읽기 범위

[공통](rules/COMMON.md), [Java](rules/JAVA.md), [Python](rules/PYTHON.md), [JavaScript/TypeScript](rules/JS_TS.md) 중 작업 대상만 읽는다. 모든 Rule 목록을 분석 API 변경 때 읽을 필요는 없다.

## 제외 범위

전체 저장소 순환 의존성, Java/TS 전역 타입 추론, interprocedural 데이터 흐름, 전체 Git 이력 Secret 탐색, semantic 중복 코드, 안전한 자동 수정, 전체 security audit는 MVP에서 제외한다. 단순 호출 이름만으로 가능한 척 구현하지 않는다.

## 활성화 게이트

각 Rule은 정상 2개 이상·위반 2개 이상·유사 정상/오탐 방지 1개 이상 fixture, 기대 위치/Severity/사유, capability 부족 케이스를 요구한다. 수치 제한 테스트·출력 비밀정보 미포함 검사도 공통 적용한다. LOW confidence는 기본 UI에서 참고 항목으로만 분리한다.

## 초기 구현 상태 (2026-09-26)

제안 규칙 전체가 활성화된 상태는 아니다. static-1.0.0은 fixture 검증을 마친 23개 구문·형식 규칙만 활성화한다. 정확한 목록·실제 검증·미구현 범위는 [구현 현황](../../runtime/IMPLEMENTATION.md)을 따른다.

## 규칙 확장 (static-1.1.0)

기존23개에 COM-003(조건/반복 깊이>4), PY-004/005(내장 eval/exec 직접 호출), PY-008(포괄 except), JS-005/006(eval/Function 동적 코드 생성)을 추가한29개다. 이름 바인딩·동적 변경을 확신할 수 없으면 해당 규칙 NOT_EVALUATED/BINDING_UNRESOLVED, 파일 범위 PARTIAL이다. 파일 안의 다른 이름 사용까지 보수적으로 제외하며 전역 타입/심볼 해석은 하지 않는다. 런타임 monkey patch와 외부 주입은 검증하지 않는다. PY-003과 PY-008 중복은 제외한다. 함수 경계에서 깊이를 초기화하며 else-if/elif는 같은 깊이로 취급한다. 새6규칙은 version1.0.0이고 기존 규칙 버전은 유지한다. 나머지9개 후보는 비활성이다.
