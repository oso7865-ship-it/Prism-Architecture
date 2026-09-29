# 백엔드 AWS 선택 반영

## 작업 계약

- 요청: 사용자가 백엔드 배포 대상으로 AWS를 확정했다.
- 범위 M: 아키텍처 main의 배포 결정과 직접 참조 문서만 변경한다. 프론트·백엔드 저장소에 문서를 추가하지 않는다.
- 읽은 문서 ID: CORE, ADR-GUIDE, ADR-TEMPLATE, ADR-DEPLOY-001/002, RENDER, OPEN-ITEMS, CONFIG, TESTING, ADR-ARCH-003.
- 기준: 사용자 최신 결정, ADR 영역별 번호·대체 관계, 중앙 문서 관리. 문서 Gate 적용.
- 계획: ADR-DEPLOY-003 → 현재 배포 소유 문서 → 직접 참조·미정사항·결정 맵 갱신 → 문서 링크/ADR 검증.
- 제외: AWS 자원 생성·결제·계정 연결·실제 배포, 앱 코드 수정, 유료 모델 호출, 전체 제품 테스트, 추가 커밋·푸시.

## 결과

AWS 선택은 확정이며 실제 실행 서비스, 리전, 장기 DB 호스팅, 예산, 도메인은 미정이다. 기존 Vercel 프론트와 Docker/FastAPI, production 보안·마이그레이션·복구 계약은 유지한다. Render 고유의 무료 플랜 가정은 현행 배포 전제에서 제거한다.

[ADR-DEPLOY-003](../docs/architecture/adr/deployment/ADR-DEPLOY-003-aws-backend.md)이 기존 DEPLOY-001/002를 대체하며, 유지되는 production 계약을 다시 명시한다. [현재 배포 설계](../docs/architecture/operations/DEPLOYMENT.md)가 현행 기준이다. 과거 ADR의 본문과 records 보관본은 소급 수정하지 않는다.

백엔드의 deployment/render.example.yaml은 아직 남아 있는 과거 예시다. 자동 배포는 비활성화돼 있으며 AWS용 배포 명세로 사용할 수 없다. AWS 서비스가 정해지면 실행 설정·배포 명세와 frontend 프록시 목적지를 함께 준비한다. 현행 앱에는 특정 Render API를 호출하는 런타임 의존성을 찾지 못했다.

## 검증 및 후속 작업

문서 검증 PASS: 현재 Markdown 86개, 등록 ID 79개, 상대 링크 360개, ADR 28개를 확인했다. 기존 대형 문서 분할 권고 3개는 유지한다. 제품 테스트·AWS 실연동은 수행하지 않았다. 지난 병합에서 미룬 CI/전체 테스트 결과 확인과 AI 의미 품질 한계는 이번 결정으로 해결되지 않는다. 이 문서 변경은 로컬 main 작업 폴더에 반영하며 원격 게시와 구현 저장소의 architecture.json pin 갱신은 후속 작업이다.
