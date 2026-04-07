import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from app.ml.model import analyze_body_type, recommend_martial_arts

app = FastAPI(
    title="몸매 기반 격투기 추천 API",
    description="MLOps 파이프라인 구축을 위한 체형 분석 및 무술 추천 가상 서버",
    version="0.1.0"
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    # 저장해둔 디자인 파일(index.html)을 불러와서 화면에 보여주기
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/predict/")
async def predict_martial_arts(file: UploadFile = File(...)):
    """
    이미지를 업로드하면 모의 AI 모델을 통해 체형을 분석하고, 
    알맞은 격투기를 추천해 줍니다.
    """
    # 1. 파일 확장자/타입 검사
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")
        
    try:
        # 2. 이미지 읽기
        image_bytes = await file.read()
        
        # 3. 모델 추론을 통한 체형 분석 (모의 로직)
        body_type = analyze_body_type(image_bytes)
        
        # 4. 체형별 격투기 추천 결과 가져오기
        recommendation = recommend_martial_arts(body_type)
        
        # 5. 결과 반환
        return {
            "filename": file.filename,
            "body_type": body_type,
            "recommendation": recommendation
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 내부 오류가 발생했습니다: {str(e)}")
