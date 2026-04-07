# Python 3.10 slim 이미지를 기반으로 하여 용량 최소화
FROM python:3.10-slim

# 환경 변수 설정
# PYTHONDONTWRITEBYTECODE: 파이썬이 .pyc 파일을 쓰지 않도록 설정
# PYTHONUNBUFFERED: 파이썬 출력이 버퍼링 없이 즉시 콘솔에 출력되도록 설정 (로깅에 유용)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (추후 OpenCV 등 복잡한 라이브러리 추가 시 libgl1-mesa-glx 등의 패키지가 필요할 수 있음)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 요구사항 파일 먼저 복사 (Docker 레이어 캐싱 활용을 통한 빌드 속도 최적화)
COPY requirements.txt .

# 파이썬 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 및 모델 복사
COPY app/ ./app/
COPY models/ ./models/

# 컨테이너가 8000번 포트를 사용함을 명시
EXPOSE 8000

# Uvicorn을 사용하여 FastAPI 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
