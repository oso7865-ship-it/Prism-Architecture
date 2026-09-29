# ADR-DEPLOY-002: 배포 전 production 설정과 검증 경계

> ID: `ADR-DEPLOY-002` · 소유: `DEPLOY` · 기준: `2026-09-27`
> 읽는 때: 운영 환경 설정·배포 준비·복구 절차를 변경할 때

- 상태: `SUPERSEDED`
- 기록일: `2026-09-27`
- 근거: 사용자가 배포 전 단계의 자율 작업을 승인했다.
- 대체하는 ADR: 없음
- 대체한 ADR: [ADR-DEPLOY-003](ADR-DEPLOY-003-aws-backend.md)

## 배경

로컬 인증 구현은 HTTP localhost와 Secure=false 쿠키를 사용한다. 이를 그대로 공개 HTTPS 환경에 적용하지 않는다. 배포 주소와 DB 제공자는 아직 확정되지 않았다.

## 결정

production 모드를 추가하여 HTTPS 공개 DNS origin, 완전한 인증 설정, PostgreSQL sslmode=verify-full을 요구한다. 앱과 API의 공개 origin은 동일한 Vercel 프록시 origin이다. OAuth/설치 binding과 refresh 쿠키는 Secure·HttpOnly·SameSite=Lax·host-only를 유지하며 삭제에도 같은 속성을 쓴다. API는 브라우저/CDN 모두 no-store, API 문서는 운영에서 비활성화한다. CSRF는 정확한 frontend Origin과 전용 헤더를 검사한다.

Render 단일 worker·비root Docker 이미지와 Vercel rewrite 템플릿을 준비한다. 자동 배포와 AI는 기본 OFF다. 런타임에서 migration을 자동 실행하지 않고 별도 승인된 배포 단계에서 한 번 수행한다. 공개 URL·키·CA·플랜은 사용자가 확정한 값으로 주입한다. 배포 템플릿 생성·빌드 성공은 실제 배포 완료를 뜻하지 않는다.

백업·복원 리허설은 별도 테스트 DB의 합성 스키마에서 수행한다. 운영 복원은 별도 DB에 복구 후 검증하고 전환한다. 장애 시 DB downgrade를 자동 실행하지 않는다.

## 대안

프론트와 API를 서로 다른 cookie site로 제공하면 교차 출처 쿠키/CSRF 정책과 브라우저 제약을 별도로 검증해야 한다. 초기 버전은 기존 동일 출처 프록시 설계를 구현한다. 개발 모드에 HTTPS를 혼합하는 대신 production 검증을 분리한다.

## 영향과 한계

DEPLOY-001의 Render 선택과 FRONTEND-001의 Vue/Vercel은 유지한다. DB CA 체인은 제공자 확정 후 설치하며 sslmode=require로 검증을 약화하지 않는다. 무료 인스턴스의 유휴/재기동과 best-effort Job 제약도 유지한다. 실제 OAuth/Set-Cookie 프록시·GitHub Webhook·다른 사용자 검증은 공개 환경에서 별도로 수행한다. AI 품질 개선은 사용자 지시대로 후순위다.

## 소유 문서와 검증

- [RENDER](../../operations/RENDER.md)
- [FRONTEND](../../frontend/README.md)

Settings 거부 사례·Secure cookie lifecycle·cache/보안 헤더·Docker 기동·프록시 설정 생성 테스트·테스트 DB 백업복원과 전체 회귀 테스트를 실행한다. 실행 증거는 구현 저장소의 배포 전 Report에서 관리한다.
