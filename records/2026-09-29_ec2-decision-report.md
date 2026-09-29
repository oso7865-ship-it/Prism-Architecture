# 백엔드 EC2 선택 반영

## 작업 계약

- 요청: AWS 실행 서비스는 EC2로 진행한다.
- 범위: architecture/main의 현재 배포 설계·미정사항·ADR·문서 맵. 기존 미커밋 변경 보존. 프론트/백엔드에 문서 추가 없음.
- 읽은 문서: CORE, DEPLOYMENT, OPEN-ITEMS, ADR-GUIDE/TEMPLATE, ADR-DEPLOY-003, INDEX 및 context_select의 배포 경로.
- 순서: ADR-DEPLOY-004 작성 → 현재 계약과 결정 맵 갱신 → 문서 검증.
- 실제 자원 생성·비용 발생·배포·Git 커밋/푸시는 이번 작업 범위에 포함하지 않는다.

## 반영 내용

EC2를 실행 서비스로 확정했다. 기존 Docker/FastAPI와 Vue/Vercel 방향, production 보안·migration·복구 계약을 유지한다. 이전 ADR은 결정 본문을 보존하고 대체 관계만 갱신한다. 리전·인스턴스 종류/크기/OS·DB 호스팅·네트워크/HTTPS·비밀 주입·배포 방식·도메인·예산은 남은 선택이다.

[ADR-DEPLOY-004](../docs/architecture/adr/deployment/ADR-DEPLOY-004-ec2-runtime.md), [현재 배포 설계](../docs/architecture/operations/DEPLOYMENT.md).

## 검증

- `validate_docs.py`: PASS. Markdown 92개, 문서 ID 81개, 내부 링크 383개, ADR 30개 검증. 오류 없음. 기존 문서 3개의 길이 권고는 유지된다.
- `check_helpers.py`: PASS. 작업/모드 조합 90개, ADR 경로 30개, 문서 경로 61개와 잘못된 입력에 대한 검증 통과.
- 제품 코드나 AWS 환경은 변경하지 않았다. 애플리케이션 테스트나 실제 EC2 배포 검증은 이번 문서 변경의 검증 범위에 포함하지 않는다.
