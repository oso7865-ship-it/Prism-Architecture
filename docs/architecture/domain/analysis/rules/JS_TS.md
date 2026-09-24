# JavaScript 계열 6개 + TypeScript 전용 6개

> ID: `RULES-JS-TS` · 소유: `backend/app/domain/analysis/rule/javascript|typescript` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: JavaScript·TypeScript Rule을 구현·변경할 때

JavaScript 계열 규칙은 해당 구문이 같은 TypeScript에도 적용할 수 있다. 별도 ID로 복제하여 같은 Finding을 두 번 만들지 않는다. JSX/TSX grammar와 줄 위치를 테스트한다.

## JavaScript 계열

| ID | 검출 조건 | 기본 Severity / Confidence | 예외/한계 |
|---|---|---|---|
| JS-001 | var 선언 | INFO / HIGH | let/const 선호 정책 |
| JS-002 | == 또는 != | WARNING / HIGH | null 비교는 기본 예외로 허용 |
| JS-003 | debugger statement | WARNING / HIGH | 개발 잔여 코드 후보 |
| JS-004 | 빈 catch | WARNING / HIGH | 의도적 무시 가능 |
| JS-005 | direct eval 형태 | WARNING / MEDIUM | 실제 취약성/taint 미검증 |
| JS-006 | Function constructor 동적 코드 생성 | WARNING / MEDIUM | 동명 사용자 정의 타입/alias 해석 필요 |

## TypeScript 전용

| ID | 검출 조건 | 기본 Severity / Confidence | 예외/한계 |
|---|---|---|---|
| TS-001 | 명시적 any 타입 | WARNING / HIGH | 외부 JSON 경계에서는 의도적일 수 있음 |
| TS-002 | @ts-ignore comment directive | WARNING / HIGH | 합리적 우회인지 사람이 확인 |
| TS-003 | @ts-nocheck comment directive | WARNING / HIGH | 파일 검사 비활성화 사실 |
| TS-004 | non-null assertion `!` | WARNING / MEDIUM | null 가능성 자체는 증명하지 않음 |
| TS-005 | `as unknown as` / `as any as` 이중 assertion | WARNING / MEDIUM | 의미상 안전성은 타입 분석 필요 |
| TS-006 | namespace 선언 | INFO / HIGH | 기본 OFF; ESM-only 정책을 설정한 프로젝트만 |

TS-004는 논리 부정과 구별하고 definite assignment assertion의 별도 구문을 혼동하지 않는다. TS-002/003은 문자열 리터럴 안의 같은 텍스트가 아니라 실제 directive comment를 검사한다. TypeScript가 추론한 implicit any는 타입 검사기를 실행하지 않으므로 검출 범위가 아니다.

필수 fixture: `x == null` 기본 예외, 문자열 속 debugger/directive, shadowed eval/Function, TS의 `!` 여러 의미, JSX/TSX, any를 의도적으로 사용하는 API boundary, 선언 파일 제외. [언어 문서](../LANGUAGES.md)의 `.vue` 미지원 범위를 유지한다.
