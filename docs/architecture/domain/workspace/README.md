# Workspace: 테넌트와 RBAC

> ID: `WORKSPACE` · 소유: `backend/app/domain/workspace` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 멤버십·RBAC·테넌트 접근을 변경할 때

## 책임과 구조

Workspace가 테넌트 경계다. 역할은 User 전체가 아니라 `WorkspaceMember`에 저장한다. WorkspaceRole이 여러 도메인에서 필요해도 이 도메인 소유로 남긴다.

```text
workspace/
├─ api.py            WorkspaceAccess·MembershipSnapshot 공개 계약
├─ router.py         팀·초대·멤버 API
├─ service.py        생성·가입·역할 변경·소유권 이전
├─ repository.py     팀/멤버/초대 접근
├─ models.py         Workspace·WorkspaceMember·Invitation
├─ role.py           OWNER·ADMIN·MEMBER
├─ permission.py     역할→허용 동작의 순수 매핑
├─ dto.py
├─ exceptions.py
└─ schema/{request,response}.py
```

## 권한표 — 설계 기본값

| 동작 | OWNER | ADMIN | MEMBER |
|---|---|---|---|
| 팀의 PR·분석·기존 AI 결과 조회 | 허용 | 허용 | 허용 |
| 분석 실행·PR 수동 동기화 | 허용 | 허용 | 허용 |
| 승인된 정책 안의 AI 설명 요청 | 허용 | 허용 | 허용 |
| 저장소 연결/해제·규칙 설정 | 허용 | 허용 | 거부 |
| MEMBER 초대/제거 | 허용 | 허용 | 거부 |
| ADMIN 역할 부여/해제 | 허용 | 거부 | 거부 |
| 외부 AI 전송 허용·보안 정책 변경 | 허용 | 거부 | 거부 |
| 소유권 이전·Workspace 삭제 요청 | 허용 | 거부 | 거부 |

삭제의 실제 구현 범위는 보관 정책을 따른다. OWNER만 가능하다는 규칙이 즉시 영구 삭제 API를 제공한다는 뜻은 아니다.

## 공개 계약과 인가

`require_permission(principal, workspace_id, permission)`은 최신 활성 멤버십을 확인하고 허용하지 않으면 도메인 예외를 발생시킨다. `GET`도 생략하지 않는다. 리소스 조회에는 별도로 workspace_id 스코프를 적용한다.

사용자가 보내는 workspace_id는 검증할 대상이지 권한 증명서가 아니다. 분석 Worker는 접수 때의 역할을 그대로 믿지 않고 실행 직전에 사용자의 활성 상태·멤버십·대상 저장소 상태를 다시 확인한다. 시스템 Webhook Job은 사용자 역할을 흉내 내지 않고 저장소의 자동 분석 허용 정책으로 실행한다.

## 상태와 데이터

`WorkspaceMember`는 `(workspace_id, user_id)`가 유일하다. 활성 OWNER는 팀당 정확히 한 명이라는 MVP 정책을 둔다. 소유권 이전 시 Workspace 행을 잠그고 이전 OWNER 강등·새 OWNER 승격을 같은 트랜잭션에서 처리한다. 마지막 OWNER 탈퇴/강등을 단독으로 허용하지 않는다.

초대는 일회성 난수 링크와 hash·만료·대상 GitHub 숫자 ID를 저장한다. 초대 링크를 받은 사람이 로그인한 ID와 초대 대상이 일치해야 한다. 이메일 발송 인프라는 MVP에 요구하지 않는다. 만료 기본값은 24시간, 한 번 가입하면 소비한다.

동일 Workspace에 가입한 모든 멤버가 연결된 저장소 메타데이터와 분석 결과를 볼 수 있다는 정책을 초대/연결 화면에 표시한다. GitHub 원본 저장소 접근 권한과 이 서비스 결과 접근 권한이 동일하다고 표현하지 않는다.

## 테스트

A팀 OWNER가 B팀 리소스를 보지 못하는지, 탈퇴/강등 뒤 Job이 실행되지 않는지, 동시 소유권 이전, 초대 탈취·재사용, ADMIN의 OWNER 승격 시도, 숨긴 버튼을 우회한 API 호출을 검증한다.

물리 컬럼·제약·인덱스와 논리 참조 검증은 [스키마 계약](../../contracts/schema/IDENTITY.md)을 따른다. 물리 FK는 생성하지 않는다.
