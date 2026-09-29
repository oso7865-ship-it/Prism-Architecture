# ADR-DEPLOY-003: AWS 백엔드와 기존 production 계약 유지

> ID: `ADR-DEPLOY-003` · 소유: `DEPLOY` · 기준: `2026-09-28`
> 읽는 때: AWS 배포 대상·운영 설정·전환 범위를 변경할 때

- 상태: `SUPERSEDED`
- 기록일: `2026-09-28`
- 근거: 사용자 “백엔드 AWS로 하기로했어” 결정
- 대체하는 ADR: [ADR-DEPLOY-001](ADR-DEPLOY-001-render-real-deployment.md), [ADR-DEPLOY-002](ADR-DEPLOY-002-production-boundary.md)
- 대체한 ADR: [ADR-DEPLOY-004](ADR-DEPLOY-004-ec2-runtime.md). 실행 서비스를 EC2로 확정한다.

## 배경

기존 결정은 Render와 해당 무료 환경을 전제로 했다. 사용자는 백엔드 호스팅을 AWS로 변경했다. 공급자 선택과 AWS 내부 실행 서비스 선택, 실제 자원 생성은 구분한다.

## 결정

백엔드 배포 대상은 AWS다. 구체 실행 서비스, 리전, 인스턴스·컨테이너 크기, 네트워크·HTTPS 진입점, DB 제공자·백업, 운영 예산, 공개 주소는 아직 확정하지 않는다. RDS 또는 특정 AWS 서비스가 자동으로 채택된 것은 아니다. Vue/Vercel 프론트 결정과 초기 개인·Organization 사용 범위는 유지한다.

DEPLOY-001의 실제 공개 주소 사용 계획과 DEPLOY-002의 다음 production 계약을 유지한다.

- FastAPI 모듈형 모놀리스, 비root Docker 이미지와 단일 Uvicorn worker, 제한된 parser subprocess로 시작한다. API/embedded Job 실행 자원과 기동·중단 동작은 선택한 AWS 서비스에서 검증한다.
- production은 HTTPS 공개 DNS origin과 완전한 인증 설정을 요구한다. PUBLIC_APP_ORIGIN과 PUBLIC_API_ORIGIN은 동일한 프론트 프록시 origin이며 AWS 백엔드 HTTPS 주소는 서버 측 프록시 목적지다.
- 로그인·설치 binding·refresh 쿠키는 Secure·HttpOnly·SameSite=Lax·host-only, 삭제 시에도 동일 속성을 적용한다. API는 브라우저/CDN 모두 no-store, 운영 API 문서는 비활성화한다. 정확한 frontend Origin과 전용 헤더로 CSRF를 검사한다.
- PostgreSQL은 sslmode=verify-full과 제공자 CA를 사용한다. 운영 키를 개발 키와 분리하며 Git·이미지·프론트 변수에 비밀값을 넣지 않는다. AWS에서의 비밀 주입 방식은 실행 서비스 선택 후 설계한다.
- 자동 배포와 AI는 기본 OFF다. migration은 앱 시작과 분리하여 배포 단계에서 한 번 실행하고 실패하면 rollout을 중단한다. schema 호환성이 확인된 이전 이미지로만 복귀하며 자동 DB downgrade를 하지 않는다.
- 백업·복원 리허설은 별도 테스트 DB에서 진행하고 운영 복원은 별도 DB에 복구·검증한 뒤 전환한다.

Render 무료 서비스의 유휴·DB 만료 정책은 AWS 설계에 적용하지 않는다. AWS 선택만으로 무료 운영이나 상시 Job 처리를 보장하지 않는다. 인프라 비용·메모리·재시작·영속성·Webhook/OAuth 전달은 선택한 구성에서 확인한다.

## 대안

Render 유지 대신 사용자의 AWS 선택을 반영한다. AWS 서비스 간 비용·성능 비교는 아직 하지 않았으므로 우월성이나 비용 절감을 결정 이유로 주장하지 않는다.

## 영향과 한계

기존 deployment/render.example.yaml은 과거 예시이며 AWS 배포 명세가 아니다. Dockerfile과 provider 중립 production 설정은 재사용 후보지만 AWS에서 실행 검증된 것으로 간주하지 않는다. 실제 자원 생성·결제·배포는 이번 결정 기록에 포함하지 않는다.

## 소유 문서와 검증

[DEPLOYMENT](../../operations/DEPLOYMENT.md), [OPEN-ITEMS](../../decisions/OPEN_ITEMS.md), [FRONTEND](../../frontend/README.md)를 동기화한다. 이번 검증은 링크·ID·ADR 관계다. 실제 OAuth 쿠키 프록시, HMAC Webhook, 두 계정 격리, Job 중단·복구, DB/메모리/비용 및 배포 smoke test는 서비스·주소 확정 후 수행한다.
