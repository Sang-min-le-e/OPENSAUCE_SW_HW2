# OPENSAUCE_SW_HW2

## CI/CD 자동 업데이트 검증 체크리스트

### 1) 푸시 전 로컬 확인
- `app/ml/model.py`, `app/index.html`, `.github/workflows/ci.yml` 변경 저장 확인
- 로컬 서버에서 최소 1회 업로드 테스트
  - 사람 사진: 정상 결과 반환
  - 사람 없는 사진: 에러 메시지 + 재업로드 유도 표시
- `git status`로 커밋 대상 파일 확인

### 2) 푸시 및 워크플로우 트리거 확인
- `main` 브랜치로 push 했는지 확인
- GitHub Actions에서 최신 run 생성 확인
- 실행 워크플로우가 `CI/CD Pipeline for Body Type MLOps API`인지 확인

### 3) CI (Build & Push) 성공 확인
- `Build and Push Docker Image` job이 `success`인지 확인
- 로그에서 아래 항목 확인
  - Docker Hub 로그인 성공
  - Docker 이미지 빌드 성공
  - `${DOCKER_HUB_USERNAME}/body-type-api:latest` push 성공

### 4) CD (Self-hosted Deploy) 성공 확인
- `Deploy to Local Self-Hosted Runner` job이 `success`인지 확인
- `최신 이미지 가져오기 및 서버 재실행` 스텝에서 아래 항목 확인
  - `docker pull ...:latest` 성공
  - `docker rm -f body-type-api-container` 실행
  - `docker run -d --name body-type-api-container -p 8000:8000 ...` 성공

### 5) 로컬 서버 자동 업데이트 반영 검증
- `http://127.0.0.1:8000` 접속 후 `Ctrl + F5` 강력 새로고침
- 기능 검증
  - 사람 사진(상반신/앉은 자세 포함): 에러 없이 분석 결과 반환
  - 사람 미검출 사진: 에러 메시지와 재업로드 유도 문구 표시
- UI 회귀 검증
  - 사진 미리보기 정상 표시
  - `다른 사진으로 다시하기` 버튼 정상 동작

### 6) 배포 실패 시 우선 확인 로그 포인트
- GitHub Actions `Deploy` 로그
  - `pwsh: command not found`, `bash: command not found` (쉘 설정 불일치)
  - `docker: command not found` (러너 Docker 미설치/경로 문제)
  - `pull access denied` (Docker Hub 시크릿/권한 문제)
  - `port is already allocated` (포트 충돌)
- Self-hosted runner 머신 점검
  - `docker ps -a`로 컨테이너 상태 확인
  - `docker logs body-type-api-container`로 앱 시작 오류 확인
- 앱 런타임 로그 점검
  - `uvicorn` startup traceback
  - OpenCV cascade 로드 실패 여부
