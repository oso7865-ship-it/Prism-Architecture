# 외부 기술 사실의 근거

> ID: `SOURCES` · 소유: `external-references` · 기준: `v0.1.0 / 2026-09-25`
> 읽는 때: 외부 기술 사실·라이브러리/서비스 제약을 재검증할 때

확인일: **2026-09-25**. 공식 문서만 사용했다. 외부 서비스 제약은 변경될 수 있으므로 배포 직전에 재확인한다. 정책 수치·패키지 배치·제품 범위는 이 프로젝트의 설계 결정이며 아래 업체가 권장/보장한 값이라고 해석하지 않는다.

이 파일은 사실 검증/의존성 업그레이드 때만 읽고 일상 구현 컨텍스트에 기본 포함하지 않는다.

## S-PY-01

Python reserved keywords

```text
https://docs.python.org/3/reference/lexical_analysis.html#keywords
```

사용 근거: global 예약어와 일반 식별자 제약.

## S-FASTAPI-BG

FastAPI Background Tasks

```text
https://fastapi.tiangolo.com/tutorial/background-tasks/
```

사용 근거: 응답 후 작업과 무거운 작업의 분리 경계. 영속성은 이 프로젝트 설계로 보완.

## S-FASTAPI-LIFE

FastAPI Lifespan Events

```text
https://fastapi.tiangolo.com/advanced/events/
```

사용 근거: 시작·종료 자원 초기화/정리.

## S-RENDER-FREE

Render Deploy for Free

```text
https://render.com/docs/free
```

사용 근거: 유휴 중지, 임시 파일시스템, 무료 서비스 제한, PostgreSQL 30일 만료.

## S-GH-PR

GitHub Pull Requests REST API

```text
https://docs.github.com/en/rest/pulls/pulls
```

사용 근거: 목록 정렬/상태/pagination, PR files 최대 3,000개와 상세 자료.

## S-GH-HMAC

GitHub Validating Webhook Deliveries

```text
https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries
```

사용 근거: 원문 payload의 HMAC-SHA256 검증.

## S-GH-WEBHOOK

GitHub Webhook Best Practices

```text
https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks
```

사용 근거: 10초 응답, 이벤트 검증, redelivery 시 같은 delivery ID.

## S-GH-RETRY

GitHub Handling Failed Deliveries

```text
https://docs.github.com/en/webhooks/using-webhooks/handling-failed-webhook-deliveries
```

사용 근거: 실패한 delivery는 자동 재전송되지 않음.

## S-GH-APP

GitHub App vs OAuth App

```text
https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/deciding-when-to-build-a-github-app
```

사용 근거: 설치·저장소별 권한과 사용자 OAuth의 차이.

## S-GH-INSTALL

GitHub App Installations API

```text
https://docs.github.com/en/rest/apps/installations
```

사용 근거: 설치 token 기반 저장소 접근과 endpoint 권한.

## S-GH-OAUTH

GitHub Authorizing OAuth Apps

```text
https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
```

사용 근거: OAuth web flow, state 및 사용자 인증 구성의 구현 근거.

## S-GH-RATE

GitHub REST API Best Practices

```text
https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api
```

사용 근거: pagination·조건부 요청·rate-limit 처리.

## S-TS-INTRO

Tree-sitter Introduction

```text
https://tree-sitter.github.io/tree-sitter/
```

사용 근거: 구문 트리 생성/파싱의 역할.

## S-TS-PY

py-tree-sitter Documentation

```text
https://tree-sitter.github.io/py-tree-sitter/
```

사용 근거: Python binding과 language/parser/query API.

## S-LC-MODEL

LangChain Models

```text
https://docs.langchain.com/oss/python/langchain/models
```

사용 근거: Provider 모델 호출과 구성.

## S-LC-STRUCTURED

LangChain Structured Output

```text
https://docs.langchain.com/oss/python/langchain/structured-output
```

사용 근거: 구조화 출력 전략. Provider별 지원 여부는 별도 검증.

## S-DB-01

SQLAlchemy Asyncio

```text
https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
```

사용 근거: AsyncSession lifecycle과 동시 작업별 Session 분리.

## S-PG-QUEUE

PostgreSQL SELECT locking clauses

```text
https://www.postgresql.org/docs/current/sql-select.html
```

사용 근거: FOR UPDATE SKIP LOCKED의 의미와 queue 소비 적용 범위.

## S-VERCEL-REWRITE

Vercel Rewrites

```text
https://vercel.com/docs/routing/rewrites
```

사용 근거: 외부 origin 프록시와 rewrite cache 동작/비활성화.

## S-PG-RELATIONS

[PostgreSQL 17 Constraints](https://www.postgresql.org/docs/17/ddl-constraints.html), [Explicit Locking](https://www.postgresql.org/docs/17/explicit-locking.html).

2026-09-25 확인. 사용 근거: 행 내부 CHECK와 UNIQUE의 범위, row lock 충돌 및 transaction 종료 시 해제. FK 미사용·Workspace별 쓰기 직렬화는 PRism 설계 선택이며 PostgreSQL이 강제하는 정책이 아니다.
