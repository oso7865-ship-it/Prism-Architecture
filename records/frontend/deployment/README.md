# Vercel 배포 준비

실제 배포는 아직 수행하지 않는다. backend의 docs/PREDEPLOYMENT.md가 운영·복구 절차를 소유한다.

1. 실제 backend HTTPS origin을 확정한다. PRISM_API_ORIGIN 환경변수에 해당 origin을 넣는다(경로·쿼리·비밀값 없음).
2. npm run configure:deployment로 vercel.json을 생성한다. 명령은 파일만 생성하며 배포하지 않는다. 기존 파일이 있으면 덮어쓰지 않는다.
3. npm ci, npm test, npm run build를 실행한다. Node24를 사용한다. Vercel 프로젝트/도메인 연결과 실제 게시 단계는 후속 승인 대상이다.
4. backend의 PUBLIC_APP_ORIGIN과 PUBLIC_API_ORIGIN은 모두 frontend HTTPS origin으로 설정한다. GitHub OAuth callback도 frontend의 /api/v1/auth/github/callback이다.
5. 실제 환경에서 로그인·refresh·logout, 쿠키 Secure/HttpOnly/host-only, API와 health 캐시 금지, 직접 SPA 경로 새로고침, 존재하지 않는 assets 경로가 HTML로 치환되지 않는지 확인한다.

템플릿은 API/health rewrite를 SPA보다 먼저 적용한다. 외부 프록시의 Set-Cookie/Location 보존과 플랫폼의 보안 헤더 적용은 단위 테스트만으로 증명되지 않으므로 공개 환경에서 확인한다. 프론트에는 GitHub secret/PEM/DeepSeek key/DB URL을 넣지 않는다. VITE_* 값은 브라우저 번들에 노출된다.

기본 Content-Security-Policy는 자체 스크립트·폰트·연결만 허용하며 GitHub avatar 이미지만 예외다. 새로운 외부 자산 도입 시 허용 출처를 검토한다. 실제 배포 후 브라우저 CSP 위반과 로그인 이동을 점검한다.
