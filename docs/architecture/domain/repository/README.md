# Repository: GitHub 저장소 연결과 분석 설정

> ID: `REPOSITORY` · 소유: `backend/app/domain/repository` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 저장소 연결·설정·설치 권한을 변경할 때

## 책임과 구조

Workspace와 GitHub 저장소/설치의 연결, 연결 상태, 분석 규칙 설정, 자동 분석/외부 AI 허용 여부를 소유한다. GitHub API transport는 shared, PR 데이터는 pull_request가 소유한다.

```text
repository/
├─ api.py              RepositoryAccess·RepositorySnapshot·설정 읽기
├─ router.py
├─ service.py          연결·해제·설정 변경
├─ repository.py       DB 접근 클래스 이름은 RepositoryStore
├─ models.py           RepositoryConnection·RuleConfigVersion
├─ policy.py           연결 가능 조건·보안 정책
├─ dto.py
├─ exceptions.py
└─ schema/{request,response}.py
```

## 연결과 권한

GitHub 로그인과 별도로 GitHub App을 설치하여 선택된 저장소만 연결한다. 기본 권한은 Metadata read, Contents read, Pull requests read이며 기존 대화 코멘트 조회에 필요한 권한은 실제 endpoint로 확인한다. 쓰기 권한은 MVP에 요청하지 않는다. GitHub App은 저장소 단위 권한과 installation token 모델을 제공한다. [S-GH-APP](../../reference/SOURCES.md#s-gh-app)

연결 요청자는 Workspace OWNER/ADMIN이어야 한다. `installation_id`를 보냈다는 이유만으로 연결하지 않는다. 로그인 사용자와 연결된 설치 흐름의 state, GitHub 측 설치/관리 권한, 해당 설치의 허용 저장소 목록을 서버에서 확인한다. GitHub 사용자 검증 권한이 부족하면 연결을 거부하고 재인증/설치 절차로 안내한다.

MVP에서는 하나의 GitHub repository ID를 하나의 활성 Workspace 연결에만 배정한다. 중복 연결 시 409로 처리한다. 계정/저장소 이름이 바뀌어도 GitHub 숫자 ID로 식별한다. 설치 제거·권한 철회 시 `SUSPENDED`로 바꾸고 새 분석과 비밀 접근을 막는다.

## 상태와 설정

연결 상태: `ACTIVE / SUSPENDED / DISCONNECTED`. 영구 삭제 대신 `DISCONNECTED`로 새 작업을 막고 기존 결과는 보관 정책에 따라 제한적으로 유지한다. 재연결은 권한을 다시 확인하고 같은 ID에 새로운 연결 세대를 부여한다.

설정은 allowlist 기반 JSON/Pydantic 구조로만 받는다. 규칙 enabled/severity/threshold, 폴더→계층 매핑, 무시할 경로, `auto_analysis_enabled`, `ai_mode`를 담는다. 임의 Python·쉘·정규식 플러그인·원격 URL을 실행하지 않는다. 정규식은 길이·복잡도를 제한하거나 단순 glob으로 대체한다.

설정 변경 시 불변 `RuleConfigVersion`을 생성한다. 실행 중 분석의 설정을 덮어쓰지 않는다. Analysis는 버전 ID와 정규화된 effective-config digest를 기록한다.

## 기본값

자동 정적 분석은 저장소 연결 화면에서 명시적으로 동의받아 활성화한다. AI는 `OFF`가 기본이다. OWNER만 전송 정책을 바꿀 수 있다. Code snippet 전송은 MVP에서 비활성화하며 [Review 계약](../review/README.md)을 따른다.

연결 성공 뒤 첫 PR 동기화는 [조립 계층](../../runtime/BOOTSTRAP.md)이 두 도메인을 연결한다. repository가 pull_request 내부 Service를 import하지 않는다.

## 테스트

타인의 installation_id 제출, 설치에는 없는 저장소, 권한 철회, 중복 연결 경쟁, 설정 버전 고정, 연결 해제 직후 진행 중 Job, 악성 경로/설정, 토큰이 DB/로그에 남지 않는지 확인한다.
