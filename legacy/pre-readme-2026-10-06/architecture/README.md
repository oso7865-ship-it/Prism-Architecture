# PRism · 프리즘

GitHub PR을 정적 규칙으로 분석하고 선택적으로 AI 설명을 제공하는 플랫폼의 아키텍처 저장소입니다.

**현재 단계: 배포 전 개발·검증, 문서 중앙 관리**

설계·ADR·README·개발 하네스·작업 보고서는 이 저장소에서 관리합니다. 구현 코드는 별도 Backend/Frontend 저장소에서 dev로 개발 후 main에 통합합니다. [문서 목록·다른 PC 복원](records/README.md)과 [현재 구현/이력](docs/architecture/runtime/IMPLEMENTATION.md)을 확인하세요. AI 품질 실패는 미해결 상태이며 소스 병합이 출시 완료를 의미하지 않습니다.

## 제품과 기술 방향

| 구분 | 방향 |
|---|---|
| 백엔드 | Python / FastAPI, 업무별 domain과 기술 공통 shared |
| 데이터베이스 | PostgreSQL 17 개발 Compose 구성. 로컬 구동 확인 완료, 운영 호스팅은 후속 작업 |
| DB 설계 | [17개 테이블 컬럼·타입·인덱스](docs/architecture/contracts/schema/README.md), 물리 FK 미사용. 실제 migration 상태는 최신 백엔드 보고서 참조 |
| 분석 언어 | Java / JavaScript / TypeScript / Python |
| 분석 방식 | 고정 commit SHA의 정적 규칙 분석. 대상 코드 실행·의존성 설치 없음 |
| AI | LangChain + DeepSeek. 동의 기반 수동 리뷰. 설정·한도·품질 한계는 Review 계약 참조 |
| 프론트 | Vue / TypeScript / Vite, Vercel은 설계 기본값 |
| 배포 | 백엔드 AWS EC2 확정. 리전·인스턴스 크기·DB 호스팅·실제 도메인 미정 |
| 초기 사용 | 본인 Organization과 개인 프로젝트. 향후 외부 사용자 가입·저장소 연결 지원 |

아직 공개 출시 단계가 아닙니다. AI는 정적 Finding을 설명하며 판정을 변경하거나 코드를 자동 수정하지 않습니다. 설계 기본값과 확정된 결정은 [ADR 맵](docs/architecture/decisions/DECISIONS.md)에서 구분합니다.

## 다른 PC에서 이어서 작업하기

문서 작업에는 **Git과 Python 3.10 이상**만 필요합니다. 검증 스크립트는 표준 라이브러리만 사용하므로 pip 설치, DB, Docker, API key가 필요하지 않습니다. 애플리케이션의 Python 3.12는 별도 설계 기본값입니다.

```bash
git clone https://github.com/oso7865-ship-it/Prism-Architecture.git prism
cd prism
python scripts/validate_docs.py
python scripts/check_helpers.py
python scripts/context_select.py --task architecture
```

Windows에서 `python` 명령이 없으면 `py`를 사용합니다. 이미 clone한 PC에서는 작업 시작 전 `git status`로 변경 사항을 확인하고, 작업 트리가 깨끗할 때 `git pull --ff-only`로 최신 내용을 받습니다.

작업을 마칠 때 검증을 실행하고 변경을 커밋·푸시해야 다른 PC에서도 받을 수 있습니다. 다른 PC로 이동하기 전에 현재 진행 상태와 다음 작업도 관련 문서 또는 이 README에 갱신합니다. 로컬 대화 기록이나 개인 경로는 작업 재개에 필요한 정보의 유일한 출처로 삼지 않습니다.

AI와 작업할 때는 다음처럼 요청할 수 있습니다.

> AGENTS.md와 README.md의 현재 단계를 읽고, context_select.py로 필요한 문서만 선택하세요. 구현 현황과 최신 Report를 확인한 뒤 다음 기능을 진행하되 아직 미정인 외부 서비스 설정은 임의로 확정하지 마세요.

## 현재 완료한 것과 다음 작업

완료한 것은 도메인 책임·공개 계약·분석 Pipeline·영속 Job·보안·배포 제약에 대한 문서와 영역별 ADR 관리 체계입니다. 기존 D/C 결정은 15개 ADR로 이관했고 문서 검증 도구로 연결을 확인했습니다. **설계 문서의 존재는 해당 기능 구현 완료를 뜻하지 않습니다.**

개발 기반 구성 범위는 아래와 같습니다. 최신 완료·검증 상태는 위 구현 현황을 따릅니다.

1. [패키지 규칙](docs/architecture/PACKAGE_RULES.md), [코드 컨벤션](docs/architecture/CODE_CONVENTIONS.md), [실행 조립](docs/architecture/runtime/BOOTSTRAP.md)을 기준으로 최소 백엔드·프론트 골격을 만듭니다.
2. 의존성 버전을 검증하여 고정하고 환경 변수 예시·로컬 실행 안내를 추가합니다.
3. DB 연결·마이그레이션·테스트 기반을 확인합니다. 로컬 Docker PostgreSQL 17과 인증·팀 6개 테이블을 구성·검증했습니다. HeidiSQL 접속 방법은 백엔드 문서를 따릅니다.
4. 문서·구조·기초 테스트를 CI에 연결합니다. 이후 구현 순서는 [테스트 및 구현 기준](docs/architecture/quality/TESTING.md)을 따릅니다.

로컬 OAuth/App 연결과 DeepSeek 실제 호출은 확인했습니다. 공개 운영 비용, 도메인, DB 호스팅·백업, 분석 정확도·자원 측정, 외부 공개 운영 정책은 [미정 사항](docs/architecture/decisions/OPEN_ITEMS.md)에 남아 있습니다. 현재 저장소는 아키텍처 관리, Prism-Backend와 Prism-Frontend는 각각 구현 코드를 관리합니다.

## 필요한 문서만 읽기

사람은 [문서 지도](docs/architecture/INDEX.md), AI는 [AGENTS.md](AGENTS.md)에서 시작합니다. 전체 문서나 모든 ADR을 매번 읽지 않습니다.

```text
AGENTS.md → CORE.md → 작업별 소유 문서 → 필요한 세부 문서·ADR
```

```bash
python scripts/context_select.py --list
python scripts/context_select.py --task database --mode edit
python scripts/context_select.py --task adr-review
python scripts/context_select.py --path backend/app/domain/analysis/pipeline.py
```

`--path`는 아직 생성하지 않은 구현 대상 경로에도 사용할 수 있습니다. 선택기는 문서 경로와 글자 수만 출력하며 문서 전체를 자동 전송하지 않습니다. 글자 수는 토큰 수가 아닙니다.

## 저장소 구조와 ADR

```text
docs/architecture/
  CORE.md                 공통 기준
  INDEX.md                문서 지도
  domain/                 업무별 소유 계약
  shared/                 공통 기술 계약
  contracts/              HTTP·데이터 모델
  runtime/                조립·Worker 실행
  frontend/               프론트 설계
  operations/             배포·보안·개인정보
  quality/                테스트·구현 순서
  adr/                    영역별 결정·작성 규칙·템플릿
  decisions/              ADR 맵·미정 사항
  context-map.json         문서·작업·ADR 매핑
scripts/                   선택·검증 도구
```

아키텍처 변경 시 [ADR 작성 규칙](docs/architecture/adr/README.md)에 따라 `ADR-영역-번호`를 발급합니다. 현재 계약은 소유 문서에, 결정 배경과 대체 이력은 ADR에 기록합니다. 변경 시 소유 문서·ADR 맵·context-map.json과 관련 테스트를 함께 갱신합니다.

## 검증과 저장 파일 기준

```bash
python scripts/validate_docs.py --report validation-report.json
python scripts/check_helpers.py --report helper-test-report.json
```

[문서 무결성 결과](validation-report.json)와 [도구 검증 결과](helper-test-report.json)는 명령으로 다시 생성할 수 있는 검증 기록으로 저장합니다. 문서 링크·ID·매핑, 선택 도구, ADR 오류 검출을 확인하며 애플리케이션 실행·성능·보안·실제 GitHub/AWS/DeepSeek 연동을 검증한 결과는 아닙니다.

공유할 문서·ADR·스크립트·검증 결과·Git 설정 파일은 버전 관리합니다. Python 캐시·가상환경·node_modules·빌드 산출물·IDE 개인 설정·로그·DB 백업·실제 `.env`·비밀키는 [.gitignore](.gitignore)로 제외합니다. 외부 서비스 자격증명은 각 환경에 별도로 설정하고 Git으로 옮기지 않습니다. 필요한 설정 형식은 구현 시 비밀 값이 없는 `.env.example`로 공유합니다.
