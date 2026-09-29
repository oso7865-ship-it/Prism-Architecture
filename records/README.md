# 개발 문서와 작업 기록

개발 문서는 이 아키텍처 저장소에서만 게시한다. backend/와 frontend/는 원래 구현 저장소의 상대 경로를 유지한 사본이며 내용은 manifest.json의 SHA-256으로 보존 검증한다. 과거 완료/미완료·경로·커밋은 당시 사실이다. 과거 상대 링크는 로컬 복원 후 원래 구현 저장소 기준으로 읽는다. 현재 설계는 docs/architecture가 소유한다.

- [백엔드 현황](backend/docs/PROJECT_STATUS.md)
- [현재 완성도 Gate와 보수 결과](2026-09-29_predeployment-hardening.md)
- [EC2 배포 전 실행 안내](2026-09-29_ec2-release-runbook.md)
- [EC2 직접 접속과 RDS 준비 상태](2026-09-30_ec2-access-report.md)
- [GHCR·EC2·Vercel 자동 배포 구현과 초기 설정](2026-09-30_automatic-deployment.md)
- [EC2 Caddy HTTPS와 실제 인증서 검증](2026-09-30_ec2-https.md)
- [운영 환경값 반영과 GitHub·AI·RDS 연결 점검](2026-09-30_production-runtime.md)
- [프론트 EC2 전환·도메인·HTTPS·실제 화면 배포](2026-09-30_frontend-ec2.md)
- [EC2 전체 출시·공개 이미지·자동 배포 최종 검증](2026-09-30_full-ec2-release.md)
- [백엔드 최신 보고서](backend/reports/_LATEST.md)
- [프론트 최신 보고서](frontend/reports/_LATEST.md)
- [AI 품질 실패와 후속 조치](backend/reports/2026-09-28_recall-repair_report.md)
- [이번 병합 계획](2026-09-28_merge-plan.md)
- [최신 병합 결과](2026-09-28_merge-report.md)

## 다른 PC에서 재개

세 저장소를 clone하고 구현 저장소 architecture.json revision과 같은 아키텍처 커밋을 checkout한다. backend 또는 frontend 루트에서 실행한다.

```sh
node scripts/restore-docs.mjs ../Prism-Architecture --check
node scripts/restore-docs.mjs ../Prism-Architecture
```

복원한 README/AGENTS/하네스/설계/Report는 Git ignore 대상이다. 기존 수정 파일과 다르면 전체 사전 검사에서 멈추고 덮어쓰지 않는다. 문서를 수정하면 중앙 records와 manifest를 갱신한다. `python scripts/validate_records.py`로 보존을 검사한다. 제품 실행과 CI는 문서 clone에 의존하지 않는다.

AI 런타임/평가용 .prompt는 코드 저장소의 실행 리소스다. 실패 후보는 평가 자료로만 보존한다. 실제 지침은 제품 해시와 최신 Report로 확인한다.
