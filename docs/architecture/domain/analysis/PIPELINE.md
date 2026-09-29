# 분석 Pipeline과 소스 취득

> ID: `ANALYSIS-PIPELINE` · 소유: `backend/app/domain/analysis/pipeline.py` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 파일 취득·Diff·자원 제한·분석 순서를 변경할 때

## 순서

```text
고정 Snapshot·권한 재검사
  → 변경 파일 목록 + 변경 줄 범위 확보
  → 파일별 고정 SHA의 전체 소스 취득
  → 비밀 패턴 검사 + 언어 감지
  → 제한된 프로세스에서 구문 파싱/구조 추출
  → 지원 가능한 Rule 평가
  → 결과·검사 범위 원자적 저장
  → 임시 소스 정리
```

Diff는 변경 위치를 표시하는 자료이지 완전한 소스 파일이 아니다. 잘린 함수 조각을 파싱하고 파일 전체 검사라고 표시하지 않는다. 파일 내용은 branch 이름이 아니라 head SHA로 가져온다. 변경 파일 API가 현재 PR 상태를 기준으로 응답하므로 취득 전후 PR의 base/head SHA를 확인한다. 고정 Snapshot과 다르면 섞어 분석하지 않고 `SNAPSHOT_CHANGED`로 종료/재접수를 안내한다.

## 완전성·예외 파일

PR 파일 목록은 pagination을 끝까지 확인하되 프로젝트 한도를 넘으면 중단하고 PARTIAL로 표시한다. GitHub PR files endpoint 자체도 최대 3,000 파일 한도가 있다. [S-GH-PR](../../reference/SOURCES.md#s-gh-pr)

Patch가 누락/절단되면 고정 base/head 파일을 모두 취득해 로컬 Diff를 계산할 수 있는 범위에서 보완한다. 정확한 PR merge-base를 확보하지 못한 경우 GitHub PR Diff와 동일하다고 표현하지 않고 CHANGED 범위 판정을 미평가 처리한다. 임의 HEAD~1을 비교 기준으로 대체하지 않는다.

이름 변경은 previous_filename 매핑을 보존한다. 삭제 파일은 head에 없으므로 현재 코드 규칙을 적용하지 않고 삭제 사실만 기록한다. 과거 비밀 노출의 완전한 탐색은 별도 Git-history 기능으로, MVP에 포함하지 않는다. fork/삭제 branch/force-push 때문에 SHA나 blob을 가져올 수 없으면 SOURCE_UNAVAILABLE이며 대체로 최신 branch를 분석하지 않는다.

바이너리·LFS pointer·symlink·submodule·인코딩 오류·생성/축약 파일은 사유를 남겨 제외한다. `.env`, JSON, YAML 등 미지원 소스 언어의 작은 텍스트도 Secret scanner 대상이 될 수 있다. '언어 미지원'을 '비밀정보 검사 완료'로 취급하지 않는다.

## 초기 자원 한도 — 측정 전 설계 기본값

| 항목 | 초기값 |
|---|---|
| 한 PR 취득/평가 파일 수 | 최대 100개 |
| 텍스트 파일 하나 | 최대 200 KiB |
| 한 run 누적 소스 bytes | 최대 2 MiB |
| 한 파일 parse/rule 시간 | 최대 5초 |
| 전체 정적 run 실행 시간 | 최대 120초 |
| 개별 외부 API timeout | 최대 10초 |
| 파일별 Finding | 최대 100건, 초과 사실 별도 표시 |

이 수치로 선택한 AWS 실행 환경에서 반드시 동작한다는 보장은 없다. 실제 피크 메모리/CPU/외부 API 수를 측정하여 조정한다. 모든 파일을 동시에 읽지 않고 하나씩 처리하고, 중간 AST를 즉시 해제한다. HTTP body와 output에도 크기 제한을 적용한다. 상한 초과를 성공적인 무결점 검사로 표시하지 않는다.

## 신뢰 경계

취득 URL은 검증된 GitHub host/공개 저장소 식별자로 client가 만든다. PR 안의 임의 URL·redirect를 credential과 함께 따라가지 않는다. 압축 파일 clone/extract, git hook, Maven/Gradle/npm/pip 설치, 저장소 설정 코드 실행을 하지 않는다.

Parser process에는 필요 없는 secret 환경변수를 전달하지 않는다. timeout 시 프로세스를 종료하고 반드시 reap한다. **같은 컨테이너의 subprocess는 완전한 보안 sandbox가 아니다.** Parser 취약점 대비 업데이트·자원 격리·악성 입력 테스트가 필요하며 민감 코드의 기업 운영 수준 격리는 별도 검증 대상이다.

소스가 꼭 필요하면 제한된 임시 디렉터리를 사용하고 finally 및 시작 시 cleanup한다. 원문을 DB/캐시/로그/장기 디스크에 쓰지 않는다. 임시 파일 삭제를 암호학적 안전 삭제 보장으로 표현하지 않는다.

## 결과 해석

변경된 함수에 기존부터 있던 문제가 검출될 수 있다. base 분석과 비교하지 않은 Finding을 '이번 PR에서 새로 생긴 결함'으로 단정하지 않는다. 기본 표기는 '선택한 PR snapshot에서 관찰된 항목'이다. 전체 저장소 순환 의존성·타입/데이터 흐름 검증은 수행하지 않는다.
