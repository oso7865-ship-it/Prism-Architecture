# 전체 변경 병합 및 문서 저장소 분리

- 요청: 누적 작업 전체 병합, 프론트·백엔드 Git에는 문서를 게시하지 않음.
- 상태: 전체 병합·원격 게시 완료. 사용자의 신속 병합 요청에 따라 추가 전체 테스트·원격 CI 결과 확인은 후속 작업으로 남겼다.
- 설계: [병합 계획](2026-09-28_merge-plan.md), [ADR-ARCH-003](../docs/architecture/adr/architecture/ADR-ARCH-003-central-documentation.md).
- 배포: 수행하지 않음. 추가 유료 모델 호출: 0회.

## 변경 내용

| 영역 | 결과 |
|---|---|
| 누적 구현 | 리뷰 근거·후속 검증·관련 코드 조회·평가 도구, 팀 일일 30회 정책, UI/UX와 사용자 문구 개선을 통합 |
| 문서 | 백엔드 291개, 프론트 199개를 records에 원래 경로·바이트로 보관. manifest SHA-256 490개 검증 |
| 구현 저장소 | README·AGENTS·CLAUDE·docs·reports·개발 하네스 등 문서를 Git 추적에서 제외. 기존 로컬 파일 보존 |
| 실행 리소스 | 런타임 및 평가 지침 57개를 .prompt로 변경. 내용과 실제 지침 버전 rh1-d634ca5b77229914 유지 |
| 다른 PC | architecture.json에 중앙 문서 위치와 커밋 고정. restore-docs.mjs가 해시·경로·기존 수정본을 검사하고 없는 문서만 복원 |
| CI | 문서 재유입·비밀 패턴 검사 및 복원 테스트를 코드 저장소에 독립 배치. 아키텍처는 현재 설계와 보관본 무결성을 각각 검증 |

과거 Git 이력은 재작성하지 않는다. 과거 커밋에는 당시 문서가 남아 있고, 이번 커밋 이후 현재 파일 트리에서 제외한다. 보관본의 과거 상태·경로는 당시 기록이다. 최신 병합 상태는 이 보고서를 기준으로 한다.

## 검증

| 검증 | 결과 |
|---|---|
| 프론트 | 10개 파일, 112개 테스트 PASS. TypeScript 및 Vite 빌드 PASS |
| 백엔드 기본 검사 | Ruff check/format, mypy PASS. 관련 평가·프롬프트 테스트 66개 PASS |
| DB | 문서를 제외한 Git index export + 격리된 Linux/PostgreSQL17. upgrade → downgrade base → upgrade 및 schema drift 검사 PASS |
| 전체 백엔드 | 357 PASS / 2 FAIL: 평가 corpus의 Git 줄바꿈 변환. 속성 수정 및 강제 재스테이징 후 새 export의 관련 테스트 15개 PASS. 전체 재실행은 사용자 요청으로 후속 작업 |
| 컨테이너 | 동일 export로 이미지 빌드 PASS. 비루트·네트워크 차단·512MiB에서 4언어 100개 파일 파싱 및 타임아웃, live200/DB없는 ready503 PASS |
| 문서 보관 | 원본/작업 폴더/실제 staged Git blob 모두 490개 SHA-256 일치 |
| 아키텍처 | 현재 문서 링크/ID/ADR 검사와 helpers 90개 조합 PASS. 기존 대형 문서 권고 경고 3개 |
| 저장소 정책 | 백엔드272·프론트59개 추적 파일에서 문서·알려진 비밀 패턴 없음. 복원 테스트 각 2개 PASS |

[컨테이너 원 결과](2026-09-28_merge-container-smoke.json). 소형 합성 파일의 순차 검증이며 최악 부하 측정은 아니다.

## 발견·해결·재발 방지

1. 평가 corpus의 원래 Windows CRLF가 Git의 JSON LF 정규화로 변환되었다. 로컬 원본 검사는 통과했지만 문서를 제외한 새 Git export에서 고정 SHA-256 두 테스트가 실패했다. `.gitattributes`에서 동결된 JSON 세 개와 `.prompt`의 바이트를 보존했다. 일반 add만으로 기존 index 내용이 갱신되지 않아 `git add --renormalize`를 적용한 뒤 export에서 15개 관련 테스트 통과를 확인했다. 데이터나 기준 해시는 바꾸지 않았다. CI가 실제 checkout 파일로 기존 무결성 검사를 계속 수행한다.
2. 문서 제거 후 CI가 GENERAL_HARNESS 내부 스크립트를 호출할 수 없어 독립 검사 스크립트로 교체했다. 빈 새 작업 폴더에서도 제품 실행·CI는 아키텍처 문서 다운로드를 요구하지 않는다.
3. Windows sandbox의 esbuild 상위 디렉터리 접근 제한은 권한이 허용된 동일 명령으로 재검증하여 112개 테스트와 빌드 통과를 확인했다. Git 소유권 검사는 해당 저장소에만 command-local safe.directory를 지정했다. 전역 설정은 변경하지 않았다.

## 기존 품질 한계

[직전 평가 보고서](backend/reports/2026-09-28_recall-repair_report.md)의 의미 품질 채택 게이트는 여전히 FAIL이다. 후보 지침은 실험 자료로만 보관하고 실제 지침은 기존 버전을 유지한다. 위치 탐지 6/6을 정확한 설명 6/6으로 해석하지 않는다. 이번 소스 병합과 기술 검증은 AI 리뷰 품질 완료 또는 출시 승인 판정이 아니다.

## 원격 통합 기록

아키텍처의 검증된 문서 스냅샷을 먼저 게시하고 구현 저장소에서 해당 커밋을 고정한다. 사용자의 후속 지시(빨리 병합, 테스트는 나중에)에 따라 CI 완료 대기는 생략한다. fast-forward로 main을 갱신하고 로컬 작업 브랜치는 dev에 유지한다. 최종 커밋·CI 링크는 완료 후 아래에 기록한다. 이후 보고서만 갱신한 아키텍처 커밋 때문에 구현의 검증된 문서 pin을 불필요하게 변경하지 않는다.


| 저장소 | 커밋 | 결과 |
|---|---|---|
| 백엔드 | [a7b9792](https://github.com/oso7865-ship-it/Prism-Backend/commit/a7b9792576e37ac85a67b58a2b7f80f8adbd0043) | main 및 dev 게시 완료, 로컬 dev 유지, 현재 문서 0개 |
| 프론트엔드 | [c33ec96](https://github.com/oso7865-ship-it/Prism-Frontend/commit/c33ec96ad0fbb6359b0bfa39826e8303bb7c3c79) | main 및 dev 게시 완료, 로컬 dev 유지, 현재 문서 0개 |
| 아키텍처 문서 스냅샷 | [2c4b743](https://github.com/oso7865-ship-it/Prism-Architecture/commit/2c4b743d55a2624cbb84f99525dcff238116043a) | main 게시 완료, 두 구현 저장소가 이 커밋에 고정 |

- 구현의 원격 main·dev를 atomic push로 함께 갱신했다. fast-forward이며 force push나 역사 재작성은 하지 않았다. 로컬 main도 동일 커밋이며 체크아웃은 dev를 유지했다.
- 현재 코드 트리에서 문서 확장자와 docs/reports/개발 하네스 디렉터리가 0개임을 확인했다. 기존 로컬 문서는 남아 있고 ignore 대상이다.
- 후속 확인: GitHub Actions 결과, 백엔드 전체 테스트 최종 재실행, 다른 PC 문서 복원 실사용 검증. CI 자동 실행 자체는 유지하며 이번 요청에 따라 완료를 기다리지 않았다.
