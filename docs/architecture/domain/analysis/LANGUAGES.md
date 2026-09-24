# 지원 언어와 Parser 경계

> ID: `LANGUAGES` · 소유: `backend/app/domain/analysis/analyzer` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 지원 확장자·grammar·구조 추출을 변경할 때

## 지원 매핑

| 언어 | 확장자 | 기본 Parser |
|---|---|---|
| Java | .java | tree-sitter-java |
| JavaScript | .js, .jsx, .mjs, .cjs | tree-sitter-javascript |
| TypeScript | .ts, .tsx, .mts, .cts | tree-sitter-typescript; TSX 분리 |
| Python | .py | tree-sitter-python |

Go 및 다른 언어는 정적 Rule 평가 대상에서 제외한다. `.d.ts` 선언 파일과 `.pyi`는 초기 제외 대상으로 사유를 남긴다. **Vue의 `.vue` 단일 파일 컴포넌트는 JS/TS 파일과 같지 않다.** script 블록 추출·위치 복원을 구현하기 전에는 미지원으로 표시한다. 이 프로젝트 프론트가 Vue여도 그 파일을 자동 분석한다고 약속하지 않는다.

확장자는 후보 판별에만 쓰고 실제 파싱 진단을 확인한다. 같은 PR 안의 언어를 각각 분석한다. 언어별 grammar와 Python binding 버전은 호환성 테스트 후 함께 고정한다.

## Parser와 Analyzer

Tree-sitter는 구문 트리를 구축하는 도구다. Java 타입 해석, TypeScript type checker, Python 실행 의미를 자동 제공하는 도구로 취급하지 않는다. Python binding으로 각 grammar를 사용한다. [S-TS-INTRO](../../reference/SOURCES.md#s-ts-intro), [S-TS-PY](../../reference/SOURCES.md#s-ts-py)

`parser.py`는 native syntax tree와 진단을 만든다. `extractor.py`는 함수/클래스/import/호출 형태와 capability를 추출한다. Rule은 그 다음 판단을 수행한다. Parser가 직접 Severity나 HTTP 응답을 만들지 않는다.

| capability | 의미 |
|---|---|
| functions | 함수/메서드 범위·인수 개수 추출 가능 |
| nesting | 정의한 조건/반복 중첩 지표 계산 가능 |
| imports | import 선언 추출 가능 |
| resolved_imports | 해당 파일 범위에서 대상 모듈을 확실히 해석 가능 |
| call_syntax | 호출 형태 확인 가능, 타입 확정은 별개 |

각 extractor가 제공하지 못하는 capability를 거짓으로 선언하지 않는다. 공통 Rule도 capability를 요구해야 한다. native tree가 필요한 언어 전용 Rule은 해당 언어 context를 사용한다.

## 정확도와 위치

Tree-sitter의 zero-based 위치를 API의 1-based 줄로 한 번만 변환한다. Unicode·CRLF·탭·멀티라인 표현·decorator/annotation·JSX/TSX·중첩 함수 fixture를 둔다. Parser error가 있는 부분을 제외할 때 적용 범위와 사유를 결과에 남긴다.

`get()`이라는 이름만으로 Java Optional.get이라고 단정하지 않는다. 같은 파일의 선언/명시 import로 타입을 좁힐 수 없으면 해당 Rule을 NOT_EVALUATED로 둔다. import alias, shadowing, 동적 import, TS 경로 alias를 정확히 해석하지 못하면 Architecture 위반을 확정하지 않는다.

Python 표준 `ast` 추가는 확장 후보이며 처음부터 Tree-sitter와 이중 파싱하지 않는다. 입력 언어 버전 범위는 fixture로 입증한 구문 목록을 릴리스 문서에 기록한다. 'Java 모든 버전 지원' 같은 포괄 문구는 사용하지 않는다.

## 검증 기준

네 언어마다 정상·위반·유사하지만 정상·구문 오류·크기/시간 초과 fixture를 가진다. 지원 확장자마다 최소 한 fixture, grammar 버전 변경 때 전체 snapshot 재검증을 요구한다.
