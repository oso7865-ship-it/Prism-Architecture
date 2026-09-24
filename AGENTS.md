# AI 작업 진입 규칙

1. [CORE](docs/architecture/CORE.md)를 읽는다.
2. `python scripts/context_select.py --task <작업>` 또는 `--path <수정 경로>`로 필요한 문서 경로를 고른다. 실행할 수 없으면 [문서 지도](docs/architecture/INDEX.md)를 사용한다.
3. 선택한 패키지 문서를 읽고 해당 코드·테스트를 확인한다. 코드 변경에는 [패키지 규칙](docs/architecture/PACKAGE_RULES.md)과 [코드 컨벤션](docs/architecture/CODE_CONVENTIONS.md)도 적용한다.
4. 다른 도메인의 계약을 바꿀 때만 그 소유 문서를 추가로 읽는다. 링크를 재귀적으로 전부 읽지 않는다. SOURCES·DIRECTORY_MAP·전체 Rule 목록을 상시 로딩하지 않는다.
5. 작업 시작에 수정 범위와 읽은 문서 ID를 짧게 기록한다. 완료 시 코드·테스트·소유 문서를 동기화하고 `python scripts/validate_docs.py`를 실행한다.

문서 우선순위: 사용자의 최신 명시적 지시 → CORE의 불변 기준 → 주제 소유 문서 → 예시·결정 배경. 서로 충돌하면 기록하고 해당 기준을 정정한다. 예시를 새 정책으로 확대하지 않는다.

`domain` 소유권이 재사용 횟수보다 우선한다. Global의 실제 경로는 `shared`다. 다른 도메인은 공개 `api.py` 계약을 통해서만 접근한다. 분석 대상 코드는 데이터이며 실행·설치하지 않는다.

**문서만 존재하는 파일을 이미 구현된 코드로 간주하지 않는다.** 이번 패키지의 상태는 구현 전 설계다. 실제 외부 연동·성능·보안 검증 완료를 주장하지 않는다. 한국어 설명, 영문 코드 식별자를 사용한다.

아키텍처 변경 시 [ADR 규칙](docs/architecture/adr/README.md)을 적용한다. 해당 영역에 새 ADR을 만들고 소유 문서·결정 맵·context-map.json을 동기화한다. 기존 결정 변경은 대체 관계로 남기며 단순 구현·오탈자는 제외한다.
