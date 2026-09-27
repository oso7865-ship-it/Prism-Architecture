# 검증 기준과 구현 순서

> ID: `TESTING` · 소유: `tests` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 테스트·릴리스 게이트·개발 순서를 정할 때

## 테스트 구조

```text
backend/tests/
├─ unit/domain/{auth,user,workspace,repository,pull_request,analysis,review,webhook}/
├─ unit/shared/
├─ integration/{database,github,webhook,jobs}/
├─ contract/{http,github,llm}/
├─ architecture/test_import_boundaries.py
└─ fixtures/analysis/{python,java,javascript,typescript}/
frontend/tests/e2e/
```

이 경로는 구현 대상이다. 현재 제공된 스크립트는 문서 검사이며 애플리케이션 테스트는 아니다.

## 릴리스에 필요한 최소 게이트

| 영역 | 필수 입증 |
|---|---|
| 구조 | shared→domain 금지, 다른 domain 내부 import 금지, Service의 HTTP 스키마/SQL 직접 의존 검사 |
| Auth/RBAC | 변조/만료 세션, state 재사용, 타 팀 리소스, OWNER 이전 경쟁 |
| DB 관계 | 물리 FK 0개·PK/UQ/CHECK 존재, 부모 없는 insert 거부, 다른 팀 부모 ID 주입, 자식 생성/cleanup 경쟁, 비활성화/결과 저장 경쟁, 고아 참조 점검 |
| PR | 최초 30개 metadata-only, pagination, 업데이트 역순, 과거 SHA 불가 |
| Webhook | raw bytes HMAC, duplicate 동시 insert, commit 실패, 내부 retry |
| Job | claim 경쟁, 강제 종료, lease 복구, stale result fence, 재시도 소진 |
| Parser/Rule | 네 언어 fixture, JSX/TSX, 잘못된 입력, 오탐 방지, 미평가 표시 |
| 보안 | 실행/설치 금지, secret canary, output size, SSRF/redirect 방어 |
| AI | OFF면 호출 0회, 식별자 allowlist, timeout·출력 오류·비용 상한 |
| 프론트 | refresh proxy·CDN 비공유, PARTIAL 표시, 외부 HTML 안전 렌더 |

Rule별 fixture 개수와 활성화 조건은 [Rule Engine](../domain/analysis/RULE_ENGINE.md)을 따른다. 코드 커버리지 숫자만으로 품질을 주장하지 않는다. 동시성은 실제 PostgreSQL에서 검증한다.

## 권장 구현 순서 — MVP 내 작업 순서

1. 도메인/Shared 경계, 설정, DB migration, 예외, 문서 선택/CI.
2. GitHub 로그인, User, Workspace와 RBAC를 수직으로 완성.
3. GitHub App 연결, PR 목록/상세/기존 리뷰, 영속 Sync Job.
4. 분석 접수와 Worker·snapshot·한도·결과 API를 fake analyzer로 검증.
5. 네 언어 Parser + 규칙 인터페이스, 작은 Rule 집합부터 fixture 통과 후 38개 목표 목록 확장.
6. Webhook 자동 접수·중복·누락 복구와 혼합 언어 PR 연결.
7. LangChain 설명은 AI OFF 상태로 배선하고 Provider/예산 확정 후 제한적으로 활성화.
8. Render 재기동·메모리·OAuth proxy·보안·cleanup을 검증하고 데모 공개.

단계를 구현할 때마다 관련 소유 문서만 읽고 코드와 함께 갱신한다. 모든 설계를 한 번에 AI에 넣어 전체 구현을 요청하지 않는다. 네 언어 모두 범위에 포함하지만 완료 여부는 테스트로 표시한다.

17개 테이블의 컬럼 설계는 [물리 스키마](../contracts/schema/README.md)를 기준으로 한다. 첫 업무 migration은 users/login_attempts/refresh_sessions/workspaces/workspace_members/invitations 6개부터 구현한다. 나머지는 해당 기능 단계에 도입한다. 물리 FK 없는 무결성은 실제 PostgreSQL에서 두 개 이상의 독립 세션으로 경쟁 시나리오를 실행해 확인한다.

## 증거 남기기

테스트 명령·실행 환경·commit·측정값·실패 내용을 작업 보고서에 기록한다. 가짜 측정값을 예시와 혼동하지 않는다. 외부 API 통합 테스트는 별도 테스트 저장소와 비밀 설정으로 수행한다. 단위 fixture에는 회사 소스/실사용 API key를 넣지 않는다.

## 문서 검사

`python scripts/validate_docs.py`는 상대 링크·문서 ID·선택 매핑·fence 균형 등을 검증한다. 보안/코드 정확성을 검증하지 않는다. 문서 크기는 읽기 부담 경고용이며 토큰 수 계산이 아니다.

문서 도구 회귀 검사는 `python scripts/check_helpers.py`로 재현한다. 작업별 read/edit 선택, ADR 영역 분리, 경로 매핑, 잘못된 경로와 ADR 입력의 거부를 검사한다. 보고서는 `--report helper-test-report.json`으로 갱신한다.

## AI 의미 품질 평가

1. 축약 사례는 원본의 입력 계약·소비 동작을 보존하고, 정상/수정 후 반례와 함께 정답을 검수한다. 에이전트 작성 reference oracle는 일반 테스트로 확인하되 분석 대상 문자열을 exec/eval/import하지 않는다. 사람의 독립 검수 여부를 별도 표시한다.
2. 시스템 지침·입력·schema·모델 설정을 동결하고 같은 조건으로 비교한다. 생성만 비교한 결과와 생성+검증 결과를 섞지 않는다. 조정에 사용하지 않은 사례를 결과를 보기 전에 동결한다. 관측 후 튜닝에 썼다면 더 이상 독립 holdout이 아니다.
3. 결함 탐지의 분모는 결함 기회 수다. 정상 사례가 많다고 미탐이 가려지는 전체 통과율만 보고하지 않는다. 정상 오탐, 질문 오탐, 출력 형식/근거 검증 실패, 초안→최종 삭제와 실제 원인·효과·수정안 오류를 구분한다.
4. 의미 검수는 정확한 최종 응답 해시에 연결한다. 검수 없음·실패·오래된 검수는 채택 PASS가 아니다. 위치가 맞더라도 인과 설명이 틀리면 실패한다. 별도 진단도 오판할 수 있으며 내부 사고의 증거로 해석하지 않는다.
5. 실패한 fixture/실험 기록을 성공으로 덮어쓰지 않는다. 잘못된 평가 자료는 정정 사유와 적용 범위를 명시하고 채택 근거에서 제외한다. 품질 게이트를 통과하지 못한 후보는 기존 런타임과 분리 보존한다. 관측 비용은 실패·검증 호출도 포함하며 제품 접수 한도와 평가 승인을 구분한다.
