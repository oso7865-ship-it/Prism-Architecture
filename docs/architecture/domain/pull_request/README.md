# Pull Request: 과거 이력과 현재 상태

> ID: `PULL-REQUEST` · 소유: `backend/app/domain/pull_request` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: PR 목록·상세·과거 리뷰 조회를 변경할 때

## 책임과 파일

GitHub PR 메타데이터를 동기화하고 기존 사람 리뷰를 조회한다. 코드 분석 결과를 PR 메타데이터에 섞거나 GitHub의 Review와 우리 AI Review를 같은 테이블로 취급하지 않는다.

```text
pull_request/
├─ api.py                 PullRequestQuery·PullRequestSnapshot
├─ router.py              목록/상세/동기화 요청
├─ service.py             조회·상세 정보 조합
├─ sync_service.py        GitHub 조회와 upsert
├─ jobs/sync_prs.py        영속 Job handler
├─ repository.py
├─ models.py              PullRequest·PullRequestSyncRun
├─ dto.py
├─ exceptions.py
└─ schema/{request,response}.py
```

PR은 `(repository_connection_id, pr_number)`로 유일하게 식별한다. 저장 필드는 GitHub ID·번호·제목·작성자 ID/login·상태·draft 여부·base/head ref 및 SHA·created/updated/closed/merged timestamp·synced_at이다. 제목·경로도 비공개 정보이므로 팀 권한과 보관 정책을 적용한다.

목록 endpoint만으로 모든 상세 필드가 채워진다고 가정하지 않는다. changed-files/commits 수와 merged 세부 상태가 없으면 `null/UNKNOWN`으로 두고 개별 상세 조회로 보강한다. [S-GH-PR](../../reference/SOURCES.md#s-gh-pr)

## 기존 리뷰 조회

상세 화면에서 필요할 때 커밋·리뷰 상태·리뷰 코멘트·일반 대화 코멘트를 각각 조회한다. 일반 대화 코멘트는 issue comments 계열이라는 차이를 어댑터가 숨긴다. 원문 코멘트/PR 본문/Diff는 영구 DB에 저장하지 않는다. 크기를 제한해 조회 응답으로만 제공하고 저장소 접근이 사라지면 재조회하지 않는다.

외부 HTML을 그대로 렌더링하지 않는다. 코드 조각과 토큰 패턴은 표시 전 필터링하며 보안 정책상 차단한 내용은 GitHub에서 직접 확인하도록 안내한다. 사람 리뷰는 정답 라벨이 아니며 AI 정확도 점수로 자동 환산하지 않는다.

## 공개 계약

`get_in_workspace(pr_id, workspace_id)`, `get_snapshot(pr_id)`, `request_sync(repository_id, actor)`, `sync_one(repository_id, pr_number)`를 제공한다. 분석에 넘기는 Snapshot에는 repository 연결·PR 번호·base/head SHA·접근 가능 여부가 포함된다. DB ORM 모델은 반환하지 않는다.

과거 PR의 '다시 분석'은 **조회 가능한 특정 head/base snapshot을 현재 규칙으로 분석**하는 기능이다. 과거 모든 commit·코멘트 시점의 상태를 복원한다는 의미가 아니다. 상세 정책은 [동기화 정책](SYNC_POLICY.md), 코드 취득은 [분석 Pipeline](../analysis/PIPELINE.md)을 읽는다.

## 테스트

PR 번호가 저장소마다 중복되는 상황, 열린/닫힌/머지 PR 구별, 필드 누락, 중복 이벤트, PR 삭제/접근 불가, 코멘트의 악성 HTML/비밀 문자열, 외부 pagination과 결과 제한을 검증한다.
