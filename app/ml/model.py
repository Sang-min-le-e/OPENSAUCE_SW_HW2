import io
import numpy as np
from PIL import Image

def analyze_body_type(image_bytes: bytes) -> str:
    """
    이미지 바이트를 입력받아 가벼운 모델로 체형을 분석하는 가상의 함수입니다.
    실제 MLOps 파이프라인 구축 시 이 부분을 실제 모델(예: PyTorch/TensorFlow/Mediapipe) 
    추론 코드로 교체하시면 됩니다.
    """
    try:
        # 1. 이미지 로드 및 전처리
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")
        image = image.resize((224, 224))
        img_array = np.array(image)
        
        # 2. 모델 예측 (임의의 로직으로 대체, 
        # 실제로는 model.predict(img_array) 등이 들어갑니다.)
        # 평균 픽셀 밝기/색상 등을 사용하여 임의 결과를 도출 (시뮬레이션 용)
        mean_val = np.mean(img_array)
        
        if mean_val < 80:
            return "근육질 (Muscular)"
        elif mean_val < 150:
            return "마른 체형 (Ectomorph)"
        elif mean_val < 200:
            return "표준 체형 (Mesomorph)"
        else:
            return "건장한 체형 (Endomorph)"
            
    except Exception as e:
        raise ValueError(f"이미지 처리 중 오류 발생: {e}")

def recommend_martial_arts(body_type: str) -> dict:
    """
    체형을 기반으로 격투기를 추천하는 로직입니다.
    """
    recommendations = {
        "근육질 (Muscular)": {
            "martial_art": "레슬링 / 종합격투기(MMA)",
            "reason": "강한 근력과 파워를 살릴 수 있는 그래플링 및 타격이 결합된 종목이 유리합니다."
        },
        "마른 체형 (Ectomorph)": {
            "martial_art": "무에타이 / 태권도",
            "reason": "긴 리치와 가벼운 체중을 활용한 타격 위주의 종목이 적합합니다."
        },
        "표준 체형 (Mesomorph)": {
            "martial_art": "복싱 / 유도",
            "reason": "민첩성과 힘의 밸런스가 좋아 타격기나 메치기에 모두 적합합니다."
        },
        "건장한 체형 (Endomorph)": {
            "martial_art": "주짓수 / 씨름",
            "reason": "체중을 활용하여 상대를 압박하고 방어 및 굳히기에 능한 그래플링 종목에 유리합니다."
        }
    }
    
    return recommendations.get(body_type, {
        "martial_art": "추천 결과를 찾을 수 없음",
        "reason": "체형 데이터가 명확하지 않습니다."
    })
